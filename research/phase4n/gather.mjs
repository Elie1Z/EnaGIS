// Phase 4N data gathering (Njombe Region, Tanzania), following docs/spec/phase4n-protocol.md.
// Usage (repository root): node research/phase4n/gather.mjs
// Boundary, council polygons and mills come from the scouting cache (no new facility retrieval). Downloads Overture
// buildings and roads (release 2026-09-23.1, zoom 14) and OpenStreetMap settlements and power (Overpass), metered,
// with a hard cap (approved by Elie: 200 MB). Writes the analysis tables to outputs/phase4n/ (gitignored) and a manifest
// with SHA-256 per file. Per-tile results are cached in outputs/phase4n/cache/, so a rerun downloads nothing.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
import * as S from "../../scripts/scout-sites.mjs";
import {shape} from "./geometry.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const OUT = path.join(ROOT, "outputs/phase4n"), CACHE = path.join(OUT, "cache");
const CAP = 200e6, Z = 14, RELEASE = "2026-09-23.1";
const BASE = `https://overturemaps-extras-us-west-2.s3.us-west-2.amazonaws.com/tiles/${RELEASE}/`;
const UA = "EnaGIS-research/1.0 (open research, OSEAS 2026 PUE-agriculture challenge)";
fs.mkdirSync(CACHE, {recursive: true});

// The scouting module replaces fetch with an offline-only wrapper; keep the real one for the metered downloads below.
const net = globalThis.fetch;
// Boundary, councils and mills exactly as the scouting audit counted them (cache only).
const {unit: U} = await S.offlineUnit("Njombe Region, Tanzania");
if (U.error) throw new Error("Njombe not in the scouting cache: " + U.error);

// From here on the network is used, metered (the scouting module installed a fetch wrapper in offline mode; replace it).
let bytes = 0, requests = 0;
globalThis.fetch = async (input, init) => {
  if (bytes > CAP) throw new Error("traffic cap reached");
  const headers = new Headers((init && init.headers) || undefined); if (!headers.has("User-Agent")) headers.set("User-Agent", UA);
  const r = await net(input, {...(init || {}), headers});
  const len = +(r.headers.get("content-length") || 0);
  if (len > 50e6) { try { await r.body?.cancel(); } catch (e) { /* ignore */ } throw new Error("refused large response"); }
  const b = await r.arrayBuffer(); bytes += b.byteLength; requests++;
  return new Response(b, {status: r.status, statusText: r.statusText, headers: r.headers});
};

const poly = U.geometry, bbox = U.bbox;
const inside = (lon, lat) => S.inPolygon(poly, lon, lat);
// Tiles that can hold an in-boundary building: a corner or the centre inside the region, or a boundary vertex inside the tile.
const verts = (poly.type === "Polygon" ? [poly.coordinates] : poly.coordinates).flatMap(p => p[0]);
const tiles = [];
for (let x = Math.floor(S.lon2x(bbox[0], Z)); x <= Math.floor(S.lon2x(bbox[2], Z)); x++)
  for (let y = Math.floor(S.lat2y(bbox[3], Z)); y <= Math.floor(S.lat2y(bbox[1], Z)); y++) {
    const w = S.x2lon(x, Z), e = S.x2lon(x + 1, Z), n = S.y2lat(y, Z), s = S.y2lat(y + 1, Z);
    const pts = [[w, n], [e, n], [w, s], [e, s], [(w + e) / 2, (n + s) / 2]];
    if (pts.some(([lo, la]) => inside(lo, la)) || verts.some(([lo, la]) => lo >= w && lo <= e && la >= s && la <= n)) tiles.push([Z, x, y]);
  }
console.log(`${tiles.length} zoom-${Z} tiles touch Njombe`);

const buildingsArchive = new globalThis.EnaTiles.PMTiles(BASE + "buildings.pmtiles");
async function buildingTile(z, x, y) {
  const f = path.join(CACHE, `b-${z}-${x}-${y}.json`);
  if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, "utf8"));
  let r;
  for (let a = 0; a < 3 && !r; a++) { try { r = await buildingsArchive.getZxy(z, x, y) || {data: null}; } catch (e) { if (/cap/.test(e.message) || a === 2) throw e; await new Promise(q => setTimeout(q, 2000 * (a + 1))); } }
  const out = [];
  if (r.data) {
    const vt = new globalThis.EnaTiles.VectorTile(new globalThis.EnaTiles.Pbf(new Uint8Array(r.data))), L = vt.layers.building;
    if (L) {
      const latC = S.y2lat(y + 0.5, z), unitM = 40075016.686 * Math.cos(latC * Math.PI / 180) / 2 ** z / L.extent;
      for (let i = 0; i < L.length; i++) {
        const ft = L.feature(i), p = ft.properties;
        if (p.is_underground === true || p.is_underground === "true") continue;
        const ring = ft.loadGeometry()[0]; if (!ring || ring.length < 3) continue;
        const n = ring.length > 1 ? ring.length - 1 : 1; let sx = 0, sy = 0;
        for (let k = 0; k < n; k++) { sx += ring[k].x; sy += ring[k].y; }
        const cx = sx / n, cy = sy / n;
        if (cx < 0 || cy < 0 || cx >= L.extent || cy >= L.extent) continue; // same one-tile rule as the app
        const lon = S.x2lon(x + cx / L.extent, z), lat = S.y2lat(y + cy / L.extent, z);
        const g = shape(ring.map(q => [q.x * unitM, q.y * unitM]));
        out.push([+lon.toFixed(6), +lat.toFixed(6), Math.round(g.area * 10) / 10, Math.round(g.perimeter * 10) / 10,
          +g.elongation.toFixed(4), +g.rectangularity.toFixed(4), p["@geometry_source"] || "other"]);
      }
    }
  }
  fs.writeFileSync(f, JSON.stringify(out)); return out;
}

async function pool(items, n, fn) { let i = 0; await Promise.all(Array.from({length: n}, async () => { while (i < items.length) { const k = i++; await fn(items[k], k); } })); }

// 1. Buildings
const rows = []; let done = 0;
await pool(tiles, 12, async ([z, x, y]) => {
  const t = await buildingTile(z, x, y);
  for (const b of t) if (inside(b[0], b[1])) rows.push(b);
  if (++done % 250 === 0) console.log(`  buildings ${done}/${tiles.length} tiles, ${rows.length} footprints, ${(bytes / 1e6).toFixed(1)} MB`);
});
rows.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
// 2. Roads (the app's converter), densified every 25 m
const roadsFile = path.join(CACHE, "roads.json");
let roadPts;
if (fs.existsSync(roadsFile)) roadPts = JSON.parse(fs.readFileSync(roadsFile, "utf8"));
else {
  globalThis.EnaConfig.OVERTURE.max_tiles = 100000;
  const t = await globalThis.EnaOverture.theme({bbox, polygon: poly}, "transportation", Z, (d, n) => { if (d % 500 === 0) console.log(`  roads ${d}/${n} tiles, ${(bytes / 1e6).toFixed(1)} MB`); });
  if (t.failed) throw new Error(`${t.failed} road tiles failed`);
  roadPts = [];
  for (const part of t.results) for (const w of part) {
    const major = /^(motorway|trunk|primary|secondary|tertiary)(_link)?$/.test(w.hw) ? 1 : 0;
    for (let k = 1; k < w.coords.length; k++) {
      const [x0, y0] = w.coords[k - 1], [x1, y1] = w.coords[k], kx = 111320 * Math.cos(y0 * Math.PI / 180);
      const steps = Math.max(1, Math.ceil(Math.hypot((x1 - x0) * kx, (y1 - y0) * 110570) / 25));
      for (let s = 0; s <= steps; s++) roadPts.push([+(x0 + (x1 - x0) * s / steps).toFixed(6), +(y0 + (y1 - y0) * s / steps).toFixed(6), major]);
    }
  }
  fs.writeFileSync(roadsFile, JSON.stringify(roadPts));
}
// 3. Settlements and power (Overpass, small)
async function overpass(q, name) {
  const f = path.join(CACHE, name + ".json"); if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, "utf8"));
  for (const ep of ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"]) {
    for (let a = 0; a < 3; a++) {
      try { const r = await fetch(ep, {method: "POST", body: "data=" + encodeURIComponent(q), headers: {"Content-Type": "application/x-www-form-urlencoded"}});
        if (!r.ok) throw new Error("HTTP " + r.status); const j = await r.json(); fs.writeFileSync(f, JSON.stringify(j)); return j; }
      catch (e) { await new Promise(q2 => setTimeout(q2, 15000 * (a + 1))); }
    }
  }
  throw new Error("Overpass failed: " + name);
}
const rel = U.osm_relation;
const places = (await overpass(`[out:json][timeout:300];rel(${rel});map_to_area->.d;node["place"~"^(city|town|village)$"](area.d);out;`, "places")).elements.map(e => [e.lon, e.lat]);
const powerJ = await overpass(`[out:json][timeout:300];rel(${rel});map_to_area->.d;(way["power"~"^(line|minor_line)$"](area.d);node["power"~"^(tower|pole)$"](area.d););out geom;`, "power");
const power = [];
for (const e of powerJ.elements) { if (e.type === "node") power.push([e.lon, e.lat]); else (e.geometry || []).forEach(g => power.push([g.lon, g.lat])); }
// 4. Mills (scouting classification) and councils
const mills = U.facilities.filter(f => f.type === "mill").map(f => [f.lon, f.lat, f.id]);
const councils = U.subdistrict_polygons.map(p => ({name: p.name, geojson: p.geojson}));

// Write tables (CSV, EPSG:4326 lon/lat) and a manifest.
const write = (name, header, data) => { const f = path.join(OUT, name); fs.writeFileSync(f, header + "\n" + data.map(r => r.join(",")).join("\n") + "\n"); return f; };
const files = [
  write("footprints.csv", "lon,lat,area_m2,perimeter_m,elongation,rectangularity,source", rows),
  write("roads.csv", "lon,lat,major", roadPts),
  write("places.csv", "lon,lat", places),
  write("power.csv", "lon,lat", power),
  write("mills.csv", "lon,lat,osm_id", mills)
];
fs.writeFileSync(path.join(OUT, "councils.json"), JSON.stringify(councils)); files.push(path.join(OUT, "councils.json"));
fs.writeFileSync(path.join(OUT, "boundary.json"), JSON.stringify(poly)); files.push(path.join(OUT, "boundary.json"));
const sha = f => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex");
const manifest = {schema: "enagis-phase4n-inputs-v1", gathered_at: new Date().toISOString(), overture_release: RELEASE, zoom: Z, tiles: tiles.length,
  osm_relation: rel, crs: "EPSG:4326 lon/lat (features are computed in EPSG:32736)", traffic_bytes_this_run: bytes, requests_this_run: requests,
  counts: {footprints: rows.length, road_points: roadPts.length, places: places.length, power_points: power.length, mills: mills.length, councils: councils.length},
  files: files.map(f => ({path: path.relative(ROOT, f).replace(/\\/g, "/"), sha256: sha(f), bytes: fs.statSync(f).size}))};
fs.writeFileSync(path.join(OUT, "manifest.json"), JSON.stringify(manifest, null, 1));
console.log(JSON.stringify(manifest.counts), `${(bytes / 1e6).toFixed(1)} MB, ${requests} requests`);
