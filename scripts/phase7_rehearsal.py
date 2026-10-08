"""Run an entirely synthetic freeze/verify exercise against an isolated local bare remote."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from verification_fixture import frame, observation, protocol  # noqa: E402

from enagis.data_io import file_hash, write_json  # noqa: E402
from enagis.science.runner import execute  # noqa: E402
from enagis.verification.analysis import analyze, init_records  # noqa: E402
from enagis.verification.bundle import prepare, read_json  # noqa: E402
from enagis.verification.contracts import Records  # noqa: E402
from enagis.verification.registration import seal, verify_seal  # noqa: E402


def run_git(repo, *args):
    env = dict(
        os.environ,
        GIT_AUTHOR_DATE="2026-10-08T00:00:00+00:00",
        GIT_COMMITTER_DATE="2026-10-08T00:00:00+00:00",
    )
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


def rehearse(output):
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("rehearsal output must be new or empty; existing evidence is retained")
    output.mkdir(parents=True, exist_ok=True)
    repo, remote = output / "repository", output / "remote.git"
    repo.mkdir()
    remote.mkdir()
    for path in (ROOT / "src/enagis").rglob("*.py"):
        destination = repo / path.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    shutil.copyfile(ROOT / "uv.lock", repo / "uv.lock")
    run_git(repo, "init", "--initial-branch=main")
    run_git(remote, "init", "--bare", "--initial-branch=main")
    run_git(repo, "config", "user.name", "Synthetic fixture")
    run_git(repo, "config", "user.email", "fixture@example.invalid")
    run_git(repo, "config", "core.autocrlf", "false")
    run_git(repo, "config", "commit.gpgsign", "false")
    run_git(repo, "config", "tag.gpgsign", "false")
    run_git(repo, "remote", "add", "origin", "../remote.git")
    execute(
        ROOT / "tests/fixtures/phase6-synthetic-config.json",
        ROOT / "tests/fixtures/phase6-synthetic-inputs.json",
        output / "science",
        repo / "uv.lock",
        allow_fixture=True,
    )
    write_json(output / "protocol.json", protocol())
    write_json(output / "frame.json", frame(file_hash(output / "science/index.json")))
    bundle = repo / "freezes/fixture-ranking-v1"
    prepare(
        output / "science",
        output / "protocol.json",
        output / "frame.json",
        bundle,
        repo / "uv.lock",
        allow_fixture=True,
    )
    run_git(repo, "add", "src", "uv.lock", "freezes")
    run_git(repo, "commit", "-m", "Synthetic Phase 7 rehearsal only")
    run_git(repo, "tag", "-a", "fixture-ranking-v1", "-m", "Synthetic fixture; no real ranking")
    run_git(repo, "push", "origin", "main", "refs/tags/fixture-ranking-v1")
    receipt = output / "seal.json"
    seal(bundle, receipt, repo, repo / "uv.lock", allow_fixture=True)
    capture = output / "synthetic-records.json"
    init_records(bundle, receipt, capture, repo, repo / "uv.lock", allow_fixture=True)
    blank = Records.model_validate_json(capture.read_bytes())
    outcomes = ["confirmed"] * 4 + [
        "node_absent",
        "undocumented_supply",
        "requirement_negligible",
        "seasonal_irrelevance",
        "unknown",
        "unreachable",
        "declined",
        "not_contacted",
    ]
    if len(blank.records) != len(outcomes):
        raise ValueError("synthetic rehearsal expects exactly twelve sampled nodes")
    # Only this explicit fixture generator supplies invented responses.
    blank.records = [
        observation(r.node_id, outcome) for r, outcome in zip(blank.records, outcomes, strict=True)
    ]
    write_json(capture, blank)
    before = file_hash(bundle / "manifest.json")
    result = analyze(
        bundle, receipt, capture, output / "analysis", repo, repo / "uv.lock", allow_fixture=True
    )
    verify_seal(bundle, receipt, repo, repo / "uv.lock", allow_fixture=True, check_remote=True)
    if file_hash(bundle / "manifest.json") != before:
        raise ValueError("analysis changed the frozen package")
    report = read_json(output / "analysis/report.json")
    summary = {
        "purpose": "synthetic_fixture",
        "freeze_id": blank.freeze_id,
        "sample": len(blank.records),
        "resolved": result["resolved"],
        "primary": report["arms"]["enagis"],
        "frozen_manifest_sha256": before,
        "shortlist_sha256": file_hash(bundle / "source/shortlist.json"),
        "sample_sha256": file_hash(bundle / "sample.json"),
        "analysis_report_sha256": file_hash(output / "analysis/report.json"),
        "remote": "isolated local bare repository; no public ranking tag created",
        "freeze_unchanged_after_analysis": True,
        "real_observations": 0,
    }
    write_json(output / "rehearsal.json", summary)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(rehearse(args.output), sort_keys=True))
