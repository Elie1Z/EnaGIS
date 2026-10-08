"""Small offline contract validator and deterministic fixture smoke command."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from pydantic import ValidationError

from enagis.validation import Bundle, FixtureSuite, smoke


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    smoke_parser = commands.add_parser("smoke")
    smoke_parser.add_argument("--fixture", type=Path, required=True)
    validate_parser = commands.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    schema_parser = commands.add_parser("schema")
    schema_parser.add_argument("--output", type=Path, required=True)
    for command in ("acquire", "ingest"):
        data_parser = commands.add_parser(command)
        data_parser.add_argument("--manifest", type=Path, default=Path("docs/data/manifest.json"))
        data_parser.add_argument("--root", type=Path, default=Path.cwd())
        data_parser.add_argument("--skip-licensing", action="store_true")
        if command == "ingest":
            data_parser.add_argument(
                "--config", type=Path, default=Path("configs/regions/ca-prairies.json")
            )
            data_parser.add_argument("--output", type=Path, default=Path("data/processed/phase2"))
    data_schema_parser = commands.add_parser("data-schema")
    data_schema_parser.add_argument("--output", type=Path, required=True)
    verify_data_parser = commands.add_parser("verify-data")
    verify_data_parser.add_argument("path", type=Path)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--root", type=Path, default=Path.cwd())
    run_parser.add_argument("--input", type=Path, default=Path("data/processed/phase2"))
    run_parser.add_argument("--region", type=Path, default=Path("configs/regions/ca-prairies.json"))
    run_parser.add_argument(
        "--scenario", type=Path, default=Path("configs/scenarios/phase3-engineering-v1.json")
    )
    run_parser.add_argument("--manifest", type=Path, default=Path("docs/data/manifest.json"))
    run_parser.add_argument("--output", type=Path, default=Path("outputs/phase3"))
    run_parser.add_argument("--allow-temporary-scenario", action="store_true")
    verify_run_parser = commands.add_parser("verify-run")
    verify_run_parser.add_argument("path", type=Path)
    trace_parser = commands.add_parser("trace")
    trace_parser.add_argument("path", type=Path)
    trace_parser.add_argument("--node-id", required=True)
    for command in (
        "prepare-experiment",
        "diagnose-experiment",
        "register-experiment",
        "evaluate-experiment",
    ):
        experiment_parser = commands.add_parser(command)
        experiment_parser.add_argument("--root", type=Path, default=Path.cwd())
        experiment_parser.add_argument(
            "--protocol", type=Path, default=Path("configs/experiments/phase4-canada-v1.1.json")
        )
        experiment_parser.add_argument(
            "--preparation", type=Path, default=Path("data/processed/phase4")
        )
        if command in ("register-experiment", "evaluate-experiment"):
            experiment_parser.add_argument(
                "--registration", type=Path, default=Path("data/manual/phase4-preregistration.json")
            )
        if command == "evaluate-experiment":
            experiment_parser.add_argument("--output", type=Path, default=Path("outputs/phase4"))
            experiment_parser.add_argument("--phase3", type=Path, default=Path("outputs/phase3"))
        if command == "diagnose-experiment":
            experiment_parser.add_argument(
                "--output", type=Path, default=Path("docs/audits/phase4-v1.1-cohorts.json")
            )
        if command == "register-experiment":
            experiment_parser.add_argument("--publish", action="store_true")
    verify_experiment_parser = commands.add_parser("verify-experiment")
    verify_experiment_parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare-experiment":
            from enagis.experiment_prepare import prepare_experiment

            print(
                json.dumps(prepare_experiment(args.root, args.protocol, args.preparation), indent=2)
            )
        elif args.command == "diagnose-experiment":
            from enagis.experiment_cohort import diagnose_cohorts

            print(
                json.dumps(
                    diagnose_cohorts(args.root, args.protocol, args.preparation, args.output),
                    indent=2,
                )
            )
        elif args.command == "register-experiment":
            from enagis.experiment import register_experiment

            print(
                json.dumps(
                    register_experiment(
                        args.root,
                        args.protocol,
                        args.preparation,
                        args.registration,
                        publish=args.publish,
                    ),
                    indent=2,
                )
            )
        elif args.command == "evaluate-experiment":
            from enagis.experiment import evaluate_experiment

            report = evaluate_experiment(
                args.root,
                args.protocol,
                args.preparation,
                args.registration,
                args.output,
                args.phase3,
            )
            print(
                json.dumps(
                    {
                        "siting_status": report["siting"]["status"],
                        "siting_decision": report["siting"]["decision"],
                        "hindcast_status": report["hindcast"]["status"],
                    },
                    indent=2,
                )
            )
        elif args.command == "verify-experiment":
            from enagis.experiment import verify_experiment

            print(json.dumps(verify_experiment(args.path), indent=2))
        elif args.command == "run":
            from enagis.pipeline import run_pipeline
            from enagis.pipeline_validation import verify_run

            audit = run_pipeline(
                args.root,
                args.input,
                args.region,
                args.scenario,
                args.manifest,
                args.output,
                args.allow_temporary_scenario,
            )
            print(
                json.dumps(
                    {
                        "verification": verify_run(args.output),
                        "disclaimer": audit["disclaimer"],
                        "known_input_tonnes": audit["known_input_tonnes"],
                        "assigned_tonnes": audit["assigned_tonnes"],
                        "explicit_unserved_tonnes": audit["explicit_unserved_tonnes"],
                        "shortlist": str(args.output / "engineering-shortlist.csv"),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        elif args.command == "verify-run":
            from enagis.pipeline_validation import verify_run

            print(json.dumps(verify_run(args.path), indent=2, sort_keys=True))
        elif args.command == "trace":
            from enagis.pipeline_validation import trace_node

            print(json.dumps(trace_node(args.path, args.node_id), indent=2, sort_keys=True))
        elif args.command == "acquire":
            from enagis.acquire import acquire_manifest

            acquire_manifest(args.manifest, args.root, args.skip_licensing)
        elif args.command == "ingest":
            from enagis.ingestion import ingest

            summary = ingest(
                args.manifest, args.config, args.root, args.output, args.skip_licensing
            )
            print(
                json.dumps(
                    {
                        "run_id": summary["metadata"]["run_id"],
                        "registry": summary["registry"],
                        "production": summary["production"],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        elif args.command == "verify-data":
            from enagis.data_validation import verify_data

            print(json.dumps(verify_data(args.path), indent=2, sort_keys=True))
        elif args.command == "data-schema":
            from enagis.data_schema import schemas

            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(schemas(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        elif args.command == "schema":
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(Bundle.model_json_schema(), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        elif args.command == "validate":
            Bundle.model_validate_json(args.path.read_bytes())
            print("Contract valid")
        else:
            suite = FixtureSuite.model_validate_json(args.fixture.read_bytes())
            print(json.dumps(smoke(suite), indent=2, sort_keys=True))
    except (ValidationError, ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
