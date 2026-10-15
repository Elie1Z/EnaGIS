# Hero data vintages and newer references

Checked 10 October 2026. The team looked for newer data alongside the historical inputs, then
explicitly selected **keep newer sources as linked references**. No newer file was downloaded or
substituted into the hero. The approved historical snapshot transferred 13,284,623 bytes (13.3 MB),
within the 100 MB budget. Source responses, retrieval timestamps and hashes are in its manifest.

| Layer | Nyabihu snapshot input (frozen) | Newer official reference found | Compatibility / next gate |
|---|---|---|---|
| Population | WorldPop Global 1 `wpgppop`, 2020; 319,239 people returned for the boundary (ESTIMATED raster sum) | [WorldPop Global 2](https://www.worldpop.org/blog/worldpop-global2-global-high-resolution-population-estimates-for-2015-2030/) covers 2015–2030; [API v2 documentation](https://api.worldpop.org/v2/openapi.json) offers polygon totals | Global 2 changes population inputs, settlement constraints and modeling; a 2025 layer is an estimate/projection, not a new census. Compare on the identical polygon and inspect release, UN adjustment, licence and resolution. Do not just change the year on the old `wpgppop` request. No 2025 Nyabihu total retrieved. |
| Production | NISR 2024 Season A district area × yield share scaled to annual national potato total; Nyabihu 184,486 t/year ESTIMATED, divided by 2022 census 319,047 | [NISR 2025 annual report catalogue](https://microdatabk.statistics.gov.rw/catalog/124/related-materials) lists the [2025 annual report](https://www.statistics.gov.rw/sites/default/files/documents/2025-12/SAS%202025%20Final%20report.pdf) | Publication existence confirmed from the official catalogue (created April 2026, modified June 2026). The PDF was not downloaded and numeric district tables were not inspected. Extract comparable district area/yield and annual totals before a versioned comparison. |
| Most recent production season identified | Full-year 2024 model basis | [NISR 2026 Season A report](https://www.statistics.gov.rw/sites/default/files/documents/2026-04/SAS%202026%20Season%20A%20_Final%20Report.pdf) | Official indexed report identified; no numerical values imported. Season A is not an annual total. Do not splice it into the annual denominator or claim it is the latest complete year. No verified 2026 Season B source was established in this search. |
| Weather | Open-Meteo 2024 daily archive, retained in full | [Open-Meteo historical API](https://open-meteo.com/en/docs/historical-weather-api) supports newer archive periods, including complete 2025 | Retrieve the same variables, coordinates and model in a separately dated scenario. 2026 is incomplete on the review date. Reanalysis is ESTIMATED weather, not a local station reading. No newer weather downloaded. |
| Footprints, roads, grid, places | Overture release 2026-09-23.1, matching the frozen siting model | [Overture documentation](https://docs.overturemaps.org/) | Do not assume release date is imagery acquisition date. A newer map release requires an explicit data-change audit before comparing scores to this model. |
| Tagged facilities and settlements | Overpass response retrieved 10 October 2026, then frozen | [OpenStreetMap](https://www.openstreetmap.org/) is continuously edited | This is already a current retrieval, but source features can be old or wrong. Missing tags do not establish absence. |

Newer data would be a **post-hoc input scenario**, not a revision to the registered Phase 4R table,
protocol, verdict or training. Retain old and new snapshots side by side; report effect on energy
magnitudes and site order separately. Scientific parameters still need human review regardless of
source vintage. No claim of worldwide accuracy follows from the hero.
