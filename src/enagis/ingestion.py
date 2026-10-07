"""Phase 2 offline data spine. No allocation, technical parameters or fitted models."""

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

from shapely import union_all
from shapely.geometry import mapping, shape

from enagis.adapters.canada import (
    normalize_deliveries,
    normalize_production,
    normalize_registry,
    read_production_rows,
)
from enagis.adapters.licensing import reconcile_licensing
from enagis.adapters.roads import audit_extract_overlaps, normalize_roads
from enagis.adapters.spatial import (
    canonical_geometry_hash,
    digital_boundaries,
    match_points,
    overlap_crosswalk,
    sadr_boundaries,
    spatial_evidence,
)
from enagis.contracts import (
    Capacity,
    Facility,
    Node,
    Outcome,
    Production,
    RunMetadata,
    ShippingLink,
    Value,
)
from enagis.data_contracts import (
    Boundary,
    GeographyOverlap,
    IngestionConfig,
    JoinAudit,
    Manifest,
    ProductionLineage,
    QualityIssue,
    RegistrySourceRow,
    SpatialMatch,
)
from enagis.data_io import file_hash, safe_path, verify_manifest, write_json, write_table


def code_hash():
    digest = hashlib.sha256()
    source_dir = Path(__file__).parent
    for path in sorted(source_dir.rglob("*.py")):
        digest.update(path.relative_to(source_dir).as_posix().encode() + b"\0" + path.read_bytes())
    return digest.hexdigest()


def validate_references(
    facilities, nodes, capacities, raw_registry, outcomes, links, production, boundaries
):
    def unique(rows, field):
        ids = [getattr(row, field) for row in rows]
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate canonical {field}")
        return set(ids)

    facility_ids = unique(facilities, "facility_id")
    unique(facilities, "source_record_id")
    node_ids = unique(nodes, "node_id")
    unique(capacities, "capacity_id")
    unique(production, "production_id")
    unique(outcomes, "outcome_id")
    if {r.facility_id for r in raw_registry} != facility_ids or len(raw_registry) != len(
        facilities
    ):
        raise ValueError("registry normalization changed source cardinality")
    if {n.facility_id for n in nodes} != facility_ids or len(nodes) != len(facilities):
        raise ValueError("candidate node construction changed facility cardinality")
    if any(c.node_id not in node_ids or c.facility_id not in facility_ids for c in capacities):
        raise ValueError("capacity has orphan identity")
    points = {o.shipping_point_id for o in outcomes}
    if len(points) != len(outcomes):
        raise ValueError("shipping point outcomes duplicated")
    if any(
        link.facility_id not in facility_ids or link.shipping_point_id not in points
        for link in links
    ):
        raise ValueError("shipping crosswalk has orphan identity")
    if len({link.facility_id for link in links}) != len(links):
        raise ValueError("facility has multiple shipping outcome assignments")
    keys = [row.spatial_id.key for row in boundaries]
    if len(set(keys)) != len(keys) or any(p.geometry_ref not in set(keys) for p in production):
        raise ValueError("duplicate/missing production boundary reference")


def ingest(
    manifest_path: Path,
    config_path: Path,
    root: Path,
    output: Path,
    skip_licensing=False,
    progress=print,
):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "data/processed") or output == root / "data/processed":
        raise ValueError("derived output must be a subdirectory of project data/processed")
    manifest = Manifest.model_validate_json(manifest_path.read_bytes())
    config_model = IngestionConfig.model_validate_json(config_path.read_bytes())
    config = config_model.model_dump(mode="json")
    identity_path = safe_path(root, config["identity_path"])
    identities = json.loads(identity_path.read_bytes())["rows"]
    progress("Verifying pinned source checksums", flush=True)
    paths = verify_manifest(manifest, root, skip_restricted=skip_licensing)
    sources = {entry.snapshot.snapshot_id: entry for entry in manifest.sources}
    chosen = {name: sources[snapshot_id] for name, snapshot_id in config["source_ids"].items()}
    if any(s.snapshot.redistribution != "permitted" for s in chosen.values()):
        raise ValueError("core data source lacks permission for public offline outputs")
    controls_bytes = (
        safe_path(root, config["licensing_parser_controls_path"]).read_bytes()
        if config["licensing_parser_controls_path"]
        else b""
    )
    if not skip_licensing and not controls_bytes:
        raise ValueError("dated licensing audit requires versioned independent parser controls")
    config_hash = hashlib.sha256(
        config_path.read_bytes() + b"\0" + identity_path.read_bytes() + b"\0" + controls_bytes
    ).hexdigest()
    adapter_hash = code_hash()
    manifest_hash = file_hash(manifest_path)
    lock_path = root / "uv.lock"
    lock_hash = file_hash(lock_path) if lock_path.is_file() else None
    run_hash = hashlib.sha256(
        (
            config_hash + manifest_hash + adapter_hash + (lock_hash or "") + str(skip_licensing)
        ).encode()
    ).hexdigest()
    metadata = RunMetadata(
        schema_version="1.0.0",
        run_id=f"phase2:{run_hash[:20]}",
        region_id=config["region_id"],
        commodity_id="wheat_non_durum",
        service_id="ambient_air_aeration",
        scenario_id="input_spine_no_scientific_scenario",
        period_start=date(2024, 1, 1),
        period_end=date(2025, 7, 31),
        config_sha256=config_hash,
        input_snapshot_ids=sorted(
            s.snapshot.snapshot_id
            for s in manifest.sources
            if s.snapshot.redistribution == "permitted"
        ),
        seed=None,
    )
    output.mkdir(parents=True, exist_ok=True)
    # A failed rebuild cannot leave an earlier success index claiming current outputs are valid.
    (output / "index.json").unlink(missing_ok=True)
    artifacts = []

    def table(name, rows, row_type, table_metadata=metadata):
        item = write_table(output / f"{name}.json", table_metadata, rows, row_type)
        item["row_contract"] = row_type.__name__
        artifacts.append(item)

    registry_source = chosen["registry"]
    facilities, nodes, capacities, registry_rows, issues, exclusions = normalize_registry(
        paths[registry_source.snapshot.snapshot_id], registry_source, identities, config
    )
    outcomes, links, original_outcomes, delivery_join, delivery_summary = normalize_deliveries(
        paths[chosen["deliveries"].snapshot.snapshot_id],
        chosen["deliveries"],
        registry_rows,
        config,
    )
    table("registry", facilities, Facility)
    table("nodes", nodes, Node)
    storage_metadata = metadata.model_copy(update={"service_id": "wheat_storage"})
    table("capacities", capacities, Capacity, storage_metadata)
    table("registry_source_rows", registry_rows, RegistrySourceRow)
    table("registry_excluded", exclusions, dict)
    delivery_metadata = metadata.model_copy(update={"period_start": date(2024, 8, 1)})
    table(
        "outcomes_development",
        [o for o in outcomes if o.split == "development"],
        Outcome,
        delivery_metadata,
    )
    table(
        "outcomes_transfer",
        [o for o in outcomes if o.split == "transfer"],
        Outcome,
        delivery_metadata,
    )
    table("outcome_source_rows", original_outcomes, dict, delivery_metadata)
    table("shipping_links", links, ShippingLink, delivery_metadata)
    progress("Normalizing full digital and production reporting geometries", flush=True)
    boundary_tables = {}
    kinds = {
        "ccs": "census_consolidated_subdivision",
        "car": "census_agricultural_region",
        "cd": "census_division",
    }
    for name, kind in kinds.items():
        source = chosen[name]
        rows, geometry_issues = digital_boundaries(paths[source.snapshot.snapshot_id], source, kind)
        boundary_tables[name] = rows
        issues.extend(geometry_issues)
        table(f"boundaries_{name}", rows, Boundary)
    production_source = chosen["production"]
    production_rows, production_source_count = read_production_rows(
        paths[production_source.snapshot.snapshot_id], config
    )
    sadr_source = chosen["sadr_geometry"]
    sadr, geometry_issues, original_sadr = sadr_boundaries(
        paths[sadr_source.snapshot.snapshot_id], sadr_source, production_rows
    )
    issues.extend(geometry_issues)
    boundary_tables["sadr"] = sadr
    table("boundaries_sadr", sadr, Boundary)
    table("sadr_source_rows", original_sadr, dict)
    production, controls, lineage, production_issues = normalize_production(
        production_rows, production_source, {b.name.value: b for b in sadr}
    )
    issues.extend(production_issues)
    # Provinces are controls, never additional allocation origins. Their geometry is a CD union.
    provinces = []
    for control in controls:
        province = next(
            row.province for row in lineage if row.production_id == control.production_id
        )
        components = [b for b in boundary_tables["cd"] if b.province == province]
        geometry = union_all([shape(b.geometry) for b in components])
        ev = spatial_evidence(
            [chosen["cd"], production_source],
            "Province control geometry derived by union of 2021 full digital census divisions; "
            "source table province DGUID retained",
        )
        provinces.append(
            Boundary(
                spatial_id=control.geography,
                province=province,
                name=Value(value=province, evidence=ev),
                geometry_crs="EPSG:3347",
                geometry=mapping(geometry),
                source_geometry_sha256=canonical_geometry_hash(
                    [b.source_geometry_sha256 for b in components]
                ),
                topology="valid_source",
                geometry_evidence=ev,
            )
        )
    table("boundaries_province_controls", provinces, Boundary)
    production_metadata = metadata.model_copy(update={"period_end": date(2024, 12, 31)})
    table("production", production, Production, production_metadata)
    table("production_province_controls", controls, Production, production_metadata)
    table("production_lineage", lineage, ProductionLineage, production_metadata)
    spatial_matches, joins = [], [delivery_join]
    for name in ("ccs", "car", "sadr"):
        kind = kinds.get(name, "small_area_data_region")
        source = chosen.get(name, sadr_source)
        matches, audit = match_points(
            list(zip(facilities, registry_rows, strict=True)),
            boundary_tables[name],
            [registry_source, source],
            kind,
        )
        spatial_matches.extend(matches)
        joins.append(audit)
    table("facility_spatial_matches", spatial_matches, SpatialMatch)
    for target in ("car", "sadr"):
        source = chosen.get(target, sadr_source)
        overlaps, audit = overlap_crosswalk(
            boundary_tables["ccs"],
            boundary_tables[target],
            [chosen["ccs"], source],
            f"ccs_to_{target}_overlap",
        )
        table(f"ccs_to_{target}_overlap", overlaps, GeographyOverlap)
        joins.append(audit)
    validate_references(
        facilities,
        nodes,
        capacities,
        registry_rows,
        outcomes,
        links,
        production + controls,
        [b for rows in boundary_tables.values() for b in rows] + provinces,
    )
    table("quality_issues", issues, QualityIssue)
    table("join_audits", joins, JoinAudit)
    roads = []
    for province in config["province_units"]:
        progress(f"Normalizing OSM highway ways: {province}", flush=True)
        source = chosen[f"roads_{province}"]
        road, rejected = normalize_roads(
            paths[source.snapshot.snapshot_id],
            output / f"roads_{province}.jsonl",
            source,
            province,
            metadata,
        )
        roads.append(road.model_dump(mode="json"))
        artifacts.extend(
            [
                {
                    "path": road.path,
                    "rows": road.way_count,
                    "sha256": road.sha256,
                    "row_contract": "RoadWay",
                    "licence": "ODbL-1.0",
                },
                rejected,
            ]
        )
    write_json(
        output / "roads_index.json", {"metadata": metadata.model_dump(mode="json"), "roads": roads}
    )
    artifacts.append(
        {
            "path": "roads_index.json",
            "rows": len(roads),
            "sha256": file_hash(output / "roads_index.json"),
        }
    )
    road_overlap = audit_extract_overlaps(output, roads)
    write_json(output / "road_extract_overlap_audit.json", road_overlap)
    artifacts.append(
        {
            "path": "road_extract_overlap_audit.json",
            "sha256": file_hash(output / "road_extract_overlap_audit.json"),
        }
    )
    licensing = {
        "status": "skipped_open_rebuild",
        "resolution": (
            "Restricted reports excluded; dated licensing reconciliation remains "
            "available in the recorded Phase 2 audit"
        ),
    }
    if not skip_licensing:
        progress("Reconciling dated licensing lists into private audit", flush=True)
        licensing, private = reconcile_licensing(
            [s for s in manifest.sources if s.role == "licensing_audit"],
            paths,
            registry_rows,
            json.loads(controls_bytes)["controls"],
        )
        write_json(
            root / "data/validation_private/phase2/licensing_reconciliation.json",
            {"run_id": metadata.run_id, "manifest_sha256": manifest_hash, "reports": private},
        )
    summary = {
        "metadata": metadata.model_dump(mode="json"),
        "manifest_sha256": manifest_hash,
        "adapter_code_sha256": adapter_hash,
        "lockfile_sha256": lock_hash,
        "execution_options": {"skip_licensing": skip_licensing},
        "identity_crosswalk_sha256": file_hash(identity_path),
        "scope": (
            "Retrospective data normalization; no travel times, disaggregation, allocation, "
            "energy calculation, siting fit or shortlist"
        ),
        "registry": {
            "facilities": len(facilities),
            "nodes": len(nodes),
            "positive_storage": sum(r.positive_reported_storage for r in registry_rows),
            "by_province": dict(sorted(Counter(r.province for r in registry_rows).items())),
            "excluded_raw_records": len(exclusions),
        },
        "deliveries": delivery_summary,
        "boundaries": {k: len(v) for k, v in boundary_tables.items()},
        "production": {
            "raw_csv_rows": production_source_count,
            "retained_component_rows": len(production_rows),
            "regional_rows": len(production),
            "known_regional_non_durum": sum(p.modeled_tonnes.value is not None for p in production),
            "unknown_regional_non_durum": sum(p.modeled_tonnes.value is None for p in production),
            "province_controls": len(controls),
        },
        "quality_issues_by_code": dict(sorted(Counter(i.code for i in issues).items())),
        "joins": [j.model_dump(mode="json") for j in joins],
        "roads": [{k: v for k, v in r.items() if k != "metadata"} for r in roads],
        "road_extract_overlap": {
            "unique_osm_way_ids": road_overlap["unique_osm_way_ids"],
            "identical_repeated_way_ids": len(road_overlap["identical_repeated_way_ids"]),
            "conflicting_way_ids": len(road_overlap["conflicting_way_ids"]),
        },
        "licensing_reconciliation": licensing,
    }
    write_json(output / "data_audit.json", summary)
    artifacts.append({"path": "data_audit.json", "sha256": file_hash(output / "data_audit.json")})
    # Completeness marker written last; per-artifact hashes cover all reusable derived files.
    write_json(
        output / "index.json",
        {
            "metadata": metadata.model_dump(mode="json"),
            "manifest_sha256": manifest_hash,
            "adapter_code_sha256": adapter_hash,
            "lockfile_sha256": lock_hash,
            "execution_options": {"skip_licensing": skip_licensing},
            "artifacts": sorted(artifacts, key=lambda a: a["path"]),
            "licences": [
                {
                    "snapshot_id": s.snapshot.snapshot_id,
                    "licence": s.snapshot.licence,
                    "licence_url": s.snapshot.licence_url,
                    "attribution": s.attribution,
                }
                for s in manifest.sources
                if s.snapshot.redistribution == "permitted"
            ],
            "licence_note": (
                "Keep the ODbL road database separately licensed and attributed. "
                "Other data retain source terms; repository code licence does not "
                "relicense data."
            ),
        },
    )
    return summary
