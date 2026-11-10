# Agricultural service screening v1

Implemented following Elie Mugisha's 10 November 2026 instruction to lead with services, broaden production beyond a single crop and add relevant agricultural energy uses. Version `service-v1` is separate from the archived commodity recipes.

## Method and applicability

Cold storage, cooling, milling and drying use the existing process equations with service-level eligible production. Their operating ranges are transferred screening assumptions labelled INFERRED. Cooling excludes holding days. Drying quantifies electric fans and handling only. The inherited ranges have not been independently validated for the broader product mix. A site still requires product-compatibility, temperature-zone and equipment checks.

Shelling and threshing, oil pressing and feed preparation expose mapped candidates and production opportunity. Electricity remains UNKNOWN until the analyst supplies positive low/central/high electricity-per-tonne values and an equipment source, date and reuse note. Energy then equals processed tonnes/day multiplied by kWh/tonne, and average operating power equals kWh/day divided by operating hours. Source fields identify user-supplied evidence and do not certify it. Shelling requires a consistent equipment input-mass basis because reported harvested grain and unshelled material differ.

Candidate types and capture assumptions inherit the closest existing stationary-processing scenario and are INFERRED. They indicate places to investigate, not confirmed equipment installations. This release concentrates on stationary post-harvest services. Irrigation needs water sources, water requirements and pumping head before adding a defensible location analysis.

Production is the sum of disjoint relevant reported categories divided by their corresponding population. Existing local potato/maize estimates are used where available. Other components use an explicitly disclosed national proxy. The catchment allocation remains based on mapped homes, population and travel access. Crop lists appear in the evidence view and require no crop selection. Coverage is always partial because unrecorded products and actual demand for the service are unknown. National and local totals in the evidence panel refer to their named geography, not the selected catchment.

Each service is an alternative scenario. Quantities for milling, drying, shelling and feed preparation overlap and must not be summed as distinct production. Capture is capped at the available catchment production in service scenarios. Feed allocation competes with food uses. Outside a data pack, total eligible production can be supplied with provenance. Rwanda production is never substituted for another country.

## Production evidence

NISR, Seasonal Agricultural Survey 2024 Annual Report, Table 0, printed page x (PDF page 10). Retrieved 10 November 2026. The publication listing gives 11 February 2025 as the update date. Figures are sums of the reported 2024 season entries, in metric tonnes. Blank season entries are not independently measured zeros.

| Category | Season A | Season B | Season C, if reported | Reported total |
| --- | ---: | ---: | ---: | ---: |
| Irish potato | 460830 | 285596 | 80929 | 827355 |
| Maize | 507985 | 119101 | — | 627086 |
| Sorghum | 47452 | 140314 | — | 187766 |
| Paddy rice | 69098 | 72834 | — | 141932 |
| Wheat | 3371 | 13045 | — | 16416 |
| Beans | 233142 | 242239 | 3046 | 478427 |
| Pea | 7042 | 4628 | 549 | 12219 |
| Groundnut | 5328 | 9062 | — | 14390 |
| Soybean | 19171 | 17051 | 483 | 36705 |
| Vegetables | 145933 | 177549 | 65980 | 389462 |
| Fruits | 25250 | 27219 | — | 52469 |

The table was text-extracted and visually checked. PDF SHA-256 is `eb783213543858d731876c0fc09d7483dc94aff1b4d2d634f60fc30f88822032`. Publicly published statistics are attributed to NISR. An explicit reuse licence was not established and is recorded as such in the data metadata. The downloaded PDF stays in local verification outputs.

[NISR report](https://statistics.gov.rw/sites/default/files/documents/2025-02/SAS%202024%20Annual.pdf)

FAO describes motorised shelling, threshing, milling, drying and other post-harvest operations. Its description supports the choice of activity categories. It supplies no universal electricity coefficient for these implementation scenarios.

[FAO post-harvest operations](https://www.fao.org/sustainable-agricultural-mechanization/guidelines-operations/on-farm-postharvest-and-value-addition/en/)

## Compatibility and verification

Legacy identifiers continue to open saved files and frozen demonstrations. New selections use service identifiers and preserve service boundaries, component coverage, equipment evidence and assumptions in saved analyses and exports. Parameter overrides reset when switching services to prevent an unrelated service from inheriting temperatures or energy intensity.

Dedicated checks cover aggregation, spatial provenance, all seven services, unavailable equipment energy, sourced intensity, missing-country data, supplied totals, physical domains, versions and reported zero. Full-result legacy digests remain pinned to the pre-refactor results. Browser verification covers normal menu selection, worker calculation, evidence, service changes, missing inputs, save/reopen and export.

Final verification on 10 November 2026 passed 240 Python tests, 74 Node tests and 126 browser checks (27 journey, 20 saved-analysis/provenance, 40 application regression, 15 service workflow and 24 archived offline demonstration). The reproduction tool passed all 23 original checksums and matched the archived and current rankings. Eight Python smoke cases passed. Ruff lint and formatting passed for all 86 tracked Python files, and JavaScript syntax and Git whitespace checks passed. The pre-existing untracked film directory is outside that tracked-file lint result. Desktop and mobile service screenshots were inspected. Controlled fixtures verify implementation behaviour, while broader service accuracy still requires evaluation against local operating data.

Verification logs and screenshots are generated locally under `outputs/service-upgrade/`. Implementation commits use Elie Mugisha's configured identity. This milestone is saved locally for the user's GitHub publication workflow.
