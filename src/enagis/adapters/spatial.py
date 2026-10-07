"""Explicit source geometries, metric crosswalks and lossless left spatial joins."""

import hashlib
import json
import sqlite3
import struct
from contextlib import closing
from pathlib import Path

from pyproj import Transformer, network
from shapely import STRtree, from_wkb, make_valid
from shapely.geometry import Point, mapping, shape
from shapely.ops import transform

from enagis.adapters.canada import PRUID, evidence, issue, sourced
from enagis.contracts import Evidence, SpatialID
from enagis.data_contracts import Boundary, GeographyOverlap, JoinAudit, SpatialMatch

network.set_network_enabled(False)


def canonical_geometry_hash(geometry):
    return hashlib.sha256(
        json.dumps(geometry, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def checked_polygon(geometry, record_id, source, issues):
    if geometry.is_empty or geometry.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError(f"non-polygon or empty source geometry: {record_id}")
    topology = "valid_source"
    if not geometry.is_valid:
        original_area = geometry.area
        geometry = make_valid(geometry)
        topology = "repaired"
        issues.append(
            issue(
                "geometry_repaired",
                record_id,
                source,
                {
                    "method": "GEOS make_valid",
                    "output_type": geometry.geom_type,
                    "source_area_m2": original_area,
                    "repaired_area_m2": geometry.area,
                },
                "original source geometry hash retained; repair reported explicitly",
            )
        )
        if geometry.geom_type not in ("Polygon", "MultiPolygon") or not geometry.is_valid:
            raise ValueError(f"geometry repair needs review: {record_id}")
    if geometry.area <= 0:
        raise ValueError(f"non-positive polygon area: {record_id}")
    return geometry, topology


def digital_boundaries(path: Path, source, geography_type: str):
    document = json.loads(path.read_bytes())
    if document.get("crs", {}).get("properties", {}).get("name") not in (
        "EPSG:3347",
        "urn:ogc:def:crs:EPSG::3347",
    ):
        raise ValueError("digital boundary source must explicitly declare EPSG:3347")
    if document.get("exceededTransferLimit") or not document.get("features"):
        raise ValueError("incomplete/empty digital boundary response")
    prefix = {
        "census_consolidated_subdivision": "CCS",
        "census_agricultural_region": "CAR",
        "census_division": "CD",
    }[geography_type]
    rows, issues, seen = [], [], set()
    for feature in document["features"]:
        p = feature["properties"]
        spatial_id = SpatialID(
            country_code="CA",
            geography_type=geography_type,
            boundary_vintage="2021",
            code=p[prefix + "UID"],
            source_geographic_id=p["DGUID"],
        )
        if spatial_id.key in seen or p["PRUID"] not in PRUID:
            raise ValueError("duplicate/out-of-footprint digital boundary")
        seen.add(spatial_id.key)
        name = p.get(prefix + "NAME") or p.get(prefix + "ENAME")
        geometry, topology = checked_polygon(
            shape(feature["geometry"]), spatial_id.key, source, issues
        )
        rows.append(
            Boundary(
                spatial_id=spatial_id,
                province=PRUID[p["PRUID"]],
                name=sourced(name, source, reason="Source geography name missing"),
                geometry_crs="EPSG:3347",
                geometry=mapping(geometry),
                source_geometry_sha256=canonical_geometry_hash(feature["geometry"]),
                topology=topology,
                geometry_evidence=evidence(
                    source,
                    "OBSERVED" if topology == "valid_source" else "ESTIMATED",
                    "2021 full digital geometry, EPSG:3347"
                    + ("; make_valid repair" if topology == "repaired" else ""),
                ),
            )
        )
    return sorted(rows, key=lambda row: row.spatial_id.key), issues


def gpkg_geometry(blob: bytes, expected_srs: int):
    if len(blob) < 8 or blob[:2] != b"GP" or blob[2] != 0:
        raise ValueError("unsupported GeoPackage geometry header")
    flags = blob[3]
    if flags & 0b11000000 or flags & 0b10000:
        raise ValueError("empty/extended GeoPackage geometry not supported")
    endian = "<" if flags & 1 else ">"
    srs = struct.unpack(endian + "i", blob[4:8])[0]
    if srs != expected_srs:
        raise ValueError("GeoPackage geometry CRS mismatch")
    envelope = (flags >> 1) & 7
    if envelope not in (0, 1, 2, 3, 4):
        raise ValueError("invalid GeoPackage envelope")
    offset = 8 + {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[envelope]
    return from_wkb(blob[offset:])


def sadr_boundaries(path: Path, source, production_rows: list[dict]):
    names = {r["GEO"] for r in production_rows if "Small Area Data Region" in r["GEO"]}
    transformer = Transformer.from_crs(3857, 3347, always_xy=True, allow_ballpark=False)
    rows, issues, originals = [], [], []
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        info = connection.execute(
            "SELECT srs_id FROM gpkg_contents WHERE table_name = ?",
            ("PRODUCTION_SMALL_AREA_DATA_REGION",),
        ).fetchone()
        if not info or info[0] != 3857:
            raise ValueError("unexpected SADR GeoPackage CRS/table")
        records = connection.execute(
            "SELECT * FROM PRODUCTION_SMALL_AREA_DATA_REGION WHERE REF_DATE = ?", (2024,)
        )
        for record in records:
            if record["GEO"] not in names:
                continue
            p = dict(record)
            blob = p.pop("Shape")
            province = PRUID[str(p["CARUID"])[:2]]
            # This field is a SADR code in this dataset, NOT a 2021 CAR join key.
            spatial_id = SpatialID(
                country_code="CA",
                geography_type="small_area_data_region",
                boundary_vintage="aafc-2024-reporting",
                code=str(p["CARUID"]),
                source_geographic_id=f"aafc:sadr:{p['CARUID']}:2024",
            )
            geometry = transform(transformer.transform, gpkg_geometry(blob, 3857))
            geometry, topology = checked_polygon(geometry, spatial_id.key, source, issues)
            rows.append(
                Boundary(
                    spatial_id=spatial_id,
                    province=province,
                    name=sourced(p["GEO"], source),
                    geometry_crs="EPSG:3347",
                    geometry=mapping(geometry),
                    source_geometry_sha256=hashlib.sha256(blob).hexdigest(),
                    topology=topology,
                    geometry_evidence=evidence(
                        source,
                        "ESTIMATED",
                        "AAFC published 2024 SADR reporting geometry; source EPSG:3857 transformed "
                        "to EPSG:3347, always_xy, no ballpark. SK source CARUID denotes SADR, "
                        "not 2021 CAR.",
                    ),
                )
            )
            originals.append(
                {
                    "geometry_key": spatial_id.key,
                    "source_geometry_sha256": hashlib.sha256(blob).hexdigest(),
                    "source_crs": "EPSG:3857",
                    "original_properties": p,
                }
            )
    if len(rows) != len(names) or len({r.name.value for r in rows}) != len(rows):
        raise ValueError("SADR geometry join missing or duplicated reporting regions")
    return sorted(rows, key=lambda row: row.spatial_id.key), issues, originals


def spatial_evidence(sources, method):
    return Evidence(
        label="INFERRED",
        source_ids=[s.snapshot.snapshot_id for s in sources],
        as_of=max(s.snapshot.effective_on for s in sources),
        licence="; ".join(sorted({s.snapshot.licence for s in sources})),
        method=method,
        missing_reason=None,
    )


def match_points(registry, boundaries, sources, geography_type):
    geometries = [shape(b.geometry) for b in boundaries]
    tree = STRtree(geometries)
    transformer = Transformer.from_crs(4326, 3347, always_xy=True, allow_ballpark=False)
    rows, unmatched, ambiguous = [], [], []
    for facility, original in registry:
        point = facility.location.point.value
        indices = (
            []
            if point is None
            else tree.query(
                Point(*transformer.transform(point.longitude, point.latitude)),
                predicate="covered_by",
            )
        )
        candidates = [boundaries[i] for i in indices]
        keys = sorted(b.spatial_id.key for b in candidates)
        status = "matched" if len(keys) == 1 else "unmatched" if not keys else "ambiguous"
        if any(b.province != original.province for b in candidates):
            status = "province_conflict"
        elif original.location_quality == "conflict":
            status = "location_conflict"
        if status == "unmatched":
            unmatched.append(facility.facility_id)
        elif status != "matched":
            ambiguous.append(facility.facility_id)
        rows.append(
            SpatialMatch(
                record_id=facility.facility_id,
                geography_type=geography_type,
                matched_keys=keys,
                status=status,
                evidence=spatial_evidence(
                    sources,
                    "Left spatial covers join; source point transformed EPSG:4326 -> EPSG:3347, "
                    "always_xy, no ballpark; all boundary candidates retained",
                ),
            )
        )
    audit = JoinAudit(
        name=f"registry_to_{geography_type}",
        left_before=len(registry),
        right_before=len(boundaries),
        output_rows=len(rows),
        retained_left=len(rows),
        unmatched_ids=unmatched,
        ambiguous_ids=ambiguous,
    )
    return rows, audit


def overlap_crosswalk(origins, targets, sources, name):
    target_geometry = [shape(row.geometry) for row in targets]
    tree = STRtree(target_geometry)
    rows, unmatched, ambiguous = [], [], []
    for origin in origins:
        geometry = shape(origin.geometry)
        found = []
        for index in tree.query(geometry, predicate="intersects"):
            area = geometry.intersection(target_geometry[index]).area
            if area > 0:
                target = targets[index]
                found.append(target.spatial_id.key)
                rows.append(
                    GeographyOverlap(
                        origin_key=origin.spatial_id.key,
                        target_key=target.spatial_id.key,
                        intersection_area_m2=area,
                        origin_area_fraction=area / geometry.area,
                        evidence=spatial_evidence(
                            sources,
                            "All positive-area intersections in EPSG:3347; denominator is full "
                            "digital origin polygon area including water. Geometry crosswalk only, "
                            "not production weights or block assignment.",
                        ),
                    )
                )
        if not found:
            unmatched.append(origin.spatial_id.key)
        elif len(found) > 1:
            ambiguous.append(origin.spatial_id.key)
    audit = JoinAudit(
        name=name,
        left_before=len(origins),
        right_before=len(targets),
        output_rows=len(rows),
        retained_left=len(origins),
        unmatched_ids=unmatched,
        ambiguous_ids=ambiguous,
    )
    return sorted(rows, key=lambda row: (row.origin_key, row.target_key)), audit
