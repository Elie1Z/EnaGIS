"""Explicit protocol choices and private observations; no implicit scientific approval."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, Field, model_validator

from enagis.contracts import ID, Contract, Hash, Text
from enagis.science.contracts import Approval

Purpose = Literal["synthetic_fixture", "scientific_reviewed"]
Stratum = Literal["top", "middle", "lower", "disagreement", "siting_flagged"]
STRATA = ("top", "middle", "lower", "disagreement", "siting_flagged")
FAILURES = ("node_absent", "undocumented_supply", "requirement_negligible", "seasonal_irrelevance")
Outcome = Literal[
    "node_absent",
    "undocumented_supply",
    "requirement_negligible",
    "seasonal_irrelevance",
    "confirmed",
    "unknown",
    "unreachable",
    "declined",
    "not_contacted",
]


class Protocol(Contract):
    schema_version: Literal["phase7-protocol-v1"]
    protocol_id: ID
    purpose: Purpose
    freeze_tag: str = Field(pattern=r"^(fixture-)?ranking-v[1-9][0-9]*$")
    seed: int = Field(ge=0)
    top_k: Literal[10]
    sample_counts: dict[
        Stratum, int
    ]  # Exact quotas; empty core pools stop, supplements report shortages.
    minimum_sample: int = Field(ge=1)
    middle_band: Literal["first_ceiling_half_after_top_k"]
    selection_method: Literal["sha256_seed_stratum_node_id"]
    supplement_order: Literal["disagreement_then_siting_flagged"]
    replacements: Literal["none_after_freeze"]
    confidence_level: float = Field(gt=0, lt=1)
    interval_method: Literal["wilson_without_continuity_correction"]
    unresolved_policy: Literal["report_bounds_and_resolved_denominator"]
    failure_precedence: list[ID]
    criteria: dict[ID, Text]
    temporal_interpretation: Text
    consent_text: Text
    allowed_methods: list[Literal["phone", "site_visit", "authority_record", "synthetic"]]
    required_baseline_arms: list[ID]
    approval: Approval | None
    participant_commitment_ref: str | None = Field(pattern=r"^private:[A-Za-z0-9:_-]+$")

    @model_validator(mode="after")
    def consistency(self):
        if set(self.sample_counts) != set(STRATA) or any(
            v < 0 for v in self.sample_counts.values()
        ):
            raise ValueError("all five nonnegative sample quotas must be explicit")
        if self.sample_counts["top"] != self.top_k:
            raise ValueError("the full top ten must be sampled")
        if not self.sample_counts["middle"] or not self.sample_counts["lower"]:
            raise ValueError("middle and lower rank strata must both be sampled")
        if self.failure_precedence != list(FAILURES):
            raise ValueError("explicit supported failure precedence required")
        if set(self.criteria) != {*FAILURES, "confirmed"}:
            raise ValueError("every failure and confirmed-candidate criterion is required")
        if not self.allowed_methods or len(set(self.allowed_methods)) != len(self.allowed_methods):
            raise ValueError("unique permitted observation methods required")
        if len(set(self.required_baseline_arms)) != len(self.required_baseline_arms):
            raise ValueError("duplicate baseline arm")
        if "enagis" in self.required_baseline_arms:
            raise ValueError("enagis is the primary arm, not a baseline")
        return self

    def authorize(self, allow_fixture=False):
        if self.purpose == "synthetic_fixture":
            if not allow_fixture or not self.protocol_id.startswith("fixture:"):
                raise ValueError(
                    "synthetic protocol requires explicit fixture permission and identity"
                )
            if not self.freeze_tag.startswith("fixture-") or self.approval is not None:
                raise ValueError("fixture cannot reserve ranking-v1 or claim human approval")
            if self.allowed_methods != ["synthetic"]:
                raise ValueError("fixture observations must be labelled synthetic")
        else:
            if self.freeze_tag.startswith("fixture-") or "synthetic" in self.allowed_methods:
                raise ValueError("real protocol cannot use fixture tag or methods")
            if not self.approval or not self.participant_commitment_ref:
                raise ValueError(
                    "human-approved protocol and committed verification participant required"
                )
            if self.minimum_sample < 12:
                raise ValueError("real verification retains the PRD minimum of twelve")
            if set(self.required_baseline_arms) != {"B0", "B1", "B2", "population", "expert"}:
                raise ValueError("all PRD baselines must be supplied or explicitly unavailable")


class Baseline(Contract):
    arm_id: ID
    ordered_node_ids: list[ID]
    evidence_ref: Text
    unavailable_reason: Text | None

    @model_validator(mode="after")
    def availability(self):
        if bool(self.ordered_node_ids) == bool(self.unavailable_reason):
            raise ValueError("baseline must have a ranking or an explicit unavailability reason")
        if len(set(self.ordered_node_ids)) != len(self.ordered_node_ids):
            raise ValueError("duplicate baseline node")
        return self


class Flag(Contract):
    node_id: ID
    kind: Literal["disagreement", "siting_flagged"]
    evidence_ref: Text


class Frame(Contract):
    schema_version: Literal["phase7-frame-v1"]
    purpose: Purpose
    source_index_sha256: Hash
    baselines: list[Baseline]
    flags: list[Flag]
    approval: Approval | None


class ScientificExit(Contract):
    schema_version: Literal["phase6-exit-v1"]
    purpose: Literal["scientific_reviewed"]
    source_index_sha256: Hash
    source_code_sha256: Hash
    parameter_and_source_review_passed: Literal[True]
    units_conservation_and_coverage_passed: Literal[True]
    real_comparison_and_ablations_reviewed: Literal[True]
    scientifically_ready_to_freeze: Literal[True]
    tests_lint_and_format_passed: Literal[True]
    review_report_path: Text
    review_report_sha256: Hash
    approval: Approval


class Observation(Contract):
    """Private adjudicated observation; identifiers and prose never enter aggregate reports."""

    node_id: ID
    observed_at: AwareDatetime | None
    method: Literal["phone", "site_visit", "authority_record", "synthetic"] | None
    contact_status: Literal["not_contacted", "completed", "unreachable", "declined"]
    consent: Literal["not_requested", "granted", "declined"]
    node_exists: bool | None
    undocumented_supply: bool | None
    requirement_negligible: bool | None
    seasonal_irrelevance: bool | None
    outcome: Outcome
    evidence_private_ref: Text | None
    assessor_private_ref: Text | None

    def failure_flags(self):
        return {
            "node_absent": None if self.node_exists is None else not self.node_exists,
            "undocumented_supply": self.undocumented_supply,
            "requirement_negligible": self.requirement_negligible,
            "seasonal_irrelevance": self.seasonal_irrelevance,
        }

    @model_validator(mode="after")
    def coherent(self):
        flags = self.failure_flags()
        if self.contact_status != "completed":
            if any(v is not None for v in flags.values()):
                raise ValueError("non-completed contact cannot contain factual observations")
            if self.outcome != self.contact_status:
                raise ValueError("contact status and outcome disagree")
            expected = "declined" if self.contact_status == "declined" else "not_requested"
            if self.consent != expected:
                raise ValueError("non-completed contact has inconsistent consent")
        else:
            if (
                self.consent != "granted"
                or not self.evidence_private_ref
                or not self.assessor_private_ref
            ):
                raise ValueError(
                    "completed observation requires consent and private evidence/assessor refs"
                )
            # An earlier unknown blocks a later primary failure classification.
            expected = "confirmed"
            for failure in FAILURES:
                if flags[failure] is None:
                    expected = "unknown"
                    break
                if flags[failure]:
                    expected = failure
                    break
            if self.outcome != expected:
                raise ValueError("outcome disagrees with ordered factual checks")
        if self.contact_status == "not_contacted":
            if self.observed_at is not None or self.method is not None:
                raise ValueError("unattempted contact cannot have observation time or method")
        elif self.observed_at is None or self.method is None:
            raise ValueError("contact attempt requires time and method")
        return self


class Records(Contract):
    schema_version: Literal["phase7-records-v1"]
    purpose: Purpose
    freeze_id: ID
    frozen_manifest_sha256: Hash
    records: list[Observation]

    def validate_against(self, sample, protocol, sealed_at: datetime):
        ids = [r.node_id for r in self.records]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate verification record; provide one adjudicated row per node")
        if set(ids) - {r["node_id"] for r in sample["rows"]}:
            raise ValueError("verification record is outside the frozen sample")
        if self.purpose != protocol.purpose:
            raise ValueError("synthetic and real verification records cannot be mixed")
        for row in self.records:
            if row.observed_at is not None and row.observed_at < sealed_at:
                raise ValueError("observation predates the registered freeze")
            if (
                self.purpose == "scientific_reviewed"
                and row.observed_at is not None
                and row.observed_at > datetime.now(UTC)
            ):
                raise ValueError("real observation cannot be dated in the future")
            if row.method is not None and row.method not in protocol.allowed_methods:
                raise ValueError("observation method is outside the frozen protocol")
