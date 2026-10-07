"""Preregistered Phase 4 runner. Real fitting is gated on explicit human protocol approval."""

import json
import subprocess
from pathlib import Path

from enagis.contracts import Artifact, Outcome, RunMetadata, ShippingLink
from enagis.data_io import file_hash, safe_path, write_json
from enagis.experiment_contracts import ExperimentProtocol, FeatureRow, Preregistration
from enagis.experiment_features import build_features
from enagis.experiment_network import build_network
from enagis.experiment_prepare import load_preparation, read_spine
from enagis.hindcast import evaluate_hindcast, join_hindcast
from enagis.ingestion import code_hash
from enagis.pipeline_contracts import NodeTrace
from enagis.pipeline_validation import verify_run
from enagis.siting import evaluate_siting


def register_experiment(root, protocol_path, preparation, registration_path):
    protocol = ExperimentProtocol.model_validate_json(protocol_path.read_bytes())
    protocol.require_approval()
    index, _ = load_preparation(preparation)
    if index["metadata"]["config_sha256"] != file_hash(protocol_path):
        raise ValueError("prepare inputs again with the approved protocol")
    if index["hashes"]["code"] != code_hash() or index["hashes"]["lock"] != file_hash(
        root / "uv.lock"
    ):
        raise ValueError("prepare inputs again with the current code and lockfile")
    if registration_path.exists():
        raise ValueError("preregistration is immutable; version a new protocol")
    review_path = safe_path(root, protocol.scientific_review_ref)
    relative_protocol = protocol_path.resolve().relative_to(root.resolve()).as_posix()
    relative_review = review_path.resolve().relative_to(root.resolve()).as_posix()
    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
            "--",
            "src/enagis",
            "configs/experiments",
            relative_protocol,
            relative_review,
            "pyproject.toml",
            "uv.lock",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    if result.stdout.strip():
        raise ValueError("commit protocol and implementation before preregistration")
    subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative_protocol, relative_review, "uv.lock"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()
    tag = f"preregister-{protocol.protocol_id}"
    existing = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if existing.returncode == 0 and existing.stdout.strip() != commit:
        raise ValueError("preregistration tag already points to another commit")
    registration = Preregistration(
        protocol_sha256=file_hash(protocol_path),
        preparation_index_sha256=file_hash(preparation / "index.json"),
        code_sha256=code_hash(),
        phase2_index_sha256=file_hash(root / "data/processed/phase2/index.json"),
        phase3_index_sha256=file_hash(root / "outputs/phase3/index.json"),
        review_document_sha256=file_hash(safe_path(root, protocol.scientific_review_ref)),
        lockfile_sha256=file_hash(root / "uv.lock"),
        git_commit=commit,
        git_tag=tag,
        registered_on=protocol.approved_on,
        purpose="Before real outcome evaluation; Manitoba excluded",
    )
    if existing.returncode != 0:
        subprocess.run(["git", "tag", tag, commit], cwd=root, check=True, capture_output=True)
    write_json(registration_path, registration)
    return registration.model_dump(mode="json")


def check_registration(root, protocol_path, preparation, registration_path):
    protocol = ExperimentProtocol.model_validate_json(protocol_path.read_bytes())
    protocol.require_approval()  # Check before reading any outcome or model result.
    registered = Preregistration.model_validate_json(registration_path.read_bytes())
    actual = (
        file_hash(protocol_path),
        file_hash(preparation / "index.json"),
        code_hash(),
        file_hash(root / "uv.lock"),
    )
    expected = (
        registered.protocol_sha256,
        registered.preparation_index_sha256,
        registered.code_sha256,
        registered.lockfile_sha256,
    )
    if actual != expected:
        raise ValueError("protocol/input/code/lock changed after preregistration")
    if (
        registered.phase2_index_sha256 != file_hash(root / "data/processed/phase2/index.json")
        or registered.phase3_index_sha256 != file_hash(root / "outputs/phase3/index.json")
        or registered.review_document_sha256
        != file_hash(safe_path(root, protocol.scientific_review_ref))
    ):
        raise ValueError(
            "source spine, allocation or review document changed after preregistration"
        )
    commit = subprocess.run(
        ["git", "rev-parse", f"refs/tags/{registered.git_tag}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    if commit != registered.git_commit:
        raise ValueError("preregistration tag changed")
    return protocol, registered


def evaluate_experiment(
    root: Path,
    protocol_path: Path,
    preparation: Path,
    registration_path: Path,
    output: Path,
    phase3: Path,
):
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "outputs") or output == root / "outputs":
        raise ValueError("experiment output must be below project outputs")
    if any(
        output.is_relative_to(p.resolve()) or p.resolve().is_relative_to(output)
        for p in (preparation, phase3)
    ) or any(p.resolve().is_relative_to(output) for p in (protocol_path, registration_path)):
        raise ValueError("experiment output overlaps an input directory")
    protocol, registered = check_registration(root, protocol_path, preparation, registration_path)
    if file_hash(phase3 / "index.json") != registered.phase3_index_sha256:
        raise ValueError("hindcast allocation is not the preregistered run")
    index, data = load_preparation(preparation)
    units, labels = data["units.json"], data["labels.json"]
    source_dir = root / "data/processed/phase2"
    source_index = json.loads((source_dir / "index.json").read_bytes())
    entries = {e["path"]: e for e in source_index["artifacts"]}
    road_paths, road_hashes = [], {}
    for province in protocol.development_units:
        name = f"roads_{province}.jsonl"
        path = source_dir / name
        if file_hash(path) != entries[name]["sha256"]:
            raise ValueError("road snapshot derivative checksum mismatch")
        road_paths.append(path)
        road_hashes[name] = entries[name]["sha256"]
    network = build_network(road_paths, units, protocol)
    network[-1]["source_ids"] = ["osm-alberta-20240101", "osm-saskatchewan-20240101"]
    features, feature_audit = build_features(
        units, data["production.json"], data["sadr.json"], network, protocol
    )
    siting, predictions, models = evaluate_siting(features, labels, units, protocol)
    # The outcome/allocation branch is opened only after independent siting features are finalized.
    verify_run(phase3)
    traces = Artifact[NodeTrace].model_validate_json((phase3 / "nodes.json").read_bytes()).rows
    tables, hindcast_hashes = read_spine(
        source_dir, {"outcomes_development.json": Outcome, "shipping_links.json": ShippingLink}
    )
    unit_by_id = {u.unit_id: u for u in units}
    facility_units = {
        f: label.unit_id
        for label in labels
        if label.status == "documented_presence"
        for f in label.facility_ids
    }
    facility_blocks = {f: unit_by_id[u].block_id for f, u in facility_units.items()}
    matched = join_hindcast(
        tables["outcomes_development.json"],
        tables["shipping_links.json"],
        traces,
        facility_blocks,
        facility_units,
        features,
        protocol,
    )
    hindcast = evaluate_hindcast(matched, protocol)
    metadata = dict(index["metadata"])
    metadata.update(
        run_id=f"phase4:{registered.protocol_sha256[:12]}:{registered.preparation_index_sha256[:12]}",
        seed=protocol.seed,
    )
    metadata["input_snapshot_ids"] = sorted(
        set(
            metadata["input_snapshot_ids"]
            + network[-1]["source_ids"]
            + ["cgc-deliveries-2024-2025"]
        )
    )
    report = {
        "status": "scientific_comparison_executed",
        "preregistration": registered.model_dump(mode="json"),
        "siting": siting,
        "hindcast": hindcast,
        "feature_audit": feature_audit,
        "source_hashes": {
            "roads": road_hashes,
            "hindcast": hindcast_hashes,
            "phase3_index": file_hash(phase3 / "index.json"),
        },
        "limitations": [
            "No field or Manitoba transfer validation",
            "Uniform-area production is a reviewed proxy",
            "Road distance is a connectivity comparison, not a driving-time catchment",
            "Siting scores discriminate documented presences from background; not probabilities",
            "Phase 3 allocation remains a temporary scenario "
            "with unvalidated commercial coefficients",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.json").unlink(missing_ok=True)
    payloads = {
        "features.json": [r.model_dump(mode="json") for r in features],
        "predictions.json": predictions,
        "fold_models.json": models,
        "hindcast_groups.json": matched,
        "report.json": report,
        "protocol.json": protocol.model_dump(mode="json"),
    }
    artifacts = []
    for name, value in payloads.items():
        write_json(
            output / name,
            {"metadata": metadata, "rows" if isinstance(value, list) else "data": value},
        )
        artifacts.append({"path": name, "sha256": file_hash(output / name)})
    write_json(output / "index.json", {"metadata": metadata, "artifacts": artifacts})
    verify_experiment(output)
    return report


def verify_experiment(output):
    index = json.loads((output / "index.json").read_bytes())
    RunMetadata.model_validate(index["metadata"])
    seen = set()
    datasets = {}
    for entry in index["artifacts"]:
        if entry["path"] in seen or file_hash(safe_path(output, entry["path"])) != entry["sha256"]:
            raise ValueError("duplicate/corrupt experiment output")
        seen.add(entry["path"])
        payload = json.loads((output / entry["path"]).read_bytes())
        if payload["metadata"] != index["metadata"]:
            raise ValueError("mixed experiment metadata")
        datasets[entry["path"]] = payload.get("rows", payload.get("data"))
        if entry["path"] == "features.json":
            for row in payload["rows"]:
                FeatureRow.model_validate(row)
    if seen != {
        "features.json",
        "predictions.json",
        "fold_models.json",
        "hindcast_groups.json",
        "report.json",
        "protocol.json",
    }:
        raise ValueError("incomplete experiment outputs")
    protocol = ExperimentProtocol.model_validate(datasets["protocol.json"])
    protocol.require_approval()
    report = datasets["report.json"]
    registered = Preregistration.model_validate(report["preregistration"])
    if registered.protocol_sha256 != index["metadata"]["config_sha256"]:
        raise ValueError("experiment metadata differs from preregistered protocol")
    features = {r["unit_id"]: r for r in datasets["features.json"]}
    if len(features) != len(datasets["features.json"]) or any(
        r["province"] not in protocol.development_units for r in features.values()
    ):
        raise ValueError("duplicate/transfer feature output")
    prediction_keys = set()
    expected_arms = {"full_model", *protocol.comparison_arms}
    for row in datasets["predictions.json"]:
        key = (row["unit_id"], row["arm"])
        if key in prediction_keys or row["arm"] not in expected_arms:
            raise ValueError("duplicate/unknown prediction arm")
        prediction_keys.add(key)
        if row["held_out_block"] != features[row["unit_id"]]["block_id"]:
            raise ValueError("prediction is not held out in its spatial block")
    for unit_id, _ in prediction_keys:
        if {arm for unit, arm in prediction_keys if unit == unit_id} != expected_arms:
            raise ValueError("comparison predictions have different cohorts")
    folds = {}
    for row in datasets["fold_models.json"]:
        key = (row["held_out_block"], row["arm"])
        if key in folds or row["arm"] not in {"base_model", "full_model"}:
            raise ValueError("duplicate/unknown model fold")
        folds[key] = row
        if row["held_out_block"] in row["training_blocks"]:
            raise ValueError("held-out block leaked into model training")
        required = protocol.base_features if row["arm"] == "base_model" else protocol.full_features
        if row["features"] != required:
            raise ValueError("model features differ from preregistration")
    for row in datasets["predictions.json"]:
        if row["arm"] in {"base_model", "full_model"}:
            if (row["held_out_block"], row["arm"]) not in folds:
                raise ValueError("prediction lacks a recorded fitted fold")
    groups = datasets["hindcast_groups.json"]
    if len({r["shipping_point_id"] for r in groups}) != len(groups):
        raise ValueError("shipping-point outcomes counted more than once")
    if report["siting"]["status"] == "feasibility_failed" and (prediction_keys or folds):
        raise ValueError("failed feasibility gate still produced fitted results")
    return {"run_id": index["metadata"]["run_id"], "verified_artifacts": len(seen)}
