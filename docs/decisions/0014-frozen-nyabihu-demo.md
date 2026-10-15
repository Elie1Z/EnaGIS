# 0014 — Frozen Nyabihu demo and evidence reporting

Status: implemented for the team's demo focus plan, 10 October 2026.

The hero is an extra entry point into decision 0012's Rwanda live app. It does not reopen the Canadian benchmark, change the Phase 4R protocol or KEEP result, fit a model, or replace the national screening. All district and chain controls remain available.

Freeze the exact gathered engine input, dated raw JSON responses, converted Overture inputs, NISR district row, code/configuration hashes and expected dry/rainy ranking. Replay uses local bundled data and the offline map. Never update expected results as part of a test. A newer-data scenario is separate and dated; a newer release date does not make old imagery new.

The engine's optional trace records existing draws without adding RNG calls. Reporting uses these draws for an order-averaged linear allocation of sample variance, with an explicit residual. This is descriptive, not causal sensitivity or a partition of the kWh interval. A separate report evaluates the existing demand function at shipped endpoints, including the existing local-production tornado endpoints. No counterfactual feeds into ranking, training or parameter selection. If fewer than two assumptions cause top-3 exits, report that finding rather than manufacture two.

ASSUMED is a qualifier on unsupported parameters; original OBSERVED/ESTIMATED/INFERRED/PREDICTED/UNKNOWN labels remain. DOCUMENTED is a display description of a source record, not observed operating refrigeration. DESK-CHECKED means a named human reviewed imagery; PHONE-CHECKED means a logged completed call under the frozen protocol, including negative and inconclusive outcomes. Neither is a field visit or validates energy demand. Initial human counts are zero.

Human approval recorded by the team: public-source acquisition up to 100 MB; activity-only phone success rule requiring a knowledgeable respondent, exact site, potato aggregation/storage in the most recent completed season, and reported tonnage greater than zero. Unknown volume is inconclusive. Scientific energy ranges have not been approved. No calls, imagery judgments, commits or publication are performed by the agent.

## Amendment, 10 October 2026: the page shows the product, not the presentation

Team direction: showing "demo", "hero case", "frozen hero" or a guide bar on the page is not professional. The site
is shown as it is, and only the presenter knows the sequence. Therefore:

- The start screen offers the snapshot as **Featured analysis · Rwanda → Nyabihu · Irish potato cold storage**, with
  a one-line description (dated open-data snapshot, reproducible ranking, opens without internet). It is one entry
  point beside search, the example districts and the four value chains.
- The six preset views have no on-screen control or caption. Page Down/Page Up (presentation clicker) or →/← move
  through them while the snapshot is open; Escape returns to free exploration. `?presenter=1` shows numbered
  controls and cue captions for rehearsal only.
- Panel and button names describe content: Provenance, Why Nyabihu, Sensitivity, Verification, Assumptions.
  Start-screen tools are **Save example districts** and **Synthetic sample**. Provenance lists files relative
  to the snapshot folder. Personal names do not appear in the app.
- Evidence labels, ranges, counts and caveats are unchanged; only presentation wording and controls changed.
  A unit test and the browser preflight fail if these words or a default step bar return to the page.
- Internal identifiers (`hero-*` element ids, `data/rwanda/hero/`, `make hero-repro`) are unchanged. They are not
  shown on the page, and renaming them would churn hashed manifests.
