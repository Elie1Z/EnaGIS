# Glossary

| Term | Meaning |
|---|---|
| Aeration | Blowing ambient air through stored grain to control temperature and moisture. The energy service modeled in the pilot. |
| Aggregation node / node | A place where product is collected, stored or processed. In the pilot, a primary grain elevator. |
| B0, B1, B2 | Baselines: B0 production only; B1 Euclidean-distance production; B2 road-network production. |
| Block / spatial block | Group of geography held out together in cross-validation (here a census agricultural region, CAR) so the test is not fooled by neighbours. |
| CAR / CCS / CD / CSD | Statistics Canada census agricultural region / consolidated subdivision / division / subdivision. |
| CGC | Canadian Grain Commission. Publishes deliveries by shipping point (kilotonnes). |
| Evidence label | OBSERVED, PREDICTED, ESTIMATED, INFERRED or UNKNOWN, attached to every value ([evidence ledger](evidence-ledger.md)). |
| Gap / gap bucket | Documented supply compared with estimated requirement: undocumented supply, undersized, verify first. |
| Hindcast | Checking a method against past observed outcomes (here 2024–2025 deliveries). |
| Hold-out (transfer) | Data kept untouched to test whether a method works somewhere new. Manitoba here. |
| KILL | Registered verdict meaning the model did not beat the best baseline under the frozen keep rule. |
| kW vs kWh | Power (rate) vs energy (amount). The app shows fan kW; kWh is per aeration cycle. |
| P1–P5 | Location precision: P1 coordinates ~100 m; P2 named place; P3 sector; P4 district; P5 unlocated. |
| Preregistration | Fixing the method, metric and decision rule (Git tag + hash) before seeing outcomes. |
| Primary elevator | Country grain elevator receiving grain from farmers. |
| Recall @ top 20% | Share of documented-presence units that fall in the top-scored 20% of units. |
| SADR | Small Area Data Region, the reporting unit for crop production statistics. |
| Scenario (temporary engineering) | A labelled set of hypothetical parameters used to exercise the pipeline; not approved science. |
| Shipping point | CGC delivery location; may serve several elevators, and volume is never duplicated across them. |
| Supply state | No documented asset / documented, known capacity / documented, unknown capacity. |
| Tie / Tied ×N | Sites with exactly equal estimates; their order uses stable IDs and does not mean urgency. |
| UNKNOWN | Not supported by evidence. Never zero, never imputed. |
