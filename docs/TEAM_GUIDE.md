# Team guide: learn, explain and demo EnaGIS

For four team members. Goal: anyone can explain any module in 10 minutes and run the demo alone.

## 1. Ten-minute explain-backs (one per module)

For each module, read the files, then explain the four prompts aloud to a teammate without notes.

| Module | Read | Explain: what goes in, what comes out, one invariant, one way it can fail |
|---|---|---|
| **Evidence contracts** | `src/enagis/contracts.py` (`Evidence`, `Value`) | Every value has a label; `value=None` requires UNKNOWN plus a reason; a known value cannot be UNKNOWN. Failure: someone fills None with 0, and validation rejects it. |
| **Acquisition & manifest** | `acquire.py`, `docs/data/manifest.json` | URL → file → SHA-256 check → licence check. Failure: source changes upstream, so the hash mismatches and the run stops. |
| **Ingestion & adapters** | `ingestion.py`, `adapters/canada.py`, `adapters/spatial.py` | Raw AAFC/StatCan columns → contracts; point-in-region joins in EPSG:3347. Failure: coordinate/attribute conflict → `location_conflict` (2 sites). |
| **Production** | `production_lineage.json` rows | Non-durum = Wheat, all − Wheat, durum per region. Failure: durum suppressed (F) → UNKNOWN (9 regions, 72 nodes). |
| **Allocation** | `allocation.py` | Equal share within region, capped at storage × 0.5 × 365/30; unserved kept. Invariant: assigned + unserved = input. |
| **Energy** | `energy.py`, `configs/scenarios/phase3-engineering-v1.json` | t → stored t → m³/s → kW → kWh. Dixon: 184,751 → 15,185 → 30.37 → 28.12 → 4,218. Failure: storage tonnes used as kW (forbidden by types). |
| **Supply & gap** | `energy.py` (`classify_gap`) | Three supply states; margin UNKNOWN if either side unknown. Real data: all "no documented asset". |
| **Ranking & traces** | `pipeline.py` (`make_traces`) | kW descending, node ID breaks ties; every node gets a trace and a question. Failure: ties read as urgency. |
| **Siting experiment** | `experiment*.py`, `siting.py`, [validation](validation.md) | Label-free features → presence-only model → recall@20% on 7 held-out blocks vs baselines → frozen rule → KILL. |
| **Hindcast** | `hindcast.py` | Ranks vs CGC shipping-point deliveries, 52 groups; volumes never split across elevators. |
| **Phase 6 engine** | `science/` | Routing, capacity, Monte Carlo tiers; synthetic only; real run gated on evidence. |
| **Verification** | `verification/`, [spec/phase7-verification](spec/phase7-verification.md) | Freeze ranking at a tag → seeded sample → private records → aggregate precision with intervals. Real n = 0. |
| **App** | `web/mvp/`, `web/view-model.js`, `scripts/build_mvp.py` | Evidence JSON embedded in one HTML file; MapLibre with flat fallback; no network. |

## 2. Three-minute demo (hero: Dixon, SK)

Before: run `node scripts/demo_preflight.mjs` on the presenting laptop. All 15 must pass. Open
`app/index.html`, choose EN and Simple, then click Fit sites.

| Time | Do | Say |
|---|---|---|
| 0:00–0:20 | Where first; logo and ten pins visible | "Energy teams can visit maybe ten sites a season. EnaGIS turns open registries into one ranked list, with the next question for each site." |
| 0:20–0:55 | Click **Dixon**; point at **Tied ×5**; scroll the card: Why, How sure, Check first | "Location and storage are reported by AAFC; fan power is estimated at 28 kW under a temporary scenario. Five sites tie exactly, and we show that instead of inventing an order. Supply and confidence are UNKNOWN, so the card ends with the question that makes the visit worth it." |
| 0:55–1:15 | **Site brief** (print preview) | "One page for the field officer. Works offline." |
| 1:15–1:55 | **How sure**: the bars | "Our ML siting model was preregistered at a Git tag. It lost to production-only by four points, and we kept the simpler baseline as the rule said. Honest negatives are part of the product." |
| 1:55–2:20 | Search **Kigali** | "Search is global, analysis is local. Here there is no package, so EnaGIS says UNKNOWN and lists the evidence to collect. It will not invent a number for Rwanda." |
| 2:20–3:00 | Back to Dixon; mention the evidence ledger | "Every number carries a label. 13.5% of our fields are UNKNOWN, and we can name which data closes each one and who holds it. What's next: operating evidence, then a frozen field check with a partner. That's our ask." |

## 3. Offline fallback

1. Wi-Fi off still works: the app needs no network.
2. No WebGL or a blank map: open `app/index.html?map=flat`.
3. Browser fails entirely: show `docs/screenshots/` (captured by the preflight) in order 1 → 6.
4. Laptop fails: the release ZIP `outputs/mvp-release/EnaGIS-MVP.zip` (from `make release`) on a
   USB stick contains the same app and docs.

## 4. Top 15 answers

1. **Where is the AI?** Siting model, preregistered, lost by 4.05 pp → KILL, reported.
2. **Is the top 10 right?** Unknown; temporary scenario; field n = 0.
3. **Why Canada?** Only open setting with every stage testable; transfer path documented.
4. **Why UNKNOWN?** No open electrical-capacity data (46%), and an over-strict rule (53%, proposal filed).
5. **Why not QGIS?** Fixed, tested workflow with labels, conservation and registered comparison.
6. **Demand = willingness to pay?** No; technical requirement only.
7. **Seasonality?** Not in the real product yet.
8. **Supply/grid?** Three states implemented; no data, so all "no documented asset".
9. **Ties?** Real artifact of equal-share assignment; shown, not hidden.
10. **Hindcast?** Mixed: Phase 3 best ρ (0.773), B2 found more top groups (8 of 11 vs 4 of 11).
11. **Reproducible?** Three commands; byte-identical app rebuild; CI green.
12. **Open?** MIT code; data under source licences; ODbL roads.
13. **Sparse data?** Unapproved stress test: never ranks without evidence; missing facilities inflate neighbours.
14. **AI code understood?** Explain-back table above; ask any of us.
15. **Next month?** Operating evidence → real Phase 6 run → freeze → verify n ≥ 12.

More: [challenger-qa.md](challenger-qa.md).

## 5. Say / never say

| Say | Never say |
|---|---|
| "Estimated under a temporary scenario" | "This site needs 28 kW" |
| "Supply is undocumented" | "This site has no power" / "energy gap here" |
| "Tied ×5; order is by ID" | "Dixon is the most urgent" |
| "The ML model lost; we report it" | "Our AI finds facilities" |
| "Worldwide search, local analysis" | "Works anywhere in the world" |
| "Field verification has not happened (n = 0)" | "Validated" / "accurate" |
| "Proposal awaiting approval" (stress test, durum bounds) | Present proposals as adopted results |
