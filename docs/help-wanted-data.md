# Help wanted: data

Every UNKNOWN in EnaGIS is an open invitation. If you hold, or can point to, any of the data
below, open a **Data wanted** issue (template provided) or a pull request adding a manifest
entry. We need the source, date, licence and how it was collected. We never need personal data
in the public repository.

| # | Data wanted | Closes | Typical holder | Licence we can use | Format |
|---|---|---|---|---|---|
| 1 | Aeration fan count, motor nameplate kW and fan type per elevator (or per elevator class) | Electrical requirement check; 261 UNKNOWN gaps | Elevator operators; PAMI equipment reports | Any open licence, or aggregate-only permission | CSV with source and date |
| 2 | Electrical service capacity (kVA) or utility connection class per site | Supply state, gap sign | SaskPower; FortisAlberta; ATCO | Open or aggregate | CSV |
| 3 | Metered aeration electricity for a few sites in one season | Calibrate kW and kWh ranges | Operators, utilities, researchers | Aggregate-only fine | kWh per week |
| 4 | Typical wheat residence time and occupancy at primary elevators | Inventory parameter | Industry studies, CGC, operators | Citable publication | Value + range + source |
| 5 | Airflow and static-pressure design values for commercial bins | Airflow / pressure parameters | ASABE standards, PAMI, extension services | Citable | Value + range |
| 6 | Unsuppressed regional durum production, or approval of the residual-bound rule | 72 nodes UNKNOWN | Statistics Canada | StatCan Open Licence | Table |
| 7 | Confirmed coordinates for Rycroft (G3) and Woodrow (Canada Direct Processing) | 2 location conflicts | Operators; AAFC Atlas | Open | lon/lat + date |
| 8 | Spring road-ban and weight-restriction schedules | Seasonal access, visit window | Sask. Ministry of Highways; Alberta Transportation | Open data portals | GeoJSON / dates |
| 9 | Facility-level receipts or throughput | Hindcast at facility level | Operators; CGC (restricted) | Aggregate permission | t per crop year |
| 10 | A field partner willing to phone-check a frozen sample (n ≥ 12) | Field verification (n = 0 today) | Energy programmes, cooperatives | Private, aggregates published | [field form](phase7-field-form.md) |
| 11 | An energy-access region with a facility registry and production statistics | Transfer evaluation | Ministries, programmes, HDX | Open | See [scope-and-transfer](scope-and-transfer.md) |
| 12 | Independent rebuild by someone outside the team | Reproducibility claim | Anyone | — | Report in an issue |

Background on each gap: [evidence-ledger.md](evidence-ledger.md).
