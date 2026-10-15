# Phase 4R results: the Rwanda siting model (registered test, KEEP)

**Verdict: KEEP.** Across all 30 districts of Rwanda, with each district hidden in turn, the siting model put
**73.1%** of the squares that hold a documented collection or processing point into the top 10% of their
own district. The best simple rule (the most buildings in the square) put **49.3%** there. The difference is
**+23.9 points, 95% interval 13.4 to 34.4**. The lower bound is above zero, which is the KEEP rule written
before the test was run.

This is the ML/GeoAI deliverable of EnaGIS Live. It is separate from the Canadian Phase 4 experiment, which
lost (KILL) and stays reported as it is ([validation](validation.md) §1).

| | |
|---|---|
| Protocol | [spec/phase4r-protocol.md](spec/phase4r-protocol.md) v1.1, SHA-256 `1a3bc8ca…`, frozen 10 Oct 2026 before any real cell was scored |
| Results | [audits/phase4r-evaluation.json](audits/phase4r-evaluation.json) (reproduced in Node); original browser run: [audits/phase4r-evaluation-browser-run.json](audits/phase4r-evaluation-browser-run.json) |
| Training table | [`data/rwanda/siting_cells.csv`](../data/rwanda/siting_cells.csv): 25,281 squares of 1 km, SHA-256 `664350e8…` |
| Label audit (after the test) | [audits/phase4r-label-audit.json](audits/phase4r-label-audit.json) |
| Code | `live/js/siting.js` (features, fit, evaluation), `live/tools/train-siting.cjs`, `live/tools/label-audit.cjs` |
| In the app | the **Likely sites** lens |

## 1. The question

Rwanda has no open register of collection centres, cold rooms, mills or markets. Open maps document only a
few of them. Can a model, using only what satellite-derived maps show everywhere (building footprints and
their sizes, roads, the grid, settlements), find the squares where such points are documented better than a
single obvious rule can?

## 2. Data

- **Unit:** 1 km × 1 km squares whose centre lies inside the district boundary. 25,281 squares in 30
  districts.
- **Features (11, fixed before the test):** buildings in the square and within about 2 km; roofs of 200 m²
  and 600 m² or more; largest roof; major-road length; minor roads and tracks; distance to a major road, to
  the mapped grid and to a town or village point; share of buildings in dense blocks. No feature uses
  facility locations, production statistics or any model output.
- **Sources:** Overture Maps release `2026-09-23.1` (building footprints from OpenStreetMap, Google Open
  Buildings and Microsoft, with areas computed from the footprint geometry; roads; power); OpenStreetMap via
  Overpass for facilities and settlement points; Overture places (confidence 0.5 or more). Gathered on
  10 October 2026 by `live/tools/harvest.js`, which runs the app's own gatherers.
- **Labels:** a square is positive if it holds a documented agricultural collection or processing point:
  mill, milk collection centre, cold store, coffee washing station, agricultural warehouse, agro-processing
  works, tea factory, market or cooperative. 134 positive squares in 27 districts.
- Unlabelled squares are **background, not proven absences**.

### Why the label includes markets and cooperatives (amendment v1.1)

The protocol first tests the narrower label: processing or storage only. Open maps document such a point in
only **44 squares in 20 districts**, below the gate of 60 squares in 6 districts. That label's result is
therefore **FEASIBILITY: not enough documented facilities to test**, and it is reported as such. The
amendment, decided on label counts alone before any model was scored, then makes the wider label primary.
Features, model, baselines, metric, interval, seed, gate and keep rule did not change.

## 3. Method

- **Model:** logistic regression with L2 penalty (λ = 1) on standardised features, balanced class weights,
  fitted by iteratively reweighted least squares. Written in plain JavaScript; it runs in the browser.
- **Baselines (no training):**
  - most buildings in the square;
  - most buildings within 2 km;
  - closest to a major road;
  - closest to a town or village;
  - closest to the mapped grid.
- **Validation:** leave one district out. Each district is scored by a model fitted on the other 29.
- **Metric:** pooled recall at the top 10%: the share of positive squares that land in the top 10% of their
  own district. Ties at the cut-off count fractionally.
- **Interval:** cluster bootstrap over the districts with a positive square, 2,000 draws, seed 20261011.
  The strongest baseline is recomputed in every draw.

## 4. Results

| Arm | Recall, top 10% | 95% interval | Recall, top 20% | AUC |
|---|---:|---|---:|---:|
| **Siting model** | **73.1%** | 61.5 – 83.9 | **88.1%** | **0.934** |
| Same model without roof sizes | 59.7% | 50.0 – 69.9 | 76.1% | 0.895 |
| Most buildings in the square | 49.3% | 39.1 – 59.8 | 62.7% | 0.854 |
| Most buildings within 2 km | 35.1% | 28.5 – 41.0 | 53.7% | 0.782 |
| Closest to a major road | 34.3% | 24.8 – 43.4 | 61.2% | 0.826 |
| Closest to a town or village | 29.1% | 20.3 – 40.8 | 48.5% | 0.761 |
| Closest to the mapped grid | 16.4% | 9.2 – 24.1 | 29.1% | 0.703 |

- **Margin over the best baseline:** +23.9 points at the top 10% (13.4 to 34.4); +25.4 points at the top
  20%.
- **What roof sizes add:** +13.4 points at the top 10% (5.1 to 21.4). Footprint areas are the part of the
  GeoAI input that a headcount does not have.
- **Per district:** of the 27 districts with a positive square, the model matched or beat the best baseline
  in 25. It was behind in Gicumbi (1 of 2 against 2 of 2) and Nyaruguru (2 of 4 against 3 of 4).
- **Coefficients, stable in sign across all 30 folds:**
  - largest roof: +2.49;
  - buildings in the square: +1.00;
  - roofs of 200 m² or more: +0.39;
  - minor roads: +0.47;
  - major road in the square: +0.32;
  - distance to a town centre: −0.47;
  - buildings within 2 km: −2.34.

In plain words: a busy square with one big roof, on a road, near a centre but not inside a dense city block.

## 5. After the test: label audit (post hoc, descriptive)

Reading every one of the 157 documented facilities by name found labels that are plainly wrong:

- a hotel (Hôtel des Mille Collines, where "Mille" matched the mill pattern);
- a football club ("Nyamata United F.C", where "amata", milk, matched);
- a café;
- a minimarket;
- a fruit shop;
- a phone-repair shop and a tile seller listed as warehouses;
- a government agency listed as a cooperative;
- a market's public toilet.

Seven positive squares depend only on such labels. A few more are doubtful, such as two general trading
companies and a handicraft cooperative. The classification rules now exclude all of these, with tests.

The registered verdict is not re-decided. The audit reruns the same protocol on corrected labels to show how
much the result depends on them:

| Scenario (descriptive) | Positive squares | Model | Best baseline | Margin, 95% interval |
|---|---:|---:|---:|---|
| Registered labels | 134 | 73.1% | 49.3% | +23.9 (13.4 to 34.4) |
| 7 clearly wrong squares removed | 127 | 73.2% | 49.6% | +23.6 (13.2 to 34.7) |
| Wrong and doubtful squares removed | 125 | 75.2% | 50.4% | +24.8 (15.7 to 34.7) |
| Clearly wrong removed, Kigali's 3 districts left out | 97 | 80.4% | 52.6% | +27.8 (15.7 to 39.4) |

The result does not hinge on the noisy labels, and it is not driven by the capital: without Kigali the
margin is larger and the gain from roof sizes rises to +20.6 points.

## 6. What this shows and what it does not

**It shows** that, in all 30 districts and under a rule fixed in advance, satellite-derived roof sizes,
roads and settlement structure point to where collection and processing points are documented, clearly
better than counting people.

**It does not show:**
- that a predicted square has a facility. The model learns where facilities are *documented*, which depends
  on who mapped what;
- that the 12 "look-alikes" per district (high score, big roof, nothing on record) are real facilities;
- anything about energy demand. The siting score never changes the energy ranking.

Labels come from open maps. They are incomplete and, as section 5 shows, sometimes wrong. The next
validation step is a phone check of the look-alikes: each confirmed or rejected square is new ground truth
for Rwanda.

## 7. Reproduce

```sh
node live/tools/train-siting.cjs data/rwanda/siting_cells.csv   # registered evaluation + frozen model
node live/tools/label-audit.cjs                                 # post-hoc audit; appends one line to the model file
```

Both are deterministic: the same table gives the same numbers. The evaluation first ran in the browser on
10 October with `live/js/siting.js` at the registered SHA-256 `a81a590d…`. Later edits to that file touch only
in-app display (`apply`, `reasons`). The Node rerun with the current file (`65cbf15d…`) gives identical
results to the sixth decimal.

To rebuild the table itself, open the app in a browser and run `live/tools/harvest.js`
(`EnaHarvest.run(EnaHarvest.RWANDA)`). It gathers live data, so a later Overture release or newly mapped
facilities will give a slightly different table: that is a new run, not this result.
