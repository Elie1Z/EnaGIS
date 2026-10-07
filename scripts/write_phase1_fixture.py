"""Author the synthetic contract examples. Expected answers are in the fixture guide.

This creates literal test data, not scientific predictions. It is never a pipeline step.
"""

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2024-08-01"
END = "2025-07-31"
SERVICE = "toy_aeration"
SOURCE = "synthetic-2024-v1"
# Independent literal answers from the worked fixture guide; never derived by an allocator.
EXPECTED = {
    "single": (12.0, 0.0, {"SP1": 12.0}),
    "competing": (10.0, 0.0, {"SP1": 10.0}),
    "known_capacity": (8.0, 0.0, {"SP1": 8.0}),
    "unknown_capacity": (8.0, 0.0, {"SP1": 8.0}),
    "overflow": (7.0, 3.0, {"SP1": 7.0}),
    "logistics_only": (5.0, 0.0, {"SP1": 5.0}),
    "missing_facility": (5.0, 0.0, {}),
    "unreachable": (0.0, 10.0, {}),
}


def evidence(label="ESTIMATED", reason=None):
    return {
        "label": label,
        "source_ids": [SOURCE],
        "as_of": DATE,
        "licence": "CC0-1.0",
        "method": "Authored synthetic Phase 1 example; no real scientific claim",
        "missing_reason": reason,
    }


def value(item, label="ESTIMATED", reason=None):
    return {"value": item, "evidence": evidence("UNKNOWN" if item is None else label, reason)}


def quantity(amount, unit="tonne", label="OBSERVED", period=False):
    dimensions = {"tonne": "storage_mass", "kilotonne": "storage_mass", "kW": "electric_power"}
    return {
        "amount": value(amount, label, "Not reported in toy source" if amount is None else None),
        "unit": unit,
        "dimension": dimensions[unit],
        "definition": "Synthetic test quantity",
        "period_start": DATE if period else None,
        "period_end": END if period else None,
    }


def location(unlocated=False):
    point = {
        "crs": "EPSG:4326",
        "coordinate_order": "longitude_latitude",
        "longitude": -110.0,
        "latitude": 52.0,
        "source_crs": "EPSG:4326",
        "transformation_method": "Identity; synthetic point",
    }
    return {
        "point": value(
            None if unlocated else point,
            "OBSERVED",
            "Unlocated synthetic record" if unlocated else None,
        ),
        "precision": "P5" if unlocated else "P1",
    }


def facility(number):
    return {
        "facility_id": f"F{number}",
        "source_record_id": f"{SOURCE}:row-{number}",
        "snapshot_id": SOURCE,
        "name": value(f"Toy facility {number}", "OBSERVED"),
        "operator": value(None, reason="Operator not reported"),
        "facility_class": value("primary_elevator", "OBSERVED"),
        "status_as_stated": value("licensed", "OBSERVED"),
        "effective_on": DATE,
        "location": location(),
    }


def node(number, missing=False, logistics=False):
    return {
        "node_id": f"N{number}",
        "facility_id": None if missing else f"F{number}",
        "facility_missing_reason": "No linked registry record" if missing else None,
        "node_type": "logistics_only" if logistics else ("candidate" if missing else "storage"),
        "origin": "rule_based" if missing else "documented",
        "existence": value(
            None if missing else "documented",
            "OBSERVED",
            "Candidate existence unverified" if missing else None,
        ),
        "stationary_service_eligible": None if missing else not logistics,
        "eligibility_evidence": evidence(
            "UNKNOWN" if missing else "OBSERVED",
            "Stationary service unverified" if missing else None,
        ),
        "location": location(missing),
        "verification_question": "Is a stationary fan documented?",
    }


def geo(code):
    return {
        "country_code": "CA",
        "geography_type": "toy_ccs",
        "boundary_vintage": "2021",
        "code": code,
        "source_geographic_id": f"toy:{code}",
    }


def requirement(number, unknown=False):
    return {
        "node_id": f"N{number}",
        "service_id": SERVICE,
        "inventory_scenario_ref": "toy-inventory",
        "electrical_kw": value(
            None
            if unknown
            else {"lower": 3.0, "central": 4.0, "upper": 5.0, "distribution_ref": "toy-range"},
            reason="Service/parameters not established" if unknown else None,
        ),
        "electricity_kwh": value(
            None
            if unknown
            else {"lower": 30.0, "central": 40.0, "upper": 50.0, "distribution_ref": "toy-range"},
            reason="Service/parameters not established" if unknown else None,
        ),
        "cycle_or_period": "Synthetic ten-hour test cycle",
        "peak_power_method": "Literal fixture",
        "parameter_refs": ["toy-only-not-approved-for-science"],
    }


def case(case_id, amounts, capacities, *, missing=False, logistics=False, unserved=0.0):
    scenario = f"toy-{case_id}"
    metadata = {
        "schema_version": "1.0.0",
        "run_id": "phase1-fixture",
        "region_id": "toy-ca",
        "commodity_id": "toy_wheat",
        "service_id": SERVICE,
        "scenario_id": scenario,
        "period_start": DATE,
        "period_end": END,
        "config_sha256": sha256(b"phase1-synthetic-settings-v1").hexdigest(),
        "input_snapshot_ids": [SOURCE],
        "seed": 17,
    }
    snapshot = {
        "snapshot_id": SOURCE,
        "publisher": "EnaGIS fixture authors",
        "original_url": "urn:enagis:synthetic:phase1-v1",
        "retrieved_on": DATE,
        "effective_on": DATE,
        "sha256": sha256(b"synthetic-phase1-source-v1").hexdigest(),
        "licence": "CC0-1.0",
        "licence_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "redistribution": "permitted",
        "processing_step": "Literal authored fixture",
    }
    total = sum(amounts) + unserved
    original = quantity(total, period=True)
    prod = {
        "production_id": "Z1",
        "geography": geo("Z1"),
        "geometry_ref": "toy-zone-1",
        "geometry_crs": "EPSG:3347",
        "commodity_id": "toy_wheat",
        "original": original,
        "conversion": None,
        "modeled_tonnes": value(total),
        "spatial_allocation_method": "Literal synthetic zone; no disaggregation",
    }
    bundle = {
        "region_config": {
            "region_id": "toy-ca",
            "country_code": "CA",
            "development_units": ["AB", "SK"],
            "transfer_units": ["MB"],
            "adapter_version": "toy-v1",
            "boundary_vintage": "2021",
            "point_crs": "EPSG:4326",
            "metric_crs": "EPSG:3347",
            "projection_review_ref": "toy-projection-not-for-routing",
        },
        "metadata": metadata,
        "snapshots": [snapshot],
        "facilities": [],
        "nodes": [],
        "production": [prod],
        "travel": [],
        "catchments": [],
        "allocations": [],
        "capacities": [],
        "inventories": [],
        "requirements": [],
        "supplies": [],
        "gaps": [],
        "uncertainty": [],
        "shortlist": [],
        "shipping_links": [],
        "outcomes": [],
        "partitions": [
            {
                "spatial_id": geo("AB"),
                "region_unit_id": "AB",
                "block_id": "toy-AB-1",
                "split": "development",
                "feature_fit_allowed": True,
                "model_selection_allowed": True,
            },
            {
                "spatial_id": geo("MB"),
                "region_unit_id": "MB",
                "block_id": "toy-MB-1",
                "split": "transfer",
                "feature_fit_allowed": False,
                "model_selection_allowed": False,
            },
        ],
        "siting_features": [
            {
                "feature_id": "production",
                "source_ids": [SOURCE],
                "unit": "tonne/period",
                "construction_method": "Toy upstream source",
                "upstream_label_free": True,
            }
        ],
    }
    for i, (mass, cap) in enumerate(zip(amounts, capacities, strict=True), start=1):
        bundle["nodes"].append(node(i, missing, logistics))
        if not missing:
            bundle["facilities"].append(facility(i))
            bundle["shipping_links"].append(
                {
                    "facility_id": f"F{i}",
                    "shipping_point_id": "SP1",
                    "match_method": "Authored link",
                    "evidence": evidence("OBSERVED"),
                }
            )
        bundle["travel"].append(
            {
                "origin_id": "Z1",
                "node_id": f"N{i}",
                "graph_snapshot_id": SOURCE,
                "scenario_id": scenario,
                "mode": "toy-road",
                "travel_minutes": value(10.0),
                "reachable": True,
                "metric_crs": "EPSG:3347",
            }
        )
        bundle["catchments"].append(
            {
                "origin_id": "Z1",
                "node_id": f"N{i}",
                "scenario_id": scenario,
                "travel_limit_minutes": 20.0,
                "travel_minutes": 10.0,
                "method_ref": "toy-limit",
                "evidence": evidence(),
            }
        )
        bundle["allocations"].append(
            {
                "allocation_id": f"A{i}",
                "production_id": "Z1",
                "node_id": f"N{i}",
                "unserved_reason": None,
                "scenario_id": scenario,
                "assigned_tonnes": value(mass),
                "inventory_scenario_ref": "toy-inventory",
            }
        )
        unknown_requirement = missing or logistics
        req = requirement(i, unknown_requirement)
        bundle["requirements"].append(req)
        supply = {
            "node_id": f"N{i}",
            "service_id": SERVICE,
            "state": "no_documented_asset"
            if unknown_requirement
            else ("documented_unknown_capacity" if cap is None else "documented_known_capacity"),
            "capacity_ref": None if unknown_requirement else f"C{i}",
            "documentation_scope": "Synthetic aeration records only; no absence claim",
            "evidence": evidence("INFERRED"),
        }
        bundle["supplies"].append(supply)
        if not unknown_requirement:
            bundle["capacities"].append(
                {
                    "capacity_id": f"C{i}",
                    "node_id": f"N{i}",
                    "facility_id": f"F{i}",
                    "service_id": SERVICE,
                    "status": "unknown" if cap is None else "known",
                    "original": quantity(cap, "kW"),
                    "conversion": None,
                }
            )
            bundle["inventories"].append(
                {
                    "node_id": f"N{i}",
                    "stored_tonnes": value(None, reason="No inventory scenario yet"),
                    "residence_scenario_ref": "toy-residence",
                    "occupancy_scenario_ref": "toy-occupancy",
                }
            )
        margin = None if cap is None or unknown_requirement else cap - 4.0
        bucket = (
            None
            if unknown_requirement
            else ("verify_first" if cap is None else ("undersized" if margin < 0 else None))
        )
        gap = {
            "node_id": f"N{i}",
            "service_id": SERVICE,
            "dimension": "electric_power",
            "unit": "kW",
            "capacity_minus_requirement_kw": value(
                margin, reason="Comparable capacity/service unavailable" if margin is None else None
            ),
            "bucket": bucket,
            "classification": "unknown"
            if unknown_requirement
            else ("flagged" if bucket else "unflagged"),
            "classification_evidence": evidence("INFERRED"),
            "policy_ref": "toy-sign-policy-not-scientific",
        }
        bundle["gaps"].append(gap)
        bundle["uncertainty"].append(
            {
                "node_id": f"N{i}",
                "seed": 17,
                "draw_count": 4,
                "included_draws": 3,
                "inclusion_frequency": 0.75,
                "tier": "contested",
                "policy_ref": "toy-membership",
                "joint_scenario_refs": [scenario],
                "magnitude_kw": req["electrical_kw"],
                "evidence": evidence("INFERRED"),
            }
        )
        bundle["shortlist"].append(
            {
                "node_id": f"N{i}",
                "rank": i,
                "tier": "contested",
                "location": location(missing),
                "requirement": req,
                "supply": supply,
                "gap": gap,
                "evidence": evidence("INFERRED"),
                "verification_question": "Is a stationary fan documented?",
                "freeze_id": "toy-freeze",
                "shortlist_version": "toy-v1",
                "shortlist_sha256": sha256(b"toy-frozen-shortlist-v1").hexdigest(),
            }
        )
    if unserved:
        bundle["allocations"].append(
            {
                "allocation_id": "AU",
                "production_id": "Z1",
                "node_id": None,
                "unserved_reason": "Toy allocation limit or no reachable node",
                "scenario_id": scenario,
                "assigned_tonnes": value(unserved),
                "inventory_scenario_ref": "toy-inventory",
            }
        )
    groups = {} if missing or not amounts else {"SP1": sum(amounts)}
    if groups:
        orig = quantity(sum(amounts) / 1000, "kilotonne", period=True)
        converted = quantity(sum(amounts), "tonne", "ESTIMATED", period=True)
        bundle["outcomes"].append(
            {
                "outcome_id": "O1",
                "shipping_point_id": "SP1",
                "province": "AB",
                "split": "development",
                "original": orig,
                "conversion": {
                    "original": deepcopy(orig),
                    "converted": converted,
                    "factor": 1000.0,
                    "reviewed_by": "Fixture unit review",
                    "evidence": evidence(),
                },
            }
        )
    return {
        "case_id": case_id,
        "explanation": "Synthetic numbers; see tests/fixtures/README.md",
        "bundle": bundle,
        "expected_served_tonnes": EXPECTED[case_id][0],
        "expected_unserved_tonnes": EXPECTED[case_id][1],
        "expected_group_tonnes": EXPECTED[case_id][2],
    }


cases = [
    case("single", [12.0], [6.0]),
    case("competing", [6.0, 4.0], [6.0, 3.0]),
    case("known_capacity", [8.0], [3.0]),
    case("unknown_capacity", [8.0], [None]),
    case("overflow", [7.0], [6.0], unserved=3.0),
    case("logistics_only", [5.0], [None], logistics=True),
    case("missing_facility", [5.0], [None], missing=True),
    case("unreachable", [], [], unserved=10.0),
]
target = ROOT / "tests" / "fixtures" / "phase1.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(
    json.dumps({"fixture_only": True, "cases": cases}, indent=2) + "\n", encoding="utf-8"
)
