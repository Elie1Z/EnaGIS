# Phase 7 — prospective freeze and verification workflow

The toolkit implements the PRD §9 and the supplied Phase 7 guide. It is usable with explicit
synthetic fixtures. Real `ranking-v1` requires the Phase 6 scientific exit, a human-approved
protocol, a committed verification participant, and a reviewed baseline/flag frame.
The [review proposal](../../configs/verification/phase7-canada-v1.review.json) records exact
proposed policy choices and unresolved outcome definitions; it cannot be executed.

## Artifacts and direction of data

`python -m enagis.verification` provides `prepare`, `seal`, `verify`, `init-records`, and `analyze`.
The freeze code accepts no verification outcomes. Analysis only reads the frozen package and
private records, and writes a separate aggregate report. Existing packages, receipts, capture
files and report directories are never overwritten by these commands.

Preparation fully replays a Phase 6 run under its recorded code and lockfile. It copies all
nine source files unchanged, including the original shortlist, full ranking, input/config,
per-draw traces and source index. It adds the approved protocol, baseline/flag frame,
prospectively selected sample, scientific exit/review and capture JSON Schema. The manifest
hashes every artifact and records run/code/lockfile, shortlist, sample and protocol hashes.

A prepared package is **unsealed**. Commit its exact files with the source and `uv.lock`, create
an annotated tag, and push that tag and its commit. `seal` checks the local Git object and the
remote annotated-tag object plus peeled commit. It refuses absent, lightweight, unpublished,
repointed or incompatible tags and emits a separate receipt only after the checks pass.
No command automatically creates, moves or force-pushes a ranking tag.

Tag validation compares every package file and Python source file against committed Git blobs,
and verifies the complete file sets and lockfile. Rehashing edited files does not bypass replay
or their Git binding. Offline verification checks against the existing seal and local tagged
objects. `--check-remote` additionally checks the current remote. Remote access is only needed
for sealing and the explicit remote audit; calculation and analysis run offline.

The freeze time is the annotated tag's recorded timestamp. Analysis rejects observations dated
before it. This is an audit of declared chronology and artifact integrity, not an independent
timestamp service or proof that human testimony is authentic. A human must maintain prospective
collection discipline. Freeze `ranking-v1` before any verification observations are collected.

## Real scientific exit and baseline frame

`ScientificExit` requires approval of parameters/sources, units/conservation/coverage, the real
comparison and ablations, tests/lint/format, and readiness to freeze. It binds the exact source
index and code hash and a hashed review report. This is a separate approved artifact; it does
not edit the Phase 6 run's conservative `scientifically_ready_to_freeze: false` metadata.
No actual exit approval has been created. The JSON Schema for this contract is available from
`enagis.verification.contracts.ScientificExit.model_json_schema()`.

`Frame` binds the source index. Each required baseline (B0/B1/B2/population/expert) contains a
unique ordered list covering exactly the primary eligible candidate cohort, an evidence
reference, and no unavailable reason; alternatively it has an empty list and an explicit reason.
Unavailable comparisons are reported, never scored as zero or fabricated. Source and human
review must support the orders; this module does not fit or choose baselines using outcomes.
Flags require candidate IDs, type and evidence references. Flags cannot silently add a node
outside the frozen source frame. Unranked source candidates may enter a declared flag supplement.

## Sampling and interpretation

The proposal samples the full top ten, three middle and three lower candidates, followed by up
to two unused disagreement cases and two unused siting flags. The latter pools may overlap;
selection deduplicates globally and records each stage's eligible pool and shortfall.
The middle band is the first ceiling half of ordered ranks after the top ten; the lower band is
the rest. Ranking input order cannot affect the sample. Hash-based seeded priority selects
within each non-census pool, with node ID as a deterministic collision tie-break.

Core quota shortages stop preparation; supplement shortages remain explicit. A sample below
the approved minimum also stops. No replacement is made for nonresponse after freezing.
Conditional selection fractions are recorded for audit, but are not marginal survey weights.
No overall population precision is calculated by pooling rank strata and targeted supplements.
The proposed minimum is twelve both for planned sample size and resolved verification count;
partial results remain reportable with an insufficient-verification status.

All these choices are versioned and require approval before real use. Synthetic settings are
separate (seed 23, ten/one/one core quotas) and do not approve the proposed real design.

## Capture, consent and failure modes

After sealing, `init-records` creates one blank row per sampled node: not contacted, consent
not requested and all factual checks null. This is a form, not a contact response. Real records
must reside under Git-ignored `data/validation_private/`. Contact/evidence/assessor records stay
private; public reports are built from a fixed whitelist of counts and metrics, without names,
node-level outcomes, free text or private references. Participant commitments use opaque
`private:...` identifiers in the public protocol.

Every attempted contact needs an aware timestamp and a method allowed by the frozen protocol.
Completed observations require consent plus private assessor/evidence references. Declined,
unreachable and unattempted rows cannot contain factual observations. Duplicate nodes,
out-of-sample identities, wrong freeze IDs/hashes, mixed synthetic/real data, and observations
before the seal fail validation. Real observations dated in the future also fail validation.
Supply one adjudicated row per node; retain raw attempts and
supporting evidence privately rather than counting repeated contacts as independent sites.

Primary failure precedence is node absent, undocumented supply, negligible requirement, then
seasonal irrelevance. A preceding unknown keeps the primary outcome unknown. Confirmation
requires all four checks resolved in the favorable direction. Multiple observed failure flags
are counted separately and may overlap. The precise evidence criteria and service/season
thresholds remain human-owned; the toolkit never derives them from a missing answer.

Verification dated in 2026 does not automatically validate the 2024 production/equipment state.
The protocol must declare the observation period and what historical comparison it supports.
Current conditions may instead support present-day follow-up screening, with that limit stated.

## Analysis

For the primary and each available baseline top ten, report the full target size, sampled size,
attempted/consenting/resolved counts, all outcomes, confirmed fraction among resolved cases and
a Wilson interval. Exact precision@10 remains null until all ten outcomes are resolved. Bounds
`[confirmed/10, (confirmed + unresolved)/10]` retain unanswered and unsampled targets as unknown;
these bounds are not confidence intervals. Rank strata have separate sample summaries.

The interval uses pinned SciPy's
[Wilson method without continuity correction](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html).
The confidence level is explicit in the protocol. It describes binomial working-model
uncertainty among resolved observations and does not cover nonresponse bias or spatial
dependence. No calibrated viability, recall or geographic transfer metric is inferred.

Available arms become comparable only when the union of their frozen top-ten sets has complete
resolved observations. Otherwise analysis labels the comparison not testable on common outcomes.
The proposed sample may not cover that union, so a comparison can legitimately remain unavailable.
Approving a different prospective sampling design requires a new protocol before outcomes.
No baseline winner or component-retention decision is inferred automatically.

## Rehearsal and later real commands

```sh
python scripts/phase7_rehearsal.py --output outputs/phase7-rehearsal
```

Use a new output directory. The rehearsal creates its own isolated repository and local bare
remote under that directory, copies current source, reruns the invented Phase 6 fixture, and
seals **fixture-ranking-v1**. It then supplies twelve visibly synthetic rows covering successes,
failures and missingness, analyzes them and rechecks all frozen bytes. This does not create the
real `ranking-v1` tag, publish a sample, or contact anyone. Tests use the same isolated workflow.

Once the actual exit, protocol and frame have been reviewed, the real sequence is:

```sh
python -m enagis.verification prepare --source outputs/phase6-reviewed --protocol configs/verification/phase7-canada-v1.json --frame configs/verification/phase7-frame-v1.json --scientific-exit docs/reviews/phase6-exit-v1.json --output freezes/ranking-v1
# Commit source, lockfile, approved inputs and the entire prepared freeze package first.
git tag -a ranking-v1 -m "Prospective EnaGIS ranking and verification sample v1"
git push origin HEAD refs/tags/ranking-v1
python -m enagis.verification seal --bundle freezes/ranking-v1 --output outputs/phase7-seal.json
python -m enagis.verification verify --bundle freezes/ranking-v1 --receipt outputs/phase7-seal.json --check-remote
python -m enagis.verification init-records --bundle freezes/ranking-v1 --receipt outputs/phase7-seal.json --output data/validation_private/phase7/records.json
# Only after real, consented observations have been recorded:
python -m enagis.verification analyze --bundle freezes/ranking-v1 --receipt outputs/phase7-seal.json --records data/validation_private/phase7/records.json --output outputs/phase7-analysis-v1
```

These are future paths, not existing approved artifacts. Use the matching source checkout for
replay and analysis. A new method or post-verification ranking must use a separate version and
report its use of previously observed outcomes. Do not move the original tag or overwrite it.
