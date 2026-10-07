"""Verify the completed input-spine index and its typed, hashed derived artifacts."""

import json
from pathlib import Path

from enagis.contracts import (
    Artifact,
    Capacity,
    Facility,
    Node,
    Outcome,
    Production,
    RunMetadata,
    ShippingLink,
)
from enagis.data_contracts import (
    Boundary,
    GeographyOverlap,
    JoinAudit,
    ProductionLineage,
    QualityIssue,
    RegistrySourceRow,
    RoadArtifact,
    RoadWay,
    SpatialMatch,
)
from enagis.data_io import file_hash, safe_path

ROW_TYPES = {
    model.__name__: model
    for model in (
        Capacity,
        Facility,
        Node,
        Outcome,
        Production,
        ShippingLink,
        Boundary,
        GeographyOverlap,
        JoinAudit,
        ProductionLineage,
        QualityIssue,
        RegistrySourceRow,
        SpatialMatch,
    )
} | {"dict": dict}


def verify_data(output: Path):
    index = json.loads((output / "index.json").read_bytes())
    if not index.get("artifacts"):
        raise ValueError("missing completed artifact index")
    metadata = RunMetadata.model_validate(index["metadata"])
    known_sources = set(metadata.input_snapshot_ids)

    def check_sources(value):
        if isinstance(value, dict):
            if "source_ids" in value and not set(value["source_ids"]) <= known_sources:
                raise ValueError("orphan evidence source in derived artifact")
            for child in value.values():
                check_sources(child)
        elif isinstance(value, list):
            for child in value:
                check_sources(child)

    seen, totals = set(), {}
    for entry in index["artifacts"]:
        if entry["path"] in seen:
            raise ValueError("duplicate derived artifact path")
        seen.add(entry["path"])
        path = safe_path(output, entry["path"])
        if file_hash(path) != entry["sha256"]:
            raise ValueError(f"derived artifact checksum mismatch: {entry['path']}")
        if entry.get("row_contract") == "RoadWay":
            count = 0
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    record = RoadWay.model_validate_json(line)
                    if not set(record.evidence.source_ids) <= known_sources:
                        raise ValueError("orphan road evidence source")
                    count += 1
        elif entry.get("row_contract") in ROW_TYPES:
            artifact = Artifact[ROW_TYPES[entry["row_contract"]]].model_validate_json(
                path.read_bytes()
            )
            if artifact.metadata.run_id != index["metadata"]["run_id"]:
                raise ValueError("mixed run IDs in artifact index")
            count = len(artifact.rows)
            check_sources(json.loads(path.read_bytes())["rows"])
        elif path.name == "roads_index.json":
            road_index = json.loads(path.read_bytes())
            for road in road_index["roads"]:
                model = RoadArtifact.model_validate(road)
                if model.metadata.run_id != index["metadata"]["run_id"]:
                    raise ValueError("mixed road run IDs")
            count = len(road_index["roads"])
        elif path.suffix == ".jsonl":
            with path.open(encoding="utf-8") as stream:
                count = sum(1 for line in stream if json.loads(line))
        else:
            json.loads(path.read_bytes())
            count = None
        if "rows" in entry and entry["rows"] != count:
            raise ValueError(f"derived row count mismatch: {entry['path']}")
        totals[entry["path"]] = count
    return {"run_id": index["metadata"]["run_id"], "verified_artifacts": len(seen), "rows": totals}
