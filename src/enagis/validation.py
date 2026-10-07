"""Cross-record engineering invariants, not an allocation or energy model."""

from collections import defaultdict
from hashlib import sha256
from math import isclose
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from enagis.contracts import (
    Allocation,
    Capacity,
    Catchment,
    Contract,
    Evidence,
    Facility,
    Gap,
    Inventory,
    Node,
    NodeCard,
    Outcome,
    Partition,
    Production,
    Quantity,
    RegionConfig,
    Requirement,
    RunMetadata,
    ShippingLink,
    SitingFeature,
    Snapshot,
    Supply,
    Travel,
    Uncertainty,
)


def unique(rows, field):
    ids = [getattr(row, field) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {field}")


def compare_quantities(capacity: Quantity, requirement: Quantity) -> float:
    if (capacity.dimension, capacity.unit, capacity.period_start, capacity.period_end) != (
        requirement.dimension,
        requirement.unit,
        requirement.period_start,
        requirement.period_end,
    ):
        raise ValueError(
            "incompatible quantity dimension, unit or period; convert explicitly first"
        )
    if capacity.amount.value is None or requirement.amount.value is None:
        raise ValueError("unknown quantity cannot be treated as zero")
    return capacity.amount.value - requirement.amount.value


def checked_many_to_one(left, right, key):
    """Retain all left rows and audit unmatched keys; reject ambiguous right keys."""
    unique(right, key)
    lookup = {getattr(row, key): row for row in right}
    result = [(row, lookup.get(getattr(row, key))) for row in left]
    return result, {
        "left_before": len(left),
        "right_before": len(right),
        "after": len(result),
        "unmatched": [getattr(row, key) for row, match in result if match is None],
    }


def canonical_bytes(model: BaseModel) -> bytes:
    import json

    return (
        json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def stable_order(scores: dict[str, float]) -> list[str]:
    """Mechanical tie break by stable ID; caller supplies the scientific scores."""
    from math import isfinite

    if not all(isfinite(score) for score in scores.values()):
        raise ValueError("scores must be finite")
    return sorted(scores, key=lambda node_id: (-scores[node_id], node_id))


def iter_evidence(value: Any):
    if isinstance(value, Evidence):
        yield value
    elif isinstance(value, BaseModel):
        for field in type(value).model_fields:
            yield from iter_evidence(getattr(value, field))
    elif isinstance(value, list):
        for item in value:
            yield from iter_evidence(item)


class Bundle(Contract):
    """One scenario/run; every enclosed table inherits this common metadata."""

    metadata: RunMetadata
    region_config: RegionConfig
    snapshots: list[Snapshot] = Field(min_length=1)
    facilities: list[Facility]
    nodes: list[Node]
    production: list[Production]
    travel: list[Travel]
    catchments: list[Catchment]
    allocations: list[Allocation]
    capacities: list[Capacity]
    inventories: list[Inventory]
    requirements: list[Requirement]
    supplies: list[Supply]
    gaps: list[Gap]
    uncertainty: list[Uncertainty]
    shortlist: list[NodeCard]
    shipping_links: list[ShippingLink]
    outcomes: list[Outcome]
    partitions: list[Partition]
    siting_features: list[SitingFeature]

    @model_validator(mode="after")
    def integrity(self):
        if self.metadata.region_id != self.region_config.region_id:
            raise ValueError("run and region configuration disagree")
        for partition in self.partitions:
            if partition.split != self.region_config.split_for(partition.region_unit_id):
                raise ValueError("partition differs from frozen regional split")
            if (partition.spatial_id.country_code, partition.spatial_id.boundary_vintage) != (
                self.region_config.country_code,
                self.region_config.boundary_vintage,
            ):
                raise ValueError("partition geography differs from region configuration")
        for outcome in self.outcomes:
            if outcome.split != self.region_config.split_for(outcome.province):
                raise ValueError("outcome differs from frozen regional split")
        for table, key in (
            (self.snapshots, "snapshot_id"),
            (self.facilities, "facility_id"),
            (self.facilities, "source_record_id"),
            (self.nodes, "node_id"),
            (self.production, "production_id"),
            (self.allocations, "allocation_id"),
            (self.capacities, "capacity_id"),
            (self.shipping_links, "facility_id"),
            (self.outcomes, "outcome_id"),
            (self.outcomes, "shipping_point_id"),
            (self.shortlist, "rank"),
            (self.siting_features, "feature_id"),
        ):
            unique(table, key)
        for table in (
            self.inventories,
            self.requirements,
            self.supplies,
            self.gaps,
            self.uncertainty,
            self.shortlist,
        ):
            unique(table, "node_id")
        for table in (self.travel, self.catchments):
            keys = [(r.origin_id, r.node_id, r.scenario_id) for r in table]
            if len(keys) != len(set(keys)):
                raise ValueError("duplicate origin/node/scenario")
        snapshot_ids = {s.snapshot_id for s in self.snapshots}
        if set(self.metadata.input_snapshot_ids) != snapshot_ids:
            raise ValueError("manifest and metadata snapshot references disagree")
        for evidence in iter_evidence(self):
            if not set(evidence.source_ids) <= snapshot_ids:
                raise ValueError("unresolved evidence source reference")
        for feature in self.siting_features:
            if not set(feature.source_ids) <= snapshot_ids:
                raise ValueError("unresolved feature source reference")
        facilities = {f.facility_id: f for f in self.facilities}
        nodes = {n.node_id: n for n in self.nodes}
        production = {p.production_id: p for p in self.production}
        capacities = {c.capacity_id: c for c in self.capacities}
        for facility in self.facilities:
            if facility.snapshot_id not in snapshot_ids:
                raise ValueError("unresolved registry snapshot")
            if not facility.source_record_id.startswith(facility.snapshot_id + ":"):
                raise ValueError("source_record_id must be qualified by snapshot vintage")
        for node in self.nodes:
            if node.facility_id is not None and node.facility_id not in facilities:
                raise ValueError("unresolved facility link")
        for link in self.shipping_links:
            if link.facility_id not in facilities:
                raise ValueError("unresolved shipping-point facility")
        assigned = defaultdict(float)
        for allocation in self.allocations:
            if allocation.production_id not in production:
                raise ValueError("unresolved production reference")
            assigned[allocation.production_id] += allocation.assigned_tonnes.value
        for observation in self.production:
            if observation.commodity_id != self.metadata.commodity_id:
                raise ValueError("commodity mismatch")
            if observation.modeled_tonnes.value is None or not isclose(
                assigned[observation.production_id],
                observation.modeled_tonnes.value,
                rel_tol=1e-12,
                abs_tol=1e-9,
            ):
                raise ValueError("allocation does not conserve source mass including unserved")
        node_tables = (
            self.allocations,
            self.travel,
            self.catchments,
            self.capacities,
            self.inventories,
            self.requirements,
            self.supplies,
            self.gaps,
            self.uncertainty,
            self.shortlist,
        )
        for table in node_tables:
            for row in table:
                if row.node_id is not None and row.node_id not in nodes:
                    raise ValueError("unresolved node reference")
                if hasattr(row, "scenario_id") and row.scenario_id != self.metadata.scenario_id:
                    raise ValueError("scenario mismatch")
                if hasattr(row, "service_id") and row.service_id != self.metadata.service_id:
                    raise ValueError("service mismatch")
        for row in (*self.travel, *self.catchments):
            if row.origin_id not in production:
                raise ValueError("unresolved travel origin")
        for travel in self.travel:
            if travel.graph_snapshot_id not in snapshot_ids:
                raise ValueError("unresolved graph snapshot")
            if travel.metric_crs != self.region_config.metric_crs:
                raise ValueError("travel CRS differs from configured projection")
        for capacity in self.capacities:
            if capacity.facility_id != nodes[capacity.node_id].facility_id:
                raise ValueError("capacity facility disagrees with node")
        for supply in self.supplies:
            if supply.capacity_ref is not None:
                capacity = capacities.get(supply.capacity_ref)
                if not capacity or (capacity.node_id, capacity.service_id) != (
                    supply.node_id,
                    supply.service_id,
                ):
                    raise ValueError("supply capacity reference mismatch")
                expected = "known" if supply.state == "documented_known_capacity" else "unknown"
                if capacity.status != expected:
                    raise ValueError("supply state disagrees with capacity status")
                if capacity.original.dimension != "electric_power":
                    raise ValueError(
                        "storage or airflow does not establish known electrical supply"
                    )
        for requirement in self.requirements:
            if nodes[requirement.node_id].stationary_service_eligible is not True:
                if requirement.electrical_kw.value or requirement.electricity_kwh.value:
                    raise ValueError(
                        "ineligible/unknown node stationary requirement must be UNKNOWN"
                    )
        requirements = {r.node_id: r for r in self.requirements}
        supplies = {r.node_id: r for r in self.supplies}
        for gap in self.gaps:
            requirement, supply = requirements.get(gap.node_id), supplies.get(gap.node_id)
            if requirement is None or supply is None:
                raise ValueError("gap requires recorded supply and requirement")
            margin = gap.capacity_minus_requirement_kw.value
            if margin is not None:
                if (
                    supply.state != "documented_known_capacity"
                    or requirement.electrical_kw.value is None
                ):
                    raise ValueError("margin cannot be computed from unknown service or capacity")
                capacity = capacities[supply.capacity_ref].original
                if capacity.unit != "kW" or not isclose(
                    margin,
                    capacity.amount.value - requirement.electrical_kw.value.central,
                    rel_tol=1e-12,
                    abs_tol=1e-9,
                ):
                    raise ValueError("margin must preserve signed comparable kW difference")
            if gap.bucket == "undocumented_supply" and supply.state != "no_documented_asset":
                raise ValueError("undocumented-supply bucket disagrees with documentation state")
        for uncertainty in self.uncertainty:
            if self.metadata.seed != uncertainty.seed:
                raise ValueError("uncertainty seed differs from run seed")
        for card in self.shortlist:
            for field in ("requirements", "supplies", "gaps"):
                singular = {"requirements": "requirement", "supplies": "supply", "gaps": "gap"}[
                    field
                ]
                if getattr(card, singular) not in getattr(self, field):
                    raise ValueError("node card must use the recorded scenario result")
        return self


class FixtureCase(Contract):
    case_id: str
    explanation: str
    bundle: Bundle
    expected_served_tonnes: float
    expected_unserved_tonnes: float
    expected_group_tonnes: dict[str, float]


class FixtureSuite(Contract):
    fixture_only: Literal[True]
    cases: list[FixtureCase] = Field(min_length=1)


def smoke(suite: FixtureSuite) -> dict:
    results = []
    for case in suite.cases:
        bundle = case.bundle
        served = sum(r.assigned_tonnes.value for r in bundle.allocations if r.node_id is not None)
        unserved = sum(r.assigned_tonnes.value for r in bundle.allocations if r.node_id is None)
        facility_group = {r.facility_id: r.shipping_point_id for r in bundle.shipping_links}
        node_group = {n.node_id: facility_group.get(n.facility_id) for n in bundle.nodes}
        groups = defaultdict(float)
        for row in bundle.allocations:
            group = node_group.get(row.node_id)
            if group is not None:
                groups[group] += row.assigned_tonnes.value
        if not isclose(served, case.expected_served_tonnes, abs_tol=1e-9):
            raise ValueError(f"{case.case_id}: served golden mismatch")
        if not isclose(unserved, case.expected_unserved_tonnes, abs_tol=1e-9):
            raise ValueError(f"{case.case_id}: unserved golden mismatch")
        if dict(groups) != case.expected_group_tonnes:
            raise ValueError(f"{case.case_id}: shipping-point golden mismatch")
        results.append(
            {
                "case_id": case.case_id,
                "served_tonnes": served,
                "unserved_tonnes": unserved,
                "group_tonnes": dict(groups),
                "bundle_sha256": sha256(canonical_bytes(bundle)).hexdigest(),
            }
        )
    return {
        "schema_version": suite.cases[0].bundle.metadata.schema_version,
        "fixture_only": True,
        "cases": results,
    }
