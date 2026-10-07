"""Small offline contract validator and deterministic fixture smoke command."""

import argparse
import json
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
    args = parser.parse_args()
    try:
        if args.command == "acquire":
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
    except (ValidationError, ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
