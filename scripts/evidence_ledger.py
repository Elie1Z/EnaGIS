"""Count evidence labels in the data the application shows, and group every UNKNOWN by reason.

Reads only the built application (app/index.html embedded JSON). It changes nothing.
Usage: python -m scripts.evidence_ledger [--app app] [--output docs/audits/evidence-ledger.json]
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

LABELS = ("OBSERVED", "PREDICTED", "ESTIMATED", "INFERRED", "UNKNOWN")


def embedded(html, identity):
    match = re.search(
        rf'<script id="{identity}" type="application/json">(.*?)</script>', html, re.S
    )
    return json.loads(match.group(1))


def walk(value, path=""):
    """Yield (field path, evidence dict) for every labelled value or evidence object."""
    if isinstance(value, dict):
        if isinstance(value.get("evidence"), dict) and "label" in value["evidence"]:
            yield path, value["evidence"]
        elif "label" in value and "missing_reason" in value and "source_ids" in value:
            yield path, value
        for key, child in value.items():
            if key != "evidence":
                yield from walk(child, f"{path}.{key}" if path else key)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child, f"{path}[]")


def ledger(app: Path):
    html = (app / "index.html").read_text(encoding="utf-8")
    candidates = embedded(html, "candidate-data")
    shortlist = embedded(html, "demo-data")["nodes"]
    result = {}
    for name, rows in (("development_nodes", candidates), ("shortlist_traces", shortlist)):
        labels, fields, unknown = Counter(), defaultdict(Counter), defaultdict(Counter)
        for row in rows:
            for path, evidence in walk(row):
                labels[evidence["label"]] += 1
                fields[path][evidence["label"]] += 1
                if evidence["label"] == "UNKNOWN":
                    unknown[path][evidence.get("missing_reason") or "no reason recorded"] += 1
        result[name] = {
            "rows": len(rows),
            "labels": {label: labels.get(label, 0) for label in LABELS},
            "fields": {path: dict(counts) for path, counts in sorted(fields.items())},
            "unknown_by_reason": {path: dict(reasons) for path, reasons in sorted(unknown.items())},
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=Path("app"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = ledger(args.app)
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({k: v["labels"] | {"rows": v["rows"]} for k, v in report.items()}, indent=2))


if __name__ == "__main__":
    main()
