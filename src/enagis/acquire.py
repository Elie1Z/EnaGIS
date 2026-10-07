"""Preparation-only download utility. The analytical pipeline never imports network code."""

import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen

from enagis.data_contracts import Manifest
from enagis.data_io import file_hash, safe_path


def download(url: str, path: Path, expected_hash: str | None = None) -> dict:
    """Never replace a raw snapshot; checksum mismatch requires explicit new versioning."""
    if path.exists():
        actual = file_hash(path)
        if expected_hash and actual != expected_hash:
            raise ValueError(f"existing snapshot checksum mismatch: {path}")
        return {"sha256": actual, "bytes": path.stat().st_size}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    if temporary.exists():
        raise ValueError(f"unfinished acquisition exists: {temporary}")
    import hashlib

    digest = hashlib.sha256()
    try:
        request = Request(url, headers={"User-Agent": "EnaGIS-source-preparation/0.1"})
        try:
            response = urlopen(request, timeout=60)
        except OSError:
            if sys.platform != "win32":
                raise
            # Some federal servers reset Python TLS handshakes; use Windows system TLS.
            quoted_url = "'" + url.replace("'", "''") + "'"
            quoted_path = "'" + str(temporary).replace("'", "''") + "'"
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    "$ErrorActionPreference='Stop'; Invoke-WebRequest -UseBasicParsing -Uri "
                    + quoted_url
                    + " -OutFile "
                    + quoted_path
                    + " -TimeoutSec 60",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            actual = file_hash(temporary)
        else:
            with response, temporary.open("xb") as stream:
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    digest.update(chunk)
                    stream.write(chunk)
            actual = digest.hexdigest()
        if expected_hash and actual != expected_hash:
            raise ValueError(f"download checksum mismatch: {url}")
        temporary.replace(path)
        return {"sha256": actual, "bytes": path.stat().st_size}
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def acquire_manifest(manifest_path: Path, root: Path, skip_restricted=False) -> None:
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    for entry in manifest.sources:
        if skip_restricted and entry.snapshot.redistribution != "permitted":
            continue
        print(f"Preparing {entry.snapshot.snapshot_id}", flush=True)
        result = download(
            entry.snapshot.original_url, safe_path(root, entry.local_path), entry.snapshot.sha256
        )
        if result["bytes"] != entry.byte_count:
            raise ValueError(f"snapshot size mismatch: {entry.local_path}")
