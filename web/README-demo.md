# EnaGIS · First-visit demo

Open **index.html** in a current browser. All scripts, geometry, evidence and fonts are local.
There is no runtime server, sign-in, API key or internet requirement. Keep the folder together.
If WebGL is unavailable, an interactive schematic map and the complete site cards remain usable.

Click **Start guided demo** for a five-step walkthrough, or explore the three views:

1. Investigate: select any of the ten sites; inspect estimated requirement and the next question.
2. Follow the evidence: trace sources, coverage, assumptions, units and labels.
3. Test against simpler choices: inspect the recorded spatial baseline test and hindcast.

CSV and GeoJSON exports contain the exact pipeline shortlist. Each card offers its complete JSON trace.
The manifest records checksums, historical run IDs, source dates, licences and input hashes.

## Claims

This is a temporary engineering screen of documented Alberta/Saskatchewan primary elevators,
for non-durum wheat storage/aeration. Assignment, inventory and fan coefficients are hypothetical.
Storage tonnes are not electrical capacity. Undocumented fan supply does not mean absent supply.
Rank ties use stable IDs; rank stability has not been assessed. Site existence, current licensing,
inventory, commercial fan duty and electrical supply require verification. Field sample n = 0.
No economics, tariffs, grid proximity, seasonal travel times or uncertainty tiers are invented.

The failed Phase 4 keep rule means **no demonstrated improvement from this proxy-based
accessible-production feature**. It is not evidence against road-catchment logic. With few CAR
blocks, intervals are wide and potentially unstable; read counts and intervals descriptively.
The AAFC registry is close to a census of primary elevators: documentation-bias robustness
cannot be tested here. The shipping-point hindcast is retrospective and diagnostic only;
absolute-volume accuracy is unvalidated. Manitoba is untouched. No worldwide accuracy is claimed.

## Rights

Application code: MIT. MapLibre GL JS 5.12.0: BSD-3-Clause; see vendor licence files.
AAFC / Statistics Canada: attribution and licence URLs are in evidence/sources.json.
Major-road display database: © OpenStreetMap contributors, ODbL-1.0
(https://www.openstreetmap.org/copyright). Its separate roads.geojson derivative and provenance
are supplied. Generalized boundaries/roads are display context, not scientific catchments.
No private licensing documents, personal contact or field-verification records are included.

## Rebuild

From the repository root, after `uv sync --locked --cache-dir .uv-cache`:

```
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py
uv run --offline --locked --cache-dir .uv-cache python scripts/build_demo.py --verify
```

The checked-in evidence archive permits a rebuild without reacquisition or evaluation.
The full pipeline and scientific data acquisition commands are documented in the repository README.
This exporter reads and verifies recorded results; it never refits models or edits frozen parameters.
