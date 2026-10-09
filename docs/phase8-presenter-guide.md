# Private presenter guide — MVP defense

Keep this document on the presenter's own device. Open `app/index.html` for the audience.
The audience sees the normal product; do not open the historic Phase 5 guided interface.

## Preparation

Keep the complete application folder together. Use 1440×900 or larger on the projector.
**Run `node scripts/demo_preflight.mjs` on the presentation laptop first** (or `make preflight`).
It walks the exact path below in a headless browser and checks 15 things: logo, map, ten
non-overlapping pins, KILL verdict, baseline bars, Kigali, flat backup, phone layout and console
errors. It saves screenshots to `outputs/demo-preflight/` as a backup deck. Do not present
on a red result.
Open the app once, fit the sites, choose Simple, and select EN (FR/RW available if appropriate).
Make sure the mouse is not covering a card or pin. Keep the ZIP and PDF/site brief as backups.
The local app works with Wi-Fi disconnected. External source/phone-map links need internet.
Use `app/index.html?map=flat` if WebGL is unavailable; it retains geographic navigation.

## Three-minute path

The current demo script, hero example and fallback steps are in [TEAM_GUIDE.md](TEAM_GUIDE.md)
§2–3. The sparse-data stress result is a **proposal awaiting approval** and is not shown in the
app. Mention it only as "proposed, not adopted"
([proposal](proposals/sparse-data-stress-diagnostic.md)).

How it works is ordinary product help: five manually selected steps explain production,
collection/assignment, technical requirement, unknowns and verification. Use it if asked about
the method; it is not an on-screen presentation guide. Keep camera/selection during lens changes.

## Hero example and comparison boundary

Dixon, Richardson Pioneer Limited, SK, is rank 1 of the recorded engineering list; its raw
scenario is 28.1204 kW, displayed as 28 kW with range UNKNOWN. Five top entries share the
same unrounded requirement (ranks 7–10 share another), so stable IDs break ties and the list
shows a **Tied ×N** badge. Do not claim Dixon is more urgent.
The coordinate is P2 named-place precision. The exact source trace and reported storage are
available in the card. Supply and actual operating conditions are not validated.

The CCS production-only siting arm is not a node-level alternative visit list. No expert
shortlist or matched site-level production-only shortlist is supplied. State that the intended
hero contrast “what a simpler baseline would visit and what we found” is not testable with the
current evidence. Do not substitute a CCS or shipping-point outcome for a field-confirmed node.

## Questions and candid answers

| Question | Answer / evidence |
|---|---|
| Can I choose my own location? | Yes: indexed place search, coordinates, or map selection. A compatible local analysis package is needed for numerical screening. |
| Where is the ML? | The spatial presence-only siting comparison, with fold-local preprocessing, CAR holdout and frozen keep/kill. It did not win here. |
| How do you know the rank is meaningful? | Conservation and artifact integrity are verified; real operating accuracy and field precision remain untested. The current order is a temporary engineering scenario. |
| Why not just QGIS? | The tool delivers a fixed workflow with source/units/missingness, recorded comparisons, a list and a site question. Better investigation outcomes still require prospective evidence. |
| What if B2 is as good? | Keep the transparent baseline. Added complexity earns its place through a declared decision benefit and common-outcome evaluation. |
| What does uncertainty mean? | Ranges reflect declared inputs; membership frequency is draw stability, not probability of viability. The public screen has no assessed range/tier yet. |
| Is this worldwide analysis? | Worldwide location selection and a region package contract are implemented. Accuracy outside the pilot is not established; sparse data can legitimately yield no numerical rank. |
| What happened in field verification? | No real observations, n = 0. The freeze/analysis software was tested with a separate synthetic rehearsal, which is not displayed as validation. |
| Did you test it with missing data? | A proposed, not yet approved [sparse-data stress diagnostic](proposals/sparse-data-stress-diagnostic.md) ran 2,000 seeded degraded runs: 0 nodes ranked without evidence, and production was conserved. Lost production shrinks the list but keeps every surviving shortlist member. Unregistered facilities inflate neighbours by about +72% at 10% missing. It is a robustness test, not accuracy evidence. |
| So what would you do in a poorly documented region? | First establish facility-registry completeness. The stress test shows that is the input the ranking is most sensitive to. A proposed decline-to-rank rule awaits review. Until then, sites in such regions should be shown unranked with a warning. |
| What did you fix after your own audit? | Brand and layout polish, visible tie groups, a scripted demo preflight and a full documentation suite. The stress diagnostic and UNKNOWN-reduction rules are proposals awaiting approval. The scientific gaps (operating evidence, field verification, Manitoba transfer) are stated as next steps, not hidden. |
| Why Canada? | One controlled benchmark with open source coverage. The product's location search and presentation contract are geographic, not Canada-only. |

## Backup and remaining preparation

Use the reproducible siting/hindcast SVGs and their source JSON if the browser is unavailable.
No verification hit rate or metered energy figure exists to show. A closed network does not
affect the application; opening source websites does.
Complete three timed live rehearsals with an actual presenter before the defense. Automated
browser tests do not establish human presentation fluency, audience comprehension or native
translation quality. No rehearsal completion is fabricated in the release audit.
