"""Spatial recall, continuous Boyce, and paired block uncertainty with explicit undefined cases."""

import math

import numpy as np
from scipy.stats import rankdata


def spearman(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if len(a) != len(b) or len(a) < 2 or not np.isfinite(a).all() or not np.isfinite(b).all():
        return None
    x, y = rankdata(a), rankdata(b)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def top_recall(ids, scores, presence, fraction):
    if not 0 < fraction < 1 or len(set(ids)) != len(ids):
        raise ValueError("invalid evaluation units/fraction")
    if len(ids) != len(scores) or len(ids) != len(presence) or not np.isfinite(scores).all():
        raise ValueError("evaluation arrays disagree or contain missing scores")
    k = math.ceil(len(ids) * fraction)
    chosen = sorted(range(len(ids)), key=lambda i: (-scores[i], ids[i]))[:k]
    positives = int(sum(presence))
    hits = int(sum(presence[i] for i in chosen))
    return {
        "units": len(ids),
        "positive_units": positives,
        "selected_units": k,
        "hits": hits,
        "recall": hits / positives if positives else None,
    }


def continuous_boyce(scores, presence, window_fraction, resolution):
    """Moving-window P/E rank correlation, consecutive duplicate ratios removed.

    Empirical background is every evaluated unit, including documented presences.
    Zero observed counts remain zero P/E; undefined expected counts are skipped.
    """
    scores = np.asarray(scores, dtype=float)
    presence = np.asarray(presence, dtype=bool)
    if len(scores) != len(presence) or not np.isfinite(scores).all():
        raise ValueError("invalid Boyce input")
    if len(scores) < 2 or not presence.any() or np.ptp(scores) == 0:
        return {"value": None, "reason": "No presences or no score variation", "windows": 0}
    width = np.ptp(scores) * window_fraction
    centers = np.linspace(scores.min() + width / 2, scores.max() - width / 2, resolution)
    valid_centers, ratios = [], []
    for center in centers:
        inside = (scores >= center - width / 2) & (scores <= center + width / 2)
        expected = float(inside.mean())
        if expected == 0:
            continue
        ratio = float((inside & presence).sum() / presence.sum()) / expected
        if ratios and ratio == ratios[-1]:
            continue
        valid_centers.append(float(center))
        ratios.append(ratio)
    value = spearman(valid_centers, ratios)
    return {
        "value": value,
        "reason": None if value is not None else "Too few distinct P/E windows",
        "windows": len(ratios),
    }


def block_intervals(block_scores, baseline_names, draws, confidence, seed):
    """Paired bootstrap: resample the same complete spatial blocks for all arms."""
    rows = [
        r
        for r in block_scores
        if all(r.get(a) is not None for a in ["full_model", *baseline_names])
    ]
    if len(rows) < 2:
        return {"status": "insufficient_blocks", "blocks": len(rows), "decision": "not_testable"}
    names = ["full_model", *baseline_names]
    values = np.asarray([[row[n] for n in names] for row in rows])
    rng = np.random.default_rng(seed)
    samples = values[rng.integers(0, len(rows), size=(draws, len(rows)))].mean(axis=1)
    alpha = (1 - confidence) / 2

    def interval(v):
        return [float(x) for x in np.quantile(v, [alpha, 1 - alpha])]

    # Best competitor is recomputed in each paired draw, rather than cherry-picking a weak arm.
    margins = samples[:, 0] - samples[:, 1:].max(axis=1)
    bounds = interval(margins)
    means = values.mean(axis=0)
    return {
        "status": "evaluated",
        "blocks": len(rows),
        "draws": draws,
        "seed": seed,
        "confidence_level": confidence,
        "arms": {
            name: {"mean": float(means[i]), "interval": interval(samples[:, i])}
            for i, name in enumerate(names)
        },
        "margin_over_best_baseline": {
            "estimate": float(means[0] - means[1:].max()),
            "interval": bounds,
        },
        "decision": "keep" if bounds[0] > 0 else "kill_or_no_demonstrated_improvement",
    }
