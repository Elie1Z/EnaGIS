"""Explicit conversion of reviewed grain airflow guidance; no standard bushel mass."""

from typing import Literal

from pydantic import Field, model_validator

from enagis.contracts import Contract, Evidence, Nonnegative, Text, Value


class BushelAirflow(Contract):
    airflow_cfm_per_bushel: Value[Nonnegative]
    airflow_bushel_basis: Literal["avery", "winchester", "source_unspecified"]
    test_weight_kg_per_bushel: Value[Nonnegative]
    test_weight_bushel_basis: Literal["avery", "winchester", "source_unspecified"]
    applicability: Text
    # Explicitly supplied engineering interpretation; source approval stays in scenario config.
    basis_review_ref: Text | None

    @model_validator(mode="after")
    def positive_mass(self):
        mass = self.test_weight_kg_per_bushel.value
        if mass is not None and mass <= 0:
            raise ValueError("test weight must be positive or explicitly UNKNOWN")
        return self


class AirflowConversion(Contract):
    unit: Literal["m3/s/tonne"]
    amount: Value[Nonnegative]
    input: BushelAirflow
    method: Text
    conversion_factors: dict[str, float] = Field(min_length=1)


def convert_airflow(value: BushelAirflow) -> AirflowConversion:
    q, mass = value.airflow_cfm_per_bushel, value.test_weight_kg_per_bushel
    missing = None
    if q.value is None or mass.value is None:
        missing = "Airflow or grain test weight is UNKNOWN; no fixed bushels/tonne assumption"
    elif "source_unspecified" in (value.airflow_bushel_basis, value.test_weight_bushel_basis):
        missing = "Source bushel basis must be resolved before converting to airflow per tonne"
    elif value.airflow_bushel_basis != value.test_weight_bushel_basis:
        missing = "Airflow and test-weight bushel bases differ; a reviewed conversion is required"
    elif value.basis_review_ref is None:
        missing = "A documented review of the matching bushel basis is required"
    # International foot is exactly 0.3048 m. This factor is dimensional, not a grain assumption.
    cubic_foot_m3 = 0.3048**3
    result = None if missing else q.value * cubic_foot_m3 / 60 * 1000 / mass.value
    evidence = Evidence(
        label="UNKNOWN" if missing else "ESTIMATED",
        source_ids=sorted(set(q.evidence.source_ids + mass.evidence.source_ids)),
        as_of=max(q.evidence.as_of, mass.evidence.as_of),
        licence="Input source licences retained in the conversion trace",
        method="cfm/bushel * (0.3048^3 m3/ft3) / 60 * (1000 kg/tonne) / (kg/bushel)",
        missing_reason=missing,
    )
    return AirflowConversion(
        unit="m3/s/tonne",
        amount=Value(value=result, evidence=evidence),
        input=value,
        method=evidence.method,
        conversion_factors={
            "m3_per_cubic_foot": cubic_foot_m3,
            "seconds_per_minute": 60,
            "kg_per_tonne": 1000,
        },
    )
