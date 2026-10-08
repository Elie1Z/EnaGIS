"""Portable kernels are checked with synthetic geography, never claimed transfer skill."""

from types import SimpleNamespace

import numpy as np
import pytest
from phase6_fixture import make_fixture, value
from pydantic import ValidationError
from pyproj import Geod

from enagis.science.contracts import Approval, Dataset, ScenarioConfig
from enagis.science.geography import inside_area, metric_projection, projection
from enagis.science.roads import project_points
from enagis.science.runner import calculate
from enagis.science.uncertainty import ablations
from enagis.science.unit_review import BushelAirflow, convert_airflow

LOCATIONS = [
    ("East Africa", "EPSG:32736", 32, -2),
    ("South America", "EPSG:32722", -50, -23),
    ("South Asia", "EPSG:32643", 76, 18),
    ("Oceania", "EPSG:32756", 152, -32),
    ("Europe", "EPSG:32632", 10, 48),
]


def relocated_fixture(crs, longitude, latitude):
    config, data = make_fixture()
    cfg, raw = config.model_dump(mode="json"), data.model_dump(mode="json")
    cfg["metric_crs"] = crs
    cfg["scenario_id"] = "fixture:portable"
    raw["region_id"] = "fixture:portable"

    def move(lon, lat):
        return longitude + (lon + 106) * 0.1, latitude + (lat - 52) * 0.1

    for road in raw["roads"]:
        road["coordinates_lon_lat"] = [move(*p) for p in road["coordinates_lon_lat"]]
    for endpoint in [*raw["origins"], *raw["sites"]]:
        p = endpoint["location"]
        p["longitude"], p["latitude"] = move(p["longitude"], p["latitude"])
    return ScenarioConfig.model_validate(cfg), Dataset.model_validate(raw)


@pytest.mark.parametrize("name,crs,longitude,latitude", LOCATIONS)
def test_same_pipeline_on_non_canadian_synthetic_geography(name, crs, longitude, latitude):
    config, data = relocated_fixture(crs, longitude, latitude)
    result = calculate(config, data, allow_fixture=True)
    assert len(result["shortlist"]) == 10
    assert len(result["draws"]) == 64
    for draw in result["draws"]:
        balances = draw["allocation"]["balances"]
        assert sum(
            b["assigned_tonnes"] + b["unserved_tonnes"]
            for b in balances
            if b["input_tonnes"] is not None
        ) == pytest.approx(700)
        assert sum(b["input_tonnes"] is None for b in balances) == 1
    # Fixture configurations do not authorize real transfer evaluations.
    config.purpose = "scientific_reviewed"
    real = data.model_copy(update={"purpose": "scientific_reviewed", "provinces": ["LOCAL"]})
    with pytest.raises(ValueError, match="new protocol"):
        config.authorize(real)


@pytest.mark.parametrize("name,crs,longitude,latitude", LOCATIONS)
def test_local_projected_distance_matches_geodesic_at_fixture_locations(
    name, crs, longitude, latitude
):
    pairs = [(longitude, latitude), (longitude + 0.01, latitude)]
    xy = project_points(projection(crs), pairs)
    distance = np.linalg.norm(xy[1] - xy[0])
    geodesic = Geod(ellps="WGS84").inv(*pairs[0], *pairs[1])[2]
    assert distance == pytest.approx(geodesic, rel=0.002)


@pytest.mark.parametrize(
    "crs,reason",
    [
        ("EPSG:4326", "projected"),
        ("EPSG:3857", "display CRS"),
        ("EPSG:2263", "metres"),
        ("EPSG:4978", "projected"),
    ],
)
def test_inappropriate_distance_crs_rejected(crs, reason):
    with pytest.raises(ValueError, match=reason):
        metric_projection(crs)


def test_area_of_use_is_selected_region_and_antimeridian_is_supported():
    with pytest.raises(ValueError, match="area of use"):
        project_points(projection("EPSG:32736"), [(-106, 52)])
    area = SimpleNamespace(west=170, east=-170, south=-50, north=0)
    assert inside_area(175, -20, area) and inside_area(-175, -20, area)
    assert not inside_area(0, -20, area)
    assert not inside_area(float("nan"), -20, area)


@pytest.mark.parametrize(
    "region,crs", [("fixture:elsewhere", "EPSG:3347"), ("ca-prairies", "EPSG:32736")]
)
def test_portable_projection_does_not_bypass_real_canadian_scope(region, crs):
    config, data = make_fixture()
    # Invented test approval exercises validation order; it is never a real run artifact.
    approval = Approval(
        approved_by="fixture:reviewer",
        approved_on="2026-10-08",
        statement="Synthetic authorization validation test only",
        applicability="fixture only",
    )
    config.purpose = "scientific_reviewed"
    config.metric_crs = crs
    config.methods_approval = approval
    config.ranking.approval = approval
    data.prepared_from_sha256 = {s.snapshot_id: s.sha256 for s in data.source_snapshots}
    data.purpose = "scientific_reviewed"
    data.provinces = ["AB", "SK"]
    data.region_id = region
    data.data_approval = approval
    with pytest.raises(ValueError, match="real Canada benchmark"):
        config.authorize(data)


def airflow_input(
    mass=30, airflow_basis="winchester", mass_basis="winchester", review="fixture:review"
):
    return BushelAirflow(
        airflow_cfm_per_bushel=value(0.1),
        airflow_bushel_basis=airflow_basis,
        test_weight_kg_per_bushel=value(mass),
        test_weight_bushel_basis=mass_basis,
        applicability="Synthetic dimensional example; no recommended test weight",
        basis_review_ref=review,
    )


def test_bushel_conversion_uses_specific_mass_and_retains_full_provenance():
    conversion = convert_airflow(airflow_input())
    assert conversion.amount.value == pytest.approx(0.001573158144)
    assert conversion.amount.evidence.label == "ESTIMATED"
    assert conversion.input.test_weight_kg_per_bushel.evidence.source_ids == ["fixture:source"]
    assert convert_airflow(airflow_input(15)).amount.value == pytest.approx(
        2 * conversion.amount.value
    )


@pytest.mark.parametrize(
    "entry",
    [
        {"mass": None},
        {"airflow_basis": "source_unspecified"},
        {"mass_basis": "avery"},
        {"review": None},
    ],
)
def test_unknown_or_mismatched_bushel_never_yields_numeric_airflow(entry):
    conversion = convert_airflow(airflow_input(**entry))
    assert conversion.amount.value is None
    assert conversion.amount.evidence.label == "UNKNOWN"
    assert conversion.amount.evidence.missing_reason


def test_zero_mass_cannot_be_used_as_a_bushel_conversion():
    with pytest.raises(ValidationError, match="positive"):
        airflow_input(0)


@pytest.mark.parametrize(
    "after,replaced,removed,added",
    [
        (["b", "c", "d"], 1, 1, 1),
        (["c"], 0, 2, 0),
        (["a", "b", "c", "d"], 0, 0, 1),
    ],
)
def test_ablation_counts_replacements_and_shortlist_size_changes_separately(
    after, replaced, removed, added
):
    base = {"draw_id": 0, "profile_id": "fixture:vehicle", "assignment_variant": "nearest_first"}
    draws = [
        {**base, "case_id": "a", "season": "dry", "top_k": ["a", "b", "c"]},
        {**base, "case_id": "b", "season": "wet", "top_k": after},
    ]
    result = ablations(draws, SimpleNamespace(reference_case="a"))[0]
    assert result["mean_replacements"] == replaced
    assert result["mean_removed"] == removed
    assert result["mean_added"] == added
    assert result["mean_membership_symmetric_difference"] == removed + added
    assert result["compares_declared_reference"] is True
    assert result["retention_decision"] == "not_made_by_engine"
