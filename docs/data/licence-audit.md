# Phase 2 input rights audit

The [manifest](manifest.json) is the source-by-source record; raw metadata and licence pages are pinned evidence. This audit records the selected terms and output handling as of 7 October 2026. Repository code licensing does not relicense data.

| Inputs | Licence basis | Handling |
|---|---|---|
| AAFC elevator registry, field-crop reporting geometries | Official open-data metadata and [Open Government Licence — Canada](https://open.canada.ca/en/open-government-licence-canada) | Attribution and non-endorsement retained in manifest/index; open derived source tables. |
| Statistics Canada digital boundary service | Service copyright/attribution identifies Open Government Licence | Full digital polygons retained in the normalized boundary database with source hashes. |
| Statistics Canada crop table | [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence) | Attribute the table/date and record adaptation; keep flags, controls and geometry mapping. No claim of endorsement. |
| CGC shipping-point delivery series | [Official open-data dataset metadata](https://open.canada.ca/data/en/dataset/b9157c04-b8e7-42fa-89bb-ffa353b6be8d) identifies Open Government Licence; the selected file comes from the same CGC series | Preserve the series licence basis and original source URL, independently of generic website terms. |
| Geofabrik historical OSM extracts | © OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/), [OSM attribution guidance](https://www.openstreetmap.org/copyright) | Keep the road database separate, retain attribution and source; apply its share-alike/notice requirements when distributing a derivative database. Do not present it as MIT/OGL data. |
| Four CGC licensing PDFs and generic terms page | [CGC non-commercial reproduction terms](https://www.grainscanada.gc.ca/en/terms.html), with separate permission for commercial reproduction | Restricted raw/parsed company records excluded from public outputs and Git. Optional local audit only; commercial redistribution requires permission. The open rebuild skips these sources. |

The CGC open-data portal resource describes an earlier crop-year download, while the publisher's series URL supplies the current historical CSV. The pinned CSV includes 2006–2007 through 2024–2025; the adapter selects exactly the frozen crop-year/category. This relationship is recorded explicitly rather than assigning generic website permission to every CGC file.

Raw snapshots, intermediate caches, large standardized databases and private verification/audit files are ignored by Git. Public repository content consists of code, tiny synthetic fixtures, source/configuration metadata, crosswalk IDs and aggregate audit findings. Private licensing rows never enrich the open registry. Public audit references/counts document restrictions and data quality; they are not a commercial redistribution grant for the reports.

Python dependencies are pinned in `uv.lock`; pydantic/pyproj and their runtime dependencies, Shapely/GEOS, NumPy and pypdf retain their upstream MIT/BSD/LGPL notices in their distributions. The repository does not vendor those binaries. The PBF schema's attribution is recorded in [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Phase 4 additions — 8 October 2026

The [Phase 4 manifest](phase4-manifest.json) records the official 2021 CSD population table
(Statistics Canada Open Licence) and AB/SK full digital CSD boundaries (Open Government Licence
– Canada), with retrieval date, URL, checksum, attribution and intended derived artifacts.
These support an audited CSD-to-CCS population baseline. No restricted licensing rows or private
verification records are included. Road features retain OpenStreetMap attribution and ODbL;
combining them into comparison outputs does not relicense them as repository code. The locked
SciPy/scikit-learn dependencies keep the licence notices distributed with those packages.
