# Evidence ledger: what we know, what we estimated, what we do not know yet

Every value EnaGIS shows carries one evidence label. This page counts them in the data the
application actually embeds, explains every UNKNOWN, and says how to close each gap.

- Counted by: `python -m scripts.evidence_ledger --output docs/audit/evidence-ledger.json`
  (read-only; parses `app/index.html`).
- Data: 261 development nodes (Alberta + Saskatchewan primary elevators, AAFC 2024 registry),
  Phase 3 temporary engineering scenario `phase3-engineering-v1`, counted 9 October 2026.

## Label meanings

| Label | Meaning in EnaGIS |
|---|---|
| OBSERVED | Reported by a named, dated, licensed source. Not verified truth. |
| PREDICTED | Output of a fitted model. *None in the shipped app: the siting model was killed.* |
| ESTIMATED | Calculated from stated assumptions (here: the temporary scenario). |
| INFERRED | A rule combining evidence, e.g. "no fan asset documented in the consumed registry". |
| UNKNOWN | Not supported by evidence. Never defaulted, imputed or treated as zero. |

## Counts

| Scope | Rows | OBSERVED | PREDICTED | ESTIMATED | INFERRED | UNKNOWN |
|---|---:|---:|---:|---:|---:|---:|
| Development nodes (all fields) | 261 | 2,088 | 0 | 744 | 782 | 562 |
| Shortlist full traces (top 10) | 10 | 80 | 0 | 80 | 30 | 10 |

The application also shows UNKNOWN **display states** that are not stored as evidence objects.
For each of the 10 shortlisted sites these are the requirement range, the rank-confidence tier,
seasonal access and the best visit window (40 states). It also shows field verification n = 0.

### By field (development nodes)

| Field | What it is | OBSERVED | ESTIMATED | INFERRED | UNKNOWN |
|---|---|---:|---:|---:|---:|
| facility name, operator, class, status, location | AAFC registry as reported | 261 each | | | |
| node existence, node location | Registry-backed node | 261 each | | | |
| storage_capacity (t, all commodities) | Reported storage mass | 261 | | | |
| node eligibility | Primary elevator with positive storage | | | 260 | 1 |
| assigned tonnes / reporting period | Administrative equal-share scenario | | 186 | | 75 |
| stored tonnes (inventory) | Scenario inventory | | 186 | | 75 |
| electrical kW | Scenario fan duty | | 186 | | 75 |
| electricity kWh (one cycle) | Scenario | | 186 | | 75 |
| supply state | `no_documented_asset` for all | | | 261 | |
| gap classification evidence | Rule output | | | 261 | |
| capacity − requirement (kW) | Signed margin | | | | 261 |

## Every UNKNOWN, classified

| Class | Fields | Share | Nodes | Reason recorded in the data | Proof |
|---|---:|---:|---:|---|---|
| **(i) avoidable — over-strict rule** | 288 | 51.2% | 72 | "Missing, suppressed or unreliable published crop component" | StatCan publishes "Wheat, all" but suppresses "Wheat, durum" (status F) in 9 AB/SK regions. Province totals bound the missing durum: residual 100,097 t (SK, 5 regions), 32,384 t (AB, 4 regions). See [proposal](proposals/durum-residual-bounds.md). |
| **(i) avoidable — over-strict rule** | 8 | 1.4% | 2 | `spatial_review_required:location_conflict` | Geometry and attribute coordinates differ by 176 m (Rycroft) and 468 m (Woodrow), but both fall in the same reporting region. See [proposal](proposals/location-conflict-region-invariance.md). |
| **(ii) irreducible with current open data** | 261 | 46.4% | 261 | "No comparable documented electrical capacity or requirement" | No consumed open source documents fan motors, electrical service or grid capacity. The AAFC registry reports storage tonnes only. |
| **(iii) correct and desirable** | 5 | 0.9% | 1 | `stationary_service_eligibility_unknown_or_ineligible` / "Positive physical storage not established by source value" | Delisle, Alliance Pulse Processors: source reports 0 t storage. Imputing storage would invent a facility attribute. |
| **Total** | **562** | 100% | | | |

Shares sum to 99.9% because of rounding. **No UNKNOWN is caused by an implementation bug**
(missed join, unit mismatch or crash). Each follows the recorded method; the two class (i)
groups need a method change, so they are proposals for human approval, not fixes.

The 40 display states are class (ii). Range and tier need approved parameter distributions plus
engineering evidence on fan duty. Seasonal access and the visit window need seasonal road
restriction data.

## How to close each gap

| Gap | Data that would resolve it | Who holds it | How to request |
|---|---|---|---|
| Electrical capacity (261) | Fan motor nameplate kW, number of fans, service size (kVA) per elevator | Elevator operators (e.g. Viterra, Richardson Pioneer, Parrish & Heimbecker, G3, Cargill); utilities (SaskPower; FortisAlberta / ATCO in AB) | Operator questionnaire in [phase7-evidence-request.md](phase7-evidence-request.md); utility service-connection data requests; equipment-class evidence from PAMI or ASABE studies |
| Durum-suppressed production (72 nodes) | Either approval of the residual-bound rule or unsuppressed regional durum | Statistics Canada | Approve the [proposal](proposals/durum-residual-bounds.md); or a custom tabulation request to StatCan (fee-based) |
| Location conflicts (2 nodes) | Confirmed site coordinates | AAFC Atlas team; operators | Approve the [proposal](proposals/location-conflict-region-invariance.md); or a confirmation call to each operator |
| Range and confidence tier (10 sites) | Sourced distributions for inventory, residence time, airflow, static pressure, fan efficiency, cycle hours | Agricultural engineering literature; PAMI; operators | Human review of [phase6-scientific-review.md](phase6-scientific-review.md) |
| Seasonal access and visit window | Spring road-ban and weight-restriction schedules | Saskatchewan Ministry of Highways; Alberta Transportation and municipalities | Provincial open-data portals; published road-ban orders |
| Field truth (n = 0) | Dated phone or site checks of a frozen shortlist | Field partner | [phase7-field-form.md](phase7-field-form.md) and [spec/phase7-verification.md](spec/phase7-verification.md) |

Open invitations to contribute this data are listed in [help-wanted-data.md](help-wanted-data.md).

## Reproduce the root-cause checks

```sh
# label counts
uv run --offline --locked --cache-dir .uv-cache python -m scripts.evidence_ledger
# durum residuals: compare province control rows with the sum of published regional durum
# in data/processed/phase2/production_lineage.json (fields component_rows, province_control)
# location conflicts: data/processed/phase2/registry_source_rows.json where location_quality == "conflict"
```

The scripts used for the residual and region checks are in [docs/audit/audit-log.md](audit/audit-log.md), entry 6.
