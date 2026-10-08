# EnaGIS application

Open `index.html` in Chrome, Edge or Firefox. Keep this folder together. No account, server,
API key or internet is needed. Search a country, indexed town or latitude, longitude; select
any other location on the map. Local names are not a complete address index.

Four lenses keep the selected site and camera: Where first, How sure, How to get there,
and How it works. The last lens explains the method as normal product help. There are no
presenter controls, presentation overlays or demonstration labels in the application.

The built-in analysis is the unchanged public Canadian Prairie wheat/aeration scenario.
Ten shortlisted sites are shown immediately; worldwide navigation is available from search.
Outside this package's geographic coverage, the application shows its evidence needs and
UNKNOWN requirement. A place name or map point cannot establish production or electrical need.
Help offers a local regional-analysis package importer; read the repository package contract.
Imported packages replace the active analysis and retain a visible synthetic label when applicable.

The confidence and interval fields remain unknown when not supplied. The old deterministic
scenario's identical endpoints are not presented as an uncertainty interval. Seasonal routing,
commercial energy coefficients, metered validation and the real field sample are pending.
External phone-map/source links open only on request and need connectivity. Device location
is optional, needs browser permission, and may be unavailable offline or outside a secure context.

The site-brief action opens the browser's A4 print dialog, where Save as PDF is available.
CSV, source traces, local fonts and all public evidence travel with this folder.
The flat geographic map at `index.html?map=flat` supports devices without WebGL.

Sources: Natural Earth public-domain world outlines/place names; pinned AAFC/Statistics Canada
boundaries and © OpenStreetMap contributors, ODbL major roads for AB/SK. Global street detail
is not bundled. The global basemap is navigation context, not an analytical data source.
Inter and Fraunces are SIL OFL 1.1; MapLibre is BSD-3-Clause with dependency notices.
The checksum manifest records the original scientific run identities and all application assets.

Rebuild: `.venv/Scripts/python.exe -m scripts.build_mvp` from the repository root.
Portable command: `uv run --offline --locked --cache-dir .uv-cache python -m scripts.build_mvp`.
Verification: add `--verify`. No scientific fitting or national download is needed.
