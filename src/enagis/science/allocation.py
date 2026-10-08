"""Shared capacity across all origins; no source mass is assigned twice."""

from math import fsum, isfinite

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def allocate(masses, limits, routes, variant, unknown_capacity, tolerance):
    if variant not in {"min_cost_max_served", "nearest_first"}:
        raise ValueError("unknown allocation variant")
    if unknown_capacity not in {"exclude_and_flag", "unbounded_and_flag"}:
        raise ValueError("explicit unknown-capacity policy required")
    if tolerance <= 0 or any(
        v is not None and (not isfinite(v) or v < 0) for v in [*masses.values(), *limits.values()]
    ):
        raise ValueError("invalid mass/capacity")
    pairs = [(r["origin_id"], r["node_id"]) for r in routes]
    if len(set(pairs)) != len(pairs):
        raise ValueError("duplicate accessibility pair")
    if set(pairs) != {(o, n) for o in masses for n in limits}:
        raise ValueError("accessibility join lost/added origin-node pairs")
    if any(
        r["minutes"] is not None and (not isfinite(r["minutes"]) or r["minutes"] < 0)
        for r in routes
    ):
        raise ValueError("invalid travel time")
    candidates = sorted(
        (r["origin_id"], r["node_id"], r["minutes"])
        for r in routes
        if r["minutes"] is not None
        and masses[r["origin_id"]] is not None
        and (limits[r["node_id"]] is not None or unknown_capacity == "unbounded_and_flag")
    )
    assignment = np.zeros(len(candidates))
    if candidates and variant == "nearest_first":
        remaining = {o: v for o, v in masses.items() if v is not None}
        available = {n: float("inf") if v is None else v for n, v in limits.items()}
        for i in sorted(
            range(len(candidates)),
            key=lambda i: (candidates[i][2], candidates[i][0], candidates[i][1]),
        ):
            origin, node, _ = candidates[i]
            value = min(remaining[origin], available[node])
            assignment[i] = value
            remaining[origin] -= value
            available[node] -= value
    elif candidates:
        origins = sorted(o for o, v in masses.items() if v is not None)
        nodes = sorted(n for n, v in limits.items() if v is not None)
        oi, ni = (
            {o: i for i, o in enumerate(origins)},
            {n: i + len(origins) for i, n in enumerate(nodes)},
        )
        a, b = [], []
        for i, (o, n, _) in enumerate(candidates):
            a.append(oi[o])
            b.append(i)
            if n in ni:
                a.append(ni[n])
                b.append(i)
        matrix = csr_matrix(
            (np.ones(len(a)), (a, b)), shape=(len(origins) + len(nodes), len(candidates))
        )
        bounds = [masses[o] for o in origins] + [limits[n] for n in nodes]
        # Two objectives in sequence: maximize served mass, then minimize tonne-minutes.
        first = linprog(-np.ones(len(candidates)), A_ub=matrix, b_ub=bounds, method="highs-ds")
        if not first.success:
            raise ValueError(f"allocation maximum-service solve failed: {first.message}")
        total = fsum(first.x)
        second = linprog(
            [c[2] for c in candidates],
            A_ub=matrix,
            b_ub=bounds,
            A_eq=csr_matrix(np.ones((1, len(candidates)))),
            b_eq=[total],
            method="highs-ds",
        )
        if not second.success:
            raise ValueError(f"allocation travel solve failed: {second.message}")
        # Sorted identities + pinned deterministic dual-simplex solver define ties.
        # No tiny cost perturbation that could silently change the scientific objective.
        assignment = second.x
    assignments = [
        {"origin_id": o, "node_id": n, "tonnes": float(v), "minutes": t}
        for (o, n, t), v in zip(candidates, assignment, strict=True)
        if v > 0
    ]
    balances = []
    for origin, mass in sorted(masses.items()):
        known = mass is not None
        assigned = fsum(r["tonnes"] for r in assignments if r["origin_id"] == origin)
        reachable = [r for r in routes if r["origin_id"] == origin and r["minutes"] is not None]
        remainder = None if not known else mass - assigned
        if known and remainder < -tolerance:
            raise ValueError("assigned more than source production")
        if known and abs(remainder) <= tolerance:
            remainder = 0.0
        reason = None
        if not known:
            reason = "production_unknown"
        elif remainder > 0:
            reason = "capacity_exhausted" if reachable else "no_reachable_candidate"
            if reachable and all(limits[r["node_id"]] is None for r in reachable):
                reason = "candidate_capacity_unknown"
        balances.append(
            {
                "origin_id": origin,
                "input_tonnes": mass,
                "assigned_tonnes": assigned if known else None,
                "unserved_tonnes": remainder,
                "residual_tonnes": mass - assigned - remainder if known else None,
                "reason": reason,
            }
        )
    totals = {n: fsum(r["tonnes"] for r in assignments if r["node_id"] == n) for n in limits}
    if any(limits[n] is not None and totals[n] > limits[n] + tolerance for n in limits):
        raise ValueError("shared node capacity exceeded")
    if any(
        b["residual_tonnes"] is not None and abs(b["residual_tonnes"]) > tolerance for b in balances
    ):
        raise ValueError("production conservation failed")
    if (
        abs(fsum(b["residual_tonnes"] for b in balances if b["residual_tonnes"] is not None))
        > tolerance
    ):
        raise ValueError("total production conservation failed")
    unknown_affected = {
        r["node_id"] for r in routes if r["minutes"] is not None and masses[r["origin_id"]] is None
    }
    return {
        "assignments": assignments,
        "balances": balances,
        "known_assigned_tonnes": totals,
        "unknown_production_nodes": sorted(unknown_affected),
        "unknown_capacity_nodes": sorted(n for n, v in limits.items() if v is None),
    }
