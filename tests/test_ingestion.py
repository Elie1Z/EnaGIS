"""Data risks: aggregate duplication, missingness, geometry, offline and immutable inputs."""

import json
import socket
from copy import deepcopy
from pathlib import Path

import pytest
from phase2_fixture import build_raw_fixture
from pydantic import ValidationError

from enagis.acquire import download
from enagis.adapters.canada import normalize_registry, registry_identity_key
from enagis.adapters.licensing import parse_station_page
from enagis.adapters.spatial import gpkg_geometry
from enagis.data_contracts import IngestionConfig, Manifest
from enagis.data_io import file_hash, safe_path, verify_manifest
from enagis.data_validation import verify_data
from enagis.ingestion import ingest


def no_network(*args, **kwargs):
    raise AssertionError("analytical rebuild attempted network access")


def test_complete_offline_rebuild_is_deterministic_and_lossless(tmp_path, monkeypatch):
    manifest_path, config_path = build_raw_fixture(tmp_path)
    monkeypatch.setattr(socket.socket, "connect", no_network)
    output = tmp_path / "data/processed/test"
    summary = ingest(manifest_path, config_path, tmp_path, output, skip_licensing=True)
    assert summary["registry"]["facilities"] == 4
    assert summary["registry"]["positive_storage"] == 2
    assert summary["production"]["unknown_regional_non_durum"] == 1
    assert summary["deliveries"]["outcome_mass_tonnes"] == 5000
    links = json.loads((output / "shipping_links.json").read_bytes())["rows"]
    assert len(links) == 3  # Two elevators share ONE outcome, never duplicate its 2000 tonnes.
    assert len({r["shipping_point_id"] for r in links}) == 2
    outcomes = json.loads((output / "outcomes_transfer.json").read_bytes())["rows"]
    assert len(outcomes) == 1 and outcomes[0]["province"] == "MB"
    assert outcomes[0]["original"]["unit"] == "kilotonne"
    assert outcomes[0]["conversion"]["converted"]["amount"]["value"] == 3000
    capacities = json.loads((output / "capacities.json").read_bytes())["rows"]
    assert capacities[2]["original"]["amount"]["value"] is None
    assert capacities[3]["original"]["amount"]["value"] == 0
    registry = json.loads((output / "registry.json").read_bytes())["rows"]
    assert registry[3]["location"]["precision"] == "P5"
    road = json.loads((output / "roads_AB.jsonl").read_text())
    assert road["node_ids"] == [10, 11] and road["tags"]["oneway"] == "yes"
    assert road["coordinates_lon_lat"][0] == [-113, 53]
    assert road["coordinates_lon_lat"][1] == pytest.approx([-112.99, 53])
    rejected = json.loads((output / "roads_AB.rejected.jsonl").read_text())
    assert rejected["node_ids"] == [10, 99]
    assert summary["roads"][0]["extract_timestamp"] == "2024-01-01T00:00:00Z"
    assert not any(j["left_before"] != j["retained_left"] for j in summary["joins"])
    before = {p.name: file_hash(p) for p in output.iterdir()}
    ingest(manifest_path, config_path, tmp_path, output, skip_licensing=True)
    assert before == {p.name: file_hash(p) for p in output.iterdir()}
    verify_manifest(Manifest.model_validate_json(manifest_path.read_bytes()), tmp_path)
    assert verify_data(output)["verified_artifacts"] >= 30
    path = output / "registry.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="derived artifact checksum"):
        verify_data(output)


def test_corrupt_input_fails_before_outputs(tmp_path):
    manifest_path, config_path = build_raw_fixture(tmp_path)
    path = tmp_path / "data/raw/phase2/registry.geojson"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="checksum/size"):
        ingest(manifest_path, config_path, tmp_path, tmp_path / "data/processed/test", True)
    assert not (tmp_path / "data/processed/test/index.json").exists()


def test_identity_survives_source_objectid_changes(tmp_path):
    manifest_path, config_path = build_raw_fixture(tmp_path)
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    source = manifest.sources[0]
    path = tmp_path / source.local_path
    raw = json.loads(path.read_bytes())
    first_key = registry_identity_key(raw["features"][0]["properties"])
    raw["features"][0]["properties"]["OBJECTID"] = 999
    assert registry_identity_key(raw["features"][0]["properties"]) == first_key
    path.write_text(json.dumps(raw), encoding="utf-8")
    identities = json.loads((tmp_path / "data/manual/facility-identities-v1.json").read_bytes())[
        "rows"
    ]
    rows = normalize_registry(path, source, identities, json.loads(config_path.read_bytes()))[0]
    assert rows[0].facility_id == "facility:1" and rows[0].source_record_id.endswith(":999")


def test_duplicate_identity_rejected(tmp_path):
    manifest_path, config_path = build_raw_fixture(tmp_path)
    source = Manifest.model_validate_json(manifest_path.read_bytes()).sources[0]
    identities = json.loads((tmp_path / "data/manual/facility-identities-v1.json").read_bytes())[
        "rows"
    ]
    with pytest.raises(ValueError, match="duplicate registry identity"):
        normalize_registry(
            tmp_path / source.local_path,
            source,
            identities + identities[:1],
            json.loads(config_path.read_bytes()),
        )


def test_paths_and_raw_snapshots_are_protected(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="escapes"):
        safe_path(tmp_path, "../escape")
    raw = tmp_path / "raw.txt"
    raw.write_text("pinned", encoding="utf-8")
    monkeypatch.setattr("enagis.acquire.urlopen", no_network)
    assert download("https://example.invalid", raw, file_hash(raw))["bytes"] == 6
    with pytest.raises(ValueError, match="existing snapshot checksum"):
        download("https://example.invalid", raw, "0" * 64)
    assert raw.read_text() == "pinned"


def test_transfer_partition_and_gpkg_crs_are_checked():
    config = json.loads(Path("configs/regions/ca-prairies.json").read_bytes())
    config["development_units"].append("MB")
    with pytest.raises(ValidationError, match="overlap"):
        IngestionConfig.model_validate(config)
    with pytest.raises(ValueError, match="header"):
        gpkg_geometry(b"not a geometry", 3857)


def test_licensing_continuations_and_shared_station_are_preserved():
    header = (
        "STATION                     RLY.   LICENSEE"
        "                                                         LICENCE      TONNES"
    )

    def line(station, railway, operator, category, tonnes):
        return f"{station:<28}{railway:<7}{operator:<64}{category:>8}{tonnes:>14}"

    text = (
        "Tableau 11 Manitoba\n"
        + header
        + "\nGARE\n"
        + line("ONE", "CN", "Example Co.", "Pri.", "1,000")
        + "\n"
        + " " * 35
        + "Limited\n"
        + line("", "CP", "Other Co.", "Pri.", "2,000")
    )
    rows = parse_station_page(text, 5)
    assert len(rows) == 2 and rows[0]["operator"] == "Example Co. Limited"
    assert rows[1]["station"] == "ONE" and rows[1]["storage_tonnes"] == 2000


def test_duplicate_manifest_sources_rejected(tmp_path):
    path, _ = build_raw_fixture(tmp_path)
    manifest = json.loads(path.read_bytes())
    manifest["sources"].append(deepcopy(manifest["sources"][0]))
    with pytest.raises(ValidationError, match="duplicate snapshot"):
        Manifest.model_validate(manifest)
    manifest["sources"].pop()
    manifest["sources"][0]["local_path"] = "data/processed/overwrite.json"
    with pytest.raises(ValidationError, match="data/raw"):
        Manifest.model_validate(manifest)


def test_spatial_join_retains_ambiguous_and_conflicting_candidates(tmp_path):
    from enagis.adapters.spatial import digital_boundaries, match_points
    from enagis.contracts import SpatialID

    manifest_path, config_path = build_raw_fixture(tmp_path)
    entries = {
        e.snapshot.snapshot_id: e
        for e in Manifest.model_validate_json(manifest_path.read_bytes()).sources
    }
    config = json.loads(config_path.read_bytes())
    registry_source = entries[config["source_ids"]["registry"]]
    identities = json.loads((tmp_path / config["identity_path"]).read_bytes())["rows"]
    facilities, nodes, capacities, raw, issues, excluded = normalize_registry(
        tmp_path / registry_source.local_path, registry_source, identities, config
    )
    boundary_source = entries[config["source_ids"]["ccs"]]
    boundaries, issues = digital_boundaries(
        tmp_path / boundary_source.local_path, boundary_source, "census_consolidated_subdivision"
    )
    ab = next(b for b in boundaries if b.province == "AB")
    second = ab.model_copy(
        update={
            "spatial_id": SpatialID(
                country_code="CA",
                geography_type="census_consolidated_subdivision",
                boundary_vintage="2021",
                code="second",
                source_geographic_id="synthetic:second",
            )
        }
    )
    rows, audit = match_points(
        [(facilities[0], raw[0])],
        [ab, second],
        [registry_source, boundary_source],
        "census_consolidated_subdivision",
    )
    assert rows[0].status == "ambiguous" and len(rows[0].matched_keys) == 2
    assert audit.left_before == audit.retained_left == 1
    second.province = "SK"
    rows, audit = match_points(
        [(facilities[0], raw[0])],
        [ab, second],
        [registry_source, boundary_source],
        "census_consolidated_subdivision",
    )
    assert rows[0].status == "province_conflict" and len(rows[0].matched_keys) == 2


def test_pbf_corruption_and_unknown_features_fail(tmp_path):
    from enagis.adapters.pbf import blocks, header_timestamp, nodes, primitive_groups, varint

    fixture = bytes.fromhex(Path("tests/fixtures/phase2-road.pbf.hex").read_text())
    path = tmp_path / "road.pbf"
    path.write_bytes(fixture)
    parsed = list(blocks(path))
    actual_nodes = [
        node
        for kind, message in parsed
        if kind == b"OSMData"
        for group, strings, granularity, lat_offset, lon_offset in primitive_groups(message)
        for node in nodes(group, granularity, lat_offset, lon_offset)
    ]
    assert actual_nodes == [
        (10, -113000000000, 53000000000),
        (11, -112990000000, 53000000000),
        (12, -113000000000, 53000000000),
    ]
    path.write_bytes(fixture[:-1])
    with pytest.raises(ValueError, match="truncated PBF"):
        list(blocks(path))
    with pytest.raises(ValueError, match="required features"):
        header_timestamp(parsed[0][1] + b"\x22\x03NEW")
    with pytest.raises(ValueError, match="varint"):
        varint(b"\x80")
