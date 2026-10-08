"""Offline end-to-end execution with complete inputs, per-draw traces and replay verification."""

import csv
import hashlib
import io
import json
from pathlib import Path

from enagis.data_io import file_hash, write_json
from enagis.ingestion import code_hash
from enagis.science import VERSION
from enagis.science.allocation import allocate
from enagis.science.contracts import Dataset, ScenarioConfig
from enagis.science.energy import annual_limit, gap, requirement
from enagis.science.roads import accessibility, build_network
from enagis.science.uncertainty import ablations, sample_parameters, summarize


def calculate(config, data, *, allow_fixture=False):
    config.authorize(data, allow_fixture=allow_fixture)
    sources = {s.snapshot_id for s in data.source_snapshots}
    if any(
        not set(p.evidence.source_ids) <= sources
        for p in [*config.parameters.values(), *config.transports]
    ):
        raise ValueError("orphan parameter/transport evidence source")
    parents = {p.production_id: p.tonnes.value for p in data.parents}
    masses = {
        o.origin_id: None
        if parents[o.production_id] is None
        else parents[o.production_id] * o.fraction
        for o in data.origins
    }
    parameter_draws = sample_parameters(config)
    draws, access = [], []
    for profile in config.transports:
        for season in config.seasons:
            network = build_network(data.roads, profile, season, config.metric_crs)
            routes, snaps = accessibility(
                network, data.origins, data.sites, profile, config.metric_crs
            )
            access.append(
                {
                    "profile_id": profile.profile_id,
                    "season": season,
                    "graph_audit": network.audit,
                    "snaps": snaps,
                    "routes": routes,
                }
            )
            reachable = {r["node_id"] for r in routes if r["minutes"] is not None}
            for variant in config.assignment_variants:
                case_id = f"{profile.profile_id}:{season}:{variant}"
                for draw_id, p in enumerate(parameter_draws):
                    limits = {
                        s.node_id: annual_limit(s.storage_tonnes.value, p) for s in data.sites
                    }
                    result = allocate(
                        masses,
                        limits,
                        routes,
                        variant,
                        config.unknown_capacity,
                        config.mass_tolerance_tonnes,
                    )
                    nodes = {}
                    for site in sorted(data.sites, key=lambda s: s.node_id):
                        reasons = []
                        mass = result["known_assigned_tonnes"][site.node_id]
                        if site.node_id in result["unknown_production_nodes"]:
                            mass = None
                            reasons.append("production_unknown")
                        if site.storage_tonnes.value is None:
                            reasons.append("storage_capacity_unknown")
                            if config.unknown_capacity == "exclude_and_flag":
                                mass = None
                        if site.node_id not in reachable:
                            reasons.append("unreachable_in_scenario")
                        if site.electrical_capacity_kw.value is None:
                            reasons.append("supply_capacity_unknown")
                        if site.unresolved_question:
                            reasons.append("site_question_unresolved")
                        req = requirement(mass, p)
                        nodes[site.node_id] = {
                            "requirement": req,
                            "gap": gap(
                                site.supply_state,
                                site.electrical_capacity_kw.value,
                                req["electrical_kw"],
                            ),
                            "verification_reasons": reasons,
                            "rank": None,
                            "in_top_k": False,
                        }
                    ranked = sorted(
                        (
                            n
                            for n, r in nodes.items()
                            if r["requirement"]["electrical_kw"] is not None
                            and r["requirement"]["electrical_kw"] > 0
                        ),
                        key=lambda n: (-nodes[n]["requirement"]["electrical_kw"], n),
                    )
                    for rank, n in enumerate(ranked, 1):
                        nodes[n]["rank"], nodes[n]["in_top_k"] = rank, rank <= config.ranking.top_k
                    draws.append(
                        {
                            "draw_id": draw_id,
                            "case_id": case_id,
                            "profile_id": profile.profile_id,
                            "season": season,
                            "assignment_variant": variant,
                            "parameters": p,
                            "allocation": result,
                            "nodes": nodes,
                            "top_k": ranked[: config.ranking.top_k],
                        }
                    )
    summary = summarize(draws, data.sites, config)
    return {
        "accessibility": access,
        "draws": draws,
        "ranking": summary,
        "shortlist": [
            r for r in summary if r["rank"] is not None and r["rank"] <= config.ranking.top_k
        ],
        "ablations": ablations(draws, config),
    }


def canonical(value):
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode() + b"\n"
    )


def load_config(path):
    raw = json.loads(path.read_bytes())
    if raw.get("status") == "pending_scientific_review":
        raise ValueError(
            "Phase 6 scientific gate: unresolved human-owned decisions; see review packet"
        )
    return ScenarioConfig.model_validate(raw)


def execute(config_path, input_path, output, lockfile, *, allow_fixture=False):
    config = load_config(config_path)
    data = Dataset.model_validate_json(input_path.read_bytes())
    config.authorize(data, allow_fixture=allow_fixture)
    if any(s.redistribution != "permitted" for s in data.source_snapshots):
        raise ValueError("portable runs cannot redistribute restricted/unresolved source evidence")
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("output must be new or empty; historical runs cannot be overwritten")
    if any(p.resolve().is_relative_to(output) for p in (config_path, input_path, lockfile)):
        raise ValueError("output cannot contain input/config/lockfile")
    result = calculate(config, data, allow_fixture=allow_fixture)
    cfg, dataset = config.model_dump(mode="json"), data.model_dump(mode="json")
    fingerprints = {
        "config_sha256": hashlib.sha256(canonical(cfg)).hexdigest(),
        "input_sha256": hashlib.sha256(canonical(dataset)).hexdigest(),
        "code_sha256": code_hash(),
        "lockfile_sha256": file_hash(lockfile),
    }
    identity = hashlib.sha256(canonical(fingerprints)).hexdigest()[:24]
    metadata = {
        "schema_version": VERSION,
        "run_id": f"phase6:{identity}",
        "purpose": config.purpose,
        "region_id": data.region_id,
        "metric_crs": config.metric_crs,
        "commodity_id": data.commodity_id,
        "service_id": data.service_id,
        "period_start": str(data.period_start),
        "period_end": str(data.period_end),
        "scenario_id": config.scenario_id,
        "reference_case": config.reference_case,
        "seed": config.seed,
        "parameter_draws_per_case": 2**config.draw_power,
        "ensemble_weighting": "equal weight per declared case; shared draws across cases",
        "interval_interpretation": "scenario/draw quantiles, not confidence intervals",
        "inclusion_interpretation": "stability under stated assumptions, not viability probability",
        "input_snapshot_ids": sorted(s.snapshot_id for s in data.source_snapshots),
        "requirement_label": "ESTIMATED",
        "classification_label": "INFERRED",
        "energy_period": "one modeled cooling cycle, not annual consumption",
        "peak_boundary": "simultaneous running fans plus auxiliary; excludes startup current",
        "scientifically_ready_to_freeze": False,
        "readiness_note": (
            "Synthetic fixtures never establish scientific readiness. Real runs need human "
            "review of ablations and benchmarks."
        ),
        **fingerprints,
    }
    files = {"config.json": cfg, "inputs.json": dataset}
    files.update(
        {f"{name}.json": {"metadata": metadata, "data": rows} for name, rows in result.items()}
    )
    output.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        write_json(output / name, body)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(
        [
            "rank",
            "node_id",
            "tier",
            "inclusion_frequency",
            "kw_lower",
            "kw_median",
            "kw_upper",
            "margin_kw_median",
            "question",
            "purpose",
        ]
    )
    for row in result["shortlist"]:
        mag = row["magnitude"]["electrical_kw"]
        writer.writerow(
            [
                row["rank"],
                row["node_id"],
                row["tier"],
                row["inclusion_frequency"],
                mag["lower"],
                mag["median"],
                mag["upper"],
                row["margin_kw"]["median"],
                row["question"],
                config.purpose,
            ]
        )
    (output / "shortlist.csv").write_text(stream.getvalue(), encoding="utf-8", newline="\n")
    entries = [
        {"path": name, "sha256": file_hash(output / name)}
        for name in sorted([*files, "shortlist.csv"])
    ]
    write_json(output / "index.json", {"metadata": metadata, "artifacts": entries})
    return {
        "run_id": metadata["run_id"],
        "purpose": config.purpose,
        "cases": len(result["accessibility"]) * len(config.assignment_variants),
        "draws": len(result["draws"]),
        "shortlist": len(result["shortlist"]),
    }


def verify(output, lockfile):
    index = json.loads((output / "index.json").read_bytes())
    expected = {
        "config.json",
        "inputs.json",
        "accessibility.json",
        "draws.json",
        "ranking.json",
        "shortlist.json",
        "ablations.json",
        "shortlist.csv",
    }
    entries = index["artifacts"]
    if {e["path"] for e in entries} != expected or len(entries) != len(expected):
        raise ValueError("unexpected artifact set")
    if {p.name for p in output.iterdir()} != expected | {"index.json"}:
        raise ValueError("unexpected files in run directory")
    for entry in entries:
        if file_hash(output / entry["path"]) != entry["sha256"]:
            raise ValueError(f"artifact checksum mismatch: {entry['path']}")
    metadata = index["metadata"]
    if metadata["code_sha256"] != code_hash() or metadata["lockfile_sha256"] != file_hash(lockfile):
        raise ValueError("replay requires the recorded code and lockfile")
    # Full replay also checks conservation, capacity, routes, ranking, quantiles and exports.
    from tempfile import TemporaryDirectory

    with TemporaryDirectory(prefix="enagis-phase6-replay-", dir=output.resolve().parent) as tmp:
        execute(
            output / "config.json",
            output / "inputs.json",
            Path(tmp),
            lockfile,
            allow_fixture=metadata["purpose"] == "synthetic_fixture",
        )
        for name in expected | {"index.json"}:
            if (Path(tmp) / name).read_bytes() != (output / name).read_bytes():
                raise ValueError(f"deterministic replay mismatch: {name}")
    return {
        "status": "verified",
        "artifacts": len(expected),
        "run_id": metadata["run_id"],
        "scientifically_ready_to_freeze": False,
    }
