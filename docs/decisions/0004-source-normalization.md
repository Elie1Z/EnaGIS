# 0004 — Source normalization and reporting geography

Status: **implemented data interface**, 7 October 2026. The user authorized Phase 2. Decision 0003's country, commodity, node class, service and transfer footprint remain frozen. This decision records concrete source differences found during ingestion; it supplies no scientific parameters.

## Production category and geography

The pinned [Statistics Canada table 32-10-0002-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210000201) has `Wheat, all` and `Wheat, durum`, with no direct non-durum category. The adapter derives non-durum tonnes by exact subtraction **only when both components are published**. Components, units, vectors, revisions and status symbols remain in `production_lineage.json`. Derived values are ESTIMATED. Blank or flagged components produce UNKNOWN, never zero or all-wheat substitution. The table's embedded legend defines `F` as too unreliable for publication.

The table's Saskatchewan geography names refer to 2016 census divisions; region 16 combines divisions 16 and 18. Its reporting units cannot be joined to 2021 CAR using a code with the same spelling. Use the corresponding published 2024 SADR geometries in the [AAFC field-crop production source](https://open.canada.ca/data/en/dataset/ae9c1230-e2dc-4155-a68b-6d521f57baaa). That source's `CARUID` is retained as a **SADR source code**, with a distinct geography type and `aafc-2024-reporting` vintage. The constructed source geographic ID is explicitly an EnaGIS namespace, not an invented Statistics Canada DGUID.

The 2021 CCS/CAR/CD layers are the [full digital boundaries](https://geo.statcan.gc.ca/geo_wa/rest/services/2021/Digital_boundary_files/MapServer), not cartographic or generalized substitutes. The pipeline publishes every positive-area CCS/SADR overlap and an independent CCS/CAR crosswalk. These are geometry correspondences, not production allocation weights. No dominant-overlap threshold, crop proxy or finer production allocation is chosen here. Province totals stay in a separate control table and cannot be added to reporting-region origins.

## Registry and temporal status

The AAFC 2024 layer establishes published primary-elevator records and reported storage. Its year has no exact licensing date or per-record surveyed accuracy guarantee. `2024-01-01` is a year anchor, recorded beside `source_date_precision=year`; P2 is a conservative named-place precision class. The source geometry and rounded coordinate attributes are both preserved. Conflicts retain candidate boundary matches but their status is `location_conflict`, requiring review before spatial modeling.

The versioned identity crosswalk assigns internal facility/node IDs once, independently of OBJECTID and year. Later operator or coordinate changes require explicit crosswalk review, rather than automatic ID replacement. Multiple elevators at a station remain distinct; only exact duplicate identities are rejected. Positive reported storage makes a technical service candidate, without proving operating status, wheat occupancy or installed fans. A reported zero remains a source observation with unresolved eligibility.

Four CGC licensing lists span August/November 2024 and February/May 2025. Positioned PDF text is checked against independent Table 9 row and storage totals. The private reconciliation uses conservative province/station/operator keys; unresolved multiple records and dated disagreements remain explicit. Appearing or disappearing from a list does not establish an opening or closure date.

## Source rights and runtime

AAFC/digital boundaries and the CGC delivery open-data series retain Open Government Licence attribution; Statistics Canada tables retain its Open Licence. Generic [CGC reproduction terms](https://www.grainscanada.gc.ca/en/terms.html) permit non-commercial reproduction and do not give a general commercial redistribution permission for the licensing PDFs. Those source rows stay in ignored private audit outputs and never populate the public registry. `--skip-licensing` provides the complete open data spine independently of that audit. OSM road derivatives remain a separate ODbL database with attribution.

Acquisition is a separate command. Ingestion reads and checks pinned local files with PROJ networking disabled. Raw files are never normalized in place. The standard-library PBF reader supports the pinned snapshot encoding, preserves every highway way and reports incomplete ways. It is independently compared with a second decoder; it does not provide speeds, travel times or a routing graph. Relations remain available in the raw PBF for Phase 3's routing implementation.

## Execution gates

Resolve coordinate conflicts, registry/licensing ambiguities, temporal membership and production missingness before relying on affected records. Review scientific disaggregation, occupancy, inventory, routing and aeration configurations in their assigned phases. Keep Manitoba untouched for fitting and model selection. This normalization establishes a reusable data spine; it establishes no field validation or worldwide accuracy.
