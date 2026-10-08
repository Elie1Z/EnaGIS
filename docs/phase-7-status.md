# Phase 7 — toolkit verified; real ranking freeze pending

Date: 8 October 2026. The ranking-freeze and verification toolkit is implemented and tested.
**Phase 7's real scientific exit has not been reached:** no real `ranking-v1` or verification
sample has been frozen. The unresolved Phase 6 evidence/review and human verification decisions
still apply. Engineering work can proceed while those gates remain open.

## Delivered

- `enagis.verification`: full source replay, immutable package preparation, seeded stratified
  sampling, exact Git/tag/remote checks, private capture initialization and aggregate analysis.
- The package includes the original ranking/shortlist, protocol, baseline/flag frame, sample,
  scientific exit evidence, capture JSON Schema and checksummed manifest. Preparation is
  explicitly unsealed until the annotated tag and commit are verified on its configured remote.
- Validators reject wrong freeze identities, duplicate/out-of-sample records, mixed real and
  synthetic records, inconsistent consent/outcomes, backdated observations and future real dates.
- Analysis reports incomplete targets and bounds, descriptive Wilson intervals and failure
  counts. It does not manufacture precision@10 from partial responses or compare baseline arms
  without complete common outcomes. Private references and individual responses are not exported.
- A [concrete proposed protocol](../configs/verification/phase7-canada-v1.review.json),
  [private field-form guide](phase7-field-form.md), [execution guide](spec/phase7-verification.md)
  and [decision record](decisions/0010-prospective-verification.md).

## Verification evidence

**218 tests passed**, including 27 Phase 7 cases. Ruff lint/format checks passed. The original
eight smoke cases and historical Phase 3 (ten artifacts), Phase 4 (six) and demo (32) verified.
No existing experiment was refitted, and the public demo was not replaced with synthetic data.

The saved rehearsal is `outputs/phase7-rehearsal/`. It creates an isolated repository and local
bare remote, using the reserved synthetic tag `fixture-ranking-v1`. Its freeze identifier is
`fixture:freeze:7155404ff347f0c7adc18512`. The new Phase 6 fixture run under the current source is
`phase6:55b909c51f1e3a461e8d0306`; all source artifacts replay before the freeze is constructed.

The sample contains twelve invented nodes (ten top-ranked, one middle, one lower). Both empty
supplement pools are reported. Twelve invented capture rows exercise all outcome types; eight
are resolved. The top ten have four confirmations, four failures and two unresolved outcomes.
The report correctly leaves precision@10 null, reports confirmation bounds 0.4–0.6, and labels
the 4/8 resolved fraction's Wilson interval (~0.215–0.785) descriptively. **These are software
test values, with zero real contacts or validation observations.**

Tests establish that even an internally consistent rewritten protocol/sample with fresh local
hashes fails the immutable Git binding. The original package is unchanged after analysis.
Missing remote/tag, false seal time, repeated outputs and attempts to place observations in
public/frozen paths are rejected. The proposed real protocol stops before source reading and
creates no output. The [machine audit](audits/phase7-engineering.json) records hashes and checks.

## Phase 7 exit checklist

| Required exit | Current evidence |
|---|---|
| Approved real ranking frozen and identifiable | Pending Phase 6 scientific exit; synthetic rehearsal only |
| Real shortlist hash/version and tag recorded | Tooling verified; real tag not created |
| Human-approved sample frozen before outcomes | Proposed design exists; real approval and participant pending |
| Verification schema and standard form | Implemented; generated schema included in every package |
| Analysis accepts verified real records | Typed real-record path implemented; end-to-end test uses invented records |
| Verification cannot silently rewrite original ranking | Downstream-only interfaces, full replay and immutable Git checks tested |

## What is still required

The [Phase 6 desk review](phase6-desk-review.md) identifies missing applicable inventory, fan-duty
and freight evidence. Resolve those and approve an actual scientific configuration; run it and
review its prospectively specified comparisons/ablations. Bind that sign-off to the exact run.

For verification, approve the proposed sample/seed/interval/consent policy, define the meaningful
failure criteria and time basis, provide a committed participant through a private reference,
and review the baseline/flag frame. AGENTS.md and PRD §9/§11 require these substantive human
decisions. Moving to Phase 7 does not itself supply them. No external-consultant requirement is
added, and no outreach has been performed.

Then prepare, commit, tag and seal the real package **before** collecting observations. This
workflow preserves the global direction: the verification module uses generic IDs and explicit
protocol settings. A real new geography still needs local adapters/evidence and a separate
untouched evaluation; a data-poor location can legitimately have no defensible numeric ranking.

## Deviations and reproducibility

- Implemented Phase 7 engineering before Phase 6 scientific closure under the user's request;
  the real freeze gate remains enforced. No phase is falsely marked scientifically complete.
- The proposed real sample has a 16-node core and at most four supplements; its choices remain
  unapproved. Synthetic quotas/seed differ and are visibly labelled. No gate was relaxed.
- Git-declared timestamps and human-reported observation dates support an audit trail; they
  are not independently trusted timestamps or proof of truthful testimony.
- Adding modules changes the package-wide code hash. Earlier runs retain their historic source
  commits; new replay uses the matching current source. No old run or audit was overwritten.
- Full tests and the rehearsal use the existing Windows Git-fixture permission. All Git writes
  in the rehearsal target its isolated local repository/remote; no real ranking tag is published.
