"""First pin only: download catalog sources and record exact immutable byte fingerprints.

Subsequent preparation uses `python -m enagis acquire` and the committed manifest.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

from enagis.acquire import download, safe_path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "configs/sources-canada.json").read_bytes())
manifest_path = ROOT / "docs/data/manifest.json"
if manifest_path.exists():
    raise SystemExit("Manifest already pinned; use acquire, or explicitly version a new catalog.")


def prepare(entry):
    print(f"Preparing {entry['id']}", flush=True)
    try:
        pinned = download(entry["url"], safe_path(ROOT, entry["local_path"]))
    except Exception as error:
        print(f"FAILED {entry['id']}: {error}", flush=True)
        return {"error": entry["id"], "reason": str(error)}
    snapshot = {
        "snapshot_id": entry["id"],
        "publisher": entry["publisher"],
        "original_url": entry["url"],
        "retrieved_on": datetime.now(UTC).date().isoformat(),
        "effective_on": entry["effective_on"],
        "sha256": pinned["sha256"],
        "licence": entry["licence"],
        "licence_url": entry["licence_url"],
        "redistribution": entry["redistribution"],
        "processing_step": entry["processing_step"],
    }
    return {
        "dataset_name": entry["name"],
        "snapshot": snapshot,
        "local_path": entry["local_path"],
        "byte_count": pinned["bytes"],
        "role": entry["role"],
        "effective_date_precision": entry["effective_date_precision"],
        "attribution": entry["attribution"],
        "licence_evidence_url": entry["licence_evidence_url"],
        "output_artifacts": entry["output_artifacts"],
    }


with ThreadPoolExecutor(max_workers=3) as pool:
    sources = list(pool.map(prepare, catalog["sources"]))
failures = [entry for entry in sources if "error" in entry]
if failures:
    raise SystemExit(json.dumps(failures, indent=2))
manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(
    json.dumps({"manifest_version": "1.0.0", "sources": sources}, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(f"Pinned {len(sources)} source files", flush=True)
