# 0007 — Phase 5 offline evidence presentation

Status: **implemented presentation integration**, 8 October 2026. The user authorized Phase 5
and requested a compelling, seamless guided demonstration. Decisions 0003–0006 and the
registered scientific method are unchanged.

## Implementation choices

Use plain HTML/CSS/JavaScript with vendored MapLibre GL JS 5.12.0 (BSD-3-Clause and bundled
dependency notices). This is the PRD's static-map architecture: no application framework,
runtime backend, account, secret or hosted tile service. The initial view contains only the
exact pipeline top ten. Cards start with the pre-visit question and distinguish estimated fan
requirement, observed storage, inferred documentation status and unknown electrical margin.

The five-step presenter guide moves through the decision, selected site, source chain,
recorded baseline test and actionable verification visit. It does not obscure the map/card.
There are no invented pillars, energy deficits, operational urgency, economic values,
seasonal travel times, grid classes or Robust/Contested tiers. No new scientific data source
is acquired. MapLibre is a software dependency, not a scientific input.

The map uses only existing pinned AB/SK province/SADR boundaries and major OSM road ways.
Boundary simplification of 1,000 m and road simplification of 250 m in EPSG:3347, then
EPSG:4326 display coordinates rounded to five decimals, reduce presentation size only.
Source geometry and all scientific outputs remain unchanged. Reporting-region shading is
labelled explicitly; it is not a catchment. Nearby number labels may separate visually;
small dots retain source coordinates and card precision remains P2. A keyboard-accessible
schematic map supports browsers without WebGL. Manitoba nodes, roads and outcome partition
remain outside the demo.

## Evidence and rebuild boundary

`scripts/build_demo.py` verifies Phase 3 and Phase 4 artifacts, asserts the comparison refers
to the same historical Phase 3 index, and copies their permitted public results to
`demo/evidence/`. Only named allowed artifacts are copied; private licensing documents,
personal data and private verification are excluded. The selected source snapshots must
permit redistribution. OSM roads remain a separate ODbL derivative with attribution and
downloadable geometry; the composite context includes the same ODbL road content.

Version the portable demo/evidence bundle after this explicit rights review. This is an
exception to the ordinary generated-output ignore rule, enabling immediate offline opening
and a reproducible presentation rebuild without national downloads or model evaluation.
The source manifest, vendor manifest and demo checksums travel with it. The artifact index
captures historical run IDs; this is presentation of those runs, not a new scientific run.
Presentation code lives outside `src/enagis`, preserving the registered scientific code hash.

The Phase 4 KILL verdict and its exact proxy-specific interpretation remain visible.
The CCS siting comparison is separate from the elevator engineering shortlist and the
shipping-point hindcast. The latter remains retrospective and diagnostic. Field sample
n = 0; no expert shortlist, metered validation or transfer result is invented.

## Verification limits

Automated tests check offline rebuild, artifact tampering, join identity/rank consistency,
null electrical margins, historical-run mismatch, licences and output-directory protection.
The existing tiny synthetic pipeline remains the CI smoke path. Desktop/mobile browser
checks cover the guide, selection, search, downloads and schematic fallback. A clean rebuild
is mechanically demonstrated; no independent human usability or clean-machine sign-off is
claimed. Those reviews and commercial/field scientific gates remain future work.
