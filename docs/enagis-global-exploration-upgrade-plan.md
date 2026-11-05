# EnaGIS global exploration upgrade plan

Status: proposed implementation plan, 5 November 2026. No product changes are made by this document.

## 1 Product decision

Make location the starting point. Users should be able to explore an area before choosing a crop, agricultural activity or calculation model. EnaGIS remains focused on agricultural energy planning, with a structure that can expand across locations and activities.

The current four models remain supported initial scenarios, rather than define the product's navigation. A global entry point must lead to useful geographic exploration even where quantitative energy analysis is not yet possible.

Product principle: search broadly, calculate only with sufficient inputs, and explain what would enable the next step.

## 2 What the current implementation requires us to change

The following findings come from inspecting the current repository, rather than a live deployment audit:

| Area | Current implementation | Required change |
| --- | --- | --- |
| Entry | `live/index.html` requires one of four crop and service models | Location search first, with exploration as the default intent |
| Initial state | `live/js/app.js` restores a model or defaults to `potato_storage` | Do not silently restore a previous crop into a new exploration session; show an explicit analysis context |
| Start content | `live/js/hero-ui.js` supplies a prominent Rwanda snapshot; the app also lists example districts | Neutral world entry; saved examples become optional case studies |
| Configuration | `live/js/config.js` combines local statistics, commodity details and service models | Separate location data, commodity profiles, process models and equipment assumptions |
| Engine | `live/js/engine.js` selects a model before filtering eligible sites and calculating results | Extract geographic preparation from scenario calculation; provide a genuine exploration result |
| Missing data | The generic country configuration has no production statistics | Keep that safeguard; show supported import and input paths instead of reusing another country's figures |
| Siting | The engine can apply the bundled siting model when inputs exist | Explicitly check geographic, feature and activity applicability before exposing a prediction or evaluation claim |
| Energy | Mapped supply proximity and solar context accompany a selected demand scenario | Keep context separate from supply feasibility or an energy deficit claim |
| Saved cases | The featured snapshot and registered evaluations preserve historical results | Maintain immutable replay and reproduction checks; version all new analysis formats |

## 3 Landing page

Use the attached sketch as the composition idea: a clear search area and short message on the left, with a large interactive globe on the right. Improve its typography, spacing, visual hierarchy and responsive behaviour. It should feel like an operational planning product.

### Suggested copy

- Brand: EnaGIS
- Motto: Mapping Energy. Powering Agriculture
- Headline: Explore energy opportunities in agriculture.
- Supporting text: Choose a place to explore agricultural activity, energy context and opportunities worth investigating.
- Search label: Where would you like to explore?
- Placeholder: Search a place or enter coordinates
- Primary action: Explore area
- Alternative action: Choose on the map
- Secondary action: Open saved analysis

### Behaviour

1. Open on a neutral world view, with no selected country, crop or result markers.
2. Allow place search and map selection. Search suggestions include country and administrative context to distinguish duplicate names.
3. Selecting a search result previews its boundary and offers confirmation. A selected point needs an explicit, adjustable study extent; do not silently treat a point as a district.
4. A country or very large region opens a regional overview or asks the user to select a smaller study area. Do not download every building or run detailed routing over an entire country.
5. Enter the workspace with the confirmed area. Do not automatically calculate potato demand or load the Rwanda snapshot.
6. Put optional saved case studies below the primary entry flow. Name their real location and date within the case, without making them the product's identity.
7. Prefer satellite imagery in the working map when available. Keep a clearly labelled fallback, attribution and visible imagery limitations. A satellite view does not imply that the analysis was inferred from the image.

The globe must use real geographic boundaries. Decorative animation must not suggest that worldwide predictions or measurements already exist. Offer an accessible search route that does not require using the globe.

## 4 New user journey

```text
Choose an area
  -> Explore local evidence and mapped activity
  -> Choose a question
       -> Where should we investigate a particular agricultural energy use?
       -> What would a known operation require?
       -> Which supply options are worth investigating for a defined load?
  -> Select or supply the required inputs
  -> Review assumptions and calculate where supported
  -> Compare results and export a brief with evidence and next checks
```

### A Explore an area

No crop is required. Show mapped agricultural facilities and their recorded activity, roads, settlements, building context, available production datasets and mapped electricity infrastructure. Explain provenance, age and coverage by layer. Buildings are not automatically farms or operating facilities.

Group documented activities into clear categories where source tags support it. Missing facilities mean incomplete knowledge, not absence of agricultural activity. Unknown data coverage cannot be converted into a fabricated completeness percentage.

Show activity cards when there is supporting evidence. Examples: cooling and storage, drying, processing, and water pumping. These are ways to navigate evidence, not claims that all calculations are implemented. Avoid filling every area with the same invented opportunity cards.

Without a selected supported scenario, show an overview and places with documented records to inspect. Do not show a universal demand ranking, kWh figures or a predicted opportunity score.

### B Investigate an agricultural use

Replace the combined dropdown with progressive choices:

| Choice | Meaning | Example |
| --- | --- | --- |
| Activity | The physical operation | Cooling, refrigerated storage, milling or drying |
| Commodity | The material and relevant properties | A supported crop, milk, or a sourced custom profile |
| Operating context | How the operation actually runs | Intake, storage days, moisture change, temperatures, equipment and operating hours |
| Location inputs | Local activity and access | Production, seasonal patterns, catchments or measured site throughput |

Crop selection is optional during exploration. It becomes required when the selected physical model needs commodity properties. A known operator may supply measured throughput instead of estimating it from area production.

Offer a searchable commodity catalogue and a sourced custom profile workflow. Entering a crop name alone does not enable a calculation. Never apply potato properties to all vegetables or maize milling parameters to every processing activity. Distinguish chilled storage from dry warehousing.

Keep the four existing combinations as quick-start presets inside the scenario builder. New crops and activities enter the supported catalogue only after their inputs, equations, units and benchmark cases are reviewed. Irrigation, pumping and other new models are future work until implemented and checked.

### C Compare energy supply options

Treat this as a separate decision after the intended use and load are known. Initial mapped context may show grid proximity and solar conditions. A later comparison may consider grid connection, solar, storage or hybrid configurations where models and inputs exist.

Do not label one option the best solely because a line is nearby or sunlight is strong. A defensible comparison needs load timing and peak power, reliability needs, supply availability, equipment constraints and, for financial comparisons, costs and tariffs. Missing inputs produce conditional findings or an unavailable comparison.

Ask what matters: lower cost, more reliable operation or a stated emissions objective. Show trade-offs and assumptions. Do not introduce an unexplained combined score.

## 5 Evidence and result states

Track readiness per layer, scenario and result. Do not give an entire country a single supported or unsupported label.

| User-facing state | What it means | Permitted output |
| --- | --- | --- |
| Explore available data | Some geographic context is available | Map, source records, evidence gaps and inspection tools |
| More inputs needed | The chosen calculation lacks essential inputs | Specific missing fields, import or manual entry with provenance |
| Estimate available | Required inputs and a reviewed process model exist | Versioned estimates, ranges, assumptions and model applicability limits |
| Locally evaluated | A particular model passed its declared evaluation in this setting | The specific evaluation and its scope; no blanket validation claim |

Data retrieval failure is distinct from no records found and from unknown coverage. OBSERVED or DOCUMENTED still does not mean visited. User inputs retain their source and verification status. Existing siting model performance is never presented as evidence of demand accuracy, discovered operating facilities or universal transfer.

## 6 Comparison and ranking

- Keep site ranking within a declared activity, commodity, season, extent and objective.
- Do not rank mixed activities as investment opportunities by their kWh alone. Higher demand is not greater benefit or commercial viability.
- Compare supported scenarios side by side with matched periods and units, uncertainty, input coverage and missing evidence.
- Do not sum overlapping catchment production or assign the same throughput to multiple processes without an explicit material-flow rule.
- Keep demand, installed supply, an energy deficit, technical feasibility and investment feasibility as separate quantities.
- Preserve current ranking definitions for legacy scenarios. A new prioritisation method requires a separately versioned and evaluated design.

## 7 Technical structure

Proposed interfaces, to implement incrementally rather than replace the application in one rewrite:

| Module | Responsibilities |
| --- | --- |
| Area selection | Resolve names, coordinates or map selections; require study extent; handle geometry limits |
| Geographic evidence | Fetch and normalise sources once; retain dates, licences, errors and provenance |
| Exploration summary | Build context and activity groups without requiring a demand model |
| Location adapters | Local units, periods, boundaries, production datasets and spatial allocation assumptions |
| Commodity registry | Physical properties, units, applicability limits and source references |
| Process registry | Required inputs, equations, thermal/electrical basis, output units and supported commodities |
| Scenario builder | Combine location, activity, commodity, operation and assumptions; validate readiness |
| Model applicability | Enforce declared scope of siting models and distinguish exploratory transfer from evaluated use |
| Calculation engine | Deterministic supported calculations and uncertainty propagation |
| Supply context and comparison | Separate geographic context from any supported design or cost comparison |
| Results and export | Consistent source labels, comparable scenarios, next checks and versioned saved files |

Separate geographic fetch/cache keys from calculation keys. Reuse geography when switching an activity, but invalidate calculations when any model version, source, extent, commodity, parameter or season changes. Cancel stale work when users change area. Version cache entries and exported analyses.

Retain static deployment and Web Workers initially. Decide whether additional services are needed from demonstrated area-size, performance or data-access constraints. No new framework, backend, purchased dataset or global data ingestion is required by this plan.

## 8 Implementation order and exit checks

### Release 1 Global entry and area exploration

- Replace the initial experience with the globe and search composition.
- Separate geographic loading from model-dependent analysis; stop the implicit potato calculation.
- Add overview, boundary confirmation, retrieval states and missing-input states.
- Move saved case studies to a secondary route; keep legacy snapshots unchanged.
- Gate model applicability before showing predictions outside their evaluated scope.

Exit: a new visitor can explore an unfamiliar place without choosing a crop; no results from Rwanda leak into that area; a missing production series still allows useful geographic inspection without fabricated kWh or ranks.

### Release 2 Flexible scenario builder

- Introduce activity, commodity and operation as separate configuration records.
- Adapt the four existing presets into the new builder without altering their scientific definitions.
- Add validation and provenance for user-supplied local production or known-site throughput.
- Add scenario readiness and a comparison layout.

Exit: supported legacy scenarios reproduce their previous outputs with unchanged inputs and parameters. Unsupported crop/activity combinations request the missing requirements rather than silently substituting defaults.

### Release 3 Additional reviewed activities and local data

- Add a location adapter using sourced inputs and evaluate its supported scope.
- Add an additional commodity or process through the declared registry and benchmark path.
- Record adaptation effort and any remaining gaps; do not expand the supported catalogue on appearance alone.

Exit: an additional setting and activity have explicit evidence, reproducible outputs and documented limits. If evidence is insufficient, release only exploration support for that setting.

### Release 4 Supply comparison

- Define the decision objective and required load/supply inputs.
- Add reviewed technical comparisons and, when justified by inputs, cost comparisons.
- Keep context-only outputs available without calling them an optimal design.

Exit: a reviewer can trace each comparison to load, supply, configuration and cost assumptions; missing inputs cannot produce a winner.

## 9 Verification required

Preserve existing engine, siting and hero reproduction checks. Add targeted checks for:

1. Clean landing state versus an explicitly reopened saved analysis.
2. Duplicate place names, coordinate input, point extent, and an oversized selected region.
3. A region outside the existing statistics pack; partial services and no connectivity.
4. True zero versus missing production; no cross-country default substitution.
5. Unknown or unsuitable commodity profiles, incompatible units and missing operating inputs.
6. Known-site throughput versus area-derived allocation.
7. Siting model scope restrictions and contextual interpretation of historical test results.
8. Scenario switching, stale requests, cache isolation and deterministic replay.
9. Exports retaining area, scenario, input dates, evidence status and model versions.
10. Desktop and mobile search, keyboard navigation, focus states and reduced motion; no on-screen presenter instructions.

Before implementation, inspect applicable repository guidance and current tests again. Existing frozen protocols and recorded outcomes remain immutable. New methodological changes must have their own version and evaluation.

## 10 Completion definition

The upgrade is successful when EnaGIS presents a global identity, lets users inspect local evidence without a fixed crop, and offers supported calculations through explicit scenarios. Its usefulness in sparse-data areas comes from partial analysis, transparent unknowns and clear ways to add evidence. It must not promise the same analytical accuracy everywhere simply because every place is searchable.
