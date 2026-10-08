"""Reproducible SVG evaluation figures from the recorded Phase 4 report, without fitting."""

import argparse
from html import escape
from pathlib import Path

from enagis.data_io import file_hash, write_json
from scripts.build_demo import ROOT, read


def svg(title, subtitle, rows, unit, filename):
    """An interval plot on the metric's full scale; exact values stay in the sidecar."""
    height = 180 + len(rows) * 64
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" '
        f'viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>',
        '<rect width="100%" height="100%" fill="#F7F5F0"/>',
        '<g font-family="sans-serif" fill="#1B2430">',
        f'<text x="32" y="40" font-size="24">{escape(title)}</text>',
        f'<text x="32" y="68" font-size="14">{escape(subtitle)}</text>',
    ]
    x0, width = 260, 540
    minimum, maximum = (0, 1) if unit == "recall" else (-1, 1)

    def project(value):
        return x0 + width * (value - minimum) / (maximum - minimum)

    ticks = [i / 5 for i in range(6)] if unit == "recall" else [-1, -0.5, 0, 0.5, 1]
    for value in ticks:
        x = project(value)
        parts.append(
            f'<line x1="{x}" y1="95" x2="{x}" y2="{height - 58}" stroke="#E4DFD5"/>'
            f'<text x="{x}" y="{height - 32}" text-anchor="middle" font-size="12">'
            f"{value * 100 if unit == 'recall' else value:g}"
            f"{'%' if unit == 'recall' else ''}</text>"
        )
    for i, (label, mean, interval, highlight) in enumerate(rows):
        y = 124 + i * 64
        color = "#BE3B0A" if highlight else "#0F766E"
        lo, hi = interval
        text = (
            f"{mean * 100:.1f}% [{lo * 100:.1f}, {hi * 100:.1f}]"
            if unit == "recall"
            else f"{mean:.3f} [{lo:.3f}, {hi:.3f}]"
        )
        parts.extend(
            [
                f'<text x="32" y="{y + 5}" font-size="14">{escape(label)}</text>',
                f'<line x1="{project(lo)}" y1="{y}" x2="{project(hi)}" y2="{y}" '
                f'stroke="{color}" stroke-width="2"/>',
                f'<circle cx="{project(mean)}" cy="{y}" r="5" fill="{color}"/>',
                f'<text x="830" y="{y + 5}" font-size="12">{escape(text)}</text>',
            ]
        )
    parts.append("</g></svg>")
    filename.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def generate(output):
    output.mkdir(parents=True, exist_ok=True)
    path = ROOT / "demo/evidence/phase4/report.json"
    report = read(path)["data"]
    names = {
        "full_model": "Full model",
        "base_model": "Base model",
        "B0": "Production only",
        "B1": "Euclidean production",
        "B2": "Road production",
        "population": "Population",
        "nearest_presence": "Nearest presence",
        "area_only": "Area only",
    }
    primary = report["siting"]["primary"]
    rows = [
        (names[key], row["mean"], row["interval"], key == "full_model")
        for key, row in sorted(primary["arms"].items(), key=lambda entry: -entry[1]["mean"])
    ]
    svg(
        "Documented elevator presence: simple baselines compete",
        "Mean CAR recall, top 20% of CCS per block; 95% descriptive block-bootstrap intervals",
        rows,
        "recall",
        output / "siting-comparison.svg",
    )
    rows = [
        (key, row["spearman"], row["interval"], key == "EnaGIS_phase3")
        for key, row in report["hindcast"]["arms"].items()
    ]
    svg(
        "Shipping-point volume hindcast",
        "Retrospective Spearman rank diagnostic; 95% descriptive block intervals. "
        "Energy is unvalidated.",
        rows,
        "spearman",
        output / "hindcast-comparison.svg",
    )
    write_json(
        output / "source.json",
        {
            "source_path": "demo/evidence/phase4/report.json",
            "source_sha256": file_hash(path),
            "siting": {
                "primary": primary,
                "cohort_units": report["siting"]["cohort_units"],
                "positive_blocks": report["siting"]["positive_blocks"],
                "interpretation": report["siting"]["interpretation"],
            },
            "hindcast": report["hindcast"],
            "field_verification_n": 0,
            "scientific_completion": False,
        },
    )
    return {name.name: file_hash(name) for name in sorted(output.iterdir()) if name.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/figures")
    args = parser.parse_args()
    print(generate(args.output))


if __name__ == "__main__":
    main()
