"""Phase 4N: footprint classifier for grain mills, Njombe Region (second site, track C1).

Usage (repository root, after `node research/phase4n/gather.mjs`):
  uv run --group research python -m research.phase4n.run
Follows docs/spec/phase4n-protocol.md; aborts if the protocol hash or the gathered inputs
do not match their records. Writes docs/audits/phase4n-evaluation.json. Metric code is
shared with Phase 4X (research/phase4x/core.py).
"""

from __future__ import annotations

import csv
import json
import math
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import shapely
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import shape

from research.phase4x import core

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "docs/spec/phase4n-protocol.md"
PROTOCOL_HASH = ROOT / "docs/spec/phase4n-protocol.sha256"
INPUTS = ROOT / "outputs/phase4n"
OUT_JSON = ROOT / "docs/audits/phase4n-evaluation.json"
KS = (0.01, 0.05)
DRAWS, SEED, BLOCK_M, MATCH_M = 2000, 20261015, 10_000, 30.0
FEATURES = [
    "log_area",
    "log_perimeter",
    "elongation",
    "rectangularity",
    "log_bld_200m",
    "log_bld_1km",
    "area_share_of_largest_200m",
    "log_dist_major_road",
    "log_dist_any_road",
    "log_dist_settlement",
    "log_dist_power",
]
BASELINES = {
    "largest_roof": "Largest roof first",
    "neighbours": "Most buildings within 200 m",
    "major_road": "Closest to a major road",
}
XGB = {**core.XGB_PARAMS, "tree_method": "hist", "max_bin": 256, "n_jobs": 4}


def check_protocol() -> str:
    recorded = PROTOCOL_HASH.read_text(encoding="utf-8").split()[0]
    actual = core.sha256_file(PROTOCOL)
    if recorded != actual:
        raise SystemExit(f"Protocol hash {actual} != frozen {recorded}; amend, do not edit.")
    return actual


def check_inputs() -> dict:
    m = json.loads((INPUTS / "manifest.json").read_text(encoding="utf-8"))
    for f in m["files"]:
        if core.sha256_file(ROOT / f["path"]) != f["sha256"]:
            raise SystemExit(f"Input changed since gathering: {f['path']}")
    return m


def read_csv(name: str, numeric: int) -> tuple[np.ndarray, list[list[str]]]:
    with (INPUTS / name).open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))[1:]
    return np.array([[float(v) for v in r[:numeric]] for r in rows]), [r[numeric:] for r in rows]


def nearest(tree: cKDTree | None, xy: np.ndarray, cap: float) -> np.ndarray:
    if tree is None:
        return np.full(len(xy), cap)
    d, _ = tree.query(xy, k=1, distance_upper_bound=cap)
    return np.minimum(d, cap)


def max_area_within(tree: cKDTree, xy: np.ndarray, area: np.ndarray, r: float) -> np.ndarray:
    out = np.empty(len(xy))
    for s in range(0, len(xy), 50_000):
        for i, nb in enumerate(tree.query_ball_point(xy[s : s + 50_000], r=r)):
            out[s + i] = area[nb].max()
    return out


def capture_per_item(scores: np.ndarray, y: np.ndarray, k: float) -> np.ndarray:
    """Each positive's (fractional) capture in its council's top share k; sums to core.captured."""
    n = len(scores)
    m = max(1, math.ceil(k * n))
    cut = np.sort(scores)[::-1][m - 1]
    gt, eq = scores > cut, scores == cut
    frac = (m - gt.sum()) / eq.sum()
    return np.where(y == 1, np.where(gt, 1.0, np.where(eq, frac, 0.0)), 0.0)


def evaluate(x, y, council, block, area, nb200, dmaj, councils, label=""):
    """Leave-one-council-out for all arms; returns point values, intervals and decisions."""
    arms = ["logistic", "xgboost", *BASELINES]
    cap = {a: [np.zeros(len(y)) for _ in KS] for a in arms}
    pooled = {a: np.zeros(len(y)) for a in arms}
    prob = {a: np.zeros(len(y)) for a in ("logistic", "xgboost")}
    for c in councils:
        te, tr = council == c, (council != c) & (council != "")
        lm = core.fit_logistic(x[tr], y[tr])
        xm = fit_xgb(x[tr], y[tr])
        s = {
            "logistic": core.logistic_margin(lm, x[te]),
            "xgboost": core.xgb_margin(xm, x[te]),
            "largest_roof": area[te],
            "neighbours": nb200[te],
            "major_road": -dmaj[te],
        }
        for a in arms:
            pooled[a][te] = s[a]
            for ki, k in enumerate(KS):
                cap[a][ki][te] = capture_per_item(s[a], y[te], k)
        for a in prob:
            prob[a][te] = core.prior_corrected(s[a], y[tr])
        print(
            f"  {label}fold {c}: {int(te.sum())} footprints, {int(y[te].sum())} positive",
            flush=True,
        )
    use = council != ""
    npos = int(y[use].sum())
    point = {a: [float(cap[a][ki][use].sum() / npos) for ki in range(len(KS))] for a in arms}
    aucs = {a: core.auc(pooled[a][use].tolist(), y[use].tolist()) for a in arms}
    # Paired cluster bootstrap over 10 km blocks holding a positive.
    pos_blocks = sorted({b for b, v in zip(block[use], y[use], strict=True) if v})
    bpos = {b: 0 for b in pos_blocks}
    bcap = {a: [{b: 0.0 for b in pos_blocks} for _ in KS] for a in arms}
    for i in np.where(use & (y == 1))[0]:
        bpos[block[i]] += 1
        for a in arms:
            for ki in range(len(KS)):
                bcap[a][ki][block[i]] += cap[a][ki][i]
    rnd = core.mulberry32(SEED)
    boot = {a: [[] for _ in KS] for a in arms}
    vs_best = {a: [[] for _ in KS] for a in ("logistic", "xgboost")}
    paired = [[] for _ in KS]
    for _ in range(DRAWS):
        sample = [pos_blocks[int(rnd() * len(pos_blocks))] for _ in pos_blocks]
        for ki in range(len(KS)):
            v = {a: core.recall(sample, bcap[a][ki], bpos) for a in arms}
            for a in arms:
                boot[a][ki].append(v[a])
            best = max(v[b] for b in BASELINES)
            for a in vs_best:
                vs_best[a][ki].append(v[a] - best)
            paired[ki].append(v["xgboost"] - v["logistic"])
    best0 = max(BASELINES, key=lambda b: point[b][0])
    cal = {a: core.calibration(prob[a][use], y[use]) for a in prob}
    margin = {
        a: {"point": point[a][0] - point[best0][0], "ci": core.ci95(vs_best[a][0])} for a in vs_best
    }
    diff = {"point": point["xgboost"][0] - point["logistic"][0], "ci": core.ci95(paired[0])}
    rule = {
        "min_points": diff["point"] >= 0.03,
        "interval_above_zero": diff["ci"][0] > 0,
        "calibration_not_worse": cal["xgboost"]["ece"] <= cal["logistic"]["ece"] + 0.01,
    }
    per_council = [
        {
            "council": c,
            "footprints": int((council == c).sum()),
            "positives": int(y[council == c].sum()),
            **{f"{a}_captured_1pct": float(cap[a][0][council == c].sum()) for a in arms},
        }
        for c in councils
    ]
    return {
        "footprints": int(use.sum()),
        "positives": npos,
        "positive_blocks": len(pos_blocks),
        "arms": [
            {
                "arm": a,
                "label": BASELINES.get(a, a),
                "evidence": "ESTIMATED (held-out recall of surveyed mills)",
                "recall": [
                    {"k": k, "point": point[a][ki], "ci": core.ci95(boot[a][ki])}
                    for ki, k in enumerate(KS)
                ],
                "auc": aucs[a],
            }
            for a in arms
        ],
        "best_baseline": best0,
        "margin_over_best_baseline": margin,
        "verdict_footprint_classifier": "KEEP" if margin["logistic"]["ci"][0] > 0 else "KILL",
        "xgboost_vs_baseline_descriptive": "above"
        if margin["xgboost"]["ci"][0] > 0
        else "not above",
        "xgboost_minus_logistic": [
            diff,
            {"point": point["xgboost"][1] - point["logistic"][1], "ci": core.ci95(paired[1])},
        ],
        "xgboost_rule": rule,
        "verdict_xgboost": "XGBOOST BETTER" if all(rule.values()) else "NOT BETTER",
        "calibration": cal,
        "per_council": per_council,
    }


def fit_xgb(x, y):
    from xgboost import XGBClassifier

    w_pos, w_neg = core.balanced_weights(y)
    m = XGBClassifier(**XGB)
    m.fit(x, y, sample_weight=np.where(y == 1, w_pos, w_neg))
    return m


def main() -> dict:
    t0 = time.time()
    protocol_sha = check_protocol()
    manifest = check_inputs()
    fp, extra = read_csv("footprints.csv", 6)
    source = np.array([e[0] for e in extra])
    lon, lat, area, perim, elong, rect = fp.T
    tf = Transformer.from_crs("EPSG:4326", "EPSG:32736", always_xy=True)
    xy = np.column_stack(tf.transform(lon, lat))
    councils_geo = json.loads((INPUTS / "councils.json").read_text(encoding="utf-8"))
    council = np.full(len(lon), "", dtype=object)
    for c in councils_geo:
        inside = shapely.contains_xy(shape(c["geojson"]), lon, lat) & (council == "")
        council[inside] = c["name"]
    councils = [c["name"] for c in councils_geo]
    print(f"{len(lon)} footprints; {int((council == '').sum())} outside every council polygon")

    tree = cKDTree(xy)
    nb200 = tree.query_ball_point(xy, r=200, return_length=True) - 1
    nb1k = tree.query_ball_point(xy, r=1000, return_length=True) - 1
    amax200 = max_area_within(tree, xy, area, 200)
    roads, _ = read_csv("roads.csv", 3)
    rxy = np.column_stack(tf.transform(roads[:, 0], roads[:, 1]))
    major = roads[:, 2] == 1
    dmaj = nearest(cKDTree(rxy[major]) if major.any() else None, xy, 15_000)
    dany = nearest(cKDTree(rxy), xy, 5_000)
    pl, _ = read_csv("places.csv", 2)
    dset = nearest(
        cKDTree(np.column_stack(tf.transform(pl[:, 0], pl[:, 1]))) if len(pl) else None, xy, 15_000
    )
    pw, _ = read_csv("power.csv", 2)
    dpow = nearest(
        cKDTree(np.column_stack(tf.transform(pw[:, 0], pw[:, 1]))) if len(pw) else None, xy, 25_000
    )
    x = np.column_stack(
        [
            np.log(np.maximum(area, 1e-6)),
            np.log(np.maximum(perim, 1e-6)),
            elong,
            rect,
            np.log1p(nb200),
            np.log1p(nb1k),
            area / amax200,
            np.log1p(dmaj),
            np.log1p(dany),
            np.log1p(dset),
            np.log1p(dpow),
        ]
    )

    # Labels: each mill to the nearest footprint centroid within 30 m.
    mills, _ = read_csv("mills.csv", 2)
    mxy = np.column_stack(tf.transform(mills[:, 0], mills[:, 1]))
    d, idx = tree.query(mxy, k=1, distance_upper_bound=MATCH_M)
    matched = np.isfinite(d)
    y = np.zeros(len(lon), dtype=int)
    y[idx[matched]] = 1
    labels = {
        "mills": len(mills),
        "matched_mills": int(matched.sum()),
        "unmatched_mills": int((~matched).sum()),
        "positive_footprints": int(y.sum()),
        "match_radius_m": MATCH_M,
        "match_distance_m_median": float(np.median(d[matched])) if matched.any() else None,
        "positive_councils": int(len({council[i] for i in np.where(y == 1)[0] if council[i]})),
        "positives_outside_councils": int(((council == "") & (y == 1)).sum()),
    }
    gate = labels["positive_footprints"] >= 300 and labels["positive_councils"] >= 6
    print(json.dumps(labels))
    block = np.array([f"{int(a // BLOCK_M)}:{int(b // BLOCK_M)}" for a, b in xy])

    if not gate:
        result = {"verdict": "FEASIBILITY"}
    else:
        result = evaluate(x, y, council, block, area, nb200, dmaj, councils)

    # Leakage check (descriptive): geometry source of positives vs background; ML-source-only rerun.
    ml = np.array([("Google" in s) or ("Microsoft" in s) for s in source])
    srcs = sorted(set(source))
    leak = {
        "source_share_positive": {s: float(np.mean(source[y == 1] == s)) for s in srcs},
        "source_share_background": {s: float(np.mean(source[y == 0] == s)) for s in srcs},
    }
    if gate and y[ml].sum() >= 100:
        c_ml = np.where(ml, council, "")
        sub = evaluate(x, y, c_ml, block, area, nb200, dmaj, councils, label="ML-only ")
        leak["ml_sources_only"] = {
            k: sub[k]
            for k in (
                "footprints",
                "positives",
                "arms",
                "best_baseline",
                "margin_over_best_baseline",
                "xgboost_minus_logistic",
            )
        }
    import sklearn
    import xgboost

    out = {
        "schema": "enagis-phase4n-evaluation-v1",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seconds": None,
        "protocol": {"file": "docs/spec/phase4n-protocol.md", "sha256": protocol_sha},
        "inputs": {
            "manifest": manifest["files"],
            "overture_release": manifest["overture_release"],
            "osm_relation": manifest["osm_relation"],
            "counts": manifest["counts"],
            "note": "Inputs stay in the gitignored outputs/phase4n/ (they hold survey points).",
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "xgboost": xgboost.__version__,
            "scikit_learn": sklearn.__version__,
            "hardware": f"{platform.machine()} CPU, no GPU",
        },
        "crs": "EPSG:32736 (UTM 36S), metres",
        "features": FEATURES,
        "xgboost_params": XGB,
        "councils": councils,
        "footprints_outside_councils": int((council == "").sum()),
        "labels": labels,
        "gate": gate,
        **result,
        "leakage_check": leak,
        "bootstrap": {
            "draws": DRAWS,
            "seed": SEED,
            "generator": "mulberry32",
            "paired": True,
            "clusters": "10 km UTM blocks holding a positive",
        },
    }
    out["seconds"] = round(time.time() - t0, 1)
    OUT_JSON.write_text(
        json.dumps(out, indent=1, default=lambda o: o.item()) + "\n", encoding="utf-8"
    )
    if gate:
        a = {r["arm"]: r["recall"][0]["point"] for r in result["arms"]}
        print(
            f"top1%: logistic {a['logistic']:.3f} xgboost {a['xgboost']:.3f} best baseline "
            f"{result['best_baseline']} {a[result['best_baseline']]:.3f} -> "
            f"{result['verdict_footprint_classifier']}, "
            f"{result['verdict_xgboost']}"
        )
    return out


if __name__ == "__main__":
    main()
