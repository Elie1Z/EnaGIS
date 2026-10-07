# 0002 — Global adaptation and data-driven pilot selection

Status: **user-authorized product direction**, 7 October 2026. This decision supersedes the Rwanda-only candidate framing and the need to ask the user for a preferred pilot location. [Decision 0003](0003-benchmark-lock.md) now freezes the first development benchmark.

## User direction

The initial location can be anywhere in the world that provides strong data for training, reasoning and evaluation. The intended product should adapt quickly and perform well in other locations on the world map. The earlier instruction to keep the candidate choice open is clarified: geography may be selected on evidence rather than personal preference.

## Decision

Build a reusable geospatial screening pipeline, prove it on one data-rich commodity/service case, then measure transfer to an untouched region. Select the first benchmark using the PRD's data gates and best-candidate fallback, expanded to international candidates. Decision 0003 selects Canadian Prairie wheat storage/aeration for development; scientific readiness remains conditional on the recorded evidence gates.

The final PRD remains the scientific reference except where this user direction changes geographic scope. Its Rwanda milk no-go is a Rwanda data finding. Its facility, throughput, verification, energy, baseline and uncertainty requirements still apply. Preserve the supplied PRD verbatim and record scope changes here.

## What adaptation requires

1. A region package supplies pinned/licensed data, administrative IDs, boundaries/CRS, source adapters, consistent units and local assumptions.
2. One canonical feature schema supports the siting experiment. Separate the feature construction, fitting, evaluation and prediction interfaces. Keep allocation, capacity, demand and gap results outside siting features.
3. Spatial validation tests generalization within the benchmark. A separate untouched region tests transfer. Register outcomes, blocks and keep/kill rules before fitting; respect at least 60 usable positives and six spatial blocks or report feasibility.
4. Fit or recalibrate locally when evidence supports it. Compare against simple local baselines. Record required local data and manual work so adaptation speed can be measured.
5. A new commodity needs sourced processing physics and coefficients. A new climate/transport system needs local scenario parameters. Neither is inferred solely from latitude/longitude.

## Phase scope

The first implementation remains one commodity and one service class. Global reuse is an architecture requirement; worldwide ingestion and simultaneous multi-commodity training are outside the first MVP. Heavy training is justified only by measured improvement over baselines. Regularized logistic regression remains the PRD starting model; increased model complexity requires evidence.

## Remaining evidence work

The exact grain/service and development/transfer footprints are resolved in decision 0003. Resolve source integrity, shipping-point joins, commercial energy parameters and committed verification participation at the later-phase gates in the completion audit. No real shortlist or global accuracy claim is established by a scope decision.
