"""Invented protocol, candidates and responses, never operational approvals or contacts."""

from enagis.verification.contracts import FAILURES, Frame, Observation, Protocol


def protocol():
    return Protocol.model_validate(
        {
            "schema_version": "phase7-protocol-v1",
            "protocol_id": "fixture:verification",
            "purpose": "synthetic_fixture",
            "freeze_tag": "fixture-ranking-v1",
            "seed": 23,
            "top_k": 10,
            "sample_counts": {
                "top": 10,
                "middle": 1,
                "lower": 1,
                "disagreement": 1,
                "siting_flagged": 1,
            },
            "minimum_sample": 12,
            "middle_band": "first_ceiling_half_after_top_k",
            "selection_method": "sha256_seed_stratum_node_id",
            "supplement_order": "disagreement_then_siting_flagged",
            "replacements": "none_after_freeze",
            "confidence_level": 0.95,
            "interval_method": "wilson_without_continuity_correction",
            "unresolved_policy": "report_bounds_and_resolved_denominator",
            "failure_precedence": list(FAILURES),
            "criteria": {
                key: f"Invented {key} criterion for software testing"
                for key in (*FAILURES, "confirmed")
            },
            "temporal_interpretation": (
                "Synthetic observation after synthetic seal; no actual site verification"
            ),
            "consent_text": "Synthetic test only; nobody is contacted",
            "allowed_methods": ["synthetic"],
            "required_baseline_arms": ["B0", "B1", "B2", "population", "expert"],
            "approval": None,
            "participant_commitment_ref": None,
        }
    )


def frame(index_hash="0" * 64):
    return Frame.model_validate(
        {
            "schema_version": "phase7-frame-v1",
            "purpose": "synthetic_fixture",
            "source_index_sha256": index_hash,
            "baselines": [
                {
                    "arm_id": a,
                    "ordered_node_ids": [],
                    "evidence_ref": "fixture:baseline",
                    "unavailable_reason": "No empirical baseline is represented by this fixture",
                }
                for a in protocol().required_baseline_arms
            ],
            "flags": [],
            "approval": None,
        }
    )


def ranking(count=24):
    return [
        {
            "node_id": f"fixture:n{i:02}",
            "rank": i,
            "tier": "Verify-first",
            "question": "Synthetic verification question",
        }
        for i in range(1, count + 1)
    ]


def observation(node_id="fixture:n01", outcome="confirmed", **updates):
    raw = {
        "node_id": node_id,
        "observed_at": "2026-10-10T12:00:00Z",
        "method": "synthetic",
        "contact_status": "completed",
        "consent": "granted",
        "node_exists": True,
        "undocumented_supply": False,
        "requirement_negligible": False,
        "seasonal_irrelevance": False,
        "outcome": outcome,
        "evidence_private_ref": "private:DO-NOT-PUBLISH-EVIDENCE",
        "assessor_private_ref": "private:DO-NOT-PUBLISH-PERSON",
    }
    if outcome == "node_absent":
        raw["node_exists"] = False
    elif outcome in FAILURES:
        raw[outcome] = True
    elif outcome == "unknown":
        raw["requirement_negligible"] = None
    elif outcome in {"unreachable", "declined", "not_contacted"}:
        raw.update({key: None for key in ["node_exists", *FAILURES[1:]]})
        raw.update(
            contact_status=outcome, consent="declined" if outcome == "declined" else "not_requested"
        )
        if outcome == "not_contacted":
            raw.update(observed_at=None, method=None)
    raw.update(updates)
    return Observation.model_validate(raw)
