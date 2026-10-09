"""Final interface rebuild preserves science and supplies offline global navigation."""

import json
import re
import socket
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from enagis.data_io import file_hash
from scripts.build_demo import verify_demo
from scripts.build_mvp import ROOT, build
from scripts.generate_figures import generate


def payload(folder, identity):
    html = (folder / "index.html").read_text(encoding="utf-8")
    match = re.search(
        rf'<script id="{identity}" type="application/json">(.*?)</script>', html, re.S
    )
    return json.loads(match.group(1))


@pytest.fixture(scope="module")
def application(tmp_path_factory):
    folder = tmp_path_factory.mktemp("mvp")
    build(folder)
    return folder


def test_mvp_rebuild_without_network_and_scientific_source_changes(application, monkeypatch):
    def no_network(*_args, **_kwargs):
        raise AssertionError("offline rebuild attempted network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)
    before = {
        path: file_hash(path) for path in (ROOT / "demo/evidence").rglob("*") if path.is_file()
    }
    assert build(application)["verification"]["status"] == "verified"
    assert all(file_hash(path) == digest for path, digest in before.items())
    assert verify_demo(ROOT / "demo")["status"] == "verified"
    manifest = json.loads((application / "manifest.json").read_text())
    assert manifest["scientific_completion"] is False


def test_navigation_data_never_creates_scientific_candidates(application):
    data, world = payload(application, "demo-data"), payload(application, "world-data")
    assert len(data["nodes"]) == 10
    candidates = payload(application, "candidate-data")
    assert len(candidates) == 261
    assert {row["province"] for row in candidates} == {"AB", "SK"}
    assert len(world["places"]) > 7000
    assert world["purpose"] == "navigation_only_not_analysis"
    assert any(place["name"] == "Kigali" for place in world["places"])
    assert data["field_verification"]["n"] == 0
    assert not data["comparison"]["siting"]["transfer_evaluated"]
    original = json.loads((ROOT / "demo/evidence/phase4/report.json").read_text())["data"]
    assert data["comparison"]["siting"]["primary"] == original["siting"]["primary"]


def test_application_has_local_resources_and_no_presenter_prompts(application):
    html = (application / "index.html").read_text(encoding="utf-8")
    assert len(re.findall(r"data-lens=", html)) == 4
    assert all(word not in html for word in ("Start guided demo", "OFFLINE DEMO", 'id="guide"'))
    urls = re.findall(r'<(?:script|link)[^>]*(?:src|href)="([^"]+)"', html)
    assert all(not url.startswith(("http", "//")) for url in urls)
    assert "connect-src 'none'" in html
    for name in ("inter.ttf", "fraunces.ttf", "fraunces-italic.ttf"):
        assert (application / "assets" / name).stat().st_size > 10000
    for name in ("enagis-wordmark.png", "enagis-mark.png"):
        assert (application / "assets/brand" / name).stat().st_size > 1000
        assert f"assets/brand/{name}" in html
    assert all(
        token not in html for token in ("__WORLD__", "__DATA__", "__CANDIDATES__", "__CONTEXT__")
    )


@pytest.mark.parametrize("folder", [".", "demo", "src/overwrite", "configs/test", "web/test"])
def test_mvp_build_rejects_source_and_historical_targets(folder):
    with pytest.raises(ValueError, match="must not overwrite"):
        build(Path(folder))


def test_defense_figures_preserve_negative_intervals_and_recorded_values(tmp_path):
    output = tmp_path / "figures"
    hashes = generate(output)
    assert len(hashes) == 3
    original = json.loads((ROOT / "demo/evidence/phase4/report.json").read_text())["data"]
    sidecar = json.loads((output / "source.json").read_text())
    assert sidecar["hindcast"] == original["hindcast"]
    assert sidecar["hindcast"]["arms"]["population"]["interval"][0] < 0
    chart = ET.parse(output / "hindcast-comparison.svg")
    circles = chart.findall(".//{http://www.w3.org/2000/svg}circle")
    assert len(circles) == len(original["hindcast"]["arms"])
    assert all(260 <= float(circle.attrib["cx"]) <= 800 for circle in circles)
    labels = [el.text for el in chart.findall(".//{http://www.w3.org/2000/svg}text")]
    assert "-1" in labels and any("-0.192" in text for text in labels if text)
    assert generate(output) == hashes
