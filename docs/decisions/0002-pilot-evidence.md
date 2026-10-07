# Global pilot evidence update

Audit date: 7 October 2026. Geographic selection is authorized by decision 0002 and the development benchmark is now frozen in [decision 0003](0003-benchmark-lock.md). This packet adds an international candidate to the original Rwanda audit; it does not claim an exhaustive comparison of every country.

## Historical source audit used for the scope lock

The [AAFC 2024 catalogue](https://open.canada.ca/data/en/dataset/3561d689-2b5b-4cf9-bc68-d7ed0dbacd1b) provides a [2024 GeoJSON](https://agriculture.canada.ca/atlas/data_donnees/cgcElevators/data_donnees/geoJSON/cgcElevators2024.geojson) with an explicit elevator class. It contains 434 point records overall; the Prairie primary-elevator subset has 340 records (AB 89, SK 172, MB 79), with 339 positive reported storage-capacity values.

The official [2024/25 delivery CSV](https://www.grainscanada.gc.ca/en/grain-research/statistics/grain-deliveries/2024-25/gdpp-2024-25-en.csv) actually contains crop years 2006–2007 through 2024–2025, so the year must be filtered explicitly. Its grain taxonomy separates `Wheat` from `Amber Durum`. The selected `Wheat`, `2024-2025`, AB/SK/MB slice contains 184 distinct shipping points. Exact province + trimmed uppercase station matching covers 181 points and 264 primary-elevator records. Many facilities can share one point's outcome: these are coverage counts, not per-facility throughput labels. The [saved audit](../audits/phase0-canada-sources.json) records source fingerprints and counts; raw snapshots still need to be pinned in Phase 2.

This establishes a stronger location/capacity/hindcast foundation than the reviewed Rwanda source leads. Energy applicability/value and committed verification remain unpassed gates; decision 0003 explicitly invokes the PRD fallback.

## Leading candidate: Canadian Prairies grain elevators

The [AAFC 2026 grain-elevator dataset](https://open.canada.ca/data/en/dataset/1f7684ff-ee15-4c6f-b38c-6830a21898eb) provides GeoJSON under the Open Government Licence - Canada. The published [Q2 2026 GeoJSON](https://agriculture.canada.ca/atlas/data_donnees/cgcElevators/data_donnees/geoJSON/cgcElevatorsQ22026.geojson) was inspected on the audit date and contains **427 point features**, with **425 positive storage-capacity values**. The Prairie provinces contain 387 records: Saskatchewan 195, Alberta 99 and Manitoba 93. These are raw record counts before licence-class, service, duplication or precision checks. Its fields include station, province, licensee, storage capacity in tonnes, latitude and longitude. The catalogue says positions are placed at actual facilities where possible, rather than station centroids; record-level precision must still be audited.

[Canadian Grain Commission elevator reports](https://www.grainscanada.gc.ca/en/grain-research/statistics/grain-elevators/reports/) publish licensed elevator types and storage capacity. [Grain Deliveries at Prairie Points](https://www.grainscanada.gc.ca/en/grain-research/statistics/grain-deliveries/) publishes crop-year deliveries by shipping point and province. Shipping-point deliveries are an aggregation-level observation; where several elevators share a point, do not duplicate its volume or claim per-facility truth.

[Statistics Canada table 32-10-0002-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210000201) provides crop area, yield and production by Small Area Data Region. It is a production-source lead; periods, suppression, boundary versions and compatible crop definitions need inspection before allocation.

| Gate | Canadian candidate | Rwanda coffee comparison |
|---|---|---|
| Geolocated facilities | 427 mapped features identified; filter licence class and service eligibility before counting usable training positives. | 207 historical points; 84 Western Province records, with 2006–2011 survey labels. |
| Capacity / throughput | Storage-capacity field present; official shipping-point delivery series available. Join coverage and comparable dates need audit. | Per-station capacity/throughput unresolved in reviewed sources. |
| Reuse licence | GeoJSON catalogue states Open Government Licence - Canada; check each additional source's terms. | Geodata/NAEB redistribution licence unresolved. |
| Production | Official subprovincial crop-production series identified. | Sector tree-count proxy identified; dated cherry-volume conversion unresolved. |
| Stationary service | Elevators handle/store grain, but drying/cleaning/processing equipment and energy service must be verified per class/site. | Coffee wet processing is clear in principle; energy coefficients unresolved. |
| Verification | Official data contacts and companies exist; no named committed field/phone contact established. | Local outreach may be easier for the Kigali team, but no committed contact recorded. |
| Energy / value | Source intensities, equipment profiles, energy carriers, tariff and product-value basis still required. | Same unresolved gate. |

## Important unit and domain limits

Storage tonnes measure inventory capacity, not tonnes per day, electricity kW or daily kWh. Shared multi-grain storage cannot be assigned in full to a wheat-only model without an explicit occupancy/allocation scenario. Drying is not assumed from an elevator label. Thermal fuel and electricity must remain distinct if drying is selected.

Use historical facility/capacity snapshots matching the delivery crop year for hindcast; the 2026 inventory cannot silently stand in for a 2024/25 network. Hold delivery outcomes out of the siting feature set, and do not use future registry information to predict historical siting.

Canadian commercial elevators can test facility and throughput methodology, but do not establish productive-use-energy gaps in Rwanda or every other country. Target-region evidence and validation are required. Rwanda remains a future deployment candidate if its data and verification pathway become adequate; changing to coffee would be a separate service/value-chain adaptation, not a direct test of wheat-model geographic transfer.

## Next audit

The grain, service, footprint, source year and hold-out are now frozen in decision 0003. Phase 2 validates the source records and crosswalks; Phase 4 preregisters the spatial blocks and experiment; human reviewers source the service parameters and secure verification participation. The [completion audit](../phase-0-completion.md) assigns these execution gates.
