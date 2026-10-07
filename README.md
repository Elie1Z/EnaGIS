# EnaGIS

EnaGIS helps productive-use-energy teams decide which agricultural aggregation and processing locations to investigate first, and how confident to be in those choices. It is a screening shortlist for phone checks and site visits, not a feasibility study.

## Project state

**Phase 0 is complete.** The first development benchmark is non-durum wheat storage and electricity for ambient-air aeration at Canadian Prairie primary elevators. Alberta and Saskatchewan are the development footprint; Manitoba is reserved for transfer evaluation. The [benchmark lock](docs/decisions/0003-benchmark-lock.md), [architecture](design.md), [interfaces](docs/spec/phase0-interfaces.md) and [completion audit](docs/phase-0-completion.md) define the next phase.

The user permits a pilot anywhere in the world, with adaptation to new regions as the product direction: see [decision 0002](docs/decisions/0002-global-transfer.md). The first benchmark is selected under the PRD's best-candidate fallback. It has strong public facility/capacity/delivery sources; validated energy parameters and committed verification participation remain explicit later-phase gates. No scientific model or field validation has been completed.

The final consolidated project description and the supplied UI concept are retained verbatim in `docs/reference/`. The PRD governs scientific scope, with the user's geographic change recorded in decisions 0002–0003. The UI concept is a design proposal to evaluate when building the map; it does not change scientific claims.

## Next step

Phase 1 creates machine-validated contracts, hand-reviewed fixtures, a pinned Python environment, developer commands and CI. Begin with capacity dimensions, missingness and shipping-point identity/cardinality. [pilot-scope.json](configs/pilot-scope.json) is scope metadata, not a scientific parameter configuration. Later-phase evidence gates are listed in the completion audit.

Code will be developed with AI assistance under human specifications, scientific decisions and review, following the PRD protocol.
