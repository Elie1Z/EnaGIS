# 0003 — First benchmark and Phase 0 scope lock

Status: **frozen development scope**, 7 October 2026. Authority: the user permits data-driven selection anywhere in the world and asked to finish Phase 0. This resolves the location, commodity and service choices for implementation. Changes require a new decision record with a concrete reason.

## Selected scope

| Item | Frozen choice |
|---|---|
| Purpose | Develop and evaluate EnaGIS agricultural energy screening on a data-rich reference case, then measure geographic transfer. |
| Country / footprint | Canada; Alberta and Saskatchewan for development; Manitoba reserved for geographic transfer evaluation. |
| Commodity | Non-durum wheat: the CGC delivery category `Wheat`. `Amber Durum` is a separate published category and is excluded from this benchmark. |
| Value-chain step | Post-harvest aggregation and storage at licensed primary grain elevators. |
| Stationary energy service | Electricity for ambient-air aeration of stored wheat. It is a modeled technical storage service; installed fans and current electricity use require separate evidence. |
| Node type | A primary elevator with documented physical storage. Multiple elevators at a shipping point remain distinct facilities linked to one aggregation group. |
| Node eligibility | Retain unknown capacity as unknown; do not discard it. Documented transit-only points and grain dealers without a storage site are logistics-only. Process and terminal elevators are outside this first benchmark. |
| Source study period | Retrospective 2024 harvest / 2024–2025 crop-year benchmark, using the 2024 registry and the corresponding delivery slice. Check within-year openings/closures before hindcast. This is not a pre-harvest forecast. |
| Siting unit | 2021 Census Consolidated Subdivision (CCS), using full digital boundaries and stable geographic identifiers. Production is sourced at Small Area Data Region level with an explicit boundary crosswalk. |
| Spatial validation | Group training units by 2021 Census Agricultural Region; require at least six usable development blocks per the PRD. Manitoba labels/outcomes stay out of fitting and selection. Block crosswalks and split details are preregistered in Phase 4. |
| Registry / capacity | AAFC 2024 grain-elevator GeoJSON, reconciled with CGC historical licensing data. Capacity is storage mass in tonnes. |
| Production | Statistics Canada table 32-10-0002-01, 2024 non-durum wheat production. AAFC Annual Crop Inventory 2024 is the fine-scale crop-location proxy, subject to its classification audit. |
| Hindcast | CGC 2024–2025 `Wheat` deliveries, evaluated by province + shipping point. Never duplicate one shipping point's volume across its elevators. |
| Verification route | Team-led contact with CGC Statistics and Business Information / Licensing and Security and public elevator offices, followed by the frozen phone/site verification protocol. Published contacts are leads, not commitments. |
| Transfer claim | Measured performance on Manitoba under the same commodity/service contract. Other countries enter through adapters, local data and a new transfer evaluation. |

## Selection evidence and fallback

The [source audit](../audits/phase0-canada-sources.json) found 340 Prairie primary-elevator records in the 2024 spatial source: Alberta 89, Saskatchewan 172 and Manitoba 79. Of those records, 339 have positive reported storage capacity. The selected delivery slice has 184 shipping points; exact province + normalized station matching connects 264 primary-elevator records to 181 of those points. These are feasibility counts before registry integrity checks, not verified operating facilities.

This demonstrates strong location and storage-capacity coverage and a concrete hindcast source. It does **not** demonstrate all commodity gates: a committed verification contact, site-level aeration equipment and validated energy/value assumptions are unresolved. No reviewed candidate has been shown to pass every gate. Use the PRD §6 best-candidate fallback rather than label those missing gates as passed. Freeze this reference benchmark to enable development and report siting as a documented feasibility experiment while those gates remain unpassed. Audited positives/blocks must still meet the experiment's requirements or its failure is reported. Field screening claims depend on the required validation.

## Service definition and unit boundary

Aeration is selected because it is a stationary storage-energy service with a physical model and published wheat-storage guidance. The service model uses stored inventory, required airflow, grain/duct resistance, fan and motor efficiency, and operating cycles. Electricity per cycle follows power multiplied by run time, with explicitly modeled auxiliary load. Peak electrical power comes from the simultaneously active fan/motor configuration, not period energy divided by hours in a day.

Storage tonnes are not annual handling tonnes, airflow or kW. Daily/seasonal inventory needs a sourced residence-time and occupancy scenario. Shared storage is used by other crops too; wheat cannot receive all reported capacity by default. Known storage capacity does not imply known aeration capability. Keep separate capacity dimensions and compare requirement only with compatible documented service capacity.

Reference sources are [wheat storage guidance](https://extension.umn.edu/agriculture/crop-production/small-grains/storing-wheat-and-barley) and [fan selection / wheat airflow resistance](https://extension.umn.edu/agriculture/crop-production/corn/selecting-fans-and-determining-airflow-for-grain-bins). Their farm-bin guidance must not be blindly extrapolated to commercial elevator geometry. Numeric parameters remain human-reviewed, sourced configuration; Phase 0 does not invent their ranges.

## Frozen and human-owned decisions

The footprint, commodity, node class, stationary service, source period and geographic transfer footprint above are frozen for the first implementation. The core Python/static-map architecture remains the PRD stack; dependency versions are pinned in Phase 1.

Humans still own parameter distributions and applicability, meaningful gap definitions, uncertainty thresholds, the verification protocol, source interpretation and scientific conclusions. Those values are not needed to define Phase 1 contracts. Contracts must represent unresolved values explicitly, and real calculations requiring them must stop with a clear missing-parameter result.

Numeric model thresholds and calibrated energy assumptions will not be chosen from the Manitoba results. If local adaptation is tested, freeze and report the untouched transfer result first; use separate adaptation/evaluation partitions afterward.

## Public contact leads

- [CGC research and data contacts](https://www.grainscanada.gc.ca/en/about-us/contact-us/research-data.html) lists Statistics and Business Information and Licensing and Security for the relevant data.
- [NDSU's energy contact page](https://www.ag.ndsu.edu/energy/aboutus) identifies Kenneth Hellevang as a grain drying, handling and storage specialist: a technical-review lead.
- [G3's Melfort opening announcement](https://www.g3.ca/en/news/G3s-newest-grain-elevator-in-Saskatchewan-is-now-officially-open), dated 10 August 2023, names Greg Claypool as its then General Manager: a dated operator lead whose current role and availability must be checked through the company.

No contact has been approached and no participation is claimed. A public lead is not a committed verifier; this remaining verification gate must be resolved by the data lead before claiming field validation.
