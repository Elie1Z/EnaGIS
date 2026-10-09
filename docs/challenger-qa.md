# Challenger Q&A

Hostile questions from three viewpoints: an OSEAS judge (J), a new contributor (C) and a domain
expert (E). **ANSWERED** means the evidence settles it. **WEAK** means we have an answer but the
evidence is thin. **UNANSWERED** means we cannot answer it yet.

| # | Who | Question | Short honest answer | Evidence | Status |
|---|---|---|---|---|---|
| 1 | J | So what? | A team with ten visits gets a traceable list and the one question to ask at each site. Whether the list is *better* than their current choice is untested. | [overview](overview.md), [validation §4](validation.md) | WEAK |
| 2 | J | Where is the AI? | A preregistered, spatially held-out presence-only siting model. It lost to production-only by 4.05 pp. The pipeline itself is mostly explicit physics and rules, by design. | [validation §1](validation.md) | ANSWERED |
| 3 | J | Then why should we credit an ML deliverable that lost? | OSEAS asks for an open pipeline, and organizers value honest negatives. Ours was frozen at a Git tag before evaluation, and the loss is reported with intervals. | tag `preregister-phase4-canada-v1.1` | ANSWERED |
| 4 | J | How do you know it is true? | We know the arithmetic, provenance and conservation are right (230 tests, verifiers). We do **not** know the kW values or ranking are right in reality: field n = 0. | [proof-of-work](proof-of-work.md) | WEAK |
| 5 | J | Why not QGIS? | QGIS could draw it. EnaGIS adds a fixed, tested workflow: evidence labels, UNKNOWN never zero, conservation checks, hash-pinned inputs, a registered comparison and a portable offline shortlist. | [architecture](architecture.md) | ANSWERED |
| 6 | J | Why so many UNKNOWNs? | 562 of 4,176 labelled fields (13.5%). 46% are electrical capacity, which no open source publishes. 53% come from an over-strict rule, for which we filed a proposal instead of quietly filling values. | [evidence-ledger](evidence-ledger.md) | ANSWERED |
| 7 | J | OSEAS is about energy access. Why Canada? | It was the only open setting where every stage could be tested: registry, production, blocks, roads and independent delivery outcomes. It tests the method, not access impact. | [scope-and-transfer](scope-and-transfer.md) | ANSWERED |
| 8 | J | What is the path to transfer? | A 7-step data list and a 10-step config path. Manitoba hold-out first, then an energy-access region. None done yet. | [scaling](scaling.md), [scope-and-transfer](scope-and-transfer.md) | WEAK |
| 9 | E | Is demand the same as willingness to pay? | No. EnaGIS estimates a technical requirement, never demand or ability to pay. The economics screen was deferred. | [limitations](limitations.md) #7 | ANSWERED |
| 10 | E | Does uncertainty just push the decision back to the planner? | Today, yes: range and tier are UNKNOWN. The Phase 6 engine produces stability tiers but runs on synthetic data only. Showing ties ("Tied ×5") at least stops false precision. | [method](method.md), [spec/phase6-science](spec/phase6-science.md) | WEAK |
| 11 | E | Seasonality and roads? | Not in the real product. Seasonal controls are disabled and roads are display context, not catchments. The Phase 6 engine supports mode and season routing on synthetic inputs. | app "How to get there" | UNANSWERED |
| 12 | E | Throughput versus real need? | Assigned tonnes are an administrative scenario, not observed throughput. Need is aeration of stored grain, modeled through residence time, not annual tonnes. Transit-only points get no stationary requirement. | [method](method.md) step 3–4 | WEAK |
| 13 | E | Supply side and grid plans? | Three supply states are implemented; all real sites are "no documented asset". No grid or utility plan data was consumed. Undocumented is not absent. | [evidence-ledger](evidence-ledger.md) | UNANSWERED |
| 14 | J | Is AI-written code understood by the team? | The PRD requires human specs, tests, review and explain-backs; [TEAM_GUIDE](TEAM_GUIDE.md) gives a 10-minute explain-back per module. Judges should test any member. | [ai-use](ai-use.md) | WEAK |
| 15 | J | What does a negative or `not_testable` result mean? | KILL means no demonstrated improvement under the frozen rule, not proof the idea is wrong. `not_testable` means the data cannot support the test; we report it rather than forcing a number. | [validation §1](validation.md) | ANSWERED |
| 16 | C | How would someone add a new crop or country? | Region config, source adapter, unit rules, service scenario, then evaluation on untouched blocks. Display-only packages take hours. | [scaling](scaling.md) | ANSWERED |
| 17 | E | 28 kW for an elevator: is that realistic? | Unknown. Hypothetical parameters (0.002 m³/s/t, 500 Pa, 60%/90% efficiency) are not approved for commercial elevators. | `configs/scenarios/phase3-engineering-v1.json` | UNANSWERED |
| 18 | E | Five sites with identical kW: is that not an artifact? | Yes. Equal-share assignment within a region plus a storage cap produces identical values. We show the tie and never claim an order of urgency. | app list, [limitations](limitations.md) #3 | ANSWERED |
| 19 | J | Your hindcast: Phase 3 wins on Spearman, B2 wins on top groups. Which is it? | Mixed. 52 of 138 shipping points, wide intervals. No claim either way, and absolute volumes are unvalidated. | [validation §2](validation.md) | ANSWERED |
| 20 | E | 214 of 369 CCS excluded. Is the siting test biased toward well-documented areas? | Possibly. 212 exclusions are production UNKNOWN. A descriptive sensitivity cohort (360 CCS) also gave KILL. | [validation §1](validation.md) | WEAK |
| 21 | E | The registry is nearly a census. Does that test finding *undocumented* facilities? | No. It is a weak test of that. Stated in the Phase 4 limitations. | [phase-4-completion](phase-4-completion.md) | ANSWERED |
| 22 | C | Can I rebuild from scratch? | Yes. Three commands for tests, and `make mvp verify-mvp` for the app. A fresh clone rebuilt a byte-identical app manifest. Real data needs `acquire` (1,002 MB). | [reproducibility](reproducibility.md) | ANSWERED |
| 23 | C | Has anyone outside the team rebuilt it? | Not yet. Only CI and the author's clean-room. | [reproducibility](reproducibility.md) | UNANSWERED |
| 24 | J | Any private or restricted data in the repo? | No. History scanned for keys, tokens and phone numbers: 0 hits. CGC PDFs and private verification data are ignored by Git. | [audit-log](audit/audit-log.md) #7 | ANSWERED |
| 25 | J | Is it open source? | Code MIT; data under its source licences; ODbL for OSM-derived roads. | [LICENSE](../LICENSE), [LICENSE-DATA](../LICENSE-DATA.md) | ANSWERED |
| 26 | E | Coordinates have 12 decimals. Survey-grade? | No. All 340 are P2 (named place). Extra digits are not precision. | [data-catalogue](data-catalogue.md) | ANSWERED |
| 27 | J | What happens if I search my own village? | You can select it. With no compatible local package EnaGIS says UNKNOWN and lists the evidence needed. It never invents a number. | screenshot `3-kigali.png` | ANSWERED |
| 28 | E | What if data is very sparse? | An unapproved stress test removed evidence 2,000 times: 0 sites ranked without evidence. Missing facilities inflated neighbours by +72% at 10% missing. A decline-to-rank rule is proposed. | [proposal](proposals/sparse-data-stress-diagnostic.md) | WEAK |
| 29 | J | Did you change anything after seeing results? | No change to the registered method. The protocol hash and tag precede evaluation; post-audit proposals are separate and unadopted. | `docs/audits/phase4-evaluation.json` → `scientific_changes_after_registration: false` | ANSWERED |
| 30 | E | Storage tonnes vs kW: did you ever convert one to the other? | No. Separate types in contracts. Storage never becomes electrical capacity. | `src/enagis/contracts.py`, tests | ANSWERED |
| 31 | J | Is the app just pretty? | It is offline and accessible, and it shows the same labels as the data. Presentation does not validate results, and we say so. | [limitations](limitations.md) | ANSWERED |
| 32 | E | Is there an expert-shortlist baseline? | No. That PRD requirement is unmet. | [validation §4](validation.md) | UNANSWERED |
| 33 | J | What would you do with one more month? | Get operating evidence for one elevator class, run the real Phase 6 engine, freeze `ranking-v1`, verify n ≥ 12. | [roadmap](roadmap.md) | ANSWERED |
| 34 | C | How do I contribute data? | Open a "Data wanted" issue; 12 invitations are listed. | [help-wanted-data](help-wanted-data.md) | ANSWERED |

**Totals: ANSWERED 21 · WEAK 8 · UNANSWERED 5** (34 questions).
