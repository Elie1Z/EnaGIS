# Regional presentation package v1

The application's Help → Open regional analysis loads a local JSON file with schema identifier
`enagis-region-view-v1`. It accepts recorded analysis products; it is not a raw-data ingestion
or a scientific calibration interface. No network service or country-specific runtime parser
is involved. The existing source adapters and scientific modules run upstream.

## Header

Required: `schema_version`, `region_id`, `title`, `run_id`, `commodity_id`, `service_id`,
`period_start`, `period_end` (ISO dates in chronological order), `crs: "EPSG:4326"`,
`purpose: "real" | "synthetic"`, nonempty `limitations`, `sources`, `coverage`, `sites`.
Maximum file size is 30 MB and maximum site count is 5,000, as browser resource limits.
These are interface limits, not scientific thresholds. An empty site set must explain its
limitations. Coverage is a GeoJSON FeatureCollection of Polygon/MultiPolygon features, with
closed longitude/latitude rings and optional holes; represent antimeridian crossings with
split polygons. Coverage is the analysis footprint, not the world basemap's country outlines.

Each source declares a unique `snapshot_id`, `publisher`, `effective_on`, `licence` and
`redistribution: "permitted"`. Include source/ licence URLs and SHA-256 from the upstream manifest.
Do not import private observations, participant details or licence-restricted source content.
Validation checks declared structure; it does not independently verify an author's truthfulness.

## Site

Required identity fields: `id`, `name`, `operator`, `rank` (positive unique integer or null),
`lon`, `lat`, `province` (display subdivision label), `kind`, `precision`, `question`.
Coordinates must agree with the `location.value` and fall inside the declared coverage.
`tier` is null or an already produced `Robust`, `Contested`, `Verify first`; do not fabricate
tiers from coordinate precision. Include `confidence` as its explanatory text and `verification`
as the recorded status. Keep provenance for any upstream tier/verification in the full trace.

Required evidence fields:

| Field | Value / unit |
|---|---|
| `need` | Nonnegative electrical number or null; unit `kW`; `range: [lower, upper]` or null |
| `margin` | Signed comparable electrical number or null; unit `kW` |
| `location` | `{longitude, latitude, crs: "EPSG:4326"}` |
| `storage` | Numeric mass or null with explicit original/converted unit |
| `throughput` | Numeric flow/period total or null with explicit unit and period |
| `travel` | Recorded access result or null, with method and unit where numeric |
| `visit_window` | Sourced date/season description or null |
| `energy_context` | Sourced context description or null |

Every field is `{value, evidence}`. Evidence contains `label`, `as_of` (ISO date), `licence`,
`method`, `source_ids` pointing into the supplied sources, and `missing_reason`. Missing values
are null, labelled UNKNOWN, with a reason. Zero is a known numeric value and cannot be labelled
UNKNOWN. Estimates without a justified interval use `range: null`; equal endpoints are rejected
as an interval. Bounds must contain the central value. Values must retain their actual units.

`supply` is one of `no_documented_asset`, `documented_known_capacity`,
`documented_unknown_capacity`, with `supply_evidence` using the same evidence structure.
`bucket` is the recorded service gap category. An optional `trace` preserves the exact upstream
site record. The viewer neither derives supply from storage mass nor recalculates ranks.

## Current scope and handoff

The built-in adapter (`web/view-model.js: fromNode`) reads the existing Phase 3 record contract.
Other upstream exporters can produce the same presentation shape from their recorded outputs.
The importer replaces the active benchmark and its CSV export; it never mixes ranks or
validation numbers across regions. Synthetic packages display a visible ribbon.
The view contract's geometry/null/provenance guards and a synthetic Rwanda import are tested.
This is software portability evidence; no empirical Rwanda performance is claimed.

The current importer renders the common site/range/supply/evidence fields. Rich seasonal route,
catchment and local evaluation panels require a future explicitly versioned presentation extension;
unsupported fields remain unknown. Use the repository's existing scientific region/scenario
configuration for computation and preserve untouched spatial validation before claiming transfer.
