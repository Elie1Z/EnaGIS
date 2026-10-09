# Limitations and non-claims

## We never claim

1. That any site **needs** energy investment, has an energy gap, or lacks supply. Supply is
   undocumented, not absent.
2. That the kW or kWh values describe real elevators. They come from a temporary, unapproved
   scenario.
3. That the top 10 is ordered by urgency. Ranks 1–5 and 7–10 are exact ties.
4. That EnaGIS is validated in the field (n = 0) or in any region other than AB/SK (none).
5. That the ML siting model works. Its registered verdict is KILL.
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
| Time basis 2024–2025 | A visit today does not verify 2024 conditions | [phase-7-status](phase-7-status.md) |
| No seasonal access, visit window or peak/off-peak | Planners must check roads and timing themselves | app "How to get there" |
| Coarse world basemap (Natural Earth 1:110m), roads only for AB/SK | Navigation context only | [LICENSE-DATA](../LICENSE-DATA.md) |
| Translations cover the interface shell only (FR, RW) | Scientific text is English | app |
| No independent human rebuild yet | Reproducibility shown by CI and author clean-room only | [reproducibility](reproducibility.md) |
| Unapproved robustness diagnostic | Missing facilities inflate neighbours (+72% at 10% missing); not adopted | [proposal](proposals/sparse-data-stress-diagnostic.md) |

The in-app version is `app/limitations.html` ("Sources and limitations").
