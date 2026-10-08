"""Copy and replay the ranking before constructing a verification package."""

import hashlib
import json
import shutil
from pathlib import Path

from enagis.data_io import file_hash, safe_path, write_json
from enagis.ingestion import code_hash
from enagis.science.runner import canonical
from enagis.science.runner import verify as verify_science
from enagis.verification import VERSION
from enagis.verification.contracts import Frame, Protocol, Records, ScientificExit
from enagis.verification.sampling import make_sample

SOURCE_FILES = {
    "index.json",
    "config.json",
    "inputs.json",
    "accessibility.json",
    "draws.json",
    "ranking.json",
    "shortlist.json",
    "shortlist.csv",
    "ablations.json",
}
BUNDLE_FILES = {f"source/{p}" for p in SOURCE_FILES} | {
    "protocol.json",
    "frame.json",
    "sample.json",
    "scientific-exit.json",
    "scientific-review.txt",
    "capture.schema.json",
}


def read_json(path):
    return json.loads(Path(path).read_bytes())


def load_protocol(path, *, allow_fixture=False):
    raw = read_json(path)
    if raw.get("status") == "pending_human_review":
        raise ValueError("Phase 7 gate: verification protocol is proposed, not human-approved")
    protocol = Protocol.model_validate(raw)
    protocol.authorize(allow_fixture=allow_fixture)
    return protocol


def source_review(protocol, source, exit_path):
    meta = read_json(source / "index.json")["metadata"]
    if meta["purpose"] != protocol.purpose:
        raise ValueError("ranking and protocol purposes disagree")
    if protocol.purpose == "synthetic_fixture":
        if exit_path is not None:
            raise ValueError("synthetic fixtures cannot carry a real scientific exit")
        return {"status": "synthetic_engineering_only"}, b"Synthetic fixture; no scientific exit.\n"
    if exit_path is None:
        raise ValueError("Phase 6 scientific exit approval is required before ranking-v1")
    exit_path = Path(exit_path)
    accepted = ScientificExit.model_validate_json(exit_path.read_bytes())
    if accepted.source_index_sha256 != file_hash(source / "index.json"):
        raise ValueError("scientific exit applies to a different ranking run")
    if accepted.source_code_sha256 != meta["code_sha256"]:
        raise ValueError("scientific exit applies to different source code")
    report = safe_path(exit_path.parent, accepted.review_report_path)
    if file_hash(report) != accepted.review_report_sha256:
        raise ValueError("scientific review report checksum mismatch")
    return accepted.model_dump(mode="json"), report.read_bytes()


def ensure_new_output(output, inputs):
    output = Path(output).resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError(
            "output must be new or empty; frozen/history artifacts cannot be overwritten"
        )
    for item in inputs:
        resolved = Path(item).resolve()
        if output == resolved or output.is_relative_to(resolved) or resolved.is_relative_to(output):
            raise ValueError("output must be separate from every input path")
    return output


def prepare(
    source, protocol_path, frame_path, output, lockfile, *, exit_path=None, allow_fixture=False
):
    protocol = load_protocol(protocol_path, allow_fixture=allow_fixture)
    # Stop on the missing real exit before reading ranking data.
    if protocol.purpose == "scientific_reviewed" and exit_path is None:
        raise ValueError("Phase 6 scientific exit approval is required before ranking-v1")
    source, lockfile = Path(source), Path(lockfile)
    dependencies = [source, protocol_path, frame_path, lockfile]
    if exit_path is not None:
        dependencies.append(exit_path)
    output = ensure_new_output(output, dependencies)
    verify_science(source, lockfile)
    acceptance, report = source_review(protocol, source, exit_path)
    frame = Frame.model_validate_json(Path(frame_path).read_bytes())
    if frame.source_index_sha256 != file_hash(source / "index.json"):
        raise ValueError("verification frame refers to a different ranking snapshot")
    ranking = read_json(source / "ranking.json")["data"]
    sample = make_sample(ranking, frame, protocol)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source").mkdir()
    for name in sorted(SOURCE_FILES):
        shutil.copyfile(source / name, output / "source" / name)
    write_json(output / "protocol.json", protocol)
    write_json(output / "frame.json", frame)
    write_json(output / "sample.json", sample)
    write_json(output / "scientific-exit.json", acceptance)
    (output / "scientific-review.txt").write_bytes(report)
    write_json(output / "capture.schema.json", Records.model_json_schema())
    hashes = {name: file_hash(output / name) for name in sorted(BUNDLE_FILES)}
    identity = hashlib.sha256(canonical(hashes)).hexdigest()[:24]
    source_meta = read_json(source / "index.json")["metadata"]
    prefix = "fixture:" if protocol.purpose == "synthetic_fixture" else ""
    manifest = {
        "schema_version": VERSION,
        "freeze_id": f"{prefix}freeze:{identity}",
        "status": "prepared_requires_git_tag_and_remote_seal",
        "purpose": protocol.purpose,
        "freeze_tag": protocol.freeze_tag,
        "source_run_id": source_meta["run_id"],
        "source_code_sha256": code_hash(),
        "lockfile_sha256": file_hash(lockfile),
        "shortlist_sha256": hashes["source/shortlist.json"],
        "sample_sha256": hashes["sample.json"],
        "protocol_sha256": hashes["protocol.json"],
        "artifacts": hashes,
    }
    write_json(output / "manifest.json", manifest)
    return {
        "freeze_id": manifest["freeze_id"],
        "status": manifest["status"],
        "sample": len(sample["rows"]),
    }


def verify_bundle(bundle, lockfile, *, allow_fixture=False):
    bundle = Path(bundle)
    manifest = read_json(bundle / "manifest.json")
    if manifest["schema_version"] != VERSION or set(manifest["artifacts"]) != BUNDLE_FILES:
        raise ValueError("unexpected freeze artifact set/version")
    found = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
    if found != BUNDLE_FILES | {"manifest.json"}:
        raise ValueError("unexpected or missing file in freeze package")
    for name, expected in manifest["artifacts"].items():
        if file_hash(safe_path(bundle, name)) != expected:
            raise ValueError(f"frozen artifact checksum mismatch: {name}")
    protocol = load_protocol(bundle / "protocol.json", allow_fixture=allow_fixture)
    frame = Frame.model_validate_json((bundle / "frame.json").read_bytes())
    verify_science(bundle / "source", Path(lockfile))
    if frame.source_index_sha256 != file_hash(bundle / "source/index.json"):
        raise ValueError("frame and source snapshot disagree")
    source_meta = read_json(bundle / "source/index.json")["metadata"]
    if source_meta["purpose"] != protocol.purpose:
        raise ValueError("ranking and protocol purposes disagree")
    if protocol.purpose == "scientific_reviewed":
        accepted = ScientificExit.model_validate_json(
            (bundle / "scientific-exit.json").read_bytes()
        )
        if (
            accepted.source_index_sha256 != frame.source_index_sha256
            or accepted.source_code_sha256 != source_meta["code_sha256"]
            or accepted.review_report_sha256 != file_hash(bundle / "scientific-review.txt")
        ):
            raise ValueError("scientific exit does not bind this source and review")
    elif read_json(bundle / "scientific-exit.json") != {"status": "synthetic_engineering_only"}:
        raise ValueError("fixture cannot claim a scientific exit")
    expected_sample = make_sample(
        read_json(bundle / "source/ranking.json")["data"], frame, protocol
    )
    if read_json(bundle / "sample.json") != expected_sample:
        raise ValueError("frozen sample differs from deterministic prospective selection")
    hashes = manifest["artifacts"]
    identity = hashlib.sha256(canonical(hashes)).hexdigest()[:24]
    prefix = "fixture:" if protocol.purpose == "synthetic_fixture" else ""
    expected = {
        "schema_version": VERSION,
        "freeze_id": f"{prefix}freeze:{identity}",
        "status": "prepared_requires_git_tag_and_remote_seal",
        "purpose": protocol.purpose,
        "freeze_tag": protocol.freeze_tag,
        "source_run_id": source_meta["run_id"],
        "source_code_sha256": code_hash(),
        "lockfile_sha256": file_hash(Path(lockfile)),
        "shortlist_sha256": hashes["source/shortlist.json"],
        "sample_sha256": hashes["sample.json"],
        "protocol_sha256": hashes["protocol.json"],
        "artifacts": hashes,
    }
    if manifest != expected:
        raise ValueError("freeze manifest identity/metadata differs from its evidence")
    if read_json(bundle / "capture.schema.json") != Records.model_json_schema():
        raise ValueError("capture schema differs from the recorded code")
    return manifest, protocol, expected_sample
