"""Deterministic prospective samples and baseline frames; no outcome argument exists."""

import hashlib

from enagis.science.runner import canonical
from enagis.verification.contracts import STRATA


def validate_frame(ranking, frame, protocol):
    ids = [r["node_id"] for r in ranking]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidate identity")
    ranked = sorted((r for r in ranking if r["rank"] is not None), key=lambda r: r["rank"])
    if [r["rank"] for r in ranked] != list(range(1, len(ranked) + 1)):
        raise ValueError("ranking must have unique contiguous positive ranks")
    if frame.purpose != protocol.purpose:
        raise ValueError("frame and protocol purposes disagree")
    if frame.purpose == "scientific_reviewed" and not frame.approval:
        raise ValueError("baseline/flag frame requires recorded human review")
    if frame.purpose == "synthetic_fixture" and frame.approval:
        raise ValueError("fixture frame cannot claim human approval")
    if frame.purpose == "synthetic_fixture" and any(not n.startswith("fixture:") for n in ids):
        raise ValueError("synthetic sample cannot consume real candidate identities")
    arms = [a.arm_id for a in frame.baselines]
    if len(set(arms)) != len(arms) or set(arms) != set(protocol.required_baseline_arms):
        raise ValueError("every required baseline needs one ranking or explicit unavailability")
    eligible = {r["node_id"] for r in ranked}
    for arm in frame.baselines:
        if arm.ordered_node_ids and set(arm.ordered_node_ids) != eligible:
            raise ValueError(
                "baseline and primary ranking must use the same eligible candidate cohort"
            )
    flags = [(f.node_id, f.kind) for f in frame.flags]
    if len(set(flags)) != len(flags) or {f.node_id for f in frame.flags} - set(ids):
        raise ValueError("duplicate flag or flag outside the frozen candidate frame")
    return ranked


def make_sample(ranking, frame, protocol):
    ranked = validate_frame(ranking, frame, protocol)
    tail = ranked[protocol.top_k :]
    midpoint = (len(tail) + 1) // 2
    pools = {
        "top": ranked[: protocol.top_k],
        "middle": tail[:midpoint],
        "lower": tail[midpoint:],
    }
    for kind in STRATA[3:]:
        flagged = {f.node_id for f in frame.flags if f.kind == kind}
        pools[kind] = [r for r in ranking if r["node_id"] in flagged]
    chosen, rows, strata = set(), [], []
    for name in STRATA:
        available = [r for r in pools[name] if r["node_id"] not in chosen]
        requested = protocol.sample_counts[name]
        if name in STRATA[:3] and len(available) < requested:
            raise ValueError(f"insufficient {name} candidates for the frozen protocol quota")
        count = min(requested, len(available))

        def priority(row, stratum=name):
            payload = [protocol.seed, stratum, row["node_id"]]
            return hashlib.sha256(canonical(payload)).hexdigest(), row["node_id"]

        selected = sorted(available, key=priority)[:count]
        strata.append(
            {
                "stratum": name,
                "pool_before_prior_selections": len(pools[name]),
                "eligible_at_selection": len(available),
                "requested": requested,
                "selected": count,
                "shortfall": requested - count,
            }
        )
        for row in selected:
            chosen.add(row["node_id"])
            rows.append(
                {
                    "node_id": row["node_id"],
                    "rank": row["rank"],
                    "tier": row["tier"],
                    "question": row["question"],
                    "stratum": name,
                    "flags": sorted(f.kind for f in frame.flags if f.node_id == row["node_id"]),
                    "conditional_selection_fraction": count / len(available),
                }
            )
    if len(rows) < protocol.minimum_sample:
        raise ValueError(
            "sample is below the protocol minimum; no relaxed gate or automatic refill"
        )
    return {
        "purpose": protocol.purpose,
        "seed": protocol.seed,
        "method": protocol.selection_method,
        "candidate_count": len(ranking),
        "eligible_ranked_count": len(ranked),
        "unranked_count": len(ranking) - len(ranked),
        "rows": sorted(rows, key=lambda r: (STRATA.index(r["stratum"]), r["node_id"])),
        "strata": strata,
        "probability_interpretation": (
            "Selection fractions are conditional on prior stages. They are not marginal survey "
            "weights; do not pool this stratified, supplemented sample into population precision."
        ),
        "replacements": protocol.replacements,
    }
