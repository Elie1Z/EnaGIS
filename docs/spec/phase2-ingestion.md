# Phase 2 offline ingestion

## Preparation and one-command rebuild

From the repository root, install the committed Python 3.12 lockfile once:

```sh
uv sync --locked --cache-dir .uv-cache
```

Prepare the pinned **open** inputs with internet access:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis acquire --skip-licensing
```

`uv --offline` prevents package resolution from using the network. The explicit `acquire` command downloads source files. The manifest contains 21 source fingerprints, of which 16 are permitted open inputs/evidence files. The full preparation including the optional non-commercial licensing audit downloads approximately 1.024 GB. Existing raw files must match SHA-256; changed bytes at mutable publisher URLs are rejected. Preserve the original pinned files for judging or offline reproduction. Availability of a future identical download is not guaranteed by a mutable URL.

Transform local raw files into the complete public input spine:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis ingest --skip-licensing
```

This command performs no API calls. It validates source sizes/hashes, configuration, stable IDs, units, geometry, references, row counts and spatial joins, then writes `data/processed/phase2/index.json` last. Missing or modified inputs fail explicitly. `make acquire`, `make ingest` and `make verify-data` are equivalent shortcuts where Make is installed. Windows PowerShell uses the same uv commands.

For the separate **non-commercial local licensing audit**, omit `--skip-licensing` from both commands. Company rows and unresolved source matches are written only to `data/validation_private/phase2/licensing_reconciliation.json`. The public data spine uses the open AAFC registry in either mode. Public audit summaries do not grant rights to redistribute the restricted reports or derived company records commercially.

Check all indexed output hashes, typed records, row counts and evidence source chains:

```sh
uv run --offline --locked --cache-dir .uv-cache python -m enagis verify-data data/processed/phase2
```

## Configuration and provenance

- [manifest](../data/manifest.json): publisher URL, access/effective dates, date precision, SHA-256, byte count, licence, redistribution, attribution, processing and output paths. Metadata/licence evidence is pinned alongside data.
- [region adapter configuration](../../configs/regions/ca-prairies.json): field mapping, development/transfer footprint, source IDs, conservative coordinate envelopes, coordinate attribute comparison tolerance, precision policy and crosswalk paths. Envelopes/tolerance are engineering checks; they are not distance, routing or scientific thresholds.
- [stable identities](../../data/manual/facility-identities-v1.json): maintained facility/node IDs. The initial UUID5 key contains province, station, operator, railway and reported coordinates, without OBJECTID or source year. Future source changes require a reviewed mapping update; the pipeline cannot silently generate replacement IDs.
- [licensing parser controls](../data/licensing-parser-controls.json): independent Table 9 counts/storage totals, used solely to check extraction quality.
- Every table is an `Artifact[Row]` with the shared Phase 1 metadata. Input hashes, configuration/crosswalk/control hash, adapter code hash and lockfile hash identify the run. Seed is null because ingestion has no random operation. Licensing execution mode is recorded separately and changes the run ID.

The [schema catalog](phase2-data.schema.json) defines additive input contracts. The Phase 1 scenario `Bundle` is intentionally not used: input production has not yet been allocated. `configs/pilot-scope.json` remains scope metadata.

## Output contracts

| Output | Intended consumer and meaning |
|---|---|
| `registry.json`, `nodes.json`, `capacities.json` | Stable facilities and documented storage candidates; original all-commodity storage tonnes. Capacity metadata uses `wheat_storage`, without granting wheat exclusive use or implying aeration kW. |
| `registry_source_rows.json`, `registry_excluded.json` | Original properties/geometry, year precision, conservative location class and explicit scope exclusions. No source rows silently discarded. |
| `outcomes_development.json`, `outcomes_transfer.json`, `shipping_links.json`, `outcome_source_rows.json` | One CGC Wheat outcome per province/shipping point for 2024–2025. Original kilotonnes and exact tonne conversion. Multiple elevators may link to one point; no volume assigned to an individual elevator. Outcomes remain outside siting features. |
| `boundaries_ccs.json`, `boundaries_car.json`, `boundaries_cd.json` | Full 2021 digital polygons in EPSG:3347; published DGUID/code/name, source geometry hash, explicit repair status. |
| `boundaries_sadr.json`, `sadr_source_rows.json` | Exact 2024 AAFC reporting geometries, transformed EPSG:3857 → 3347 with longitude/latitude axis handling and no ballpark operation. Mixed reporting vintage is explicit. |
| `boundaries_province_controls.json` | CD union geometries for province control records; derived geometry is INFERRED, source DGUID retained. |
| `production.json`, `production_province_controls.json`, `production_lineage.json` | Reporting-region non-durum tonnes or UNKNOWN, raw all/durum components/flags and exact arithmetic. Province controls are separate. No disaggregation or proxy weights. |
| `facility_spatial_matches.json` | One left-join result per facility and geography type. All candidate keys and unmatched/ambiguous/province/location-conflict states retained. |
| `ccs_to_car_overlap.json`, `ccs_to_sadr_overlap.json` | Positive polygon intersection area in m² and fraction of the full digital CCS area, including water. These are not crop areas, production weights or silently selected block assignments. |
| `roads_AB/SK/MB.jsonl`, corresponding `.rejected.jsonl`, `roads_index.json` | ODbL highway-way source database: global way IDs, version, ordered node IDs, EPSG:4326 coordinates and complete tags. The temporary SQLite node cache is removed after parsing. No drivable-class filtering, speeds or travel times are assumed. |
| `road_extract_overlap_audit.json` | Cross-extract global IDs: identical duplicates can later be merged once; conflicting geometries/versions require review. |
| `quality_issues.json`, `join_audits.json`, `data_audit.json`, `index.json` | Explicit exceptions, lossless left-record counts, aggregate coverage, licences and reusable file hashes. An absent index means a build is incomplete. |

Period metadata spans the relevant sources; production tables use calendar 2024 and outcome tables August 2024–July 2025. Original quantity periods remain explicit. Annual mass is not instantaneous inventory, daily flow or electrical power.

## Spatial and temporal limitations

Boundary repair retains a hash of the source geometry and reports source/repaired area. Original polygons remain recoverable from raw snapshots. EPSG:3347 areas describe geometric overlap only. Canadian projection and source adapters are not universal region parameters.

Published coordinates are representative source positions, with no surveyed accuracy claim. Two registry facilities have both longitude and latitude disagreements; their spatial results are marked for review. Registry year anchoring does not establish crop-year operating membership. Dated licensing reconciliation cannot determine opening/closure dates from missing records.

Production uses a 2026 revision of 2024 statistics. It is retrospective input, not a demonstrably available 2024 forecast vintage. Fifteen regional durum components are unpublished (`F`), leaving non-durum production UNKNOWN. Published partial regional totals cannot be treated as a complete conserved mass budget. Finer allocation and a defensible missing-data scenario remain scientific gates.

Roads use January 2024 extract timestamps. They do not establish later road completeness, passability or connectivity. Border extracts overlap; retain global IDs and inspect the overlap audit before constructing a graph. Turn restrictions/relations remain in the raw PBF and require a separate routing adapter.

No external contact, real allocation, energy model, fitted siting experiment, shortlist or map is produced in Phase 2.

## Checks and tests

CI runs the complete raw → normalized path on tiny **synthetic** GeoJSON, CSV, ZIP, GeoPackage, PBF and OSM XML inputs with socket connections forbidden. The 254-byte PBF fixture is independently specified: ways precede nodes, dense and ordinary nodes have negative longitude/nonzero offsets, one way references an unavailable node. Expected coordinates, version, tags, timestamp and explicit rejection are checked. Tests also cover immutable/corrupt raw files, stable identity under OBJECTID changes, duplicates, CRS mismatch, transfer separation, non-duplication of shipping-point volume, missingness and deterministic output hashes.

The real road decoder is compared with an independent pyosmium extraction in [the decoder audit](../audits/phase2-road-decoder-audit.json). The native library was removed because its older Windows release hung on shutdown and Windows blocked DLLs in newer releases. Runtime therefore does not require that native dependency.
