"""Phase 4X: XGBoost vs the registered logistic siting model on the frozen Rwanda table.

Usage (repository root): uv run --group research python -m research.phase4x.run
Follows docs/spec/phase4x-protocol.md exactly; aborts if the protocol hash, the table hash or the
reproduction of the registered Phase 4R result does not match. Writes:
  docs/audits/phase4x-evaluation.json, live/js/model-comparison.js
"""

from __future__ import annotations

import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

from research.phase4x import core

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "docs/spec/phase4x-protocol.md"
PROTOCOL_HASH = ROOT / "docs/spec/phase4x-protocol.sha256"
TABLE = ROOT / "data/rwanda/siting_cells.csv"
REGISTERED = ROOT / "docs/audits/phase4r-evaluation.json"
OUT_JSON = ROOT / "docs/audits/phase4x-evaluation.json"
OUT_APP = ROOT / "live/js/model-comparison.js"
KS = (0.1, 0.2)
DRAWS = 2000
SEED_REGISTERED, SEED_4X, SEED_PERM = 20261011, 20261012, 20261013
LABEL = "y_any"
ADOPT_MIN_POINTS = 0.03
ECE_TOLERANCE = 0.01


def pct1(v: float) -> float:
    return round(v * 1000) / 10


def check_protocol() -> str:
    recorded = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0]
    actual = core.sha256_file(PROTOCOL)
    if recorded != actual:
        raise SystemExit(f"Protocol hash {actual} != frozen {recorded}; amend, do not edit.")
    return actual


def folds(rows: list[dict], x: np.ndarray, y: np.ndarray, districts: list[str]) -> dict:
    """Leave-one-district-out for the registered logistic model and the baselines."""
    out = {}
    names = np.array([r["district"] for r in rows])
    for d in districts:
        test, train = np.where(names == d)[0], np.where(names != d)[0]
        lm = core.fit_logistic(x[train], y[train])
        scores = {"logistic": core.logistic_margin(lm, x[test])}
        for b, f in core.BASELINES.items():
            scores[b] = np.array([f(rows[i]) for i in test], dtype=float)
        out[d] = {
            "test": test,
            "train": train,
            "y": y[test],
            "scores": scores,
            "models": {"logistic": lm},
        }
    return out


def add_xgboost(f: dict, x: np.ndarray, y: np.ndarray, districts: list[str]) -> None:
    """Scored only after the reproduction gate has passed (protocol)."""
    for d in districts:
        m = core.fit_xgb(x[f[d]["train"]], y[f[d]["train"]])
        f[d]["models"]["xgboost"] = m
        f[d]["scores"]["xgboost"] = core.xgb_margin(m, x[f[d]["test"]])
        print(
            f"  xgboost fold {d}: {len(f[d]['test'])} cells, {int(f[d]['y'].sum())} positive",
            flush=True,
        )


def bootstrap(blocks, caps, pos, arms, seed, ki):
    rnd = core.mulberry32(seed)
    boot = {a: [] for a in arms}
    best_margin = {a: [] for a in arms}
    paired = []
    base = list(core.BASELINES)
    for _ in range(DRAWS):
        sample = [blocks[int(rnd() * len(blocks))] for _ in blocks]
        v = {a: core.recall(sample, caps[a][ki], pos) for a in arms}
        for a in arms:
            boot[a].append(v[a])
        best = max(v[b] for b in base)
        for a in ("logistic", "xgboost"):
            best_margin[a].append(v[a] - best)
        paired.append(v["xgboost"] - v["logistic"])
    return boot, best_margin, paired


def registered_bootstrap(blocks, caps, pos):
    """The exact Phase 4R loop (both k values consume one sample per draw)."""
    rnd = core.mulberry32(SEED_REGISTERED)
    margin = [[] for _ in KS]
    for _ in range(DRAWS):
        sample = [blocks[int(rnd() * len(blocks))] for _ in blocks]
        for ki in range(len(KS)):
            best = max(core.recall(sample, caps[b][ki], pos) for b in core.BASELINES)
            margin[ki].append(core.recall(sample, caps["logistic"][ki], pos) - best)
    return margin


def permutation_importance(f: dict, x: np.ndarray, districts: list[str]) -> dict:
    rng = np.random.default_rng(SEED_PERM)
    ys = np.concatenate([f[d]["y"] for d in districts])
    base = {
        a: core.auc(np.concatenate([f[d]["scores"][a] for d in districts]).tolist(), ys.tolist())
        for a in ("logistic", "xgboost")
    }
    out = {a: [] for a in base}
    for j, fid in enumerate(core.FEATURE_IDS):
        drops = {a: [] for a in base}
        for _ in range(5):
            pooled = {a: [] for a in base}
            for d in districts:
                xt = x[f[d]["test"]].copy()
                xt[:, j] = xt[rng.permutation(len(xt)), j]
                pooled["logistic"].append(core.logistic_margin(f[d]["models"]["logistic"], xt))
                pooled["xgboost"].append(core.xgb_margin(f[d]["models"]["xgboost"], xt))
            for a in base:
                drops[a].append(base[a] - core.auc(np.concatenate(pooled[a]).tolist(), ys.tolist()))
        for a in base:
            out[a].append({"feature": fid, "auc_drop": float(np.mean(drops[a]))})
    return {"baseline_auc": base, "repeats": 5, "seed": SEED_PERM, **out}


def main() -> dict:
    t0 = time.time()
    protocol_sha = check_protocol()
    rows = core.load_table(TABLE)
    x = core.design(rows)
    y = np.array([int(r[LABEL]) for r in rows])
    districts = sorted({r["district"] for r in rows})
    pos = {d: int(sum(r[LABEL] for r in rows if r["district"] == d)) for d in districts}
    blocks = [d for d in districts if pos[d] > 0]
    y_narrow = [r for r in rows if r["y"]]
    gate = int(y.sum()) >= 60 and len(blocks) >= 6
    print(
        f"{len(rows)} cells, {len(districts)} districts, {int(y.sum())} positive in {len(blocks)}"
    )

    f = folds(rows, x, y, districts)
    ys = np.concatenate([f[d]["y"] for d in districts])

    def caps_for(a):
        return [
            {d: core.captured(f[d]["scores"][a].tolist(), f[d]["y"].tolist(), k) for d in districts}
            for k in KS
        ]

    def auc_for(a):
        return core.auc(
            np.concatenate([f[d]["scores"][a] for d in districts]).tolist(), ys.tolist()
        )

    caps = {a: caps_for(a) for a in ["logistic", *core.BASELINES]}
    point = {a: [core.recall(blocks, caps[a][ki], pos) for ki in range(len(KS))] for a in caps}

    # Reproduction gate: the registered Phase 4R numbers, to 0.1 point.
    reg = json.loads(REGISTERED.read_text(encoding="utf-8"))
    reg_ev = reg["evaluation"]
    reg_model = next(a for a in reg_ev["arms"] if a["arm"] == "model")
    reg_best = reg_ev["best_baseline"][0]
    best0 = max(core.BASELINES, key=lambda b: point[b][0])
    rmargin = registered_bootstrap(blocks, caps, pos)
    repro_ci = core.ci95(rmargin[0])
    full_logistic = core.fit_logistic(x, y)
    coef_diff = float(
        np.max(np.abs(np.array(full_logistic["coef"]) - np.array(reg["model"]["coef"])))
    )
    reproduction = {
        "logistic_recall_10": point["logistic"][0],
        "registered_recall_10": reg_model["recall"][0]["point"],
        "best_baseline": best0,
        "registered_best_baseline": reg_best,
        "best_baseline_recall_10": point[best0][0],
        "margin_10": point["logistic"][0] - point[best0][0],
        "margin_10_ci": repro_ci,
        "registered_margin_10_ci": reg_ev["margin"][0]["ci"],
        "full_model_max_coef_difference": coef_diff,
    }
    ok = (
        pct1(point["logistic"][0]) == 73.1
        and pct1(point[best0][0]) == 49.3
        and best0 == reg_best
        and pct1(reproduction["margin_10"]) == 23.9
        and [pct1(v) for v in repro_ci] == [13.4, 34.4]
        and coef_diff < 1e-6
    )
    reproduction["pass"] = ok
    print("reproduction:", json.dumps({k: v for k, v in reproduction.items()}, default=str))
    if not ok:
        raise SystemExit(
            "Registered Phase 4R result not reproduced; XGBoost comparison not reported."
        )

    # Only now: the challenger.
    add_xgboost(f, x, y, districts)
    arms = ["logistic", "xgboost", *core.BASELINES]
    caps["xgboost"] = caps_for("xgboost")
    point["xgboost"] = [core.recall(blocks, caps["xgboost"][ki], pos) for ki in range(len(KS))]
    aucs = {a: auc_for(a) for a in arms}

    # Phase 4X bootstrap (new seed, paired across arms).
    boot, best_margin, paired = bootstrap(blocks, caps, pos, arms, SEED_4X, 0)
    boot20, best_margin20, paired20 = bootstrap(blocks, caps, pos, arms, SEED_4X, 1)
    diff = point["xgboost"][0] - point["logistic"][0]
    diff_ci = core.ci95(paired)

    # Calibration on prior-corrected held-out probabilities.
    cal = {}
    for a in ("logistic", "xgboost"):
        p = np.concatenate(
            [core.prior_corrected(f[d]["scores"][a], y[f[d]["train"]]) for d in districts]
        )
        cal[a] = core.calibration(p, ys)
    cal_ok = cal["xgboost"]["ece"] <= cal["logistic"]["ece"] + ECE_TOLERANCE
    rule = {
        "min_points": diff >= ADOPT_MIN_POINTS,
        "interval_above_zero": diff_ci[0] > 0,
        "calibration_not_worse": cal_ok,
    }
    verdict = "FEASIBILITY" if not gate else "ADOPT" if all(rule.values()) else "TESTED, NOT BETTER"

    # Interpretation (descriptive).
    full_xgb = core.fit_xgb(x, y)
    gain = full_xgb.get_booster().get_score(importance_type="total_gain")
    gains = [
        {"feature": fid, "total_gain": float(gain.get(f"f{j}", 0.0))}
        for j, fid in enumerate(core.FEATURE_IDS)
    ]
    perm = permutation_importance(f, x, districts)
    abs_coef = np.abs(full_logistic["coef"])
    pi_x = [r["auc_drop"] for r in perm["xgboost"]]
    pi_l = [r["auc_drop"] for r in perm["logistic"]]
    agreement = {
        "xgb_perm_vs_logistic_perm": float(spearmanr(pi_x, pi_l).statistic),
        "xgb_perm_vs_logistic_abs_coef": float(spearmanr(pi_x, abs_coef).statistic),
        "logistic_perm_vs_logistic_abs_coef": float(spearmanr(pi_l, abs_coef).statistic),
        "xgb_gain_vs_logistic_abs_coef": float(
            spearmanr([g["total_gain"] for g in gains], abs_coef).statistic
        ),
    }

    import sklearn
    import xgboost

    arm_labels = {
        "logistic": "Logistic regression (registered Phase 4R model)",
        "xgboost": "XGBoost, fixed hyperparameters",
        "people": "Most buildings in the cell",
        "density": "Most buildings within 2 km",
        "road": "Closest to a major road",
        "town": "Closest to a town or village centre",
        "grid": "Closest to the mapped grid",
    }
    result = {
        "schema": "enagis-phase4x-evaluation-v1",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": None,
        "protocol": {"file": "docs/spec/phase4x-protocol.md", "sha256": protocol_sha},
        "registered_protocol": {
            "file": "docs/spec/phase4r-protocol.md",
            "sha256": reg["protocol"]["sha256"],
        },
        "input": {
            "file": "data/rwanda/siting_cells.csv",
            "sha256": core.TABLE_SHA256,
            "rows": len(rows),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "xgboost": xgboost.__version__,
            "scikit_learn": sklearn.__version__,
            "hardware": f"{platform.machine()} CPU, n_jobs=1, no GPU",
        },
        "label": LABEL,
        "label_y_processing_or_storage": {
            "positive_cells": len(y_narrow),
            "positive_districts": len({r["district"] for r in y_narrow}),
            "verdict": "FEASIBILITY (below 60 cells; counts only)",
        },
        "cells": len(rows),
        "districts": len(districts),
        "positive_cells": int(y.sum()),
        "positive_districts": len(blocks),
        "gate": gate,
        "xgboost_params": core.XGB_PARAMS,
        "reproduction": reproduction,
        "arms": [
            {
                "arm": a,
                "label": arm_labels[a],
                "evidence": "ESTIMATED (held-out recall of documented cells)",
                "recall": [
                    {
                        "k": k,
                        "point": point[a][ki],
                        "ci": core.ci95(boot[a] if ki == 0 else boot20[a]),
                    }
                    for ki, k in enumerate(KS)
                ],
                "auc": aucs[a],
            }
            for a in arms
        ],
        "xgboost_minus_logistic": [
            {"k": 0.1, "point": diff, "ci": diff_ci},
            {
                "k": 0.2,
                "point": point["xgboost"][1] - point["logistic"][1],
                "ci": core.ci95(paired20),
            },
        ],
        "margin_over_best_baseline": {
            a: [
                {"k": 0.1, "point": point[a][0] - point[best0][0], "ci": core.ci95(best_margin[a])},
                {
                    "k": 0.2,
                    "point": point[a][1] - max(point[b][1] for b in core.BASELINES),
                    "ci": core.ci95(best_margin20[a]),
                },
            ]
            for a in ("logistic", "xgboost")
        },
        "calibration": {
            **cal,
            "method": "prior-corrected held-out probabilities, 10 equal-count bins",
            "tolerance": ECE_TOLERANCE,
        },
        "decision_rule": {**rule, "min_points_required": ADOPT_MIN_POINTS},
        "verdict": verdict,
        "importance": {
            "xgboost_total_gain": gains,
            "permutation_auc_drop": perm,
            "logistic_full_model_coef": dict(
                zip(core.FEATURE_IDS, full_logistic["coef"], strict=True)
            ),
            "spearman_agreement": agreement,
        },
        "per_district": [
            {
                "district": d,
                "cells": len(f[d]["test"]),
                "positives": pos[d],
                "logistic_captured_10": caps["logistic"][0][d],
                "xgboost_captured_10": caps["xgboost"][0][d],
                "best_baseline_captured_10": caps[best0][0][d],
            }
            for d in districts
        ],
        "bootstrap": {
            "draws": DRAWS,
            "seed": SEED_4X,
            "generator": "mulberry32",
            "paired": True,
            "clusters": "districts with at least one positive cell",
        },
    }
    result["seconds"] = round(time.time() - t0, 1)
    OUT_JSON.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    app = {
        "verdict": verdict,
        "protocol_sha256": protocol_sha,
        "label": LABEL,
        "positive_cells": int(y.sum()),
        "positive_districts": len(blocks),
        "rows": [
            {
                "arm": a,
                "label": arm_labels[a],
                "recall10": point[a][0],
                "ci": core.ci95(boot[a]),
                "auc": aucs[a],
            }
            for a in ("xgboost", "logistic", best0)
        ],
        "difference": {"point": diff, "ci": diff_ci},
        "ece": {a: cal[a]["ece"] for a in cal},
        "rule": rule,
    }
    OUT_APP.write_text(
        "/* Phase 4X model comparison (XGBoost vs registered logistic).\n"
        " * Generated by research/phase4x/run.py under docs/spec/phase4x-protocol.md\n"
        f" * (sha256 {protocol_sha[:16]}…). Do not edit by hand. */\n"
        f"window.EnaModelComparison = {json.dumps(app)};\n",
        encoding="utf-8",
    )
    print(
        f"logistic {pct1(point['logistic'][0])}%  xgboost {pct1(point['xgboost'][0])}%  "
        f"diff {pct1(diff)} [{pct1(diff_ci[0])}, {pct1(diff_ci[1])}]  ECE "
        f"{cal['logistic']['ece']:.4f} vs {cal['xgboost']['ece']:.4f}  -> {verdict}"
    )
    return result


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
