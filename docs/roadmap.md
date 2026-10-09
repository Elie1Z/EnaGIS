# Roadmap

Ordered by what most improves the decision, not by what is easiest to build. Each milestone
has an exit test. Nothing below is claimed as done.

| # | Milestone | Exit test | Depends on |
|---|---|---|---|
| 1 | Human review of open proposals (durum bounds, location conflicts, stress diagnostic, decline-to-rank) | Decision records written; accepted rules in versioned config | Team |
| 2 | Operating evidence for one elevator class: fan kW, airflow, pressure, cycle hours | Approved parameter ranges with sources ([phase6-scientific-review](phase6-scientific-review.md)) | Data wanted #1, #4, #5 |
| 3 | Real Phase 6 run: road catchments, capacity limits, Monte Carlo ranges and tiers | `enagis.science verify` passes on real inputs; ranges replace UNKNOWN | 2 |
| 4 | Compare the new shortlist with B0/B2 and an expert shortlist on matched outcomes | New preregistered protocol and result, win or lose | 3 |
| 5 | Freeze `ranking-v1` and verify n ≥ 12 with a field partner | Precision@k with Wilson intervals and decomposed failure modes | 3, partner |
| 6 | Manitoba transfer evaluation (untouched hold-out) | Transfer report with coverage | 3 |
| 7 | Onboard one energy-access region end to end | Measured adaptation effort, coverage, an evaluated result or an insufficient-data result | [scope-and-transfer](scope-and-transfer.md) |
| 8 | Independent rebuild by an outside person | Signed rebuild report | — |

Lesson from the audit: secure milestones 2 and 5 (evidence and a verification partner) before
investing further in software.
