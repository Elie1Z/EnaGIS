# EnaGIS global redesign brief

Copy the brief below into the design AI. Pair it with the attached landing-page sketch and `docs/enagis-global-exploration-upgrade-plan.md`.

## Brief

Redesign EnaGIS as a professional agricultural energy planning platform that can expand across locations, crops and activities. Create an original, polished design using the sketch as a composition reference, not a literal drawing to reproduce. Improve the hierarchy, spacing, typography and interactions.

### Product and brand

EnaGIS helps users explore geographic evidence, investigate agricultural energy requirements and identify places worth checking. It uses maps, local data, explicit models and uncertainty. Rwanda is an existing case study; it must not define the homepage or become the default location.

Use the real EnaGIS logo, its green and navy colours, and the exact motto:

Mapping Energy. Powering Agriculture

Use existing brand assets at `live/assets/brand/`. Retain their proportions. Use the established Inter/Fraunces typography where it serves the new composition. Identify the creator as Dynamis if needed.

### Landing composition

- Left: concise message and a prominent, usable location search.
- Right: a large globe with accurate geography and restrained, smooth motion.
- Heading: Explore energy opportunities in agriculture.
- Supporting text: Choose a place to explore agricultural activity, energy context and opportunities worth investigating.
- Search label: Where would you like to explore?
- Search placeholder: Search a place or enter coordinates
- Primary action: Explore area
- Alternative: Choose on the map
- Secondary: Open saved analysis
- Optional real case studies below the main entry flow, with dates and scope.

Do not preselect a country, crop or process. Do not invent global results, glowing opportunity markers or statistics to decorate the globe. On mobile, give the search priority and simplify the globe. Provide a keyboard-accessible alternative and respect reduced motion.

### Workspace and analysis flow

After the user confirms an area and its extent, open an evidence overview with the selected area visible. Prefer satellite imagery when available, with attribution and a clearly labelled fallback.

Users can explore mapped agricultural activity, access, energy infrastructure, datasets and gaps without choosing a crop. Then they can choose an activity, commodity and operating context to build a supported scenario. Cooling, refrigerated storage, milling and drying are current starting activities; additional models must be represented as unavailable until implemented and reviewed.

Replace the fixed combined menu such as Cold storage / Irish potato with progressive choices. Offer existing combinations as quick presets inside the scenario builder. Include a clear route for sourced local inputs and known-site throughput. A custom commodity name alone cannot enable a calculation.

Distinguish these tasks:

1. Explore an area and its evidence.
2. Investigate a specific agricultural energy use or known operation.
3. Compare energy supply options for a defined load, where sufficient inputs exist.

Do not make users complete a long setup form before they can see a map. Ask for inputs when they become relevant. Keep the selected area and active scenario visible, and make it easy to change either.

### Results and honest states

Design populated, partial-data, missing-input, loading and failed-service states. Distinguish absent records from unavailable data. Show what can be explored now and what is needed for a calculation.

Use short language in the primary interface. Place technical parameters and provenance in expandable details. Preserve evidence labels, uncertainty and model applicability. A mapped facility is not automatically verified; a nearby line is not a confirmed connection.

Do not display demand rankings before a supported scenario exists. Do not label solar or another supply option best from map context alone. Do not compare unrelated activities using an unexplained overall score. No fabricated accuracy, cost savings or global coverage claims.

### Visual quality

Aim for the clarity and finish of a professional planning product: a strong map composition, readable type, deliberate whitespace, restrained panels and consistent controls. Motion should help users follow search, area selection and results; it should not delay useful interaction. Keep primary actions easy to find and the map legible.

Preserve standard map attribution. Avoid unnecessary popups, giant statistic cards and excessive decorative gradients. Include no demo badges, presenter steps, click-here instructions or fake functioning controls.

### Required design output

Provide coherent desktop and mobile views for:

- Landing page with search and globe.
- Search suggestions and boundary confirmation.
- Area overview with partial or missing evidence.
- Activity and commodity selection with scenario readiness.
- A supported scenario result, selected-site detail and evidence view.
- Side-by-side supported scenario comparison.
- A known-operation input flow.
- Unavailable model or insufficient-data state with a useful next step.

Explain the interaction flow and identify which screens rely on existing functionality versus new engineering. Treat supply optimisation and unimplemented process models as future capabilities. Do not create a cosmetic redesign that keeps the old country-and-crop assumption underneath.

If implementing within the repository, inspect its guidance and current architecture first. Use incremental modules, preserve saved-case replay and recorded scientific results, and follow the release sequence and acceptance checks in the upgrade plan. Do not deploy or replace the existing application as part of a design-only task.
