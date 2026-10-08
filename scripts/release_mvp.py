"""One-command offline rebuild and deterministic portable MVP-defense archive."""

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from enagis.data_io import file_hash, write_json
from scripts.build_mvp import ROOT, build
from scripts.generate_figures import generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/mvp-release")
    parser.add_argument("--check", action="store_true", help="Run all Python tests, lint and smoke")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "outputs").resolve()):
        raise ValueError("Release archives must be written under outputs/")
    if args.check:
        for command in (
            ["pytest"],
            ["ruff", "check", "."],
            ["ruff", "format", "--check", "."],
            ["enagis", "smoke", "--fixture", "tests/fixtures/phase1.json"],
        ):
            subprocess.run([sys.executable, "-m", *command], cwd=ROOT, check=True)
    application = build(ROOT / "app")
    figures = generate(ROOT / "docs/figures")
    output.mkdir(parents=True, exist_ok=True)
    files = {p.relative_to(ROOT).as_posix(): p for p in (ROOT / "app").rglob("*") if p.is_file()}
    for name in (
        "docs/phase8-method-report.md",
        "docs/phase8-presenter-guide.md",
        "docs/phase8-acceptance.md",
        "docs/spec/regional-view-package.md",
        "THIRD_PARTY_NOTICES.md",
        "docs/audits/phase8.json",
        "docs/audits/phase8/browser-acceptance.json",
    ):
        files[name] = ROOT / name
    for p in (ROOT / "docs/figures").iterdir():
        if p.is_file():
            files[p.relative_to(ROOT).as_posix()] = p
    archive = output / "EnaGIS-MVP.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, path in sorted(files.items()):
            item = zipfile.ZipInfo("EnaGIS/" + name, date_time=(2000, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            bundle.writestr(
                item, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )
    audit = {
        "date": "2026-10-09",
        "application": application,
        "figures": figures,
        "archive_sha256": file_hash(archive),
        "archive_files": len(files),
        "scientific_completion": False,
        "remaining": [
            "approved commercial parameters and real Phase 6 exit",
            "real ranking-v1 freeze and participant",
            "real verification outcomes",
            "independent rebuild review and measured regional transfer",
        ],
    }
    write_json(output / "release.json", audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
