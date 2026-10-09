"""Rebuild the final offline application from unchanged, verified public evidence."""

import argparse
import json
import re
import shutil
from pathlib import Path

from enagis.data_io import file_hash, safe_path, write_json
from scripts.build_demo import ROOT, export, read, verify_demo


def build(output):
    output = output.resolve()
    if (
        output == ROOT.resolve()
        or output == (ROOT / "demo").resolve()
        or any(
            output.is_relative_to((ROOT / name).resolve())
            for name in (
                "src",
                "configs",
                "data",
                "docs",
                "web",
                "demo",
                "tests",
                "scripts",
                ".git",
            )
        )
    ):
        raise ValueError("MVP build must not overwrite source or historical evidence")
    assets = ROOT / "web/assets"
    provenance = read(assets / "manifest.json")
    for entry in provenance["sources"]:
        if file_hash(safe_path(assets, entry["path"])) != entry["sha256"]:
            raise ValueError("Interface asset checksum mismatch: " + entry["path"])
    if file_hash(assets / "world.json") != provenance["world_sha256"]:
        raise ValueError("World-navigation checksum mismatch")
    export(
        ROOT / "demo/evidence/phase3",
        ROOT / "demo/evidence/phase4",
        read(ROOT / "demo/evidence/context.json"),
        output,
        read(ROOT / "demo/evidence/sources.json"),
    )
    initial = (output / "index.html").read_text(encoding="utf-8")
    data = json.loads(
        re.search(
            r'<script id="demo-data" type="application/json">(.*?)</script>',
            initial,
            re.S,
        ).group(1)
    )
    rows = read(ROOT / "demo/evidence/phase3/nodes.json")["rows"]
    # Preserve the required evidence fields; full original rows remain in evidence/phase3.
    fields = (
        "node_id",
        "node",
        "facility",
        "province",
        "rank",
        "requirement",
        "storage_capacity",
        "assigned_tonnes_per_reporting_period",
        "inventory",
        "supply",
        "gap",
        "verification_question",
    )
    candidates = [{key: row[key] for key in fields} for row in rows]
    context = data.pop("context")
    data["comparison"]["siting"] = {
        key: data["comparison"]["siting"][key]
        for key in (
            "primary",
            "interpretation",
            "power",
            "cohort_units",
            "documented_positive_units",
            "positive_blocks",
            "status",
            "transfer_evaluated",
        )
    }
    data["comparison"] = {key: data["comparison"][key] for key in ("siting", "hindcast")}
    world = read(assets / "world.json")
    template = (ROOT / "web/mvp/index.html").read_text(encoding="utf-8")
    for key, value in (
        ("__DATA__", data),
        ("__WORLD__", world),
        ("__CANDIDATES__", candidates),
        ("__CONTEXT__", context),
    ):
        encoded = json.dumps(value, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
        template = template.replace(key, encoded.replace("<", "\\u003c"))
    (output / "index.html").write_text(template, encoding="utf-8", newline="\n")
    for name in ("app.js", "style.css", "limitations.html"):
        shutil.copyfile(ROOT / "web/mvp" / name, output / name)
    shutil.copyfile(ROOT / "web/view-model.js", output / "view-model.js")
    (output / "assets").mkdir(exist_ok=True)
    for name in (
        "inter.ttf",
        "fraunces.ttf",
        "fraunces-italic.ttf",
        "OFL-Inter.txt",
        "OFL-Fraunces.txt",
    ):
        shutil.copyfile(assets / name, output / "assets" / name)
    # Project-owned brand marks: the supplied wordmark and its derived web/favicon sizes.
    (output / "assets/brand").mkdir(exist_ok=True)
    for name in ("enagis-wordmark.png", "enagis-mark.png"):
        shutil.copyfile(assets / "brand" / name, output / "assets/brand" / name)
    write_json(output / "evidence/interface-assets.json", provenance)
    shutil.copyfile(ROOT / "web/mvp/README.md", output / "README.md")
    manifest = read(output / "manifest.json")
    manifest["purpose"] = "offline_application_of_recorded_evidence_with_global_navigation"
    manifest["interface_assets"] = provenance
    manifest["scientific_completion"] = False
    manifest["artifacts"] = [
        {"path": p.relative_to(output).as_posix(), "sha256": file_hash(p)}
        for p in sorted(output.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    ]
    # Include the vendored library manifest as an asset as well.
    manifest["artifacts"].append(
        {"path": "vendor/manifest.json", "sha256": file_hash(output / "vendor/manifest.json")}
    )
    manifest["artifacts"].sort(key=lambda row: row["path"])
    write_json(output / "manifest.json", manifest)
    verification = verify_demo(output)
    return {
        "output": str(output),
        "shortlist": len(data["nodes"]),
        "candidates": len(candidates),
        "search_places": len(world["places"]),
        "world_countries": len(world["countries"]["features"]),
        "verification": verification,
        "scientific_completion": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "app")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify_demo(args.output) if args.verify else build(args.output), indent=2))


if __name__ == "__main__":
    main()
