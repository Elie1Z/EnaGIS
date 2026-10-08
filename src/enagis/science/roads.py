"""Directed scenario travel times, conservative unsupported-tag handling and snap audit.

This is a screening network, not a turn-by-turn or legal freight routing service.
Way data do not include node barriers or turn-restriction relations; real use is gated.
"""

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree

from enagis.science.contracts import Transport
from enagis.science.geography import inside_area, projection


def access_keys(profile):
    if profile.mode == "foot":
        return ["access", "foot"]
    if profile.mode == "bicycle":
        return ["access", "vehicle", "bicycle"]
    specific = "motorcycle" if profile.mode == "motorbike" else profile.vehicle_access_key
    return ["access", "vehicle", "motor_vehicle", specific]


def speed_limit(text):
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(?:\s*(km/h|mph))?", text)
    if not match:
        return None
    value = float(match[1]) * (1.609344 if match[2] == "mph" else 1)
    return value if value > 0 else None


def way_policy(tags: dict, profile: Transport, season: str):
    if season not in {"dry", "wet"}:
        raise ValueError("unknown season")
    highway = tags["highway"]
    if highway not in profile.class_speed_kph:
        return None, "unconfigured_highway"
    # Conditions, directional access and freight dimensions need additional inputs/logic.
    unsupported = (
        "maxweight",
        "maxaxleload",
        "maxheight",
        "maxwidth",
        "maxlength",
        "barrier",
        "ford",
        "ice_road",
        "winter_road",
        "seasonal",
        "impassable",
    )
    if any(
        ":conditional" in k
        or k in unsupported
        or (
            k.endswith((":forward", ":backward"))
            and k != "maxspeed:forward"
            and k != "maxspeed:backward"
        )
        for k in tags
    ):
        return None, "unsupported_restriction_review"
    access = None
    for key in access_keys(profile):
        if key in tags:
            access = tags[key]
    if access is None:
        if profile.missing_access == "exclude":
            return None, "access_unknown"
    elif access not in profile.allowed_access_values:
        return None, "access_restricted_or_unresolved"
    surface = profile.surface_factors.get(tags.get("surface", "UNKNOWN"))
    if surface is None:
        return None, "surface_unconfigured"
    factor = getattr(surface, season)
    if factor is None:
        return None, "scenario_impassable"
    speed = profile.class_speed_kph[highway] * factor
    general_oneway = tags.get("oneway")
    if general_oneway is None and (tags.get("junction") == "roundabout" or highway == "motorway"):
        general_oneway = "yes"
    oneway = None
    for key in access_keys(profile)[1:]:
        oneway = tags.get(f"oneway:{key}", oneway)
    if oneway is None:
        if profile.mode == "foot":
            if general_oneway and highway in {"footway", "path", "corridor"}:
                return None, "pedestrian_oneway_ambiguous"
            oneway = (general_oneway or "no") if highway in {"steps", "via_ferrata"} else "no"
        else:
            oneway = general_oneway or "no"
    if oneway not in {"yes", "1", "true", "-1", "no", "0", "false"}:
        return None, "oneway_unresolved"
    forward, backward = oneway != "-1", oneway not in {"yes", "1", "true"}
    speeds = []
    for direction in ("forward", "backward"):
        capped = speed
        limit = tags.get(f"maxspeed:{direction}", tags.get("maxspeed"))
        if limit is not None and profile.mode in {"vehicle", "motorbike"}:
            maximum = speed_limit(limit)
            if maximum is None:
                return None, "maxspeed_unresolved"
            capped = min(capped, maximum)
        speeds.append(capped)
    return (forward, backward, *speeds), "retained"


def project_points(transform, points):
    area = transform.target_crs.area_of_use
    if area is None or any(not inside_area(x, y, area) for x, y in points):
        raise ValueError("coordinates outside the metric CRS area of use")
    x, y = transform.transform(*zip(*points, strict=True), errcheck=True)
    result = np.column_stack([x, y])
    if not np.isfinite(result).all():
        raise ValueError("nonfinite projected coordinates")
    return result


@dataclass
class Network:
    matrix: csr_matrix
    node_ids: list[int]
    coordinates: np.ndarray
    audit: dict


def build_network(roads, profile, season, crs):
    transform = projection(crs)
    seen, coordinates, edges, audit = {}, {}, {}, Counter()
    for road in roads:
        payload = [road.osm_version, road.node_ids, road.coordinates_lon_lat, road.tags]
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        if road.way_id in seen:
            if seen[road.way_id] != digest:
                raise ValueError("conflicting duplicate OSM way")
            audit["duplicate_ways"] += 1
            continue
        seen[road.way_id] = digest
        policy, status = way_policy(road.tags, profile, season)
        audit[status] += 1
        if policy is None:
            continue
        xy = project_points(transform, road.coordinates_lon_lat)
        for identity, point in zip(road.node_ids, xy, strict=True):
            if identity in coordinates and not np.array_equal(coordinates[identity], point):
                raise ValueError("conflicting coordinates for OSM node")
            coordinates[identity] = point
        forward, backward, speed_f, speed_b = policy
        for i, (a, b) in enumerate(zip(road.node_ids[:-1], road.node_ids[1:], strict=True)):
            length = float(np.linalg.norm(xy[i + 1] - xy[i]))
            if a == b or length == 0:
                audit["zero_length_segments"] += 1
                continue
            for enabled, start, end, speed in ((forward, a, b, speed_f), (backward, b, a, speed_b)):
                if enabled:
                    minutes = length * 60 / (1000 * speed)
                    # Parallel edges represent alternatives; CSR must not sum their times.
                    edges[start, end] = min(edges.get((start, end), float("inf")), minutes)
    ids = sorted({n for pair in edges for n in pair})
    indices = {n: i for i, n in enumerate(ids)}
    pairs = sorted(edges)
    matrix = csr_matrix(
        (
            [edges[p] for p in pairs],
            ([indices[p[0]] for p in pairs], [indices[p[1]] for p in pairs]),
        ),
        shape=(len(ids), len(ids)),
    )
    audit.update({"nodes": len(ids), "directed_edges": len(edges)})
    return Network(matrix, ids, np.array([coordinates[n] for n in ids]), dict(audit))


def accessibility(network, origins, sites, profile, crs):
    transform = projection(crs)
    endpoints = [*origins, *sites]
    snaps = {}
    if network.node_ids:
        tree = cKDTree(network.coordinates)
        points = project_points(
            transform, [(e.location.longitude, e.location.latitude) for e in endpoints]
        )
        for endpoint, point in zip(endpoints, points, strict=True):
            key = endpoint.origin_id if hasattr(endpoint, "origin_id") else endpoint.node_id
            distance, _ = tree.query(point)
            # Stable OSM identity resolves equal-distance snaps, independent of input order.
            candidates = tree.query_ball_point(point, float(distance) + 1e-8)
            selected = min(
                candidates,
                key=lambda i: (
                    float(np.linalg.norm(network.coordinates[i] - point)),
                    network.node_ids[i],
                ),
            )
            snaps[key] = {
                "index": selected if distance <= profile.max_snap_metres else None,
                "metres": float(distance),
                "osm_node_id": network.node_ids[selected],
                "precision": endpoint.precision,
            }
    else:
        for endpoint in endpoints:
            key = endpoint.origin_id if hasattr(endpoint, "origin_id") else endpoint.node_id
            snaps[key] = {
                "index": None,
                "metres": None,
                "osm_node_id": None,
                "precision": endpoint.precision,
            }
    rows = []
    # Reverse graph search from each destination gives directed origin -> destination times.
    for site in sorted(sites, key=lambda s: s.node_id):
        end = snaps[site.node_id]
        times = (
            None
            if end["index"] is None
            else dijkstra(
                network.matrix.T.tocsr(),
                directed=True,
                indices=end["index"],
                limit=profile.max_travel_minutes,
            )
        )
        for origin in sorted(origins, key=lambda o: o.origin_id):
            start = snaps[origin.origin_id]
            minutes, status = None, "snap_failure"
            if times is not None and start["index"] is not None:
                value = float(times[start["index"]])
                value += (
                    (start["metres"] + end["metres"]) * 60 / (1000 * profile.connector_speed_kph)
                )
                status = "unreachable_or_over_budget"
                if np.isfinite(value) and value <= profile.max_travel_minutes:
                    minutes, status = value, "reachable"
            rows.append(
                {
                    "origin_id": origin.origin_id,
                    "node_id": site.node_id,
                    "minutes": minutes,
                    "status": status,
                }
            )
    return rows, snaps
