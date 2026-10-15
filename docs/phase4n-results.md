# Phase 4N results: can footprints find grain mills in Njombe, Tanzania? (second site, KILL)

**Verdict: KILL.** In each held-out district council, the top 1% of building footprints contains these shares of the
surveyed grain mills:

| Ranking | Share of mills in the top 1% |
|---|---:|
| Logistic footprint model | **5.7%** |
| XGBoost | 5.8% |
| Best simple rule, closest to a major road | 4.1% |
| Largest roof first | 2.8% |

The logistic model's margin over the road rule is +1.6 points, with a 95% interval of −0.3 to 3.4. That interval
includes zero, so the rule fixed in advance says KILL. XGBoost is no better than logistic (+0.1, −1.8 to 2.0). The
brief's "largest roofs first" rule is the weakest signal, because grain mills are small buildings.

This is the second-site test that scouting allowed (track C1). It is reported separately from Rwanda and changes no
Rwanda or Canada result.

| | |
|---|---|
| Protocol | [spec/phase4n-protocol.md](spec/phase4n-protocol.md), SHA-256 `d3a9cc02…` ([hash file](spec/phase4n-protocol.sha256)), frozen 11 Oct 2026 04:46 UTC, before any footprint was downloaded or scored |
| Results | [audits/phase4n-evaluation.json](audits/phase4n-evaluation.json) |
| Why Njombe | [second-site-scouting.md](second-site-scouting.md): the only one of seven candidate regions with ≥ 300 documented processing points in ≥ 6 sub-districts |
| Code | `research/phase4n/gather.mjs` (data), `research/phase4n/run.py` (evaluation, shares Phase 4X metric code), `make research-njombe` |
| Data | Overture Maps buildings and roads, release 2026-09-23.1 (3,874 tiles, 65.7 MB, approved by Elie up to 200 MB); OpenStreetMap settlements and power; mills from OpenStreetMap, 881 of 882 tagged "WFP Field Survey 2021, OMDTZ" |
| Run | 95 s on CPU, no GPU; deterministic (two runs identical) |

## 1. Setup

- **Units:** 673,866 Overture building footprints inside Njombe Region (21,244 km²). 307 footprints fall in no
  council polygon and are excluded.
- **Labels:** each of the 882 mills was matched to the nearest footprint centre within 30 m. 830 matched (median
  8.3 m) and 52 did not. That gives 830 positive footprints in all 6 councils (gate: ≥ 300 in ≥ 6, met).
- **Features (11, fixed in advance, label-free):**
  - area, perimeter, elongation and rectangularity;
  - buildings within 200 m and within 1 km;
  - the footprint's area relative to the largest building within 200 m;
  - distances to a major road, any road, a settlement point and the mapped grid.

  All are computed in UTM 36S (EPSG:32736).
- **Arms:**
  - logistic regression, the primary model, as in Rwanda;
  - XGBoost, with the Phase 4X settings and the hist method;
  - three rules with no training: largest roof, most neighbours, closest to a major road.
- **Test:** leave one council out (6 folds), recall at the top 1% of each held-out council. The paired cluster bootstrap
  uses 2,000 draws over 145 blocks of 10 km that hold a mill, seed 20261015.

## 2. Results (ESTIMATED: held-out recall of surveyed mills)

| Arm | Top 1% | 95% interval | Top 5% | AUC |
|---|---:|---|---:|---:|
| Logistic footprint model | **5.7%** | 3.8 – 7.7 | 19.6% | 0.741 |
| XGBoost | 5.8% | 4.0 – 7.7 | 20.7% | 0.756 |
| Closest to a major road (best rule) | 4.1% | 2.7 – 5.7 | 18.4% | 0.637 |
| Largest roof first | 2.8% | 1.7 – 4.0 | 12.0% | 0.628 |
| Most buildings within 200 m | 2.0% | 0.8 – 3.4 | 10.2% | 0.681 |

| Decision | Value | Rule | Verdict |
|---|---|---|---|
| Logistic − best rule, top 1% | +1.6 points (−0.3 to 3.4) | lower bound > 0 | **KILL** |
| XGBoost − best rule (descriptive) | +1.7 points (0.0 to 3.3) | lower bound > 0 | not met (bound exactly 0) |
| XGBoost − logistic | +0.1 points (−1.8 to 2.0) | ≥ +3 and interval > 0 | **NOT BETTER** |

- **Per council**, logistic found 5 to 11 mills in the top 1% (Makete 6 of 111, Ludewa 7 of 154, Njombe 8 of 140,
  Wanging'ombe 10 of 153, Makambako 5 of 119, Njombe Municipal 11 of 153).
- **Ranking is the problem, not calibration.** Calibration is fine for both models (ECE 0.0002 and 0.0003). AUC near
  0.75 means footprints carry some signal, but far too little to pick out a mill among a hundred thousand buildings.

## 3. Leakage check (descriptive)

- **Geometry sources:** mill footprints come from OpenStreetMap tracing a little more often than other buildings (63%
  against 55%). The rest come from Google Open Buildings (33% against 36%) and Microsoft (4% against 8%).
- **Machine-learning footprints only** (300,623 footprints, 307 mills): logistic 6.5% equals the road rule 6.5%
  (margin 0.0, −3.1 to 3.0), and XGBoost reaches 7.2%. The small advantage on all footprints does not survive on
  footprints whose mapping process is independent of the survey.

## 4. What this means

- **For the brief's suggested tools:** we ran XGBoost and a footprint classifier at the one candidate site where the
  data allowed it, under a rule fixed before scoring. Neither beats "near a major road" with confidence.
- **No image detector could be trained here.** OpenAerialMap has one 0.2 m image in the region, and it covers none of
  the mills (scouting audit).
- **Why Rwanda differs:** in Rwanda the label is collection and processing points, including markets, cooperatives
  and large stores, scored on 1 km squares. There, large roofs carry the signal (Phase 4R, KEEP). In Njombe the label
  is small village grain mills scored one building at a time, and roof size does not single them out.

## 5. Limits

- **Survey completeness unknown.** The labels come from one 2021 survey. Unsurveyed mills sit in the background and
  lower measured recall.
- **Unmatched mills.** 52 mills had no footprint within 30 m.
- **Sparse grid mapping.** The region has 5 mapped power-line ways (1,311 points), so the grid distance carries little
  information.
- **Mills are not cold stores.** Nothing here transfers to cold storage or to energy demand.
- **No field verification** (n = 0).

## 6. Reproduce

```sh
make research-njombe   # gather (cached after the first run) + evaluate; ~2 minutes once data are cached
```

The input tables stay in the gitignored `outputs/phase4n/` folder, because they contain the surveyed mill points.
Their SHA-256 values are recorded in the audit file. No mill names or phone numbers are published.
