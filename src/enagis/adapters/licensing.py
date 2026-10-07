"""Restricted CGC station-table audit. Parsed company rows stay in private outputs."""

import re
from collections import Counter, defaultdict
from pathlib import Path

from pypdf import PdfReader

from enagis.adapters.canada import normalized_name


def operator_key(name):
    return "".join(c for c in normalized_name(name) if c.isalnum())


def parse_station_page(text: str, page_number: int):
    lines = text.splitlines()
    header = next((line for line in lines if "STATION" in line and "LICENSEE" in line), None)
    if header is None or "Tableau 11" not in text[:300]:
        return []
    compact_title = "".join(c for c in text[:300].upper() if c.isalpha())
    province = next(
        (
            code
            for name, code in (("MANITOBA", "MB"), ("SASKATCHEWAN", "SK"), ("ALBERTA", "AB"))
            if name in compact_title
        ),
        None,
    )
    if province is None:
        return []
    railway, licensee, licence, tonnes = (
        header.index(word) for word in ("RLY.", "LICENSEE", "LICENCE", "TONNES")
    )
    station, rows = None, []
    for line in lines[lines.index(header) + 2 :]:
        if "Canadian Grain Commission" in line or "Commission canadienne" in line:
            break
        category = re.search(
            r"\b(P\s*r\s*i\.|P\s*r\s*o\s*c\.|T\s*e\s*r\s*m\.)\s+([\d,]+)\s*$", line[licence:]
        )
        operator = line[licensee:licence].strip()
        # Source footnote superscripts are aligned after whitespace; retain company numbers.
        operator = re.sub(r"\s{2,}(?:\d+|[A-Z])\s*$", "", operator).strip()
        if category:
            reported_station = line[:railway].strip()
            station = reported_station or station
            if not station or not operator:
                raise ValueError(f"licensing table parse needs review on page {page_number}")
            rows.append(
                {
                    "province": province,
                    "station": station,
                    "railway": line[railway:licensee].strip(),
                    "operator": operator,
                    "class": re.sub(r"\s", "", category.group(1)),
                    "storage_tonnes": int(category.group(2).replace(",", "")),
                    "pdf_page": page_number,
                }
            )
        elif rows and operator and not line[:licensee].strip():
            rows[-1]["operator"] += " " + operator
    return rows


def positioned_station_text(page):
    """Reconstruct columns from PDF text positions, including reflected November matrices.

    Visitor text sometimes joins railway and tonnes into one event; split that field using
    the table's two independently declared headers. One PDF point is a typography grouping
    tolerance, not a geospatial/scientific threshold.
    """
    events = []

    def visitor(text, cm, tm, font, size):
        if text.strip():
            x = tm[4] * cm[0] + tm[5] * cm[2] + cm[4]
            y = tm[4] * cm[1] + tm[5] * cm[3] + cm[5]
            events.append((text.strip(), x, y))

    page.extract_text(visitor_text=visitor)
    headers = {
        text: (x, y)
        for text, x, y in events
        if text in ("STATION", "RLY.", "LICENSEE", "LICENCE", "TONNES")
    }
    if len(headers) != 5:
        return ""
    title = " ".join(text for text, x, y in events if y > headers["STATION"][1])
    if "Tableau 11" not in title:
        return ""
    groups = []
    for text, x, y in sorted(events, key=lambda event: (-event[2], event[1])):
        if y >= headers["STATION"][1] - 15 or y < 35:
            continue
        if not groups or abs(groups[-1][0] - y) > 1:
            groups.append((y, []))
        groups[-1][1].append((text, x))
    # Scale to roomy fixed columns; data coordinates are compared to source header positions.
    stops = [headers[h][0] for h in ("STATION", "RLY.", "LICENSEE", "LICENCE", "TONNES")]
    lines = [
        title,
        "STATION".ljust(40)
        + "RLY.".ljust(15)
        + "LICENSEE".ljust(120)
        + "LICENCE".ljust(15)
        + "TONNES",
        "GARE",
    ]
    for _y, pieces in groups:
        cells = [[], [], [], [], []]
        for text, x in pieces:
            index = (
                max(i for i, stop in enumerate(stops) if x >= stop - 2) if x >= stops[0] - 2 else 0
            )
            if index == 1:
                merged = re.fullmatch(r"([A-Z]+\d?)\s+([\d,]+)", text)
                if merged:
                    cells[1].append(merged.group(1))
                    cells[4].append(merged.group(2))
                    continue
            if index == 2 and re.fullmatch(r"\d+|[A-Z]", text):
                continue  # separately positioned footnote, not part of company name
            cells[index].append(text)
        values = [" ".join(cell) for cell in cells]
        lines.append(
            f"{values[0]:<40}{values[1]:<15}{values[2]:<120}{values[3]:>15}{values[4]:>16}"
        )
    return "\n".join(lines)


def parse_licensing(path: Path):
    rows = []
    for index, page in enumerate(PdfReader(path).pages):
        text = positioned_station_text(page)
        rows.extend(parse_station_page(text, index + 1))
    if not rows:
        raise ValueError("licensing report contains no parseable Prairie station rows")
    return rows


def reconcile_licensing(entries, paths, registry_rows, controls):
    reports, private, prior = [], [], None
    for source in sorted(entries, key=lambda e: e.snapshot.effective_on):
        rows = parse_licensing(paths[source.snapshot.snapshot_id])
        primary = [row for row in rows if row["class"] == "Pri."]
        by_key = defaultdict(list)
        for row in primary:
            by_key[
                (row["province"], normalized_name(row["station"]), operator_key(row["operator"]))
            ].append(row)
        counts = Counter(row["province"] for row in primary)
        storage_totals = Counter()
        for row in primary:
            storage_totals[row["province"]] += row["storage_tonnes"]
        control = controls[source.snapshot.snapshot_id]
        if (
            dict(counts) != control["primary_rows_by_province"]
            or dict(storage_totals) != control["storage_tonnes_by_province"]
        ):
            raise ValueError(
                f"licensing parser differs from Table 9 controls: {source.snapshot.snapshot_id}"
            )
        matched, unmatched, ambiguous, differing_capacity = [], [], [], []
        for registry in registry_rows:
            p = registry.original_properties
            key = (registry.province, normalized_name(p["Station"]), operator_key(p["Licensee"]))
            candidates = by_key.get(key, [])
            if len(candidates) == 1:
                matched.append(registry.facility_id)
                if candidates[0]["storage_tonnes"] != p["Capacity_tonne"]:
                    differing_capacity.append(registry.facility_id)
            elif candidates:
                ambiguous.append(registry.facility_id)
            else:
                unmatched.append(registry.facility_id)
        keys = set(by_key)
        changes = (
            None
            if prior is None
            else {
                "new_listed_keys": len(keys - prior),
                "no_longer_listed_keys": len(prior - keys),
                "interpretation": (
                    "List membership changes only; not confirmed opening or closure dates"
                ),
            }
        )
        reports.append(
            {
                "snapshot_id": source.snapshot.snapshot_id,
                "effective_on": source.snapshot.effective_on.isoformat(),
                "primary_rows": len(primary),
                "primary_rows_by_province": dict(sorted(counts.items())),
                "storage_tonnes_by_province": dict(sorted(storage_totals.items())),
                "parser_control_status": "matches_independent_table9_counts_and_storage_totals",
                "matched_registry_rows": len(matched),
                "unmatched_registry_rows": len(unmatched),
                "ambiguous_registry_rows": len(ambiguous),
                "reported_storage_disagreements": len(differing_capacity),
                "changes_from_previous_report": changes,
            }
        )
        private.append(
            {
                "snapshot_id": source.snapshot.snapshot_id,
                "parsed_rows": rows,
                "unmatched_facility_ids": unmatched,
                "ambiguous_facility_ids": ambiguous,
                "storage_disagreement_facility_ids": differing_capacity,
            }
        )
        prior = keys
    return {
        "status": "audited_private_source_rows",
        "reports": reports,
        "resolution": (
            "Dated disagreements retained for review. Restricted source fields never "
            "replace the open registry. No absence or opening/closure inference."
        ),
    }, private
