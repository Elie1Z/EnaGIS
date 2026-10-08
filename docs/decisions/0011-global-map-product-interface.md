# 0011 — Global location selection and final product appearance

Status: user-authorized interface work, 9 October 2026. The user requested completion through
Phase 8 for the MVP defense, worldwide place selection/search, the updated Design MD appearance,
and presenter guidance outside the audience interface.

## Scope

Preserve the registered experiment, historic outputs and scientific gates. The new application
is a static presentation consumer in `web/mvp/`, built to `app/`. The original Phase 5 archive
remains byte-identical. No `src/enagis`, scientific config, protocol, source index or registration
changes are required. The new design brief is preserved in `docs/reference/design-2026-10-09.md`.
It governs presentation; the PRD and scientific decisions continue to govern analysis.

## Product behavior

Use a light survey-sheet layout, local Inter/Fraunces fonts, MapLibre, four plain-language
lenses, evidence chips, a persistent selected site, source details and a printable site brief.
The product contains no presentation launch button or presenter overlay. How it works is
ordinary method help; the defense choreography exists only in a separate presenter document.

The local gazetteer and world map support country/place search, latitude/longitude input and
map selection. Names are incomplete; any valid point can be selected by coordinates. Display
latitude/longitude order explicitly. The Mercator map clips its visible latitude near 85°;
the flat geographic fallback retains polar navigation and coordinates.

The global basemap uses public-domain Natural Earth polygons and names, pinned to revision
`ca96624a56bd078437bca8184e78163e5039ad19`. It is coarse navigation context only. This choice avoids
acquiring a worldwide OSM street database or requiring online geocoding/tile services. Existing
dated AB/SK OSM roads and statistical boundaries remain local context. This is a documented
deviation from the brief's entirely OSM-derived global basemap; no scientific feature consumes
Natural Earth. No Manitoba source partitions are opened or added.

Fonts are pinned to Google Fonts revision `2eb0b48d5f760f62e286216f0859a8c540dbc1bd`, SIL OFL 1.1.
Acquisition is a separate build-time script; the ordinary rebuild reads checked-in hashes and
uses no network. Country boundaries and map geometry must not imply legal completeness or
facility coverage. Runtime external links open only through a user action.

## Evidence and appearance decisions

- Identical deterministic endpoints do not become an interval. The card explicitly reports
  unknown ranges/confidence; Sharp/Soft/Blurry or Robust/Contested classifications are not
  invented. Marker size uses square-root visual scaling of the recorded scenario kW.
- Reporting regions are labelled as such. A missing analytical catchment is not fabricated
  from a district polygon. Energy context and visit windows stay UNKNOWN. Unsupported season
  controls are disabled and explained.
- Evidence pattern, text and color coexist. The ember text/action color is darkened to
  `#BE3B0A`, amber to `#8B5A12`, and secondary ink to `#626D7D` for contrast on light surfaces;
  the design's `#D9480F` remains an accent token. This is a presentation contrast adjustment.
- EN/FR/RW shell and core card headings are provided; source excerpts/scientific reports retain
  their original language. Translation is not certified and needs native-speaker review.
- The A4 brief uses the browser print/Save as PDF workflow, retaining local fonts and evidence.
  Downloads include the active shortlist and exact source traces. No private data are packaged.
- Regional presentation packages declare purpose, coverage, units, evidence and sources.
  The importer replaces the active analysis, validates before committing UI state, rejects
  malformed inputs, and visibly labels synthetic packages. It displays recorded results;
  selecting a new point never fits a model or creates operating facts.

## Completion boundary

Software/UI delivery and real scientific validation are different gates. No user instruction
to complete the project creates an external participant, operating evidence or consented field
observations. The remaining Phase 6/7 scientific exits stay open. No `ranking-v1` tag or human
approval is fabricated, and synthetic checks cannot establish worldwide accuracy.
