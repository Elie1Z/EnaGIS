"""Invented Canadian-coordinate topology, not Canadian observations or recommendations."""

from pathlib import Path

from enagis.data_io import write_json
from enagis.science.contracts import PARAMETER_UNITS, Dataset, ScenarioConfig


def evidence(missing=None):
    return {
        "label": "UNKNOWN" if missing else "ESTIMATED",
        "source_ids": ["fixture:source"],
        "as_of": "2026-10-08",
        "licence": "MIT synthetic test data",
        "method": "Invented hand-checkable fixture; no real observations or scientific approval",
        "missing_reason": missing,
    }


def value(amount):
    return {
        "value": amount,
        "evidence": evidence("Intentionally unknown fixture" if amount is None else None),
    }


def point(lon=-106, lat=52):
    return {
        "crs": "EPSG:4326",
        "coordinate_order": "longitude_latitude",
        "longitude": lon,
        "latitude": lat,
        "source_crs": "EPSG:4326",
        "transformation_method": "Synthetic coordinates; no transformation",
    }


def make_fixture():
    fixed = {
        "residence_days": 10,
        "modeled_operating_days": 100,
        "wheat_storage_fraction": 0.5,
        "processing_fraction": 1,
        "airflow_per_tonne": 0.002,
        "static_pressure": 500,
        "fan_efficiency": 0.5,
        "motor_efficiency": 0.8,
        "simultaneous_fraction": 1,
        "cycle_hours": 100,
        "auxiliary_power": 0,
    }
    parameters = {
        name: {
            "unit": PARAMETER_UNITS[name],
            "lower": n,
            "central": n,
            "upper": n,
            "distribution": "fixed",
            "joint_group": name,
            "evidence": evidence(),
            "approval": None,
        }
        for name, n in fixed.items()
    }
    parameters["residence_days"].update(lower=8, upper=12, distribution="triangular")
    parameters["airflow_per_tonne"].update(
        lower=0.001, upper=0.003, distribution="triangular", joint_group="fixture:fan_duty"
    )
    parameters["static_pressure"].update(
        lower=400, upper=600, distribution="triangular", joint_group="fixture:fan_duty"
    )
    config = {
        "version": "phase6-v1",
        "scenario_id": "fixture:phase6",
        "purpose": "synthetic_fixture",
        "as_of": "2026-10-08",
        "metric_crs": "EPSG:3347",
        "distance_unit": "metre",
        "time_unit": "minute",
        "parameters": parameters,
        "transports": [
            {
                "profile_id": "fixture:vehicle",
                "mode": "vehicle",
                "vehicle_access_key": "hgv",
                "class_speed_kph": {"primary": 60, "service": 30},
                "surface_factors": {
                    "asphalt": {"dry": 1, "wet": 0.8},
                    "gravel": {"dry": 0.7, "wet": None},
                },
                "allowed_access_values": ["yes", "permissive", "designated"],
                "missing_access": "exclude",
                "max_snap_metres": 0.1,
                "connector_speed_kph": 5,
                "max_travel_minutes": 20,
                "evidence": evidence(),
                "approval": None,
                "limitations": ["Artificial graph with no node barriers or restrictions."],
            }
        ],
        "seasons": ["dry", "wet"],
        "assignment_variants": ["min_cost_max_served", "nearest_first"],
        "reference_case": "fixture:vehicle:dry:min_cost_max_served",
        "unknown_capacity": "exclude_and_flag",
        "mass_tolerance_tonnes": 1e-6,
        "draw_power": 4,
        "seed": 17,
        "ranking": {
            "top_k": 10,
            "robust_inclusion": 0.8,
            "interval_quantiles": [0.05, 0.95],
            "score": "technical_kw",
            "missing_supply_requires_verification": True,
            "approval": None,
        },
        "methods_approval": None,
        "joint_dependency_description": (
            "Fixture airflow and pressure share quantiles; residence independent."
        ),
        "production_proxy_description": "Invented point origins. Fractions preserve parent totals.",
        "limitations": ["Fixture parameters, tiers and ranks have no scientific interpretation."],
    }
    coordinates = {1: [-106, 52], 2: [-105.9, 52], 3: [-108, 53], 99: [-107.99, 53]}
    sites, roads = [], []
    for i in range(12):
        identity = 10 + i
        coordinates[identity] = [-105.995 + 0.008 * i, 52.01 + 0.002 * (i % 2)]
        sites.append(
            {
                "node_id": f"fixture:site{i:02d}",
                "location": point(*coordinates[identity]),
                "precision": "P2",
                "storage_tonnes": value(8 + i),
                "supply_state": "documented_known_capacity" if i < 4 else "no_documented_asset",
                "electrical_capacity_kw": value(0.025 if i < 4 else None),
                "supply_evidence": evidence(),
                "unresolved_question": None,
            }
        )
        roads.append(
            {
                "way_id": f"fixture:way{i}",
                "osm_version": 1,
                "node_ids": [1 if i < 6 else 2, identity],
                "coordinates_lon_lat": [coordinates[1 if i < 6 else 2], coordinates[identity]],
                "crs": "EPSG:4326",
                "evidence": evidence(),
                "tags": {
                    "highway": "service",
                    "surface": "gravel" if i >= 10 else "asphalt",
                    "access": "yes",
                },
            }
        )
    sites.append(
        {
            "node_id": "fixture:site_unknown",
            "location": point(*coordinates[99]),
            "precision": "P4",
            "storage_tonnes": value(None),
            "supply_state": "documented_unknown_capacity",
            "electrical_capacity_kw": value(None),
            "supply_evidence": evidence(),
            "unresolved_question": "Resolve fixture inventory.",
        }
    )
    for a, b in ((1, 2), (3, 99)):
        roads.append(
            {
                "way_id": f"fixture:link{a}",
                "osm_version": 1,
                "node_ids": [a, b],
                "coordinates_lon_lat": [coordinates[a], coordinates[b]],
                "crs": "EPSG:4326",
                "evidence": evidence(),
                "tags": {"highway": "primary", "surface": "asphalt", "access": "yes"},
            }
        )
    data = {
        "schema_version": "phase6-input-v1",
        "purpose": "synthetic_fixture",
        "region_id": "fixture:region",
        "provinces": ["TEST"],
        "commodity_id": "wheat_non_durum",
        "service_id": "ambient_air_aeration",
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
        "source_snapshots": [
            {
                "snapshot_id": "fixture:source",
                "publisher": "EnaGIS test authors",
                "original_url": "https://example.invalid/synthetic",
                "retrieved_on": "2026-10-08",
                "effective_on": "2024-01-01",
                "sha256": "0" * 64,
                "licence": "MIT synthetic test data",
                "licence_url": "https://opensource.org/license/mit",
                "redistribution": "permitted",
                "processing_step": "Invented test data",
            }
        ],
        "parents": [
            {"production_id": f"fixture:parent{i}", "tonnes": value(m)}
            for i, m in ((1, 350), (2, 350), (3, None))
        ],
        "origins": [
            {
                "origin_id": f"fixture:origin{i}",
                "production_id": f"fixture:parent{i}",
                "fraction": 1,
                "location": point(*coordinates[i]),
                "precision": "P4",
                "evidence": evidence(),
            }
            for i in (1, 2, 3)
        ],
        "sites": sites,
        "roads": roads,
        "data_approval": None,
        "network_review": None,
        "prepared_from_sha256": {},
    }
    return ScenarioConfig.model_validate(config), Dataset.model_validate(data)


if __name__ == "__main__":
    config, data = make_fixture()
    write_json(Path("tests/fixtures/phase6-synthetic-config.json"), config)
    write_json(Path("tests/fixtures/phase6-synthetic-inputs.json"), data)
