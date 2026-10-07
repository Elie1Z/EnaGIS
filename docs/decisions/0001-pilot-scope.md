# 0001 — Commodity and pilot scope

Status: historical Rwanda candidate packet; **superseded for geographic scope by [decision 0002](0002-global-transfer.md)**. On 7 October 2026 the user first kept the choice open, then authorized selection of a data-rich pilot anywhere in the world. The coffee recommendation below remains an unselected candidate, not a default.

## Already fixed by the final PRD

- User and question: an energy planning team selects agricultural aggregation/processing points for scarce site visits, with uncertainty and an evidence trail.
- Rwanda was the original country context for the commodity audit; the latest user request permits any country.
- Milk was a no-go for the Rwanda open-data pilot under the PRD audit. That local finding is not a global ban on dairy. The committed siting experiment, baselines, hindcast, frozen verification and top-10 remain required.
- Processing must occur at the aggregation point. Transit-only nodes cannot receive invented stationary demand.

## Recommendation requiring team approval

Select **coffee cherries at coffee washing stations**, modelling wet processing (washing/pulping and associated on-site services), and use **Western Province** as the detailed pilot. Keep a national station registry and define a separate national sector-level siting experiment only if audited positives and spatial blocks support it. The 207-point public geodata layer includes 84 Western Province records across seven named districts in the live query on 7 October 2026. All 84 have a sector value, but the layer's survey labels span 2006–2011. The current pilot boundary, station validity and cross-district coverage require audit.

The service class is processing energy, **not milk/perishables cooling**. Its components and kWh-per-tonne range are human/source decisions. Do not use the toy coefficients from the supplied bootstrap script as scientific defaults.

## Decision fields to record before Phase 1 defaults or real-data modelling

| Decision | Current state | Needed evidence / owner |
|---|---|---|
| Commodity and processing step | Coffee wet processing recommended; **pending** | Team approves after applying all PRD gates. |
| Pilot geography | Western Province recommended; **pending** | Team confirms boundary and feasible field access. |
| Eligible nodes | Coffee washing stations recommended; candidate sites may be separately flagged; **pending** | Team confirms whether mini-washing stations qualify and the exact stationary service. |
| Registry source | Public geodata CWS point layer identified; **provisional** | Check age, duplicates, precision, status, licence and current NAEB register. |
| Production source | NAEB 2015 sector coffee-tree layer identified as a **proxy**, not production tonnage | Find dated crop-volume statistics and a defensible conversion; retain uncertainty. |
| Capacity / hindcast source | **Unresolved** | Need at least 30 facility-level capacity or throughput values, or use the PRD district-total fallback explicitly. |
| Verification pathway | **Unresolved** | Named team contact at NAEB, district agriculture office, cooperative or equivalent; approved phone/site protocol. Public directory entries do not establish team access. |
| Energy service and value screen | Wet-processing energy proposed; **coefficients unresolved** | Source intensity, batch/standing loads and cost-vs-product-value inputs. |
| Data reuse | **Unresolved** | Confirm licence/redistribution conditions for geodata and NAEB layers. |

## Decision record to complete

- Decision date: pending for this historical candidate (7 October 2026: explicitly kept open).
- Human approver(s): pending.
- Selected commodity and processing step: pending.
- Pilot geography and boundary/version: pending.
- Eligible node types: pending.
- Primary registry and production source: pending.
- Capacity/hindcast source or fallback: pending.
- Named verification contact and pathway: pending.
- Energy service and parameter-source owner: pending.
- Reason for decision, including failed gates: pending.

These fields preserve the unresolved Rwanda candidate audit. Current scope and next decisions are recorded in decision 0002; lack of a country preference is no longer a blocker.
