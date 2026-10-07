"""Canadian pilot table adapters. Raw records are preserved beside canonical fields."""

import csv
import io
import json
import math
import unicodedata
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

from enagis.contracts import (
    Capacity,
    Conversion,
    Evidence,
    Facility,
    Location,
    Node,
    Outcome,
    Point,
    Production,
    Quantity,
    ShippingLink,
    SpatialID,
    Value,
)
from enagis.data_contracts import JoinAudit, ProductionLineage, QualityIssue, RegistrySourceRow

PROVINCES = {"Alberta": "AB", "Saskatchewan": "SK", "Manitoba": "MB"}
PRUID = {"48": "AB", "47": "SK", "46": "MB"}


def normalized_name(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).strip().upper().split())


def evidence(source, label="OBSERVED", method="As reported by source", reason=None):
    return Evidence(
        label=label,
        source_ids=[source.snapshot.snapshot_id],
        as_of=source.snapshot.effective_on,
        licence=source.snapshot.licence,
        method=method,
        missing_reason=reason,
    )


def sourced(value, source, label="OBSERVED", method="As reported by source", reason=None):
    if value is None:
        return Value(value=None, evidence=evidence(source, "UNKNOWN", method, reason))
    return Value(value=value, evidence=evidence(source, label, method))


def quantity(
    value,
    source,
    unit="tonne",
    label="OBSERVED",
    definition="As reported",
    start=None,
    end=None,
    reason=None,
):
    return Quantity(
        amount=sourced(value, source, label, definition, reason),
        unit=unit,
        dimension="storage_mass",
        definition=definition,
        period_start=start,
        period_end=end,
    )


def issue(code, record, source, detail, disposition):
    return QualityIssue(
        code=code,
        record_id=record,
        source_ids=[source.snapshot.snapshot_id],
        detail=detail,
        disposition=disposition,
    )


def registry_identity_key(properties: dict) -> str:
    # No row number/OBJECTID, guessed distance threshold, or source-year in internal identity.
    return "|".join(
        normalized_name(str(properties[field]))
        for field in ("PR", "Station", "Licensee", "Railway", "Longitude", "Latitude")
    )


def normalize_registry(path: Path, source, identity_rows: list[dict], config: dict):
    document = json.loads(path.read_bytes())
    if document.get("crs", {}).get("properties", {}).get("name") != "EPSG:4326":
        raise ValueError("registry CRS must explicitly declare EPSG:4326")
    identities = {row["identity_key"]: row for row in identity_rows}
    if len(identities) != len(identity_rows):
        raise ValueError("duplicate registry identity key")
    facilities, nodes, capacities, raw_rows, issues, exclusions = [], [], [], [], [], []
    seen_keys = set()
    for feature in document["features"]:
        p = feature["properties"]
        record_id = f"{source.snapshot.snapshot_id}:{p['OBJECTID']}"
        if p["PR"] not in config["province_units"] or p["Elevator_type"] != "Primary":
            exclusions.append(
                {
                    "source_record_id": record_id,
                    "properties": p,
                    "reason": "outside frozen province/class footprint",
                }
            )
            continue
        key = registry_identity_key(p)
        if key in seen_keys or key not in identities:
            raise ValueError(f"ambiguous or unregistered stable identity: {record_id}")
        seen_keys.add(key)
        identity = identities[key]
        facility_id, node_id = identity["facility_id"], identity["node_id"]
        amount = p.get("Capacity_tonne")
        usable = (
            not isinstance(amount, bool)
            and isinstance(amount, (float, int))
            and math.isfinite(amount)
            and amount > 0
        )
        if amount is not None and (
            isinstance(amount, bool)
            or not isinstance(amount, (float, int))
            or not math.isfinite(amount)
            or amount < 0
        ):
            issues.append(
                issue(
                    "invalid_storage_value",
                    facility_id,
                    source,
                    {"raw_value": amount},
                    "raw retained; canonical capacity UNKNOWN; no constraint inferred",
                )
            )
            amount = None
        if not usable:
            issues.append(
                issue(
                    "nonpositive_or_unknown_storage",
                    facility_id,
                    source,
                    {"raw_value": p.get("Capacity_tonne")},
                    "retained; storage eligibility unresolved; do not assume no asset",
                )
            )
        geometry = feature.get("geometry")
        point, quality = None, "unknown"
        if geometry and geometry.get("type") == "Point":
            lon, lat = geometry["coordinates"][:2]
            bounds = config["province_coordinate_envelopes"][p["PR"]]
            if (
                math.isfinite(lon)
                and math.isfinite(lat)
                and bounds[0] <= lon <= bounds[2]
                and bounds[1] <= lat <= bounds[3]
            ):
                point = Point(
                    crs="EPSG:4326",
                    coordinate_order="longitude_latitude",
                    longitude=lon,
                    latitude=lat,
                    source_crs="EPSG:4326",
                    transformation_method="Identity; GeoJSON source geometry retained",
                )
                quality = "reported"
                # Published attribute coordinates are rounded; flag disagreements beyond precision.
                for name, observed in (("Longitude", lon), ("Latitude", lat)):
                    if (
                        p.get(name) is not None
                        and abs(float(p[name]) - observed)
                        > config["coordinate_attribute_tolerance_degrees"]
                    ):
                        quality = "conflict"
                        issues.append(
                            issue(
                                "coordinate_attribute_conflict",
                                facility_id,
                                source,
                                {"field": name, "geometry": observed, "attribute": p[name]},
                                "source geometry retained; manual review before spatial use",
                            )
                        )
        if point is None:
            issues.append(
                issue(
                    "unusable_location",
                    facility_id,
                    source,
                    {"geometry": geometry},
                    "source retained; P5 UNKNOWN location, no invented geocoding",
                )
            )
        loc = Location(
            point=sourced(point, source, reason="Invalid/missing source point"),
            precision=config["registry_point_precision"] if point else "P5",
        )
        facilities.append(
            Facility(
                facility_id=facility_id,
                source_record_id=record_id,
                snapshot_id=source.snapshot.snapshot_id,
                name=sourced(p["Station"].strip(), source),
                operator=sourced(p.get("Licensee") or None, source, reason="Operator not reported"),
                facility_class=sourced(p["Elevator_type"], source),
                status_as_stated=sourced(
                    "Listed in the 2024 grain-elevator spatial source", source
                ),
                effective_on=source.snapshot.effective_on,
                location=loc,
            )
        )
        eligible = True if usable else None
        nodes.append(
            Node(
                node_id=node_id,
                facility_id=facility_id,
                facility_missing_reason=None,
                node_type="storage",
                origin="documented",
                existence=sourced("documented", source),
                stationary_service_eligible=eligible,
                eligibility_evidence=evidence(
                    source,
                    "INFERRED" if eligible else "UNKNOWN",
                    "Primary elevator with positive reported storage; "
                    "technical service candidate only",
                    None
                    if eligible
                    else "Positive physical storage not established by source value",
                ),
                location=loc,
                verification_question=(
                    "What installed fan capacity and wheat inventory are documented?"
                ),
            )
        )
        capacities.append(
            Capacity(
                capacity_id=f"{node_id}:storage",
                node_id=node_id,
                facility_id=facility_id,
                service_id="wheat_storage",
                status="known" if amount is not None else "unknown",
                original=quantity(
                    amount,
                    source,
                    definition=(
                        "Reported elevator storage tonnes, all commodities; "
                        "not wheat-specific inventory or fan power"
                    ),
                    reason="Source storage quantity invalid or absent; see raw record",
                ),
                conversion=None,
            )
        )
        raw_rows.append(
            RegistrySourceRow(
                facility_id=facility_id,
                node_id=node_id,
                source_record_id=record_id,
                province=p["PR"],
                original_properties=p,
                original_geometry=geometry,
                source_date_precision=source.effective_date_precision,
                precision_method=config["registry_precision_method"],
                positive_reported_storage=usable,
                location_quality=quality,
            )
        )
    if seen_keys != set(identities):
        raise ValueError("stable identity crosswalk includes unmatched source identities")
    return facilities, nodes, capacities, raw_rows, issues, exclusions


def normalize_deliveries(path: Path, source, raw_registry, config: dict):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        all_rows = list(csv.DictReader(stream))
    required = {"crop_year", "grain", "Province", "Station", "deliveries_kT"}
    if not all_rows or not required <= set(all_rows[0]):
        raise ValueError("CGC delivery source schema changed")
    outcomes, original_rows, groups = [], [], {}
    for row in all_rows:
        province = PROVINCES.get(row["Province"])
        if (
            row["crop_year"] != config["delivery_crop_year"]
            or row["grain"] != "Wheat"
            or province not in config["province_units"]
        ):
            continue
        key = (province, normalized_name(row["Station"]))
        if key in groups:
            raise ValueError(f"duplicate shipping-point outcome: {key}")
        from hashlib import sha256

        point_id = "ca:shipping:" + sha256("|".join(key).encode()).hexdigest()[:20]
        original = quantity(
            float(row["deliveries_kT"]),
            source,
            "kilotonne",
            definition="CGC shipping-point Wheat deliveries, not per-elevator volume",
            start=date(2024, 8, 1),
            end=date(2025, 7, 31),
        )
        converted = quantity(
            original.amount.value * 1000.0,
            source,
            label="ESTIMATED",
            definition="Exact SI conversion: kilotonnes multiplied by 1000",
            start=original.period_start,
            end=original.period_end,
        )
        conversion = Conversion(
            original=original,
            converted=converted,
            factor=1000.0,
            reviewed_by="EnaGIS adapter unit rule: SI kilotonne-to-tonne",
            evidence=evidence(source, "ESTIMATED", converted.definition),
        )
        split = "transfer" if key[0] in config["transfer_units"] else "development"
        outcomes.append(
            Outcome(
                outcome_id=f"{point_id}:2024-2025:Wheat",
                shipping_point_id=point_id,
                province=key[0],
                split=split,
                original=original,
                conversion=conversion,
            )
        )
        original_rows.append({"shipping_point_id": point_id, "row": row})
        groups[key] = point_id
    if not outcomes:
        raise ValueError("delivery slice is empty; verify source fields and frozen scope mapping")
    links, unmatched = [], []
    for registry in raw_registry:
        key = (registry.province, normalized_name(registry.original_properties["Station"]))
        if key in groups:
            links.append(
                ShippingLink(
                    facility_id=registry.facility_id,
                    shipping_point_id=groups[key],
                    match_method=(
                        "Exact province + Unicode-normalized, trimmed uppercase station; "
                        "no fuzzy match"
                    ),
                    evidence=Evidence(
                        label="INFERRED",
                        source_ids=[
                            source.snapshot.snapshot_id,
                            registry.source_record_id.split(":")[0],
                        ],
                        as_of=source.snapshot.effective_on,
                        licence=source.snapshot.licence,
                        method="Exact name crosswalk; facility volumes not assigned",
                        missing_reason=None,
                    ),
                )
            )
        else:
            unmatched.append(registry.facility_id)
    matched = {link.shipping_point_id for link in links}
    audit = JoinAudit(
        name="registry_to_shipping_point",
        left_before=len(raw_registry),
        right_before=len(outcomes),
        output_rows=len(raw_registry),
        retained_left=len(raw_registry),
        unmatched_ids=unmatched,
        ambiguous_ids=[],
    )
    summary = {
        "raw_rows": len(all_rows),
        "selected_outcomes": len(outcomes),
        "matched_facilities": len(links),
        "matched_points": len(matched),
        "unmatched_outcome_points": sorted(set(groups.values()) - matched),
        "outcome_mass_tonnes": sum(o.conversion.converted.amount.value for o in outcomes),
    }
    return outcomes, links, original_rows, audit, summary


def read_production_rows(path: Path, config: dict) -> tuple[list[dict], int]:
    with zipfile.ZipFile(path) as archive:
        with archive.open("32100002.csv") as stream:
            reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig"))
            retained, count = [], 0
            for row in reader:
                count += 1
                if (
                    row["REF_DATE"] == str(config["harvest_year"])
                    and row["Harvest disposition"] == "Production (metric tonnes)"
                    and row["Type of crop"] in ("Wheat, all", "Wheat, durum")
                ):
                    if any(province in row["GEO"] for province in PROVINCES):
                        if row["UOM"] != "Metric tonnes" or row["SCALAR_FACTOR"] != "units":
                            raise ValueError("production unit/scalar mismatch")
                        retained.append(row)
    return retained, count


def published_number(row: dict) -> float | None:
    if row["STATUS"] or not row["VALUE"].strip():
        return None  # F, x, .. etc. are not zero. Raw status/symbol remain in lineage.
    number = float(row["VALUE"])
    if not math.isfinite(number) or number < 0:
        raise ValueError("invalid published production quantity")
    return number


def normalize_production(rows: list[dict], source, geography_by_name: dict):
    grouped = defaultdict(dict)
    for row in rows:
        category = row["Type of crop"]
        if category in grouped[row["GEO"]]:
            raise ValueError("duplicate production geography/category")
        grouped[row["GEO"]][category] = row
    production, controls, lineage, issues = [], [], [], []
    for name, components in sorted(grouped.items()):
        if set(components) != {"Wheat, all", "Wheat, durum"}:
            raise ValueError(f"missing crop-component row: {name}")
        province = next(code for full, code in PROVINCES.items() if full in name)
        control = name in PROVINCES
        values = [published_number(components[crop]) for crop in ("Wheat, all", "Wheat, durum")]
        tonnes = None if any(v is None for v in values) else values[0] - values[1]
        if tonnes is not None and tonnes < 0:
            raise ValueError(f"durum exceeds total wheat: {name}")
        if control:
            spatial_id = SpatialID(
                country_code="CA",
                geography_type="province",
                boundary_vintage="2021",
                code={v: k for k, v in PRUID.items()}[province],
                source_geographic_id=components["Wheat, all"]["DGUID"],
            )
        else:
            if name not in geography_by_name:
                raise ValueError(f"unmatched production reporting geometry: {name}")
            spatial_id = geography_by_name[name].spatial_id
        production_id = f"{spatial_id.key}:2024:non-durum"
        if tonnes is None:
            issues.append(
                issue(
                    "unknown_non_durum_production",
                    production_id,
                    source,
                    {"component_status": {crop: row["STATUS"] for crop, row in components.items()}},
                    "retained UNKNOWN; suppressed/unreliable durum cannot be replaced with zero",
                )
            )
        method = (
            "Derived reporting-region total: published Wheat, all minus Wheat, durum; "
            "no finer spatial allocation"
        )
        original = quantity(
            tonnes,
            source,
            label="ESTIMATED",
            definition=method,
            start=date(2024, 1, 1),
            end=date(2024, 12, 31),
            reason="Missing, suppressed or unreliable published crop component",
        )
        observation = Production(
            production_id=production_id,
            geography=spatial_id,
            geometry_ref=spatial_id.key,
            geometry_crs="EPSG:3347",
            commodity_id="wheat_non_durum",
            original=original,
            conversion=None,
            modeled_tonnes=sourced(
                tonnes,
                source,
                "ESTIMATED",
                method,
                "Missing, suppressed or unreliable published crop component",
            ),
            spatial_allocation_method=(
                "Identity at reporting region; disaggregation is not configured"
            ),
        )
        (controls if control else production).append(observation)
        lineage.append(
            ProductionLineage(
                production_id=production_id,
                province=province,
                reporting_geography_name=name,
                component_rows=list(components.values()),
                expression="Wheat, all - Wheat, durum",
                province_control=control,
                evidence=evidence(source, "ESTIMATED", method),
            )
        )
    return production, controls, lineage, issues
