"""Phase 4X: the Python port must match the registered JavaScript evaluation, and the frozen
protocol/outputs must be consistent. Reference values were produced by live/js/siting.js."""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from research.phase4x import core

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/audits/phase4x-evaluation.json"


def test_mulberry32_is_bit_exact_with_siting_js():
    rnd = core.mulberry32(20261011)
    expected = [
        0.34649015543982387,
        0.8141545492690057,
        0.5728907466400415,
        0.28456209879368544,
        0.048498414224013686,
        0.8908840359654278,
    ]
    assert [rnd() for _ in expected] == expected


def test_captured_and_auc_match_siting_js_including_ties():
    assert core.captured([5, 4, 4, 4, 1, 0, 0, 0, 0, 0], [1, 0, 1, 0, 1, 0, 0, 0, 0, 1], 0.2) == (
        pytest.approx(4 / 3)
    )
    assert core.captured([3, 3, 3, 3], [1, 0, 0, 1], 0.5) == 1
    assert core.auc([1, 2, 2, 3, 0], [0, 1, 0, 1, 0]) == pytest.approx(0.9166666666666666)
    assert core.auc([1, 2], [0, 0]) is None


def test_logistic_port_matches_siting_js_fit():
    x = np.array([[0, 1], [1, 3], [2, 2], [3, 5], [4, 4], [5, 7], [6, 5], [7, 9]], dtype=float)
    y = np.array([0, 0, 1, 0, 1, 0, 1, 1])
    m = core.fit_logistic(x, y)
    assert m["intercept"] == pytest.approx(-0.0004812250372854122, abs=1e-9)
    assert m["coef"] == pytest.approx([0.8968673157272748, -0.23721037698090852], abs=1e-9)


def test_prior_correction_and_calibration_are_well_defined():
    y_train = np.array([1] + [0] * 9)
    # A balanced-weight margin of 0 means odds 1:1 under weights; corrected to the 1:9 prior.
    assert core.prior_corrected(np.array([0.0]), y_train)[0] == pytest.approx(0.1)
    p = np.linspace(0.05, 0.95, 20)
    y = (p > 0.5).astype(int)
    c = core.calibration(p, y)
    assert len(c["reliability"]) == 10 and sum(b["n"] for b in c["reliability"]) == 20
    assert 0 <= c["ece"] <= 1 and c["brier"] == pytest.approx(float(np.mean((p - y) ** 2)))


def test_features_follow_the_registered_order_and_transforms():
    assert core.FEATURE_IDS[0] == "log_bld" and core.FEATURE_IDS[-1] == "urban_share"
    js = (ROOT / "live/js/siting.js").read_text(encoding="utf-8")
    assert [i for i in core.FEATURE_IDS if f'id: "{i}"' in js] == core.FEATURE_IDS
    row = {
        "nb": 9,
        "nbN": 99,
        "n200": 1,
        "n600": 0,
        "amax": 600,
        "maj_km": 7,
        "min_km": 2,
        "d_maj": 1000,
        "d_pow": 3000,
        "d_set": 500,
        "urb": 0.25,
    }
    x = core.design([row])[0]
    assert x[0] == pytest.approx(math.log(10)) and x[5] == 5 and x[7] == pytest.approx(math.log(2))


def test_protocol_hash_is_frozen_and_matches():
    recorded = (ROOT / "docs/spec/phase4x-protocol.sha256").read_text(encoding="utf-8").split()[0]
    assert core.sha256_file(ROOT / "docs/spec/phase4x-protocol.md") == recorded
    # The registered Phase 4R protocol is untouched.
    r = (ROOT / "docs/spec/phase4r-protocol.sha256").read_text(encoding="utf-8").split()[0]
    assert core.sha256_file(ROOT / "docs/spec/phase4r-protocol.md") == r


@pytest.mark.skipif(not AUDIT.exists(), reason="Phase 4X has not been run")
def test_phase4x_audit_is_consistent_with_its_protocol_and_decision_rule():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["protocol"]["sha256"] == core.sha256_file(ROOT / "docs/spec/phase4x-protocol.md")
    assert a["input"]["sha256"] == core.TABLE_SHA256 and a["reproduction"]["pass"] is True
    rule = a["decision_rule"]
    d = a["xgboost_minus_logistic"][0]
    assert rule["min_points"] == (d["point"] >= 0.03)
    assert rule["interval_above_zero"] == (d["ci"][0] > 0)
    ece = a["calibration"]
    assert rule["calibration_not_worse"] == (ece["xgboost"]["ece"] <= ece["logistic"]["ece"] + 0.01)
    expected = (
        "ADOPT"
        if all(rule[k] for k in ("min_points", "interval_above_zero", "calibration_not_worse"))
        else "TESTED, NOT BETTER"
    )
    assert a["verdict"] == expected
    app = (ROOT / "live/js/model-comparison.js").read_text(encoding="utf-8")
    assert a["protocol"]["sha256"][:16] in app and json.dumps(a["verdict"]) in app
    assert "validated" not in json.dumps(a).lower()
