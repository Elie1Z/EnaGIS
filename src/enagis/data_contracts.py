"""Additive Phase 2 input contracts, separate from scenario/allocation results."""

from pathlib import PurePosixPath
from typing import Literal

from pydantic import Field, model_validator

from enagis.contracts import (
    ID,
    Contract,
    Evidence,
    Hash,
    Nonnegative,
    RunMetadata,
    Snapshot,
    SpatialID,
    Text,
    Value,
)


class SourceEntry(Contract):
    dataset_name: Text
    snapshot: Snapshot
    local_path: Text
    byte_count: int = Field(gt=0)
    role: ID
    effective_date_precision: Text
    attribution: Text
    licence_evidence_url: Text
    output_artifacts: list[Text]

    @model_validator(mode="after")
    def raw_path(self):
        path = PurePosixPath(self.local_path)
        if (
            path.is_absolute()
            or "\\" in self.local_path
            or ".." in path.parts
            or path.parts[:2] != ("data", "raw")
            or len(path.parts) < 3
        ):
            raise ValueError("snapshot path must be relative and contained in data/raw")
        return self


class Manifest(Contract):
    manifest_version: Literal["1.0.0"]
    sources: list[SourceEntry] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_sources(self):
        ids = [s.snapshot.snapshot_id for s in self.sources]
        paths = [s.local_path for s in self.sources]
        if len(ids) != len(set(ids)) or len(paths) != len(set(paths)):
            raise ValueError("duplicate snapshot ID or raw path")
        return self


class IngestionConfig(Contract):
    adapter_version: Literal["canada-v1"]
    region_id: ID
    province_units: list[Literal["AB", "SK", "MB"]]
    development_units: list[Literal["AB", "SK", "MB"]]
    transfer_units: list[Literal["AB", "SK", "MB"]]
    province_coordinate_envelopes: dict[str, tuple[float, float, float, float]]
    registry_point_precision: Literal["P2"]
    registry_precision_method: Text
    coordinate_attribute_tolerance_degrees: Nonnegative
    delivery_crop_year: Literal["2024-2025"]
    harvest_year: Literal[2024]
    identity_path: Text
    licensing_parser_controls_path: Text | None = None
    source_ids: dict[str, ID]

    @model_validator(mode="after")
    def partitions(self):
        for units in (self.province_units, self.development_units, self.transfer_units):
            if len(units) != len(set(units)):
                raise ValueError("duplicate province in ingestion partition")
        if set(self.development_units) & set(self.transfer_units):
            raise ValueError("development and transfer units overlap")
        if set(self.development_units + self.transfer_units) != set(self.province_units):
            raise ValueError("partitions do not cover ingestion footprint")
        if set(self.province_coordinate_envelopes) != set(self.province_units):
            raise ValueError("province coordinate validation envelopes missing")
        for west, south, east, north in self.province_coordinate_envelopes.values():
            if not -180 <= west < east <= 180 or not -90 <= south < north <= 90:
                raise ValueError("invalid coordinate envelope")
        return self


class Boundary(Contract):
    spatial_id: SpatialID
    province: ID
    name: Value[Text]
    geometry_crs: Literal["EPSG:3347"]
    geometry: dict
    source_geometry_sha256: Hash
    topology: Literal["valid_source", "repaired"]
    geometry_evidence: Evidence


class RegistrySourceRow(Contract):
    facility_id: ID
    node_id: ID
    source_record_id: ID
    province: ID
    original_properties: dict
    original_geometry: dict | None
    source_date_precision: Text
    precision_method: Text
    positive_reported_storage: bool
    location_quality: Literal["reported", "unknown", "conflict"]


class SpatialMatch(Contract):
    record_id: ID
    geography_type: ID
    matched_keys: list[ID]
    status: Literal["matched", "unmatched", "ambiguous", "province_conflict", "location_conflict"]
    evidence: Evidence


class GeographyOverlap(Contract):
    origin_key: ID
    target_key: ID
    intersection_area_m2: Nonnegative
    origin_area_fraction: Nonnegative
    evidence: Evidence


class ProductionLineage(Contract):
    production_id: ID
    province: ID
    reporting_geography_name: Text
    component_rows: list[dict] = Field(min_length=2)
    expression: Literal["Wheat, all - Wheat, durum"]
    province_control: bool
    evidence: Evidence


class RoadWay(Contract):
    way_id: ID
    osm_version: int = Field(gt=0)
    node_ids: list[int] = Field(min_length=2)
    coordinates_lon_lat: list[tuple[float, float]] = Field(min_length=2)
    crs: Literal["EPSG:4326"]
    tags: dict[str, str]
    evidence: Evidence

    @model_validator(mode="after")
    def coordinates(self):
        if len(self.node_ids) != len(self.coordinates_lon_lat):
            raise ValueError("road geometry and node IDs differ in length")
        if any(
            not -180 <= lon <= 180 or not -90 <= lat <= 90 for lon, lat in self.coordinates_lon_lat
        ):
            raise ValueError("invalid road longitude/latitude")
        if "highway" not in self.tags:
            raise ValueError("road way must retain its highway tag")
        return self


class RoadArtifact(Contract):
    metadata: RunMetadata
    source_snapshot_id: ID
    extract_timestamp: Text
    province: ID
    path: Text
    sha256: Hash
    way_count: int = Field(ge=0)
    rejected_way_count: int = Field(ge=0)
    routing_parameters_status: Literal["not_configured_no_travel_times"]
    licence: Literal["ODbL-1.0"]
    attribution: Text


class QualityIssue(Contract):
    code: ID
    record_id: ID
    source_ids: list[ID] = Field(min_length=1)
    detail: dict
    disposition: Text


class JoinAudit(Contract):
    name: ID
    left_before: int = Field(ge=0)
    right_before: int = Field(ge=0)
    output_rows: int = Field(ge=0)
    retained_left: int = Field(ge=0)
    unmatched_ids: list[ID]
    ambiguous_ids: list[ID]

    @model_validator(mode="after")
    def retained(self):
        if self.left_before != self.retained_left:
            raise ValueError("join lost or duplicated source records")
        return self
