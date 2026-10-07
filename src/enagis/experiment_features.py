"""Label-free production, population and road covariates; no node allocation imports."""

import numpy as np
from scipy.spatial.distance import cdist
from shapely.geometry import shape

from enagis.contracts import Evidence, Value
from enagis.experiment_contracts import FeatureRow
from enagis.experiment_network import catchment_masks


def build_features(units, production, sadr, network, protocol):
    protocol.require_approval()
    by_region = {p.geometry_ref: p for p in production}
    area = {b.spatial_id.key: shape(b.geometry).area for b in sadr}
    graph, xy, road_lengths, junctions, network_audit = network
    masses, contexts = [], []
    for u in units:
        overlaps = u.production_intersections_m2
        if not overlaps or any(
            key not in by_region or by_region[key].modeled_tonnes.value is None for key in overlaps
        ):
            masses.append(None)
            contexts.append(None)
            continue
        masses.append(
            sum(
                by_region[key].modeled_tonnes.value * value / area[key]
                for key, value in overlaps.items()
            )
        )
        contexts.append(
            sum(by_region[key].modeled_tonnes.value * value for key, value in overlaps.items())
            / sum(overlaps.values())
        )
    points = [u.point_xy for u in units]
    b1_masks = cdist(points, points) <= protocol.catchment_distance_m
    b2_masks, snaps, snap_valid = catchment_masks(graph, xy, points, protocol)
    production_sources = sorted(
        {s for p in production for s in p.modeled_tonnes.evidence.source_ids}
        | {"statcan-ccs-digital-2021", "aafc-fieldcrop-production-20261007"}
    )
    road_sources = sorted(set(network_audit["source_ids"] + ["statcan-ccs-digital-2021"]))
    # An unsnapped origin nearby could contribute mass: do not silently treat it as zero.
    uncertain_road_coverage = (b1_masks & ~snap_valid[None, :]).any(axis=1)

    def amount(value, method, sources, missing):
        return Value(
            value=value,
            evidence=Evidence(
                label="UNKNOWN" if value is None else "ESTIMATED",
                source_ids=sources,
                as_of="2024-01-01",
                licence="Source licences retained; OSM derivatives ODbL-1.0",
                method=method,
                missing_reason=missing if value is None else None,
            ),
        )

    def masked_sum(mask):
        values = [masses[j] for j in np.flatnonzero(mask)]
        return None if not values or any(v is None for v in values) else sum(values)

    rows = []
    for i, u in enumerate(units):
        features = {
            "production_context": amount(
                contexts[i],
                "B0: overlap-area weighted source SADR tonnes context; not CCS tonnage",
                production_sources,
                "Missing contributing regional production",
            ),
            "euclidean_production": amount(
                masked_sum(b1_masks[i]),
                "B1: uniform-area CCS mass proxies at representative points "
                "in configured metric buffer",
                production_sources,
                "Unknown production in Euclidean catchment",
            ),
            "accessible_production": amount(
                masked_sum(b2_masks[i])
                if snap_valid[i] and not uncertain_road_coverage[i]
                else None,
                "B2: uniform-area mass proxies within undirected road-distance budget "
                "plus point connectors; development footprint only",
                sorted(set(production_sources + road_sources)),
                "Unknown reachable production or potentially reachable point beyond snap tolerance",
            ),
            "population": u.population,
            "road_density": amount(
                float(road_lengths[i] / 1000 / (u.area_m2 / 1e6)),
                "Selected road km per polygon km2",
                road_sources,
                None,
            ),
            "junction_density": amount(
                float(junctions[i] / (u.area_m2 / 1e6)),
                "Topology degree >=3 nodes per polygon km2",
                road_sources,
                None,
            ),
        }
        rows.append(
            FeatureRow(
                unit_id=u.unit_id,
                block_id=u.block_id,
                province=u.province,
                features=features,
                snap_distance_m=float(snaps[i]),
                missing_reasons=[
                    v.evidence.missing_reason for v in features.values() if v.value is None
                ],
            )
        )
    proxy_audit = []
    for key, p in sorted(by_region.items()):
        covered = sum(u.production_intersections_m2.get(key, 0) for u in units)
        if covered > area[key] + 1:
            raise ValueError("CCS/source-region overlap double counts area")
        mass = p.modeled_tonnes.value
        proxy_audit.append(
            {
                "production_id": p.production_id,
                "source_area_m2": area[key],
                "covered_area_m2": covered,
                "input_tonnes": mass,
                "represented_tonnes": None if mass is None else mass * covered / area[key],
                "outside_ccs_footprint_tonnes": None
                if mass is None
                else mass * (1 - covered / area[key]),
            }
        )
    return rows, {
        "production_proxy": proxy_audit,
        "network": network_audit,
        "known_ccs_mass_proxies": sum(v is not None for v in masses),
        "snapped_units": int(snap_valid.sum()),
        "units_with_uncertain_road_origin_coverage": int(uncertain_road_coverage.sum()),
        "no_label_sources_used": True,
    }
