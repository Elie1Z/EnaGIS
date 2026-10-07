"""Phase 3 scenario and trace contracts; temporary values cannot imply approval."""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from enagis.contracts import (
    ID,
    Allocation,
    Capacity,
    Contract,
    Facility,
    Gap,
    Inventory,
    Node,
    Nonnegative,
    Production,
    Requirement,
    ScientificParameter,
    Supply,
    Text,
    Value,
)

PARAMETER_UNITS = {
    "residence_days": "day",
    "modeled_operating_days": "day",
    "wheat_storage_fraction": "fraction",
    "airflow_per_tonne": "m3/s/tonne",
    "static_pressure": "Pa",
    "fan_efficiency": "fraction",
    "motor_efficiency": "fraction",
    "simultaneous_fraction": "fraction",
    "cycle_hours": "hour",
    "auxiliary_power": "kW",
}


class Scenario(Contract):
    scenario_id: ID
    source_id: ID
    as_of: date
    purpose: Literal["temporary_engineering", "scientific_reviewed"]
    disclaimer: Text
    assignment_method: Literal["same_reporting_region_bounded_equal_share"]
    inventory_method: Literal["steady_flow_residence"]
    ranking_method: Literal["scenario_kw_descending_then_node_id"]
    gap_policy: Literal["signed_margin_and_documentation"]
    methods_approved_by: Text | None
    methods_approved_on: date | None
    method_sources: list[Text] = Field(min_length=1)
    parameters: list[ScientificParameter] = Field(min_length=1)
    mass_tolerance_tonnes: Nonnegative
    shortlist_size: int = Field(gt=0)

    @model_validator(mode="after")
    def parameter_set(self):
        params = {p.parameter_id: p for p in self.parameters}
        if len(params) != len(self.parameters) or set(params) != set(PARAMETER_UNITS):
            raise ValueError("scenario requires exactly the named aeration parameters")
        for key, parameter in params.items():
            if parameter.unit != PARAMETER_UNITS[key]:
                raise ValueError(f"wrong unit for {key}")
            value = parameter.value.value
            if value is None or value < 0:
                raise ValueError(f"scenario requires nonnegative explicit value: {key}")
            if key != "auxiliary_power" and value == 0:
                raise ValueError(f"scenario parameter must be positive: {key}")
            if parameter.unit == "fraction" and value > 1:
                raise ValueError(f"fraction exceeds one: {key}")
            if self.purpose == "temporary_engineering" and (
                parameter.approved_by or parameter.approved_on
            ):
                raise ValueError("temporary parameters must not carry approval")
        if params["residence_days"].value.value > params["modeled_operating_days"].value.value:
            raise ValueError("residence exceeds modeled operating period")
        return self

    def authorize(self, allow_temporary: bool):
        if self.purpose == "temporary_engineering":
            if not allow_temporary:
                raise ValueError("temporary scenario requires --allow-temporary-scenario")
        else:
            if not self.methods_approved_by or not self.methods_approved_on:
                raise ValueError("scientific methods require recorded human approval")
            for parameter in self.parameters:
                parameter.require_approved()
                if set(parameter.value.evidence.source_ids) <= {self.source_id}:
                    raise ValueError(
                        "scientific parameter requires sourced evidence, not scenario alone"
                    )

    def number(self, key: str) -> float:
        return next(p.value.value for p in self.parameters if p.parameter_id == key)


class ProductionBalance(Contract):
    production_id: ID
    input_tonnes: Nonnegative | None
    assigned_tonnes: Nonnegative | None
    unserved_tonnes: Nonnegative | None
    residual_tonnes: float | None
    missing_reason: Text | None

    @model_validator(mode="after")
    def known_or_missing(self):
        values = (
            self.input_tonnes,
            self.assigned_tonnes,
            self.unserved_tonnes,
            self.residual_tonnes,
        )
        if self.input_tonnes is None:
            if any(v is not None for v in values) or not self.missing_reason:
                raise ValueError("unknown production must not become a zero balance")
        elif any(v is None for v in values) or self.missing_reason:
            raise ValueError("known production requires complete balance")
        return self


class NodeTrace(Contract):
    node_id: ID
    province: ID
    split: Literal["development"]
    rank: int | None = Field(default=None, gt=0)
    purpose: Literal["temporary_engineering", "scientific_reviewed"]
    scenario_id: ID
    disclaimer: Text
    assignment_status: Text
    reporting_region: ID | None
    facility: Facility
    node: Node
    storage_capacity: Capacity
    production_inputs: list[Production]
    allocations: list[Allocation]
    assigned_tonnes_per_reporting_period: Value[Nonnegative]
    inventory: Inventory
    airflow_m3_s: Value[Nonnegative]
    requirement: Requirement
    supply: Supply
    supply_capacity: Capacity | None
    gap: Gap
    verification_question: Text

    @model_validator(mode="after")
    def consistent_node(self):
        for row in (
            self.node,
            self.storage_capacity,
            self.inventory,
            self.requirement,
            self.supply,
            self.gap,
        ):
            if row.node_id != self.node_id:
                raise ValueError("trace mixes node IDs")
        if self.node.facility_id != self.facility.facility_id:
            raise ValueError("trace mixes facilities")
        if any(a.node_id != self.node_id for a in self.allocations):
            raise ValueError("trace includes another node's allocation")
        if self.rank is not None and (
            self.requirement.electrical_kw.value is None
            or self.requirement.electrical_kw.value.central <= 0
        ):
            raise ValueError("ranking requires positive modeled technical power")
        return self
