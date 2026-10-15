# Limitations and non-claims

## Nyabihu hero demo

The frozen Rwanda hero adds reproducibility and reporting, not new ground truth. Its snapshot mixes
WorldPop 2020, NISR 2024 production / 2022 census, 2024 weather and Overture 2026-09-23.1; imagery can
be older than its release. [Newer references](hero-data-freshness.md) were identified but not downloaded,
by team decision. The [assumption sheet](hero-assumptions.md) marks unsupported exact ranges
ASSUMED; crop-loss rate is UNKNOWN/not modeled. These parameters remain scientifically unapproved.

The tornado is a descriptive linear allocation of sample variance with residual, not causal attribution
or a decomposition of the energy interval. No single tested endpoint moved a top-three site outside
the top ten; joint changes sometimes did. DESK-CHECKED/PHONE-CHECKED are workflow evidence, not field
validation. All real human counts initially remain zero. The phone rule establishes reported potato
activity above zero tonnes, not refrigeration or energy need. The presenting-laptop recording remains
a human acceptance item. The optional follow-on exports/cross-checks are below the plan's cut line
until those human acceptance items are complete.

## Suggested tools and the second site

- **XGBoost lost to the logistic model** on Rwanda (Phase 4X: −9.0 points). Its settings were fixed and not tuned; a
  tuned comparison is untested.
- **No image detector was trained.** Scouting found no open, licence-compatible sub-metre imagery over labelled
  facilities in seven candidate regions. This is a statement about open data on 10 October 2026, not about what
  detectors can do.
- **The Njombe test (Phase 4N, KILL)** concerns small grain mills from one 2021 survey of unknown completeness. It does
  not transfer to cold storage or to energy demand.
- **Second-site labels are OpenStreetMap records.** They are incomplete, and names written only in non-Latin scripts
  are not classified.

## We never claim

1. That any site **needs** energy investment, has an energy gap, or lacks supply. Supply is
   undocumented, not absent.
2. That the kW or kWh values describe real elevators. They come from a temporary, unapproved
   scenario.
3. That the top 10 is ordered by urgency. Ranks 1–5 and 7–10 are exact ties.
4. That EnaGIS is validated in the field (n = 0) or in any region other than AB/SK (none).
5. That a siting model finds facilities that exist. The Canadian model lost (KILL). The Rwandan model
   passed its registered test (KEEP), but only against facilities *documented* in open maps. Its
   look-alikes are leads to check, not findings.
6. That worldwide search means worldwide analysis. Outside the pilot every number is UNKNOWN.
7. That a high rank establishes demand, willingness to pay, grid access or viability.
8. That reported storage tonnes are electrical capacity, or that annual throughput equals peak
   demand.

## Known limitations

| Limitation | Effect | Evidence |
|---|---|---|
| Assignment is administrative equal share, not a road catchment | Rank reflects storage and region production, not real flows | [method](method.md), [phase8-method-report](phase8-method-report.md) |
| 9 of 25 production regions UNKNOWN (durum suppressed) | 72 of 261 nodes unranked; possible documentation bias | [evidence-ledger](evidence-ledger.md); [proposal](proposals/durum-residual-bounds.md) |
| No electrical capacity data | Gap UNKNOWN for all 261 | [evidence-ledger](evidence-ledger.md) |
| Registry is close to a census of primary elevators | Weak test of finding *undocumented* facilities in sparse settings | [phase-4-completion](phase-4-completion.md) |
| All locations P2 (named place) | Do not navigate to the exact pin without checking | registry |
| Only 7 positive spatial blocks | Wide intervals in the siting test | [validation](validation.md) |
| Rwanda labels come from open maps: incomplete, and 7 of 134 positive squares were plainly wrong (a hotel, a football club…) | Label noise; the result holds without them | [phase4r-results](phase4r-results.md) §5 |
| Rwanda district production is ESTIMATED (Season A shares scaled to 2024 national totals; 3 districts imputed) | Even spread inside a district | `data/rwanda/district_production_2024.csv` |
| Time basis 2024–2025 | A visit today does not verify 2024 conditions | [phase-7-status](phase-7-status.md) |
| No seasonal access, visit window or peak/off-peak | Planners must check roads and timing themselves | app "How to get there" |
| Coarse world basemap (Natural Earth 1:110m), roads only for AB/SK | Navigation context only | [LICENSE-DATA](../LICENSE-DATA.md) |
| Translations cover the interface shell only (FR, RW) | Scientific text is English | app |
| No independent human rebuild yet | Reproducibility shown by CI and author clean-room only | [reproducibility](reproducibility.md) |
| Unapproved robustness diagnostic | Missing facilities inflate neighbours (+72% at 10% missing); not adopted | [proposal](proposals/sparse-data-stress-diagnostic.md) |

The in-app version is `app/limitations.html` ("Sources and limitations").
