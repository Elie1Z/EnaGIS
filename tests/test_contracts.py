"""Invalid external inputs must fail visibly, rather than being repaired silently."""

from copy import deepcopy

import pytest
from pydantic import ValidationError

from enagis.contracts import (
    Artifact,
    Capacity,
    Node,
    Point,
    Quantity,
    ScientificParameter,
    SitingFeature,
    Value,
)
from enagis.validation import Bundle, compare_quantities


@pytest.mark.parametrize("label", ["OBSERVED", "PREDICTED", "ESTIMATED", "INFERRED"])
def test_evidence_labels_are_preserved(raw_bundle, label):
    item = deepcopy(raw_bundle["production"][0]["modeled_tonnes"])
    item["evidence"]["label"] = label
    assert Value[float].model_validate(item).evidence.label == label


@pytest.mark.parametrize("mutation", ["no_reason", "known_label", "zero_unknown", "invalid_label"])
def test_unknown_is_never_zero(raw_suite, mutation):
    item = deepcopy(raw_suite["cases"][3]["bundle"]["capacities"][0]["original"]["amount"])
    if mutation == "no_reason":
        item["evidence"]["missing_reason"] = None
    elif mutation == "known_label":
        item["evidence"]["label"] = "OBSERVED"
    elif mutation == "zero_unknown":
        item["value"] = 0.0
    else:
        item["evidence"]["label"] = "ASSUMED"
    with pytest.raises(ValidationError):
        Value[float].model_validate(item)


@pytest.mark.parametrize("mutation", ["swap", "crs", "order", "infinity", "precision"])
def test_spatial_failures(raw_bundle, mutation):
    location = raw_bundle["nodes"][0]["location"]
    point = location["point"]["value"]
    if mutation == "swap":
        point["longitude"], point["latitude"] = point["latitude"], point["longitude"]
    elif mutation == "crs":
        point["crs"] = "EPSG:3347"
    elif mutation == "order":
        point["coordinate_order"] = "latitude_longitude"
    elif mutation == "infinity":
        point["longitude"] = float("inf")
    else:
        location["precision"] = "P5"
    with pytest.raises(ValidationError):
        Node.model_validate(raw_bundle["nodes"][0])


@pytest.mark.parametrize("crs", ["EPSG:4326", "EPSG:4269", "EPSG:999999"])
def test_metric_crs_must_be_real_and_projected(raw_bundle, crs):
    raw_bundle["travel"][0]["metric_crs"] = crs
    with pytest.raises(ValidationError):
        Bundle.model_validate(raw_bundle)


def test_geographic_keys_include_vintage(raw_bundle):
    from enagis.contracts import SpatialID

    geo = SpatialID.model_validate(raw_bundle["production"][0]["geography"])
    assert geo.key == "CA:toy_ccs:2021:Z1"


@pytest.mark.parametrize("field", ["facility_id", "source_record_id", "snapshot_id"])
def test_required_identity(raw_bundle, field):
    raw_bundle["facilities"][0][field] = ""
    with pytest.raises(ValidationError):
        Bundle.model_validate(raw_bundle)


@pytest.mark.parametrize("mutation", ["extra", "duplicate", "orphan", "bare_objectid", "source"])
def test_registry_integrity(raw_bundle, mutation):
    if mutation == "extra":
        raw_bundle["facilities"][0]["capacity"] = 42
    elif mutation == "duplicate":
        raw_bundle["nodes"].append(deepcopy(raw_bundle["nodes"][0]))
    elif mutation == "orphan":
        raw_bundle["nodes"][0]["facility_id"] = "not-present"
    elif mutation == "bare_objectid":
        raw_bundle["facilities"][0]["source_record_id"] = "12"
    else:
        raw_bundle["facilities"][0]["name"]["evidence"]["source_ids"] = ["missing-source"]
    with pytest.raises(ValidationError):
        Bundle.model_validate(raw_bundle)


@pytest.mark.parametrize(
    "unit,dimension", [("tonne/day", "mass_flow"), ("m3/s", "airflow"), ("tonne", "storage_mass")]
)
def test_power_cannot_compare_to_mass_flow_or_airflow(raw_bundle, unit, dimension):
    capacity = deepcopy(raw_bundle["capacities"][0]["original"])
    capacity.update(unit=unit, dimension=dimension)
    if dimension == "mass_flow":
        capacity.update(period_start="2024-08-01", period_end="2025-07-31")
    power = Quantity.model_validate(raw_bundle["capacities"][0]["original"])
    with pytest.raises(ValueError, match="incompatible"):
        compare_quantities(Quantity.model_validate(capacity), power)


def test_zero_capacity_is_known_not_missing(raw_bundle):
    item = deepcopy(raw_bundle["capacities"][0])
    item["original"]["amount"]["value"] = 0.0
    assert Capacity.model_validate(item).status == "known"


def test_unknown_capacity_cannot_compare(raw_suite, raw_bundle):
    unknown = Quantity.model_validate(raw_suite["cases"][3]["bundle"]["capacities"][0]["original"])
    known = Quantity.model_validate(raw_bundle["capacities"][0]["original"])
    with pytest.raises(ValueError, match="unknown"):
        compare_quantities(unknown, known)


@pytest.mark.parametrize("mutation", ["dimension", "negative", "nan", "capacity_status", "period"])
def test_quantity_validation(raw_bundle, mutation):
    item = raw_bundle["capacities"][0]
    if mutation == "dimension":
        item["original"]["dimension"] = "storage_mass"
    elif mutation == "negative":
        item["original"]["amount"]["value"] = -1
    elif mutation == "nan":
        item["original"]["amount"]["value"] = float("nan")
    elif mutation == "capacity_status":
        item["status"] = "unknown"
    else:
        item["original"]["period_end"] = "2025-07-31"
    with pytest.raises(ValidationError):
        Capacity.model_validate(item)


@pytest.mark.parametrize("mutation", ["factor", "converted", "original", "date"])
def test_kilotonne_conversion_rejects_bad_arithmetic(raw_bundle, mutation):
    conv = raw_bundle["outcomes"][0]["conversion"]
    if mutation == "factor":
        conv["factor"] = 1.0
        conv["converted"]["amount"]["value"] = conv["original"]["amount"]["value"]
    elif mutation == "converted":
        conv["converted"]["amount"]["value"] = 12000
    elif mutation == "original":
        conv["original"]["amount"]["value"] = 0.024
        conv["converted"]["amount"]["value"] = 24.0
    else:
        conv["converted"]["period_end"] = "2025-06-01"
    with pytest.raises(ValidationError):
        Bundle.model_validate(raw_bundle)


@pytest.mark.parametrize(
    "feature",
    [
        "allocation",
        "capacity",
        "deliveries",
        "energy",
        "gap",
        "supply",
        "verification",
        "processor_distance",
        "night_lights",
    ],
)
def test_blocked_siting_features(feature):
    with pytest.raises(ValidationError):
        SitingFeature(
            feature_id=feature,
            source_ids=["s"],
            unit="x",
            construction_method="x",
            upstream_label_free=True,
        )


def test_transfer_cannot_fit_preprocessing_or_select_models(raw_bundle):
    for field in ("feature_fit_allowed", "model_selection_allowed"):
        changed = deepcopy(raw_bundle)
        changed["partitions"][1][field] = True
        with pytest.raises(ValidationError, match="transfer"):
            Bundle.model_validate(changed)


def test_transfer_outcome_cannot_be_relabelled_as_development(raw_bundle):
    raw_bundle["outcomes"][0]["province"] = "MB"
    with pytest.raises(ValidationError, match="frozen regional split"):
        Bundle.model_validate(raw_bundle)


def test_holdout_partition_cannot_be_relabelled_as_development(raw_bundle):
    raw_bundle["partitions"][1]["split"] = "development"
    with pytest.raises(ValidationError, match="frozen regional split"):
        Bundle.model_validate(raw_bundle)


def test_logistics_requirement_stays_unknown(raw_suite):
    bundle = deepcopy(raw_suite["cases"][5]["bundle"])
    bundle["requirements"][0]["electrical_kw"] = deepcopy(
        raw_suite["cases"][0]["bundle"]["requirements"][0]["electrical_kw"]
    )
    with pytest.raises(ValidationError, match="stationary requirement"):
        Bundle.model_validate(bundle)


def test_scientific_parameter_gate(raw_bundle):
    item = raw_bundle["capacities"][0]["original"]["amount"]
    parameter = ScientificParameter(
        parameter_id="fan-efficiency",
        unit="fraction",
        value=item,
        approved_by=None,
        approved_on=None,
    )
    with pytest.raises(ValueError, match="unapproved"):
        parameter.require_approved()
    parameter.approved_by = "Human fixture reviewer"
    parameter.approved_on = parameter.value.evidence.as_of
    assert parameter.require_approved() == 6.0


def test_standalone_artifact_carries_run_metadata(raw_bundle):
    artifact = Artifact[Node].model_validate(
        {"metadata": raw_bundle["metadata"], "rows": raw_bundle["nodes"]}
    )
    assert artifact.metadata.schema_version == "1.0.0"


def test_point_schema_has_named_lon_lat(raw_bundle):
    point = Point.model_validate(raw_bundle["nodes"][0]["location"]["point"]["value"])
    assert (point.longitude, point.latitude) == (-110.0, 52.0)
