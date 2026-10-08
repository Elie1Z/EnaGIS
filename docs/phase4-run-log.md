# Phase 4 v1.1 conditional run log

Date: 8 October 2026. Baseline implementation commit: `de21725`.
Remote configured: `origin`, `https://github.com/Elie1Z/EnaGIS.git`.

## Authority and sequence

The user conditionally authorizes v1.1 amendments, a counts-only gate, frozen-values check,
tests/lint, approval recording, committed/pushed registration and evaluation. Ask only at a STOP.
The exact approval sentence is reserved for Step 5 after the required conditions pass:

> I, Elie (Mugisha Elie), approve phase4-canada-v1.1 as amended, on 8 October 2026, conditional on the Step 2 gate passing and the Step 3 check passing.

Original v1 config is preserved. No new sources, Manitoba evaluation or relaxed gates are allowed.
Step 2 must not fit, score, open CGC outcomes or calculate an evaluation metric. A failed primary
gate stops subsequent steps. Any frozen-value change, test/lint failure, remote/push failure or
post-registration error stops this run.

## Step 1 — amendments before registration

- Added `log_ccs_area` to feature allowlist, base/full models and an area-only comparison arm.
  It is natural log of area in square metres, EPSG:3347; it is not logged a second time.
- Added proxy-specific failed-rule interpretation, limited CAR-bootstrap power and census-like
  AAFC registry documentation-bias limitation. Crop raster is possible future v2 only, not acquired.
- Declared nonproduction descriptive sensitivity features and availability cohort; primary rule
  and all v1 numerical thresholds/hyperparameters remain fixed.
- Added remotely pushed commit/tag requirement and remote publication fields to registration.
  No real registration has occurred at this stage; approval fields remain null.

## Assumptions and ordering resolutions

1. Step 1(d) requests a descriptive sensitivity **cohort**, not another fitted model. Therefore
   this run reports its availability counts/exclusions without introducing another inferential
   rule or model. Its features are population, road/junction density and log CCS area.
2. Sensitivity drops catchment/snap requirements because these belong to dropped production
   features. It retains population, geometry and label checks. Counts by reason can overlap.
3. `unresolved_match` is missing unit-level label/CAR identity. Known coordinate conflicts retain
   `spatial_review`; unlocated facilities are not assigned invented unit-level exclusions.
4. Counts-only topology preparation is explicitly authorized before approval recording. It
   computes connectivity/snap/missingness flags, skips road-density/junction covariate values,
   and never sums production, ranks a baseline, fits, reads CGC outcomes or computes skill.
5. Step 1(e) requires pushed references before registration succeeds, while Step 6 names register
   before push. `register-experiment --publish` pushes branch/tag within the command and verifies
   both before writing registration. Failure leaves no accepted registration and is a STOP.

## Step 2 — PASS: counts-only diagnostic

Amended config remains draft until all prerequisite gates pass. Diagnostic recorded in
`docs/audits/phase4-v1.1-cohorts.json`; only existing pinned source inputs were used.

| Cohort | Complete CCS | Positive CCS | Positive CARs | Excluded CCS |
|---|---:|---:|---:|---:|
| Primary | 155 | 60 | 7 | 214 |
| Descriptive nonproduction sensitivity | 360 | 130 | 14 | 9 |

Primary exclusion reasons (overlapping): population unknown 7; production unknown 212;
snap failure 9; spatial-review 2; unresolved unit-level match 0.
Sensitivity: population unknown 7; production unknown 0; snap failure 0; spatial-review 2;
unresolved unit-level match 0. No scores, fits, CGC outcome-file reads or evaluation metrics.
Primary gate passed exactly at 60 positives with seven positive CARs; thresholds were unchanged.

Before Step 4, completed mechanical line wrapping/import ordering and retained v1 nonnegativity
validation for original features; only log-area can be negative. No scientific method changed.

## Step 3 — frozen-values check tooling correction

The first check decoded Git's UTF-8 document output using Windows' default encoding and failed
to match the multiplication symbol in the original budget text. Numeric frozen-value comparisons
had passed; no differing method value was found. Added explicit UTF-8 decoding to the check
script and reran it before registration. This is a tooling correction, not a method change;
the user's Step 3 STOP applies to differing frozen values, and the post-registration error STOP
does not apply because no registration exists. If the corrected check finds a difference, stop.

The corrected script passed: primary metric/budget, secondary fraction, 2,000 draws, seed
20261008, keep rule, 60/6 gate, 15-group minimum, leave-one-CAR-out design and logistic
hyperparameters match committed v1 (`de21725`). Metric implementation is identical to v1.
The user subsequently instructed "now we continue"; the conditional guards remain in force.

## Step 4 — STOP: lint and test failures

The user instructed stopping if anything fails. Commands were launched concurrently; collected
results from those already running and did not repair or rerun them.

- Ruff format check: PASS (72 files).
- Ruff lint: FAIL, two E501 lines of 102 characters: `experiment_cohort.py:117` and `siting.py:117`.
- Pytest: 126 PASS, one FAIL. The offline end-to-end synthetic registration test encountered
  `git ls-remote` exit 128 for its temporary local bare remote before the expected unpublished-ref
  refusal. The cause has not been assumed or repaired. No real remote push was attempted.

STOP applied before Steps 5–7. Real approval fields remain null; no production registration,
commit/tag/push, outcome evaluation or scientific metric exists for v1.1. The amended source
files remain uncommitted. Synthetic tests use temporary fixture data/repositories; their older
Phase 2/3 fixture includes synthetic Manitoba records, not real transfer data or evaluation.
No new data source or crop raster was acquired. No thresholds, folds, seeds or method were relaxed.

Continuation requires user direction at this STOP condition. Proposed next action, not applied:
fix only the two formatting lines and investigate/correct the temporary-remote test/registration
implementation issue, preserving all scientific settings; then rerun Step 4 and proceed only
after all checks pass. The Step 2 primary gate and corrected Step 3 check had passed.

## Authorized resumption after Step 4 STOP

The user explicitly delegated completion and authorized correction of the implementation issues.
The two lint lines were wrapped without changing their strings. A direct reproduction of the
temporary-remote failure showed Git's MSYS shell failing to create a Windows named object with
access denied (`NtCreateDirectoryObject`, 0xC0000022) inside the sandbox. This is an execution
permission failure, not evidence of a changed scientific method or failed remote-ref guard.
The suite will be rerun with the necessary execution permission; no guard is bypassed in code.

Resumed checks: **127 tests PASS**, Ruff lint PASS, Ruff format PASS (72 files), frozen-values
script PASS. No scientific setting changed during remediation. The real GitHub remote is
reachable and currently returns no HEAD/main refs (new empty repository).

## Step 5 — approval recorded

After Steps 2–4 passed, recorded `approved_by: Elie (Mugisha Elie)`, date `2026-10-08`, and exactly:

> I, Elie (Mugisha Elie), approve phase4-canada-v1.1 as amended, on 8 October 2026, conditional on the Step 2 gate passing and the Step 3 check passing.

The Step 2 audit retains its original draft-config hash as evidence of its timing. Preparation
is rebuilt with the approved config/code before registration; approval metadata changes no
features or cohort rules. The original v1 config remains unchanged. A new real v1.1 preparation
directory preserves the previous v1 artifacts.

## Step 6 — registration pending

The approved method, counts audit, frozen check and implementation will be committed before
`register-experiment --publish` atomically pushes the commit/tag and verifies their remote hashes.

Step 6 completed successfully. Registration commit:
`948cf2fddbb5a9f093883dd06b1a58a1d5a905fe`; tag: `preregister-phase4-canada-v1.1`;
remote: `https://github.com/Elie1Z/EnaGIS.git`. Both `refs/heads/main` and the tag were independently
confirmed by `git ls-remote` at that exact commit before evaluation. Registration is saved in
`data/manual/phase4-preregistration.json`, including remote URL/commit and all pinned hashes.
The registration command succeeded; no push failure occurred. No scientific code, configuration,
protocol, folds, thresholds, seeds, features or keep/kill rule will change after this registration.

## Step 7 — evaluation running

Started the real `evaluate-experiment --preparation data/processed/phase4-v1.1` command after
remote verification. It verified the registered hashes before building AB/SK topology/features.
No new source was acquired and Manitoba is excluded from the real development evaluation.

An optional GitHub Actions status lookup was unavailable because GitHub CLI is not authenticated.
This did not concern a required execution gate: Git push and independent remote-ref verification
had already succeeded, and the local full suite passed. No CI-success claim is made from this
lookup, no credentials were changed, and no registered method was altered. The evaluation command
continues unchanged. Documentation updates after registration describe execution only; the hashed
protocol/config/code remain frozen.

## Step 7 — COMPLETE: evaluation and verification passed

Real evaluation exited 0: `siting_status: evaluated`,
`siting_decision: kill_or_no_demonstrated_improvement`, `hindcast_status: evaluated_diagnostic`.
Independent `verify-experiment outputs/phase4` exited 0 and verified six artifacts for run
`phase4:ccb98f6b1f4f:050f5cff43a9`. No evaluation/verification error occurred after registration.

The primary cohort equals the counts-only cohort: 155 CCS, 60 positives, seven positive CARs.
Full-model top-20% recall: 0.35714285714285715; B0: 0.3976190476190476. Full-minus-best-baseline
margin: −0.04047619047619044, 95% interval [−0.39285714285714285, −0.0071428571428571175].
Verdict KILL: **no demonstrated improvement from this proxy-based accessible-production feature**,
not evidence against road-catchment logic. Few-block intervals/counts are descriptive.

Hindcast: 52 common groups from 138 points in seven CARs; 86 excluded. Phase 3 Spearman
0.7728304762796138, interval [0.2816421189908316, 0.8214157875066804]. Absolute-volume accuracy
remains unvalidated. Sensitivity remains descriptive: 360 CCS, 130 positives, 14 positive CARs.

Created completion report, final machine audit and six verified local outputs. Updated status
and reproduction guide. A reporting-only patch was rejected because it specified both deletion
and addition of the same status-document path in one patch; it was reapplied as an in-place
documentation update. No registered code, protocol, config, source or output was affected.
Reporting changes and registration record are saved separately from the frozen method commit.

Final check: `git diff` against the registration commit for `src/enagis`, experiment configs,
the frozen protocol, `pyproject.toml` and `uv.lock` is empty. `git diff --check` passes. Only
registration/result records and explanatory documentation are included in the completion commit.
