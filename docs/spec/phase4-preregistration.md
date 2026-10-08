# Phase 4 scientific protocol — v1.1 amended before registration

**Status: APPROVED; amended before registration.** 8 October 2026.
Configuration: [`phase4-canada-v1.1.json`](../../configs/experiments/phase4-canada-v1.1.json).
The original v1 configuration is preserved unchanged as the frozen-values reference.
No real baseline scoring, model fitting, outcome comparison or Manitoba evaluation has been
performed under this protocol. Source availability counts below are preparation diagnostics.
Synthetic tests are implementation checks, not evidence of predictive performance.

## Amendments before registration and reasons

| Amendment | One-line reason |
|---|---|
| a. Add natural log CCS polygon area to base/full model and an area-only arm | Control polygon size before attributing improvement to accessible production. |
| b. Add proxy interpretation and limited-power clause | A proxy-specific test with few blocks cannot reject road-catchment logic. |
| c. State registry documentation-bias limit; raster only in possible future v2 | A registry close to a census cannot establish documentation-bias robustness. |
| d. Declare a descriptive cohort without production-dependent features | Show the coverage retained without production missingness, independently of the primary rule. |
| e. Require remotely pushed registration commit/tag and record the remote | Publish the exact method before accepting registration. |

The user's conditional instruction authorizes these amendments and the counts-only diagnostic.
The counts gate passed (155 complete CCS, 60 positives, seven positive CARs), the frozen-values
check passed, and all 127 tests plus lint/format passed. The user authorized correction and
resumption after the recorded Step 4 implementation/environment STOP.

Approval recorded verbatim:

> I, Elie (Mugisha Elie), approve phase4-canada-v1.1 as amended, on 8 October 2026, conditional on the Step 2 gate passing and the Step 3 check passing.
No new data source is acquired. The AAFC crop-inventory raster is a possible future v2 only.

## Authorized exploratory method

The conditionally authorized exploratory method uses a **coarse
uniform-area production proxy** for the first comparison because the AAFC Annual Crop Inventory
2024 raster and wheat-class audit specified in decision 0003 are not yet available in the pinned
spine. This approved exploratory amendment does not complete that raster's classification audit.
It preserves commodity, geography, service and holdout scope. The resulting model cannot resolve
actual crop locations within reporting regions. An audited crop raster is reserved for a possible
future v2, outside this run.

The road comparison uses **50 km of undirected network distance**, with at most **5 km** from a
CCS representative point to its nearest retained OSM vertex. These are proposed comparison
settings, not empirically established grain catchments or driving-time isochrones. Approval of
this experiment does not approve Phase 3 energy coefficients, field screening or worldwide
accuracy. The repository's `AGENTS.md` requires human approval of scientific assumptions; the
PRD requires the keep/kill rule to be fixed before outcomes are inspected.

## Frozen target, labels and geography

- Alberta and Saskatchewan only. Manitoba units are excluded from preparation outputs, model
  selection and outcome evaluation; only AB/SK road extracts are opened. Provincial extracts can
  contain border segments. A later transfer evaluation requires its own protocol.
- Unit: 2021 Census Consolidated Subdivision (CCS), full digital geometry, EPSG:3347 metres.
  Validation block: 2021 Census Agricultural Region (CAR), from the pinned one-parent crosswalk.
- Positive label: at least one documented AAFC 2024 primary elevator uniquely matched to a CCS.
  Any unresolved registry coordinate match affecting a CCS censors that entire CCS. Capacity,
  throughput, energy and supply are not used to choose the siting labels or features.
- Unlabeled CCS are background, **not verified absences**. Multiple elevators in one CCS are one
  positive unit. The model describes documented placement, not unmet need or true prevalence.
- Preparation audit: 369 development CCS; 132 positive CCS across 14 positive CARs; 235 unlabeled
  CCS and two spatial-review CCS. These are not a registry completeness estimate.

## Pinned inputs and population preparation

Existing Phase 2 hashes identify 2024 non-durum wheat production (all wheat minus durum), SADR,
CCS and CAR boundaries/crosswalks, AAFC registry and January 2024 OSM roads. Registry evidence is
loaded separately from feature inputs. Input allowlists prevent discovery of downstream outputs.

[`phase4-manifest.json`](../data/phase4-manifest.json) pins two additional official sources:

1. [Statistics Canada table 98-10-0002-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=9810000201),
   2021 CSD population, downloaded 8 October 2026 (Statistics Canada Open Licence).
2. [Statistics Canada 2021 digital CSD boundaries, layer 9](https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Digital_boundary_files/MapServer/9),
   the complete AB/SK query, EPSG:3347 (Open Government Licence – Canada).

Sum CSD counts within CCS only after unique representative-point matching and checking full
polygon containment. One square metre is a coordinate arithmetic tolerance, not a population
allocation tolerance. Repair invalid polygons explicitly and record the repair. Ambiguous
containment censors all candidate CCS; a missing component makes the entire CCS total UNKNOWN.
Repeated `Symbols` headers in the published CSV are read by column position, preserving the
population flag rather than a different measure's flag. No area-weighted people are invented.

Observed preparation: 1,374 CSD records and geometry IDs agree; all match uniquely, with full
containment within numerical tolerance. Nine CSD population observations are missing; 362 CCS
totals are known and seven UNKNOWN. Population is from 2021, not contemporaneous 2024 population.
The initially considered GeoSuite download returned HTTP 403; this protocol uses the accessible
official table and full digital geometry sources above.

## Label-free features and baseline definitions

Let P(r) be reported non-durum tonnes for SADR r and A(r) its full polygon area. Define a CCS mass
proxy M(u) = sum over r of P(r) × area(u intersect r) / A(r). Use the positive-area Phase 2
crosswalk, including small slivers. An unknown contributing region makes the result UNKNOWN.
Audit represented and outside-CCS mass separately; never renormalize uncovered production away.
This geometric proxy is ESTIMATED, not observed field production.

| Arm or feature | Definition | Unit |
|---|---|---|
| B0 / production context | Area-weighted mean of contributing SADR **total** production | source-region tonnes context; not CCS tonnes |
| B1 / Euclidean production | Sum M(u) at CCS representative points within 50 km | proxy tonnes |
| B2 / accessible production | Sum M(u) within the approved road-distance budget, including both point connectors | proxy tonnes |
| Population | Audited CSD-to-CCS sum | people |
| Road density | Retained OSM line length clipped to the CCS divided by polygon area | km/km² |
| Junction density | Retained graph vertices with at least three distinct neighbors in the CCS | junctions/km² |
| Nearest presence | Negative Euclidean distance to nearest **training-block** positive CCS point | metres |
| Area-only / log CCS area | Natural log of full CCS polygon area measured in EPSG:3347 | log(area / 1 m²), dimensionless |

The production buffers are overlapping context comparisons, not competing facility allocations.
They do not conserve mass across different target buffers; only the underlying M(u) crosswalk
has a mass-accounting audit. Computation covers the development footprint only. Contributions
outside it are outside the estimand, not proof that crops do not exist there.

Road classes: motorway, trunk, primary, secondary, tertiary and their `_link` classes;
unclassified, residential, service and track. Exclude explicit access `no` and `private`.
Join shared OSM node IDs, check coordinate consistency, deduplicate identical provincial ways,
and reject conflicting duplicates. Repeated graph edges use the minimum length, never the sum.
Use projected segment lengths and an undirected graph. Missing access tags are not evidence of
legal access. There are no claims about speeds, one-way rules, turns, vehicle suitability or
seasonal passability. A point beyond the snap tolerance has UNKNOWN accessibility. If an
unsnapped source point is within a target's Euclidean radius, that target's B2 is also UNKNOWN:
potentially reachable mass must not silently disappear. A valid point includes its own M(u).
Unknown production in either catchment propagates to an UNKNOWN catchment score.

Feature values retain evidence labels, sources, vintages and licences. Population/boundary
licences remain in the source manifest; road-derived outputs retain ODbL and OpenStreetMap
attribution. No licensed private verification observations enter public outputs.

## Models, common cohort and spatial validation

The base model uses production context, population, road density, junction density and natural
log CCS polygon area (square metres, EPSG:3347). The full
model adds accessible production. No other feature or model family is selected after results.
Compare full model against B0, B1, B2, population, nearest training presence, base model and
area-only. Area enters both models as log(area), standardized within each training fold; it is
not subjected to log(1+x) a second time. Other feature preprocessing is unchanged from v1.

**Descriptive sensitivity cohort:** require population, road density, junction density and
log CCS area, with the same geometry/label review rules. Drop all production-dependent features,
their production-completeness tests and catchment-snap requirements. Road density and junction
density do not require a snapped representative point. Report complete CCS, positive CCS and
positive CAR counts, excluded-unit lists and reason counts. This is a descriptive availability
sensitivity only: no second fitted model or keep/kill decision is introduced, and it cannot
override the primary rule. Exclusion counts overlap when a CCS has multiple reasons.
`unresolved_match` means a missing unit-level label or CAR identity; it does not invent a CCS
for unlocated registry records. `spatial_review` retains the existing coordinate-conflict censor.

The primary and sensitivity counts are computed before any model fit, baseline score, CGC outcome
file access or evaluation metric. Topology, point snapping and boolean catchment membership may
be prepared solely to identify missing source coverage; production quantities are not summed.
Continue only if the primary has at least 60 positive CCS and six positive CARs. Otherwise stop
and present options without applying any. No threshold or method is adjusted to recover the gate.

Every arm uses the same complete CCS cohort: all required model/baseline values known and no
spatial-review label. Report each excluded unit and reason. Available production and population
give an **upper bound** of 197 complete units, 74 positive units across eight positive CARs.
Network/catchment completeness can reduce this further. Require **at least 60 positive CCS and
six positive CARs** after all exclusions. Counting positive CCS rather than duplicate facilities
is conservative. If either gate fails, report `feasibility_failed / not_testable`, with no fitting
or relaxed thresholds. A future data improvement needs a separately versioned protocol.

Use leave-one-CAR-out CV. In each fold, transform the original nonnegative features with log(1+x),
retain the separately computed log-area feature, then fit
standardization using all training CCS only. Fit regularized logistic regression on documented
training presences as class 1 and all training CCS (including those presences) as background
class 0. Use balanced class weights, L2 regularization, C=1, lbfgs, tolerance 1e-8 and at most
2,000 iterations. Nonconvergence is an error, not a result. No tuning against held-out blocks.
Record training block IDs, feature order, scaler parameters, coefficients and iteration count.
Decision-function scores are relative discrimination scores, not calibrated probabilities.

The presence/background distinction follows the limitation described by
[Fithian and Hastie](https://pmc.ncbi.nlm.nih.gov/articles/PMC4258396/); this finite balanced logistic
implementation is not claimed to be an exact point-process likelihood. Fold preprocessing follows
the [scikit-learn leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).

## Metrics and preregistered decision

- Primary: equal-weight mean CAR recall among the top **20%** of each held-out block's eligible
  units. Budget is ceil(fraction × block size); ties use ascending stable CCS ID. A block with no
  documented positives has undefined recall and is excluded from recall inference, with counts.
- Secondary diagnostic: the same metric at **10%**. It cannot override the primary decision.
- Boyce diagnostic: moving-window presence/background P/E rank correlation. Window width is 10%
  of each held-out arm's score range; 100 equally spaced centers span min+half-width through
  max−half-width. Windows are closed; skip zero expected mass, retain zero observed ratios, and
  remove consecutive equal P/E ratios before Spearman correlation. Constant scores or too few
  distinct windows return null with a reason. This independently implemented convention is
  documented explicitly; it is not a claim of bit-for-bit equivalence with
  [ecospat](https://github.com/cran/ecospat/blob/master/R/ecospat.boyce.R).
- Uncertainty: **2,000 paired CAR bootstrap draws**, 95% percentile intervals, seed **20261008**.
  Resample the same complete CARs for all comparison arms. Recompute the best baseline in every
  draw. Report per-arm intervals and the full-minus-best-baseline margin interval. This is
  conditional uncertainty over recorded CV folds, without retraining per draw.
- **Keep only if the lower 95% confidence bound of the primary margin exceeds zero.** Otherwise
  report kill/no demonstrated improvement. A feasibility failure is not a model-performance loss.
  The secondary and Boyce diagnostics cannot rescue a failed primary rule.

**Interpretation and power:** with a uniform-area production proxy inside each SADR, a failed
keep rule means **"no demonstrated improvement from this proxy-based accessible-production
feature"**, not evidence against road-catchment logic. With few CAR blocks the paired bootstrap
interval is wide and potentially unstable; report intervals and counts descriptively. The AAFC
registry is close to a census of primary elevators, so this experiment cannot test robustness
to documentation bias. No performance claim extends beyond these protocol-defined comparisons.

This decision concerns the siting component only. The PRD's separate top-10 component-change and
verified-hit tests cannot be satisfied without the later frozen field-verification sample. No
component is promoted to operational use on synthetic tests or a siting score alone.

## Shipping-point hindcast and fallback

Only after siting features are finalized, load the preregistered Phase 3 node allocations and
development CGC 2024–2025 Wheat outcomes. Validate the Phase 3 bundle. A shipping point is one
outcome, even with several elevators. Sum member predictions once; missing any member prediction
makes the whole predicted total UNKNOWN. Never split or duplicate observed volumes per elevator.
Require a unique CAR for the entire group. Unmatched/ambiguous groups remain in the audit.

Convert published kilotonnes to tonnes using the existing explicit conversion record. Baseline
point scores are the mean contextual exposure over its **unique CCS IDs**, avoiding repeated
context for co-located elevators. They are ranking scores, not estimated delivery volumes.
Compare B0/B1/B2/population and the Phase 3 modeled tonnes on the same complete point cohort.
Report all observed, included and excluded counts, reasons, and source outcomes.

At least **15 complete groups** are needed for rank diagnostics. Report Spearman and recall of
the top 20% observed-volume groups, stable shipping-point ties, and 2,000 CAR-bootstrap 95%
intervals for rank correlation; undefined draws remain counted. Report volume MAE, bias and
predicted/observed sum ratio separately for Phase 3. These residuals do not validate absolute
volumes: crop harvest differs from marketed crop-year deliveries, and formal-channel share,
carry-over and within-year registry chronology are unresolved. Do not calibrate those assumptions
against these outcomes in this experiment.

Fallback: aggregate matched observed and predicted point totals by CAR, retaining group counts
and coverage. These are **partial matched-point totals**, not complete district observations.
If there are too few groups, no validation claim is made. The PRD's complete-district fallback
remains unavailable unless complete district observations or a complete audited point-to-district
crosswalk are supplied. No fabricated district totals or facility-level observations are created.

The expert-shortlist contract accepts ordered shipping-point IDs plus author, elicitation date,
scope and consent/release reference. No expert list has been supplied; mark this arm unavailable.
The code does not contact an expert or invent their choices.

## Registration, execution and reproducibility

1. Follow the user's conditional sequence: amendments, counts-only gate, frozen-values script,
   all tests/lint, then verbatim approval recording. Draft/null fields prohibit real evaluation.
2. Rebuild preparation with the approved config. Commit implementation, config, this document and
   lockfile before registration. No metrics or coefficients have been inspected at this step.
3. `register-experiment` creates `preregister-phase4-canada-v1.1` and requires the exact commit
   and tag to exist on the configured remote before writing the immutable registration. Use
   `--publish` to push the committed branch and tag atomically within the command, then verify
   both remote references before accepting registration. This satisfies the pushed-before-success
   requirement while following the user's commit → register/push → verify sequence.
   The immutable
   registration contains commit, protocol, review document, source-index, preparation-index,
   Phase 3 index, code and lockfile hashes also records remote URL, remote branch and verified
   remote commit hash. An existing registration cannot be overwritten.
4. `evaluate-experiment` checks all registration hashes/tag before reading outcomes; build the
   graph and features, apply the feasibility gate, evaluate eligible CV and shipping-point
   diagnostics, and export hashed feature, prediction, fold, group, protocol and report artifacts.
5. `verify-experiment` checks artifact hashes/metadata, common comparison identities, feature
   allowlist, fold separation and unique shipping-point outcomes. Save failures as failures;
   For this conditional run, any error after registration means stop and report; no method,
   code, thresholds, metrics, seeds, folds, features or keep/kill rule may be edited after Step 6.

No network is needed for preparation/evaluation once the two manifests' files are acquired.
Raw, intermediate and large output files are ignored by Git. The repository retains the protocol,
hash manifests, synthetic tests and concise audit; preserve the local data separately.
