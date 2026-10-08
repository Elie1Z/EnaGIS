"""Private observation capture and downstream-only, aggregate public analysis."""

from collections import Counter
from datetime import datetime
from pathlib import Path

from scipy.stats import binomtest

from enagis.data_io import file_hash, write_json
from enagis.verification.bundle import ensure_new_output, read_json
from enagis.verification.contracts import FAILURES, STRATA, Frame, Observation, Records
from enagis.verification.registration import git, verify_seal

RESOLVED = {*FAILURES, "confirmed"}


def private_path(path, root, purpose, bundle):
    path, root, bundle = Path(path).resolve(), Path(root).resolve(), Path(bundle).resolve()
    if path == bundle or path.is_relative_to(bundle) or bundle.is_relative_to(path):
        raise ValueError("observations must remain outside the frozen package")
    if purpose == "scientific_reviewed":
        if not path.is_relative_to(root / "data/validation_private"):
            raise ValueError("real verification records must stay under data/validation_private")
        git(root, "check-ignore", "-q", "--", path.relative_to(root).as_posix())
    return path


def init_records(bundle, receipt_path, output, root, lockfile, *, allow_fixture=False):
    manifest, protocol, sample, _ = verify_seal(
        bundle, receipt_path, root, lockfile, allow_fixture=allow_fixture
    )
    output = private_path(output, root, protocol.purpose, bundle)
    if output.exists():
        raise ValueError("capture file already exists; never overwrite observations")
    rows = [
        Observation(
            node_id=r["node_id"],
            observed_at=None,
            method=None,
            contact_status="not_contacted",
            consent="not_requested",
            node_exists=None,
            undocumented_supply=None,
            requirement_negligible=None,
            seasonal_irrelevance=None,
            outcome="not_contacted",
            evidence_private_ref=None,
            assessor_private_ref=None,
        )
        for r in sample["rows"]
    ]
    records = Records(
        schema_version="phase7-records-v1",
        purpose=protocol.purpose,
        freeze_id=manifest["freeze_id"],
        frozen_manifest_sha256=file_hash(Path(bundle) / "manifest.json"),
        records=rows,
    )
    write_json(output, records)
    return {"status": "blank_capture_created", "rows": len(rows), "purpose": protocol.purpose}


def group_summary(ids, records, protocol, sampled_ids=None):
    selected = [records.get(n) for n in ids]
    sampled_ids = set(ids) if sampled_ids is None else sampled_ids
    counts = Counter(
        "not_sampled" if n not in sampled_ids else r.outcome if r else "not_contacted"
        for n, r in zip(ids, selected, strict=True)
    )
    resolved = sum(counts[k] for k in RESOLVED)
    confirmed = counts["confirmed"]
    unresolved = len(ids) - resolved
    interval = None
    if resolved:
        ci = binomtest(confirmed, resolved).proportion_ci(
            confidence_level=protocol.confidence_level, method="wilson"
        )
        interval = {"lower": ci.low, "upper": ci.high}
    return {
        "target_count": len(ids),
        "attempted": sum(r is not None and r.contact_status != "not_contacted" for r in selected),
        "completed_with_consent": sum(
            r is not None and r.contact_status == "completed" for r in selected
        ),
        "resolved": resolved,
        "confirmed": confirmed,
        "unresolved": unresolved,
        "outcomes": {
            key: counts[key]
            for key in [
                *FAILURES,
                "confirmed",
                "unknown",
                "unreachable",
                "declined",
                "not_contacted",
                "not_sampled",
            ]
        },
        "resolved_fraction_confirmed": confirmed / resolved if resolved else None,
        "resolved_fraction_wilson_interval": interval,
        "all_target_confirmation_bounds": {
            "lower": confirmed / len(ids),
            "upper": (confirmed + unresolved) / len(ids),
        }
        if ids
        else None,
        "precision_at_k": confirmed / len(ids) if ids and not unresolved else None,
        "precision_status": "complete_target"
        if ids and not unresolved
        else "not_testable_incomplete_target",
    }


def summarize(records, manifest, sample, protocol, frame, ranking):
    by_id = {r.node_id: r for r in records.records}
    ranked = sorted((r for r in ranking if r["rank"] is not None), key=lambda r: r["rank"])
    arm_ids = {"enagis": [r["node_id"] for r in ranked[: protocol.top_k]]}
    unavailable = []
    for arm in frame.baselines:
        if arm.ordered_node_ids:
            arm_ids[arm.arm_id] = arm.ordered_node_ids[: protocol.top_k]
        else:
            # No user-entered reason/prose is copied to aggregate output.
            unavailable.append(arm.arm_id)
    sampled_ids = {r["node_id"] for r in sample["rows"]}
    arms = {name: group_summary(ids, by_id, protocol, sampled_ids) for name, ids in arm_ids.items()}
    for name, arm in arms.items():
        arm["sampled_in_target"] = sum(
            n in {r["node_id"] for r in sample["rows"]} for n in arm_ids[name]
        )
    strata = {}
    for name in STRATA:
        ids = [r["node_id"] for r in sample["rows"] if r["stratum"] == name]
        stats = group_summary(ids, by_id, protocol)
        # Middle/lower/supplements are sample fractions, never whole-stratum precision@k.
        stats.pop("precision_at_k")
        stats.pop("precision_status")
        strata[name] = stats
    sampled = {r["node_id"] for r in sample["rows"]}
    union = set().union(*map(set, arm_ids.values()))
    common_complete = all(n in by_id and by_id[n].outcome in RESOLVED for n in union)
    resolved_sample = sum(n in by_id and by_id[n].outcome in RESOLVED for n in sampled)
    # These counts are deliberately allowed to overlap; the primary outcome above is exclusive.
    failures = {
        key: sum(
            r.failure_flags()[key] is True
            for r in records.records
            if r.contact_status == "completed"
        )
        for key in FAILURES
    }
    return {
        "schema_version": "phase7-aggregate-v1",
        "purpose": protocol.purpose,
        "freeze_id": manifest["freeze_id"],
        "source_run_id": manifest["source_run_id"],
        "sample_size": len(sampled),
        "records_supplied": len(records.records),
        "resolved_sample_size": resolved_sample,
        "minimum_required": protocol.minimum_sample,
        "verification_status": "minimum_resolved_count_met"
        if resolved_sample >= protocol.minimum_sample
        else "insufficient_resolved_verification",
        "arms": arms,
        "unavailable_arms": sorted(unavailable),
        "baseline_comparison_status": (
            "no_available_baseline"
            if len(arms) == 1
            else "available_arms_share_complete_observed_union"
            if common_complete
            else "not_testable_incomplete_common_outcomes"
        ),
        "strata": strata,
        "overlapping_failure_flags": failures,
        "confidence_level": protocol.confidence_level,
        "interval_method": protocol.interval_method,
        "interpretation": [
            "Synthetic fixtures are not field evidence."
            if protocol.purpose == "synthetic_fixture"
            else "Reported verification does not independently prove facility performance.",
            "Wilson intervals describe confirmed fractions among resolved observations under a "
            "binomial working model; nonresponse and spatial dependence are not covered.",
            "Bounds retain every unresolved or unsampled target as unknown; "
            "they are not confidence intervals.",
            "No pooled population accuracy, recall, calibrated viability or worldwide "
            "transfer claim is estimated.",
            "Strata and targeted supplements are reported separately; "
            "no retrospective reranking or replacement occurs.",
        ],
    }


def analyze(bundle, receipt_path, records_path, output, root, lockfile, *, allow_fixture=False):
    manifest, protocol, sample, receipt = verify_seal(
        bundle, receipt_path, root, lockfile, allow_fixture=allow_fixture
    )
    records_path = private_path(records_path, root, protocol.purpose, bundle)
    records = Records.model_validate_json(records_path.read_bytes())
    manifest_hash = file_hash(Path(bundle) / "manifest.json")
    if (
        records.freeze_id != manifest["freeze_id"]
        or records.frozen_manifest_sha256 != manifest_hash
    ):
        raise ValueError("verification records refer to a different frozen ranking/sample")
    records.validate_against(sample, protocol, datetime.fromisoformat(receipt["sealed_at"]))
    output = ensure_new_output(output, [bundle, records_path, receipt_path, lockfile])
    frame = Frame.model_validate_json((Path(bundle) / "frame.json").read_bytes())
    report = summarize(
        records,
        manifest,
        sample,
        protocol,
        frame,
        read_json(Path(bundle) / "source/ranking.json")["data"],
    )
    report["frozen_manifest_sha256"] = manifest_hash
    report["private_records_sha256"] = file_hash(records_path)
    report["seal_sha256"] = file_hash(Path(receipt_path))
    write_json(output / "report.json", report)
    write_json(
        output / "index.json",
        {
            "schema_version": "phase7-report-index-v1",
            "freeze_id": manifest["freeze_id"],
            "report_sha256": file_hash(output / "report.json"),
            "frozen_manifest_sha256": manifest_hash,
        },
    )
    return {
        "status": report["verification_status"],
        "purpose": protocol.purpose,
        "sample": len(sample["rows"]),
        "resolved": report["resolved_sample_size"],
    }
