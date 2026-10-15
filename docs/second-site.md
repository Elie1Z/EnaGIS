# Second site

This page holds everything about running the challenge's suggested tools outside Rwanda. Its numbers are not Rwanda
numbers and are never mixed with them. Every number here is in an audit file. Field verification: n = 0.

## 1. Where could the tools run at all? (scouting)

[second-site-scouting.md](second-site-scouting.md) · [audit](audits/second-site-scouting.json) ·
`node scripts/scout-sites.mjs`

We checked seven candidate regions (13 districts) in India, Bangladesh, Kenya, Uganda, Tanzania and Ethiopia. For
each one we recorded the documented processing and storage points (counted with the app's own rules), their spread
over sub-districts, the Overture footprints, the open imagery with its resolution and licence, and national
electrification.

| Candidate | Processing/storage points documented | Image detector (C2) | Footprint classifier (C1) |
|---|---:|---|---|
| India, Uttar Pradesh potato belt (Agra, Firozabad, Hathras) | 13 | fail | fail |
| India, West Bengal potato belt (Hooghly, Purba Bardhaman) | 18 | fail | fail |
| Bangladesh (Munshiganj, Bogura) | 64 | fail | fail |
| Kenya (Nyandarua, Meru) | 5 | fail | fail |
| Uganda (Kabale) | 3 | fail | fail |
| **Tanzania (Njombe)** | **882** (881 from one WFP 2021 mill survey) | fail | **pass** |
| Ethiopia (East and West Gojjam) | 2 | fail | fail |

- **No region passes the image-detector checklist.** That needs open imagery at 1 m or finer, under a licence that
  allows training and publishing, covering at least 300 labelled facilities.
  - **OpenAerialMap:** images exist over only 4 of the 13 districts: 48 in Munshiganj, 2 in Nyandarua, 1 in Meru
    and 1 in Njombe. None covers a labelled processing or storage point.
  - **Maxar Open Data:** CC-BY-NC (non-commercial only), and no event overlaps a candidate.
  - **Open Cities AI:** covers 10 cities, none of them a candidate, and its labels are buildings only.
  - **Sentinel-2:** 10 m resolution.
- **Footprint classifier:** only Njombe passes, because a single field survey mapped its grain mills.

## 2. The one run the data allowed: Njombe grain mills (Phase 4N, KILL)

[phase4n-results.md](phase4n-results.md) · [protocol](spec/phase4n-protocol.md) (SHA-256 `d3a9cc02…`, frozen before
download) · [audit](audits/phase4n-evaluation.json)

The data: 673,866 footprints and 830 surveyed mills matched to a footprint, with 6 district councils each held out in
turn. In the top 1% of each held-out council's footprints:

| Ranking | Share of mills found |
|---|---:|
| Logistic footprint model | 5.7% |
| XGBoost | 5.8% |
| Closest to a major road | 4.1% |
| Largest roof first | 2.8% |

**KILL:** the model's margin over the road rule is +1.6 points, with an interval (−0.3 to 3.4) that includes zero.
XGBoost is not better than logistic. On footprints from the Google and Microsoft detectors alone, the model only ties
the road rule.

## 3. What we did not test

- **An image detector (YOLO-type).** No open, licence-compatible sub-metre imagery covers labelled facilities in any
  candidate. There is also no GPU on the team machine.
- **Earth Engine / Sentinel-2 time series** (vegetation-based siting, as in the 2019 Bihar paper). It is a different
  question, about where storage should be rather than where it is, and it has no open label set.
- **The India NHB cold-storage lists.** They have no coordinates, date from 2000–2005 sanctions, and many addresses
  give only the district. Fuzzy geocoding would make them weak labels, so they were not used.
- **Tuned XGBoost.** Settings were fixed in advance. A tuned comparison needs a new protocol with inner cross-validation.
- **Labels written only in Devanagari, Bengali or Amharic.** The app's classification rules read English, French and
  Kinyarwanda names; where `name:en` exists we use it. The number of unreadable elements per district is in the
  scouting audit.
- **Cold storage at a second site.** Too few cold stores are documented openly in any candidate: 3 in Agra, 1 in
  Hathras, 3 in Hooghly, 3 in Munshiganj and 2 in Bogura.
