"""Explicit Phase 6 commands; no mutation of the registered Phase 4 experiment."""

import argparse
import json
from pathlib import Path

from enagis.science.audit import readiness
from enagis.science.runner import execute, verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser(
        "run", help="Run a reviewed scenario or an explicitly synthetic fixture"
    )
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--input", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--allow-fixture", action="store_true")
    run.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
    check = commands.add_parser("verify", help="Check hashes and replay the complete run")
    check.add_argument("output", type=Path)
    check.add_argument("--lockfile", type=Path, default=Path("uv.lock"))
    audit = commands.add_parser("audit", help="Audit readiness without fitting or scoring")
    audit.add_argument("--input-dir", type=Path, default=Path("data/processed/phase2"))
    audit.add_argument(
        "--review", type=Path, default=Path("configs/scenarios/phase6-canada-v1.review.json")
    )
    audit.add_argument("--output", type=Path, default=Path("docs/audits/phase6-readiness.json"))
    args = parser.parse_args()
    try:
        if args.command == "run":
            result = execute(
                args.config,
                args.input,
                args.output,
                args.lockfile,
                allow_fixture=args.allow_fixture,
            )
        elif args.command == "verify":
            result = verify(args.output, args.lockfile)
        else:
            result = readiness(args.input_dir, args.review, args.output)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f"Phase 6 stopped: {error}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
