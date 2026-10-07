"""Strict, region-independent interchange contracts; no scientific defaults."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator
from pyproj import CRS

from enagis import SCHEMA_VERSION

ID = Annotated[str, Field(min_length=1, pattern=r"^\S+$")]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Hash = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Finite = Annotated[float, Field(allow_inf_nan=False)]
Label = Literal["OBSERVED", "PREDICTED", "ESTIMATED", "INFERRED", "UNKNOWN"]
Precision = Literal["P1", "P2", "P3", "P4", "P5"]
Dimension = Literal["storage_mass", "mass_flow", "airflow", "electric_power", "energy"]
Unit = Literal["tonne", "kilotonne", "tonne/day", "m3/s", "kW", "kWh"]
UNIT_DIMENSION = {
    "tonne": "storage_mass",
    "kilotonne": "storage_mass",
    "tonne/day": "mass_flow",
    "m3/s": "airflow",
    "kW": "electric_power",
    "kWh": "energy",
}


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, allow_inf_nan=False)


class Evidence(Contract):
    label: Label
    source_ids: list[ID] = Field(min_length=1)
    as_of: date
    licence: Text
    method: Text
    missing_reason: Text | None


class Value[T](Contract):
    value: T | None
    evidence: Evidence

    @model_validator(mode="after")
    def missingness(self):
        if self.value is None:
            if self.evidence.label != "UNKNOWN" or not self.evidence.missing_reason:
                raise ValueError("null requires UNKNOWN and an explicit missing_reason")
        elif self.evidence.label == "UNKNOWN" or self.evidence.missing_reason is not None:
            raise ValueError("known value cannot have UNKNOWN evidence or missing_reason")
        return self


class Snapshot(Contract):
    snapshot_id: ID
    publisher: Text
    original_url: Text
    retrieved_on: date
    effective_on: date
    sha256: Hash
    licence: Text
    licence_url: Text
    redistribution: Literal["permitted", "restricted", "unresolved"]
    processing_step: Text


class RunMetadata(Contract):
    schema_version: Literal[SCHEMA_VERSION]
    run_id: ID
    region_id: ID
    commodity_id: ID
    service_id: ID
    scenario_id: ID
    period_start: date
    period_end: date
    config_sha256: Hash
    input_snapshot_ids: list[ID] = Field(min_length=1)
    seed: int | None = Field(ge=0)

    @model_validator(mode="after")
    def period(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end precedes period_start")
        return self


class Artifact[T](Contract):
    metadata: RunMetadata
    rows: list[T]


class SpatialID(Contract):
    country_code: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    geography_type: ID
    boundary_vintage: ID
    code: ID
    source_geographic_id: ID

    @property
    def key(self) -> str:
        return ":".join((self.country_code, self.geography_type, self.boundary_vintage, self.code))


class Point(Contract):
    crs: Literal["EPSG:4326"]
    coordinate_order: Literal["longitude_latitude"]
    longitude: Annotated[float, Field(ge=-180, le=180, allow_inf_nan=False)]
    latitude: Annotated[float, Field(ge=-90, le=90, allow_inf_nan=False)]
    source_crs: Annotated[str, Field(pattern=r"^EPSG:[0-9]+$")]
    transformation_method: Text


class Location(Contract):
    point: Value[Point]
    precision: Precision

    @model_validator(mode="after")
    def unlocated(self):
        if (self.point.value is None) != (self.precision == "P5"):
            raise ValueError("P5 must be unlocated; P1-P4 require a representative point")
        return self


class Facility(Contract):
    facility_id: ID
    source_record_id: ID
    snapshot_id: ID
    name: Value[Text]
    operator: Value[Text]
    facility_class: Value[Text]
    status_as_stated: Value[Text]
    effective_on: date
    location: Location


class Node(Contract):
    node_id: ID
    facility_id: ID | None
    facility_missing_reason: Text | None
    node_type: Literal["storage", "processing", "logistics_only", "candidate"]
    origin: Literal["documented", "rule_based"]
    existence: Value[Literal["documented", "confirmed"]]
    stationary_service_eligible: bool | None
    eligibility_evidence: Evidence
    location: Location
    verification_question: Text

    @model_validator(mode="after")
    def eligibility(self):
        Value[bool](value=self.stationary_service_eligible, evidence=self.eligibility_evidence)
        if (self.facility_id is None) != (self.facility_missing_reason is not None):
            raise ValueError("missing facility link needs a reason")
        if self.node_type == "logistics_only" and self.stationary_service_eligible is not False:
            raise ValueError("logistics-only nodes cannot assume stationary service")
        return self


class Quantity(Contract):
    amount: Value[Nonnegative]
    unit: Unit
    dimension: Dimension
    definition: Text
    period_start: date | None
    period_end: date | None

    @model_validator(mode="after")
    def dimensions(self):
        if UNIT_DIMENSION[self.unit] != self.dimension:
            raise ValueError("unit does not match dimension")
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("quantity period must have both endpoints")
        if self.period_start and self.period_end < self.period_start:
            raise ValueError("invalid quantity period")
        if self.dimension in ("mass_flow", "energy") and self.period_start is None:
            raise ValueError("flow and energy require a reporting period")
        return self


class Conversion(Contract):
    original: Quantity
    converted: Quantity
    factor: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    reviewed_by: Text
    evidence: Evidence

    @model_validator(mode="after")
    def conservation(self):
        from math import isclose

        if self.original.dimension != self.converted.dimension:
            raise ValueError("conversion cannot change dimension")
        factors = {("kilotonne", "tonne"): 1000.0, ("tonne", "kilotonne"): 0.001}
        if self.original.unit == self.converted.unit:
            expected_factor = 1.0
        else:
            expected_factor = factors.get((self.original.unit, self.converted.unit))
        if expected_factor is None or self.factor != expected_factor:
            raise ValueError("unsupported or incorrect unit conversion factor")
        if (self.original.period_start, self.original.period_end) != (
            self.converted.period_start,
            self.converted.period_end,
        ):
            raise ValueError("conversion cannot change the reporting period")
        left, right = self.original.amount.value, self.converted.amount.value
        if left is None or right is None or not isclose(left * self.factor, right, rel_tol=1e-12):
            raise ValueError("conversion arithmetic mismatch or unknown input")
        return self


class Capacity(Contract):
    capacity_id: ID
    node_id: ID
    facility_id: ID | None
    service_id: ID
    status: Literal["known", "unknown"]
    original: Quantity
    conversion: Conversion | None

    @model_validator(mode="after")
    def known(self):
        if (self.original.amount.value is None) != (self.status == "unknown"):
            raise ValueError("capacity status disagrees with value")
        if self.conversion and self.conversion.original != self.original:
            raise ValueError("conversion must retain the source capacity")
        return self


class Production(Contract):
    production_id: ID
    geography: SpatialID
    geometry_ref: ID
    geometry_crs: Annotated[str, Field(pattern=r"^EPSG:[0-9]+$")]
    commodity_id: ID
    original: Quantity
    conversion: Conversion | None
    modeled_tonnes: Value[Nonnegative]
    spatial_allocation_method: Text

    @model_validator(mode="after")
    def production_units(self):
        if self.original.dimension != "storage_mass" or self.original.period_start is None:
            raise ValueError("production requires mass and reporting period")
        if (
            self.modeled_tonnes.value is not None
            and self.modeled_tonnes.evidence.label != "ESTIMATED"
        ):
            raise ValueError("modeled production is ESTIMATED")
        if self.conversion and self.conversion.original != self.original:
            raise ValueError("conversion must retain original production")
        return self


class Travel(Contract):
    origin_id: ID
    node_id: ID
    graph_snapshot_id: ID
    scenario_id: ID
    mode: ID
    travel_minutes: Value[Nonnegative]
    reachable: bool | None
    metric_crs: Annotated[str, Field(pattern=r"^EPSG:[0-9]+$")]

    @model_validator(mode="after")
    def reachability(self):
        if (self.travel_minutes.value is not None) != (self.reachable is True):
            raise ValueError("unreachable/unknown travel must stay null")
        try:
            projection = CRS.from_user_input(self.metric_crs)
        except Exception as error:
            raise ValueError("unrecognized metric CRS") from error
        if not projection.is_projected or any(
            axis.unit_name != "metre" for axis in projection.axis_info
        ):
            raise ValueError("metric calculations require a projected CRS in metres")
        return self


class Catchment(Contract):
    origin_id: ID
    node_id: ID
    scenario_id: ID
    travel_limit_minutes: Nonnegative
    travel_minutes: Nonnegative
    method_ref: ID
    evidence: Evidence

    @model_validator(mode="after")
    def inside(self):
        if self.travel_minutes > self.travel_limit_minutes:
            raise ValueError("catchment member exceeds configured travel limit")
        return self


class Allocation(Contract):
    allocation_id: ID
    production_id: ID
    node_id: ID | None
    unserved_reason: Text | None
    scenario_id: ID
    assigned_tonnes: Value[Nonnegative]
    inventory_scenario_ref: ID

    @model_validator(mode="after")
    def destination(self):
        if (self.node_id is None) != (self.unserved_reason is not None):
            raise ValueError("allocation must name a node or an explicit unserved reason")
        if self.assigned_tonnes.value is None:
            raise ValueError("an allocation must specify assigned mass")
        return self


class Inventory(Contract):
    node_id: ID
    stored_tonnes: Value[Nonnegative]
    residence_scenario_ref: ID
    occupancy_scenario_ref: ID


class Range(Contract):
    lower: Nonnegative
    central: Nonnegative
    upper: Nonnegative
    distribution_ref: ID

    @model_validator(mode="after")
    def ordering(self):
        if not self.lower <= self.central <= self.upper:
            raise ValueError("range must be ordered")
        return self


class Requirement(Contract):
    node_id: ID
    service_id: ID
    inventory_scenario_ref: ID
    electrical_kw: Value[Range]
    electricity_kwh: Value[Range]
    cycle_or_period: Text
    peak_power_method: Text
    parameter_refs: list[ID] = Field(min_length=1)

    @model_validator(mode="after")
    def estimated(self):
        for item in (self.electrical_kw, self.electricity_kwh):
            if item.value is not None and item.evidence.label != "ESTIMATED":
                raise ValueError("modeled requirement must preserve ESTIMATED evidence")
        return self


SupplyState = Literal[
    "no_documented_asset", "documented_known_capacity", "documented_unknown_capacity"
]
GapBucket = Literal["undocumented_supply", "undersized", "verify_first"]


class Supply(Contract):
    node_id: ID
    service_id: ID
    state: SupplyState
    evidence: Evidence
    capacity_ref: ID | None
    documentation_scope: Text

    @model_validator(mode="after")
    def documented_capacity(self):
        if (self.capacity_ref is not None) != (self.state != "no_documented_asset"):
            raise ValueError("documented supply requires a capacity record, even when unknown")
        return self


class Gap(Contract):
    node_id: ID
    service_id: ID
    dimension: Literal["electric_power"]
    unit: Literal["kW"]
    capacity_minus_requirement_kw: Value[Finite]
    bucket: GapBucket | None
    classification: Literal["flagged", "unflagged", "unknown"]
    classification_evidence: Evidence
    policy_ref: ID

    @model_validator(mode="after")
    def classified(self):
        if (self.bucket is not None) != (self.classification == "flagged"):
            raise ValueError("only flagged classifications carry a bucket")
        if self.bucket == "undersized":
            margin = self.capacity_minus_requirement_kw.value
            if margin is None or margin >= 0:
                raise ValueError("undersized needs a negative comparable margin")
        return self


Tier = Literal["robust", "contested", "verify_first"]


class Uncertainty(Contract):
    node_id: ID
    seed: int = Field(ge=0)
    draw_count: int = Field(gt=0)
    included_draws: int = Field(ge=0)
    inclusion_frequency: Annotated[float, Field(ge=0, le=1)]
    tier: Tier
    policy_ref: ID
    joint_scenario_refs: list[ID] = Field(min_length=1)
    magnitude_kw: Value[Range]
    evidence: Evidence

    @model_validator(mode="after")
    def frequency(self):
        from math import isclose

        if self.included_draws > self.draw_count or not isclose(
            self.inclusion_frequency, self.included_draws / self.draw_count, abs_tol=1e-12
        ):
            raise ValueError("inclusion frequency must match draw counts")
        return self


class NodeCard(Contract):
    node_id: ID
    rank: int = Field(gt=0)
    tier: Tier
    location: Location
    requirement: Requirement
    supply: Supply
    gap: Gap
    evidence: Evidence
    verification_question: Text
    freeze_id: ID
    shortlist_version: ID
    shortlist_sha256: Hash

    @model_validator(mode="after")
    def references(self):
        if any(row.node_id != self.node_id for row in (self.requirement, self.supply, self.gap)):
            raise ValueError("node-card references disagree")
        services = {row.service_id for row in (self.requirement, self.supply, self.gap)}
        if len(services) != 1:
            raise ValueError("node-card service references disagree")
        return self


class ShippingLink(Contract):
    facility_id: ID
    shipping_point_id: ID
    match_method: Text
    evidence: Evidence


class Outcome(Contract):
    outcome_id: ID
    shipping_point_id: ID
    province: ID
    split: Literal["development", "transfer"]
    original: Quantity
    conversion: Conversion

    @model_validator(mode="after")
    def reported_mass(self):
        if self.original != self.conversion.original:
            raise ValueError("outcome conversion must retain its original quantity")
        if self.original.amount.evidence.label != "OBSERVED":
            raise ValueError("outcome requires OBSERVED source quantity")
        if self.conversion.converted.unit != "tonne" or self.original.period_start is None:
            raise ValueError("outcome requires reporting period and converted tonnes")
        return self


class SitingFeature(Contract):
    feature_id: Literal[
        "production", "accessibility", "population", "road_class", "junctions", "town"
    ]
    source_ids: list[ID] = Field(min_length=1)
    unit: Text
    construction_method: Text
    upstream_label_free: Literal[True]


class Partition(Contract):
    spatial_id: SpatialID
    region_unit_id: ID
    block_id: ID
    split: Literal["development", "transfer"]
    feature_fit_allowed: bool
    model_selection_allowed: bool

    @model_validator(mode="after")
    def transfer_is_untouched(self):
        if self.split == "transfer" and (self.feature_fit_allowed or self.model_selection_allowed):
            raise ValueError("transfer data cannot fit preprocessing or select models")
        return self


class RegionConfig(Contract):
    region_id: ID
    country_code: Annotated[str, Field(pattern=r"^[A-Z]{2}$")]
    development_units: list[ID] = Field(min_length=1)
    transfer_units: list[ID] = Field(min_length=1)
    adapter_version: ID
    boundary_vintage: ID
    point_crs: Literal["EPSG:4326"]
    metric_crs: Annotated[str, Field(pattern=r"^EPSG:[0-9]+$")]
    projection_review_ref: ID

    @model_validator(mode="after")
    def disjoint(self):
        if set(self.development_units) & set(self.transfer_units):
            raise ValueError("development and transfer regions must be disjoint")
        for units in (self.development_units, self.transfer_units):
            if len(units) != len(set(units)):
                raise ValueError("duplicate region unit")
        return self

    def split_for(self, region_unit_id: str) -> str:
        if region_unit_id in self.development_units:
            return "development"
        if region_unit_id in self.transfer_units:
            return "transfer"
        raise ValueError(f"region outside configured footprint: {region_unit_id}")


class ScientificParameter(Contract):
    parameter_id: ID
    unit: Text
    value: Value[Finite]
    approved_by: Text | None
    approved_on: date | None

    def require_approved(self) -> float:
        if self.value.value is None or not self.approved_by or not self.approved_on:
            raise ValueError(f"missing or unapproved scientific parameter: {self.parameter_id}")
        return self.value.value
