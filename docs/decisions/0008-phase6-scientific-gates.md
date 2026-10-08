# 0008 — Phase 6 engine and scientific execution gates

Status: **engineering implementation; scientific choices pending review**, 8 October 2026.

The user requested the complete Phase 6. This authorizes implementation, testing and source
audits. It does not supply the reviewed scientific values required by AGENTS.md, decision 0003
and the Phase 0 handoff gates. The detailed Phase 4 approval applies only to its registered
experiment; it does not approve transport speeds, seasonal effects or commercial fan ranges.

## Incremental implementation

Implement A/B routing, C allocation, D/E energy and supply, then F/G uncertainty/ranking as
separate kernels in `enagis.science`. Exercise them together only with unmistakably synthetic
inputs until the real configuration is reviewed. The shipped review JSON has null decisions,
not borrowed Phase 3 coefficients with a new scientific label. No distribution is generated
by putting an arbitrary percentage around a temporary value.

The frozen pilot remains AB/SK development, non-durum wheat, primary elevators and ambient-air
aeration. Other modes are supported by configuration for method testing; suitability for bulk
wheat is a scientific decision. Manitoba outcomes and roads are not consumed by this work.
No crop raster or new empirical dataset is acquired. Reference documentation was consulted
to check semantics and equations, without treating it as site measurements.

## Proposed methods implemented, not approved for real ranking

- Directed OSM way topology, EPSG:3347 metres, minutes, explicit class speeds and dry/wet surface
  factors. Mode-specific restrictions override general access. Unsupported restrictions and
  unconfigured surfaces are excluded and counted. Legal speed tags cap scenario speed; they
  are not measurements. Snaps include distance and explicit connector travel time.
- Two assignment variants: maximum total served mass followed by minimum tonne-minutes;
  and nearest-first across sorted origin-node arcs. Capacity is shared across all origins.
  Variant comparisons are descriptive; the engine never picks the best-looking result.
- Inventory and simultaneous fan duty, explicit treated fraction and auxiliary load. Output
  energy is for one cooling cycle. No annual-energy or startup-power inference is added.
- Fixed or triangular parameter distributions, named shared-quantile groups, power-of-two
  scrambled Sobol draws and identical draws across cases. Shared groups impose comonotonic
  dependence; they do not learn it. Between-group independence and global coefficients must
  be reviewed. This implementation cannot express arbitrary copulas or physical fan curves.
- Equal case weighting, top-k inclusion then median technical kW then node ID. Robust requires
  the approved inclusion threshold in every case. Unresolved source/supply issues override
  stability and produce Verify-first. This is a proposed investigation policy, not investment
  merit, a probability of viability or calibrated truth.

These choices have explicit configuration/review boundaries. Scientific execution requires
human approval of the data, methods, distributions, transport profiles and ranking policy.
The fixture switch cannot authorize scientific data or fabricate scientific approvals.

## Limits and exit

The current OSM way adapter omits node barriers and turn-restriction relations. Its road engine
is a screening network, not navigation or legal freight routing. Review network completeness
and commodity-specific movement before real use. A reviewed origin adapter is still required:
the engine accepts conserved parent-to-point fractions but does not silently choose where
within an SADR production occurred. The full Prairie graph has not been performance-qualified
for this implementation. A real-data run must also assess excluded paths and source coverage.

Historical Phase 4 metrics and hindcast remain available for the earlier model. They do not
validate the new allocation/energy engine. Approve a new comparison protocol before scoring
its predictions; never retune the registered experiment or use Manitoba for selection.

No final scientific shortlist or Phase 7 freeze is created. Secondary context, affordability,
documentation scoring and visit-window scoring remain deferred because their sources and
rules have not been approved. Phase 6 closes only after the review packet is resolved, real
inputs are prepared under it, real runs replay, ablations are reviewed and the exit is signed.
