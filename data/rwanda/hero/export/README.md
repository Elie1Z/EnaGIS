# Nyabihu potato cold storage: GeoJSON export

`nyabihu-potato-ranking.geojson` is plain GeoJSON (RFC 7946, EPSG:4326 longitude/latitude). It
loads in QGIS, Energy Access Explorer or any GIS that reads GeoJSON. Compatibility with any specific
platform is not certified.

It contains 315 point features:

- 310 `ranked_site` features. These are every candidate site in the dated Nyabihu snapshot, ordered by
  dry-season rank. Each one has dry- and rainy-season rank, tier, share of simulations in the top 10,
  effective catchment people, production (t/yr), and energy need (kWh per peak day, central and
  p5–p95). It also carries running kW, mapped-grid state, siting percentile and the first question
  to ask on site.
- 5 `siting_lookalike` features. These are the top cells from the registered Phase 4R siting model,
  i.e. places that resemble documented processing or storage sites. They are predictions, not
  detected facilities.

Every value carries its evidence label in a matching `*_evidence` property:
OBSERVED, INFERRED, ESTIMATED, PREDICTED or UNKNOWN. The 15 verification targets also carry
`desk_checked`, `phone_checked`, call outcome counts and `field_visits`, computed from
`../desk-check.csv` and `../phone-log.csv` under the pre-registered protocol. At export time all of
these counts are 0. The file's `enagis` member gives the snapshot date, Overture release, engine
version, seed, draws, units, label definitions and the protocol SHA-256.

Rebuild with `node live/tools/export-hero-geojson.cjs` (or `make hero-geojson`) after logging new
desk or phone checks. The tool re-runs the shipped engine on the frozen input and refuses to write
unless the ranking equals `../nyabihu-potato/expected.json`. Run `--check` to confirm the committed
file is current. Output is deterministic and has no wall-clock fields.

These are screening results, not a feasibility study. The licence is in the file: it contains
OpenStreetMap and Overture Maps information (ODbL 1.0; Overture places CDLA-Permissive-2.0), so ODbL
share-alike applies to this derived database. WorldPop and Open-Meteo inputs are CC BY 4.0.
