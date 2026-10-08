"""Prepare, seal and analyze prospective verification without rewriting the ranking."""

import argparse
import json
from pathlib import Path

from pydantic import ValidationError

from enagis.verification.analysis import analyze, init_records
from enagis.verification.bundle import prepare, verify_bundle
from enagis.verification.registration import seal, verify_seal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser(
        "prepare", help="Replay the approved ranking and prepare an unsealed package"
    )
    build.add_argument("--source", type=Path, required=True)
    build.add_argument("--protocol", type=Path, required=True)
    build.add_argument("--frame", type=Path, required=True)
    build.add_argument("--scientific-exit", type=Path)
    build.add_argument("--output", type=Path, required=True)
    check = sub.add_parser(
        "verify", help="Replay package; optionally check a seal against local/remote Git"
    )
    check.add_argument("--receipt", type=Path)
    check.add_argument("--check-remote", action="store_true")
    sealing = sub.add_parser(
        "seal", help="Record an existing annotated tag after verifying its remote"
    )
    sealing.add_argument("--remote", default="origin")
    sealing.add_argument("--output", type=Path, required=True)
    capture = sub.add_parser(
        "init-records", help="Create blank private rows after the freeze is sealed"
    )
    capture.add_argument("--output", type=Path, required=True)
    analysis = sub.add_parser(
        "analyze", help="Read private records and write only aggregate results"
    )
    analysis.add_argument("--records", type=Path, required=True)
    analysis.add_argument("--output", type=Path, required=True)
    for command in [check, sealing, capture, analysis]:
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--repo", type=Path, default=Path.cwd())
    for command in [capture, analysis]:
        command.add_argument("--receipt", type=Path, required=True)
    for command in [build, check, sealing, capture, analysis]:
        command.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
        command.add_argument("--allow-fixture", action="store_true")
    args = parser.parse_args()
    fixture = {"allow_fixture": args.allow_fixture}
    try:
        if args.command == "prepare":
            result = prepare(
                args.source,
                args.protocol,
                args.frame,
                args.output,
                args.lockfile,
                exit_path=args.scientific_exit,
                **fixture,
            )
        elif args.command == "seal":
            result = seal(
                args.bundle, args.output, args.repo, args.lockfile, remote=args.remote, **fixture
            )
        elif args.command == "verify":
            if args.check_remote and not args.receipt:
                raise ValueError("remote verification requires a seal receipt")
            if args.receipt:
                manifest, _, sample, _ = verify_seal(
                    args.bundle,
                    args.receipt,
                    args.repo,
                    args.lockfile,
                    check_remote=args.check_remote,
                    **fixture,
                )
            else:
                manifest, _, sample = verify_bundle(args.bundle, args.lockfile, **fixture)
            result = {
                "status": "sealed_verified" if args.receipt else "prepared_verified_unsealed",
                "freeze_id": manifest["freeze_id"],
                "purpose": manifest["purpose"],
                "sample": len(sample["rows"]),
            }
        elif args.command == "init-records":
            result = init_records(
                args.bundle, args.receipt, args.output, args.repo, args.lockfile, **fixture
            )
        else:
            result = analyze(
                args.bundle,
                args.receipt,
                args.records,
                args.output,
                args.repo,
                args.lockfile,
                **fixture,
            )
    except ValidationError as error:
        fields = [".".join(map(str, e["loc"])) for e in error.errors()]
        parser.exit(2, f"Phase 7 stopped: invalid fields {fields}; private values omitted\n")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"Phase 7 stopped: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
