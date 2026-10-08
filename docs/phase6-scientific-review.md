# Phase 6 — scientific review packet

**Decision needed before a real scientific ranking.** The implementation and synthetic
acceptance run are available; no real Phase 6 ranking has been generated or frozen.

## Why this cannot be completed by a generic approval

AGENTS.md requires sourced, human-approved scientific parameters and scenarios. Decision 0003
and the Phase 0 handoff specifically reserve commercial applicability, parameter ranges,
meaningful gap rules and uncertainty thresholds for R3/R4 review. The Phase 4 approval covered
a different experiment. Neither it nor permission to implement Phase 6 provides the missing
commercial ranges. Merely entering an approver name beside unknown values is insufficient.

The next useful action is to have a grain-storage/aeration reviewer and the project decision
owner complete the six decisions below. No new source acquisition or outreach is being
performed implicitly. Published specialists are leads, not engaged reviewers.

## Evidence already available

The [machine audit](audits/phase6-readiness.json) verifies the consumed pinned inputs.

| Coverage | Result | Interpretation |
|---|---:|---|
| AB/SK elevators | 261 (89 / 172) | Development registry candidates |
| Reported storage capacity | 261 known | All-commodity tonnes, not airflow or electrical kW |
| Production reporting regions | 25 | 16 known, nine UNKNOWN |
| Spatial review | 2 nodes | Coordinate/reporting-region conflicts |
| Eligibility unresolved | 1 node | Requires explicit disposition |
| Electrical capacity observations in consumed tables | 0 | Missing documentation, not absent fans |
| AB / SK road ways | 512,513 / 254,384 | Provincial counts; overlapping extracts not deduplicated here |
| AB / SK ways without surface tags | 257,718 / 47,219 | Cannot assign wet-road effects from documented surface alone |
| AB / SK ways without access tags | 502,568 / 251,940 | Default legal access needs a reviewed mode/class policy |
| AB / SK ways with conditional tags | 629 / 20 | Need richer handling or declared exclusions |

No delivery outcome files or Manitoba roads were opened for this audit. The historical
Phase 4 comparisons remain available, with their original limitations and KILL wording.

## Six decisions to resolve

The machine-readable companion is
[`phase6-canada-v1.review.json`](../configs/scenarios/phase6-canada-v1.review.json).
All six `approved_value` fields and the overall approval are deliberately null.

1. **Production origins (R2/R3).** Specify the spatial proxy, parent-to-origin fractions,
   precision, suppression policy, affected-site exclusions and source/period applicability.
   Every known SADR total must be counted once. The existing uniform-area proxy could support
   a declared diagnostic, but does not identify farms. Phase 4's failed keep rule means
   “no demonstrated improvement from this proxy-based accessible-production feature”; it
   does not disprove road-catchment logic. The crop raster remains a possible future input,
   not something acquired for this work.
2. **Transport and seasons (R3/R1).** For bulk wheat, review an HGV vehicle profile. Supply
   class speeds (km/h), dry/wet factors or explicit impassability for each surface, unknown
   surface/access policy, maximum travel time (minutes), snap limit (metres) and connector
   speed. Review node barriers, turns, freight restrictions and graph exclusions. Walking,
   cycling and motorbike code support does not make those appropriate bulk-grain scenarios.
3. **Inventory and assignment (R3/R4).** Provide operating-period and residence ranges,
   wheat storage share, treated fraction and dependence. Confirm whether steady-flow inventory
   is adequate or supply the evidence for a seasonal/peak inventory adapter. Approve the
   assignment variants and unknown-capacity treatment. The proposed two variants are
   maximum-served/minimum-tonne-minutes and nearest-first; their synthetic contrast demonstrates
   why one must not choose a variant by looking at attractive rankings.
4. **Commercial aeration (technical reviewer with R3/R4).** Complete the parameter worksheet
   below using grain depth/geometry, fan curves, inventory and operation evidence applicable
   to primary elevators. Specify the operating boundary and physically admissible joint
   relationships. Farm-bin example values alone do not establish this applicability.
5. **Supply, uncertainty and investigation policy (R3/R4 and project owner).** Confirm comparable
   installed electrical capacity semantics and signed margins. Approve distribution forms,
   dependencies, Sobol seed/draw count, case weights, summary quantiles and Robust threshold.
   The proposed priority is inclusion frequency, median technical kW, stable ID; it is an
   investigation ordering. Undocumented supply remains Verify-first. The project budget is
   ten; no scientific 80% threshold or fixture seed has been selected.
6. **Exit review (R4/R3).** Before scoring new predictions, specify a Phase 6 comparison using
   development shipping-point groups with common coverage and no duplicated deliveries.
   Review real ablations and source/date exclusions, qualify runtime/memory on the approved
   graph, then record whether the ranking is scientifically ready to freeze. Historical
   Phase 4 hindcast performance belongs to the previous model. No Manitoba transfer claim
   or field-validation claim is available.

## Technical worksheet

For each row supply lower / central / upper (or a justified fixed value), distribution, joint
group or required richer joint model, source snapshot/URL/date, applicability and reviewer/date.
Blank entries are execution gates, not zero values. Source documents need applicable terms
and pinned metadata before they become runtime evidence.

| Parameter | Unit | Needed evidence |
|---|---|---|
| Residence time | day | Wheat inventory and turnover over the modeled period |
| Modeled operating period | day | Period definition; not an assumed operating-status observation |
| Wheat storage share | fraction | Competing-crop occupancy and usable storage |
| Treated-at-node fraction | fraction | Which assigned wheat receives the modeled storage/aeration service |
| Required airflow | m³/s per tonne | Storage geometry and service duty |
| Total static pressure | Pa | Compatible grain/duct resistance at that airflow |
| Fan efficiency | fraction | Duty-specific air-power definition and fan performance |
| Motor efficiency | fraction | Motor/drive operating conditions |
| Simultaneous inventory fraction | fraction | Fans/bins operated together |
| Cooling-cycle duration | hour | Operating criterion and completion, not an annual cycle count |
| Auxiliary load | kW | Explicit included equipment and concurrent operation |

The executable method is described in the [Phase 6 guide](spec/phase6-science.md). It supports
global fixed/triangular parameters with shared quantiles. If the review requires site-level
parameters, nonlinear fan curves, arbitrary dependence, harvest trajectories or seasonal
peak inventory, extend and test that contract before running; do not squeeze a different
scientific method into the existing fields.

## Sources checked for method review

- [OpenStreetMap access documentation](https://wiki.openstreetmap.org/wiki/Key:access):
  mode-specific access may override general access. These tags describe permissions rather
  than measured travel speeds. This informs parsing, not approval of a Canadian freight profile.
- [OpenStreetMap one-way documentation](https://wiki.openstreetmap.org/wiki/Key:oneway):
  direction restrictions and mode exceptions need explicit interpretation; pedestrian paths
  can be ambiguous. Unsupported cases are excluded for review.
- [University of Minnesota wheat and barley storage guidance](https://extension.umn.edu/agriculture/crop-production/small-grains/storing-wheat-and-barley):
  supports reviewing the cooling-service boundary and monitoring completion. It does not
  supply site-specific commercial inventory or fan parameters.
- [University of Minnesota fan selection guidance](https://extension.umn.edu/agriculture/crop-production/corn/selecting-fans-and-determining-airflow-for-grain-bins)
  and [DOE fan-system sourcebook](https://www.energy.gov/sites/default/files/2014/05/f16/fan_sourcebook.pdf):
  support reviewing air-power, resistance, equipment performance and the electrical boundary.
  No numeric recommendations were adopted as commercial-elevator measurements.
- [SciPy Sobol documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.qmc.Sobol.html):
  use complete power-of-two samples for balance. This supports sampling mechanics, not the
  project's distribution choices or stability threshold. Execution uses the pinned lockfile.

Consulted 8 October 2026. These are methodological references, not new empirical inputs.

## After review

Record the substantive choices and applicable source evidence in a new scientific configuration,
with approval attached to the exact values/method version. Build and validate the reviewed
origin/network/site input bundle; retain UNKNOWN and exclusion reasons. Run and replay offline,
review ablations and the predefined benchmark, and sign the Phase 6 exit. Only then proceed to
Phase 7 ranking freeze and its separately approved verification protocol.
