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
    args = parser.parse_args()
    try:
        if args.command == "schema":
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
