# 0012 — EnaGIS Live: search-time analysis for any place

Status: **implemented**, 9 October 2026, at the team's request ("a tool, not a static display").

## Context

The Phase 8 app (`app/`) displays recorded Canadian results. Searching elsewhere moves the camera
but computes nothing, by design (decisions 0007, 0011). For an energy-access audience the team
needs the method to run where they are: search a Rwandan district and get a real shortlist.

## Decision

Add `live/`, a static web app with a browser-side engine that runs the full chain at search time:

1. find the area;
2. gather OpenStreetMap and Open-Meteo data;
3. build road catchments (dry and rainy);
4. estimate need with ranges;
5. simulate;
6. rank;
7. add supply context and a simpler baseline;
8. write plain-language findings.

Method: [live-engine.md](../live-engine.md).

- **No server.** The browser calls open, keyless services directly. That keeps hosting free
  (GitHub Pages or a file) and avoids a single point of failure at the venue.
- **Reproducible.** Every response is kept with its query, endpoint and time; "Save analysis"
  replays it offline.
- **Responsive.** The engine runs in a Web Worker so the page does not freeze.

## Deliberate deviations from earlier rules

| Earlier rule | Now | Why |
|---|---|---|
| No network at runtime (design brief, 0011) | Live search uses the network; saved analyses and the synthetic demo work offline | A tool must gather data for the place asked about |
| Four lenses at most | Six lenses plus separate basemaps | The team asked for map views that match different user needs; basemap and lens are separate controls so each stays simple |
| No Robust/Contested tiers without uncertainty analysis | Tiers shown | They now come from a 300-draw simulation per analysis |

## What does not change

`src/enagis`, configs, the registered Phase 4 protocol, results and verdict, and the `app/` and
`demo/` builds and checksums. Live results are screening estimates. They are not a registered
experiment and are never mixed with the Canadian evidence.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Public Overpass servers busy or slow | Three mirrors, browser cache, saved analyses for demos |
| Thin OSM coverage hides sites | Map-data lens, hatched "not yet known" squares, coverage sentence in findings, town/village stand-ins labelled INFERRED |
| Large areas | Limit of 2,500 km² inside the boundary; queries follow the boundary |
| Unapproved parameters mistaken for facts | Evidence chips, Assumptions panel, "Screening tool, not a feasibility study" on every screen |
