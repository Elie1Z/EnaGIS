# Phase 5 completion — Monday-ready integrated demo

**COMPLETE at the presentation/integration boundary, 8 October 2026.** Open
[demo/index.html](../demo/index.html) and click **Start guided demo**. The
[presenter guide](phase-5-demo-guide.md) provides a three-minute walkthrough and offline rebuild.

## Delivered

- Plain static MapLibre map with vendored assets, existing pinned AB/SK major-road context,
  reporting-region shading, ten exact pipeline sites and a schematic fallback without WebGL.
- Question-led cards: identity/operator/type/precision/rank, scenario throughput/inventory/
  airflow/power/cycle energy, observed storage, supply documentation, gap bucket, UNKNOWN
  electrical margin, uncertainty status, source dates/licences and complete JSON trace export.
- Five-step guide: decision → selected site → source/process chain → recorded comparison →
  export and next verification action. Search, map/list selection and keyboard controls work.
- Coverage and explicit temporary scenario tables, all 11 permitted public source snapshots,
  the original verified Phase 3/4 artifacts, vendor notices and 32 checksummed demo artifacts.
- Exact shortlist CSV, typed GeoJSON and a separately attributed ODbL roads derivative.
  Ready offline bundle is checked in after the rights review in [decision 0007](decisions/0007-offline-demo.md).

## Evidence shown

261 development candidates; 186 ranked scenario estimates; ten shortlisted sites. Exclusions
remain visible: 72 production unknown, two coordinate conflicts and one eligibility unresolved.
Known mass 11,918,640 t is conserved; nine unknown origins remain outside those mass totals.
The top ten in this historical run are all SK; the coverage footprint remains AB/SK.

The CCS experiment is separate from the engineering shortlist. The demo shows all eight arms,
intervals, primary 155-CCS/60-positive/seven-positive-CAR cohort, sensitivity availability and
overlapping exclusions. Full-model top-20% mean CAR recall 35.7%; production-only 39.8%;
margin −4.05 pp, paired 95% interval [−39.29, −0.71] pp. Verdict **KILL / no demonstrated
improvement from this proxy-based accessible-production feature**. It is not evidence against
road-catchment logic. With few CAR blocks, intervals are wide and potentially unstable and
reported descriptively. AAFC census-like registry coverage cannot test documentation bias.

The separate shipping-point hindcast uses 52 common groups/seven CARs, with 86 exclusions.
Phase 3 Spearman 0.773 [0.282, 0.821], diagnostic only; absolute-volume accuracy is unvalidated.
No field sample (n = 0), expert shortlist, metered energy or Manitoba transfer result is invented.
Temporary energy coefficients/methods retain null approvals; uncertainty tiers are not assessed.

## Verification

- Complete suite: **133 tests passed**, including the tiny complete offline pipeline,
  determinism, conservation, holdout and trace checks plus six Phase 5 artifact tests.
- Ruff lint and format checks passed; JavaScript syntax check passed; eight smoke cases passed.
- Offline rebuild from the portable evidence archive passed; tampering, run mismatch,
  restricted sources and scientific-output overwrite checks passed. Export is deterministic.
- Canonical JSON and LF bytes preserve checksums across platforms. All 33 staged Git blobs
  match the portable files/manifest; the 33-file ZIP passed its integrity check.
- Original Phase 3: ten artifacts independently verified. Original Phase 4: six independently
  verified. Demo manifest: 32 artifacts verified.
- Browser checks passed: desktop guide, all views, site/list/map selection, mobile search and
  keyboard selection, selected-site JSON download, CSV download, ten-pin schematic fallback,
  responsive layout without horizontal page overflow, and no application console errors.
- Scientific code hash is unchanged:
  `0396fc8b65020508899642f8108a6af72c74418d7a9baac7bb8b65dd3074754c`.
  Phase 4 frozen-values check passed. No experiment was refitted or scored for Phase 5.

See [machine audit](audits/phase5-demo.json) and [desktop preview](audits/phase5-demo-desktop.jpg).
The in-app browser prohibits file URLs; visual QA used a localhost-only static preview of the
public demo folder. All delivered resources are local; runtime serving is not required.

## Limits and next work

This phase completes the demonstration, not the final scientific screening product. It does
not add seasonal travel times, crop raster inputs, Monte Carlo tiers, tariffs, economics, grid
access or new ranking rules. Commercial inventory/fan applicability, source/time ambiguities,
independent human review and field/transfer validation remain gates. The exporter protects
the link to the historical experiment instead of silently evaluating a newer scientific run.
