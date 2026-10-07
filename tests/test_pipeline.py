"""Scientific failure modes and the offline real-input walking-skeleton path."""

import csv
import json
import shutil
import socket
from copy import deepcopy
from math import fsum
from pathlib import Path

import pytest
from phase2_fixture import build_raw_fixture
from pydantic import ValidationError

from enagis.allocation import allocate, annual_limit, bounded_shares
from enagis.contracts import Capacity, Evidence, Supply, Value
from enagis.data_contracts import IngestionConfig
from enagis.data_io import file_hash, write_json
from enagis.energy import classify_gap, energy_requirement
from enagis.ingestion import ingest
from enagis.pipeline import load_inputs, make_traces, run_pipeline
from enagis.pipeline_contracts import Scenario
from enagis.pipeline_validation import trace_node, verify_run

SCENARIO_PATH = Path("configs/scenarios/phase3-engineering-v1.json")


@pytest.fixture
def scenario():
    return Scenario.model_validate_json(SCENARIO_PATH.read_bytes())


@pytest.fixture(scope="module")
def spine(tmp_path_factory):
    root = tmp_path_factory.mktemp("phase3")
    manifest, region = build_raw_fixture(root)
    input_dir = root / "data/processed/test"
    ingest(manifest, region, root, input_dir, skip_licensing=True)
    shutil.copyfile("uv.lock", root / "uv.lock")
    return root, manifest, region, input_dir


@pytest.mark.parametrize(
    "total,limits,expected,unserved",
    [
        (100, {"a": 10, "b": 70}, {"a": 10, "b": 70}, 20),
        (100, {"a": 10, "b": None}, {"a": 10, "b": 90}, 0),
        (100, {"a": None, "b": None}, {"a": 50, "b": 50}, 0),
        (100, {"a": 0, "b": 1000}, {"a": 0, "b": 100}, 0),
        (100, {}, {}, 100),
        (0, {"a": None}, {"a": 0}, 0),
        (90, {"a": 10, "b": 20, "c": 100}, {"a": 10, "b": 20, "c": 60}, 0),
    ],
)
def test_bounded_mass_conservation(total, limits, expected, unserved):
    shares, remainder = bounded_shares(total, limits)
    assert shares == expected and remainder == unserved
    assert fsum([*shares.values(), remainder]) == pytest.approx(total, abs=1e-8)
    assert bounded_shares(total, dict(reversed(list(limits.items())))) == (shares, remainder)


@pytest.mark.parametrize(
    "total,limits", [(-1, {}), (1, {"a": -1}), (float("inf"), {}), (1, {"a": float("nan")})]
)
def test_invalid_mass_is_rejected(total, limits):
    with pytest.raises(ValueError):
        bounded_shares(total, limits)


def test_storage_not_annual_throughput_and_unknown_is_not_zero(spine, scenario):
    tables = load_inputs(spine[3])[1]
    known, unknown = tables["capacities.json"][0], tables["capacities.json"][2]
    assert annual_limit(known, scenario) == pytest.approx(100 * 0.5 * 365 / 30)
    assert annual_limit(unknown, scenario) is None
    missing_production = next(
        p for p in tables["production.json"] if p.modeled_tonnes.value is None
    )
    rows, balance = allocate(missing_production, [known], scenario)
    assert not rows and balance.input_tonnes is None and balance.unserved_tonnes is None
    production = next(p for p in tables["production.json"] if p.modeled_tonnes.value is not None)
    with pytest.raises(ValueError, match="duplicate node"):
        allocate(production, [known, known], scenario)
    wrong_unit = known.model_dump(mode="json")
    wrong_unit["original"].update(dimension="electric_power", unit="kW")
    with pytest.raises(ValueError, match="storage mass"):
        annual_limit(Capacity.model_validate(wrong_unit), scenario)


def test_temporary_values_cannot_become_approved_silently(scenario):
    with pytest.raises(ValueError, match="allow-temporary"):
        scenario.authorize(False)
    scenario.authorize(True)
    raw = scenario.model_dump(mode="json")
    raw["purpose"] = "scientific_reviewed"
    scientific = Scenario.model_validate(raw)
    with pytest.raises(ValueError, match="human approval"):
        scientific.authorize(True)
    raw["methods_approved_by"], raw["methods_approved_on"] = "Test human", "2026-10-07"
    scientific = Scenario.model_validate(raw)
    with pytest.raises(ValueError, match="unapproved scientific parameter"):
        scientific.authorize(True)
    raw = scenario.model_dump(mode="json")
    raw["parameters"][0]["approved_by"] = "Invented approval"
    with pytest.raises(ValidationError, match="must not carry approval"):
        Scenario.model_validate(raw)


@pytest.mark.parametrize(
    "key,value,unit",
    [
        ("residence_days", 0, "day"),
        ("motor_efficiency", 1.1, "fraction"),
        ("static_pressure", 500, "kW"),
        ("wheat_storage_fraction", -1, "fraction"),
    ],
)
def test_scenario_units_and_physical_domain(scenario, key, value, unit):
    raw = scenario.model_dump(mode="json")
    parameter = next(p for p in raw["parameters"] if p["parameter_id"] == key)
    parameter["unit"], parameter["value"]["value"] = unit, value
    with pytest.raises(ValidationError):
        Scenario.model_validate(raw)


def assigned(value):
    return Value(
        value=value,
        evidence=Evidence(
            label="ESTIMATED" if value is not None else "UNKNOWN",
            source_ids=["fixture"],
            as_of="2024-01-01",
            licence="CC0",
            method="Synthetic throughput",
            missing_reason=None if value is not None else "Missing production",
        ),
    )


def test_dimensional_fan_calculation_and_cycle_boundary(scenario):
    inventory, airflow, requirement = energy_requirement("node:a", assigned(3650), scenario)
    assert inventory.stored_tonnes.value == 300
    assert airflow.value == pytest.approx(0.6)
    assert requirement.electrical_kw.value.central == pytest.approx(0.6 * 500 / (1000 * 0.6 * 0.9))
    assert requirement.electricity_kwh.value.central == pytest.approx(83.33333333333333)
    assert requirement.electrical_kw.evidence.label == "ESTIMATED"
    zero = energy_requirement("node:a", assigned(0), scenario)
    assert zero[2].electrical_kw.value.central == 0
    missing = energy_requirement("node:a", assigned(None), scenario)
    assert missing[0].stored_tonnes.value is None and missing[2].electricity_kwh.value is None


def supply_case(state, amount=None, dimension="electric_power", unit="kW"):
    ev = assigned(amount).evidence
    capacity = (
        None
        if state == "no_documented_asset"
        else Capacity.model_validate(
            {
                "capacity_id": "capacity:a",
                "node_id": "node:a",
                "facility_id": None,
                "service_id": "ambient_air_aeration",
                "status": "unknown" if amount is None else "known",
                "original": {
                    "dimension": dimension,
                    "unit": unit,
                    "amount": {"value": amount, "evidence": ev.model_dump(mode="json")},
                    "period_start": None,
                    "period_end": None,
                    "definition": "Synthetic fan capacity",
                },
                "conversion": None,
            }
        )
    )
    supply = Supply(
        node_id="node:a",
        service_id="ambient_air_aeration",
        state=state,
        evidence=assigned(1).evidence,
        capacity_ref=None if capacity is None else capacity.capacity_id,
        documentation_scope="Synthetic documented asset",
    )
    return supply, capacity


@pytest.mark.parametrize(
    "state,amount,bucket,classification,margin",
    [
        ("no_documented_asset", None, "undocumented_supply", "flagged", None),
        ("documented_unknown_capacity", None, "verify_first", "flagged", None),
        ("documented_known_capacity", 0.2, "undersized", "flagged", 0.2 - 5 / 9),
        ("documented_known_capacity", 1, None, "unflagged", 1 - 5 / 9),
    ],
)
def test_three_supply_states_and_signed_margin(
    scenario, state, amount, bucket, classification, margin
):
    requirement = energy_requirement("node:a", assigned(3650), scenario)[2]
    supply, capacity = supply_case(state, amount)
    gap = classify_gap(supply, capacity, requirement, scenario)
    assert (gap.bucket, gap.classification) == (bucket, classification)
    assert gap.capacity_minus_requirement_kw.value == (
        None if margin is None else pytest.approx(margin)
    )


def test_missing_requirement_and_incompatible_supply_do_not_become_deficit(scenario):
    requirement = energy_requirement("node:a", assigned(None), scenario)[2]
    supply, capacity = supply_case("no_documented_asset")
    gap = classify_gap(supply, capacity, requirement, scenario)
    assert gap.classification == "unknown" and gap.bucket is None
    supply, capacity = supply_case("documented_known_capacity", 100, "storage_mass", "tonne")
    with pytest.raises(ValueError, match="electrical gap"):
        classify_gap(supply, capacity, requirement, scenario)


def test_complete_offline_pipeline_determinism_holdout_and_trace(spine, monkeypatch):
    root, manifest, region, input_dir = spine

    def no_network(*args, **kwargs):
        raise AssertionError("pipeline attempted network")

    monkeypatch.setattr(socket.socket, "connect", no_network)
    output = root / "outputs/integration"
    args = (root, input_dir, region, SCENARIO_PATH, manifest, output)
    before = {p.name: file_hash(p) for p in input_dir.iterdir()}
    audit = run_pipeline(*args, allow_temporary=True)
    assert audit["nodes"] == 3 and audit["ranked_nodes"] == 2
    assert audit["known_input_tonnes"] == pytest.approx(
        audit["assigned_tonnes"] + audit["explicit_unserved_tonnes"], abs=1e-6
    )
    assert audit["explicit_unserved_tonnes"] > 0  # Tiny real-shaped fixture has limited storage.
    assert audit["transfer_units_excluded_from_run"] == ["MB"]
    assert verify_run(output)["shortlist_rows"] == 2
    with (output / "engineering-shortlist.csv").open(encoding="utf-8", newline="") as stream:
        exported = list(csv.DictReader(stream))
    assert exported[0]["capacity_minus_requirement_label"] == "UNKNOWN"
    assert exported[0]["ranking_label"] == "INFERRED"
    assert exported[0]["capacity_minus_requirement_kw"] == ""
    assert "registry only" in exported[0]["supply_documentation_scope"]
    trace = trace_node(output, "node:1")["trace"]
    assert trace["facility"]["facility_id"] == "facility:1"
    assert trace["production_inputs"] and trace["allocations"]
    assert trace["supply"]["state"] == "no_documented_asset"
    assert trace["gap"]["capacity_minus_requirement_kw"]["value"] is None
    first = {p.name: file_hash(p) for p in output.iterdir()}
    run_pipeline(*args, allow_temporary=True)
    assert first == {p.name: file_hash(p) for p in output.iterdir()}
    assert before == {p.name: file_hash(p) for p in input_dir.iterdir()}
    with pytest.raises(ValueError, match="absent from development"):
        trace_node(output, "node:3")
    with pytest.raises(ValueError, match="subdirectory"):
        run_pipeline(*args[:-1], root / "data/raw/overwrite", allow_temporary=True)
    with pytest.raises(ValueError, match="overlaps"):
        run_pipeline(root, output, region, SCENARIO_PATH, manifest, output, allow_temporary=True)
    corrupt = root / "outputs/corrupt"
    shutil.copytree(output, corrupt)
    path = corrupt / "engineering-shortlist.csv"
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="checksum"):
        verify_run(corrupt)
    # Semantic verification must also fail when someone updates a corrupted file's checksum.
    semantic = root / "outputs/semantic-corruption"
    shutil.copytree(output, semantic)
    path = semantic / "production_balances.json"
    raw = json.loads(path.read_bytes())
    known = next(row for row in raw["rows"] if row["input_tonnes"] is not None)
    known["input_tonnes"] += 1
    write_json(path, raw)
    index_path = semantic / "index.json"
    index = json.loads(index_path.read_bytes())
    next(entry for entry in index["artifacts"] if entry["path"] == path.name)["sha256"] = file_hash(
        path
    )
    write_json(index_path, index)
    with pytest.raises(ValueError, match="differs from conservation"):
        verify_run(semantic)


def test_spatial_conflict_missing_production_and_input_order(spine, scenario):
    tables = load_inputs(spine[3])[1]
    region = IngestionConfig.model_validate_json(spine[2].read_bytes())
    traces, allocations, balances = make_traces(tables, region, scenario)
    reordered = {k: list(reversed(v)) for k, v in tables.items()}
    assert make_traces(reordered, region, scenario) == (traces, allocations, balances)
    bad = deepcopy(tables)
    match = next(
        m
        for m in bad["facility_spatial_matches.json"]
        if m.record_id == "facility:1" and m.geography_type == "small_area_data_region"
    )
    match.status = "location_conflict"
    trace = next(t for t in make_traces(bad, region, scenario)[0] if t.node_id == "node:1")
    assert trace.rank is None and trace.assigned_tonnes_per_reporting_period.value is None
    bad = deepcopy(tables)
    production = next(p for p in bad["production.json"] if p.modeled_tonnes.value is not None)
    production.modeled_tonnes = assigned(None)
    missing = make_traces(bad, region, scenario)
    assert any(b.input_tonnes is None for b in missing[2])
    bad = deepcopy(tables)
    bad["capacities.json"].append(bad["capacities.json"][0])
    with pytest.raises(ValueError, match="duplicate"):
        make_traces(bad, region, scenario)


def test_corrupt_derived_source_rejected_before_run(spine):
    root, _, _, input_dir = spine
    corrupt = root / "data/processed/corrupt"
    shutil.copytree(input_dir, corrupt)
    path = corrupt / "production.json"
    write_json(path, {"changed": True})
    with pytest.raises(ValueError, match="checksum"):
        load_inputs(corrupt)
