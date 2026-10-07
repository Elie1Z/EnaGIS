"""Inventory-based fan duty and evidence-preserving electrical supply comparison."""

from enagis.contracts import (
    Capacity,
    Evidence,
    Gap,
    Inventory,
    Range,
    Requirement,
    Supply,
    Value,
)
from enagis.pipeline_contracts import Scenario


def evidence(
    scenario: Scenario,
    sources: list[str],
    method: str,
    missing: str | None = None,
    label="ESTIMATED",
) -> Evidence:
    return Evidence(
        label="UNKNOWN" if missing else label,
        source_ids=sorted(set(sources + [scenario.source_id])),
        as_of=scenario.as_of,
        licence="Source licences retained; scenario/code MIT",
        method=f"{scenario.purpose}: {method}",
        missing_reason=missing,
    )


def energy_requirement(node_id: str, assigned: Value, scenario: Scenario):
    sources = assigned.evidence.source_ids
    missing = assigned.evidence.missing_reason
    mass = assigned.value
    stored = (
        None
        if mass is None
        else (mass * scenario.number("residence_days") / scenario.number("modeled_operating_days"))
    )
    airflow = (
        None
        if stored is None
        else (
            stored * scenario.number("airflow_per_tonne") * scenario.number("simultaneous_fraction")
        )
    )
    kw = (
        None
        if airflow is None
        else (
            airflow
            * scenario.number("static_pressure")
            / (1000 * scenario.number("fan_efficiency") * scenario.number("motor_efficiency"))
            + (scenario.number("auxiliary_power") if stored > 0 else 0)
        )
    )
    kwh = None if kw is None else kw * scenario.number("cycle_hours")
    inventory = Inventory(
        node_id=node_id,
        stored_tonnes=Value(
            value=stored,
            evidence=evidence(
                scenario,
                sources,
                "assigned tonnes * residence days / modeled operating days",
                missing,
            ),
        ),
        residence_scenario_ref=scenario.scenario_id,
        occupancy_scenario_ref=scenario.scenario_id,
    )
    airflow_value = Value(
        value=airflow,
        evidence=evidence(
            scenario, sources, "stored tonnes * m3/s/tonne * simultaneous fraction", missing
        ),
    )

    def range_value(value, method):
        return Value(
            value=None
            if value is None
            else Range(
                lower=value,
                central=value,
                upper=value,
                distribution_ref="deterministic_no_uncertainty",
            ),
            evidence=evidence(scenario, sources, method, missing),
        )

    requirement = Requirement(
        node_id=node_id,
        service_id="ambient_air_aeration",
        inventory_scenario_ref=scenario.scenario_id,
        electrical_kw=range_value(
            kw,
            "Q(m3/s) * total static pressure(Pa) / (1000 * fan eta * motor eta)"
            " + auxiliary kW; simultaneous fan duty",
        ),
        electricity_kwh=range_value(kwh, "electrical kW * configured hours for one cooling cycle"),
        cycle_or_period="One hypothetical cooling cycle; not annual consumption",
        peak_power_method="Concurrent fan duty, no kWh/24 inference; excludes startup current",
        parameter_refs=[p.parameter_id for p in scenario.parameters],
    )
    return inventory, airflow_value, requirement


def classify_gap(
    supply: Supply, capacity: Capacity | None, requirement: Requirement, scenario: Scenario
) -> Gap:
    if supply.node_id != requirement.node_id or supply.service_id != requirement.service_id:
        raise ValueError("supply and requirement references disagree")
    demand = requirement.electrical_kw.value
    sources = supply.evidence.source_ids + requirement.electrical_kw.evidence.source_ids
    margin, bucket, classification = None, None, "unknown"
    missing = "No comparable documented electrical capacity or requirement"
    if supply.state == "no_documented_asset":
        if capacity is not None:
            raise ValueError("undocumented asset cannot carry a capacity")
        if demand is not None and demand.central > 0:
            bucket, classification = "undocumented_supply", "flagged"
    else:
        if capacity is None or supply.capacity_ref != capacity.capacity_id:
            raise ValueError("documented supply requires its matching capacity")
        if capacity.node_id != supply.node_id or capacity.service_id != supply.service_id:
            raise ValueError("supply capacity belongs to another node/service")
        quantity = capacity.conversion.converted if capacity.conversion else capacity.original
        if quantity.dimension != "electric_power" or quantity.unit != "kW":
            raise ValueError("electrical gap cannot compare storage, airflow or energy")
        amount = quantity.amount.value
        if (amount is not None) != (supply.state == "documented_known_capacity"):
            raise ValueError("documented supply state disagrees with capacity missingness")
        if amount is None:
            bucket, classification = "verify_first", "flagged"
        elif demand is not None:
            margin = amount - demand.central
            missing = None
            bucket, classification = (
                ("undersized", "flagged") if margin < 0 else (None, "unflagged")
            )
    return Gap(
        node_id=supply.node_id,
        service_id=supply.service_id,
        dimension="electric_power",
        unit="kW",
        capacity_minus_requirement_kw=Value(
            value=margin,
            evidence=evidence(
                scenario, sources, "documented electrical kW minus scenario required kW", missing
            ),
        ),
        bucket=bucket,
        classification=classification,
        classification_evidence=evidence(
            scenario,
            sources,
            "Documentation scope only; undocumented does not mean absent",
            label="INFERRED",
        ),
        policy_ref=scenario.gap_policy,
    )
