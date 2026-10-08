# Phase 6 status — engine delivered, scientific exit pending

**Phase 6 is not scientifically complete and the ranking is not ready to freeze.**
Date: 8 October 2026. The authorized engineering work, deterministic synthetic run and real
source-readiness audit are delivered. Six human-owned scientific gates remain open in the
[review packet](phase6-scientific-review.md); no temporary coefficients were promoted to
approved ranges. This follows AGENTS.md, decision 0003 and the Phase 0 execution gates.

## Delivered and checked

| Component | Delivered | Remaining real-data requirement |
|---|---|---|
| A/B Roads and dry/wet | Directed mode-aware screening graph, explicit speeds/surfaces, restrictions audit, units/CRS, snaps and time budget | Approved freight/season scenarios; barrier/turn review; real origin adapter; large-graph qualification |
| C Allocation | Shared capacity across origins, maximum-service/minimum-travel and nearest-first variants, overflow, unknown handling, deterministic ties and conservation | Approved inventory/assignment assumptions and real comparison |
| D Energy | Treated fraction, residence, inventory, simultaneous airflow, fan/motor/auxiliary kW, cycle energy and ranges | Commercial applicability and sourced joint parameter ranges; seasonal peak method if required |
| E Supply/gaps | Three states, signed comparable kW margins, no missing-to-zero conversion | Applicable installed-capacity evidence and approved interpretation |
| F/G Uncertainty/rank | Joint Sobol draws, separate magnitude/stability summaries, tiers, deterministic top ten, questions, matched ablations | Approved distributions/dependence/thresholds/priority and reviewed real results |
| H Secondary components | Explicitly deferred | Approved sources and core scientific exit first |

The engine writes eight artifacts plus index and fully replays them for verification.
The [execution guide](spec/phase6-science.md) includes the commands and equations.

## Scientific desk-review continuation

The [desk review](phase6-desk-review.md) is complete. It supplies source findings, a
[versioned policy proposal](../configs/scenarios/phase6-policy-proposal-v1.json) and a
[blank evidence worksheet](../data/manual/phase6-site-evidence-template.json).
The policy remains unapproved; commercial inventory/fan/transport inputs remain unresolved.

- **191 tests passed**, with Ruff lint and formatting clean. The continuation adds 26 cases
  covering regional projections, dimensional conversion, approval boundaries and ablations.
- The same synthetic pipeline runs in five non-Canadian geographies. Its selected CRS is
  explicit and checked locally; these tests demonstrate portability, not predictive transfer.
- Airflow conversion requires grain-specific test weight and a reviewed matching bushel basis.
  UNKNOWN inputs do not yield numerical coefficients. Ablations count replacements separately
  from changed identities and shortlist additions/removals.
- Current synthetic run: `phase6:e0af416ec6d6cc7985ae83b0`, four cases and 64 draws; eight
  artifacts replay byte for byte in `outputs/phase6-review-fixture/`. The Canadian synthetic
  inputs and fixture parameters were not changed.
- Historical Phase 3 (ten artifacts), Phase 4 (six) and the demo (32) still verify. The refreshed
  counts-only audit confirms 261 development sites, 16 known/nine unknown production regions,
  two spatial-review nodes, one eligibility issue and zero documented electrical observations.
  All 766,897 AB/SK way rows were checked again. No empirical datasets were acquired.

The [continuation audit](audits/phase6-desk-review.json) records source hashes and checks; its
[readiness audit](audits/phase6-review-readiness.json) binds the updated review packet.
The original audits below are historical records from commit `5953c5f`, not current-code replay
certificates. Preserve the matching source version when reproducing each run.

## Original engineering verification evidence

- Full regression suite: **165 passed**, including 32 new Phase 6 cases; Ruff lint and format
  checks passed. All eight Phase 1 smoke cases passed.
- Complete synthetic run: `phase6:5ad783a05fc50d73069108c9`; four cases × 16 draws = 64 runs;
  13 invented sites, ten exported ranks, all three tiers exercised. Known mass is 700 tonnes
  per case/draw, with one UNKNOWN parent preserved. Eight artifacts passed byte-for-byte replay.
- Tests cover direction/access precedence, MPH conversion, dry/wet closures, duplicate ways,
  CRS, snap failures, global competition, capacity exhaustion, unknown mass/capacity, no
  candidates, conservation, hand-calculated energy, signed margins, parameter dependence,
  gates, Manitoba rejection, input-order independence and tamper detection after rehashing.
- Historical Phase 3: ten artifacts verified; Phase 4: six verified; Phase 5 demo: 32 verified.
  The registered experiment was not refitted or scored. Its verdict and old shortlist remain
  unchanged. Baseline/hindcast results stay accessible for their original model only.
- Real readiness audit: 261 development elevators with reported storage; 25 production
  regions, 16 known and nine unknown; two spatial-review nodes and one eligibility issue;
  zero documented electrical-capacity observations in consumed tables. All 766,897 provincial
  AB/SK road-way rows were validated and their file hashes checked. No MB roads/outcomes read.

The synthetic output is local at `outputs/phase6-synthetic/`. Its input fixtures are committed
and rebuild offline. The [machine readiness audit](audits/phase6-readiness.json) and
[engineering audit](audits/phase6-engineering.json) record the checks. No real scientific
ranking or public map replacement is created.

## Deviations and limits

- Implementation proceeded in module order within this request. The original phase guide's
  incremental intent was followed through separate kernels and acceptance checks.
- New code lives under `enagis.science`; the registered Phase 4 code/config/results were not
  edited. The overall package hash changes by design. Reproducing the historical registered
  evaluation requires its original Git tag; historical verification remains available here.
- Windows sandbox temp-directory permissions initially broke two replay tests; replay now
  uses a generated sibling directory within the writable workspace. No scientific arithmetic
  changed to address that environment failure. The complete suite uses the established local
  Git-fixture permission needed on Windows.
- No empirical source acquisition, Manitoba evaluation, outreach, field verification, economic
  screen or arbitrary scientific threshold was added. Reference sources were read to check
  semantics and equations. Synthetic thresholds remain confined to fixture files.
- The current network omits barriers/turn relations and requires a commodity-specific review;
  the current energy method is a steady-flow scenario, not measured harvest peak power.
  A synthetic pass does not establish scale, transfer, commercial validity or decision benefit.

**Remaining evidence gate:** supply applicable inventory, grain/storage, fan-duty/cycle and
freight assumptions from an existing operator report, engineering study or suitable technical
source, using the worksheet. Human approval must then identify the exact values and method.
AGENTS.md and the PRD require that review; they do not require an external consultant.
Real execution, a prospectively specified comparison and reviewed ablations still follow.
Phase 7's real ranking freeze remains gated. Its [engineering toolkit](phase-7-status.md) has
since been implemented under the user's next-phase request; no real Phase 6 ranking is
described as ready to freeze.
