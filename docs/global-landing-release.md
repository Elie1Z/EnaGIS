# Global landing and continuous Earth journey

Updated 6 November 2026.

## Experience

The landing uses the existing MapLibre GL JS 5.12.0 map with globe projection and Esri satellite imagery. The left side has a light search and introduction panel; the right side shows a slowly rotating Earth against space. The same geographic canvas stays mounted at the same viewport size through the flight and the analysis workspace. No extra mapping dependency was added.

Search offers named place matches. Selecting a match immediately starts a 4.2-second geographic camera flight and gathers the selected area's open data in parallel. There is no second enter button. Valid coordinates start directly; their study window is explicitly labelled in degrees. The landing copy fades away as the camera moves, a progress card follows actual gathering steps, and the existing analysis controls appear on arrival.

The map loads imagery during zooming. Geographic labels fade in at closer scales. Satellite tile detail still depends on provider response time; lower-resolution imagery may temporarily remain visible during a fast flight. Attribution stays visible. If imagery fails, the existing Natural Earth fallback remains usable and is labelled as unavailable imagery.

Rotation pauses during search interaction and can be paused explicitly. Dragging uses the real globe controls. Reduced motion disables rotation and skips the animated flight. Skip flight and Escape arrive immediately. Desktop and mobile use different camera padding. Comparison maps inherit the arrival camera and their divider aligns with the imagery split.

## Evidence and analysis handoff

Detailed gathering starts automatically only for areas within the existing analysis-size limit. The arrival panel displays actual source progress and unavailable checks. Once gathered, inputs are reused when the user selects an activity; a new data download is unnecessary. An activity selected while gathering is pending starts analysis when that gathering finishes.

No crop, energy demand, ranking or production figure is silently chosen by the new entry flow. Regions above the analysis-size limit open as overviews with instructions to narrow the study area. Pending exploration responses cannot replace a newer search, a saved analysis or a replay.

The existing four crop/service calculations remain the supported analytical choices. This change does not implement the separate commodity/activity builder, new process physics or supply optimisation in the broader upgrade plan. Search and navigation can reach global locations; this does not establish uniform evidence coverage or analytical validity everywhere. No scientific thresholds, coefficients or models were changed.

## Verification

- 27 controlled journey checks passed: geographic globe, pause, immediate gathering, progressive camera movement, persistent canvas and dimensions, selected-area framing, source failures, explicit activity choice, input reuse, comparison alignment, skip, stale-response isolation, large-region gate, coordinate validation, mobile and reduced motion.
- 40 existing browser workflow checks passed: lenses, activity changes, assumptions, candidate and siting displays, comparison, exports, saved-file replay, source fallback, mobile and direct file opening.
- 32 existing engine, Overture, siting and frozen-snapshot tests passed.
- JavaScript syntax checks and Git whitespace checks passed.
- Live satellite imagery and a flight into a Nyabihu study window were inspected in Edge, at desktop and mobile sizes. Climate and Overture data were observed returning. A population request failed during one run and remained explicitly unavailable; other provider requests were still pending when the visual check ended. This was a visual integration check, not a certification of all live services.
- Controlled browser fixtures establish interface behaviour, not real-world analytical accuracy.

Preview screenshots are local under `outputs/global-landing/`: `satellite-desktop.png`, `satellite-flight.png`, `satellite-arrival.png` and `satellite-mobile.png`. The other journey-test images use controlled fixtures or the offline fallback.

## Implementation references

MapLibre's official [globe camera example](https://maplibre.org/maplibre-gl-js/docs/examples/zoom-and-planet-size-relation-on-globe/) and [globe atmosphere example](https://maplibre.org/maplibre-gl-js/docs/examples/display-a-globe-with-an-atmosphere/) informed the integration. Behaviour was verified against the repository's bundled version.

## Preview and commits

Serve the `live` directory and open its root page. The active local preview is `http://localhost:8766/`. Reload the page to pick up the new files. The public Netlify deployment has not been updated.

All task commits use the configured author Elie Mugisha, mugishaelie160@gmail.com. Unrelated README edits, packaging scripts and video-project files were left out of these commits.
