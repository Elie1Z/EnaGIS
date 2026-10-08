"""Prospective sampling, consent, missingness, frozen ancestry and privacy regressions."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from verification_fixture import frame, observation, protocol, ranking

from enagis.verification.contracts import Baseline, Flag, Records
from enagis.verification.sampling import make_sample


def test_seeded_sample_is_disjoint_order_independent_and_covers_top_ten():
    p, f, rows = protocol(), frame(), ranking()
    f.flags = [
        Flag(node_id=n, kind=k, evidence_ref="fixture:flag")
        for n in ("fixture:n01", "fixture:n22", "fixture:n23", "fixture:n24")
        for k in ("disagreement", "siting_flagged")
    ]
    sample = make_sample(rows, f, p)
    assert sample == make_sample(list(reversed(rows)), f, p)
    assert len(sample["rows"]) == len({r["node_id"] for r in sample["rows"]}) == 14
    assert {r["rank"] for r in sample["rows"] if r["stratum"] == "top"} == set(range(1, 11))
    assert {r["stratum"] for r in sample["rows"]} == set(p.sample_counts)
    assert "not marginal" in sample["probability_interpretation"]


def test_core_shortage_stops_but_supplement_shortage_is_reported():
    with pytest.raises(ValueError, match="insufficient lower"):
        make_sample(ranking(11), frame(), protocol())
    sample = make_sample(ranking(12), frame(), protocol())
    assert len(sample["rows"]) == 12
    assert [s["shortfall"] for s in sample["strata"]] == [0, 0, 0, 1, 1]


def test_baseline_common_cohort_and_flag_identity_cannot_silently_change():
    p, f, rows = protocol(), frame(), ranking()
    f.baselines[0] = Baseline(
        arm_id="B0",
        ordered_node_ids=["fixture:n01"],
        evidence_ref="fixture:baseline",
        unavailable_reason=None,
    )
    with pytest.raises(ValueError, match="same eligible"):
        make_sample(rows, f, p)
    f = frame()
    f.flags = [Flag(node_id="fixture:unknown", kind="disagreement", evidence_ref="fixture:flag")]
    with pytest.raises(ValueError, match="outside"):
        make_sample(rows, f, p)


@pytest.mark.parametrize(
    "outcome",
    [
        "confirmed",
        "node_absent",
        "undocumented_supply",
        "requirement_negligible",
        "seasonal_irrelevance",
        "unknown",
        "unreachable",
        "declined",
        "not_contacted",
    ],
)
def test_private_outcomes_are_explicit_and_coherent(outcome):
    assert observation(outcome=outcome).outcome == outcome


def test_unknown_absence_and_consent_cannot_be_promoted_to_confirmation():
    with pytest.raises(ValidationError, match="ordered factual"):
        observation(node_exists=None)
    with pytest.raises(ValidationError, match="consent"):
        observation(consent="declined")
    with pytest.raises(ValidationError, match="factual"):
        observation(outcome="unreachable", node_exists=True)
    with pytest.raises(ValidationError, match="ordered factual"):
        observation(outcome="seasonal_irrelevance", requirement_negligible=None)


def test_pre_freeze_or_out_of_sample_observation_is_rejected():
    p = protocol()
    sample = make_sample(ranking(), frame(), p)
    records = Records(
        schema_version="phase7-records-v1",
        purpose="synthetic_fixture",
        freeze_id="fixture:freeze",
        frozen_manifest_sha256="0" * 64,
        records=[observation()],
    )
    with pytest.raises(ValueError, match="predates"):
        records.validate_against(sample, p, datetime(2026, 10, 11, tzinfo=UTC))
    records.records = [observation(node_id="fixture:alien")]
    with pytest.raises(ValueError, match="outside"):
        records.validate_against(sample, p, datetime(2026, 10, 8, tzinfo=UTC))


def test_fixture_cannot_claim_ranking_v1_or_scientific_approval():
    p = protocol()
    with pytest.raises(ValueError, match="fixture permission"):
        p.authorize()
    p.freeze_tag = "ranking-v1"
    with pytest.raises(ValueError, match="reserve ranking-v1"):
        p.authorize(allow_fixture=True)


def test_real_protocol_approval_cannot_be_bypassed_with_fixture_flag():
    p = protocol()
    p.purpose = "scientific_reviewed"
    p.protocol_id = "ca:verification"
    p.freeze_tag = "ranking-v1"
    p.allowed_methods = ["phone"]
    with pytest.raises(ValueError, match="human-approved protocol"):
        p.authorize(allow_fixture=True)


def test_duplicate_mixed_and_future_real_records_fail():
    p = protocol()
    sample = make_sample(ranking(), frame(), p)
    records = Records(
        schema_version="phase7-records-v1",
        purpose=p.purpose,
        freeze_id="fixture:freeze",
        frozen_manifest_sha256="0" * 64,
        records=[observation(), observation()],
    )
    stamp = datetime(2026, 10, 8, tzinfo=UTC)
    with pytest.raises(ValueError, match="duplicate"):
        records.validate_against(sample, p, stamp)
    records.records = [observation()]
    records.purpose = "scientific_reviewed"
    with pytest.raises(ValueError, match="cannot be mixed"):
        records.validate_against(sample, p, stamp)
    p.purpose = "scientific_reviewed"
    records.records = [observation(observed_at="2099-01-01T00:00:00Z")]
    with pytest.raises(ValueError, match="future"):
        records.validate_against(sample, p, stamp)
