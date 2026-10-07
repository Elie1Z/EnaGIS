# EnaGIS — Codex Development Prompts

## General rule for every phase

The repository does contains the following so i uploaded here so we follow them:

- the EnaGIS project description / PRD;
- `design.md`;
- the current repository and bootstrap/tooling setup;

so,
any decisions, datasets, fixtures and code produced by previous phases.

Treat those as the primary source of truth.

Before changing anything:

1. Read the project description.
2. Read `design.md`.
3. Read `AGENTS.md` or equivalent repository instructions if present.
4. Inspect the existing repository structure, tests, configuration and current implementation.
5. Check what parts of the current phase are already complete.

Do **not** rebuild something that already works merely because you would design it differently.

The current tool stack is a bootstrap, not a permanent restriction. You may recommend or adopt a better tool/library if it materially improves correctness, reproducibility, maintainability, geospatial capability or development speed. Do not introduce dependency churn for cosmetic reasons.

Any new critical dependency must preferably be:
- open-source;
- reproducible/pinnable;
- compatible with the project's clean-machine rebuild;
- usable without requiring a closed hosted service at runtime;
- justified against the existing solution.

### Development mode

This prompt is resumable.

On each run:

1. Determine the **next smallest incomplete task that blocks this phase**.
2. State that task briefly.
3. Inspect only the files relevant to it.
4. Write or update acceptance tests first where applicable.
5. Implement the task.
6. Run the relevant tests and lint/type/static checks available in the repository.
7. Fix failures caused by your change.
8. Do not expand into another major task merely because context remains.
9. Stop with:
   - what changed;
   - files changed;
   - tests/checks run;
   - assumptions or unresolved issues;
   - the next recommended task.

If all exit criteria for the phase are genuinely satisfied, perform a short audit and finish with:

`PHASE COMPLETE`

Do not weaken tests simply to make implementation pass.

Never silently invent scientific assumptions, parameter ranges, thresholds, field evidence or source data. Human-only decisions defined by the project remain human decisions.

Preserve EnaGIS principles including:
- OBSERVED / PREDICTED / ESTIMATED / INFERRED / UNKNOWN evidence labels;
- missing data is not absence;
- UNKNOWN must never silently become zero;
- ranges rather than unsupported precision;
- unlabeled locations are not automatically negatives;
- explicit units;
- explicit CRS;
- reproducible seeds;
- provenance;
- row-count checks after joins;
- mass conservation where applicable;
- no data leakage;
- honest limitations.

---

# PHASE 0 — Product Decision and Architecture Lock

## Objective

Establish a stable foundation before substantial implementation begins.

The purpose of EnaGIS is to help productive-use-energy planning teams decide **which agricultural aggregation/processing locations should be investigated first and how confident we are in those choices**.

This phase must prevent later AI sessions from repeatedly reopening product decisions or restructuring the repository.

## Your job

First inspect the project description, `design.md`, existing decisions and repository.

Determine whether the following are already explicitly decided:

- selected commodity/value chain;
- pilot geography;
- aggregation/processing node types;
- processing step being modelled;
- expected facility/registry source;
- production-data source;
- verification pathway;
- basic energy service being evaluated.

Do not reopen a decision that has already been deliberately frozen unless you find a concrete contradiction that would make implementation invalid.

If commodity selection is still unresolved, evaluate the candidates using the selection rule defined in the project description.

Do not make an unsupported final scientific/product decision on behalf of the team. Instead produce a concise decision packet showing:

- evidence available;
- which gate each candidate passes/fails;
- missing evidence;
- recommended choice;
- consequence of the choice for implementation.

Once the human decision is available or already recorded, make sure the repository reflects it.

## Architecture audit

Verify that `design.md` and the repository architecture support the intended flow:

raw/pinned data  
→ registry  
→ production representation  
→ road/accessibility layer  
→ catchment/allocation  
→ energy requirement  
→ documented supply state  
→ gap classification  
→ baselines/hindcast  
→ uncertainty  
→ ranking  
→ verification  
→ map/shortlist/report

Also preserve the parallel facility-siting experiment.

Define clear module boundaries and interfaces rather than implementing scientific modules now.

Check that modules do not depend circularly on downstream results.

Especially ensure that siting features cannot accidentally consume allocation, capacity, demand or gap outputs.

## Deliverables for this phase

The completed phase should leave the repository with:

- frozen commodity/value-chain decision or an explicit human-decision blocker;
- frozen pilot geography;
- documented node typology;
- clear module map;
- clear major input/output contracts;
- clear ownership of configuration versus code;
- documented important decisions;
- alignment between `design.md` and the PRD.

If appropriate, add/update architecture documentation and decision records.

Do not implement catchment algorithms, ML models, Monte Carlo or UI in this phase.

## Exit criteria

Phase 0 is complete when another developer or fresh Codex session can answer:

- What exactly are we modelling?
- In what geography?
- What is a node?
- What is the processing/service class?
- What goes into each major module?
- What comes out?
- Which decisions are frozen?
- Which decisions remain human-owned?

without guessing.

---

# PHASE 1 — Repository Foundation, Contracts, Tests and CI

## Objective

Create the engineering skeleton that prevents later AI-generated modules from disagreeing about schemas, units, missing values and interfaces.

Do not yet try to build the full analysis.

## Your job

Inspect the existing bootstrap first. Preserve working infrastructure.

Implement or complete the contracts needed for the pipeline.

At minimum evaluate contracts for:

- facility/registry records;
- candidate nodes;
- production observations;
- spatial/admin identifiers;
- travel/accessibility results;
- catchment/allocation results;
- facility capacity;
- energy requirement;
- supply state;
- gap bucket;
- uncertainty output;
- final shortlist/node-card data.

Schemas must make important units explicit.

Do not use ambiguous fields such as:

`capacity`

when the actual meaning needs to distinguish things such as:

`capacity_kg_per_day`,
`tank_volume_l`,
`throughput_tonnes_per_year`, etc.

## Data-quality rules

Build validation around:

- coordinate validity;
- longitude/latitude ordering;
- CRS requirements;
- required identifiers;
- duplicate IDs;
- evidence labels;
- source/provenance fields;
- precision class;
- units;
- UNKNOWN/null handling.

No silent `fillna(0)` or silent dropping of problematic records.

## Toy fixtures

Create very small deterministic fixtures with hand-computable expected results.

Fixtures should eventually support tests such as:

- one production zone and one node;
- multiple nodes competing for production;
- a node with known capacity;
- a node with unknown capacity;
- overflow/unserved production;
- logistics-only node;
- missing facility information.

Keep them intentionally tiny.

## Developer commands

Ensure there is a simple supported way to perform operations such as:

- tests;
- lint/static checks;
- tiny pipeline/smoke test.

Use the existing bootstrap conventions where possible.

Avoid creating five overlapping command systems.

## CI

Ensure CI can execute a lightweight smoke test without requiring the entire national dataset.

CI should catch interface/schema breakage.

## Exit criteria

Phase 1 is complete when:

- core interfaces are explicit;
- toy fixtures exist;
- tests run locally;
- lint/checks run;
- CI can run the small fixture;
- a downstream module can rely on stable schemas rather than guessing column names.

Do not build advanced modelling yet.

---

# PHASE 2 — Data Spine, Registry and Provenance

## Objective

Build a trustworthy path from raw project inputs to standardized data that every later modelling stage can consume.

The main objective is **data reliability**, not sophisticated modelling.

## Your job

Inspect what real datasets are already present.

Implement the smallest ingestion/normalization pipeline necessary for the chosen pilot.

Prioritize:

1. facility/processing registry;
2. administrative boundaries;
3. production statistics;
4. candidate nodes;
5. road/accessibility source inputs needed later.

Additional layers should only be added if already needed by an approved downstream task.

## Registry requirements

Each facility/node record must preserve, where available:

- source;
- source date;
- licence;
- location/geocoding precision class;
- original facility type;
- normalized node type;
- original capacity/throughput value;
- original unit;
- normalized unit only when conversion is defensible;
- stated status;
- evidence label;
- location/existence status.

Do not pretend district-level geocoding is point-level accuracy.

Do not infer facility absence from lack of documentation.

Transit/logistics-only locations must not accidentally become stationary-processing demand nodes.

## Data manifest

Maintain or create the project's data manifest.

For reproducible inputs record appropriate metadata such as:

- dataset name;
- source;
- source URL/reference;
- access/snapshot date;
- licence;
- redistributability;
- checksum/hash where applicable;
- processing step;
- output artifact.

Do not overwrite raw source snapshots with cleaned versions.

## Spatial integrity

Add tests/checks for:

- expected CRS;
- coordinate ranges;
- geometry validity;
- admin joins;
- unmatched records;
- row counts before/after joins;
- duplicates.

Report unmatched or ambiguous locations instead of silently dropping them.

## Runtime reproducibility

The final pipeline must not depend on a web API being live during judging.

Downloading/acquisition may happen as a preparation step, but the reproducible analytical run should use pinned/local inputs according to the project specification.

## Exit criteria

Phase 2 is complete when one command or documented pipeline path can transform the pilot raw inputs into standardized, validated analysis-ready datasets with provenance.

The outputs should be usable by later spatial/model modules without manual dataframe surgery.

---

# PHASE 3 — Walking Skeleton / First End-to-End EnaGIS Run

## Objective

Produce the first **complete vertical slice** of EnaGIS.

Do not optimize individual algorithms yet.

The goal is to prove that the architecture actually connects from source data to a ranked shortlist.

## Required flow

Using the selected pilot and available real data, get this path working:

registry/nodes  
→ production representation  
→ simple accessibility/catchment or assignment  
→ throughput allocation  
→ initial technical energy requirement  
→ documented supply state  
→ gap bucket  
→ ranking  
→ shortlist artifact

Use the simplest scientifically valid implementation allowed by the project description.

Do not insert sophisticated Monte Carlo, complex isochrones or UI polish merely to make this phase look complete.

## Allocation requirements

Even the initial implementation must respect:

- production cannot be double counted;
- allocated production plus explicitly unserved production must reconcile with input production within defined tolerance;
- known capacity constraints must not be silently exceeded;
- unknown capacity is not zero capacity;
- units must be asserted;
- deterministic behavior where relevant.

Add explicit mass-conservation tests.

## Energy requirement

Implement only the minimum energy-requirement path appropriate to the selected commodity/service class.

Technical requirement is not bankable demand.

Do not claim willingness to pay, actual electricity use or facility operational status.

If some coefficients remain human-owned and unavailable, design the interface and use clearly marked configuration/temporary scenario inputs rather than hardcoding unexplained constants.

## Gap classification

Preserve the project's three supply states:

- no documented asset;
- documented asset with known capacity;
- documented asset with unknown capacity.

Preserve honest wording such as:

- undocumented supply;
- undersized;
- verify first;
- unserved requirement.

Do not transform “not documented” into “does not exist.”

## Ranking

Generate an initial deterministic ranking suitable for engineering integration.

Do not present this ranking as the final scientific ranking.

Produce a machine-readable shortlist such as CSV/GeoParquet/GeoPackage according to the design.

## Exit criteria

Phase 3 is complete when a clean invocation can take the current pilot data through the pipeline and produce a real shortlist.

A team member should be able to point to a node and trace:

source data  
→ assigned throughput  
→ energy calculation  
→ supply state  
→ gap classification  
→ ranking output.

This is the critical walking skeleton.

---

# PHASE 4 — Baselines, Hindcast and Facility-Siting Experiment

## Objective

Establish the scientific comparison layer.

EnaGIS must demonstrate whether its additional complexity improves decision quality compared with simpler approaches.

Do not assume sophisticated means better.

## Task group A — Baselines

Implement the applicable project baselines:

- B0: production-based ranking at the relevant administrative level;
- B1: production within a Euclidean catchment/buffer;
- B2: road/accessibility-based catchment production;
- population baseline where defined;
- expert shortlist interface/data representation where available.

Ensure baseline outputs use comparable identifiers and evaluation interfaces.

## Task group B — Hindcast

Implement evaluation against reported facility throughput/volume where available.

Report sample sizes.

Do not claim strong validation from weak data.

If the expected facility-level hindcast dataset is insufficient, implement the fallback specified in the project rather than fabricating observations.

Evaluation should distinguish ranking skill from absolute-volume accuracy.

## Task group C — Facility-siting experiment

Implement the committed siting experiment according to the project description.

Respect all anti-leakage requirements.

Candidate features may include approved label-free variables such as:

- accessibility-weighted production;
- population;
- road characteristics;
- junction/accessibility variables;
- town status;
- distance to processor;
- night lights;

only when the required source data is legitimately available.

Never use downstream allocation, capacity, energy demand or gap outputs as siting features.

Use spatial validation grouped by district/block as specified.

Do not randomly split spatial observations when that violates the methodology.

The model should start with the simpler approved model. Only introduce additional model complexity if there is an evidence-based reason.

Report the experiment even if the result is negative.

## Evaluation

Implement the metrics specified by the project, including the appropriate top-fraction recall, spatial evaluation and interval estimation.

Ensure the keep/kill criterion is recorded before using final results to decide whether a model “wins.”

Do not move thresholds after seeing results simply to produce a positive result.

## Exit criteria

Phase 4 is complete when the repository can answer:

- How does EnaGIS compare with B0/B1/B2/population?
- How well does estimated allocation agree with available observed throughput?
- Does the siting experiment beat its specified baselines?
- How uncertain are those results?
- If it fails, is the failure clearly and honestly reported?

A scientifically negative result still counts as a successful implementation.

---

# PHASE 5 — Monday-Ready Integrated Demo

## Objective

By Monday, 12 October, produce a coherent working EnaGIS demonstration.

This phase is **integration**, not feature expansion.

Do not begin major new scientific components here unless they are required to make the existing vertical slice function.

## Demo flow

A reviewer should be able to see:

open/pinned data  
→ EnaGIS processing  
→ candidate aggregation nodes  
→ estimated requirement / supply evidence  
→ ranked locations  
→ why a specific location appears in the shortlist.

## Map

Implement or complete the minimal static interactive map specified by the project/design.

Prefer the existing planned architecture rather than adding a full web framework or server.

The map should focus on decision-relevant information.

At minimum, where data exists, a ranked node should be inspectable and show information such as:

- node identity/location;
- node type;
- rank;
- evidence status;
- throughput/requirement;
- supply state;
- gap bucket;
- uncertainty/status available at this stage;
- relevant sources;
- verification/pre-visit information.

Do not turn the product into a generic GIS layer explorer.

## Node card

Build a clear node-card representation that answers:

“Why should an energy/site-assessment team investigate this place?”

Do not imply precision the model does not possess.

## Shortlist

Produce a top shortlist file in the project-approved formats.

Ensure its values come from the pipeline rather than a manually curated demo copy.

## Reproducible demo

Create or update concise instructions so another team member can reproduce the demo.

The demo should not depend on secret credentials or a remote server.

Run the smoke pipeline, tests and lint.

## Scope discipline

Do not spend this phase on:

- visual polish;
- animations;
- advanced dashboards;
- authentication;
- backend servers;
- unrelated GIS layers;
- speculative features.

Monday success means **the system works coherently**, not that EnaGIS is finished.

## Exit criteria

Phase 5 is complete when the team can demonstrate, without hand-waving:

1. where the input came from;
2. how EnaGIS processes it;
3. the resulting ranked nodes;
4. evidence behind one selected node;
5. how EnaGIS differs from at least a simple baseline.

---

# PHASE 6 — Strengthen the Scientific Pipeline

## Objective

Replace the simplified assumptions/components of the walking skeleton with the scientifically defensible MVP implementations required before ranking freeze.

Do this incrementally.

Do not attempt every submodule during a single Codex run.

Choose the next incomplete task in this approximate dependency order.

## A. Roads and accessibility

Complete the mode-aware road/accessibility representation required by the design.

Support the approved transport modes and road/path handling.

Keep speeds/configuration externalized as scenario parameters rather than unexplained constants.

Validate CRS and distance/time units aggressively.

## B. Dry/wet scenarios

Implement dry/wet accessibility scenarios.

Road surface and accessibility effects should be configuration-driven and traceable.

Do not invent seasonal multipliers where human/source decisions are still missing.

## C. Capacity-constrained allocation

Complete the production-to-node allocation model.

Test:

- overlapping catchments;
- competing nodes;
- capacity exhaustion;
- overflow;
- unknown capacity;
- no candidate;
- conservation of total production;
- deterministic tie handling.

Support the agreed assignment variants as scenarios rather than silently choosing whichever produces nicer rankings.

## D. Technical energy model

Implement the commodity/service-class energy requirement model specified by the design.

Preserve parameter ranges.

Separate:

- throughput;
- energy intensity;
- standing/auxiliary load;
- processing-at-node fraction;
- dwell/turnover assumptions;
- batch/peak-power calculation.

Do not compute peak power merely as daily kWh ÷ 24 when the project specifies batch-based reasoning.

Keep technical energy requirement separate from willingness to pay or business viability.

## E. Supply states and gap buckets

Complete the three supply states and gap logic.

Capacity units must be reconciled before comparison.

Never convert facility count into energy capacity.

Retain signed margins when required.

## F. Uncertainty / Monte Carlo

Implement the project's uncertainty analysis over the approved uncertain parameters.

Use reproducible seeds/quasi-random sampling as designed.

The main decision outputs are tiers such as:

- Robust;
- Contested;
- Verify-first.

Top-k inclusion frequency is a model stability measure under stated assumptions — not a calibrated probability that a project is viable.

Keep magnitude uncertainty separate from ranking uncertainty.

## G. Ranking

Produce the decisive top-10 using the approved ranking methodology.

For uncertain nodes, expose the most decision-relevant unresolved question when possible.

## H. Secondary MVP/important components

Only after core scientific modules are stable, evaluate project-approved components such as:

- documentation index;
- energy-context second axis;
- value-at-stake affordability screen;
- best visit window;
- other “important” rather than “core” requirements.

Follow the cut ladder if schedule pressure exists.

## Ablation principle

For every significant complexity added, determine whether it actually changes the decision.

Where appropriate compare top-10 membership/ranking before and after the component.

Do not keep complexity merely because it is technically impressive.

## Exit criteria

Phase 6 is complete when the ranking is scientifically ready to freeze:

- capacity-constrained allocation works;
- mass is conserved;
- wet/dry scenarios work;
- energy ranges work;
- supply/gap logic is defensible;
- uncertainty tiers work;
- baselines/hindcast remain available;
- major assumptions are configured and documented;
- final ranking can be regenerated deterministically.

---

# PHASE 7 — Ranking Freeze and Verification Package

## Objective

Freeze the analytical result **before** observing verification outcomes.

Verification must test the ranking rather than modify the ranking retrospectively.

## Ranking freeze

Run the approved ranking pipeline.

Perform integrity checks before freezing:

- correct configuration;
- correct data snapshot;
- reproducible seed;
- tests passing;
- no unexpected data loss;
- no unresolved unit failures;
- no accidental manual edits to shortlist.

Create the required ranking freeze artifacts, including the repository tag/version information and shortlist hash specified by the project.

Do not silently rerank after verification data starts arriving.

## Verification sample

Generate the seeded/stratified verification sample according to the approved protocol.

It should appropriately represent the relevant groups defined by the project, potentially including:

- high-ranked nodes;
- middle-ranked nodes;
- lower-ranked nodes;
- disagreement cases;
- siting-model flagged candidates.

The exact human-approved verification protocol must be used.

Do not invent contact responses.

## Verification schema

Prepare structured data capture for the approved failure modes such as:

- node does not exist;
- undocumented supply exists;
- requirement negligible;
- highly seasonal/not relevant;
- confirmed candidate;
- unknown/unreachable where appropriate.

Keep personal/contact-sensitive verification information private according to the project protocol.

## Analysis code

Implement analysis that can later consume real verification results and compute the approved metrics and confidence intervals.

The code should work with fixture/fake test data before real results arrive, but fake test data must never be mixed with real results.

## No leakage rule

Verification results must not alter `ranking-v1`.

If a later ranking is produced, it must be a clearly separate post-verification analysis/version.

## Exit criteria

Phase 7 is complete when:

- ranking is frozen and identifiable;
- shortlist hash/version is recorded;
- verification sample is frozen;
- verification data schema exists;
- analysis can accept real verification records;
- the team can prove verification did not leak backward into the original ranking.

---

# PHASE 8 — Final MVP, Reproducibility, Report and Defense

## Objective

Turn the scientifically working repository into a submission that another person can rebuild, inspect and defend.

At this stage prefer fixing, simplifying and explaining over adding features.

## A. Verification results

When real verification data exists:

- ingest it through the approved schema;
- compute the planned evaluation;
- report sample size;
- report uncertainty/confidence intervals;
- decompose failure modes;
- compare EnaGIS against relevant baselines.

Do not exaggerate generalization from a small verification sample.

## B. Final map and node card

Polish only what affects comprehension.

The final interface should clearly communicate:

- rank;
- node/location;
- evidence;
- requirement;
- supply state;
- gap category;
- uncertainty tier;
- verification state where appropriate;
- energy context if implemented;
- best visit window if implemented;
- pre-visit question/checklist.

Avoid unnecessary dashboard complexity.

## C. Reproducibility

Perform a clean-machine style audit.

Verify:

- environment dependencies are pinned;
- data inputs are pinned/hashed where required;
- seeds are recorded;
- configuration is versioned;
- manual steps are documented;
- licences are documented;
- small CI fixture passes;
- main commands are understandable;
- no undocumented secret/manual step is necessary.

The target should be as close as practical to a one-command rebuild of generated analysis products.

## D. Documentation

Ensure documentation explains:

- problem and intended user;
- chosen scope/value chain;
- datasets and licences;
- registry;
- spatial methodology;
- allocation;
- energy methodology;
- siting experiment;
- baselines;
- hindcast;
- uncertainty;
- verification;
- limitations;
- scaling/generalization;
- how to reproduce outputs.

Preserve the distinction between OBSERVED, PREDICTED, ESTIMATED, INFERRED and UNKNOWN.

Explicitly state what EnaGIS does **not** claim.

## E. Figures

Generate evaluation and presentation figures reproducibly from code rather than manually editing final numbers into charts.

Where possible keep the approved `make figures` or equivalent workflow.

## F. Defense preparation

Prepare the repository outputs needed for the defense narrative:

problem  
→ decision question  
→ method  
→ baseline comparison  
→ siting experiment  
→ hindcast  
→ verification  
→ ranked shortlist  
→ hero node  
→ limitations  
→ next steps.

Identify a strong hero example:

- first node the model recommends investigating;
- what a simpler baseline would have recommended;
- available verification/evidence;
- why the difference matters.

Prepare evidence for likely questions:

- Why is this useful?
- Where is the ML/GeoAI?
- How do you know the ranking is meaningful?
- Why is this more useful than simply opening QGIS and looking at production?
- What happens if the sophisticated model does not beat B2?
- What does your uncertainty actually mean?
- What does the model not know?

If a simple baseline performs equally well, report that honestly.

## G. Final cut discipline

Do not introduce major architecture changes near freeze unless they fix a correctness/reproducibility problem.

When time is limited, use the project's cut ladder.

Never sacrifice the core evidence chain merely to improve appearance.

## Final MVP audit

Before declaring completion, verify that the MVP contains the required core evidence chain:

- open registry with provenance and precision;
- facility-siting experiment reported win or lose;
- hindcast against baselines;
- capacity-constrained requirement;
- ranges/uncertainty;
- three supply states;
- frozen verification;
- decisive top-10;
- pre-visit information;
- map/node card;
- machine-readable shortlist;
- clean rebuild;
- limitations report.

Run tests, lint and the cleanest available end-to-end reproduction.

Finish by identifying any remaining limitation explicitly rather than hiding it.

When those requirements genuinely pass:

`PHASE COMPLETE — MVP READY FOR DEFENSE`