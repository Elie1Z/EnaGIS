"""Portable demo preserves scientific claims, provenance and exact historical rankings."""

import csv
import json
import re
import shutil
import socket
from copy import deepcopy
from pathlib import Path

import pytest

from enagis.data_io import file_hash, write_json
from scripts.build_demo import export, read, verify_demo

DEMO = Path("demo")


def embedded(output):
    html = (output / "index.html").read_text(encoding="utf-8")
    text = re.search(r'<script id="demo-data" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(text.group(1))


@pytest.fixture(scope="module")
def rebuilt(tmp_path_factory):
    output = tmp_path_factory.mktemp("offline-demo")
    export(
        DEMO / "evidence/phase3",
        DEMO / "evidence/phase4",
        read(DEMO / "evidence/context.json"),
        output,
        read(DEMO / "evidence/sources.json"),
    )
    return output


def test_offline_rebuild_uses_only_portable_verified_artifacts(rebuilt, monkeypatch, tmp_path):
    def no_network(*_args, **_kwargs):
        raise AssertionError("offline demo attempted networking")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    portable = tmp_path / "demo"
    export(
        rebuilt / "evidence/phase3",
        rebuilt / "evidence/phase4",
        dict(reversed(list(read(rebuilt / "evidence/context.json").items()))),
        portable,
        read(rebuilt / "evidence/sources.json"),
    )
    assert verify_demo(portable)["status"] == "verified"
    assert file_hash(portable / "index.html") == file_hash(rebuilt / "index.html")
    assert b"\r\n" not in (portable / "index.html").read_bytes()
    assert b"\r\n" not in (portable / "vendor/manifest.json").read_bytes()
    payload = embedded(portable)
    assert payload["field_verification"] == {"n": 0, "status": "not_collected"}
    assert payload["comparison"]["siting"]["decision"] == "kill_or_no_demonstrated_improvement"
    assert not payload["comparison"]["siting"]["transfer_evaluated"]
    assert not payload["comparison"]["hindcast"]["absolute_volume_accuracy_validated"]
    assert not payload["scenario"]["methods_approved_by"]


def test_csv_geojson_cards_are_the_same_shortlist_and_unknown_is_null(rebuilt):
    data = embedded(rebuilt)
    with (rebuilt / "shortlist.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    features = read(rebuilt / "shortlist.geojson")["features"]
    assert len(csv_rows) == len(features) == len(data["nodes"]) == 10
    assert (rebuilt / "shortlist.csv").read_bytes() == (
        DEMO / "evidence/phase3/engineering-shortlist.csv"
    ).read_bytes()
    for csv_row, feature, card in zip(csv_rows, features, data["nodes"], strict=True):
        assert csv_row["node_id"] == feature["properties"]["node_id"] == card["node_id"]
        assert int(csv_row["rank"]) == feature["properties"]["rank"] == card["rank"]
        assert feature["properties"]["trace"] == card
        assert card["province"] in {"AB", "SK"}
        assert card["requirement"]["electrical_kw"]["evidence"]["label"] == "ESTIMATED"
        assert card["storage_capacity"]["original"]["amount"]["evidence"]["label"] == "OBSERVED"
        assert card["gap"]["capacity_minus_requirement_kw"]["value"] is None
        assert card["gap"]["capacity_minus_requirement_kw"]["evidence"]["label"] == "UNKNOWN"


def test_demo_tampering_is_rejected(rebuilt, tmp_path):
    copy = tmp_path / "tampered"
    shutil.copytree(rebuilt, copy)
    (copy / "shortlist.csv").write_text("invented shortlist", encoding="utf-8")
    with pytest.raises(ValueError, match="demo checksum mismatch: shortlist.csv"):
        verify_demo(copy)


def test_restricted_sources_and_scientific_overwrites_are_rejected(rebuilt, tmp_path):
    sources = deepcopy(read(rebuilt / "evidence/sources.json"))
    sources[0]["redistribution"] = "restricted"
    phase3, phase4 = rebuilt / "evidence/phase3", rebuilt / "evidence/phase4"
    context = read(rebuilt / "evidence/context.json")
    with pytest.raises(ValueError, match="restricted sources"):
        export(phase3, phase4, context, tmp_path / "rejected", sources)
    with pytest.raises(ValueError, match="overwrite scientific"):
        export(phase3, phase4, context, phase3, sources)


def test_comparison_cannot_silently_attach_to_another_pipeline_run(rebuilt, tmp_path):
    phase3 = tmp_path / "other-phase3"
    shutil.copytree(rebuilt / "evidence/phase3", phase3)
    index = read(phase3 / "index.json")
    index["hashes"]["code"] = "0" * 64
    write_json(phase3 / "index.json", index)
    with pytest.raises(ValueError, match="different historical Phase 3 run"):
        export(
            phase3,
            rebuilt / "evidence/phase4",
            read(rebuilt / "evidence/context.json"),
            tmp_path / "rejected",
            read(rebuilt / "evidence/sources.json"),
        )


def test_context_and_dependency_assets_have_offline_licence_boundaries(rebuilt):
    context = read(rebuilt / "evidence/context.json")
    assert context["purpose"] == "display_only_not_routing_or_catchments"
    assert context["roads_licence"] == "ODbL-1.0"
    assert {f["properties"]["province"] for f in context["provinces"]["features"]} == {"AB", "SK"}
    assert all("MB" not in entry["path"] for entry in context["inputs"])
    assert read(rebuilt / "roads.geojson") == context["roads"]
    assert all(s["redistribution"] == "permitted" for s in read(rebuilt / "evidence/sources.json"))
    html = (rebuilt / "index.html").read_text(encoding="utf-8")
    resource_urls = re.findall(r'<(?:script|link)[^>]*(?:src|href)="([^"]+)"', html)
    assert resource_urls and all(not url.startswith(("http", "//")) for url in resource_urls)
    assert "__DATA__" not in html
    vendor = read(rebuilt / "vendor/manifest.json")
    assert vendor["version"] == "5.12.0"
    for name, digest in vendor["files"].items():
        assert file_hash(rebuilt / "vendor" / name) == digest
