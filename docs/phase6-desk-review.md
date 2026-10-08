# Phase 6 scientific desk review — 8 October 2026

**Desk review completed; scientific execution remains evidence-gated.** The review now has
specific source findings, a concrete decision-policy proposal and a local evidence template.
The user reconfirmed global adaptability as the product mission. Canada remains the development
benchmark; changing location must not silently transfer its units, climate or operational assumptions.

## Findings that change the review

| Finding | Consequence for EnaGIS |
|---|---|
| The routing kernel hard-coded EPSG:3347 | The shared kernel now accepts an explicitly configured projected metre CRS, checks its own area of use, and rejects geographic coordinates, feet and Web Mercator for distance analysis. Canada retains EPSG:3347. |
| Canadian test weights distinguish bushel definitions and vary with grain | A new conversion requires specific kg/bushel and matching, reviewed bushel bases. Missing or incompatible inputs return UNKNOWN. |
| Grain-only pressure charts omit ductwork, fines and filling effects | Such a table is insufficient as total system pressure or a site-specific fan duty. |
| Commercial bins and silos have different operating regimes | A single global airflow/pressure/cycle distribution lacks adequate support. Local equipment, inventory and climate must define the service scenario. |
| Freight restrictions can alter permitted loads and access | Dry/wet speed multipliers alone do not establish legal or physically usable freight catchments. |
| Human review has both policy choices and factual input gaps | A project owner can approve policy; approval cannot create missing site evidence. An external consultant is not a repository requirement, although technical competence is needed to judge applicability. |

The former response asked a reviewer to complete the whole task. This continuation performs
the research and makes the policy choices reviewable. The repository still requires human
approval of the resulting values and method. No human approval or commercial expertise has
been attributed to the assistant.

## Source findings and their limits

### Cooling airflow and unit basis

CGC's [PAMI airflow guidance](https://www.grainscanada.gc.ca/en/grain-quality/manage/manage-storage-prevent-infestations/airflow-resistance-charts.html)
gives a cooling target of **0.1–0.25 cfm/bushel**. This is retained as a source-native guideline,
with no chosen probability distribution or universal conversion to tonnes. Its resistance
tables depend on grain and depth and exclude additional losses from fines, ductwork and filling.
The published fan examples are equipment examples, not installed equipment at our candidates.

CGC's [test-weight explanation](https://www.grainscanada.gc.ca/en/grain-quality/grain-grading/grading-factors/test-weight-grain.html)
distinguishes Canadian Avery and US Winchester bushels and warns against one fixed
bushels-to-tonnes factor. Use measured or appropriately sourced grain test weight on the same
basis as the airflow guideline. A source with an unspecified bushel basis stays unresolved.
The conversion is:

```text
(cfm/bushel) × (0.3048³ m³/ft³) / (60 s/min)
             × (1000 kg/tonne) / (specific kg/bushel)
```

`unit_review.py` records the original inputs, source dates and licences, the dimensional
factors and the missingness reason. Its synthetic arithmetic example is not a recommended
test weight. Matching labels alone are not scientific approval of source applicability.

### Commercial applicability and cycle timing

[Oklahoma State's commercial-elevator bulletin](https://extension.okstate.edu/fact-sheets/storing-moist-wheat-at-commercial-elevators-in-oklahoma)
distinguishes steel-bin and concrete-silo airflow, and describes cooling behavior that depends
on grain shape and storage conditions. It concerns Oklahoma and includes moist-grain management;
that context cannot be transferred directly to Canada. It is useful evidence that a universal
commercial coefficient is inappropriate, rather than a licence to borrow one.

[University of Minnesota wheat guidance](https://extension.umn.edu/agriculture/crop-production/small-grains/storing-wheat-and-barley)
uses an approximate farm-bin cooling-time relation of 15 divided by airflow in cfm/bushel and
requires temperature checks to determine completion. This relation would couple airflow and
cycle hours if adopted; independently sampling both as unrelated parameters would not implement
that method. It has not been selected as a commercial-elevator model.

CGC's [monitoring and aeration guidance](https://www.grainscanada.gc.ca/en/grain-quality/manage/manage-storage-prevent-infestations/monitor-grain-temperature.html)
emphasizes storage configuration, grain type, static pressure and equipment-specific timing.
Its discussion also illustrates why cooling opportunity depends on local ambient conditions.
Consequently, Canadian climate assumptions cannot establish service hours for a warmer region.

### Freight and inventory

[Alberta's road-restriction guidance](https://www.alberta.ca/road-restrictions-and-bans) and
[Saskatchewan's seasonal truck-weight guidance](https://www.saskatchewan.ca/business/transportation-and-road-construction/information-for-truckers-and-commercial-trucking-companies/regulations-and-road-restrictions/increased-weights-and-road-restrictions)
show that seasonal road management includes load limits. They identify a necessary input class;
current pages do not establish the historical restrictions for a specific 2024 route. Actual
weights, dates, routes and local road authority coverage still need review before routing use.

CGC's [statistics catalogue](https://www.grainscanada.gc.ca/en/grain-research/statistics/index.html)
identifies aggregate stocks and movement data as possible review leads. Aggregate stocks cannot
be allocated to individual elevators as observed inventory or silently used to calibrate against
the same delivery outcomes later used for evaluation. No new inventory dataset was acquired.

All links were consulted on 8 October 2026. References are review evidence, not newly pinned
runtime inputs. No source tables, fan curves or source text have been copied into a redistributable
scientific dataset. Public runtime inputs need their own version, hash, terms and applicability review.

## Concrete policy proposal

The [versioned proposal](../configs/scenarios/phase6-policy-proposal-v1.json) recommends:

- Keep nearest-first as the reference assignment, consistent with the PRD; compare the shared
  maximum-served/minimum-travel variant on identical inputs and parameter draws.
- Preserve unknown production and capacity, retain signed comparable kW margins, and use
  Verify-first when supply evidence is missing.
- Use the existing top-ten budget and inclusion-frequency ordering. Propose 80% inclusion in
  every declared case for Robust, with unresolved evidence taking precedence.
- Propose 1,024 scrambled Sobol draws per case, seed 20261008, equal case weights and 5–95%
  magnitude quantiles. These are explicit design choices awaiting approval, not calibrated facts.
- Apply the PRD ablation rule prospectively. Count actual replacements separately from set
  symmetric difference: one replacement produces two changed identities. Missing evaluation
  evidence cannot become a claim that added complexity improves decisions.

Approving this proposal would settle policy choices only. It would not fill the missing
physical, transport or production parameters, approve a final ranking, authorize outreach,
or change the registered Phase 4 experiment. A fresh Phase 6 common-cohort comparison must
be specified before scoring. The earlier Phase 4 hindcast remains historical evidence for
its original model.

## Smallest useful evidence handoff

The [JSON worksheet](../data/manual/phase6-site-evidence-template.json) gives the exact fields.
An existing operator report, engineering study or appropriately applicable technical source
can supply them; a new field survey is not automatically necessary. For the relevant site
classes, establish wheat inventory/turnover, storage geometry and test weight, a compatible fan
operating point and cycle boundary, plus commodity transport and seasonal access assumptions.
Every proposed range needs its applicability and joint relationships reviewed. Record unknown
installed electrical capacity explicitly; it must never be inferred from storage tonnes.

The current consumed data do not contain those operating details. Searching general guidance
does not identify them for these 261 sites. Broad invented ranges would not solve that gap.
Approval must be attached to actual values and a concrete method, after that evidence exists.

## Global reuse delivered and its practical limit

The same allocation/energy/uncertainty pipeline is now exercised with synthetic geography in
East Africa, South America, South Asia, Oceania and Europe. The tests retain mass, UNKNOWN and
ranking behavior, and compare local projected distances with geodesic distances at their test
locations. They demonstrate software portability only. They are not training, field validation
or evidence that the model predicts well in those regions.

For a real new region, provide source adapters, a suitable analysis CRS, local production and
equipment evidence, local transport/climate scenarios and an untouched evaluation protocol.
The real-run authorization still protects the Canadian development scope and Manitoba holdout.
New service types need their own physics. A map location alone does not identify a service need.

**Scientific exit:** unresolved local inputs and human approval still prevent a real Phase 6
ranking from being declared ready to freeze. The desk review and portability work are complete;
the phase remains open at this specific evidence gate.
