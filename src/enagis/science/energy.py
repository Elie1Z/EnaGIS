"""Storage aeration physics. Cycle energy is never relabeled annual consumption."""


def annual_limit(storage_tonnes, p):
    if storage_tonnes is None:
        return None
    return (
        storage_tonnes
        * p["wheat_storage_fraction"]
        * p["modeled_operating_days"]
        / (p["residence_days"] * p["processing_fraction"])
    )


def requirement(tonnes, p):
    if tonnes is None:
        return {
            k: None
            for k in (
                "incoming_tonnes_per_period",
                "treated_tonnes_per_period",
                "inventory_tonnes",
                "simultaneous_inventory_tonnes",
                "airflow_m3_s",
                "fan_kw",
                "auxiliary_kw",
                "electrical_kw",
                "electricity_kwh_one_cycle",
                "kwh_per_active_tonne_one_cycle",
            )
        }
    treated = tonnes * p["processing_fraction"]
    inventory = treated * p["residence_days"] / p["modeled_operating_days"]
    active = inventory * p["simultaneous_fraction"]
    airflow = active * p["airflow_per_tonne"]
    fan = airflow * p["static_pressure"] / (1000 * p["fan_efficiency"] * p["motor_efficiency"])
    auxiliary = p["auxiliary_power"] if active > 0 else 0.0
    power = fan + auxiliary
    energy = power * p["cycle_hours"]
    return {
        "incoming_tonnes_per_period": tonnes,
        "treated_tonnes_per_period": treated,
        "inventory_tonnes": inventory,
        "simultaneous_inventory_tonnes": active,
        "airflow_m3_s": airflow,
        "fan_kw": fan,
        "auxiliary_kw": auxiliary,
        "electrical_kw": power,
        "electricity_kwh_one_cycle": energy,
        "kwh_per_active_tonne_one_cycle": energy / active if active > 0 else None,
    }


def gap(state, capacity_kw, required_kw):
    if state not in {
        "no_documented_asset",
        "documented_known_capacity",
        "documented_unknown_capacity",
    }:
        raise ValueError("unknown supply state")
    if (capacity_kw is not None) != (state == "documented_known_capacity"):
        raise ValueError("supply state/capacity disagreement")
    margin, bucket, status = None, None, "unknown"
    if required_kw is None:
        bucket = "verify_first"
    elif state == "documented_unknown_capacity":
        bucket, status = "verify_first", "flagged"
    elif state == "no_documented_asset":
        if required_kw > 0:
            bucket, status = "undocumented_supply", "flagged"
    else:
        margin = capacity_kw - required_kw
        bucket, status = ("undersized", "flagged") if margin < 0 else (None, "unflagged")
    return {"capacity_minus_requirement_kw": margin, "bucket": bucket, "status": status}
