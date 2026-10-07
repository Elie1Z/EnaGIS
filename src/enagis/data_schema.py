"""Schema catalog for the input spine; distinct from the post-allocation bundle."""

from enagis.contracts import Artifact, Capacity, Facility, Node, Outcome, Production, ShippingLink
from enagis.data_contracts import (
    Boundary,
    GeographyOverlap,
    IngestionConfig,
    JoinAudit,
    Manifest,
    ProductionLineage,
    QualityIssue,
    RegistrySourceRow,
    RoadArtifact,
    RoadWay,
    SpatialMatch,
)


def schemas():
    models = [Manifest, IngestionConfig, RoadWay, RoadArtifact]
    rows = [
        Facility,
        Node,
        Capacity,
        Outcome,
        Production,
        ShippingLink,
        Boundary,
        GeographyOverlap,
        JoinAudit,
        ProductionLineage,
        QualityIssue,
        RegistrySourceRow,
        SpatialMatch,
    ]
    return {
        "schema_version": "1.0.0",
        "schemas": {
            model.__name__: model.model_json_schema()
            for model in models + [Artifact[row] for row in rows]
        },
    }
