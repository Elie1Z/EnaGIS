"""Offline hashing, path validation and deterministic artifact serialization."""

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from enagis.contracts import Artifact, RunMetadata
from enagis.data_contracts import Manifest


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes project root: {relative}")
    return path


def verify_manifest(manifest: Manifest, root: Path, skip_restricted=False) -> dict[str, Path]:
    paths = {}
    for entry in manifest.sources:
        if skip_restricted and entry.snapshot.redistribution != "permitted":
            continue
        path = safe_path(root, entry.local_path)
        if not path.is_file():
            raise ValueError(f"missing pinned snapshot: {entry.local_path}; run acquire first")
        if path.stat().st_size != entry.byte_count or file_hash(path) != entry.snapshot.sha256:
            raise ValueError(f"snapshot checksum/size mismatch: {entry.local_path}")
        paths[entry.snapshot.snapshot_id] = path
    return paths


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, BaseModel):
        data = data.model_dump(mode="json")
    path.write_text(
        json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_table(path: Path, metadata: RunMetadata, rows: list, row_type):
    artifact = Artifact[row_type](metadata=metadata, rows=rows)
    write_json(path, artifact)
    return {"path": path.name, "rows": len(rows), "sha256": file_hash(path)}
