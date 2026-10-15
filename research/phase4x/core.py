"""Phase 4X building blocks: a faithful Python port of the registered Phase 4R siting evaluation
(`live/js/siting.js`) plus the gradient-boosted challenger. Pure functions, deterministic.

Units: distances in the table are metres; features follow siting.js exactly (log1p of counts, km).
"""

from __future__ import annotations

import csv
import hashlib
import math
from collections.abc import Callable, Sequence
from pathlib import Path

import numpy as np

TABLE_SHA256 = "664350e8aa446b228ee541143621a3cdaeaca6250b4f6c136355f08565b11c92"
NUMERIC = "lon lat nb nbN n200 n600 amax maj_km min_km d_maj d_pow d_set urb y y_any".split()

# The 11 registered features, in order (siting.js FEATURES).
FEATURES: list[tuple[str, Callable[[dict], float]]] = [
    ("log_bld", lambda r: math.log1p(r["nb"])),
    ("log_bld_2km", lambda r: math.log1p(r["nbN"])),
    ("log_roof200", lambda r: math.log1p(r["n200"])),
    ("log_roof600", lambda r: math.log1p(r["n600"])),
    ("log_roof_max", lambda r: math.log1p(r["amax"])),
    ("major_road_km", lambda r: min(r["maj_km"], 5.0)),
    ("log_minor_road_km", lambda r: math.log1p(r["min_km"])),
    ("log_dist_major_road", lambda r: math.log1p(r["d_maj"] / 1000)),
    ("log_dist_power", lambda r: math.log1p(r["d_pow"] / 1000)),
    ("log_dist_centre", lambda r: math.log1p(r["d_set"] / 1000)),
    ("urban_share", lambda r: r["urb"]),
]
FEATURE_IDS = [f for f, _ in FEATURES]

# Single-signal baselines: higher = more likely (siting.js BASELINES).
BASELINES: dict[str, Callable[[dict], float]] = {
    "people": lambda r: r["nb"],
    "density": lambda r: r["nbN"],
    "road": lambda r: -r["d_maj"],
    "town": lambda r: -r["d_set"],
    "grid": lambda r: -r["d_pow"],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_table(path: Path, expected_sha: str = TABLE_SHA256) -> list[dict]:
    digest = sha256_file(path)
    if expected_sha and digest != expected_sha:
        raise ValueError(f"Training table hash {digest} != registered {expected_sha}")
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in NUMERIC:
            r[k] = float(r[k])
    return rows


def design(rows: Sequence[dict]) -> np.ndarray:
    return np.array([[f(r) for _, f in FEATURES] for r in rows], dtype=float)


# ------------------------------------------------------------------ registered generator and stats
def mulberry32(seed: int) -> Callable[[], float]:
    """Bit-exact port of siting.js mulberry32 (32-bit unsigned arithmetic)."""
    state = seed & 0xFFFFFFFF

    def imul(a: int, b: int) -> int:
        return (a * b) & 0xFFFFFFFF

    def rnd() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & 0xFFFFFFFF
        t = state
        t = imul(t ^ (t >> 15), t | 1)
        t = (t ^ ((t + imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rnd


def quantile(values: Sequence[float], p: float) -> float:
    s = sorted(values)
    pos = (len(s) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def ci95(values: Sequence[float]) -> list[float]:
    return [quantile(values, 0.025), quantile(values, 0.975)]


def captured(scores: Sequence[float], y: Sequence[int], k: float) -> float:
    """Positives in the top share k; ties at the cut-off count fractionally (siting.js)."""
    n = len(scores)
    m = max(1, math.ceil(k * n))
    cut = sorted(scores, reverse=True)[m - 1]
    gt = pos_gt = eq = pos_eq = 0
    for s, v in zip(scores, y, strict=True):
        if s > cut:
            gt += 1
            pos_gt += v
        elif s == cut:
            eq += 1
            pos_eq += v
    return pos_gt + pos_eq * (m - gt) / eq


def auc(scores: Sequence[float], y: Sequence[int]) -> float | None:
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rank_sum = 0.0
    npos = 0
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for t in range(i, j + 1):
            if y[order[t]]:
                rank_sum += r
                npos += 1
        i = j + 1
    nneg = len(y) - npos
    return (rank_sum - npos * (npos + 1) / 2) / (npos * nneg) if npos and nneg else None


def balanced_weights(y: np.ndarray) -> tuple[float, float]:
    n, npos = len(y), int(y.sum())
    nneg = n - npos
    return (n / (2 * npos) if npos else 1.0), (n / (2 * nneg) if nneg else 1.0)


# ------------------------------------------------------------------ registered logistic (IRLS)
def fit_logistic(x: np.ndarray, y: np.ndarray, lam: float = 1.0) -> dict:
    n, d = x.shape
    mean = x.mean(axis=0)
    sd = np.sqrt(((x - mean) ** 2).mean(axis=0))
    sd[sd == 0] = 1.0
    z = np.hstack([np.ones((n, 1)), (x - mean) / sd])
    w_pos, w_neg = balanced_weights(y)
    w = np.where(y == 1, w_pos, w_neg)
    beta = np.zeros(d + 1)
    for _ in range(50):
        p = 1 / (1 + np.exp(-(z @ beta)))
        g = z.T @ (w * (y - p))
        h = (z * (w * p * (1 - p))[:, None]).T @ z
        g[1:] -= lam * beta[1:]
        h[np.arange(1, d + 1), np.arange(1, d + 1)] += lam
        step = np.linalg.solve(h, g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-7:
            break
    return {"intercept": float(beta[0]), "coef": beta[1:].tolist(), "mean": mean, "sd": sd}


def logistic_margin(model: dict, x: np.ndarray) -> np.ndarray:
    return model["intercept"] + ((x - model["mean"]) / model["sd"]) @ np.asarray(model["coef"])


# ------------------------------------------------------------------ gradient-boosted challenger
XGB_PARAMS = {
    "max_depth": 3,
    "n_estimators": 200,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 1.0,
    "min_child_weight": 5,
    "reg_lambda": 1.0,
    "reg_alpha": 0.0,
    "gamma": 0.0,
    "objective": "binary:logistic",
    "tree_method": "exact",
    "n_jobs": 1,
    "random_state": 20261012,
}


def fit_xgb(x: np.ndarray, y: np.ndarray):
    from xgboost import XGBClassifier

    w_pos, w_neg = balanced_weights(y)
    model = XGBClassifier(**XGB_PARAMS)
    model.fit(x, y, sample_weight=np.where(y == 1, w_pos, w_neg))
    return model


def xgb_margin(model, x: np.ndarray) -> np.ndarray:
    return model.predict(x, output_margin=True).astype(float)


# ------------------------------------------------------------------ evaluation pieces
def prior_corrected(margin: np.ndarray, y_train: np.ndarray) -> np.ndarray:
    npos = int(y_train.sum())
    nneg = len(y_train) - npos
    return 1 / (1 + np.exp(-(margin - math.log(nneg / npos))))


def calibration(p: np.ndarray, y: np.ndarray, bins: int = 10) -> dict:
    order = np.argsort(p, kind="stable")
    table = []
    ece = 0.0
    for chunk in np.array_split(order, bins):
        mp, my = float(p[chunk].mean()), float(y[chunk].mean())
        ece += len(chunk) / len(p) * abs(mp - my)
        table.append({"n": int(len(chunk)), "mean_predicted": mp, "observed_share": my})
    return {"brier": float(np.mean((p - y) ** 2)), "ece": ece, "reliability": table}


def recall(blocks: Sequence[str], caps: dict, pos: dict) -> float | None:
    c = sum(caps[d] for d in blocks)
    p = sum(pos[d] for d in blocks)
    return c / p if p else None
