"""Shipping-point evaluation: one observed outcome per group, never per elevator."""

from collections import defaultdict
from math import fsum

import numpy as np

from enagis.experiment_metrics import spearman, top_recall


def join_hindcast(outcomes, links, traces, facility_blocks, facility_units, features, protocol):
    protocol.require_approval()
    point_members = defaultdict(list)
    seen_facilities = set()
    for link in links:
        if link.facility_id in seen_facilities:
            raise ValueError("facility appears in multiple shipping-point groups")
        seen_facilities.add(link.facility_id)
        point_members[link.shipping_point_id].append(link.facility_id)
    observed = {o.shipping_point_id: o for o in outcomes}
    if len(observed) != len(outcomes):
        raise ValueError("duplicated observed shipping point")
    if any(o.split != "development" for o in outcomes):
        raise ValueError("transfer outcomes cannot enter hindcast development")
    by_facility = {t.facility.facility_id: t for t in traces}
    if len(by_facility) != len(traces):
        raise ValueError("duplicate predicted facility")
    by_unit = {f.unit_id: f for f in features}
    rows = []
    for point_id, outcome in sorted(observed.items()):
        facilities = sorted(point_members[point_id])
        source = outcome.conversion.converted
        if source.unit != "tonne" or source.dimension != "storage_mass":
            raise ValueError("hindcast outcomes must be period tonnes")
        reasons = []
        if not facilities:
            reasons.append("No matched facility")
        predictions = [
            by_facility[f].assigned_tonnes_per_reporting_period.value if f in by_facility else None
            for f in facilities
        ]
        if any(v is None for v in predictions):
            reasons.append("At least one member has unknown/missing modeled volume")
        blocks = {facility_blocks.get(f) for f in facilities}
        block = next(iter(blocks)) if len(blocks) == 1 and None not in blocks else None
        if block is None:
            reasons.append("No unique spatial block for entire shipping-point group")
        unit_ids = {facility_units.get(f) for f in facilities}
        scores = {}
        for arm, key in (
            ("B0", "production_context"),
            ("B1", "euclidean_production"),
            ("B2", "accessible_production"),
            ("population", "population"),
        ):
            values = [by_unit[u].features[key].value if u in by_unit else None for u in unit_ids]
            # Baselines are relative geographic exposure scores, not additive deliveries.
            # Mean over unique CCS avoids duplicating a shared contextual score across elevators.
            scores[arm] = (
                float(np.mean(values)) if values and all(v is not None for v in values) else None
            )
        predicted = (
            fsum(predictions) if predictions and not any(v is None for v in predictions) else None
        )
        scores["EnaGIS_phase3"] = predicted
        if any(v is None for v in scores.values()):
            reasons.append("At least one comparison arm lacks a score")
        rows.append(
            {
                "shipping_point_id": point_id,
                "facility_ids": facilities,
                "member_count": len(facilities),
                "block_id": block,
                "observed_tonnes": source.amount.value,
                "predicted_tonnes": predicted,
                "scores": scores,
                "exclusion_reasons": reasons,
                "outcome_source": outcome.model_dump(mode="json"),
                "prediction_status": "Phase 3 temporary administrative/inventory scenario",
                "absolute_volume_interpretation": "Diagnostic residual only: "
                "crop harvest versus crop-year marketed deliveries,"
                " unresolved channel share, carry-over and registry chronology",
            }
        )
    return rows


def evaluate_hindcast(rows, protocol):
    protocol.require_approval()
    included = [r for r in rows if not r["exclusion_reasons"]]
    report = {
        "observed_groups": len(rows),
        "common_comparison_groups": len(included),
        "excluded_groups": len(rows) - len(included),
        "facility_level_observations": 0,
        "observed_total_tonnes_counted_once": fsum(r["observed_tonnes"] for r in rows),
        "scope": "Retrospective shipping-point diagnostic, "
        "not per-facility or temporal forecast validation",
        "absolute_volume_accuracy_validated": False,
        "expert_shortlist": "Unavailable; no expert elicitation supplied",
    }
    blocks = sorted({r["block_id"] for r in included})
    # CAR fallback retains matched point observations, not complete district totals.
    report["partial_car_fallback"] = [
        {
            "block_id": b,
            "matched_groups": sum(r["block_id"] == b for r in included),
            "observed_matched_tonnes": fsum(
                r["observed_tonnes"] for r in included if r["block_id"] == b
            ),
            "predicted_matched_tonnes": fsum(
                r["predicted_tonnes"] for r in included if r["block_id"] == b
            ),
            "complete_district_total": False,
        }
        for b in blocks
    ]
    if len(included) < protocol.minimum_hindcast_groups:
        return report | {
            "status": "insufficient_common_groups",
            "decision": "No validation claim; partial CAR fallback only",
        }
    observed = np.asarray([r["observed_tonnes"] for r in included])
    predicted = np.asarray([r["predicted_tonnes"] for r in included])
    report["diagnostic_volume_residuals"] = {
        "mae_tonnes": float(np.abs(predicted - observed).mean()),
        "bias_tonnes": float((predicted - observed).mean()),
        "sum_prediction_over_sum_observation": float(predicted.sum() / observed.sum())
        if observed.sum()
        else None,
    }
    arms = list(included[0]["scores"])
    rng = np.random.default_rng(protocol.seed)
    draws = []
    if len(blocks) >= 2:
        for _ in range(protocol.bootstrap_draws):
            chosen = rng.choice(blocks, size=len(blocks), replace=True)
            selected = [r for b in chosen for r in included if r["block_id"] == b]
            draws.append(
                {
                    a: spearman(
                        [r["scores"][a] for r in selected], [r["observed_tonnes"] for r in selected]
                    )
                    for a in arms
                }
            )
    alpha = (1 - protocol.confidence_level) / 2
    metrics = {}
    for arm in arms:
        values = [r["scores"][arm] for r in included]
        valid = [r[arm] for r in draws if r[arm] is not None]
        # Recall of the highest observed-volume groups, using the same budget for every arm.
        ids = [r["shipping_point_id"] for r in included]
        k = int(np.ceil(len(ids) * protocol.primary_top_fraction))
        top_observed = set(sorted(range(len(ids)), key=lambda i: (-observed[i], ids[i]))[:k])
        metrics[arm] = {
            "spearman": spearman(values, observed),
            "interval": np.quantile(valid, [alpha, 1 - alpha]).tolist() if valid else None,
            "valid_bootstrap_draws": len(valid),
            "top_volume_group_recall": top_recall(
                ids,
                values,
                [i in top_observed for i in range(len(ids))],
                protocol.primary_top_fraction,
            ),
        }
    return report | {
        "status": "evaluated_diagnostic",
        "blocks": len(blocks),
        "arms": metrics,
        "confidence_level": protocol.confidence_level,
        "seed": protocol.seed,
    }
