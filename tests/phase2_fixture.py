"""Tiny synthetic raw sources exercise the same complete path as the national rebuild."""

import csv
import io
import json
import sqlite3
import struct
import zipfile
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import box, mapping
from shapely.ops import transform

from enagis.adapters.canada import registry_identity_key
from enagis.data_io import file_hash, write_json


def build_raw_fixture(root: Path):
    config = json.loads(Path("configs/regions/ca-prairies.json").read_bytes())
    config["licensing_parser_controls_path"] = None
    raw = root / "data/raw/phase2"
    raw.mkdir(parents=True)
    entries = []

    def source(key, path, role="fixture"):
        sid = config["source_ids"][key]
        entries.append(
            {
                "dataset_name": "SYNTHETIC " + key,
                "snapshot": {
                    "snapshot_id": sid,
                    "publisher": "Synthetic fixture; no real observation",
                    "original_url": "https://example.invalid/fixture",
                    "retrieved_on": "2026-10-07",
                    "effective_on": "2024-01-01",
                    "sha256": file_hash(path),
                    "licence": "CC0-1.0",
                    "licence_url": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "redistribution": "permitted",
                    "processing_step": "Synthetic raw test fixture",
                },
                "local_path": path.relative_to(root).as_posix(),
                "byte_count": path.stat().st_size,
                "role": role,
                "effective_date_precision": "year",
                "attribution": "Synthetic fixture",
                "licence_evidence_url": "https://example.invalid/fixture",
                "output_artifacts": [],
            }
        )
        if key.startswith("roads"):
            entries[-1]["snapshot"]["licence"] = "ODbL-1.0"

    coordinates = {"AB": (-113, 53), "SK": (-106, 52), "MB": (-98, 50)}
    features, identities = [], []
    records = [
        ("AB", "ONE", "A", 100, (-113, 53)),
        ("AB", "ONE", "B", 200, (-113, 53)),
        ("MB", "TWO", "C", None, (-98, 50)),
        ("AB", "BAD", "D", 0, (53, -113)),
    ]
    for oid, (province, station, operator, capacity, point) in enumerate(records, 1):
        p = {
            "OBJECTID": oid,
            "PR": province,
            "Station": station,
            "Licensee": operator,
            "Railway": "CN",
            "Elevator_type": "Primary",
            "Capacity_tonne": capacity,
            "Longitude": point[0],
            "Latitude": point[1],
            "Year": "2024",
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": point},
                "properties": p,
            }
        )
        identities.append(
            {
                "identity_key": registry_identity_key(p),
                "facility_id": f"facility:{oid}",
                "node_id": f"node:{oid}",
            }
        )
    path = raw / "registry.geojson"
    write_json(
        path,
        {
            "type": "FeatureCollection",
            "crs": {"properties": {"name": "EPSG:4326"}},
            "features": features,
        },
    )
    source("registry", path)
    write_json(root / config["identity_path"], {"rows": identities})
    path = raw / "deliveries.csv"
    path.write_text(
        "crop_year,grain,Province,Station,deliveries_kT\n2024-2025,Wheat,Alberta,ONE,2\n"
        "2024-2025,Wheat,Manitoba,TWO,3\n2024-2025,Amber Durum,Alberta,ONE,9\n",
        encoding="utf-8",
    )
    source("deliveries", path)
    to_metric = Transformer.from_crs(4326, 3347, always_xy=True)
    metric_geometries = {}
    for province, (lon, lat) in coordinates.items():
        x, y = to_metric.transform(lon, lat)
        metric_geometries[province] = box(x - 1000, y - 1000, x + 1000, y + 1000)
    for key, prefix in (("ccs", "CCS"), ("car", "CAR"), ("cd", "CD")):
        features = []
        for province, code in (("AB", "48"), ("SK", "47"), ("MB", "46")):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        prefix + "UID": code + "01",
                        "DGUID": "dguid:" + prefix + code,
                        prefix + ("ENAME" if key == "car" else "NAME"): province,
                        "PRUID": code,
                    },
                    "geometry": mapping(metric_geometries[province]),
                }
            )
        path = raw / (key + ".geojson")
        write_json(
            path,
            {
                "type": "FeatureCollection",
                "crs": {"properties": {"name": "EPSG:3347"}},
                "features": features,
            },
        )
        source(key, path)
    production_rows = []
    for province, name, code in (
        ("AB", "Alberta", "48"),
        ("SK", "Saskatchewan", "47"),
        ("MB", "Manitoba", "46"),
    ):
        for geography in (name, f"Small Area Data Region 1, {name}"):
            for crop, value in (("Wheat, all", "200"), ("Wheat, durum", "50")):
                unknown = province == "MB" and geography != name and crop == "Wheat, durum"
                production_rows.append(
                    {
                        "REF_DATE": "2024",
                        "GEO": geography,
                        "DGUID": "dguid:" + code,
                        "Harvest disposition": "Production (metric tonnes)",
                        "Type of crop": crop,
                        "UOM": "Metric tonnes",
                        "SCALAR_FACTOR": "units",
                        "VALUE": "" if unknown else value,
                        "STATUS": "F" if unknown else "",
                        "SYMBOL": "r",
                        "VECTOR": "v" + code,
                    }
                )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(production_rows[0]))
    writer.writeheader()
    writer.writerows(production_rows)
    path = raw / "production.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("32100002.csv", stream.getvalue())
    source("production", path)
    path = raw / "sadr.gpkg"
    to_web = Transformer.from_crs(3347, 3857, always_xy=True)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE gpkg_contents (table_name TEXT, srs_id INTEGER)")
        connection.execute(
            "INSERT INTO gpkg_contents VALUES ('PRODUCTION_SMALL_AREA_DATA_REGION',3857)"
        )
        connection.execute(
            "CREATE TABLE PRODUCTION_SMALL_AREA_DATA_REGION "
            "(REF_DATE INTEGER, GEO TEXT, CARUID TEXT, Shape BLOB)"
        )
        for province, name, code in (
            ("AB", "Alberta", "48"),
            ("SK", "Saskatchewan", "47"),
            ("MB", "Manitoba", "46"),
        ):
            geometry = transform(to_web.transform, metric_geometries[province])
            blob = b"GP\x00\x01" + struct.pack("<i", 3857) + geometry.wkb
            connection.execute(
                "INSERT INTO PRODUCTION_SMALL_AREA_DATA_REGION VALUES (?,?,?,?)",
                (2024, f"Small Area Data Region 1, {name}", code + "01", blob),
            )
    source("sadr_geometry", path)
    for index, (province, (lon, lat)) in enumerate(coordinates.items(), 1):
        path = raw / (province + (".pbf" if province == "AB" else ".osm"))
        if province == "AB":
            path.write_bytes(bytes.fromhex(Path("tests/fixtures/phase2-road.pbf.hex").read_text()))
        else:
            path.write_text(
                f'<osm version="0.6"><node id="1" version="1" lon="{lon}" lat="{lat}"/>'
                f'<node id="2" version="1" lon="{lon + 0.01}" lat="{lat}"/>'
                f'<way id="{index}" version="2"><nd ref="1"/><nd ref="2"/>'
                '<tag k="highway" v="primary"/><tag k="oneway" v="yes"/></way></osm>',
                encoding="utf-8",
            )
        source("roads_" + province, path, "roads")
    config_path, manifest_path = root / "config.json", root / "manifest.json"
    write_json(config_path, config)
    write_json(manifest_path, {"manifest_version": "1.0.0", "sources": entries})
    return manifest_path, config_path
