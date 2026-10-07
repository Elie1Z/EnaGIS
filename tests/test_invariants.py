import json
from copy import deepcopy
from pathlib import Path
from random import Random

import pytest
from pydantic import ValidationError

from enagis.cli import main
from enagis.validation import (
    Bundle,
    FixtureSuite,
    canonical_bytes,
    checked_many_to_one,
    smoke,
    stable_order,
)


def test_all_hand_computed_cases(raw_suite):
    suite = FixtureSuite.model_validate(raw_suite)
    result = smoke(suite)
    assert len(result["cases"]) == 8
    competing = result["cases"][1]
    assert competing["group_tonnes"] == {"SP1": 10.0}  # 6 + 4, not 10 per elevator.
    assert result["cases"][4]["unserved_tonnes"] == 3.0  # 10 - 7.


@pytest.mark.parametrize("mutation", ["lost", "duplicated", "orphan", "missing_unserved"])
def test_allocation_conservation(raw_suite, mutation):
    bundle = deepcopy(raw_suite["cases"][4]["bundle"])
    if mutation == "lost":
        bundle["allocations"][0]["assigned_tonnes"]["value"] = 6.0
    elif mutation == "duplicated":
        duplicate = deepcopy(bundle["allocations"][0])
        duplicate["allocation_id"] = "duplicate-mass"
        bundle["allocations"].append(duplicate)
    elif mutation == "orphan":
        bundle["allocations"][0]["production_id"] = "bad"
    else:
        bundle["allocations"].pop()
    with pytest.raises(ValidationError):
        Bundle.model_validate(bundle)


def test_shipping_outcome_not_duplicated_across_elevators(raw_suite):
    bundle = deepcopy(raw_suite["cases"][1]["bundle"])
    assert len(bundle["shipping_links"]) == 2
    parsed = Bundle.model_validate(bundle)
    assert parsed.outcomes[0].conversion.converted.amount.value == 10.0  # 0.010 kT × 1000.
    duplicate = deepcopy(bundle["outcomes"][0])
    duplicate["outcome_id"] = "O2"
    bundle["outcomes"].append(duplicate)
    with pytest.raises(ValidationError, match="duplicate shipping_point_id"):
        Bundle.model_validate(bundle)


def test_join_audits_cardinality_and_unmatched(raw_suite):
    bundle = Bundle.model_validate(raw_suite["cases"][1]["bundle"])
    rows, audit = checked_many_to_one(bundle.nodes, bundle.facilities[:1], "facility_id")
    assert len(rows) == 2
    assert audit == {"left_before": 2, "right_before": 1, "after": 2, "unmatched": ["F2"]}
    with pytest.raises(ValueError, match="duplicate"):
        checked_many_to_one(bundle.nodes, bundle.facilities + bundle.facilities[:1], "facility_id")


@pytest.mark.parametrize(
    "mutation",
    [
        "bad_margin",
        "unknown_power",
        "undersized",
        "seed",
        "frequency",
        "range",
        "rank",
        "service",
        "period",
        "manifest",
    ],
)
def test_cross_table_and_output_failures(raw_bundle, mutation):
    if mutation == "bad_margin":
        raw_bundle["gaps"][0]["capacity_minus_requirement_kw"]["value"] = 0.0
    elif mutation == "unknown_power":
        raw_bundle["supplies"][0]["state"] = "documented_unknown_capacity"
    elif mutation == "undersized":
        raw_bundle["gaps"][0].update(bucket="undersized", classification="flagged")
    elif mutation == "seed":
        raw_bundle["uncertainty"][0]["seed"] = 99
    elif mutation == "frequency":
        raw_bundle["uncertainty"][0]["inclusion_frequency"] = 0.5
    elif mutation == "range":
        raw_bundle["requirements"][0]["electrical_kw"]["value"]["lower"] = 9.0
    elif mutation == "rank":
        raw_bundle["shortlist"].append(deepcopy(raw_bundle["shortlist"][0]))
    elif mutation == "service":
        raw_bundle["requirements"][0]["service_id"] = "bad"
    elif mutation == "period":
        raw_bundle["metadata"]["period_end"] = "2024-01-01"
    else:
        raw_bundle["metadata"]["input_snapshot_ids"] = ["not-pinned"]
    with pytest.raises(ValidationError):
        Bundle.model_validate(raw_bundle)


def test_signed_margin_is_not_clamped(raw_suite):
    bundle = Bundle.model_validate(raw_suite["cases"][2]["bundle"])
    assert bundle.gaps[0].capacity_minus_requirement_kw.value == -1.0  # 3 kW - 4 kW.
    assert bundle.gaps[0].bucket == "undersized"
    adequate = Bundle.model_validate(raw_suite["cases"][0]["bundle"])
    assert adequate.gaps[0].bucket is None
    assert adequate.gaps[0].classification == "unflagged"


def test_unreachable_time_cannot_be_zero(raw_bundle):
    raw_bundle["travel"][0]["reachable"] = False
    raw_bundle["travel"][0]["travel_minutes"]["value"] = 0.0
    with pytest.raises(ValidationError, match="unreachable"):
        Bundle.model_validate(raw_bundle)


def test_storage_not_electrical_supply(raw_bundle):
    raw_bundle["capacities"][0]["original"].update(unit="tonne", dimension="storage_mass")
    with pytest.raises(ValidationError, match="electrical supply"):
        Bundle.model_validate(raw_bundle)


def test_deterministic_ties_seeds_and_serialization(raw_suite):
    assert stable_order({"N2": 1.0, "N1": 1.0, "N3": 0.0}) == ["N1", "N2", "N3"]
    with pytest.raises(ValueError, match="finite"):
        stable_order({"N1": float("nan")})
    suite = FixtureSuite.model_validate(raw_suite)
    rng1, rng2 = Random(suite.cases[0].bundle.metadata.seed), Random(17)
    assert [rng1.random() for _ in range(4)] == [rng2.random() for _ in range(4)]
    assert canonical_bytes(suite) == canonical_bytes(
        FixtureSuite.model_validate_json(canonical_bytes(suite))
    )
    assert smoke(suite) == smoke(suite)


def test_committed_json_schema_matches_contract():
    root = Path(__file__).resolve().parents[1]
    committed = json.loads(
        (root / "docs/spec/phase1-bundle.schema.json").read_text(encoding="utf-8")
    )
    assert committed == Bundle.model_json_schema()


def test_cli_success_and_failure(raw_suite, monkeypatch, tmp_path, capsys):
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(raw_suite), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["enagis", "smoke", "--fixture", str(fixture)])
    assert main() == 0
    assert json.loads(capsys.readouterr().out)["fixture_only"] is True
    raw_suite["cases"][0]["expected_served_tonnes"] = 999
    fixture.write_text(json.dumps(raw_suite), encoding="utf-8")
    assert main() == 1
    assert "golden mismatch" in capsys.readouterr().err
