# Final product acceptance and scientific exit audit

9 October 2026. **Product implementation delivered; full scientific completion pending.**
The final application is `app/index.html`; its normal audience view has no presenter overlay,
guided-demo launch or demo banner. The historical Phase 5 bundle remains an unchanged archive.

## Delivered per lens

| Lens | Working behavior | Evidence boundary |
|---|---|---|
| Where first | Exact recorded top ten, numbered markers, list/filter, four-part node card, global search/coordinates/map selection, local package importer, CSV/source export and A4 brief | Temporary engineering order; missing supply and uncertainty stay UNKNOWN |
| How sure | Labels, range status, recorded siting baseline intervals/KILL verdict and shipping-point diagnostic | No fabricated confidence tier, field precision or energy validation |
| How to get there | Roads display, coordinate copy, phone-map handoff and pre-visit checklist | Seasonal controls disabled; route/visit-window/context values remain UNKNOWN |
| How it works | Five user-selected method steps and explicit layer/camera changes | Ordinary method help; source story does not substitute for validation |

## Checked design requirements

The machine browser report and 1440×900 / 390×844 screenshots are in `docs/audits/phase8/`.
Browser QA uses headless Edge, local file URLs, networking disabled, reduced motion and 4× CPU
throttling. This is a device-performance proxy, not a test on a physical mid-range phone.

| Requirement | Status | Evidence and qualification |
|---|---|---|
| Light survey-sheet theme | PASS | Eight inspected lens screenshots; local paper/land/water colors and requested typography |
| AA text contrast | PASS for tested states | Computed visible initial text/background ratios on desktop/mobile; text/semantic styles darkened for contrast. This is not a certified accessibility audit |
| Initial top ten under 1 second | PASS in tested environment | Desktop 685.6 ms; mobile viewport 720.3 ms under 4× CPU throttling. Road/registry decoding is deferred. A physical-phone timing claim remains untested |
| Selection and camera persist across lenses | PASS | Keyboard selection and deep camera comparisons across all four lenses on both sizes |
| Units, range semantics and UNKNOWN | PASS within supplied contracts | Original source quantities kept; no equal-endpoint false interval; strict unit/null/range/provenance package tests. Unsupported fields are explicitly unknown |
| Non-color encoding | PASS | Evidence text/patterns, numbered sites, unknown double rings/hatching and accessible list |
| Keyboard select/read/switch | PASS | Browser keyboard selection through list, markers, search and lens controls, including the geographic fallback |
| Simple/Expert and language persistence | PASS | Storage/reload checks for EN/FR/RW shell and detail switch. Source excerpts retain original language |
| Mobile three-height sheet | PASS | Handle click/drag implementation; snap-state/visible-map checks and screenshots. No claim of independent touch usability study |
| Genuine 200% text sizing | PASS in checked flow | Relative type sizes; computed body text doubles and the page retains horizontal bounds |
| Offline assets and no runtime calls | PASS | Local fonts explicitly loaded with offline browser context; no external requests or uncaught browser errors; source/phone links are user-triggered |
| No pipeline/config/registered output edits | PASS | Scientific source hash unchanged; Git diff for `src/enagis`, `configs`, `uv.lock`, `demo`, registration and protocol is empty |
| Worldwide location selection | PASS | Indexed country/town searches across continents, coordinates including zero/polar values, selectable map points |
| Other regional outputs | PASS for contract/rehearsal | Valid synthetic Rwanda package replaces current data, shows its interval/ribbon and exports its own CSV; malformed packages retain prior state. No real regional accuracy claim |
| A4 site brief | PASS for inspected example | Browser print output is one A4 page, rendered and visually inspected. Arbitrarily long imported text may require more pages |

Global names are incomplete: the bundled navigation data have 177 coarse country polygons and
7,519 country/place index entries. Coordinates/map selection cover unindexed locations. The
global background uses Natural Earth, rather than a worldwide OSM street database. OSM detail
is the existing pinned AB/SK roads; the legal/source attribution remains visible.

## Reproducibility and checks

The pinned Python environment, 227 passing Python tests, Ruff checks, eight smoke fixtures, six passing dependency-free
JavaScript contract tests and offline browser flows are checked. Exact results and hashes are
recorded in the machine audit. A fresh isolated environment was installed from `uv.lock` and
reproduced the application without scientific acquisition or fitting. Initial environment
installation needed network because two pinned wheels were missing from the local cache;
subsequent product building and use are offline. The lockfile was unchanged.

The release command builds the portable application, figures, method report/presenter handoff
and deterministic archive. The archive excludes private licensing/verification data. Mechanical
rebuild does not constitute an independent person's clean-machine review. CI now also checks
the presentation contract and rebuild; only an observed remote run may be called green.

## Scientific MVP checklist

| Required PRD evidence | Current status |
|---|---|
| Registry/provenance/precision | Delivered for frozen pilot |
| Siting experiment win/lose and baselines | Delivered, KILL under the registered rule |
| Shipping-point hindcast against baselines | Delivered as retrospective diagnostic |
| Capacity-constrained allocation and service computation | Engine delivered; real approved Phase 6 scientific exit pending |
| Real energy ranges and rank tiers | Unknown for public screen; synthetic engine rehearsal available |
| Three supply states | Implemented/tested; consumed pilot has undocumented comparable electrical supply |
| Real ranking freeze and verification sample | Pending; no real ranking-v1 tag or sample |
| Real verification outcomes/intervals | Not collected, n = 0 |
| Top ten / question / card / exports | Delivered for recorded temporary scenario |
| Real seasonal access / best visit window | Unknown in current public package |
| Expert shortlist and measured transfer | Not supplied / not performed |
| Independent review / live defense rehearsals | Not claimed |

These missing facts prevent declaring `PHASE COMPLETE — MVP READY FOR DEFENSE` under the full
scientific PRD, or calling the project 100% validated. They do not prevent opening, using and
presenting the implemented product. The presenter guide makes the claim boundary explicit.

## Deviations and assumptions

Decision 0011 records the new interface boundary, coarse public-domain world context, contrast
colors, unassessed confidence labels, disabled unsupported seasons and print/Save as PDF brief.
No new scientific coefficients, thresholds, seeds, folds or observations were selected.
No external messages were sent. EN/FR/RW translations need native-speaker review.
The initial archive command referenced a nonexistent root `LICENSE`; packaging was corrected
to include the existing `THIRD_PARTY_NOTICES.md` and bundled asset licences. No new project
licence or copyright ownership was assigned.
The first remote CI run failed before release checks. A fresh checkout reproduced a test
setup defect: the configured `.pytest_cache/tmp` required a missing parent directory. Test
initialization now creates that parent explicitly; this does not change scientific behavior.
The next Linux run passed tests, lint, smoke, JavaScript contracts, application rebuild and
figure generation, then failed uv cache cleanup because the action used a different cache
directory from the Makefile. The action now uses `.uv-cache`, keyed by `uv.lock`.

## Manual handoff checks

Open the portable folder's `app/index.html` with Wi-Fi disabled; inspect ten list rows. Search
Kigali and an unindexed coordinate; verify requirement remains unknown. Restore Home, select a
site, switch all lenses and inspect sources. Print its brief to A4. On a phone, select a row
from Locations, use the sheet handle and return to the map. Open the separate presenter guide
on the presenter's own screen. Perform three timed human rehearsals before the actual defense.
