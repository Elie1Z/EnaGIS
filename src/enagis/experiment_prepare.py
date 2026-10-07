"""Prepare upstream geography, labels and population without fitting or evaluating outcomes."""

import csv
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from shapely import STRtree, make_valid
from shapely.geometry import shape

from enagis.contracts import Artifact, Evidence, Facility, Production, RunMetadata, Value
from enagis.data_contracts import Boundary, GeographyOverlap, Manifest, SpatialMatch
from enagis.data_io import file_hash, safe_path, verify_manifest, write_json
from enagis.experiment_contracts import ExperimentProtocol, PresenceLabel, StudyUnit
from enagis.ingestion import code_hash

UPSTREAM_TABLES = {
    "boundaries_ccs.json": Boundary,
    "boundaries_sadr.json": Boundary,
    "production.json": Production,
    "ccs_to_car_overlap.json": GeographyOverlap,
    "ccs_to_sadr_overlap.json": GeographyOverlap,
}
LABEL_TABLES = {"registry.json": Facility, "facility_spatial_matches.json": SpatialMatch}


def read_spine(directory: Path, table_types: dict):
    """Explicit caller-specific allowlist: no discovery/glob can pull downstream features in."""
    index = json.loads((directory / "index.json").read_bytes())
    entries = {e["path"]: e for e in index["artifacts"]}
    if len(entries) != len(index["artifacts"]):
        raise ValueError("duplicate source artifact")
    tables, hashes = {}, {}
    for name, model in table_types.items():
        entry = entries[name]
        path = safe_path(directory, name)
        if file_hash(path) != entry["sha256"] or entry["row_contract"] != model.__name__:
            raise ValueError(f"source checksum/contract mismatch: {name}")
        artifact = Artifact[model].model_validate_json(path.read_bytes())
        if (
            len(artifact.rows) != entry["rows"]
            or artifact.metadata.run_id != index["metadata"]["run_id"]
        ):
            raise ValueError("source row count/run mismatch")
        tables[name], hashes[name] = artifact.rows, entry["sha256"]
    return tables, hashes


def read_population(path: Path):
    result = {}
    with zipfile.ZipFile(path) as archive:
        with archive.open("98100002.csv") as raw:
            rows = csv.reader(io.TextIOWrapper(raw, encoding="utf-8-sig"))
            header = next(rows)
            column = header.index("Population and dwelling counts (13): Population, 2021 [1]")
            # Every measure repeats 'Symbols'; DictReader would overwrite the earlier columns.
            for row in rows:
                if len(row) <= column + 1 or not row[2].startswith(("2021A000547", "2021A000548")):
                    continue
                if row[2] in result or row[0] != "2021":
                    raise ValueError("duplicate/wrong-vintage population observation")
                value, symbol = row[column], row[column + 1]
                result[row[2]] = {
                    "population": float(value) if value and not symbol else None,
                    "symbol": symbol,
                    "raw_value": value,
                    "name": row[1],
                }
    return result


def population_crosswalk(boundaries, csd_path, population_path, source_ids):
    polygons = [shape(b.geometry) for b in boundaries]
    tree = STRtree(polygons)
    raw = json.loads(csd_path.read_bytes())
    if raw.get("exceededTransferLimit") or "3347" not in str(raw.get("crs")):
        raise ValueError("truncated CSD source or wrong CRS")
    population = read_population(population_path)
    csd_ids, crosswalk, members = set(), [], defaultdict(list)
    for feature in raw["features"]:
        props = feature["properties"]
        dguid = props["DGUID"]
        if dguid in csd_ids:
            raise ValueError("duplicate CSD geometry")
        csd_ids.add(dguid)
        geometry = shape(feature["geometry"])
        repaired = not geometry.is_valid
        if repaired:
            geometry = make_valid(geometry)
        point = geometry.representative_point()
        candidates = [int(i) for i in tree.query(point, predicate="intersects")]
        row = {
            "csd_id": dguid,
            "csd_code": props["CSDUID"],
            "name": props["CSDNAME"],
            "raw_population": population.get(dguid),
            "geometry_repaired": repaired,
            "candidate_units": [boundaries[i].spatial_id.key for i in candidates],
            "status": "matched" if len(candidates) == 1 else "spatial_review_required",
        }
        # Audit the entire polygon as well as its representative point. Material cross-boundary
        # discrepancies stay UNKNOWN; 1 m² is only a coordinate arithmetic tolerance.
        row["outside_assigned_ccs_m2"] = (
            float(geometry.difference(polygons[candidates[0]]).area)
            if len(candidates) == 1
            else None
        )
        if row["status"] != "matched" or (
            row["outside_assigned_ccs_m2"] is not None and row["outside_assigned_ccs_m2"] > 1
        ):
            row["status"] = "spatial_review_required"
            candidates = [int(i) for i in tree.query(geometry, predicate="intersects")]
            row["candidate_units"] = [boundaries[i].spatial_id.key for i in candidates]
        for i in candidates:
            members[boundaries[i].spatial_id.key].append(row)
        crosswalk.append(row)
    if csd_ids != set(population):
        raise ValueError("CSD population/geometry universe mismatch")
    values = {}
    for boundary in boundaries:
        rows = members[boundary.spatial_id.key]
        missing = not rows or any(
            r["status"] != "matched"
            or r["raw_population"] is None
            or r["raw_population"]["population"] is None
            for r in rows
        )
        values[boundary.spatial_id.key] = Value(
            value=None if missing else sum(r["raw_population"]["population"] for r in rows),
            evidence=Evidence(
                label="UNKNOWN" if missing else "ESTIMATED",
                source_ids=source_ids,
                as_of="2021-01-01",
                licence="Statistics Canada Open Licence; Open Government Licence - Canada",
                method="Sum published CSD counts via audited full-digital CSD-to-CCS containment; "
                "no area-weighted people",
                missing_reason="Missing population component or uncertain CSD/CCS containment"
                if missing
                else None,
            ),
        )
    return values, members, crosswalk


def prepare_experiment(root: Path, protocol_path: Path, output: Path):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "data/processed") or output == root / "data/processed":
        raise ValueError("preparation output must be a subdirectory of data/processed")
    source_dir = root / "data/processed/phase2"
    if output.is_relative_to(source_dir) or source_dir.is_relative_to(output):
        raise ValueError("preparation output overlaps the source spine")
    protocol = ExperimentProtocol.model_validate_json(protocol_path.read_bytes())
    if protocol.development_units != ["AB", "SK"] or protocol.untouched_transfer_units != ["MB"]:
        raise ValueError("Canadian benchmark partition differs from decision 0003")
    tables, input_hashes = read_spine(source_dir, UPSTREAM_TABLES)
    label_tables, label_hashes = read_spine(source_dir, LABEL_TABLES)
    manifest_path = root / "docs/data/phase4-manifest.json"
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    paths = verify_manifest(manifest, root)
    if any(s.snapshot.redistribution != "permitted" for s in manifest.sources):
        raise ValueError("preparation contains restricted sources")
    source_ids = [s.snapshot.snapshot_id for s in manifest.sources]
    population_path = paths["statcan-population-csd-2021-20261008"]
    csd_path = paths["statcan-csd-development-digital-2021"]
    boundaries = sorted(
        (b for b in tables["boundaries_ccs.json"] if b.province in protocol.development_units),
        key=lambda b: b.spatial_id.key,
    )
    population, members, crosswalk = population_crosswalk(
        boundaries, csd_path, population_path, source_ids + ["statcan-ccs-digital-2021"]
    )
    blocks, overlaps = defaultdict(list), defaultdict(dict)
    for row in tables["ccs_to_car_overlap.json"]:
        blocks[row.origin_key].append(row.target_key)
    for row in tables["ccs_to_sadr_overlap.json"]:
        if row.target_key in overlaps[row.origin_key]:
            raise ValueError("duplicate production overlap")
        overlaps[row.origin_key][row.target_key] = row.intersection_area_m2
    units = []
    for b in boundaries:
        key, polygon = b.spatial_id.key, shape(b.geometry)
        if len(blocks[key]) != 1:
            raise ValueError("ambiguous/missing CCS validation block")
        point = polygon.representative_point()
        units.append(
            StudyUnit(
                unit_id=key,
                block_id=blocks[key][0],
                province=b.province,
                crs="EPSG:3347",
                point_xy=(point.x, point.y),
                area_m2=polygon.area,
                geometry=b.geometry,
                population=population[key],
                population_csd_ids=[r["csd_id"] for r in members[key]],
                production_intersections_m2=overlaps[key],
            )
        )
    development_keys = {u.unit_id for u in units}
    development_facilities = {
        m.record_id
        for m in label_tables["facility_spatial_matches.json"]
        if m.geography_type == "census_consolidated_subdivision"
        and set(m.matched_keys) & development_keys
    }
    valid_facilities = {
        f.facility_id
        for f in label_tables["registry.json"]
        if f.facility_id in development_facilities and f.facility_class.value == "Primary"
    }
    positives, uncertain = defaultdict(list), set()
    for match in label_tables["facility_spatial_matches.json"]:
        if (
            match.geography_type != "census_consolidated_subdivision"
            or match.record_id not in valid_facilities
        ):
            continue
        for key in match.matched_keys:
            if match.status == "matched" and len(match.matched_keys) == 1:
                positives[key].append(match.record_id)
            else:
                uncertain.add(key)
    labels = [
        PresenceLabel(
            unit_id=u.unit_id,
            status="spatial_review_required"
            if u.unit_id in uncertain
            else "documented_presence"
            if positives[u.unit_id]
            else "unlabeled",
            facility_ids=sorted(positives[u.unit_id]),
            source_ids=["aafc-elevators-2024"],
            definition="Documented primary elevator; unlabeled is not confirmed absence",
        )
        for u in units
    ]
    selected_sadr = {
        b.spatial_id.key
        for b in tables["boundaries_sadr.json"]
        if b.province in protocol.development_units
    }
    production = [p for p in tables["production.json"] if p.geometry_ref in selected_sadr]
    sadr = [b for b in tables["boundaries_sadr.json"] if b.spatial_id.key in selected_sadr]
    block_by_unit = {u.unit_id: u.block_id for u in units}
    positive_blocks = Counter(
        block_by_unit[r.unit_id] for r in labels if r.status == "documented_presence"
    )
    audit = {
        "status": "prepared_no_fit_or_outcome_evaluation",
        "units": len(units),
        "positive_units": sum(r.status == "documented_presence" for r in labels),
        "positive_blocks": dict(sorted(positive_blocks.items())),
        "label_statuses": dict(Counter(r.status for r in labels)),
        "population_known_units": sum(u.population.value is not None for u in units),
        "population_unknown_units": sum(u.population.value is None for u in units),
        "csd_rows": len(crosswalk),
        "csd_statuses": dict(Counter(r["status"] for r in crosswalk)),
        "unknown_production_regions": sum(p.modeled_tonnes.value is None for p in production),
        "transfer_excluded": ["MB"],
        "upstream_input_hashes": input_hashes,
        "label_input_hashes": label_hashes,
        "phase4_manifest_sha256": file_hash(manifest_path),
        "scientific_approval": protocol.status,
    }
    known_regions = {p.geometry_ref for p in production if p.modeled_tonnes.value is not None}
    status_by_unit = {r.unit_id: r.status for r in labels}
    upper_cohort = [
        u
        for u in units
        if u.population.value is not None
        and u.production_intersections_m2
        and set(u.production_intersections_m2) <= known_regions
        and status_by_unit[u.unit_id] != "spatial_review_required"
    ]
    upper_positives = [
        u for u in upper_cohort if status_by_unit[u.unit_id] == "documented_presence"
    ]
    audit["complete_basic_covariate_upper_bound"] = {
        "units": len(upper_cohort),
        "positive_units": len(upper_positives),
        "positive_blocks": len({u.block_id for u in upper_positives}),
        "note": "Availability only; network catchments can reduce the common cohort further",
    }
    hashes = {
        "upstream": input_hashes,
        "labels": label_hashes,
        "manifest": file_hash(manifest_path),
        "protocol": file_hash(protocol_path),
        "code": code_hash(),
        "lock": file_hash(root / "uv.lock"),
    }
    run_hash = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    metadata = RunMetadata(
        schema_version="1.0.0",
        run_id=f"phase4-preparation:{run_hash[:20]}",
        region_id="ca-prairies",
        commodity_id="wheat_non_durum",
        service_id="ambient_air_aeration",
        scenario_id=protocol.protocol_id,
        period_start="2024-01-01",
        period_end="2025-07-31",
        config_sha256=file_hash(protocol_path),
        seed=None,
        input_snapshot_ids=sorted(
            set(
                source_ids
                + [
                    "aafc-elevators-2024",
                    "statcan-ccs-digital-2021",
                    "statcan-car-digital-2021",
                    "statcan-32100002-20261007",
                    "aafc-fieldcrop-production-20261007",
                ]
            )
        ),
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.json").unlink(missing_ok=True)
    datasets = {
        "units.json": [u.model_dump(mode="json") for u in units],
        "labels.json": [r.model_dump(mode="json") for r in labels],
        "production.json": [p.model_dump(mode="json") for p in production],
        "sadr.json": [b.model_dump(mode="json") for b in sadr],
        "population_crosswalk.json": crosswalk,
        "audit.json": audit,
        "source_manifest.json": manifest.model_dump(mode="json"),
    }
    artifacts = []
    for name, data in datasets.items():
        write_json(
            output / name,
            {
                "metadata": metadata.model_dump(mode="json"),
                "rows" if isinstance(data, list) else "data": data,
            },
        )
        artifacts.append({"path": name, "sha256": file_hash(output / name)})
    write_json(
        output / "index.json",
        {
            "metadata": metadata.model_dump(mode="json"),
            "hashes": hashes,
            "artifacts": artifacts,
            "audit": audit,
        },
    )
    return audit


def load_preparation(path: Path):
    index = json.loads((path / "index.json").read_bytes())
    metadata = RunMetadata.model_validate(index["metadata"])
    data = {}
    for entry in index["artifacts"]:
        if entry["path"] in data or file_hash(safe_path(path, entry["path"])) != entry["sha256"]:
            raise ValueError("duplicate or corrupt prepared artifact")
        value = json.loads((path / entry["path"]).read_bytes())
        if value["metadata"] != metadata.model_dump(mode="json"):
            raise ValueError("mixed preparation run metadata")
        data[entry["path"]] = value.get("rows", value.get("data"))
    types = {
        "units.json": StudyUnit,
        "labels.json": PresenceLabel,
        "production.json": Production,
        "sadr.json": Boundary,
    }
    if set(data) != set(types) | {
        "population_crosswalk.json",
        "audit.json",
        "source_manifest.json",
    }:
        raise ValueError("incomplete preparation artifacts")
    for name, model in types.items():
        data[name] = [model.model_validate(row) for row in data[name]]
    return index, data
