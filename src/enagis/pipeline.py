"""Offline walking skeleton: real development inputs to a traceable integration shortlist."""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from math import fsum
from pathlib import Path

from enagis.allocation import allocate, storage_tonnes
from enagis.contracts import (
    Artifact,
    Capacity,
    Facility,
    Node,
    Production,
    RunMetadata,
    Supply,
    Value,
)
from enagis.data_contracts import (
    IngestionConfig,
    Manifest,
    ProductionLineage,
    RegistrySourceRow,
    SpatialMatch,
)
from enagis.data_io import file_hash, safe_path, write_json, write_table
from enagis.energy import classify_gap, energy_requirement, evidence
from enagis.ingestion import code_hash
from enagis.pipeline_contracts import NodeTrace, Scenario

INPUTS = {
    "registry.json": Facility,
    "nodes.json": Node,
    "capacities.json": Capacity,
    "production.json": Production,
    "production_lineage.json": ProductionLineage,
    "registry_source_rows.json": RegistrySourceRow,
    "facility_spatial_matches.json": SpatialMatch,
}
CSV_FIELDS = [
    "rank",
    "node_id",
    "facility_name",
    "province",
    "longitude",
    "latitude",
    "crs",
    "precision",
    "scenario_id",
    "purpose",
    "throughput_label",
    "assigned_tonnes_per_reporting_period",
    "reporting_period_start",
    "reporting_period_end",
    "inventory_label",
    "stored_tonnes",
    "airflow_m3_s",
    "requirement_label",
    "electrical_kw",
    "electricity_kwh_one_cycle",
    "supply_state",
    "gap_bucket",
    "gap_label",
    "capacity_minus_requirement_kw",
    "ranking_method",
    "verification_question",
    "disclaimer",
    "storage_capacity_tonnes",
    "storage_capacity_label",
    "capacity_minus_requirement_label",
    "supply_documentation_scope",
    "ranking_label",
    "source_ids",
    "registry_as_of",
    "registry_licence",
    "production_as_of",
    "production_licence",
    "scenario_as_of",
]


def indexed(rows, field):
    result = {getattr(row, field): row for row in rows}
    if len(result) != len(rows):
        raise ValueError(f"duplicate {field}")
    return result


def source_ids(value):
    if isinstance(value, dict):
        result = set(value.get("source_ids", []))
        for child in value.values():
            result.update(source_ids(child))
        return result
    if isinstance(value, list):
        return set().union(*(source_ids(child) for child in value))
    return set()


def load_inputs(input_dir: Path):
    index = json.loads((input_dir / "index.json").read_bytes())
    metadata = RunMetadata.model_validate(index["metadata"])
    entries = {e["path"]: e for e in index["artifacts"]}
    if len(entries) != len(index["artifacts"]):
        raise ValueError("duplicate phase 2 artifact path")
    tables, consumed = {}, []
    for name, row_type in INPUTS.items():
        entry = entries[name]
        path = safe_path(input_dir, name)
        if entry.get("row_contract") != row_type.__name__ or file_hash(path) != entry["sha256"]:
            raise ValueError(f"input contract/checksum mismatch: {name}")
        artifact = Artifact[row_type].model_validate_json(path.read_bytes())
        expected_metadata = metadata
        if name == "capacities.json":
            expected_metadata = metadata.model_copy(update={"service_id": "wheat_storage"})
        elif name in ("production.json", "production_lineage.json"):
            expected_metadata = metadata.model_copy(update={"period_end": date(2024, 12, 31)})
        if artifact.metadata != expected_metadata or len(artifact.rows) != entry["rows"]:
            raise ValueError(f"input metadata/row count mismatch: {name}")
        if not source_ids(artifact.model_dump(mode="json")) <= set(metadata.input_snapshot_ids):
            raise ValueError(f"orphan evidence source in input: {name}")
        tables[name] = artifact.rows
        consumed.append(entry)
    return index, tables, consumed


def make_traces(tables, region: IngestionConfig, scenario: Scenario):
    facilities = indexed(tables["registry.json"], "facility_id")
    nodes = indexed(tables["nodes.json"], "node_id")
    raw = indexed(tables["registry_source_rows.json"], "facility_id")
    capacities = indexed(tables["capacities.json"], "node_id")
    lineage = indexed(tables["production_lineage.json"], "production_id")
    production = indexed(tables["production.json"], "production_id")
    if (
        set(raw) != set(facilities)
        or len(nodes) != len(facilities)
        or set(capacities) != set(nodes)
    ):
        raise ValueError("node/registry/capacity join lost or duplicated records")
    if {n.facility_id for n in nodes.values()} != set(facilities):
        raise ValueError("node/facility join has orphan or duplicate identity")
    for node in nodes.values():
        capacity = capacities[node.node_id]
        if (
            capacity.facility_id != node.facility_id
            or raw[node.facility_id].node_id != node.node_id
        ):
            raise ValueError("registry/capacity facility association disagrees")
        if capacity.service_id != "wheat_storage":
            raise ValueError("allocation capacity is not wheat storage")
    matches = {}
    for row in tables["facility_spatial_matches.json"]:
        if row.geography_type != "small_area_data_region":
            continue
        if row.record_id in matches:
            raise ValueError("duplicate reporting-region spatial join")
        matches[row.record_id] = row
    if set(matches) != set(facilities):
        raise ValueError("spatial join lost or added facilities")
    dev_production = [
        p
        for p in production.values()
        if lineage[p.production_id].province in region.development_units
    ]
    by_region = indexed(dev_production, "geometry_ref")
    selected = sorted(
        (n for n in nodes.values() if raw[n.facility_id].province in region.development_units),
        key=lambda n: n.node_id,
    )
    groups, status, node_regions = defaultdict(list), {}, {}
    for node in selected:
        if node.facility_id not in facilities:
            raise ValueError("node has no source facility")
        match = matches[node.facility_id]
        valid_match = match.status == "matched" and len(match.matched_keys) == 1
        key = match.matched_keys[0] if valid_match else None
        node_regions[node.node_id] = key
        if not valid_match:
            status[node.node_id] = f"spatial_review_required:{match.status}"
        elif node.stationary_service_eligible is not True or node.node_type != "storage":
            status[node.node_id] = "stationary_service_eligibility_unknown_or_ineligible"
        elif key not in by_region:
            status[node.node_id] = "no_development_production_origin"
        else:
            status[node.node_id] = "assigned_within_reporting_region"
            groups[key].append(capacities[node.node_id])
    allocations, balances = [], []
    for p in sorted(dev_production, key=lambda p: p.production_id):
        rows, balance = allocate(p, groups[p.geometry_ref], scenario)
        allocations.extend(rows)
        balances.append(balance)
    by_node = defaultdict(list)
    for a in allocations:
        if a.node_id:
            by_node[a.node_id].append(a)
    traces = []
    for node in selected:
        key = node_regions[node.node_id]
        p = by_region.get(key)
        assigned = by_node[node.node_id]
        missing = None
        if status[node.node_id] != "assigned_within_reporting_region":
            missing = status[node.node_id]
        elif p.modeled_tonnes.value is None:
            missing = p.modeled_tonnes.evidence.missing_reason
            status[node.node_id] = "production_unknown"
        source_ids = node.eligibility_evidence.source_ids + (
            p.modeled_tonnes.evidence.source_ids if p else []
        )
        value = Value(
            value=None if missing else fsum(a.assigned_tonnes.value for a in assigned),
            evidence=evidence(
                scenario,
                source_ids,
                "Sum of conserved administrative scenario assignments, tonnes/reporting period",
                missing,
            ),
        )
        inventory, airflow, requirement = energy_requirement(node.node_id, value, scenario)
        capacity = capacities[node.node_id]
        stored = inventory.stored_tonnes.value
        limit = storage_tonnes(capacity)
        if (
            stored is not None
            and limit is not None
            and (
                stored
                > limit * scenario.number("wheat_storage_fraction") + scenario.mass_tolerance_tonnes
            )
        ):
            raise ValueError("modeled inventory exceeds configured known storage constraint")
        # Registry documents storage, not installed electrical fan supply. Do not use storage as kW.
        supply = Supply(
            node_id=node.node_id,
            service_id=requirement.service_id,
            state="no_documented_asset",
            evidence=evidence(
                scenario,
                node.eligibility_evidence.source_ids,
                "No fan asset documentation in consumed open registry; absence not established",
                label="INFERRED",
            ),
            capacity_ref=None,
            documentation_scope="AAFC 2024 primary elevator/storage registry only; "
            "no fan inventory, grid audit, operator confirmation or private verification used",
        )
        traces.append(
            NodeTrace(
                node_id=node.node_id,
                province=raw[node.facility_id].province,
                split="development",
                purpose=scenario.purpose,
                scenario_id=scenario.scenario_id,
                disclaimer=scenario.disclaimer,
                assignment_status=status[node.node_id],
                reporting_region=key,
                facility=facilities[node.facility_id],
                node=node,
                storage_capacity=capacity,
                production_inputs=[p] if p else [],
                allocations=assigned,
                assigned_tonnes_per_reporting_period=value,
                inventory=inventory,
                airflow_m3_s=airflow,
                requirement=requirement,
                supply=supply,
                supply_capacity=None,
                gap=classify_gap(supply, None, requirement, scenario),
                verification_question="Confirm location/licensing and wheat inventory/residence; "
                "what fan airflow, static pressure, motor kW and cycle hours are documented?",
            )
        )
    rankable = sorted(
        (
            t
            for t in traces
            if t.requirement.electrical_kw.value is not None
            and t.requirement.electrical_kw.value.central > 0
        ),
        key=lambda t: (-t.requirement.electrical_kw.value.central, t.node_id),
    )
    for rank, trace in enumerate(rankable, 1):
        trace.rank = rank
    return traces, allocations, balances


def csv_rows(traces: list[NodeTrace], scenario: Scenario):
    for trace in sorted((t for t in traces if t.rank is not None), key=lambda t: t.rank):
        point = trace.node.location.point.value
        period = trace.production_inputs[0].original
        yield dict(
            zip(
                CSV_FIELDS,
                [
                    trace.rank,
                    trace.node_id,
                    trace.facility.name.value,
                    trace.province,
                    point.longitude,
                    point.latitude,
                    point.crs,
                    trace.node.location.precision,
                    scenario.scenario_id,
                    scenario.purpose,
                    "ESTIMATED",
                    trace.assigned_tonnes_per_reporting_period.value,
                    period.period_start,
                    period.period_end,
                    "ESTIMATED",
                    trace.inventory.stored_tonnes.value,
                    trace.airflow_m3_s.value,
                    "ESTIMATED",
                    trace.requirement.electrical_kw.value.central,
                    trace.requirement.electricity_kwh.value.central,
                    trace.supply.state,
                    trace.gap.bucket,
                    "INFERRED",
                    trace.gap.capacity_minus_requirement_kw.value,
                    scenario.ranking_method,
                    trace.verification_question,
                    trace.disclaimer,
                    storage_tonnes(trace.storage_capacity),
                    trace.storage_capacity.original.amount.evidence.label,
                    trace.gap.capacity_minus_requirement_kw.evidence.label,
                    trace.supply.documentation_scope,
                    "INFERRED",
                    ";".join(trace.assigned_tonnes_per_reporting_period.evidence.source_ids),
                    trace.facility.effective_on,
                    trace.facility.name.evidence.licence,
                    trace.production_inputs[0].modeled_tonnes.evidence.as_of,
                    trace.production_inputs[0].modeled_tonnes.evidence.licence,
                    scenario.as_of,
                ],
                strict=True,
            )
        )


def run_pipeline(
    root: Path,
    input_dir: Path,
    region_path: Path,
    scenario_path: Path,
    manifest_path: Path,
    output: Path,
    allow_temporary=False,
):
    root, input_dir, output = root.resolve(), input_dir.resolve(), output.resolve()
    if not output.is_relative_to(root / "outputs") or output == root / "outputs":
        raise ValueError("pipeline output must be a subdirectory of project outputs")
    if (
        output.is_relative_to(input_dir)
        or input_dir.is_relative_to(output)
        or any(
            path.resolve().is_relative_to(output)
            for path in (region_path, scenario_path, manifest_path)
        )
    ):
        raise ValueError("pipeline output overlaps an input/configuration path")
    scenario = Scenario.model_validate_json(scenario_path.read_bytes())
    scenario.authorize(allow_temporary)
    region = IngestionConfig.model_validate_json(region_path.read_bytes())
    index, tables, consumed = load_inputs(input_dir)
    old_metadata = RunMetadata.model_validate(index["metadata"])
    if old_metadata.region_id != region.region_id or old_metadata.commodity_id != "wheat_non_durum":
        raise ValueError("input region/commodity differs from configured pilot")
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    if file_hash(manifest_path) != index["manifest_sha256"]:
        raise ValueError("source manifest differs from pinned input-spine manifest")
    snapshots = {s.snapshot.snapshot_id: s.snapshot for s in manifest.sources}
    used_sources = set().union(
        *(source_ids([row.model_dump(mode="json") for row in rows]) for rows in tables.values())
    )
    parameter_sources = source_ids(scenario.model_dump(mode="json")) - {scenario.source_id}
    used_sources.update(parameter_sources)
    if scenario.source_id in used_sources:
        raise ValueError("scenario source identity collides with input provenance")
    for sid in old_metadata.input_snapshot_ids:
        if sid not in snapshots or snapshots[sid].redistribution != "permitted":
            raise ValueError("input provenance has missing or restricted snapshot")
    if any(
        sid not in snapshots or snapshots[sid].redistribution != "permitted" for sid in used_sources
    ):
        raise ValueError("scenario/input evidence requires pinned, permitted snapshots")
    hashes = {
        "input_index": file_hash(input_dir / "index.json"),
        "region": file_hash(region_path),
        "scenario": file_hash(scenario_path),
        "manifest": file_hash(manifest_path),
        "code": code_hash(),
        "lock": file_hash(root / "uv.lock"),
    }
    digest = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    metadata = old_metadata.model_copy(
        update={
            "run_id": f"phase3:{digest[:20]}",
            "scenario_id": scenario.scenario_id,
            "config_sha256": hashes["scenario"],
            "input_snapshot_ids": sorted(used_sources | {scenario.source_id}),
            "period_start": date(region.harvest_year, 1, 1),
            "period_end": date(region.harvest_year, 12, 31),
        }
    )
    traces, allocations, balances = make_traces(tables, region, scenario)
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.json").unlink(missing_ok=True)
    from enagis.contracts import Allocation
    from enagis.pipeline_contracts import ProductionBalance

    artifacts = []
    development_origin_ids = {b.production_id for b in balances}
    development_production = sorted(
        (p for p in tables["production.json"] if p.production_id in development_origin_ids),
        key=lambda p: p.production_id,
    )
    development_lineage = sorted(
        (p for p in tables["production_lineage.json"] if p.production_id in development_origin_ids),
        key=lambda p: p.production_id,
    )
    for name, rows, model in (
        ("nodes.json", traces, NodeTrace),
        ("allocations.json", allocations, Allocation),
        ("production_balances.json", balances, ProductionBalance),
        ("production_inputs.json", development_production, Production),
        ("production_lineage.json", development_lineage, ProductionLineage),
    ):
        artifacts.append(
            write_table(output / name, metadata, rows, model) | {"contract": model.__name__}
        )
    ranking = list(csv_rows(traces, scenario))
    for name, rows in (
        ("engineering-ranking.csv", ranking),
        ("engineering-shortlist.csv", ranking[: scenario.shortlist_size]),
    ):
        with (output / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        artifacts.append({"path": name, "rows": len(rows), "sha256": file_hash(output / name)})
    known = [b for b in balances if b.input_tonnes is not None]
    audit = {
        "metadata": metadata.model_dump(mode="json"),
        "purpose": scenario.purpose,
        "disclaimer": scenario.disclaimer,
        "hashes": hashes,
        "consumed_inputs": consumed,
        "development_units": region.development_units,
        "transfer_units_excluded_from_run": region.transfer_units,
        "nodes": len(traces),
        "ranked_nodes": len(ranking),
        "shortlist_rows": min(len(ranking), scenario.shortlist_size),
        "assignment_statuses": dict(sorted(Counter(t.assignment_status for t in traces).items())),
        "known_production_origins": len(known),
        "unknown_production_origins": len(balances) - len(known),
        "known_input_tonnes": fsum(b.input_tonnes for b in known),
        "assigned_tonnes": fsum(b.assigned_tonnes for b in known),
        "explicit_unserved_tonnes": fsum(b.unserved_tonnes for b in known),
        "maximum_absolute_mass_residual_tonnes": max(
            (abs(b.residual_tonnes) for b in known), default=0
        ),
        "mass_tolerance_tonnes": scenario.mass_tolerance_tonnes,
        "unknown_origins_excluded_from_mass_totals": True,
        "travel_times": "Not calculated; administrative assignment is a temporary scenario",
        "ranking": "Deterministic scenario kW then stable ID; no final score or uncertainty claim",
        "scientific_readiness": "Pending human-reviewed methods, commercial parameters, "
        "data and verification gates",
    }
    write_json(output / "audit.json", audit)
    artifacts.append({"path": "audit.json", "sha256": file_hash(output / "audit.json")})
    write_json(output / "scenario.json", scenario)
    artifacts.append({"path": "scenario.json", "sha256": file_hash(output / "scenario.json")})
    write_json(
        output / "source_snapshots.json",
        [snapshots[s].model_dump(mode="json") for s in sorted(used_sources)],
    )
    artifacts.append(
        {"path": "source_snapshots.json", "sha256": file_hash(output / "source_snapshots.json")}
    )
    write_json(
        output / "index.json",
        {
            "metadata": metadata.model_dump(mode="json"),
            "purpose": scenario.purpose,
            "hashes": hashes,
            "artifacts": artifacts,
        },
    )
    return audit
