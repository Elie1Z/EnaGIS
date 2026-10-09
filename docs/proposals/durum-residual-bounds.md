# Proposal: bounded non-durum production where durum is suppressed

**Status: PROPOSAL — awaiting human approval.** Nothing has been changed. UNKNOWN stays
UNKNOWN in every output until this is approved and implemented under a new decision record.

## Problem

72 of 261 development nodes (288 UNKNOWN fields: assigned tonnes, stored tonnes, kW, kWh) are
UNKNOWN because their reporting region's non-durum wheat production is UNKNOWN. The recorded
method computes non-durum as `Wheat, all − Wheat, durum`
(`data/processed/phase2/production_lineage.json`, field `expression`). In 9 AB/SK reporting
regions Statistics Canada publishes "Wheat, all" but suppresses "Wheat, durum" (status `F`,
too unreliable to publish). The method then returns UNKNOWN. That is correct under the current
rule. This proposal changes the rule.

## Evidence (Statistics Canada Table 32-10-0002-01, 2024, snapshot `statcan-32100002-20261007`)

| Province | Province durum (control row) | Sum of published regional durum | Residual for suppressed regions | Suppressed regions |
|---|---:|---:|---:|---|
| SK | 4,971,666 t | 4,871,569 t | **100,097 t** | 5 (SADR 5, 9, 14, 16, 17) |
| AB | 1,307,581 t | 1,275,197 t | **32,384 t** | 4 (SADR 40, 50, 60, 70) |

Regions exhaust each province: the sums of regional "Wheat, all" match province controls within
rounding (AB −1 t, SK −11 t, MB +1 t). Each suppressed region's durum therefore lies in
`[0, residual]`. Its non-durum production lies in `[Wheat, all − residual, Wheat, all]`.

| Region | Wheat, all (t) | Proposed non-durum interval (t) | Relative width |
|---|---:|---|---:|
| SK 14 | 1,192,005 | 1,091,908 – 1,192,005 | 8.4% |
| SK 5 | 1,254,966 | 1,154,869 – 1,254,966 | 8.0% |
| SK 9 | 969,386 | 869,289 – 969,386 | 10.3% |
| SK 16 | 761,092 | 660,995 – 761,092 | 13.2% |
| SK 17 | 528,069 | 427,972 – 528,069 | 19.0% |
| AB 70 | 1,553,526 | 1,521,142 – 1,553,526 | 2.1% |
| AB 50 | 1,179,613 | 1,147,229 – 1,179,613 | 2.7% |
| AB 60 | 864,382 | 831,998 – 864,382 | 3.7% |
| AB 40 | 763,867 | 731,483 – 763,867 | 4.2% |

Reproduce: the command block "durum residuals" in [evidence-ledger.md](../evidence-ledger.md).

## Proposed rule

When exactly one component is suppressed and a province control row is published, represent
non-durum production as an **ESTIMATED interval** with method text naming the residual
derivation. Do not use a point value. Downstream, carry the interval (Phase 6 range machinery)
or rank nodes by the lower bound with the interval shown. Never use the upper bound alone.

## What it would change and what it would not

- Would move up to 72 nodes from UNKNOWN to ESTIMATED-with-interval in a **new** run ID.
- Would **not** change the registered Phase 3 run, the Phase 4 cohorts or verdict, or any
  hashed artifact. The Phase 4 primary cohort excluded 212 CCS as `production_unknown`. A future
  protocol could use this rule, but only under a new registration.
- Manitoba must stay untouched (transfer hold-out).

## Questions for the reviewer

1. Is the province control row the right closure total, given that SADR values carry revision
   symbol `r`?
2. Is ranking on the lower bound acceptable, or should these nodes stay unranked with an interval?
