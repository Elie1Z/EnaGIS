"""Export verified historical runs as an offline presentation; never rerun science."""

import argparse
import json
import shutil
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import LineString, mapping, shape
from shapely.ops import transform, unary_union

from enagis.data_io import file_hash, safe_path, write_json
from enagis.experiment import verify_experiment
from enagis.pipeline_validation import verify_run

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_bytes())


def checked(spine, name):
    index = read(spine / "index.json")
    entry = next(e for e in index["artifacts"] if e["path"] == name)
    path = safe_path(spine, name)
    if file_hash(path) != entry["sha256"]:
        raise ValueError(f"context input checksum mismatch: {name}")
    return path, entry


def feature(geometry, **properties):
    return {"type": "Feature", "geometry": geometry, "properties": properties}


def collection(features):
    return {"type": "FeatureCollection", "features": features}


def display_geometry(geometry):
    """Round only generalized display coordinates, never source/node measurements."""

    def rounded(value):
        if isinstance(value, (list, tuple)):
            return [rounded(v) for v in value]
        return round(value, 5)

    result = mapping(geometry)
    return {"type": result["type"], "coordinates": rounded(result["coordinates"])}


def make_context(spine):
    """Generalized display geometry only; never scientific allocation/catchments."""
    to_lonlat = Transformer.from_crs(3347, 4326, always_xy=True).transform
    to_metric = Transformer.from_crs(4326, 3347, always_xy=True).transform
    inputs, provinces, regions, road_lines, seen = [], [], [], [], set()
    for name, target in (
        ("boundaries_province_controls.json", provinces),
        ("boundaries_sadr.json", regions),
    ):
        path, entry = checked(spine, name)
        inputs.append(entry)
        for row in read(path)["rows"]:
            if row["province"] not in {"AB", "SK"}:
                continue
            if row["geometry_crs"] != "EPSG:3347":
                raise ValueError("display boundary CRS differs from declared source")
            geometry = shape(row["geometry"])
            target.append(
                feature(
                    display_geometry(transform(to_lonlat, geometry.simplify(1000))),
                    id=":".join(
                        [
                            "CA",
                            row["spatial_id"]["geography_type"],
                            row["spatial_id"]["boundary_vintage"],
                            row["spatial_id"]["code"],
                        ]
                    ),
                    province=row["province"],
                    name=row["name"]["value"],
                    evidence=row["geometry_evidence"],
                )
            )
    domain = unary_union([shape(f["geometry"]) for f in provinces])
    for province in ("AB", "SK"):
        path, entry = checked(spine, f"roads_{province}.jsonl")
        inputs.append(entry)
        lines, source_ids = [], set()
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                if row["tags"].get("highway") not in {"motorway", "trunk", "primary", "secondary"}:
                    continue
                key = (row["way_id"], row["osm_version"])
                if key in seen:
                    continue
                seen.add(key)
                if row["crs"] != "EPSG:4326":
                    raise ValueError("display road CRS differs from declared source")
                geometry = LineString(row["coordinates_lon_lat"]).intersection(domain)
                if geometry.is_empty or geometry.geom_type not in {"LineString", "MultiLineString"}:
                    continue
                geometry = transform(to_lonlat, transform(to_metric, geometry).simplify(250))
                display = display_geometry(geometry)
                lines.extend(
                    [display["coordinates"]]
                    if display["type"] == "LineString"
                    else display["coordinates"]
                )
                source_ids.update(row["evidence"]["source_ids"])
        road_lines.append(
            feature(
                {"type": "MultiLineString", "coordinates": lines}, source_ids=sorted(source_ids)
            )
        )
    return {
        "crs": "EPSG:4326",
        "purpose": "display_only_not_routing_or_catchments",
        "provinces": collection(provinces),
        "regions": collection(regions),
        "roads": collection(road_lines),
        "inputs": inputs,
        "simplification_metres": {"boundaries": 1000, "roads": 250},
        "display_coordinate_decimal_places": 5,
        "roads_licence": "ODbL-1.0",
        "roads_attribution": "© OpenStreetMap contributors",
        "roads_scope": (
            "Major roads from pinned 2024 AB/SK extracts; clipped to development footprint"
        ),
    }


def copy_run(source, destination):
    destination.mkdir(parents=True, exist_ok=True)
    for name in ["index.json", *[e["path"] for e in read(source / "index.json")["artifacts"]]]:
        source_file, dest_file = safe_path(source, name), safe_path(destination, name)
        if source_file.resolve() != dest_file.resolve():
            shutil.copyfile(source_file, dest_file)


def export(phase3, phase4, context, output, sources):
    if any(output.resolve().is_relative_to(p.resolve()) for p in (phase3, phase4)):
        raise ValueError("presentation output cannot overwrite scientific input directories")
    vendor = read(ROOT / "web/vendor/manifest.json")
    for name, digest in vendor["files"].items():
        if file_hash(safe_path(ROOT / "web/vendor", name)) != digest:
            raise ValueError("vendored browser dependency checksum mismatch")
    verified = {"phase3": verify_run(phase3), "phase4": verify_experiment(phase4)}
    report = read(phase4 / "report.json")["data"]
    if report["preregistration"]["phase3_index_sha256"] != file_hash(phase3 / "index.json"):
        raise ValueError("comparison belongs to a different historical Phase 3 run")
    metadata = read(phase3 / "index.json")["metadata"]
    rows = read(phase3 / "nodes.json")["rows"]
    if any(n["province"] not in {"AB", "SK"} for n in rows):
        raise ValueError("transfer nodes cannot enter the demo")
    shortlist_size = read(phase3 / "scenario.json")["shortlist_size"]
    shortlist = sorted([n for n in rows if n["rank"] is not None], key=lambda n: n["rank"])
    shortlist = shortlist[:shortlist_size]
    used = set(metadata["input_snapshot_ids"])
    used.update(read(phase4 / "index.json")["metadata"]["input_snapshot_ids"])
    for layer in ("provinces", "regions", "roads"):
        for item in context[layer]["features"]:
            used.update(item["properties"].get("source_ids", []))
            used.update(item["properties"].get("evidence", {}).get("source_ids", []))
    sources = [s for s in sources if s["snapshot_id"] in used]
    if any(s["redistribution"] != "permitted" for s in sources):
        raise ValueError("restricted sources cannot enter public demo")
    if used - {s["snapshot_id"] for s in sources} - {"scenario:" + metadata["scenario_id"]}:
        raise ValueError("demo evidence lacks a permitted source snapshot")
    output.mkdir(parents=True, exist_ok=True)
    evidence = output / "evidence"
    copy_run(phase3, evidence / "phase3")
    copy_run(phase4, evidence / "phase4")
    write_json(evidence / "context.json", context)
    write_json(evidence / "sources.json", sources)
    shutil.copyfile(phase3 / "engineering-shortlist.csv", output / "shortlist.csv")
    geojson = collection(
        [
            feature(
                {
                    "type": "Point",
                    "coordinates": [
                        n["node"]["location"]["point"]["value"]["longitude"],
                        n["node"]["location"]["point"]["value"]["latitude"],
                    ],
                },
                node_id=n["node_id"],
                rank=n["rank"],
                name=n["facility"]["name"]["value"],
                province=n["province"],
                node_type=n["node"]["node_type"],
                precision=n["node"]["location"]["precision"],
                trace=n,
            )
            for n in shortlist
        ]
    )
    write_json(output / "shortlist.geojson", geojson)
    write_json(output / "roads.geojson", context["roads"])
    data = {
        "metadata": metadata,
        "nodes": shortlist,
        "sources": sources,
        "audit": read(phase3 / "audit.json"),
        "scenario": read(phase3 / "scenario.json"),
        "comparison": report,
        "context": context,
        "verified": verified,
        "field_verification": {"status": "not_collected", "n": 0},
    }
    template = (ROOT / "web/index.html").read_text(encoding="utf-8")
    encoded = json.dumps(data, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
    encoded = encoded.replace("<", "\\u003c")
    (output / "index.html").write_text(
        template.replace("__DATA__", encoded), encoding="utf-8", newline="\n"
    )
    for name in ("app.js", "style.css"):
        shutil.copyfile(ROOT / "web" / name, output / name)
    shutil.copytree(ROOT / "web/vendor", output / "vendor", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "web/README-demo.md", output / "README.md")
    files = sorted(p for p in output.rglob("*") if p.is_file() and p != output / "manifest.json")
    manifest = {
        "schema_version": "1.0.0",
        "purpose": "offline_presentation_of_historical_verified_runs",
        "metadata": metadata,
        "verification": verified,
        "phase3_index_sha256": file_hash(phase3 / "index.json"),
        "phase4_index_sha256": file_hash(phase4 / "index.json"),
        "context_inputs": context["inputs"],
        "sources": sources,
        "artifacts": [
            {"path": p.relative_to(output).as_posix(), "sha256": file_hash(p)} for p in files
        ],
    }
    write_json(output / "manifest.json", manifest)
    return {"shortlist_rows": len(shortlist), "verified": verified, "output": str(output)}


def verify_demo(output):
    manifest = read(output / "manifest.json")
    for entry in manifest["artifacts"]:
        if file_hash(safe_path(output, entry["path"])) != entry["sha256"]:
            raise ValueError(f"demo checksum mismatch: {entry['path']}")
    if manifest["verification"]["phase3"] != verify_run(output / "evidence/phase3"):
        raise ValueError("demo Phase 3 verification differs")
    if manifest["verification"]["phase4"] != verify_experiment(output / "evidence/phase4"):
        raise ValueError("demo Phase 4 verification differs")
    return {"verified_artifacts": len(manifest["artifacts"]), "status": "verified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase3", type=Path, default=ROOT / "demo/evidence/phase3")
    parser.add_argument("--phase4", type=Path, default=ROOT / "demo/evidence/phase4")
    parser.add_argument("--context", type=Path, default=ROOT / "demo/evidence/context.json")
    parser.add_argument("--spine", type=Path, help="First export only: pinned Phase 2 map inputs")
    parser.add_argument("--output", type=Path, default=ROOT / "demo")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verify_demo(args.output), indent=2))
        return
    context = make_context(args.spine) if args.spine else read(args.context)
    sources = []
    for name in ("manifest.json", "phase4-manifest.json"):
        sources.extend(s["snapshot"] for s in read(ROOT / "docs/data" / name)["sources"])
    print(json.dumps(export(args.phase3, args.phase4, context, args.output, sources), indent=2))
    print(json.dumps(verify_demo(args.output), indent=2))


if __name__ == "__main__":
    main()
