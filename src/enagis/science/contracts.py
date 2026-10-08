"""Explicit scientific choices. No production defaults or implicit approvals."""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from enagis.contracts import (
    ID,
    Contract,
    Evidence,
    Hash,
    Nonnegative,
    Point,
    Snapshot,
    Text,
    Value,
)
from enagis.data_contracts import RoadWay

PARAMETER_UNITS = {
    "residence_days": "day",
    "modeled_operating_days": "day",
    "wheat_storage_fraction": "fraction",
    "processing_fraction": "fraction",
    "airflow_per_tonne": "m3/s/tonne",
    "static_pressure": "Pa",
    "fan_efficiency": "fraction",
    "motor_efficiency": "fraction",
    "simultaneous_fraction": "fraction",
    "cycle_hours": "hour",
    "auxiliary_power": "kW",
}


class Approval(Contract):
    approved_by: Text
    approved_on: date
    statement: Text
    applicability: Text


class ParameterRange(Contract):
    unit: Text
    lower: Nonnegative
    central: Nonnegative
    upper: Nonnegative
    distribution: Literal["fixed", "triangular"]
    joint_group: ID
    evidence: Evidence
    approval: Approval | None

    @model_validator(mode="after")
    def range_order(self):
        if not self.lower <= self.central <= self.upper:
            raise ValueError("unordered parameter range")
        if (self.lower == self.upper) != (self.distribution == "fixed"):
            raise ValueError("fixed requires equal bounds; triangular requires a range")
        if self.evidence.label == "UNKNOWN" or self.evidence.missing_reason:
            raise ValueError("numeric parameter requires known evidence")
        return self


class Surface(Contract):
    dry: Nonnegative | None
    wet: Nonnegative | None

    @model_validator(mode="after")
    def multiplier(self):
        if any(v is not None and not 0 < v <= 1 for v in (self.dry, self.wet)):
            raise ValueError("surface speed factor must be (0, 1], or null for impassable")
        return self


class Transport(Contract):
    profile_id: ID
    mode: Literal["foot", "bicycle", "motorbike", "vehicle"]
    vehicle_access_key: Literal["motorcar", "hgv"]
    class_speed_kph: dict[ID, Nonnegative]
    surface_factors: dict[ID, Surface]
    allowed_access_values: list[ID]
    missing_access: Literal["class_scenario", "exclude"]
    max_snap_metres: Nonnegative
    connector_speed_kph: Nonnegative
    max_travel_minutes: Nonnegative
    evidence: Evidence
    approval: Approval | None
    limitations: list[Text] = Field(min_length=1)

    @model_validator(mode="after")
    def positive_speeds(self):
        if not self.class_speed_kph or any(v <= 0 for v in self.class_speed_kph.values()):
            raise ValueError("explicit positive class speeds required")
        if self.connector_speed_kph <= 0 or self.max_travel_minutes <= 0:
            raise ValueError("positive connector speed and travel budget required")
        if not self.surface_factors:
            raise ValueError("explicit surface policy required; absent surfaces are excluded")
        if self.evidence.label == "UNKNOWN" or self.evidence.missing_reason:
            raise ValueError("configured transport values require known evidence")
        if set(self.allowed_access_values) - {"yes", "designated", "permissive"}:
            raise ValueError("private/conditional/destination access needs a richer adapter")
        return self


class RankingPolicy(Contract):
    top_k: int = Field(gt=0)
    robust_inclusion: float = Field(gt=0, le=1)
    interval_quantiles: tuple[float, float]
    score: Literal["technical_kw"]
    # Never turn documentation into numerical capacity or a probability of viability.
    missing_supply_requires_verification: Literal[True]
    approval: Approval | None

    @model_validator(mode="after")
    def quantiles(self):
        lo, hi = self.interval_quantiles
        if not 0 <= lo < 0.5 < hi <= 1:
            raise ValueError("summary quantiles must straddle the median")
        return self


class ScenarioConfig(Contract):
    version: Literal["phase6-v1"]
    scenario_id: ID
    purpose: Literal["synthetic_fixture", "scientific_reviewed"]
    as_of: date
    metric_crs: Literal["EPSG:3347"]
    distance_unit: Literal["metre"]
    time_unit: Literal["minute"]
    parameters: dict[ID, ParameterRange]
    transports: list[Transport] = Field(min_length=1)
    seasons: list[Literal["dry", "wet"]] = Field(min_length=2, max_length=2)
    assignment_variants: list[Literal["min_cost_max_served", "nearest_first"]] = Field(min_length=1)
    reference_case: ID
    unknown_capacity: Literal["exclude_and_flag", "unbounded_and_flag"]
    mass_tolerance_tonnes: float = Field(gt=0, allow_inf_nan=False)
    draw_power: int = Field(ge=1, le=16)
    seed: int = Field(ge=0)
    ranking: RankingPolicy
    methods_approval: Approval | None
    joint_dependency_description: Text
    production_proxy_description: Text
    limitations: list[Text] = Field(min_length=1)

    @model_validator(mode="after")
    def consistency(self):
        if set(self.parameters) != set(PARAMETER_UNITS):
            raise ValueError("exact inventory/aeration parameter set required")
        for name, p in self.parameters.items():
            if p.unit != PARAMETER_UNITS[name]:
                raise ValueError(f"wrong parameter unit: {name}")
            if name != "auxiliary_power" and p.lower <= 0:
                raise ValueError(f"strictly positive lower bound required: {name}")
            if p.unit == "fraction" and p.upper > 1:
                raise ValueError(f"fraction exceeds one: {name}")
        if (
            self.parameters["residence_days"].upper
            > self.parameters["modeled_operating_days"].lower
        ):
            raise ValueError("residence can exceed the operating period")
        if set(self.seasons) != {"dry", "wet"}:
            raise ValueError("both dry and wet scenarios required")
        if len(set(self.assignment_variants)) != len(self.assignment_variants):
            raise ValueError("duplicate assignment variant")
        if len({t.profile_id for t in self.transports}) != len(self.transports):
            raise ValueError("duplicate transport profile")
        cases = {
            f"{t.profile_id}:{s}:{v}"
            for t in self.transports
            for s in self.seasons
            for v in self.assignment_variants
        }
        if self.reference_case not in cases:
            raise ValueError("reference case is not in the declared scenario ensemble")
        return self

    def authorize(self, dataset, *, allow_fixture=False):
        if self.purpose != dataset.purpose:
            raise ValueError("scenario and data purpose disagree")
        if self.purpose == "synthetic_fixture":
            if not allow_fixture:
                raise ValueError("synthetic run requires --allow-fixture")
            if not all(x.startswith("fixture:") for x in dataset.all_ids()):
                raise ValueError("fixture execution cannot consume real identities")
            if dataset.provinces != ["TEST"]:
                raise ValueError("fixture provenance must declare TEST, not a real province")
            if any(p.approval for p in [*self.parameters.values(), *self.transports]):
                raise ValueError("fixtures cannot carry scientific parameter approvals")
            return
        if set(dataset.provinces) - {"AB", "SK"}:
            raise ValueError("development only: Manitoba/other regions require a new protocol")
        if not dataset.data_approval or not self.methods_approval or not self.ranking.approval:
            raise ValueError("data, methods and ranking policy require recorded human review")
        if self.ranking.top_k != 10:
            raise ValueError("real Phase 6 shortlist budget is ten")
        for item in [*self.parameters.values(), *self.transports]:
            if not item.approval:
                raise ValueError("all scientific parameters and transports require human approval")
        if not dataset.network_review:
            raise ValueError("barriers/restrictions and network completeness need review")


class ParentProduction(Contract):
    production_id: ID
    tonnes: Value[Nonnegative]


class Origin(Contract):
    origin_id: ID
    production_id: ID
    fraction: float = Field(gt=0, le=1)
    location: Point
    precision: Literal["P1", "P2", "P3", "P4"]
    evidence: Evidence


class Site(Contract):
    node_id: ID
    location: Point
    precision: Literal["P1", "P2", "P3", "P4"]
    storage_tonnes: Value[Nonnegative]
    supply_state: Literal[
        "no_documented_asset", "documented_known_capacity", "documented_unknown_capacity"
    ]
    electrical_capacity_kw: Value[Nonnegative]
    supply_evidence: Evidence
    unresolved_question: Text | None

    @model_validator(mode="after")
    def capacity(self):
        if (self.electrical_capacity_kw.value is not None) != (
            self.supply_state == "documented_known_capacity"
        ):
            raise ValueError("electrical capacity disagrees with supply state")
        return self


class Dataset(Contract):
    schema_version: Literal["phase6-input-v1"]
    purpose: Literal["synthetic_fixture", "scientific_reviewed"]
    region_id: ID
    provinces: list[ID] = Field(min_length=1)
    commodity_id: Literal["wheat_non_durum"]
    service_id: Literal["ambient_air_aeration"]
    period_start: date
    period_end: date
    source_snapshots: list[Snapshot] = Field(min_length=1)
    parents: list[ParentProduction] = Field(min_length=1)
    origins: list[Origin] = Field(min_length=1)
    sites: list[Site] = Field(min_length=1)
    roads: list[RoadWay] = Field(min_length=1)
    data_approval: Approval | None
    network_review: Approval | None
    prepared_from_sha256: dict[ID, Hash]

    def all_ids(self):
        return (
            [p.production_id for p in self.parents]
            + [o.origin_id for o in self.origins]
            + [s.node_id for s in self.sites]
            + [s.snapshot_id for s in self.source_snapshots]
            + [r.way_id for r in self.roads]
        )

    @model_validator(mode="after")
    def joins(self):
        from math import fsum

        if self.period_start > self.period_end:
            raise ValueError("invalid reporting period")
        for rows, key in (
            (self.parents, "production_id"),
            (self.origins, "origin_id"),
            (self.sites, "node_id"),
            (self.source_snapshots, "snapshot_id"),
        ):
            if len({getattr(r, key) for r in rows}) != len(rows):
                raise ValueError(f"duplicate identity: {key}")
        parents = {p.production_id for p in self.parents}
        if {o.origin_id for o in self.origins} & {s.node_id for s in self.sites}:
            raise ValueError("origins and sites must have distinct identities")
        if {o.production_id for o in self.origins} != parents:
            raise ValueError("origin/parent join loses or adds production")
        for p in parents:
            if abs(fsum(o.fraction for o in self.origins if o.production_id == p) - 1) > 1e-12:
                raise ValueError("origin weights must conserve each parent's mass exactly once")
        snapshots = {s.snapshot_id for s in self.source_snapshots}
        evidence = (
            [p.tonnes.evidence for p in self.parents]
            + [o.evidence for o in self.origins]
            + [r.evidence for r in self.roads]
            + [
                e
                for s in self.sites
                for e in (
                    s.storage_tonnes.evidence,
                    s.electrical_capacity_kw.evidence,
                    s.supply_evidence,
                )
            ]
        )
        if any(not set(e.source_ids) <= snapshots for e in evidence):
            raise ValueError("orphan input evidence source")
        if self.purpose == "scientific_reviewed":
            expected = {s.snapshot_id: s.sha256 for s in self.source_snapshots}
            if self.prepared_from_sha256 != expected:
                raise ValueError("prepared inputs must identify every pinned snapshot hash")
        return self
