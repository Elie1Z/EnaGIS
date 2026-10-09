# Proposal: sparse-data stress diagnostic (v1)

**Status: PROPOSAL — awaiting human approval.** Two decisions are requested:
(1) accept this diagnostic as part of the submission and show it in the app's "How sure" lens;
(2) review the decline-to-rank rule below. Until approved, the result is **not** shown in the
application, and the code lives in `scripts/` so the registered `src/enagis` is unchanged.

Run on 9 October 2026 after the Phase 8 audit. It was not preregistered, and it is
**not accuracy evidence**. It tests how the recorded
Phase 3 screening procedure behaves when documentation disappears. It does not test whether
the procedure finds real energy opportunities.

Protocol: [`sparse-data-stress-v1.protocol.json`](sparse-data-stress-v1.protocol.json).
Report with seed and input/code hashes: [`sparse-data-stress-v1.report.json`](sparse-data-stress-v1.report.json). Its `code` hash is the unchanged HEAD scientific source.
Rebuild (needs the prepared Phase 2 spine):

```sh
uv run --offline --locked --cache-dir .uv-cache python -m scripts.sparse_data_stress --allow-temporary-scenario
```

## Why

The Phase 8 assessment found that the system handles missing data honestly but had never
shown what happens to the shortlist as data thins. Nine of 25 production regions and 75 of 261
development nodes were already UNKNOWN. That left open whether the shortlist simply reflects
where documentation is good. This diagnostic measures that risk directly.

## Method

The unchanged `make_traces` allocation and fan-duty logic is re-run on the real AB/SK
development inputs after seeded removal of evidence. There are 200 replicates per level and
2,000 degraded runs in total. Manitoba is not touched. The three mechanisms are:

| Mechanism | What is removed |
|---|---|
| Production loss | Known modeled tonnes for a share of reporting regions become UNKNOWN with a reason |
| Location unknown | A share of facilities lose their reporting-region spatial match but stay listed |
| Undocumented facility | A share of facilities disappear entirely, as if never registered |

Each run checks **abstention**: no node is ranked when its production, location or registration
was removed. It also checks **conservation**: known production equals assigned plus unserved.
It then compares the tie-inclusive top-10 with the baseline. Ties matter because ranks 1–5
share 28.1204 kW and ranks 7–10 share 25.4372 kW.

## Results

Baseline: 261 development nodes, 186 ranked, 11,918,640 known tonnes.

**Integrity held in every run.** Across 2,000 degraded runs, zero nodes were ranked without
the removed evidence. The largest conservation residual was 2.3 × 10⁻¹⁰ t, which is
floating-point noise.

| Mechanism | Removed | Ranked (mean) | Surviving top-10 kept | Mean worst kW inflation |
|---|---:|---:|---:|---:|
| Production loss | 10% | 163 | 100% | 0% |
| Production loss | 25% | 139 | 100% | 0% |
| Production loss | 50% | 93 | 100% | 0% |
| Production loss | 75% | 45 | 100% | 0% |
| Location unknown | 10% | 168 | 89.5% | +67% |
| Location unknown | 25% | 139 | 69.5% | +164% |
| Location unknown | 50% | 93 | 39.4% | +423% |
| Undocumented facility | 10% | 168 | 92.2% | +72% |
| Undocumented facility | 25% | 140 | 68.5% | +157% |
| Undocumented facility | 50% | 94 | 41.3% | +397% |

"Surviving top-10 kept" counts only baseline shortlist members whose own evidence survived.
"Mean worst kW inflation" is the mean, across replicates, of the largest increase of any
still-ranked site over its baseline estimate.

## Interpretation

1. **Losing production data degrades gracefully.** The list gets shorter, never wrong. Sites
   in affected regions become UNKNOWN; every other site keeps its estimate and place. Entrants
   appear only because the cutoff moves down, not because their values changed.
2. **Missing facilities is the real weakness.** The equal-share administrative assignment
   hands an absent elevator's production to its documented neighbours. With only 10% of
   facilities unregistered, some remaining site's requirement rises by about 72% on average,
   and roughly 2 of the 3–4 new shortlist entrants are there purely through that inflation.
   This is the measured form of the assessment's concern that the shortlist reflects where
   documentation is sufficient.
3. **Consequence for new regions.** Registry completeness has to be established before a
   regional shortlist is trusted. A place where only some facilities are documented will
   overstate the documented ones.

## Proposed decline-to-rank rule (needs human approval)

This is a proposal, not an implemented scientific rule. Following repository policy, it
belongs in versioned configuration only after review:

> Rank nodes in a reporting region only when facility-registry completeness for that region
> is documented, for example by matching deliveries or a census. Otherwise report the region's
> nodes as UNKNOWN with reason `registry_completeness_unknown`, or show them unranked with a
> visible redistribution warning.

The Phase 6 capacity-constrained engine and road catchments may reduce this sensitivity.
They should be re-tested under this same protocol once real inputs are approved.

## Limits

- The removal is random. Real documentation gaps cluster: remote, small or informal sites go
  missing first. Random removal therefore probably understates the bias.
- This tests one temporary scenario. It does not validate the energy coefficients, the
  allocation method or field outcomes. Field sample n = 0.
- Transfer to Manitoba and genuinely sparse regions remains untested.

## If approved

1. Move the protocol to `configs/experiments/` under a new decision record.
2. Restore the "When data goes missing" block in the How sure lens (the removed code is in
   [docs/audit/changes.md](../audit/changes.md)).
3. Add the report to the release archive.
