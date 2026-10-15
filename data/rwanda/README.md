# Rwanda data for EnaGIS Live

| File | What it is | SHA-256 |
|---|---|---|
| `district_production_2024.csv` / `.json` | Potato and maize production by district: NISR Seasonal Agricultural Survey 2024 Season A area × yield shares, scaled to the 2024 national annual totals; 2022 census population. Kirehe, Ngoma and Bugesera yields imputed from neighbours. ESTIMATED. | `36f1e19e…` / `208661f2…` |
| `siting_cells.csv` | Phase 4R training table: 25,281 squares of 1 km in all 30 districts, 11 feature inputs, labels `y` (processing or storage) and `y_any` (adds markets and cooperatives), and the documented facilities in each square. Built on 10 Oct 2026 by `live/tools/harvest.js` from Overture Maps `2026-09-23.1`, OpenStreetMap and Overture places. This exact table was evaluated: [phase4r-results](../../docs/phase4r-results.md). | `664350e8aa446b22…` |
| `harvest_summaries.json` | District summaries written by the harvest on 10 Oct (morning engine). Kept for provenance: it predates the look-alike fixes (tea factories, toilets, hotels). | `4b88a0e4…` |
| `district_summaries.json` | The same 30 districts analysed in the browser with the shipped engine, all four value chains. Source of [rwanda-national-screening](../../docs/rwanda-national-screening.md). | `3c9d25fa…` |

Licences: OpenStreetMap and Overture-derived values are ODbL 1.0 (Overture places CDLA-Permissive-2.0);
WorldPop CC BY 4.0; NISR statistics are public. Unlabelled squares are background, not proven absences.
