# Phase 2 completion audit

Status: **COMPLETE — offline data spine and provenance**, 7 October 2026.

The raw → standardized input spine is implemented for the frozen Prairie benchmark. It preserves source observations, unknowns, units, precision, reporting vintages and licence boundaries. Phase 2 does not establish operating membership, validated energy parameters or a scientific shortlist.

## Deliverables

- Twenty-one pinned source/evidence files, 1,023,887,943 bytes in the complete local preparation; 16 permitted open inputs/evidence files support the open rebuild.
- Separate `acquire` and offline `ingest` commands; immutable raw-file SHA-256/size verification, versioned source adapters/configuration, stable facility/node crosswalk and typed outputs.
- Registry, candidates, original storage observations, shipping-point outcomes and crosswalks; full digital CCS/CAR/CD boundaries, actual production reporting geometries and spatial correspondence tables.
- ODbL highway-way database with preserved topology/tags and explicit incomplete-way/overlap audits; no inferred speeds or travel times.
- Private dated licensing reconciliation with independent extraction controls, quality reports and an output hash verifier.
- [Ingestion guide](spec/phase2-ingestion.md), [manifest](data/manifest.json), [licence audit](data/licence-audit.md), [source decision](decisions/0004-source-normalization.md) and [schema catalog](spec/phase2-data.schema.json).

## Real input findings

| Item | Result |
|---|---|
| Registry | 340 facilities/nodes: AB 89, SK 172, MB 79; 339 positive reported storage values, one reported zero retained with unresolved eligibility. 94 out-of-scope records explicitly retained as exclusions. |
| Identity | 340 maintained internal ID pairs; no exact duplicate identity tuple or exact coordinate pair in the selected source. Distinct facilities at a shared shipping point remain separate. |
| Deliveries | 184 shipping-point outcomes: 138 development, 46 transfer. 264 facilities link to 181 points; 76 facilities and three outcome points remain unmatched. Selected total: 23,783,747.932 tonnes after explicit kilotonne conversion, counted once per point. |
| Administrative geometry | 474 full digital CCS (AB 72, SK 297, MB 105), 27 CAR and 60 CD. Four CCS geometries require explicit `make_valid` repairs, with source/repaired areas and raw hashes retained. |
| Production geography | 37 actual AAFC SADR polygons: AB 8, SK 17, MB 12. They remain separate from 2021 CAR identifiers. Every selected reporting region has a geometry. |
| Production values | 80 raw all/durum components for 37 regions and three provincial controls, selected from 348,436 CSV rows. Twenty-two regional non-durum quantities are derivable; 15 remain UNKNOWN because a component is unpublished. Province controls stay separate. |
| Facility spatial joins | All 340 points find one candidate CCS, CAR and SADR. Two facilities have longitude/latitude source conflicts (four field discrepancies); their matches are `location_conflict`, requiring review. Left-record cardinality is conserved. |
| Geographic crosswalks | 474 CCS/CAR overlaps, no unmatched or multiple CAR candidates. 978 CCS/SADR overlaps; 339 CCS intersect multiple reporting polygons, including source-boundary/sliver differences. No area threshold or production weighting is applied. |
| Roads | AB 512,513, SK 254,384, MB 160,003 highway ways: 926,900 extract rows, 925,139 unique global IDs. There are 1,761 identical repeated IDs and no conflicting versions/geometries. Node references/tags remain available; merge those identical IDs once before graph construction. |
| Licensing chronology | Prairie primary counts 339 → 332 → 333 → 333 in August/November 2024 and February/May 2025. Parser counts and province storage totals match independent Table 9 controls. Disagreements, ambiguous matches and membership changes remain review records; no opening/closure dates are inferred. |

The machine-readable [data audit](audits/phase2-data-audit.json) is the authoritative final run record. These are source coverage counts, not confirmed operating facilities, training results or worldwide performance measures.

## Verification

- **88 pytest tests passed**, including the full synthetic path with networking forbidden, deterministic output hashes, immutable/corrupt input rejection, source/path/identity integrity, CRS and ambiguous spatial joins, unknown production, shipping-point non-duplication, road topology/tags and output integrity.
- Ruff lint and formatting passed; all eight Phase 1 smoke cases passed. CI uses the same fixture checks without national data.
- The standard-library road reader matched an independent decoder across **all 926,900 ways**: identical IDs, versions, ordered node IDs and tags; maximum coordinate difference approximately 1.42 × 10⁻¹⁴ degrees from floating-point representation. [Comparison record](audits/phase2-road-decoder-audit.json).
- Licensing extraction was checked against rendered pages and independent province row/mass controls, including changed November/February layouts.
- The final offline rebuild and indexed output verification are recorded in the machine audit. Raw/private/large derived files remain ignored by Git; source metadata and synthetic fixtures make the implementation inspectable.

## Remaining scientific gates

| Gate | Required before |
|---|---|
| Resolve two coordinate conflicts; review dated registry/licensing ambiguities and membership | Reliance on affected spatial records and scientific hindcast. A licensing non-match is not absence. |
| Review production missingness and finer-scale method; exclude province controls from origin sums | Conserved allocation. Partial known regional totals are not a complete mass budget. |
| Review road access/speed/scenario policy, merge global IDs and include needed relations/restrictions | Routing/accessibility. January 2024 extract coverage is not confirmed passability. |
| Approve harvest, residence, wheat/competing-crop occupancy, inventory and aeration parameters | Technical demand/supply/gap calculation. Storage tonnes are not fan power. |
| Preregister development blocks/metrics; preserve untouched Manitoba evaluation | Siting fitting and transfer claims. |
| Secure verification participation and protocol | Frozen phone/site verification and field-validation claims. |

These are subsequent execution gates, not a reopened pilot selection. Next is **Phase 3 — real pipeline and first shortlist**, subject to sourced, human-approved scientific configurations and the PRD fallback/unknown rules.
