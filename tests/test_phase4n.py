"""Phase 4N (Njombe second site): frozen protocol, consistent verdicts, no personal data."""

import json
import re
from pathlib import Path

import pytest

from research.phase4x import core

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/audits/phase4n-evaluation.json"


def test_protocol_hash_is_frozen_and_matches():
    recorded = (ROOT / "docs/spec/phase4n-protocol.sha256").read_text(encoding="utf-8").split()[0]
    assert core.sha256_file(ROOT / "docs/spec/phase4n-protocol.md") == recorded


@pytest.mark.skipif(not AUDIT.exists(), reason="Phase 4N has not been run")
def test_phase4n_audit_follows_its_decision_rules():
    a = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert a["protocol"]["sha256"] == core.sha256_file(ROOT / "docs/spec/phase4n-protocol.md")
    assert a["gate"] == (
        a["labels"]["positive_footprints"] >= 300 and a["labels"]["positive_councils"] >= 6
    )
    m = a["margin_over_best_baseline"]["logistic"]
    assert a["verdict_footprint_classifier"] == ("KEEP" if m["ci"][0] > 0 else "KILL")
    rule = a["xgboost_rule"]
    d = a["xgboost_minus_logistic"][0]
    assert rule["min_points"] == (d["point"] >= 0.03)
    assert rule["interval_above_zero"] == (d["ci"][0] > 0)
    assert a["verdict_xgboost"] == ("XGBOOST BETTER" if all(rule.values()) else "NOT BETTER")
    arms = {r["arm"]: r for r in a["arms"]}
    caps = sum(c["logistic_captured_1pct"] for c in a["per_council"])
    assert abs(caps / a["positives"] - arms["logistic"]["recall"][0]["point"]) < 1e-9
    assert a["labels"]["matched_mills"] + a["labels"]["unmatched_mills"] == a["labels"]["mills"]


@pytest.mark.skipif(not AUDIT.exists(), reason="Phase 4N has not been run")
def test_published_files_carry_no_names_or_phone_numbers():
    text = AUDIT.read_text(encoding="utf-8") + (ROOT / "docs/phase4n-results.md").read_text(
        encoding="utf-8"
    )
    assert "contact" not in text.lower() and "Milling Machine" not in text
    assert not re.search(r"\b255\d{9}\b", text)
    assert "validated" not in text.lower()
