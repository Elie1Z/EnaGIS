# Frozen Nyabihu hero and human evidence

`nyabihu-potato/input.json` is the exact shipped-engine input gathered on 10 October 2026.
`acquisition-responses.json` retains raw geocoder, Overpass, weather and population JSON responses
with request URLs/times. Overture inputs are the exact converted tile geometry used by the engine,
including footprint centroids/areas, roads and power; raw PMTiles archives are not redistributed.
`MANIFEST.json` lists every snapshot input/report file, byte count and SHA-256 plus runtime hashes,
release, CRS and seed. The manifest excludes itself; the compressed browser bundle has its own hash.

Run `node live/tools/hero-repro.cjs` from the repository root. No network is used and expected.json
is never rewritten by that check. `build-hero.cjs` rebuilds the presentation bundle only when the
ranking still matches expected.json. It does not silently bless a new ranking. The public-source
acquisition command requires explicit human approval and is separate from build/test/replay.

Licences and attribution are retained per source in the manifest: OpenStreetMap/Overture building,
transport and base derivatives include ODbL obligations; Overture places CDLA-Permissive-2.0;
WorldPop and Open-Meteo CC BY 4.0. NISR numbers are attributed to the source publications linked
in the assumption sheet. Source retrieval dates do not establish observation dates or precision.
Coordinates are EPSG:4326 longitude, latitude. Roof areas and grid distances are estimates from
mapped geometry, not surveys. No contact details or private verification data are in the bundle.

`nyabihu-potato/verification-targets.json` fixes the ten ranked targets and five predicted look-alikes.
`phone-kit/01.html` through `15.html` are one-page printable scripts; matching CSVs are blank
per-target templates, not completed calls. `desk-check.csv` and `phone-log.csv` initially contain
headers only. The protocol and its approval/hash/timestamp are frozen before any call.

Use the in-app **Verification** panel for local reviews; export CSV for inspection. Completed reviews
are kept in this browser until exported; the frozen public replay bundle does not contain personal
verification data. Store identities, contact numbers and raw notes only in the ignored
`data/validation_private/hero/` directory. Never treat an empty template as zero activity or count
synthetic test records as real checks. DESK-CHECKED and PHONE-CHECKED are not field validation.

Newer data were identified but not downloaded by team decision. See
`docs/hero-data-freshness.md`. All initial real check counts and field visits remain zero.
