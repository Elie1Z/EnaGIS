"""Counts and provenance only. Never consumes delivery outcomes or Manitoba road files."""

import hashlib
import json
from collections import Counter

from enagis.data_contracts import RoadWay
from enagis.data_io import file_hash, safe_path, write_json
from enagis.pipeline import load_inputs


def readiness(input_dir, review_path, output):
    review = json.loads(review_path.read_bytes())
    if review.get("status") != "pending_scientific_review":
        raise ValueError("readiness audit requires the explicit pending review packet")
    index, tables, consumed = load_inputs(input_dir)
    raw = {r.facility_id: r for r in tables["registry_source_rows.json"]}
    nodes = [n for n in tables["nodes.json"] if raw[n.facility_id].province in {"AB", "SK"}]
    lineage = {p.production_id: p for p in tables["production_lineage.json"]}
    production = [
        p for p in tables["production.json"] if lineage[p.production_id].province in {"AB", "SK"}
    ]
    matches = [
        m
        for m in tables["facility_spatial_matches.json"]
        if m.geography_type == "small_area_data_region"
        and raw[m.record_id].province in {"AB", "SK"}
    ]
    storage = [c for c in tables["capacities.json"] if c.service_id == "wheat_storage"]
    capacities = {c.node_id: c for c in storage}
    if len(capacities) != len(storage) or any(n.node_id not in capacities for n in nodes):
        raise ValueError("storage join lost or duplicated development nodes")
    node_ids = {n.node_id for n in nodes}
    electrical_count = 0
    for capacity in tables["capacities.json"]:
        quantity = capacity.conversion.converted if capacity.conversion else capacity.original
        if (
            capacity.node_id in node_ids
            and capacity.service_id == "ambient_air_aeration"
            and quantity.dimension == "electric_power"
            and quantity.amount.value is not None
        ):
            electrical_count += 1
    entries = {e["path"]: e for e in index["artifacts"]}
    roads = {}
    for province in ("AB", "SK"):
        name = f"roads_{province}.jsonl"
        path = safe_path(input_dir, name)
        counts, classes, surfaces = Counter(), Counter(), Counter()
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for line in stream:
                digest.update(line)
                row = RoadWay.model_validate_json(line)
                tags = row.tags
                counts["ways"] += 1
                classes[tags["highway"]] += 1
                surfaces[tags.get("surface", "UNKNOWN")] += 1
                for key in (
                    "surface",
                    "access",
                    "foot",
                    "bicycle",
                    "motor_vehicle",
                    "hgv",
                    "motorcycle",
                    "oneway",
                    "maxspeed",
                    "smoothness",
                    "tracktype",
                ):
                    counts[f"missing_{key}"] += key not in tags
                counts["conditional_tags"] += any(":conditional" in key for key in tags)
                counts["freight_dimension_tags"] += any(
                    key in tags for key in ("maxweight", "maxaxleload", "maxheight", "maxwidth")
                )
        if digest.hexdigest() != entries[name]["sha256"] or counts["ways"] != entries[name]["rows"]:
            raise ValueError(f"road audit input integrity failed: {name}")
        roads[province] = {
            "sha256": digest.hexdigest(),
            "counts": dict(counts),
            "highway_classes": dict(sorted(classes.items())),
            "surface_tags": dict(sorted(surfaces.items())),
        }
    result = {
        "schema_version": "phase6-readiness-v1",
        "status": "blocked_scientific_review",
        "scientifically_ready_to_freeze": False,
        "scope": "AB/SK development; no Manitoba roads or outcome files opened",
        "input_index_sha256": file_hash(input_dir / "index.json"),
        "review_sha256": file_hash(review_path),
        "consumed_tables": consumed,
        "counts": {
            "development_nodes": len(nodes),
            "by_province": dict(Counter(raw[n.facility_id].province for n in nodes)),
            "known_storage_nodes": sum(
                capacities[n.node_id].original.amount.value is not None for n in nodes
            ),
            "unresolved_eligibility_nodes": sum(
                n.stationary_service_eligible is not True for n in nodes
            ),
            "spatial_review_nodes": sum(m.status != "matched" for m in matches),
            "production_origins": len(production),
            "known_production_origins": sum(p.modeled_tonnes.value is not None for p in production),
            "unknown_production_origins": sum(p.modeled_tonnes.value is None for p in production),
            "documented_electrical_capacity_observations_in_consumed_tables": electrical_count,
        },
        "roads": roads,
        "road_interpretation": (
            "Counts are ways, not road length. Missing tags do not prove legal or physical access. "
            "Node barriers and relation restrictions are absent from this adapter."
        ),
        "gates": review["gates"],
        "scientific_ranking": None,
        "uncertainty_tiers": None,
        "assumptions": [
            "No new production proxy or speed/seasonal coefficient was selected.",
            "No CGC outcome file was opened; no model or baseline was scored.",
            "Registry storage is not electrical capacity; source scope is retained.",
        ],
    }
    write_json(output, result)
    return {
        "status": result["status"],
        "counts": result["counts"],
        "road_ways": {p: r["counts"]["ways"] for p, r in roads.items()},
        "open_gates": len(review["gates"]),
    }
