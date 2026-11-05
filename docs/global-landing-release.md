# Global landing release

Implemented 5 November 2026.

## Experience

EnaGIS opens with a slowly rotating geographic globe in a dark space setting. The canvas uses the bundled Natural Earth boundaries, so the globe itself works without external imagery or a network connection. Search uses the existing geocoder and offers explicit place choices. Coordinate entry creates a labelled study window.

The globe pauses while the search has focus, turns toward the selected location, and moves closer before the application opens its area view. Dragging and arrow keys rotate the globe. A pause control and reduced-motion preference are supported. The workspace requests satellite imagery and uses the existing labelled offline fallback if the provider is unavailable.

A new area opens without a demand result, a rank or a preselected activity. Users can inspect its map and extent, then explicitly select one of the existing supported analyses. Large regions are described as overviews and require a smaller study area for detailed analysis.

The existing four crop/service calculations remain the supported analytical choices. This release does not yet implement the separate commodity/activity builder, new process physics or supply optimisation described in the broader upgrade plan. The initial overview provides geographic orientation, not a new survey of local agricultural activities.

## Files

- `live/landing.css`: responsive dark landing composition.
- `live/js/landing.js`: local globe renderer, interaction, search and transition.
- `live/js/app.js`: explicit area preview and saved-file integration.
- `tests/live/landing.cjs`: controlled browser checks for the new entry flow.
- `tests/live/e2e.cjs`: existing workspace regression suite, entered after dismissing the new landing.

## Verification

- 32 existing engine, Overture, siting and snapshot checks passed.
- 40 existing browser workflow checks passed, including all lenses, switching analyses, CSV export, saved-file replay, source fallback, mobile and direct file opening.
- New browser checks passed for desktop and mobile entry, search selection, preview without energy results, coordinate limits, reduced motion and return navigation. No browser JavaScript errors were recorded.
- Screenshots were reviewed at desktop and mobile sizes. Network-dependent browser paths use controlled fixtures; these checks do not establish current public-provider availability or analytical accuracy.

## Preview

Open `live/index.html` locally or serve the `live` directory. The public deployment has not been updated by this release. Git commits use the repository's configured author, Elie Mugisha.
