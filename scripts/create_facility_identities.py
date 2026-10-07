"""One-time crosswalk construction; future source changes require explicit identity review."""

import json
from pathlib import Path
from uuid import UUID, uuid5

from enagis.adapters.canada import registry_identity_key

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "data/manual/facility-identities-v1.json"
if target.exists():
    raise SystemExit(
        "Identity crosswalk exists; review and version changes rather than regenerate."
    )
namespace = UUID("b4906b7d-b128-4f91-bd1c-6ee065ac45b0")
source = json.loads((ROOT / "data/raw/phase2/aafc-elevators-2024.geojson").read_bytes())
rows = []
for feature in source["features"]:
    properties = feature["properties"]
    if properties["PR"] in ("AB", "SK", "MB") and properties["Elevator_type"] == "Primary":
        key = registry_identity_key(properties)
        identity = str(uuid5(namespace, key))
        rows.append(
            {
                "identity_key": key,
                "facility_id": f"ca:facility:{identity}",
                "node_id": f"ca:node:{identity}",
                "initial_source_record_id": f"aafc-elevators-2024:{properties['OBJECTID']}",
            }
        )
if len({row["identity_key"] for row in rows}) != len(rows):
    raise SystemExit("Duplicate identity keys require review")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(
    json.dumps(
        {
            "version": "1",
            "method": (
                "UUID5 assigned once to source identity tuple; "
                "maintained crosswalk is authoritative. "
                "No fuzzy deduplication or human verification claimed."
            ),
            "rows": sorted(rows, key=lambda row: row["facility_id"]),
        },
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"Assigned {len(rows)} stable facility/node IDs")
