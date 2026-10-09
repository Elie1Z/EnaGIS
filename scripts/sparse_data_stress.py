"""Sparse-data stress diagnostic for the recorded Phase 3 screening procedure.

The diagnostic removes documentation under a declared, seeded protocol and re-runs the unchanged
trace/allocation/energy logic. It reports abstention integrity, production conservation,
tie-inclusive shortlist retention and redistribution inflation. It never measures accuracy.

Status: proposal awaiting human approval (docs/proposals/sparse-data-stress-diagnostic.md).
It lives in scripts/ so the registered scientific source in src/enagis stays unchanged.
Usage: python -m scripts.sparse_data_stress --allow-temporary-scenario
"""

import argparse
import json
import random
from math import fsum
from pathlib import Path
from statistics import fmean

from enagis.contracts import Evidence, Value
from enagis.data_contracts import IngestionConfig
from enagis.data_io import file_hash, safe_path, write_json
from enagis.pipeline import code_hash, load_inputs, make_traces
from enagis.pipeline_contracts import Scenario

MECHANISMS = ("production_origin_loss", "location_unknown", "facility_undocumented")


def kw(trace):
    value = trace.requirement.electrical_kw.value
    return None if value is None else value.central


def top_set(traces, size, tolerance):
    """Tie-inclusive shortlist: every ranked node whose kW reaches the size-th ranked kW."""
    ranked = sorted((t for t in traces if t.rank), key=lambda t: t.rank)
    if not ranked:
        return set()
    cutoff = kw(ranked[min(size, len(ranked)) - 1])
    return {t.node_id for t in ranked if kw(t) >= cutoff - tolerance}


def mask_production(row, reason):
    unknown = Value[float](
        value=None,
        evidence=Evidence(
            **{
                **row.modeled_tonnes.evidence.model_dump(),
                "label": "UNKNOWN",
                "missing_reason": reason,
            }
        ),
    )
    return row.model_copy(update={"modeled_tonnes": unknown})


def degrade(tables, region, mechanism, fraction, rng, protocol_id):
    """Return degraded tables and the identities whose documentation was removed."""
    tables = {name: list(rows) for name, rows in tables.items()}
    reason = f"removed by {protocol_id} {mechanism} at fraction {fraction}"
    if mechanism == "production_origin_loss":
        provinces = {row.production_id: row.province for row in tables["production_lineage.json"]}
        known = sorted(
            row.production_id
            for row in tables["production.json"]
            if provinces[row.production_id] in region.development_units
            and row.modeled_tonnes.value is not None
        )
        removed = set(rng.sample(known, round(fraction * len(known))))
        tables["production.json"] = [
            mask_production(row, reason) if row.production_id in removed else row
            for row in tables["production.json"]
        ]
        regions = {
            row.geometry_ref for row in tables["production.json"] if row.production_id in removed
        }
        return tables, {"production_ids": removed, "reporting_regions": regions}
    provinces = {row.facility_id: row.province for row in tables["registry_source_rows.json"]}
    development = sorted(f for f, p in provinces.items() if p in region.development_units)
    removed = set(rng.sample(development, round(fraction * len(development))))
    if mechanism == "location_unknown":
        tables["facility_spatial_matches.json"] = [
            row.model_copy(update={"status": "unmatched", "matched_keys": []})
            if row.record_id in removed and row.geography_type == "small_area_data_region"
            else row
            for row in tables["facility_spatial_matches.json"]
        ]
    elif mechanism == "facility_undocumented":
        nodes = {n.node_id for n in tables["nodes.json"] if n.facility_id in removed}
        for name, key, gone in (
            ("registry.json", "facility_id", removed),
            ("registry_source_rows.json", "facility_id", removed),
            ("nodes.json", "facility_id", removed),
            ("capacities.json", "node_id", nodes),
            ("facility_spatial_matches.json", "record_id", removed),
        ):
            tables[name] = [row for row in tables[name] if getattr(row, key) not in gone]
    else:
        raise ValueError(f"unknown stress mechanism: {mechanism}")
    return tables, {"facility_ids": removed}


def measure(traces, balances, baseline, removed, size, tolerance):
    by_id = {t.node_id: t for t in traces}
    ranked = [t for t in traces if t.rank]
    masked_regions = removed.get("reporting_regions", set())
    masked_facilities = removed.get("facility_ids", set())
    violations = sum(
        1
        for t in ranked
        if t.reporting_region in masked_regions or t.facility.facility_id in masked_facilities
    )
    residual = max(
        (
            abs(b.input_tonnes - b.assigned_tonnes - b.unserved_tonnes)
            for b in balances
            if b.input_tonnes is not None
        ),
        default=0.0,
    )
    base_top = top_set(baseline["traces"], size, tolerance)
    top = top_set(traces, size, tolerance)
    surviving = {n for n in base_top if n in by_id and by_id[n].rank}
    entrants = top - base_top
    inflated = {
        n
        for n in entrants
        if baseline["kw"].get(n) is not None and kw(by_id[n]) > baseline["kw"][n] + tolerance
    }
    ratios = [kw(t) / baseline["kw"][t.node_id] for t in ranked if baseline["kw"].get(t.node_id)]
    return {
        "ranked": len(ranked),
        "reported_unknown": len(traces) - len(ranked),
        "abstention_violations": violations,
        "max_conservation_residual_tonnes": residual,
        "top_set_size": len(top),
        "retention": len(top & base_top) / len(base_top),
        "retention_among_surviving": len(top & surviving) / len(surviving) if surviving else None,
        "entrants": len(entrants),
        "entrants_inflated_by_redistribution": len(inflated),
        "max_kw_inflation_fraction": max(ratios, default=1.0) - 1,
    }


def quantile(values, q):
    """Empirical quantile of sorted values (nearest lower rank)."""
    return values[min(len(values) - 1, int(q * len(values)))]


def summarize(rows):
    out = {}
    for key in rows[0]:
        values = sorted(r[key] for r in rows if r[key] is not None)
        if not values:
            out[key] = None
            continue
        out[key] = {
            "mean": fmean(values),
            "p05": quantile(values, 0.05),
            "p95": quantile(values, 0.95),
            "min": values[0],
            "max": values[-1],
        }
    return out


def run_stress(root: Path, protocol_path: Path, output: Path, allow_temporary=False):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "outputs") or output == root / "outputs":
        raise ValueError("stress output must be a subdirectory of project outputs")
    protocol = json.loads(protocol_path.read_bytes())
    scenario_path = safe_path(root, protocol["scenario_path"])
    region_path = safe_path(root, protocol["region_path"])
    input_dir = safe_path(root, protocol["input_dir"])
    scenario = Scenario.model_validate_json(scenario_path.read_bytes())
    scenario.authorize(allow_temporary)
    region = IngestionConfig.model_validate_json(region_path.read_bytes())
    _, tables, _ = load_inputs(input_dir)
    size, tolerance = protocol["shortlist_size"], protocol["kw_tie_tolerance"]
    traces, _, balances = make_traces(tables, region, scenario)
    baseline = {"traces": traces, "kw": {t.node_id: kw(t) for t in traces if t.rank}}
    base_top = top_set(traces, size, tolerance)
    results = {}
    for mechanism in MECHANISMS:
        results[mechanism] = []
        for fraction in protocol["mechanisms"][mechanism]["fractions"]:
            rng = random.Random(f"{protocol['seed']}:{mechanism}:{fraction}")
            rows = []
            for _ in range(protocol["replicates"]):
                degraded, removed = degrade(
                    tables, region, mechanism, fraction, rng, protocol["protocol_id"]
                )
                run, _, run_balances = make_traces(degraded, region, scenario)
                rows.append(measure(run, run_balances, baseline, removed, size, tolerance))
            results[mechanism].append({"fraction": fraction, **summarize(rows)})
    violations = sum(
        level["abstention_violations"]["max"] for levels in results.values() for level in levels
    )
    residual = max(
        level["max_conservation_residual_tonnes"]["max"]
        for levels in results.values()
        for level in levels
    )
    report = {
        "protocol_id": protocol["protocol_id"],
        "status": protocol["status"],
        "purpose": protocol["purpose"],
        "scientific_accuracy_evidence": False,
        "scenario_id": scenario.scenario_id,
        "seed": protocol["seed"],
        "replicates": protocol["replicates"],
        "hashes": {
            "protocol": file_hash(protocol_path),
            "scenario": file_hash(scenario_path),
            "region": file_hash(region_path),
            "input_index": file_hash(input_dir / "index.json"),
            "code": code_hash(),
        },
        "baseline": {
            "development_nodes": len(traces),
            "ranked": len(baseline["kw"]),
            "tie_inclusive_top_set": sorted(base_top),
            "top_set_size": len(base_top),
            "known_production_tonnes": fsum(
                b.input_tonnes for b in balances if b.input_tonnes is not None
            ),
        },
        "checks": {
            "abstention_violations_total": violations,
            "max_conservation_residual_tonnes": residual,
            "abstention_holds": violations == 0,
        },
        "results": results,
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--protocol", type=Path, default=Path("docs/proposals/sparse-data-stress-v1.protocol.json")
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/sparse-data-stress"))
    parser.add_argument("--allow-temporary-scenario", action="store_true")
    args = parser.parse_args()
    report = run_stress(args.root, args.protocol, args.output, args.allow_temporary_scenario)
    print(json.dumps({"checks": report["checks"], "scientific_accuracy_evidence": False}, indent=2))


if __name__ == "__main__":
    main()
