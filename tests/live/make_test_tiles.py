"""Builds small Overture-shaped PMTiles archives of the SYNTHETIC test area for browser e2e tests.
Run: node tests/live/make_test_tiles.cjs && python3 tests/live/make_test_tiles.py
(needs pmtiles, mapbox-vector-tile, shapely). Not real data."""

import gzip
import json
import math
import os

import mapbox_vector_tile
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pmtiles.writer import Writer
from shapely.geometry import box, shape

HERE = os.path.join(os.path.dirname(__file__), "tiles")
L = json.load(open(os.path.join(HERE, "layers.json")))
W, S, E, N = L["bbox"]


def lon2x(lon, z):
    return (lon + 180) / 360 * 2**z


def lat2y(lat, z):
    r = math.radians(lat)
    return (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2**z


def x2lon(x, z):
    return x / 2**z * 360 - 180


def y2lat(y, z):
    return math.degrees(math.atan(math.sinh(math.pi - 2 * math.pi * y / 2**z)))


def build(name, layers, z):
    x0, x1 = int(lon2x(W, z)), int(lon2x(E, z))
    y0, y1 = int(lat2y(N, z)), int(lat2y(S, z))
    tiles = []
    geoms = {
        ln: [(shape(f["geometry"]), f["properties"]) for f in feats] for ln, feats in layers.items()
    }
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            w, e, n, s = x2lon(x, z), x2lon(x + 1, z), y2lat(y, z), y2lat(y + 1, z)
            bw, bh = (e - w) * 64 / 4096, (n - s) * 64 / 4096
            clip = box(w - bw, s - bh, e + bw, n + bh)
            out = []
            for ln, items in geoms.items():
                feats = []
                for g, p in items:
                    if not g.intersects(clip):
                        continue
                    c = g.intersection(clip)
                    if c.is_empty:
                        continue
                    feats.append(
                        {
                            "geometry": c.wkt,
                            "properties": {k: v for k, v in p.items() if v is not None},
                        }
                    )
                if feats:
                    out.append({"name": ln, "features": feats})
            if not out:
                continue
            data = mapbox_vector_tile.encode(
                out,
                default_options={
                    "quantize_bounds": (w, s, e, n),
                    "extents": 4096,
                    "y_coord_down": False,
                },
            )
            tiles.append((zxy_to_tileid(z, x, y), gzip.compress(data)))
    tiles.sort()
    with open(os.path.join(HERE, f"{name}.pmtiles"), "wb") as f:
        wr = Writer(f)
        for tid, d in tiles:
            wr.write_tile(tid, d)
        wr.finalize(
            {
                "tile_type": TileType.MVT,
                "tile_compression": Compression.GZIP,
                "min_zoom": z,
                "max_zoom": z,
                "min_lon_e7": int(W * 1e7),
                "min_lat_e7": int(S * 1e7),
                "max_lon_e7": int(E * 1e7),
                "max_lat_e7": int(N * 1e7),
                "center_zoom": z,
                "center_lon_e7": int((W + E) / 2 * 1e7),
                "center_lat_e7": int((S + N) / 2 * 1e7),
            },
            {
                "name": name,
                "description": "SYNTHETIC test tiles for EnaGIS Live",
                "vector_layers": [{"id": k, "fields": {}} for k in layers],
            },
        )
    print(
        name, len(tiles), "tiles", os.path.getsize(os.path.join(HERE, f"{name}.pmtiles")), "bytes"
    )


build("buildings", {"building": L["buildings"]}, 14)
build("transportation", {"segment": L["segments"]}, 14)
build("places", {"place": L["places"]}, 14)
build("base", {"infrastructure": L["infra"]}, 13)
