"""Strict inputs and approval boundary for the independent Phase 4 experiment."""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from enagis.contracts import ID, Contract, Hash, Nonnegative, Text, Value

Feature = Literal[
    "production_context",
    "euclidean_production",
    "accessible_production",
    "population",
    "road_density",
    "junction_density",
    "log_ccs_area",
]


class ExperimentProtocol(Contract):
    protocol_id: ID
    amendment_status: Literal["amended before registration"] | None = None
    amendment_reasons: dict[str, Text] = Field(default_factory=dict)
    status: Literal["draft", "approved"]
    approved_by: Text | None
    approved_on: date | None
    approval_evidence: Text | None
    scientific_review_ref: Text
    development_units: list[ID]
    untouched_transfer_units: list[ID]
    metric_crs: Literal["EPSG:3347"]
    primary_metric: Literal["equal_weight_mean_car_top_fraction_recall"] = (
        "equal_weight_mean_car_top_fraction_recall"
    )
    primary_budget: Literal["ceil_fraction_times_block_size_stable_unit_id_ties"] = (
        "ceil_fraction_times_block_size_stable_unit_id_ties"
    )
    cv_design: Literal["leave_one_car_out"] = "leave_one_car_out"
    production_proxy: Literal["uniform_area_with_explicit_unknowns"]
    road_method: Literal["undirected_network_distance_not_vehicle_travel_time"]
    road_highways: list[ID] = Field(min_length=1)
    excluded_access_values: list[ID]
    catchment_distance_m: float = Field(gt=0)
    maximum_snap_distance_m: float = Field(gt=0)
    primary_top_fraction: float = Field(gt=0, lt=1)
    secondary_top_fraction: float = Field(gt=0, lt=1)
    minimum_positive_units: int = Field(ge=1)
    minimum_positive_blocks: int = Field(ge=2)
    minimum_hindcast_groups: int = Field(ge=2)
    bootstrap_draws: int = Field(ge=100)
    confidence_level: float = Field(gt=0, lt=1)
    seed: int = Field(ge=0)
    logistic_c: float = Field(gt=0)
    optimizer_tolerance: float = Field(gt=0)
    optimizer_max_iterations: int = Field(gt=0)
    logistic_solver: Literal["lbfgs"] = "lbfgs"
    logistic_regularization: Literal["L2"] = "L2"
    logistic_class_weight: Literal["balanced"] = "balanced"
    boyce_window_fraction: float = Field(gt=0, lt=1)
    boyce_resolution: int = Field(ge=3)
    base_features: list[Feature] = Field(min_length=1)
    full_features: list[Feature] = Field(min_length=1)
    comparison_arms: list[
        Literal["B0", "B1", "B2", "population", "nearest_presence", "base_model", "area_only"]
    ]
    sensitivity_features: list[Feature] = Field(default_factory=list)
    sensitivity_role: Literal["descriptive_only_cannot_override_primary"] = (
        "descriptive_only_cannot_override_primary"
    )
    registration_remote: ID = "origin"
    require_pushed_commit_and_tag: bool = True
    keep_rule: Literal["paired_block_bootstrap_lower_margin_over_best_baseline_gt_zero"]

    @model_validator(mode="after")
    def coherent(self):
        if set(self.development_units) & set(self.untouched_transfer_units):
            raise ValueError("development and untouched transfer overlap")
        for values in (
            self.development_units,
            self.untouched_transfer_units,
            self.base_features,
            self.full_features,
            self.road_highways,
            self.comparison_arms,
        ):
            if len(values) != len(set(values)):
                raise ValueError("duplicate protocol choice")
        if not set(self.base_features) < set(self.full_features):
            raise ValueError("full model must add upstream features to base model")
        required_arms = {
            "B0",
            "B1",
            "B2",
            "population",
            "nearest_presence",
            "base_model",
        }
        if self.amendment_status:
            required_arms.add("area_only")
            if "log_ccs_area" not in self.base_features:
                raise ValueError("v1.1 base model must control polygon area")
            if self.sensitivity_features != [
                "population",
                "road_density",
                "junction_density",
                "log_ccs_area",
            ]:
                raise ValueError("sensitivity must drop every production-dependent feature")
            if not self.require_pushed_commit_and_tag:
                raise ValueError("v1.1 requires a remotely published registration")
        if set(self.comparison_arms) != required_arms:
            raise ValueError("all preregistered comparison arms are required")
        if self.status == "draft" and any(
            (self.approved_by, self.approved_on, self.approval_evidence)
        ):
            raise ValueError("draft protocol cannot assert approval")
        return self

    def require_approval(self):
        if self.status != "approved" or not all(
            (self.approved_by, self.approved_on, self.approval_evidence)
        ):
            raise ValueError(
                "Phase 4 scientific run requires human approval of the versioned protocol"
            )


class StudyUnit(Contract):
    unit_id: ID
    block_id: ID
    province: ID
    crs: Literal["EPSG:3347"]
    point_xy: tuple[float, float]
    area_m2: float = Field(gt=0)
    geometry: dict
    population: Value[Nonnegative]
    population_csd_ids: list[ID]
    production_intersections_m2: dict[ID, Nonnegative]


class PresenceLabel(Contract):
    unit_id: ID
    status: Literal["documented_presence", "unlabeled", "spatial_review_required"]
    facility_ids: list[ID]
    source_ids: list[ID] = Field(min_length=1)
    definition: Literal["Documented primary elevator; unlabeled is not confirmed absence"]


class FeatureRow(Contract):
    unit_id: ID
    block_id: ID
    province: ID
    features: dict[Feature, Value[float]]
    snap_distance_m: Nonnegative
    missing_reasons: list[Text]

    @model_validator(mode="after")
    def original_features_remain_nonnegative(self):
        for key, value in self.features.items():
            if key != "log_ccs_area" and value.value is not None and value.value < 0:
                raise ValueError("original scientific features must remain nonnegative")
        return self


class ExpertShortlist(Contract):
    source_id: ID
    elicited_by: Text
    elicited_on: date
    consent_and_release_ref: Text
    geographic_scope: Text
    ordered_shipping_point_ids: list[ID] = Field(min_length=1)

    @model_validator(mode="after")
    def unique(self):
        if len(set(self.ordered_shipping_point_ids)) != len(self.ordered_shipping_point_ids):
            raise ValueError("expert list repeats a shipping point")
        return self


class Preregistration(Contract):
    protocol_sha256: Hash
    preparation_index_sha256: Hash
    phase2_index_sha256: Hash
    phase3_index_sha256: Hash
    review_document_sha256: Hash
    code_sha256: Hash
    lockfile_sha256: Hash
    git_commit: Text
    git_tag: Text
    remote_url: Text
    remote_commit: Text
    remote_branch_ref: Text
    registered_on: date
    purpose: Literal["Before real outcome evaluation; Manitoba excluded"]
