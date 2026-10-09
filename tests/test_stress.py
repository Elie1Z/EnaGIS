"""Sparse-data stress diagnostic: abstention, conservation, determinism and scope guards."""

import json
import random
import shutil
from pathlib import Path

import pytest
from phase2_fixture import build_raw_fixture

from enagis.data_contracts import IngestionConfig
from enagis.ingestion import ingest
from enagis.pipeline import load_inputs
from scripts.sparse_data_stress import degrade, run_stress

PROTOCOL = Path("docs/proposals/sparse-data-stress-v1.protocol.json")
SCENARIO = Path("configs/scenarios/phase3-engineering-v1.json")


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    root = tmp_path_factory.mktemp("stress")
    manifest, region = build_raw_fixture(root)
    ingest(manifest, region, root, root / "data/processed/test", skip_licensing=True)
    (root / "configs").mkdir(exist_ok=True)
    shutil.copyfile(SCENARIO, root / "configs/scenario.json")
    protocol = json.loads(PROTOCOL.read_bytes())
    protocol.update(
        replicates=6,
        scenario_path="configs/scenario.json",
        region_path=Path(region).resolve().relative_to(root.resolve()).as_posix(),
        input_dir="data/processed/test",
    )
    path = root / "configs/protocol.json"
    path.write_text(json.dumps(protocol), encoding="utf-8")
    return root, path, region


def test_degraded_runs_abstain_and_conserve_production(project):
    root, protocol, _ = project
    report = run_stress(root, protocol, root / "outputs/stress", allow_temporary=True)
    assert report["scientific_accuracy_evidence"] is False
    assert report["checks"]["abstention_holds"] is True
    assert report["checks"]["abstention_violations_total"] == 0
    assert report["checks"]["max_conservation_residual_tonnes"] < 1e-6
    assert set(report["results"]) == {
        "production_origin_loss",
        "location_unknown",
        "facility_undocumented",
    }
    for levels in report["results"].values():
        for level in levels:
            assert 0 <= level["retention"]["min"] <= level["retention"]["max"] <= 1
    again = run_stress(root, protocol, root / "outputs/stress-again", allow_temporary=True)
    assert again["results"] == report["results"]  # Seeded replicates are reproducible.
    assert (root / "outputs/stress/report.json").is_file()


def test_production_loss_becomes_explicit_unknown_and_transfer_is_untouched(project):
    root, _, region_path = project
    region = IngestionConfig.model_validate_json(Path(region_path).read_bytes())
    _, tables, _ = load_inputs(root / "data/processed/test")
    degraded, removed = degrade(
        tables, region, "production_origin_loss", 1.0, random.Random(1), "test-protocol"
    )
    masked = [
        r for r in degraded["production.json"] if r.production_id in removed["production_ids"]
    ]
    assert masked and all(r.modeled_tonnes.value is None for r in masked)
    assert all(r.modeled_tonnes.evidence.label == "UNKNOWN" for r in masked)
    assert all("test-protocol" in r.modeled_tonnes.evidence.missing_reason for r in masked)
    provinces = {r.production_id: r.province for r in tables["production_lineage.json"]}
    assert all(provinces[pid] in region.development_units for pid in removed["production_ids"])
    _, gone = degrade(tables, region, "facility_undocumented", 1.0, random.Random(1), "t")
    sources = {r.facility_id: r.province for r in tables["registry_source_rows.json"]}
    assert all(sources[f] in region.development_units for f in gone["facility_ids"])


def test_stress_requires_temporary_authorization_and_output_scope(project):
    root, protocol, _ = project
    with pytest.raises(ValueError):
        run_stress(root, protocol, root / "outputs/unauthorized")
    with pytest.raises(ValueError, match="subdirectory"):
        run_stress(root, protocol, root / "data/stress", allow_temporary=True)
