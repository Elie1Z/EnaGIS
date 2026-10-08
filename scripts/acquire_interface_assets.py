"""Build-time acquisition of pinned public display assets, never scientific inputs."""

import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from shapely.geometry import mapping, shape

from enagis.data_io import file_hash, write_json

ROOT = Path(__file__).resolve().parents[1]
NE = "ca96624a56bd078437bca8184e78163e5039ad19"
FONTS = "2eb0b48d5f760f62e286216f0859a8c540dbc1bd"


def fetch(url):
    request = Request(url, headers={"User-Agent": "EnaGIS-interface-assets/1"})
    with urlopen(request, timeout=90) as response:
        return response.read()


def main():
    assets = ROOT / "web/assets"
    assets.mkdir(parents=True, exist_ok=True)
    sources = []
    features, places = [], []
    for layer in ("ne_110m_admin_0_countries", "ne_10m_populated_places_simple"):
        url = f"https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{NE}/geojson/{layer}.geojson"
        raw = fetch(url)
        source = assets / f"{layer}.source.geojson"
        source.write_bytes(raw)
        sources.append({"url": url, "sha256": file_hash(source), "path": source.name})
        data = json.loads(raw)
        for item in data["features"]:
            p = {k.lower(): v for k, v in item["properties"].items()}
            if "countries" in layer:
                geometry = mapping(shape(item["geometry"]).simplify(0.04, preserve_topology=True))
                name = p.get("name_en") or p.get("name")
                features.append(
                    {
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": {"name": name, "code": p.get("adm0_a3")},
                    }
                )
                center = shape(item["geometry"]).representative_point()
                places.append(
                    {
                        "name": name,
                        "country": name,
                        "kind": "country",
                        "lon": round(center.x, 5),
                        "lat": round(center.y, 5),
                        "aliases": [p.get("name_fr"), p.get("formal_en"), p.get("name")],
                        "bounds": list(shape(item["geometry"]).bounds),
                    }
                )
            else:
                x, y = item["geometry"]["coordinates"][:2]
                places.append(
                    {
                        "name": p.get("name"),
                        "country": p.get("adm0name"),
                        "kind": "place",
                        "lon": round(x, 5),
                        "lat": round(y, 5),
                        "aliases": [p.get("nameascii"), p.get("namealt")],
                        "capital": bool(p.get("adm0cap")),
                    }
                )
    world = {
        "crs": "EPSG:4326",
        "purpose": "navigation_only_not_analysis",
        "countries": {"type": "FeatureCollection", "features": features},
        "places": places,
        "licence": "Public domain",
        "source": "Natural Earth",
        "licence_url": "https://www.naturalearthdata.com/about/terms-of-use/",
        "revision": NE,
        "retrieved_on": "2026-10-09",
    }
    write_json(assets / "world.json", world)
    for family, filenames in {
        "fraunces": [
            ("Fraunces[SOFT,WONK,opsz,wght].ttf", "fraunces.ttf"),
            ("Fraunces-Italic[SOFT,WONK,opsz,wght].ttf", "fraunces-italic.ttf"),
            ("OFL.txt", "OFL-Fraunces.txt"),
        ],
        "inter": [("Inter[opsz,wght].ttf", "inter.ttf"), ("OFL.txt", "OFL-Inter.txt")],
    }.items():
        for filename, destination in filenames:
            url = f"https://raw.githubusercontent.com/google/fonts/{FONTS}/ofl/{family}/{quote(filename)}"
            path = assets / destination
            path.write_bytes(fetch(url))
            sources.append({"url": url, "sha256": file_hash(path), "path": destination})
    write_json(
        assets / "manifest.json",
        {
            "purpose": "display_and_typography_only",
            "retrieved_on": "2026-10-09",
            "natural_earth_revision": NE,
            "fonts_revision": FONTS,
            "sources": sources,
            "world_sha256": file_hash(assets / "world.json"),
            "countries": len(features),
            "places": len(places),
            "licences": {"Natural Earth": "Public domain", "Inter / Fraunces": "SIL OFL 1.1"},
        },
    )
    print(json.dumps({"countries": len(features), "places": len(places), "output": str(assets)}))


if __name__ == "__main__":
    main()
