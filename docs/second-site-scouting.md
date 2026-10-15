# Second-site scouting: can the suggested tools run honestly somewhere else?

Run 2026-10-11 with `node scripts/scout-sites.mjs` (config `configs/second-site-candidates.json`, SHA-256 `4a6584021d58…`). Audit file: [audits/second-site-scouting.json](audits/second-site-scouting.json). Traffic: 26.4 MB in 628 requests (cap 280 MB).

## Decision

**Image detector (YOLO-type, C2): no candidate passes.** None has open imagery at 1 m or finer, under a licence that allows training and publishing, covering the documented facilities.

**Footprint classifier (C1): Tanzania, Njombe passes** (≥ 300 documented processing/storage points in ≥ 6 sub-districts, redistributable labels).

## Checklist by candidate

| Candidate | Region | Documented processing/storage points (app rules + name:en) | strict app rules | Sub-districts with a point | Open imagery ≤ 1 m covering points | C1 footprint | C2 detector | Failed tests |
|---|---|---:|---:|---:|---:|---|---|---|
| India, Uttar Pradesh potato cold-storage belt | South Asia | 13 | 13 | 5 | 0 | FAIL | FAIL | labelled_positives, subdistrict_spread, detector_imagery |
| India, West Bengal potato cold-storage belt | South Asia | 18 | 18 | 11 | 0 | FAIL | FAIL | labelled_positives, detector_imagery |
| Bangladesh potato areas | South Asia | 64 | 64 | 11 | 0 | FAIL | FAIL | labelled_positives, detector_imagery |
| Kenya, Nyandarua and Meru | Africa | 5 | 5 | 3 | 0 | FAIL | FAIL | labelled_positives, subdistrict_spread, detector_imagery |
| Uganda, Kabale | Africa | 3 | 3 | 0 | 0 | FAIL | FAIL | labelled_positives, subdistrict_spread, detector_imagery |
| Tanzania, Njombe | Africa | 882 | 882 | 6 | 0 | PASS | FAIL | detector_imagery |
| Ethiopia, Gojjam (East and West Gojjam zones) | Africa | 2 | 2 | 1 | 0 | FAIL | FAIL | labelled_positives, subdistrict_spread, detector_imagery |

- **India, Uttar Pradesh potato cold-storage belt:** fails on 13 documented processing/storage points (needs 300); points in 5 sub-districts (needs 6); 0 points under open imagery at ≤ 1 m (needs 300).
- **India, West Bengal potato cold-storage belt:** fails on 18 documented processing/storage points (needs 300); 0 points under open imagery at ≤ 1 m (needs 300).
- **Bangladesh potato areas:** fails on 64 documented processing/storage points (needs 300); 0 points under open imagery at ≤ 1 m (needs 300).
- **Kenya, Nyandarua and Meru:** fails on 5 documented processing/storage points (needs 300); points in 3 sub-districts (needs 6); 0 points under open imagery at ≤ 1 m (needs 300).
- **Uganda, Kabale:** fails on 3 documented processing/storage points (needs 300); points in 0 sub-districts (needs 6); 0 points under open imagery at ≤ 1 m (needs 300).
- **Tanzania, Njombe:** passes the footprint-classifier tests; the image detector fails on 0 points under open imagery at ≤ 1 m (needs 300). Label provenance: 881 of 882 points carry the source tag "WFP Field Survey 2021, OMDTZ".
- **Ethiopia, Gojjam (East and West Gojjam zones):** fails on 2 documented processing/storage points (needs 300); points in 1 sub-districts (needs 6); 0 points under open imagery at ≤ 1 m (needs 300).

Pass rules (all required): an energy-access region (Africa or South Asia); ≥ 300 documented processing or storage points (mill, milk_centre, cold_store, coffee_station, warehouse, agro_factory, tea_factory); spread over ≥ 6 sub-districts; labels redistributable (OpenStreetMap, ODbL). The detector additionally needs open imagery at ≤ 1 m (≤ 0.6 m for small assets), under a licence that allows training and publishing (CC-BY-4.0, CC-BY-SA-4.0, CC0-1.0, PDDL-1.0, ODbL-1.0), covering ≥ 300 of those points.

## By district

| District (OSM relation) | Area km² | Points (any aggregation) | Processing/storage | By type | Sub-district level · units | Overture buildings (ESTIMATED) | Largest roofs in sample | Roof at sampled facilities ≥ 600 m² | OAM images (≤ 1 m) | Maxar Open Data events | OSM power-line ways |
|---|---:|---:|---:|---|---|---:|---|---|---|---|---:|
| Agra (1958554) | 4,028 | 49 | 11 | market 38, milk_centre 8, cold_store 3 | 6 · 6 | 1,092,053 (8/854 tiles) | max 2,184 m², p99 525 m², 0.7% ≥ 600 m² | 5 of 8 | 0 (0) | none | 231 |
| Firozabad (1958557) | 2,412 | 2 | 1 | market 1, mill 1 | 6 · 4 | 491,258 (8/510 tiles) | max 2,385 m², p99 313 m², 0.3% ≥ 600 m² | 1 of 1 | 0 (0) | none | 98 |
| Hathras (1958145) | 1,777 | 1 | 1 | cold_store 1 | 6 · 4 | 586,645 (8/379 tiles) | max 2,094 m², p99 394 m², 0.3% ≥ 600 m² | 0 of 1 | 0 (0) | none | 53 |
| Hooghly (1970297) | 3,145 | 18 | 14 | market 4, mill 3, cold_store 3, warehouse 3, agro_factory 3, milk_centre 2 | 6 · 18 | 1,177,484 (8/616 tiles) | max 5,231 m², p99 244 m², 0.2% ≥ 600 m² | 6 of 8 | 0 (0) | none | 173 |
| Purba Bardhaman (1970280) | 5,400 | 9 | 4 | market 5, agro_factory 2, warehouse 1, mill 1 | 6 · 23 | 1,226,506 (8/1076 tiles) | max 1,456 m², p99 232 m², 0.1% ≥ 600 m² | 3 of 4 | 0 (0) | none | 31 |
| Munshiganj District (9523777) | 927 | 57 | 7 | market 50, cold_store 3, milk_centre 2, mill 2 | 6 · 6 | 433,761 (8/191 tiles) | max 3,160 m², p99 312 m², 0.2% ≥ 600 m² | 5 of 7 | 48 (48) | none | 10 |
| Bogura District (9494884) | 2,903 | 151 | 57 | market 94, mill 35, warehouse 13, agro_factory 4, milk_centre 3, cold_store 2 | 6 · 12 | 1,064,003 (8/594 tiles) | max 92,738 m², p99 404 m², 0.6% ≥ 600 m² | 4 of 8 | 0 (0) | none | 66 |
| Nyandarua (3495557) | 3,287 | 9 | 3 | market 6, warehouse 2, milk_centre 1 | 6 · 5 | 407,907 (8/553 tiles) | max 25,413 m², p99 210 m², 0.2% ≥ 600 m² | 0 of 3 | 2 (1) | none | 2 |
| Meru (3495553) | 6,991 | 19 | 2 | market 17, warehouse 2 | 6 · 9 | 280,770 (8/1176 tiles) | max 708 m², p99 196 m², 0.1% ≥ 600 m² | 2 of 2 | 1 (0) | none | 3 |
| Kabale (3501894) | 616 | 11 | 3 | market 8, milk_centre 1, warehouse 1, agro_factory 1 | none · 0 | 142,188 (8/102 tiles) | max 1,040 m², p99 195 m², 0.1% ≥ 600 m² | 1 of 3 | 0 (0) | none | 0 |
| Njombe (3775101) | 21,244 | 887 | 882 | mill 882, market 5 | 5 · 6 | 1,286,190 (8/3688 tiles) | max 1,024 m², p99 240 m², 0.0% ≥ 600 m² | 0 of 8 | 1 (1) | none | 5 |
| East Gojjam (3306144) | 14,222 | 16 | 1 | market 15, warehouse 1 | 6 · 8 | 1,026,092 (8/2474 tiles) | max 624 m², p99 172 m², 0.0% ≥ 600 m² | 1 of 1 | 0 (0) | none | 25 |
| West Gojjam (3306153) | 13,326 | 35 | 1 | market 34, warehouse 1 | none · 0 | 1,078,695 (8/2338 tiles) | max 652 m², p99 217 m², 0.1% ≥ 600 m² | 1 of 1 | 0 (0) | none | 79 |

## Imagery checked

- **OpenAerialMap** (catalogue default licence CC-BY 4.0; per-image licence recorded where given): searched by each district's bounding box; images, resolution and dates are listed per district in the audit file. Coverage counts a documented point only if it lies inside an image footprint at the required resolution.
- **Maxar Open Data** (55 events in the STAC catalogue; catalogue licence CC-BY-NC-4.0): event extents intersected with each district. CC-BY-NC is non-commercial only, so it fails the training/publishing licence test for this project even where an event overlaps.
- **Open Cities AI Challenge (GFDRR; Source Cooperative open-cities/ai-challenge)**: Checked the STAC catalogues on 10 Oct 2026. Tier-1 training collections are acc, mon, ptn, kam, dar, znz and nia. Their bounding boxes are small urban patches in Accra, Monrovia, Pointe-Noire, Kampala (0.25N 32.63E), Dar es Salaam, Zanzibar and Niamey; tier 2 adds gao, kin and mah. None lies in a candidate district. Per-collection licence 'various' (znz CC-BY-4.0); README licence ODbL-1.0. Labels are building footprints only, with no agricultural storage or processing class. Fails coverage and labels for every candidate.
- **Sentinel-2 (Copernicus)**: Global, free and open, but the finest bands are 10 m. That is 10 times coarser than the 1 m detector threshold, so it fails the resolution test everywhere. It may show the largest cold-storage roofs, but that is unproven and was not tested.
- **Commercial basemaps (Google, Bing, Esri World Imagery)**: Sub-metre in many places, but these are proprietary basemaps, not open imagery. Their terms were not reviewed in detail. They are treated as failing the open training-and-publishing licence test.

## Energy-access context (national, DOCUMENTED)

| Country | Access to electricity, % of population | Rural, % of rural population | Year |
|---|---:|---:|---|
| IND | 99.9 | 99.9 | 2024 |
| BGD | 99.5 | 99.6 | 2024 |
| KEN | 77 | 67.1 | 2024 |
| UGA | 55.3 | 44.8 | 2024 |
| TZA | 52.4 | 33.7 | 2024 |
| ETH | 56.6 | 44.8 | 2024 |

District-level electrification was not found in an easily reusable public source; OSM power-line counts per district are listed above as mapped-grid context only (mapping completeness varies).

## Method and limits

- Facilities: OpenStreetMap via Overpass, retrieved on the run date, classified with the app's own `classifySite` rules (same look-alike exclusions as Rwanda). Where an element's `name` is in a non-Latin script and an English `name:en` exists, the rules read the English name ("app rules + name:en"); the strict count without that fallback is shown too. Names only in Devanagari, Bengali or Amharic without an English tag cannot be classified by these rules; their number is in the audit file per district (`unclassifiable_non_latin_without_english`).
- Duplicates (a node and a building for the same place) are merged with the app's rule: same type or same name within 80 m.
- Sub-districts: the first administrative level below the district with at least 3 units in OpenStreetMap; a facility is counted in the sub-district whose area contains it.
- Buildings: Overture Maps buildings (release 2026-09-23.1) read from a seeded random sample of zoom-14 tiles inside the boundary, scaled by the number of such tiles (ESTIMATED). Roof areas use the app's footprint-area code.
- OpenStreetMap documents only some facilities; absence of a mapped facility is not absence of a facility. Counts are a lower bound of what exists and an upper bound of what is usable as labels.
- No field verification (n = 0). This is a data-availability audit, not a model result.

