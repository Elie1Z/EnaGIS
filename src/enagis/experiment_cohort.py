"""Counts-only availability audit. No scores, fitted models, outcomes or evaluation metrics."""

import json
from pathlib import Path

import numpy as np
from scipy.spatial.distance import cdist

from enagis.data_io import file_hash, safe_path, write_json
from enagis.experiment_contracts import ExperimentProtocol
from enagis.experiment_network import build_network, catchment_masks
from enagis.experiment_prepare import load_preparation

REASONS = (
    "population_unknown",
    "production_unknown",
    "snap_failure",
    "spatial_review",
    "unresolved_match",
)


def count_cohorts(units, labels, production, graph, xy, protocol):
    """Reachability and known/missing flags only; never sum or rank production."""
    if any(u.province not in protocol.development_units for u in units):
        raise ValueError("transfer study unit in development counts")
    if len({u.unit_id for u in units}) != len(units):
        raise ValueError("duplicate study unit")
    labels_by_id = {label.unit_id: label for label in labels}
    if len(labels_by_id) != len(labels):
        raise ValueError("duplicate presence label")
    regions = {p.geometry_ref: p.modeled_tonnes.value is not None for p in production}
    points = [u.point_xy for u in units]
    euclidean = cdist(points, points) <= protocol.catchment_distance_m
    reachable, _, snapped = catchment_masks(graph, xy, points, protocol)
    production_known = np.asarray(
        [
            bool(u.production_intersections_m2)
            and all(regions.get(key, False) for key in u.production_intersections_m2)
            for u in units
        ]
    )
    nearby_unsnapped = (euclidean & ~snapped[None, :]).any(axis=1)
    primary_reasons, sensitivity_reasons = [], []
    for i, unit in enumerate(units):
        common = []
        label = labels_by_id.get(unit.unit_id)
        if label is None or not unit.block_id:
            common.append("unresolved_match")
        if label is not None and label.status == "spatial_review_required":
            common.append("spatial_review")
        if unit.population.value is None:
            common.append("population_unknown")
        sensitivity_reasons.append(common.copy())
        required_known = (
            production_known[i]
            and production_known[euclidean[i]].all()
            and production_known[reachable[i]].all()
        )
        primary = common.copy()
        if not required_known:
            primary.append("production_unknown")
        if not snapped[i] or nearby_unsnapped[i]:
            primary.append("snap_failure")
        primary_reasons.append(primary)

    def summarize(reasons, feature_names):
        included = [u for u, r in zip(units, reasons, strict=True) if not r]
        positives = [u for u in included if labels_by_id[u.unit_id].status == "documented_presence"]
        return {
            "input_ccs": len(units),
            "complete_ccs": len(included),
            "positive_ccs": len(positives),
            "positive_cars": len({u.block_id for u in positives}),
            "excluded_ccs": len(units) - len(included),
            "exclusions_by_reason": {
                reason: sum(reason in r for r in reasons) for reason in REASONS
            },
            "reason_counts_overlap": True,
            "feature_names": feature_names,
            "complete_unit_ids": [u.unit_id for u in included],
            "excluded_units": [
                {"unit_id": u.unit_id, "reasons": r}
                for u, r in zip(units, reasons, strict=True)
                if r
            ],
        }

    primary = summarize(
        primary_reasons,
        sorted(
            set(protocol.full_features)
            | {
                "production_context",
                "euclidean_production",
                "accessible_production",
                "population",
                "log_ccs_area",
            }
        ),
    )
    sensitivity = summarize(sensitivity_reasons, protocol.sensitivity_features)
    gate = (
        primary["positive_ccs"] >= protocol.minimum_positive_units
        and primary["positive_cars"] >= protocol.minimum_positive_blocks
    )
    return {
        "status": "counts_only_no_scores_fits_outcomes_or_metrics",
        "primary": primary,
        "sensitivity": sensitivity | {"role": protocol.sensitivity_role},
        "primary_gate_passed": bool(gate),
        "decision": "proceed_to_frozen_values_check" if gate else "STOP_not_testable",
        "reason_definitions": {
            "population_unknown": "Any missing or spatially uncertain population component",
            "production_unknown": "Missing contributing production in B0, B1 or B2; "
            "no tonnage sum computed",
            "snap_failure": "Target or potentially reachable source exceeds "
            "unchanged snap tolerance",
            "spatial_review": "CCS censored by unresolved registry coordinate match",
            "unresolved_match": "Missing CCS label or CAR identity; "
            "not an invented location for unlocated facilities",
        },
        "sensitivity_definition": "Drops all production features and their catchment/snap "
        "completeness requirements; population, geometry and label checks remain",
        "transfer_evaluated": False,
    }


def diagnose_cohorts(root: Path, protocol_path: Path, preparation: Path, output: Path):
    protocol = ExperimentProtocol.model_validate_json(protocol_path.read_bytes())
    if protocol.development_units != ["AB", "SK"] or protocol.untouched_transfer_units != ["MB"]:
        raise ValueError("partition differs from frozen benchmark")
    index, data = load_preparation(preparation)
    if index["metadata"]["config_sha256"] != file_hash(protocol_path):
        raise ValueError("preparation differs from amended configuration")
    source = root / "data/processed/phase2"
    entries = {e["path"]: e for e in json.loads((source / "index.json").read_bytes())["artifacts"]}
    paths = []
    for province in protocol.development_units:
        name = f"roads_{province}.jsonl"
        path = safe_path(source, name)
        if file_hash(path) != entries[name]["sha256"]:
            raise ValueError("road checksum mismatch")
        paths.append(path)
    network = build_network(paths, data["units.json"], protocol, counts_only=True)
    report = count_cohorts(
        data["units.json"],
        data["labels.json"],
        data["production.json"],
        network[0],
        network[1],
        protocol,
    )
    report.update(
        protocol_sha256=file_hash(protocol_path),
        preparation_index_sha256=file_hash(preparation / "index.json"),
        topology_audit=network[-1],
    )
    write_json(output, report)
    return {
        k: v for k, v in report.items() if k in {"status", "primary_gate_passed", "decision"}
    } | {
        name: {
            k: v
            for k, v in report[name].items()
            if k
            in {
                "input_ccs",
                "complete_ccs",
                "positive_ccs",
                "positive_cars",
                "excluded_ccs",
                "exclusions_by_reason",
            }
        }
        for name in ("primary", "sensitivity")
    }
