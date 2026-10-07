"""Deterministic bounded equal shares within a reporting region, with explicit overflow."""

from math import fsum, isfinite

from enagis.contracts import Allocation, Capacity, Evidence, Production, Value
from enagis.pipeline_contracts import ProductionBalance, Scenario


def storage_tonnes(capacity: Capacity) -> float | None:
    quantity = capacity.conversion.converted if capacity.conversion else capacity.original
    if quantity.dimension != "storage_mass" or quantity.unit != "tonne":
        raise ValueError("allocation capacity must be storage mass in tonnes")
    return quantity.amount.value


def annual_limit(capacity: Capacity, scenario: Scenario) -> float | None:
    storage = storage_tonnes(capacity)
    if storage is None:
        # Unknown is unbounded in this scenario, never zero; it requires verification.
        return None
    return (
        storage
        * scenario.number("wheat_storage_fraction")
        * scenario.number("modeled_operating_days")
        / scenario.number("residence_days")
    )


def bounded_shares(total: float, limits: dict[str, float | None]) -> tuple[dict[str, float], float]:
    """Water-fill equal shares; sorted identities make floating-point behavior reproducible."""
    if (
        not isfinite(total)
        or total < 0
        or any(v is not None and (not isfinite(v) or v < 0) for v in limits.values())
    ):
        raise ValueError("negative allocation input")
    assigned = dict.fromkeys(sorted(limits), 0.0)
    active, remaining = sorted(limits), total
    while active and remaining > 0:
        share = remaining / len(active)
        capped = [key for key in active if limits[key] is not None and limits[key] <= share]
        if not capped:
            for key in active:
                assigned[key] = share
            remaining = 0.0
            break
        for key in capped:
            assigned[key] = limits[key]
        active = [key for key in active if key not in capped]
        remaining = max(0.0, total - fsum(assigned.values()))
    # A roundoff residual in a fully shared origin is audited, not labeled unserved production.
    return assigned, remaining


def allocate(production: Production, capacities: list[Capacity], scenario: Scenario):
    mass = production.modeled_tonnes.value
    if mass is None:
        return [], ProductionBalance(
            production_id=production.production_id,
            input_tonnes=None,
            assigned_tonnes=None,
            unserved_tonnes=None,
            residual_tonnes=None,
            missing_reason=production.modeled_tonnes.evidence.missing_reason,
        )
    if len({c.node_id for c in capacities}) != len(capacities):
        raise ValueError("duplicate node capacity would double count assignment")
    shares, unserved = bounded_shares(
        mass, {c.node_id: annual_limit(c, scenario) for c in capacities}
    )
    evidence = Evidence(
        label="ESTIMATED",
        source_ids=sorted(
            set(
                production.modeled_tonnes.evidence.source_ids
                + [scenario.source_id]
                + [s for c in capacities for s in c.original.amount.evidence.source_ids]
            )
        ),
        as_of=scenario.as_of,
        licence="Source licences retained; scenario/code MIT",
        method=f"{scenario.purpose}: {scenario.assignment_method}; not observed throughput",
        missing_reason=None,
    )
    rows = [
        Allocation(
            allocation_id=f"{scenario.scenario_id}:{production.production_id}:{node}",
            production_id=production.production_id,
            node_id=node,
            unserved_reason=None,
            scenario_id=scenario.scenario_id,
            assigned_tonnes=Value(value=value, evidence=evidence),
            inventory_scenario_ref=scenario.scenario_id,
        )
        for node, value in shares.items()
    ]
    if unserved > 0 or not capacities:
        rows.append(
            Allocation(
                allocation_id=f"{scenario.scenario_id}:{production.production_id}:unserved",
                production_id=production.production_id,
                node_id=None,
                unserved_reason="No eligible node in reporting region"
                if not capacities
                else "Modeled wheat inventory exceeds configured share of known storage",
                scenario_id=scenario.scenario_id,
                assigned_tonnes=Value(value=unserved, evidence=evidence),
                inventory_scenario_ref=scenario.scenario_id,
            )
        )
    assigned = fsum(shares.values())
    balance = ProductionBalance(
        production_id=production.production_id,
        input_tonnes=mass,
        assigned_tonnes=assigned,
        unserved_tonnes=unserved,
        residual_tonnes=mass - fsum((assigned, unserved)),
        missing_reason=None,
    )
    if abs(balance.residual_tonnes) > scenario.mass_tolerance_tonnes:
        raise ValueError("production conservation failed")
    return rows, balance
