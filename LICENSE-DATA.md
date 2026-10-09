# Data and content licences

The MIT [LICENSE](LICENSE) covers EnaGIS code, configuration and documentation written for this
project. It matches the licence already recorded for EnaGIS-authored scenario values in
`configs/scenarios/phase3-engineering-v1.json`. **Data keeps its own licence.** The MIT licence
does not relicense any source data or its derivatives.

| Material in this repository or its outputs | Licence | Redistributed here? |
|---|---|---|
| AAFC grain elevators 2024, AAFC field-crop production, StatCan census boundaries (CCS, CAR, CD, CSD) | [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada) | Derived evidence in `app/evidence/`, `demo/evidence/` |
| Statistics Canada tables 32-10-0002-01 and 98-10-0002-01 | [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/reference/licence) | Derived values only |
| CGC deliveries at prairie points 2024–2025 | Open Government Licence – Canada | Derived evidence |
| **OpenStreetMap-derived roads** (`app/roads.geojson`, `demo/roads.geojson`, road features) | **[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/)**, © OpenStreetMap contributors | Yes. Any public use of these derivatives must keep attribution and share-alike |
| CGC licensed-elevator PDFs (2024–2025) | CGC non-commercial reproduction terms (not an open licence) | **No.** Restricted; used only for private audit rows and kept out of public outputs |
| Natural Earth countries and populated places | Public domain | Yes (`web/assets/`) |
| Inter and Fraunces fonts | SIL Open Font License 1.1 (`app/assets/OFL-*.txt`) | Yes |
| MapLibre GL JS | BSD-3-Clause (`app/vendor/LICENSE-*.txt`) | Yes |
| EnaGIS wordmark (`web/assets/brand/`) | Project brand; the code licence does not grant trademark rights | Yes |

Per-snapshot licence, URL, retrieval date and SHA-256 are in [docs/data/manifest.json](docs/data/manifest.json),
[docs/data/phase4-manifest.json](docs/data/phase4-manifest.json) and the readable
[data catalogue](docs/data-catalogue.md). The licence decisions are explained in
[docs/data/licence-audit.md](docs/data/licence-audit.md). Code notices for referenced third-party
schemas are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
