"""ODbL road-way database; preserve source topology/tags without routing assumptions."""

import hashlib
import json
import sqlite3
import xml.etree.ElementTree as ET
from contextlib import closing
from pathlib import Path

from enagis.adapters.canada import evidence
from enagis.adapters.pbf import blocks, header_timestamp, nodes, primitive_groups, ways
from enagis.data_contracts import RoadArtifact, RoadWay
from enagis.data_io import file_hash


def normalize_roads(path: Path, output: Path, source, province, metadata):
    output.parent.mkdir(parents=True, exist_ok=True)
    rejected_path = output.with_suffix(".rejected.jsonl")
    cache_path = output.with_suffix(".nodes.sqlite")
    if cache_path.exists():
        raise ValueError(f"unfinished node cache exists: {cache_path}")
    count, rejected_count, timestamp, seen = 0, 0, "not_reported", set()
    try:
        with (
            closing(sqlite3.connect(cache_path)) as connection,
            output.open("w", encoding="utf-8", newline="\n") as stream,
            rejected_path.open("w", encoding="utf-8", newline="\n") as rejected,
        ):
            connection.execute(
                "PRAGMA journal_mode=OFF"
            )  # temporary cache, never an input snapshot
            connection.execute("PRAGMA synchronous=OFF")
            connection.execute(
                "CREATE TABLE nodes (id INTEGER PRIMARY KEY, lon INTEGER, lat INTEGER)"
            )

            def add_nodes(rows):
                connection.executemany("INSERT INTO nodes VALUES (?,?,?)", rows)

            def write_way(identity, version, refs, tags):
                nonlocal count, rejected_count
                if identity in seen:
                    raise ValueError(f"duplicate OSM highway way: {identity}")
                seen.add(identity)
                locations = {}
                for start in range(0, len(refs), 500):
                    chunk = refs[start : start + 500]
                    placeholders = ",".join("?" for ref in chunk)
                    for nid, lon, lat in connection.execute(
                        f"SELECT id,lon,lat FROM nodes WHERE id IN ({placeholders})", chunk
                    ):
                        locations[nid] = (lon * 1e-9, lat * 1e-9)
                if len(refs) < 2 or any(ref not in locations for ref in refs):
                    rejected.write(
                        json.dumps(
                            {
                                "way_id": str(identity),
                                "osm_version": version,
                                "node_ids": refs,
                                "tags": tags,
                                "source_snapshot_id": source.snapshot.snapshot_id,
                                "reason": (
                                    "fewer than two nodes or incomplete extract node locations"
                                ),
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n"
                    )
                    rejected_count += 1
                    return
                record = RoadWay(
                    way_id=str(identity),
                    osm_version=version,
                    node_ids=refs,
                    coordinates_lon_lat=[locations[ref] for ref in refs],
                    crs="EPSG:4326",
                    tags=tags,
                    evidence=evidence(
                        source,
                        "OBSERVED",
                        "All highway-tagged OSM ways, source node IDs/order and tags retained. "
                        "No speed, passability, travel time or network connectivity inferred.",
                    ),
                )
                stream.write(record.model_dump_json() + "\n")
                count += 1

            if path.suffix == ".osm":  # small synthetic fixtures; real sources are pinned PBF
                document = ET.parse(path).getroot()
                add_nodes(
                    (
                        int(n.attrib["id"]),
                        round(float(n.attrib["lon"]) * 1e9),
                        round(float(n.attrib["lat"]) * 1e9),
                    )
                    for n in document.findall("node")
                )
                for way in document.findall("way"):
                    tags = {t.attrib["k"]: t.attrib["v"] for t in way.findall("tag")}
                    if "highway" in tags:
                        write_way(
                            int(way.attrib["id"]),
                            int(way.attrib["version"]),
                            [int(n.attrib["ref"]) for n in way.findall("nd")],
                            tags,
                        )
            else:
                # Two passes support legal PBF files where ways precede their nodes.
                headers = 0
                for kind, message in blocks(path):
                    if kind == b"OSMHeader":
                        timestamp = header_timestamp(message)
                        headers += 1
                    else:
                        if headers != 1:
                            raise ValueError("PBF requires one preceding header")
                        for (
                            group,
                            _strings,
                            granularity,
                            lat_offset,
                            lon_offset,
                        ) in primitive_groups(message):
                            add_nodes(nodes(group, granularity, lat_offset, lon_offset))
                if headers != 1:
                    raise ValueError("PBF missing/duplicate header")
                connection.commit()
                for kind, message in blocks(path):
                    if kind == b"OSMData":
                        for (
                            group,
                            strings,
                            _granularity,
                            _lat_offset,
                            _lon_offset,
                        ) in primitive_groups(message):
                            for road in ways(group, strings):
                                write_way(*road)
        artifact = RoadArtifact(
            metadata=metadata,
            source_snapshot_id=source.snapshot.snapshot_id,
            extract_timestamp=timestamp,
            province=province,
            path=output.name,
            sha256=file_hash(output),
            way_count=count,
            rejected_way_count=rejected_count,
            routing_parameters_status="not_configured_no_travel_times",
            licence="ODbL-1.0",
            attribution=source.attribution,
        )
        return artifact, {
            "path": rejected_path.name,
            "rows": rejected_count,
            "sha256": file_hash(rejected_path),
        }
    finally:
        cache_path.unlink(missing_ok=True)


def audit_extract_overlaps(output, road_artifacts):
    seen, identical, conflicts, row_count = {}, set(), set(), 0
    for artifact in road_artifacts:
        with (output / artifact["path"]).open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                identity = row["way_id"]
                content = {
                    k: row[k] for k in ("osm_version", "node_ids", "coordinates_lon_lat", "tags")
                }
                digest = hashlib.sha256(
                    json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
                ).digest()
                if identity in seen:
                    (identical if seen[identity] == digest else conflicts).add(identity)
                else:
                    seen[identity] = digest
                row_count += 1
    return {
        "extract_way_rows": row_count,
        "unique_osm_way_ids": len(seen),
        "identical_repeated_way_ids": sorted(identical, key=int),
        "conflicting_way_ids": sorted(conflicts, key=int),
        "routing_gate": (
            "Merge identical global OSM way IDs once; resolve conflicting versions/geometries "
            "before graph construction. Extract rows are not unique network edges."
        ),
    }
