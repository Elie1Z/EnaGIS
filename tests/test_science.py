"""Phase 6 numerical, routing, gating and reproducibility acceptance cases."""

import json
import socket
from math import fsum
from pathlib import Path

import numpy as np
import pytest
from phase6_fixture import make_fixture, point
from pydantic import ValidationError

from enagis.contracts import Point
from enagis.data_io import file_hash, write_json
from enagis.science.allocation import allocate
from enagis.science.contracts import Dataset, ScenarioConfig
from enagis.science.energy import annual_limit, gap, requirement
from enagis.science.roads import accessibility, build_network, projection, way_policy
from enagis.science.runner import calculate, execute, load_config, verify
from enagis.science.uncertainty import sample_parameters


@pytest.fixture
def fixture():
    return make_fixture()


def routes(values):
    return [{"origin_id": o, "node_id": n, "minutes": t} for (o, n), t in values.items()]


def test_global_allocation_competition_requires_maximum_served_before_distance():
    # Flexible origin x must go to b, leaving a for captive origin y.
    masses, limits = {"x": 10, "y": 10}, {"a": 10, "b": 10}
    access = routes({("x", "a"): 1, ("x", "b"): 2, ("y", "a"): 2, ("y", "b"): None})
    result = allocate(masses, limits, access, "min_cost_max_served", "exclude_and_flag", 1e-6)
    assert {(r["origin_id"], r["node_id"]): r["tonnes"] for r in result["assignments"]} == {
        ("x", "b"): 10,
        ("y", "a"): 10,
    }
    greedy = allocate(masses, limits, access, "nearest_first", "exclude_and_flag", 1e-6)
    assert sum(b["unserved_tonnes"] for b in greedy["balances"]) == 10


@pytest.mark.parametrize("variant", ["min_cost_max_served", "nearest_first"])
def test_shared_capacity_conservation_overflow_and_stable_ties(variant):
    masses, limits = {"x": 90, "y": 60}, {"a": 40, "b": 50}
    access = routes({(o, n): 1 for o in masses for n in limits})
    result = allocate(masses, limits, access, variant, "exclude_and_flag", 1e-6)
    assert result["known_assigned_tonnes"] == {"a": 40, "b": 50}
    assert fsum(b["unserved_tonnes"] for b in result["balances"]) == 60
    assert all(abs(b["residual_tonnes"]) < 1e-6 for b in result["balances"])
    assert (
        allocate(
            dict(reversed(list(masses.items()))),
            dict(reversed(list(limits.items()))),
            list(reversed(access)),
            variant,
            "exclude_and_flag",
            1e-6,
        )
        == result
    )


def test_unknown_production_capacity_and_unreachable_preserve_meaning():
    access = routes({("x", "a"): 1, ("u", "a"): 2, ("z", "a"): None})
    result = allocate(
        {"x": 10, "u": None, "z": 5},
        {"a": None},
        access,
        "min_cost_max_served",
        "exclude_and_flag",
        1e-6,
    )
    assert result["unknown_production_nodes"] == ["a"]
    assert result["unknown_capacity_nodes"] == ["a"]
    balance = {b["origin_id"]: b for b in result["balances"]}
    assert balance["u"]["assigned_tonnes"] is None
    assert balance["x"]["reason"] == "candidate_capacity_unknown"
    assert balance["z"]["reason"] == "no_reachable_candidate"
    unbounded = allocate(
        {"x": 10, "u": None, "z": 5},
        {"a": None},
        access,
        "min_cost_max_served",
        "unbounded_and_flag",
        1e-6,
    )
    assert unbounded["known_assigned_tonnes"]["a"] == 10
    assert unbounded["unknown_capacity_nodes"] == ["a"]


@pytest.mark.parametrize(
    "values",
    [
        [],
        [{"origin_id": "x", "node_id": "a", "minutes": -1}],
        [{"origin_id": "x", "node_id": "a", "minutes": float("nan")}],
    ],
)
def test_bad_routes_fail(values):
    with pytest.raises(ValueError):
        allocate({"x": 1}, {"a": 1}, values, "min_cost_max_served", "exclude_and_flag", 1e-6)


@pytest.mark.parametrize(
    "tags,mode,status",
    [
        ({"access": "no", "foot": "yes"}, "foot", "retained"),
        ({"access": "yes", "hgv": "no"}, "vehicle", "access_restricted_or_unresolved"),
        ({"access": "private"}, "vehicle", "access_restricted_or_unresolved"),
        ({"hgv:conditional": "no @ wet"}, "vehicle", "unsupported_restriction_review"),
        ({"access:forward": "no"}, "vehicle", "unsupported_restriction_review"),
        ({"maxweight": "10"}, "vehicle", "unsupported_restriction_review"),
        ({"maxspeed": "signals"}, "vehicle", "maxspeed_unresolved"),
        ({"oneway": "reversible"}, "bicycle", "oneway_unresolved"),
        ({"surface": "unknown"}, "vehicle", "surface_unconfigured"),
        ({"highway": "path"}, "vehicle", "unconfigured_highway"),
    ],
)
def test_mode_access_precedence_and_unsupported_tags(fixture, tags, mode, status):
    profile = fixture[0].transports[0].model_copy(update={"mode": mode})
    base = {"highway": "primary", "surface": "asphalt", "access": "yes"}
    base.update(tags)
    assert way_policy(base, profile, "dry")[1] == status


def test_speed_units_seasons_and_direction_rules(fixture):
    profile = fixture[0].transports[0]
    base = {
        "highway": "primary",
        "surface": "asphalt",
        "access": "yes",
        "oneway": "-1",
        "maxspeed": "10 mph",
    }
    result, _ = way_policy(base, profile, "dry")
    assert result[:2] == (False, True)
    assert result[2:] == pytest.approx((16.09344, 16.09344))
    assert way_policy({**base, "surface": "gravel"}, profile, "wet")[1] == "scenario_impassable"
    foot = profile.model_copy(update={"mode": "foot"})
    assert way_policy(base, foot, "dry")[0][:2] == (True, True)
    assert way_policy({**base, "oneway:foot": "-1"}, foot, "dry")[0][:2] == (False, True)


def test_directed_route_crs_snaps_and_parallel_edges(fixture):
    config, data = fixture
    profile = config.transports[0]
    road = data.roads[-2].model_copy(deep=True)
    road.tags["oneway"] = "yes"
    graph = build_network([road], profile, "dry", config.metric_crs)
    duplicated = build_network([road, road], profile, "dry", config.metric_crs)
    assert np.array_equal(graph.matrix.toarray(), duplicated.matrix.toarray())
    assert duplicated.audit["duplicate_ways"] == 1
    origin = data.origins[0]
    destination = data.sites[0].model_copy(update={"location": data.origins[1].location})
    access, snaps = accessibility(graph, [origin], [destination], profile, config.metric_crs)
    expected_km = np.linalg.norm(graph.coordinates[0] - graph.coordinates[1]) / 1000
    assert access[0]["minutes"] == pytest.approx(expected_km)  # 60 km/h => 1 minute/km
    reverse = origin.model_copy(update={"location": destination.location})
    target = destination.model_copy(update={"location": origin.location})
    assert (
        accessibility(graph, [reverse], [target], profile, config.metric_crs)[0][0]["minutes"]
        is None
    )
    far = destination.model_copy(update={"location": Point.model_validate(point(-110, 54))})
    assert (
        accessibility(graph, [origin], [far], profile, config.metric_crs)[0][0]["status"]
        == "snap_failure"
    )
    with pytest.raises(ValueError, match="projected"):
        projection("EPSG:4326")
    conflict = road.model_copy(deep=True)
    conflict.tags["oneway"] = "no"
    with pytest.raises(ValueError, match="conflicting duplicate"):
        build_network([road, conflict], profile, "dry", config.metric_crs)
    assert snaps[origin.origin_id]["metres"] == 0


def test_energy_hand_calculation_and_shared_limit(fixture):
    p = {name: param.central for name, param in fixture[0].parameters.items()}
    p.update(processing_fraction=0.5, simultaneous_fraction=0.25, auxiliary_power=2)
    req = requirement(2000, p)
    assert req["treated_tonnes_per_period"] == 1000
    assert req["inventory_tonnes"] == 100
    assert req["simultaneous_inventory_tonnes"] == 25
    assert req["airflow_m3_s"] == 0.05
    assert req["fan_kw"] == pytest.approx(0.0625)
    assert req["electrical_kw"] == pytest.approx(2.0625)
    assert req["electricity_kwh_one_cycle"] == pytest.approx(206.25)
    assert req["kwh_per_active_tonne_one_cycle"] == pytest.approx(8.25)
    assert annual_limit(200, p) == 2000
    assert annual_limit(None, p) is None
    assert all(v is None for v in requirement(None, p).values())
    assert requirement(0, p)["electrical_kw"] == 0


@pytest.mark.parametrize(
    "state,capacity,demand,margin,bucket",
    [
        ("no_documented_asset", None, 10, None, "undocumented_supply"),
        ("documented_unknown_capacity", None, 10, None, "verify_first"),
        ("documented_known_capacity", 5, 10, -5, "undersized"),
        ("documented_known_capacity", 15, 10, 5, None),
        ("documented_known_capacity", 5, None, None, "verify_first"),
    ],
)
def test_supply_states_signed_margins(state, capacity, demand, margin, bucket):
    result = gap(state, capacity, demand)
    assert result["capacity_minus_requirement_kw"] == margin
    assert result["bucket"] == bucket


def test_joint_draws_repeat_and_preserve_dependence(fixture):
    config = fixture[0]
    a, b = sample_parameters(config), sample_parameters(config)
    assert a == b and len(a) == 16
    assert all(8 <= p["residence_days"] <= 12 for p in a)
    assert np.corrcoef([p["airflow_per_tonne"] for p in a], [p["static_pressure"] for p in a])[
        0, 1
    ] == pytest.approx(1)
    assert sample_parameters(config.model_copy(update={"seed": 18})) != a


def test_approval_missing_values_wrong_units_and_holdout_fail(fixture):
    config, data = fixture
    with pytest.raises(ValueError, match="allow-fixture"):
        config.authorize(data)
    with pytest.raises(ValueError, match="identities"):
        config.authorize(
            data.model_copy(
                update={
                    "region_id": "AB",
                    "parents": [
                        data.parents[0].model_copy(update={"production_id": "actual:production"})
                    ],
                }
            ),
            allow_fixture=True,
        )
    real = config.model_copy(update={"purpose": "scientific_reviewed"})
    real_data = data.model_copy(update={"purpose": "scientific_reviewed", "provinces": ["AB"]})
    with pytest.raises(ValueError, match="human review"):
        real.authorize(real_data, allow_fixture=True)
    with pytest.raises(ValueError, match="Manitoba"):
        real.authorize(real_data.model_copy(update={"provinces": ["MB"]}))
    raw = config.model_dump(mode="json")
    raw["parameters"]["static_pressure"]["unit"] = "kWh"
    with pytest.raises(ValidationError, match="wrong parameter unit"):
        ScenarioConfig.model_validate(raw)
    with pytest.raises(ValueError, match="scientific gate"):
        load_config(Path("configs/scenarios/phase6-canada-v1.review.json"))


def test_parent_mass_join_and_supply_mismatch_are_rejected(fixture):
    _, data = fixture
    raw = data.model_dump(mode="json")
    raw["origins"][0]["fraction"] = 0.5
    with pytest.raises(ValidationError, match="conserve"):
        Dataset.model_validate(raw)
    raw = data.model_dump(mode="json")
    raw["sites"][0]["supply_state"] = "no_documented_asset"
    with pytest.raises(ValidationError, match="supply state"):
        Dataset.model_validate(raw)


@pytest.fixture(scope="module")
def complete_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("phase6")
    config, data = make_fixture()
    write_json(root / "config.json", config)
    write_json(root / "data.json", data)
    result = execute(
        root / "config.json", root / "data.json", root / "run", Path("uv.lock"), allow_fixture=True
    )
    return root, result


def test_complete_offline_replay_and_tiers(complete_run, monkeypatch):
    def offline(*args, **kwargs):
        raise AssertionError("science run attempted network access")

    monkeypatch.setattr(socket, "socket", offline)
    monkeypatch.setattr(socket, "create_connection", offline)
    root, result = complete_run
    assert result["draws"] == 64 and result["shortlist"] == 10
    assert verify(root / "run", Path("uv.lock"))["status"] == "verified"
    ranking = json.loads((root / "run/ranking.json").read_bytes())
    assert ranking["metadata"]["scientifically_ready_to_freeze"] is False
    assert ranking["metadata"]["purpose"] == "synthetic_fixture"
    assert {r["tier"] for r in ranking["data"]} == {"Robust", "Contested", "Verify-first"}
    for row in ranking["data"]:
        assert 0 <= row["inclusion_frequency"] <= 1
        if row["node_id"] == "fixture:site_unknown":
            assert row["tier"] == "Verify-first" and row["rank"] is None
            assert row["magnitude"]["electrical_kw"]["median"] is None
        if row["margin_kw"]["known_draws"] == 0:
            assert row["margin_kw"]["median"] is None
    draws = json.loads((root / "run/draws.json").read_bytes())["data"]
    for draw in draws:
        known = [b for b in draw["allocation"]["balances"] if b["input_tonnes"] is not None]
        assert fsum(b["assigned_tonnes"] + b["unserved_tonnes"] for b in known) == pytest.approx(
            700
        )
    comparisons = json.loads((root / "run/ablations.json").read_bytes())["data"]
    assert any(
        r["factor"] == "season" and r["max_membership_symmetric_difference"] > 0
        for r in comparisons
    )
    assert all(r["retention_decision"] == "not_made_by_engine" for r in comparisons)


def test_input_permutation_leaves_numerical_results_unchanged(fixture):
    config, data = fixture
    result = calculate(config, data, allow_fixture=True)
    permuted = data.model_copy(
        update={
            name: list(reversed(getattr(data, name)))
            for name in ("sites", "origins", "parents", "roads")
        }
    )
    assert calculate(config, permuted, allow_fixture=True) == result


def test_run_protects_existing_outputs_and_verifier_rejects_rehashed_tamper(complete_run, tmp_path):
    import shutil

    root, _ = complete_run
    with pytest.raises(ValueError, match="new or empty"):
        execute(
            root / "config.json",
            root / "data.json",
            root / "run",
            Path("uv.lock"),
            allow_fixture=True,
        )
    output = tmp_path / "tampered"
    shutil.copytree(root / "run", output)
    ranking = json.loads((output / "ranking.json").read_bytes())
    ranking["data"][0]["inclusion_frequency"] = 0
    write_json(output / "ranking.json", ranking)
    index = json.loads((output / "index.json").read_bytes())
    for entry in index["artifacts"]:
        if entry["path"] == "ranking.json":
            entry["sha256"] = file_hash(output / entry["path"])
    write_json(output / "index.json", index)
    with pytest.raises(ValueError, match="replay mismatch"):
        verify(output, Path("uv.lock"))


def test_checked_in_fixtures_match_source_generator(fixture):
    config, data = fixture
    assert config == ScenarioConfig.model_validate_json(
        Path("tests/fixtures/phase6-synthetic-config.json").read_bytes()
    )
    assert data == Dataset.model_validate_json(
        Path("tests/fixtures/phase6-synthetic-inputs.json").read_bytes()
    )
