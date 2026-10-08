"""Exercise Git ancestry, freeze replay and downstream-only private analysis end to end."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest
from verification_fixture import frame, observation, protocol, ranking

from enagis.data_io import file_hash, write_json
from enagis.science.runner import canonical
from enagis.verification.analysis import analyze, group_summary, private_path, summarize
from enagis.verification.bundle import prepare, read_json, verify_bundle
from enagis.verification.contracts import Baseline, Frame, Protocol, Records
from enagis.verification.registration import remote_matches, seal, verify_seal
from enagis.verification.sampling import make_sample

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def rehearsal(tmp_path_factory):
    path = tmp_path_factory.mktemp("verification-rehearsal")
    spec = importlib.util.spec_from_file_location("rehearsal", ROOT / "scripts/phase7_rehearsal.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.rehearse(path)
    return path


def test_wilson_reference_and_unresolved_bounds_do_not_impute_failures():
    p = protocol()
    ids = [f"fixture:n{i}" for i in range(15)]
    records = {
        n: observation(n, "confirmed" if i < 12 else "node_absent") for i, n in enumerate(ids)
    }
    result = group_summary(ids, records, p)
    assert result["precision_at_k"] == 0.8
    ci = result["resolved_fraction_wilson_interval"]
    assert ci["lower"] == pytest.approx(0.5481455, abs=1e-6)
    assert ci["upper"] == pytest.approx(0.9295245, abs=1e-5)
    del records[ids[-1]]
    result = group_summary(ids, records, p)
    assert result["precision_at_k"] is None
    assert result["outcomes"]["not_contacted"] == 1
    assert result["all_target_confirmation_bounds"] == {"lower": 12 / 15, "upper": 13 / 15}
    empty = group_summary(ids, {}, p)
    assert empty["resolved_fraction_wilson_interval"] is None
    assert empty["all_target_confirmation_bounds"] == {"lower": 0, "upper": 1}


def test_baseline_incomplete_union_has_no_comparative_performance_claim():
    p, f, rows = protocol(), frame(), ranking()
    f.baselines[0] = Baseline(
        arm_id="B0",
        ordered_node_ids=[r["node_id"] for r in rows][::-1],
        evidence_ref="fixture:reversed",
        unavailable_reason=None,
    )
    sample = make_sample(rows, f, p)
    records = Records(
        schema_version="phase7-records-v1",
        purpose=p.purpose,
        freeze_id="fixture:freeze",
        frozen_manifest_sha256="0" * 64,
        records=[observation(r["node_id"]) for r in rows[:10]],
    )
    result = summarize(
        records, {"freeze_id": "fixture:freeze", "source_run_id": "fixture:run"}, sample, p, f, rows
    )
    assert result["arms"]["enagis"]["precision_at_k"] == 1
    assert result["arms"]["B0"]["precision_at_k"] is None
    assert result["arms"]["B0"]["outcomes"]["not_sampled"] == (
        10 - result["arms"]["B0"]["sampled_in_target"]
    )
    assert result["baseline_comparison_status"] == "not_testable_incomplete_common_outcomes"
    text = json.dumps(result)
    assert "DO-NOT-PUBLISH" not in text and "fixture:n01" not in text


def test_real_review_gate_stops_before_reading_any_source(tmp_path):
    pending = tmp_path / "review.json"
    write_json(pending, {"status": "pending_human_review"})
    with pytest.raises(ValueError, match="not human-approved"):
        prepare(
            tmp_path / "nonexistent",
            pending,
            tmp_path / "no-frame",
            tmp_path / "output",
            ROOT / "uv.lock",
        )
    assert not (tmp_path / "output").exists()


def test_real_records_require_private_ignored_location(tmp_path):
    with pytest.raises(ValueError, match="data/validation_private"):
        private_path(ROOT / "public-contact.json", ROOT, "scientific_reviewed", tmp_path / "freeze")


def test_complete_fixture_seal_analysis_and_remote_proof(rehearsal):
    repo = rehearsal / "repository"
    bundle = repo / "freezes/fixture-ranking-v1"
    manifest, _, sample, receipt = verify_seal(
        bundle,
        rehearsal / "seal.json",
        repo,
        repo / "uv.lock",
        allow_fixture=True,
        check_remote=True,
    )
    assert len(sample["rows"]) == 12
    assert receipt["tag"] == "fixture-ranking-v1"
    assert manifest["purpose"] == "synthetic_fixture"
    report = read_json(rehearsal / "analysis/report.json")
    assert report["sample_size"] == 12 and report["resolved_sample_size"] == 8
    assert report["arms"]["enagis"]["all_target_confirmation_bounds"] == {
        "lower": 0.4,
        "upper": 0.6,
    }
    assert report["arms"]["enagis"]["precision_at_k"] is None
    assert report["arms"]["enagis"]["resolved_fraction_confirmed"] == 0.5
    assert "DO-NOT-PUBLISH" not in json.dumps(report)
    assert report["verification_status"] == "insufficient_resolved_verification"


def test_remote_absence_cannot_produce_a_seal(rehearsal):
    repo = rehearsal / "repository"
    bundle = repo / "freezes/fixture-ranking-v1"
    with pytest.raises(ValueError, match="Git config failed"):
        seal(
            bundle,
            rehearsal / "missing-remote-seal.json",
            repo,
            repo / "uv.lock",
            remote="unconfigured",
            allow_fixture=True,
        )
    assert not (rehearsal / "missing-remote-seal.json").exists()
    receipt = read_json(rehearsal / "seal.json")
    with pytest.raises(ValueError, match="Git ls-remote failed"):
        remote_matches(
            repo, "../remote.git", "fixture-ranking-v99", receipt["tag_object"], receipt["commit"]
        )


def test_rehashing_a_modified_sample_does_not_defeat_replay(rehearsal):
    bundle = rehearsal / "repository/freezes/fixture-ranking-v1"
    sample_path, manifest_path = bundle / "sample.json", bundle / "manifest.json"
    original_sample, original_manifest = sample_path.read_bytes(), manifest_path.read_bytes()
    try:
        sample = read_json(sample_path)
        sample["rows"][0]["question"] = "Tampered after freeze"
        write_json(sample_path, sample)
        manifest = read_json(manifest_path)
        manifest["artifacts"]["sample.json"] = file_hash(sample_path)
        write_json(manifest_path, manifest)
        with pytest.raises(ValueError, match="deterministic prospective selection"):
            verify_bundle(bundle, ROOT / "uv.lock", allow_fixture=True)
    finally:
        sample_path.write_bytes(original_sample)
        manifest_path.write_bytes(original_manifest)


def test_analysis_rejects_wrong_freeze_and_preserves_every_frozen_byte(rehearsal):
    repo = rehearsal / "repository"
    bundle = repo / "freezes/fixture-ranking-v1"
    before = {
        p.relative_to(bundle).as_posix(): file_hash(p) for p in bundle.rglob("*") if p.is_file()
    }
    records = read_json(rehearsal / "synthetic-records.json")
    records["freeze_id"] = "fixture:wrong-freeze"
    write_json(rehearsal / "wrong-records.json", records)
    with pytest.raises(ValueError, match="different frozen"):
        analyze(
            bundle,
            rehearsal / "seal.json",
            rehearsal / "wrong-records.json",
            rehearsal / "wrong-analysis",
            repo,
            repo / "uv.lock",
            allow_fixture=True,
        )
    assert not (rehearsal / "wrong-analysis").exists()
    assert before == {
        p.relative_to(bundle).as_posix(): file_hash(p) for p in bundle.rglob("*") if p.is_file()
    }


def test_internally_consistent_new_protocol_cannot_replace_tagged_freeze(rehearsal):
    repo = rehearsal / "repository"
    bundle = repo / "freezes/fixture-ranking-v1"
    originals = {
        name: (bundle / name).read_bytes()
        for name in ["protocol.json", "sample.json", "manifest.json"]
    }
    try:
        p = Protocol.model_validate_json(originals["protocol.json"])
        p.seed += 1
        f = Frame.model_validate_json((bundle / "frame.json").read_bytes())
        write_json(bundle / "protocol.json", p)
        write_json(
            bundle / "sample.json",
            make_sample(read_json(bundle / "source/ranking.json")["data"], f, p),
        )
        manifest = read_json(bundle / "manifest.json")
        for name in ["protocol.json", "sample.json"]:
            manifest["artifacts"][name] = file_hash(bundle / name)
        manifest["sample_sha256"] = manifest["artifacts"]["sample.json"]
        manifest["protocol_sha256"] = manifest["artifacts"]["protocol.json"]
        identity = hashlib.sha256(canonical(manifest["artifacts"])).hexdigest()[:24]
        manifest["freeze_id"] = f"fixture:freeze:{identity}"
        write_json(bundle / "manifest.json", manifest)
        verify_bundle(bundle, repo / "uv.lock", allow_fixture=True)
        with pytest.raises(ValueError, match="tag does not contain the exact"):
            verify_seal(bundle, rehearsal / "seal.json", repo, repo / "uv.lock", allow_fixture=True)
    finally:
        for name, body in originals.items():
            (bundle / name).write_bytes(body)


def test_changed_seal_time_and_overwriting_freeze_are_rejected(rehearsal):
    repo = rehearsal / "repository"
    bundle = repo / "freezes/fixture-ranking-v1"
    receipt = read_json(rehearsal / "seal.json")
    receipt["sealed_at"] = "2020-01-01T00:00:00+00:00"
    write_json(rehearsal / "backdated-seal.json", receipt)
    with pytest.raises(ValueError, match="receipt does not match"):
        verify_seal(
            bundle, rehearsal / "backdated-seal.json", repo, repo / "uv.lock", allow_fixture=True
        )
    with pytest.raises(ValueError, match="outside the frozen"):
        seal(bundle, bundle / "receipt.json", repo, repo / "uv.lock", allow_fixture=True)
    with pytest.raises(ValueError, match="cannot be overwritten"):
        prepare(
            rehearsal / "science",
            rehearsal / "protocol.json",
            rehearsal / "frame.json",
            bundle,
            repo / "uv.lock",
            allow_fixture=True,
        )
