"""OSM topology for an explicitly limited undirected road-distance comparison."""

import hashlib
import json
from array import array

import numpy as np
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from shapely import STRtree
from shapely.geometry import LineString, Point, shape


def build_network(road_paths, units, protocol, progress=print, *, counts_only=False):
    if not counts_only:
        protocol.require_approval()
    project = Transformer.from_crs(4326, protocol.metric_crs, always_xy=True, allow_ballpark=False)
    coordinates, identifiers = {}, {}
    starts, ends, lengths = array("q"), array("q"), array("d")
    polygons = [shape(u.geometry) for u in units]
    tree = STRtree(polygons)
    road_lengths = np.zeros(len(units))
    retained, rejected, duplicates, seen = 0, 0, 0, {}
    for path in road_paths:
        progress(f"Reading road topology: {path.name}", flush=True)
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                way_id = row["way_id"]
                # Duplicates across provincial extracts are checked before graph accumulation.
                fingerprint = hashlib.sha256(
                    json.dumps(
                        [
                            row["osm_version"],
                            row["node_ids"],
                            row["coordinates_lon_lat"],
                            row["tags"],
                        ],
                        separators=(",", ":"),
                        sort_keys=True,
                    ).encode()
                ).digest()
                if way_id in seen:
                    if seen[way_id] != fingerprint:
                        raise ValueError("conflicting duplicate OSM way")
                    duplicates += 1
                    continue
                seen[way_id] = fingerprint
                tags = row["tags"]
                if (
                    tags["highway"] not in protocol.road_highways
                    or tags.get("access") in protocol.excluded_access_values
                ):
                    rejected += 1
                    continue
                if row["crs"] != "EPSG:4326" or len(row["node_ids"]) != len(
                    row["coordinates_lon_lat"]
                ):
                    raise ValueError("road coordinates/CRS mismatch")
                points = row["coordinates_lon_lat"]
                x, y = project.transform(*zip(*points, strict=True))
                indices = []
                for osm_id, lonlat, xx, yy in zip(row["node_ids"], points, x, y, strict=True):
                    coordinate = tuple(lonlat)
                    if osm_id in coordinates and coordinates[osm_id][0] != coordinate:
                        raise ValueError("OSM node has conflicting coordinates")
                    if osm_id not in identifiers:
                        identifiers[osm_id] = len(identifiers)
                        coordinates[osm_id] = (coordinate, (xx, yy))
                    indices.append(identifiers[osm_id])
                for a, b, x1, y1, x2, y2 in zip(
                    indices[:-1], indices[1:], x[:-1], y[:-1], x[1:], y[1:], strict=True
                ):
                    if a != b:
                        starts.append(a)
                        ends.append(b)
                        lengths.append(float(np.hypot(x2 - x1, y2 - y1)))
                if not counts_only:
                    geometry = LineString(zip(x, y, strict=True))
                    for i in tree.query(geometry, predicate="intersects"):
                        road_lengths[int(i)] += geometry.intersection(polygons[int(i)]).length
                retained += 1
    if not identifiers:
        raise ValueError("no retained road topology")
    left, right, weight = np.asarray(starts), np.asarray(ends), np.asarray(lengths)
    a, b = np.concatenate([left, right]), np.concatenate([right, left])
    w = np.concatenate([weight, weight])
    order = np.lexsort((b, a))
    a, b, w = a[order], b[order], w[order]
    first = np.r_[True, (a[1:] != a[:-1]) | (b[1:] != b[:-1])]
    indices = np.flatnonzero(first)
    # CSR sums duplicate edges by default, which would make a repeated street longer.
    graph = csr_matrix(
        (np.minimum.reduceat(w, indices), (a[indices], b[indices])),
        shape=(len(identifiers), len(identifiers)),
    )
    xy = np.asarray([coordinates[key][1] for key in identifiers])
    junction_counts = np.zeros(len(units))
    for i in [] if counts_only else np.flatnonzero(np.diff(graph.indptr) >= 3):
        point = Point(xy[i])
        for j in tree.query(point, predicate="intersects"):
            junction_counts[int(j)] += 1
    return (
        graph,
        xy,
        road_lengths,
        junction_counts,
        {
            "retained_ways": retained,
            "excluded_ways": rejected,
            "identical_duplicate_ways": duplicates,
            "graph_nodes": len(identifiers),
            "directed_edge_entries": graph.nnz,
            "method": protocol.road_method,
            "covariates_computed": not counts_only,
            "crs": protocol.metric_crs,
            "licence": "ODbL-1.0",
            "attribution": "OpenStreetMap contributors",
            "limitations": "Undirected connectivity, no travel speeds, "
            "one-way or turn-restriction claims",
        },
    )


def catchment_masks(graph, xy, points, protocol):
    snaps, vertices = cKDTree(xy).query(np.asarray(points))
    valid = snaps <= protocol.maximum_snap_distance_m
    masks = np.zeros((len(points), len(points)), dtype=bool)
    for i, vertex in enumerate(vertices):
        if not valid[i]:
            continue
        distances = dijkstra(
            graph, directed=False, indices=int(vertex), limit=protocol.catchment_distance_m
        )
        masks[i] = valid & (distances[vertices] + snaps[i] + snaps <= protocol.catchment_distance_m)
        masks[i, i] = True
    return masks, snaps, valid
