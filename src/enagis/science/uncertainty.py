"""Joint, reproducible parameter draws and distinct magnitude/ranking summaries."""

from itertools import combinations
from math import sqrt

import numpy as np
from scipy.stats import qmc


def sample_parameters(config):
    groups = sorted(
        {p.joint_group for p in config.parameters.values() if p.distribution != "fixed"}
    )
    # Shared group = same quantile, explicitly comonotonic, not an inferred covariance model.
    uniforms = qmc.Sobol(d=max(1, len(groups)), scramble=True, seed=config.seed).random_base2(
        config.draw_power
    )
    rows = []
    for u in uniforms:
        parameters = {}
        for name, p in sorted(config.parameters.items()):
            value = p.central
            if p.distribution == "triangular":
                quantile = u[groups.index(p.joint_group)]
                width = p.upper - p.lower
                split = (p.central - p.lower) / width
                if quantile < split:
                    value = p.lower + sqrt(quantile * width * (p.central - p.lower))
                else:
                    value = p.upper - sqrt((1 - quantile) * width * (p.upper - p.central))
            parameters[name] = float(value)
        rows.append(parameters)
    return rows


def magnitude(values, quantiles):
    known = [v for v in values if v is not None]
    if not known:
        return {"lower": None, "median": None, "upper": None, "known_draws": 0}
    lo, mid, hi = np.quantile(known, [quantiles[0], 0.5, quantiles[1]], method="linear")
    return {"lower": float(lo), "median": float(mid), "upper": float(hi), "known_draws": len(known)}


def summarize(draws, sites, config):
    rows = []
    cases = sorted({d["case_id"] for d in draws})
    for site in sorted(sites, key=lambda s: s.node_id):
        records = [d["nodes"][site.node_id] for d in draws]
        by_case = {}
        for case in cases:
            subset = [d["nodes"][site.node_id] for d in draws if d["case_id"] == case]
            by_case[case] = sum(r["in_top_k"] for r in subset) / len(subset)
        reasons = sorted({reason for r in records for reason in r["verification_reasons"]})
        inclusion = sum(r["in_top_k"] for r in records) / len(records)
        tier = (
            "Verify-first"
            if reasons
            else (
                "Robust"
                if min(by_case.values()) >= config.ranking.robust_inclusion
                else "Contested"
            )
        )
        magnitudes = {
            key: magnitude(
                [r["requirement"][key] for r in records], config.ranking.interval_quantiles
            )
            for key in records[0]["requirement"]
        }
        rows.append(
            {
                "node_id": site.node_id,
                "tier": tier,
                "inclusion_frequency": inclusion,
                "inclusion_by_case": by_case,
                "draw_count": len(records),
                "magnitude": magnitudes,
                "margin_kw": magnitude(
                    [r["gap"]["capacity_minus_requirement_kw"] for r in records],
                    config.ranking.interval_quantiles,
                ),
                "verification_reasons": reasons,
                "question": question(site, reasons),
                "eligible_draws": sum(r["rank"] is not None for r in records),
            }
        )
    rows.sort(
        key=lambda r: (
            -r["inclusion_frequency"],
            -(r["magnitude"]["electrical_kw"]["median"] or 0),
            r["node_id"],
        )
    )
    rank = 0
    for row in rows:
        row["rank"] = None
        if row["eligible_draws"]:
            rank += 1
            row["rank"] = rank
    return rows


def question(site, reasons):
    if "production_unknown" in reasons:
        return "What wheat quantity and seasonal inventory does this site's source area support?"
    if "storage_capacity_unknown" in reasons:
        return "What physical storage is available to wheat, and for how long?"
    if "supply_capacity_unknown" in reasons:
        return "Which aeration fans operate simultaneously, and what is their measured input kW?"
    if "unreachable_in_scenario" in reasons:
        return "Is the mapped access route usable in the modeled season and transport mode?"
    return (
        site.unresolved_question
        or "Do measured peak wheat inventory and fan duty support this estimate?"
    )


def ablations(draws, config):
    # Descriptive matched-draw comparisons only; these do not select a winning method.
    by_case = {}
    for row in draws:
        by_case.setdefault(row["case_id"], {})[row["draw_id"]] = row
    results = []
    for a, b in combinations(sorted(by_case), 2):
        # Compare one configured factor at a time.
        left, right = by_case[a][0], by_case[b][0]
        changed = [k for k in ("profile_id", "season", "assignment_variant") if left[k] != right[k]]
        if len(changed) != 1:
            continue
        membership_changes, displacements = [], []
        for draw_id in sorted(by_case[a]):
            la, lb = by_case[a][draw_id]["top_k"], by_case[b][draw_id]["top_k"]
            membership_changes.append(len(set(la) ^ set(lb)))
            common = set(la) & set(lb)
            displacements.append(sum(abs(la.index(n) - lb.index(n)) for n in common))
        results.append(
            {
                "case_a": a,
                "case_b": b,
                "factor": changed[0],
                "draws": len(membership_changes),
                "mean_membership_symmetric_difference": float(np.mean(membership_changes)),
                "max_membership_symmetric_difference": max(membership_changes),
                "mean_common_rank_displacement": float(np.mean(displacements)),
                "retention_decision": "not_made_by_engine",
            }
        )
    return results
