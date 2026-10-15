# FAQ for judges

Short answers, each with a link to the evidence.

**What is EnaGIS in one line?** A reproducible screening shortlist of agricultural storage sites
to investigate first for productive-use energy, with an evidence label on every number.

**Which OSEAS deliverables are here?**
(1) ML/GeoAI pipeline: two registered spatial siting tests. Canada, Phase 4: KILL, reported. Rwanda,
Phase 4R in EnaGIS Live: KEEP, +23.9 points over the best simple rule ([phase4r-results](phase4r-results.md)).
(2) Interactive map: `live/index.html` (any place, seven lenses) and `app/index.html` (the Canadian pilot,
offline, four lenses).
(3) Documentation: [method](method.md), [data catalogue](data-catalogue.md),
[validation](validation.md), [scaling](scaling.md), [limitations](limitations.md).

**How do I run it?** Open `app/index.html`. To rebuild: three commands in the [README](../README.md).

**Where is the AI?** In three places:
- Building footprints come from Google's and Microsoft's deep-learning detectors, via Overture Maps.
- Our siting model scores every 1 km square from roof sizes, roads and settlement structure. In Rwanda,
  with each district hidden in turn, it puts 73.1% of documented collection and processing points in the
  top 10% of their district, against 49.3% for counting buildings. That is KEEP under a rule written
  before the test ([phase4r-results](phase4r-results.md)).
- In Canada a different model lost to production-only by 4.05 points (KILL). We report both.

**Why not YOLO, XGBoost or Earth Engine, as the brief suggests?** We tested them rather than assume.
- **XGBoost** ran under a protocol hashed before scoring. On Rwanda's held-out districts it found 64.2% of
  documented sites against 73.1% for our logistic model: −9.0 points (−15.1 to −3.3). We kept logistic
  ([phase4x-results](phase4x-results.md)).
- **YOLO** needs open sub-metre imagery over labelled facilities. None of the seven African and South-Asian regions we
  scouted has it: OpenAerialMap covers no labelled point, and Maxar Open Data is non-commercial
  ([second-site-scouting](second-site-scouting.md)).
- **A footprint classifier at the one site with enough labels**, 830 surveyed grain mills in Njombe, Tanzania, did not
  beat "closest to a major road": +1.6 points (−0.3 to 3.4), KILL ([phase4n-results](phase4n-results.md)).
- **Earth Engine's Sentinel-2** is 10 m imagery, too coarse for a cold room. We did not test it. The full "not tested"
  list is in the [second-site page](second-site.md).

**Is the top 10 right?** Unknown. It comes from unapproved screening ranges, and nothing has been
field-verified (n = 0). The siting model is tested only against facilities documented in open maps.

**Why Canada?** It was the only open setting where the method could be *tested* end to end. See
[scope-and-transfer](scope-and-transfer.md), which also gives the path to an energy-access region.

**Why so many UNKNOWNs?** 562 of 4,176 labelled fields across 261 sites (13.5%). Of those
UNKNOWNs, 46% are electrical capacity, which no open source publishes, and 53% need a method
change we have proposed but not adopted. See the [evidence ledger](evidence-ledger.md).

**Can I contribute?** Yes. See [CONTRIBUTING](../CONTRIBUTING.md) and [help-wanted-data](help-wanted-data.md).

**Is it open?** Code MIT; data under its source licences (OGL-Canada, StatCan Open Licence,
ODbL for OSM-derived roads). No restricted data in public outputs.
