"""Independently check exported conservation, physical constraints and shortlist traces."""

import csv
import json
from collections import defaultdict
from math import fsum, isclose
from pathlib import Path

from enagis.allocation import annual_limit, storage_tonnes
from enagis.contracts import Allocation, Artifact, Production, RunMetadata, Snapshot
from enagis.data_contracts import ProductionLineage
from enagis.data_io import file_hash, safe_path
from enagis.energy import classify_gap, energy_requirement
from enagis.pipeline import csv_rows, indexed, source_ids
from enagis.pipeline_contracts import NodeTrace, ProductionBalance, Scenario


def verify_run(output: Path):
    index = json.loads((output / "index.json").read_bytes())
    metadata = RunMetadata.model_validate(index["metadata"])
    paths = [entry["path"] for entry in index["artifacts"]]
    expected = {
        "nodes.json",
        "allocations.json",
        "production_balances.json",
        "engineering-ranking.csv",
        "engineering-shortlist.csv",
        "audit.json",
        "scenario.json",
        "source_snapshots.json",
        "production_inputs.json",
        "production_lineage.json",
    }
    if len(paths) != len(set(paths)) or set(paths) != expected:
        raise ValueError("duplicate or incomplete run index")
    for entry in index["artifacts"]:
        if file_hash(safe_path(output, entry["path"])) != entry["sha256"]:
            raise ValueError(f"run artifact checksum mismatch: {entry['path']}")
    scenario = Scenario.model_validate_json((output / "scenario.json").read_bytes())
    scenario.authorize(allow_temporary=True)
    if scenario.scenario_id != metadata.scenario_id or scenario.purpose != index["purpose"]:
        raise ValueError("scenario metadata mismatch")

    def table(name, model):
        artifact = Artifact[model].model_validate_json((output / name).read_bytes())
        entry = next(e for e in index["artifacts"] if e["path"] == name)
        if artifact.metadata != metadata or entry["rows"] != len(artifact.rows):
            raise ValueError("mixed run metadata/row count")
        if not source_ids(artifact.model_dump(mode="json")) <= set(metadata.input_snapshot_ids):
            raise ValueError("orphan evidence source in exported run")
        return artifact.rows

    traces = table("nodes.json", NodeTrace)
    allocations = table("allocations.json", Allocation)
    balances = table("production_balances.json", ProductionBalance)
    production = indexed(table("production_inputs.json", Production), "production_id")
    lineage = indexed(table("production_lineage.json", ProductionLineage), "production_id")
    nodes = indexed(traces, "node_id")
    origins = indexed(balances, "production_id")
    if set(production) != set(origins) or set(lineage) != set(origins):
        raise ValueError("production/balance/lineage join lost or duplicated origins")
    indexed(allocations, "allocation_id")
    by_origin, by_node = defaultdict(list), defaultdict(list)
    for row in allocations:
        if row.production_id not in origins or row.scenario_id != scenario.scenario_id:
            raise ValueError("orphan allocation origin/scenario")
        by_origin[row.production_id].append(row)
        if row.node_id is not None:
            if row.node_id not in nodes:
                raise ValueError("orphan allocation node")
            by_node[row.node_id].append(row)
    tolerance = scenario.mass_tolerance_tonnes

    def equal(left, right):
        if not isclose(left, right, rel_tol=0, abs_tol=tolerance):
            raise ValueError("conservation/quantity mismatch")

    for balance in balances:
        if production[balance.production_id].modeled_tonnes.value != balance.input_tonnes:
            raise ValueError("production input differs from conservation balance")
        rows = by_origin[balance.production_id]
        if balance.input_tonnes is None:
            if rows:
                raise ValueError("unknown production was assigned")
            continue
        assigned = fsum(a.assigned_tonnes.value for a in rows if a.node_id is not None)
        unserved = fsum(a.assigned_tonnes.value for a in rows if a.node_id is None)
        equal(assigned, balance.assigned_tonnes)
        equal(unserved, balance.unserved_tonnes)
        equal(balance.input_tonnes, fsum((assigned, unserved)))
        equal(balance.residual_tonnes, balance.input_tonnes - fsum((assigned, unserved)))
    ranks = []
    for trace in traces:
        if trace.scenario_id != scenario.scenario_id or trace.purpose != scenario.purpose:
            raise ValueError("mixed trace scenario/purpose")
        if trace.allocations != by_node[trace.node_id]:
            raise ValueError("trace does not retain exact assignments")
        if trace.assigned_tonnes_per_reporting_period.value is not None:
            equal(
                trace.assigned_tonnes_per_reporting_period.value,
                fsum(a.assigned_tonnes.value for a in trace.allocations),
            )
            limit = annual_limit(trace.storage_capacity, scenario)
            if (
                limit is not None
                and trace.assigned_tonnes_per_reporting_period.value > limit + tolerance
            ):
                raise ValueError("known capacity exceeded")
        for production in trace.production_inputs:
            if origins[production.production_id].input_tonnes != production.modeled_tonnes.value:
                raise ValueError("production trace disagrees with input balance")
        inventory, airflow, requirement = energy_requirement(
            trace.node_id, trace.assigned_tonnes_per_reporting_period, scenario
        )
        if (inventory, airflow, requirement) != (
            trace.inventory,
            trace.airflow_m3_s,
            trace.requirement,
        ):
            raise ValueError("energy trace equation/provenance mismatch")
        storage_tonnes(trace.storage_capacity)  # Assert physical units even for unknown throughput.
        if trace.gap != classify_gap(
            trace.supply, trace.supply_capacity, trace.requirement, scenario
        ):
            raise ValueError("gap trace mismatch")
        if trace.rank is not None:
            ranks.append(trace)
    ranked = sorted(ranks, key=lambda t: (-t.requirement.electrical_kw.value.central, t.node_id))
    if [t.rank for t in ranked] != list(range(1, len(ranked) + 1)):
        raise ValueError("ranking is not deterministic/contiguous")
    expected_rows = list(csv_rows(traces, scenario))
    for filename, rows in (
        ("engineering-ranking.csv", expected_rows),
        ("engineering-shortlist.csv", expected_rows[: scenario.shortlist_size]),
    ):
        with (output / filename).open(encoding="utf-8", newline="") as stream:
            actual = list(csv.DictReader(stream))
        serialized = [{k: "" if v is None else str(v) for k, v in row.items()} for row in rows]
        if actual != serialized:
            raise ValueError("CSV export does not match typed node traces")
        entry = next(e for e in index["artifacts"] if e["path"] == filename)
        if entry["rows"] != len(actual):
            raise ValueError("CSV row count differs from index")
    snapshots = [
        Snapshot.model_validate(s)
        for s in json.loads((output / "source_snapshots.json").read_bytes())
    ]
    snapshot_ids = [s.snapshot_id for s in snapshots]
    if (
        len(snapshot_ids) != len(set(snapshot_ids))
        or set(snapshot_ids) != (set(metadata.input_snapshot_ids) - {scenario.source_id})
        or any(s.redistribution != "permitted" for s in snapshots)
    ):
        raise ValueError("exported snapshot provenance is incomplete or restricted")
    return {
        "run_id": metadata.run_id,
        "purpose": scenario.purpose,
        "verified_artifacts": len(paths),
        "nodes": len(nodes),
        "ranked_nodes": len(ranked),
        "shortlist_rows": min(len(ranked), scenario.shortlist_size),
        "conserved_known_origins": sum(b.input_tonnes is not None for b in balances),
    }


def trace_node(output: Path, node_id: str):
    verify_run(output)
    artifact = Artifact[NodeTrace].model_validate_json((output / "nodes.json").read_bytes())
    row = next((t for t in artifact.rows if t.node_id == node_id), None)
    if row is None:
        raise ValueError(f"node absent from development run: {node_id}")
    lineage = Artifact[ProductionLineage].model_validate_json(
        (output / "production_lineage.json").read_bytes()
    )
    origin_ids = {p.production_id for p in row.production_inputs}
    return {
        "metadata": artifact.metadata.model_dump(mode="json"),
        "trace": row.model_dump(mode="json"),
        "scenario": json.loads((output / "scenario.json").read_bytes()),
        "source_snapshots": json.loads((output / "source_snapshots.json").read_bytes()),
        "production_lineage": [
            p.model_dump(mode="json") for p in lineage.rows if p.production_id in origin_ids
        ],
    }
