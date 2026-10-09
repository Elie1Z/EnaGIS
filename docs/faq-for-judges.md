# FAQ for judges

Short answers. Longer, harder questions with evidence: [challenger-qa.md](challenger-qa.md).

**What is EnaGIS in one line?** A reproducible screening shortlist of agricultural storage sites
to investigate first for productive-use energy, with an evidence label on every number.

**Which OSEAS deliverables are here?**
(1) ML/GeoAI pipeline: a preregistered spatial siting experiment (result KILL, reported).
(2) Interactive map: `app/index.html`, offline, four lenses.
(3) Documentation: [method](method.md), [data catalogue](data-catalogue.md),
[validation](validation.md), [scaling](scaling.md), [limitations](limitations.md).

**How do I run it?** Open `app/index.html`. To rebuild: three commands in the [README](../README.md).

**Where is the AI?** The siting model ([validation](validation.md)). It lost to a production-only
baseline by 4.05 percentage points under a rule frozen before we looked. We kept the simpler
baseline.

**Is the top 10 right?** Unknown. It comes from a temporary, unapproved energy scenario, and
nothing has been field-verified (n = 0).

**Why Canada?** It was the only open setting where the method could be *tested* end to end. See
[scope-and-transfer](scope-and-transfer.md), which also gives the path to an energy-access region.

**Why so many UNKNOWNs?** 562 of 4,176 labelled fields across 261 sites (13.5%). Of those
UNKNOWNs, 46% are electrical capacity, which no open source publishes, and 53% need a method
change we have proposed but not adopted. See the [evidence ledger](evidence-ledger.md).

**Can I contribute?** Yes. See [CONTRIBUTING](../CONTRIBUTING.md) and [help-wanted-data](help-wanted-data.md).

**Is it open?** Code MIT; data under its source licences (OGL-Canada, StatCan Open Licence,
ODbL for OSM-derived roads). No restricted data in public outputs.
