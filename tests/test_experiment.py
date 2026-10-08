"""Synthetic scientific-boundary tests; fixture approval is never a real study approval."""

import csv
import io
import json
import shutil
import socket
import subprocess
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest
from phase2_fixture import build_raw_fixture
from pydantic import ValidationError
from pyproj import Transformer
from scipy.sparse import csr_matrix
from shapely.geometry import box, mapping

from enagis.cli import main
from enagis.contracts import Evidence, Value
from enagis.data_io import file_hash, write_json
from enagis.experiment import (
    check_registration,
    evaluate_experiment,
    register_experiment,
    verify_experiment,
)
from enagis.experiment_cohort import count_cohorts
from enagis.experiment_contracts import ExperimentProtocol, FeatureRow, PresenceLabel, StudyUnit
from enagis.experiment_features import build_features
from enagis.experiment_metrics import block_intervals, continuous_boyce, spearman, top_recall
from enagis.experiment_network import build_network, catchment_masks
from enagis.experiment_prepare import (
    load_preparation,
    population_crosswalk,
    prepare_experiment,
    read_population,
)
from enagis.hindcast import evaluate_hindcast, join_hindcast
from enagis.ingestion import ingest
from enagis.pipeline import run_pipeline
from enagis.siting import evaluate_siting, fit_presence_background

PROTOCOL = Path("configs/experiments/phase4-canada-v1.1.json")


@pytest.fixture
def protocol():
    raw = json.loads(PROTOCOL.read_bytes())
    raw.update(
        status="approved",
        approved_by="SYNTHETIC TEST ONLY",
        approved_on="2026-10-08",
        approval_evidence="Synthetic fixture, not authorization to run real science",
        minimum_positive_units=6,
        minimum_positive_blocks=3,
        minimum_hindcast_groups=2,
        bootstrap_draws=100,
    )
    return ExperimentProtocol.model_validate(raw)


def value(number):
    return Value(
        value=number,
        evidence=Evidence(
            label="ESTIMATED" if number is not None else "UNKNOWN",
            source_ids=["synthetic-fixture"],
            as_of="2024-01-01",
            licence="CC0-1.0",
            method="Synthetic test value",
            missing_reason="Synthetic missing component" if number is None else None,
        ),
    )


def unit(i, block="block:0", point=None):
    x, y = point or (float(i * 100), 0.0)
    return StudyUnit(
        unit_id=f"unit:{i}",
        block_id=block,
        province="AB",
        crs="EPSG:3347",
        point_xy=(x, y),
        area_m2=100,
        geometry=mapping(box(x - 5, y - 5, x + 5, y + 5)),
        population=value(100),
        population_csd_ids=[f"csd:{i}"],
        production_intersections_m2={"sadr:0": 100},
    )


def cohort():
    units, features, labels = [], [], []
    for i in range(40):
        u = unit(i, f"block:{i // 10}")
        units.append(u)
        features.append(
            FeatureRow(
                unit_id=u.unit_id,
                block_id=u.block_id,
                province=u.province,
                snap_distance_m=0,
                missing_reasons=[],
                features={
                    "production_context": value(i % 10 + 1),
                    "euclidean_production": value(i % 10 + 10),
                    "accessible_production": value((i % 10 + 1) ** 2),
                    "population": value(100 + i),
                    "road_density": value(1 + i % 3),
                    "junction_density": value(i % 4),
                    "log_ccs_area": value(float(np.log(u.area_m2))),
                },
            )
        )
        positive = i % 10 >= 8
        labels.append(
            PresenceLabel(
                unit_id=u.unit_id,
                status="documented_presence" if positive else "unlabeled",
                facility_ids=[f"facility:{i}"] if positive else [],
                source_ids=["synthetic-registry"],
                definition="Documented primary elevator; unlabeled is not confirmed absence",
            )
        )
    return units, features, labels


def test_draft_cannot_register_or_evaluate_real_data(tmp_path, capsys, monkeypatch):
    raw = json.loads(PROTOCOL.read_bytes())
    raw.update(status="draft", approved_by=None, approved_on=None, approval_evidence=None)
    draft = ExperimentProtocol.model_validate(raw)
    draft_path = tmp_path / "draft.json"
    draft_path.write_text(draft.model_dump_json())
    with pytest.raises(ValueError, match="human approval"):
        check_registration(tmp_path, draft_path, tmp_path, tmp_path / "absent.json")
    with pytest.raises(ValueError, match="human approval"):
        fit_presence_background([[1]], [True], [[1]], draft)
    monkeypatch.setattr(
        sys, "argv", ["enagis", "evaluate-experiment", "--protocol", str(draft_path)]
    )
    assert main() == 1
    assert "human approval" in capsys.readouterr().err
    raw = draft.model_dump(mode="json")
    raw["approved_by"] = "invented"
    with pytest.raises(ValidationError, match="cannot assert approval"):
        ExperimentProtocol.model_validate(raw)


def test_recall_ties_unknown_and_rank_units():
    result = top_recall(["c", "a", "b"], [1, 1, 1], [False, True, False], 0.2)
    assert result["selected_units"] == 1 and result["recall"] == 1
    assert top_recall(["a"], [0], [False], 0.2)["recall"] is None
    assert spearman([1, 2, 3], [1000, 2000, 3000]) == pytest.approx(1)
    assert spearman([1, 1], [1, 2]) is None
    with pytest.raises(ValueError):
        top_recall(["a", "a"], [1, 2], [True, False], 0.2)


def test_boyce_direction_and_undefined():
    scores = np.arange(101)
    assert continuous_boyce(scores, scores > 75, 0.2, 100)["value"] > 0.9
    assert continuous_boyce(-scores, scores > 75, 0.2, 100)["value"] < -0.9
    result = continuous_boyce([1, 1], [True, False], 0.1, 100)
    assert result["value"] is None and result["reason"]


def test_paired_block_rule_and_seed():
    rows = [{"full_model": 0.8, "a": 0.4, "b": 0.6} for _ in range(6)]
    first = block_intervals(rows, ["a", "b"], 100, 0.95, 123)
    assert first == block_intervals(rows, ["a", "b"], 100, 0.95, 123)
    assert first["decision"] == "keep"
    assert first["margin_over_best_baseline"]["estimate"] == pytest.approx(0.2)
    # Beating the weaker baseline does not suffice.
    rows[0]["b"] = 1.0
    for row in rows:
        row["full_model"] = 0.6
    assert block_intervals(rows, ["a", "b"], 100, 0.95, 123)["decision"] != "keep"
    assert block_intervals(rows[:1], ["a", "b"], 100, 0.95, 123)["decision"] == "not_testable"


def test_spatial_cv_and_train_only_preprocessing(protocol, monkeypatch):
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network access"))
    units, features, labels = cohort()
    report, predictions, models = evaluate_siting(features, labels, units, protocol)
    assert report["status"] == "evaluated" and not report["transfer_evaluated"]
    assert len(predictions) == 40 * 8 and len(models) == 4 * 2
    assert "decision" not in report["secondary"] and "decision" not in report["boyce"]
    assert report["boyce_diagnostics"]
    for model in models:
        assert model["held_out_block"] not in model["training_blocks"]
        assert model["background_includes_presences"]
        assert model["training_units"] == 30 and model["training_presence_units"] == 6
    # Altering test-block features must not alter the model fitted for that block.
    modified = deepcopy(features)
    for row in modified[:10]:
        row.features["population"] = value(1e9)
    _, _, second_models = evaluate_siting(modified, labels, units, protocol)
    assert [m for m in models if m["held_out_block"] == "block:0"] == [
        m for m in second_models if m["held_out_block"] == "block:0"
    ]
    # The nearest-presence comparator also excludes test-block labels.
    nearest = next(
        r for r in predictions if r["unit_id"] == "unit:9" and r["arm"] == "nearest_presence"
    )
    assert nearest["score"] == -900


def test_common_cohort_gate_and_no_feature_leakage(protocol):
    units, features, labels = cohort()
    for row in features[:30]:
        row.features["population"] = value(None)
    report, predictions, models = evaluate_siting(features, labels, units, protocol)
    assert report["status"] == "feasibility_failed"
    assert report["cohort_units"] == 10 and not predictions and not models
    raw = features[0].model_dump(mode="json")
    raw["features"]["energy_gap"] = value(5).model_dump(mode="json")
    with pytest.raises(ValidationError):
        FeatureRow.model_validate(raw)
    features[0].province = "MB"
    with pytest.raises(ValueError, match="transfer"):
        evaluate_siting(features, labels, units, protocol)


def population_zip(path, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(
        [
            "REF_DATE",
            "GEO",
            "DGUID",
            "Population and dwelling counts (13): Population, 2021 [1]",
            "Symbols",
            "Other measure",
            "Symbols",
        ]
    )
    writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("98100002.csv", stream.getvalue())


def test_population_repeated_symbols_and_missing_components(tmp_path):
    path = tmp_path / "pop.zip"
    ids = ["2021A00054800001", "2021A00054800002"]
    population_zip(
        path,
        [
            ["2021", "A", ids[0], "42", "", "9", ".."],
            ["2021", "B", ids[1], "", "..", "9", ""],
            [],
            ["footer"],
        ],
    )
    parsed = read_population(path)
    assert parsed[ids[0]]["population"] == 42 and parsed[ids[1]]["population"] is None
    boundary = NS(geometry=mapping(box(0, 0, 20, 10)), spatial_id=NS(key="unit:0"))
    geometries = [box(0, 0, 10, 10), box(10, 0, 20, 10)]
    raw = {
        "crs": "EPSG:3347",
        "features": [
            {"geometry": mapping(g), "properties": {"DGUID": d, "CSDUID": d, "CSDNAME": d}}
            for g, d in zip(geometries, ids, strict=True)
        ],
    }
    csd = tmp_path / "csd.json"
    csd.write_text(json.dumps(raw))
    result, _, crosswalk = population_crosswalk([boundary], csd, path, ["synthetic"])
    assert result["unit:0"].value is None and len(crosswalk) == 2
    assert all(r["status"] == "matched" for r in crosswalk)
    # A CSD whose point lies outside CCS coverage can still overlap a CCS polygon.
    # That CCS must be censored rather than receiving a deceptively complete subtotal.
    population_zip(
        path,
        [
            ["2021", "A", ids[0], "42", "", "9", ""],
            ["2021", "B", ids[1], "99", "", "9", ""],
        ],
    )
    raw["features"][1]["geometry"] = mapping(box(19, 0, 100, 10))
    csd.write_text(json.dumps(raw))
    result, _, crosswalk = population_crosswalk([boundary], csd, path, ["synthetic"])
    assert result["unit:0"].value is None
    assert crosswalk[1]["status"] == "spatial_review_required"


def test_network_dedup_topology_connectors_and_missing_origin(tmp_path, protocol):
    points = [(-113, 53), (-112.99, 53), (-112.98, 53), (-112.99, 53.01)]
    rows = []
    for way, ids in enumerate(([0, 1, 2], [1, 3]), 1):
        rows.append(
            {
                "way_id": way,
                "osm_version": 1,
                "node_ids": ids,
                "coordinates_lon_lat": [points[i] for i in ids],
                "crs": "EPSG:4326",
                "tags": {"highway": "primary"},
            }
        )
    a, b = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    a.write_text("\n".join(json.dumps(r) for r in rows))
    b.write_text(json.dumps(rows[0]) + "\n")
    project = Transformer.from_crs(4326, 3347, always_xy=True)
    xy = [project.transform(*p) for p in points]
    units = [unit(i, point=p) for i, p in enumerate(xy)]
    network = build_network([a, b], units, protocol, progress=lambda *a, **k: None)
    graph, _, _, junctions, audit = network
    assert audit["identical_duplicate_ways"] == 1 and graph.nnz == 6
    assert junctions[1] == 1
    assert graph[0, 1] == pytest.approx(np.linalg.norm(np.asarray(xy[0]) - xy[1]))
    network[-1]["source_ids"] = ["synthetic-roads"]
    rows[0]["osm_version"] = 2
    b.write_text(json.dumps(rows[0]) + "\n")
    with pytest.raises(ValueError, match="conflicting duplicate"):
        build_network([a, b], units, protocol, progress=lambda *a, **k: None)
    # A disconnected source within the Euclidean radius makes coverage uncertain.
    units.append(unit(4, point=(xy[0][0] - 10000, xy[0][1])))
    masks, _, valid = catchment_masks(graph, network[1], [u.point_xy for u in units], protocol)
    assert not valid[-1] and not masks[:, -1].any()


def test_features_conserve_proxy_mass_and_propagate_unknowns(protocol):
    units = [unit(0, point=(0, 0)), unit(1, point=(10000, 0))]
    production = [NS(geometry_ref="sadr:0", production_id="p:0", modeled_tonnes=value(500))]
    sadr = [NS(spatial_id=NS(key="sadr:0"), geometry=mapping(box(0, 0, 10, 100)))]
    network = (
        csr_matrix([[0, 1], [1, 0]]),
        np.asarray([[0, 0], [1, 0]]),
        np.zeros(2),
        np.zeros(2),
        {"source_ids": ["synthetic-roads"]},
    )
    features, audit = build_features(units, production, sadr, network, protocol)
    assert features[0].features["euclidean_production"].value == 100
    assert features[0].features["accessible_production"].value is None
    assert audit["units_with_uncertain_road_origin_coverage"] == 2
    p = audit["production_proxy"][0]
    assert p["represented_tonnes"] + p["outside_ccs_footprint_tonnes"] == 500
    production[0].modeled_tonnes = value(None)
    features, _ = build_features(units, production, sadr, network, protocol)
    assert features[0].features["production_context"].value is None
    assert features[0].features["euclidean_production"].value is None


def test_shipping_point_volume_counted_once_and_incomplete_members_excluded(protocol):
    _, features, _ = cohort()
    source = NS(unit="tonne", dimension="storage_mass", amount=value(2000))
    outcome = NS(
        shipping_point_id="point:0",
        split="development",
        conversion=NS(converted=source),
        model_dump=lambda **k: {"synthetic": True},
    )
    links = [NS(facility_id=f"f:{i}", shipping_point_id="point:0") for i in range(2)]
    traces = [
        NS(
            facility=NS(facility_id=f"f:{i}"),
            assigned_tonnes_per_reporting_period=value(100 + i * 100),
        )
        for i in range(2)
    ]
    blocks = {"f:0": "block:0", "f:1": "block:0"}
    units = {"f:0": "unit:0", "f:1": "unit:0"}
    rows = join_hindcast([outcome], links, traces, blocks, units, features, protocol)
    assert len(rows) == 1 and rows[0]["predicted_tonnes"] == 300
    assert rows[0]["scores"]["population"] == 100  # shared CCS not counted twice
    report = evaluate_hindcast(rows, protocol)
    assert report["observed_total_tonnes_counted_once"] == 2000
    assert report["facility_level_observations"] == 0
    assert not report["partial_car_fallback"][0]["complete_district_total"]
    traces[1].assigned_tonnes_per_reporting_period = value(None)
    rows = join_hindcast([outcome], links, traces, blocks, units, features, protocol)
    assert rows[0]["predicted_tonnes"] is None and rows[0]["exclusion_reasons"]
    with pytest.raises(ValueError, match="duplicated observed"):
        join_hindcast([outcome, outcome], links, traces, blocks, units, features, protocol)
    outcome.split = "transfer"
    with pytest.raises(ValueError, match="transfer outcomes"):
        join_hindcast([outcome], links, traces, blocks, units, features, protocol)


def test_offline_preparation_registration_export_and_tampering(tmp_path, protocol, monkeypatch):
    """Entire public path on synthetic inputs, including a real temporary Git registration."""
    root = tmp_path
    manifest_path, region = build_raw_fixture(root)
    raw_sk = root / "data/raw/phase2/SK.osm"
    # Independent fixture provinces must not reuse global OSM IDs at different coordinates.
    raw_sk.write_text(raw_sk.read_text().replace('="1"', '="1001"').replace('="2"', '="1002"'))
    manifest = json.loads(manifest_path.read_bytes())
    entry = next(e for e in manifest["sources"] if e["local_path"].endswith("SK.osm"))
    entry["snapshot"]["sha256"], entry["byte_count"] = file_hash(raw_sk), raw_sk.stat().st_size
    write_json(manifest_path, manifest)
    source = root / "data/processed/phase2"
    ingest(manifest_path, region, root, source, skip_licensing=True)
    shutil.copyfile("uv.lock", root / "uv.lock")
    phase3 = root / "outputs/phase3"
    run_pipeline(
        root,
        source,
        region,
        Path("configs/scenarios/phase3-engineering-v1.json"),
        manifest_path,
        phase3,
        allow_temporary=True,
    )
    boundaries = json.loads((source / "boundaries_ccs.json").read_bytes())["rows"]
    dev = [b for b in boundaries if b["province"] in {"AB", "SK"}]
    csd_features, pop_rows = [], []
    for b in dev:
        dguid = "2021A0005" + ("48" if b["province"] == "AB" else "47") + "00001"
        csd_features.append(
            {
                "geometry": b["geometry"],
                "properties": {"DGUID": dguid, "CSDUID": dguid, "CSDNAME": "Synthetic CSD"},
            }
        )
        pop_rows.append(["2021", "Synthetic CSD", dguid, "100", "", "9", ""])
    extra = root / "data/raw/phase4"
    extra.mkdir(parents=True)
    population_zip(extra / "population-csd-2021.zip", pop_rows)
    write_json(
        extra / "csd-development-2021.geojson", {"crs": "EPSG:3347", "features": csd_features}
    )
    population_manifest = json.loads(Path("docs/data/phase4-manifest.json").read_bytes())
    for e in population_manifest["sources"]:
        path = root / e["local_path"]
        e["snapshot"].update(
            sha256=file_hash(path),
            publisher="Synthetic fixture",
            processing_step="Synthetic test only",
        )
        e["dataset_name"], e["byte_count"] = "Synthetic test source", path.stat().st_size
    write_json(root / "docs/data/phase4-manifest.json", population_manifest)
    protocol_path = root / "configs/experiments/test.json"
    write_json(protocol_path, protocol)
    review = root / protocol.scientific_review_ref
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text("SYNTHETIC protocol; no real scientific approval.")
    preparation = root / "data/processed/phase4"
    monkeypatch.setattr(socket, "create_connection", lambda *a, **k: pytest.fail("network access"))
    audit = prepare_experiment(root, protocol_path, preparation)
    assert audit["units"] == 2 and audit["transfer_excluded"] == ["MB"]
    first = file_hash(preparation / "index.json")
    prepare_experiment(root, protocol_path, preparation)
    assert file_hash(preparation / "index.json") == first
    assert len(load_preparation(preparation)[1]["units.json"]) == 2

    def git(*args):
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

    git("init")
    git("add", "configs/experiments", "docs/spec/phase4-preregistration.md", "uv.lock")
    git(
        "-c",
        "user.name=Synthetic test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "Synthetic preregistration fixture",
    )
    remote = root / "remote.git"
    git("init", "--bare", str(remote))
    git("remote", "add", "origin", str(remote))
    registration_path = root / "data/manual/registration.json"
    with pytest.raises(ValueError, match="pushed to the remote"):
        register_experiment(root, protocol_path, preparation, registration_path)
    assert not registration_path.exists()
    registered = register_experiment(
        root, protocol_path, preparation, registration_path, publish=True
    )
    assert registered["protocol_sha256"] == file_hash(protocol_path)
    assert registered["remote_commit"] == registered["git_commit"]
    with pytest.raises(ValueError, match="immutable"):
        register_experiment(root, protocol_path, preparation, registration_path)
    output = root / "outputs/phase4"
    report = evaluate_experiment(
        root, protocol_path, preparation, registration_path, output, phase3
    )
    assert report["siting"]["status"] == "feasibility_failed"
    assert report["hindcast"]["observed_groups"] == 1
    assert verify_experiment(output)["verified_artifacts"] == 6
    hashes = {p.name: file_hash(p) for p in output.iterdir()}
    evaluate_experiment(root, protocol_path, preparation, registration_path, output, phase3)
    assert hashes == {p.name: file_hash(p) for p in output.iterdir()}
    # Even with a refreshed checksum, duplicate point outcomes are semantically rejected.
    path = output / "hindcast_groups.json"
    raw = json.loads(path.read_bytes())
    raw["rows"].append(deepcopy(raw["rows"][0]))
    write_json(path, raw)
    index = json.loads((output / "index.json").read_bytes())
    next(e for e in index["artifacts"] if e["path"] == path.name)["sha256"] = file_hash(path)
    write_json(output / "index.json", index)
    with pytest.raises(ValueError, match="counted more than once"):
        verify_experiment(output)
    review.write_text("Changed after preregistration")
    with pytest.raises(ValueError, match="review document changed"):
        check_registration(root, protocol_path, preparation, registration_path)


def test_counts_only_cohorts_drop_production_without_changing_primary(protocol):
    units, _, labels = cohort()
    units[0].population = value(None)
    labels[1].status = "spatial_review_required"
    production = [NS(geometry_ref="sadr:0", modeled_tonnes=value(None))]
    graph = csr_matrix([[0, 4000], [4000, 0]])
    xy = np.asarray([[0, 0], [4000, 0]])
    result = count_cohorts(units, labels, production, graph, xy, protocol)
    assert result["primary"]["complete_ccs"] == 0
    assert result["primary"]["exclusions_by_reason"]["production_unknown"] == 40
    assert result["primary"]["exclusions_by_reason"]["population_unknown"] == 1
    assert result["primary"]["exclusions_by_reason"]["spatial_review"] == 1
    assert result["sensitivity"]["complete_ccs"] == 38
    assert result["sensitivity"]["positive_ccs"] == 8
    assert result["sensitivity"]["positive_cars"] == 4
    assert not result["primary_gate_passed"]
    assert result["status"] == "counts_only_no_scores_fits_outcomes_or_metrics"


def test_area_transform_is_not_logged_twice(protocol):
    x = np.asarray([[2.0, 1.0], [4.0, 10.0], [6.0, 100.0]])
    _, model = fit_presence_background(
        x, [True, False, True], x, protocol, ["log_ccs_area", "population"]
    )
    assert model["scaler_mean"][0] == 4
    assert model["scaler_mean"][1] == pytest.approx(np.log1p(x[:, 1]).mean())
