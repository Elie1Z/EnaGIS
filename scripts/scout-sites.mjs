// Second-site scouting (advanced-tools track, Step B). Run from the repository root on a machine that can reach
// Nominatim, Overpass, the Overture PMTiles bucket, OpenAerialMap, Maxar Open Data and the World Bank API:
//   node scripts/scout-sites.mjs            gather (metered, cached) and write the audit + report
//   node scripts/scout-sites.mjs --offline  rebuild the audit + report from the cache only (no network)
// Inputs: configs/second-site-candidates.json. Outputs: docs/audits/second-site-scouting.json and
// docs/second-site-scouting.md. Raw responses are cached in outputs/scouting-cache/ (not published; personal
// contact fields from imagery catalogues are dropped before caching). Facilities are classified with the app's own
// rules (live/js/engine.js classifySite), so counts mean exactly what they mean for Rwanda.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import crypto from "node:crypto";
import {fileURLToPath, pathToFileURL} from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const CACHE = path.join(ROOT, "outputs/scouting-cache");
const OUT_JSON = path.join(ROOT, "docs/audits/second-site-scouting.json");
const OUT_MD = path.join(ROOT, "docs/second-site-scouting.md");
const UA = "EnaGIS-scouting/1.0 (open research, OSEAS 2026 PUE-agriculture challenge)";
const OVERPASS = ["https://overpass-api.de/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter"];
const NOMINATIM = "https://nominatim.openstreetmap.org/search";
const OAM = "https://api.openaerialmap.org/meta";
const MAXAR = "https://maxar-opendata.s3.amazonaws.com/events/";
const WB = "https://api.worldbank.org/v2/country/";

// ------------------------------------------------------------------ pure helpers (exported for tests)
export const mulberry32 = (seed) => {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
};
export function shuffled(list, seed) {
  const r = mulberry32(seed), a = list.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}
const rings = g => !g ? [] : g.type === "Polygon" ? [g.coordinates] : g.type === "MultiPolygon" ? g.coordinates : [];
export function inPolygon(geom, lon, lat) {
  const inRing = ring => {
    let c = false;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      const [xi, yi] = ring[i], [xj, yj] = ring[j];
      if ((yi > lat) !== (yj > lat) && lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  };
  return rings(geom).some(poly => inRing(poly[0]) && !poly.slice(1).some(inRing));
}
export function polygonAreaKm2(geom) {
  let s = 0;
  rings(geom).forEach(poly => poly.forEach((ring, k) => {
    const lat0 = ring.reduce((a, p) => a + p[1], 0) / ring.length, kx = 111.32 * Math.cos(lat0 * Math.PI / 180), ky = 110.57;
    let a2 = 0;
    for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) a2 += ring[j][0] * kx * ring[i][1] * ky - ring[i][0] * kx * ring[j][1] * ky;
    s += (k === 0 ? 1 : -1) * Math.abs(a2) / 2;
  }));
  return s;
}
export const lon2x = (lon, z) => (lon + 180) / 360 * 2 ** z;
export const lat2y = (lat, z) => { const r = lat * Math.PI / 180; return (1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * 2 ** z; };
export const x2lon = (x, z) => x / 2 ** z * 360 - 180;
export const y2lat = (y, z) => { const n = Math.PI - 2 * Math.PI * y / 2 ** z; return 180 / Math.PI * Math.atan(Math.sinh(n)); };
// z-tiles whose centre lies inside the boundary (used to scale sampled building counts up to the unit).
export function tilesInside(geom, bbox, z) {
  const out = [];
  for (let x = Math.floor(lon2x(bbox[0], z)); x <= Math.floor(lon2x(bbox[2], z)); x++)
    for (let y = Math.floor(lat2y(bbox[3], z)); y <= Math.floor(lat2y(bbox[1], z)); y++)
      if (inPolygon(geom, x2lon(x + 0.5, z), y2lat(y + 0.5, z))) out.push([z, x, y]);
  return out;
}
// OpenAerialMap reports gsd in the image CRS: metres for projected images, degrees for EPSG:4326 ones.
export function gsdMetres(gsd, lat) {
  if (!(gsd > 0)) return null;
  return gsd < 0.001 ? gsd * 111320 * Math.cos(lat * Math.PI / 180) : gsd;
}
export const licenceId = s => {
  const t = String(s || "").toUpperCase().replace(/\s+/g, "");
  if (/CC-?BY-?NC/.test(t)) return "CC-BY-NC-4.0";
  if (/CC-?BY-?SA/.test(t)) return "CC-BY-SA-4.0";
  if (/CC-?BY/.test(t)) return "CC-BY-4.0";
  if (/CC0/.test(t)) return "CC0-1.0";
  return s ? String(s) : "UNKNOWN";
};
// Non-Latin "name" with a Latin name:en: the app's English/French/Kinyarwanda rules see the English name instead.
const nonLatin = s => /[^\u0000-ɏ\s\d.,'&()\-\/]/.test(s || "");
export function classifyBoth(tags, classifySite) {
  const strict = classifySite(tags);
  if (strict || !nonLatin(tags.name) || !tags["name:en"]) return {strict, fallback: strict};
  return {strict, fallback: classifySite({...tags, name: tags["name:en"]})};
}
const centerOf = el => el.center ? [el.center.lon, el.center.lat] : el.lat !== undefined ? [el.lon, el.lat] : null;
// Same duplicate rule as the app (engine.js parseSites): same type, or same name, within 80 m.
export function dedupeFacilities(elements, classifySite) {
  const out = [];
  for (const el of elements) {
    if (!el.tags) continue;
    const c = centerOf(el); if (!c) continue;
    const {strict, fallback} = classifyBoth(el.tags, classifySite);
    if (!fallback) continue;
    const name = (el.tags["name:en"] || el.tags.name || "").trim();
    const kx = 111320 * Math.cos(c[1] * Math.PI / 180);
    const dup = out.find(s => Math.hypot((s.lon - c[0]) * kx, (s.lat - c[1]) * 110570) < 80 && (s.type === fallback || (name && s.name === name)));
    if (dup) { dup.ids.push(`${el.type}/${el.id}`); continue; }
    out.push({id: `${el.type}/${el.id}`, ids: [`${el.type}/${el.id}`], type: fallback, strict_type: strict, name: name || null, lon: c[0], lat: c[1],
      source: el.tags.source || null});
  }
  return out;
}
export function roofStats(areas) {
  if (!areas.length) return {buildings: 0};
  const s = areas.slice().sort((a, b) => a - b), q = p => s[Math.min(s.length - 1, Math.floor(p * (s.length - 1)))];
  return {buildings: s.length, share_ge_200m2: s.filter(a => a >= 200).length / s.length, share_ge_600m2: s.filter(a => a >= 600).length / s.length,
    p50_m2: q(0.5), p99_m2: q(0.99), max_m2: s[s.length - 1], largest_10_m2: s.slice(-10).reverse()};
}
export function evaluateCandidate(cand, units, cfg) {
  const L = cfg.checklist, label = new Set(L.label_types);
  const positives = units.flatMap(u => (u.facilities || []).filter(f => label.has(f.type)));
  const positivesStrict = units.flatMap(u => (u.facilities || []).filter(f => label.has(f.strict_type)));
  const subs = new Set(units.flatMap(u => Object.entries(u.positives_by_subdistrict || {}).filter(([k, n]) => n > 0 && k !== "(no sub-district)").map(([k]) => `${u.query}|${k}`)));
  const covered = units.reduce((a, u) => a + (u.imagery?.positives_covered_open_licence_le_1m || 0), 0);
  const covered06 = units.reduce((a, u) => a + (u.imagery?.positives_covered_open_licence_le_0_6m || 0), 0);
  const tests = {
    energy_access_region: {pass: L.energy_access_regions.includes(cand.region), value: cand.region},
    labelled_positives: {pass: positives.length >= L.min_positive_facilities, value: positives.length, strict_rules_value: positivesStrict.length, need: L.min_positive_facilities},
    subdistrict_spread: {pass: subs.size >= L.min_subdistricts_with_positives, value: subs.size, need: L.min_subdistricts_with_positives},
    redistributable_labels: {pass: L.redistributable_label_licences.includes("ODbL-1.0"), value: "OpenStreetMap, ODbL-1.0 (share-alike)"},
    detector_imagery: {pass: covered >= L.detector_min_covered_positives, value: covered, value_le_0_6m: covered06, need: L.detector_min_covered_positives}
  };
  const missing = units.filter(u => u.error).map(u => `${u.query}: ${u.error}`);
  const c1 = ["energy_access_region", "labelled_positives", "subdistrict_spread", "redistributable_labels"].every(k => tests[k].pass) && !missing.length;
  return {id: cand.id, label: cand.label, tests, incomplete_units: missing,
    footprint_classifier_c1: c1 ? "PASS" : "FAIL", image_detector_c2: c1 && tests.detector_imagery.pass ? "PASS" : "FAIL",
    failed_tests: Object.entries(tests).filter(([, t]) => !t.pass).map(([k]) => k)};
}

// ------------------------------------------------------------------ metered, cached network
const meter = {bytes: 0, requests: 0, cap: Infinity, offline: false};
function cachePath(kind, key) { return path.join(CACHE, kind, crypto.createHash("sha1").update(key).digest("hex") + ".json"); }
function readCache(kind, key) { const p = cachePath(kind, key); return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : undefined; }
function writeCache(kind, key, v) { const p = cachePath(kind, key); fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, JSON.stringify(v)); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
function installMeter() {
  const orig = globalThis.fetch;
  globalThis.fetch = async (input, init) => {
    if (meter.offline) throw new Error("offline mode: cache miss for " + String(input).slice(0, 120));
    if (meter.bytes > meter.cap) throw new Error("traffic cap reached");
    // Keep every caller header intact (PMTiles relies on Range); only add a User-Agent.
    const headers = new Headers((init && init.headers) || undefined);
    if (!headers.has("User-Agent")) headers.set("User-Agent", UA);
    const r = await orig(input, {...(init || {}), headers});
    const len = +(r.headers.get("content-length") || 0);
    if (len > 50e6) { try { await r.body?.cancel(); } catch (e) { /* ignore */ } throw new Error(`refused ${(len / 1e6).toFixed(0)} MB response`); }
    const b = await r.arrayBuffer(); meter.bytes += b.byteLength; meter.requests++;
    return new Response(b, {status: r.status, statusText: r.statusText, headers: r.headers});
  };
}
async function getJSON(kind, url, {body, sanitize, retries = 3, pause = 1200} = {}) {
  const key = url + (body || "");
  const hit = readCache(kind, key); if (hit !== undefined) return hit;
  let err;
  for (let i = 0; i < retries; i++) {
    try {
      await sleep(pause);
      const r = await fetch(url, body ? {method: "POST", body, headers: {"Content-Type": "application/x-www-form-urlencoded"}} : {});
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      let v = await r.json(); if (sanitize) v = sanitize(v);
      if (v && v.remark && /runtime error|timed out|out of memory/i.test(v.remark)) throw new Error(v.remark);
      writeCache(kind, key, v); return v;
    } catch (e) { err = e; if (/offline mode|traffic cap/.test(e.message)) throw e; await sleep((kind === "overpass" ? 15000 : 4000) * (i + 1)); }
  }
  throw err;
}
async function overpass(q) {
  let err;
  // Either server's cached answer is valid (the cache key includes the endpoint), so offline tries both.
  for (const ep of OVERPASS) { try { return await getJSON("overpass", ep, {body: "data=" + encodeURIComponent(q), pause: 3000}); } catch (e) { err = e; if (/traffic cap/.test(e.message)) throw e; } }
  throw err;
}

const LEDGER = path.join(CACHE, "traffic-ledger.json");
function readLedger() { return fs.existsSync(LEDGER) ? JSON.parse(fs.readFileSync(LEDGER, "utf8")) : {bytes: 0, requests: 0, runs: []}; }
function addTraffic(kind) {
  const l = readLedger();
  l.runs.push({kind, at: new Date().toISOString(), bytes: meter.bytes, requests: meter.requests});
  l.bytes += meter.bytes; l.requests += meter.requests;
  fs.mkdirSync(CACHE, {recursive: true}); fs.writeFileSync(LEDGER, JSON.stringify(l, null, 1)); return l;
}

// ------------------------------------------------------------------ app modules (classification, Overture reader)
function loadApp() {
  globalThis.window = globalThis;
  for (const f of ["live/js/config.js", "live/vendor/enagis-tiles.js", "live/js/siting.js", "live/js/engine.js", "live/js/overture.js"])
    vm.runInThisContext(fs.readFileSync(path.join(ROOT, f), "utf8") + (f.includes("enagis-tiles") ? "\nwindow.EnaTiles=EnaTiles;" : ""), {filename: f});
  return {classifySite: globalThis.EnaEngine.classifySite, O: globalThis.EnaOverture};
}

// Retrieval filter: the app's site query (live/js/sources.js), without settlements, plus name:en and a few
// South-Asian facility words so candidates reach the same classifier. Classification itself is unchanged.
const FILTERS = [
  'nwr["amenity"="marketplace"]', 'nwr["shop"~"^(agrarian|farm|wholesale|dairy)$"]', 'nwr["industrial"]',
  'nwr["man_made"~"^(works|watermill|windmill|silo)$"]', 'nwr["craft"~"^(miller|agricultural_engines)$"]',
  'nwr["building"~"^(warehouse|cold_storage|silo)$"]', 'nwr["office"="cooperative"]', 'nwr["cooperative"]', 'nwr["product"]',
  'nwr["name"~"cooperative|coop|koperative|milk|amata|dairy|laiterie|collection cent|washing station|coffee|cold room|cold stor|frigo|mill|minoterie|moulin|warehouse|entrep|ububiko|isoko|market|march|chilling",i]',
  'nwr["name:en"~"cooperative|coop|milk|dairy|collection cent|washing station|coffee|cold room|cold stor|mill|warehouse|market|chilling",i]'
];
// Small queries (one or a few filters each) instead of one large union: public servers time out (504) on the latter
// for dense South-Asian districts. Results are merged by element id.
const FILTER_GROUPS = [[0, 1, 6, 7], [2], [3, 4, 5], [8], [9], [10]];

async function scoutUnit(query, cfg, app) {
  const u = {query};
  const geo = await getJSON("nominatim", `${NOMINATIM}?q=${encodeURIComponent(query)}&format=jsonv2&limit=5&polygon_geojson=1&polygon_threshold=0.003`,
    {sanitize: v => v.map(r => ({osm_type: r.osm_type, osm_id: r.osm_id, name: r.name, display_name: r.display_name, category: r.category, type: r.type,
      addresstype: r.addresstype, boundingbox: r.boundingbox, geojson: r.geojson}))});
  const hit = geo.find(r => r.osm_type === "relation" && r.type === "administrative" && /Polygon/.test(r.geojson?.type || ""));
  if (!hit) { u.error = "no administrative boundary found in Nominatim"; return u; }
  const bb = hit.boundingbox.map(Number);
  Object.assign(u, {osm_relation: hit.osm_id, name: hit.name, display_name: hit.display_name, bbox: [bb[2], bb[0], bb[3], bb[1]],
    area_km2: Math.round(polygonAreaKm2(hit.geojson)), geometry: hit.geojson});
  // Administrative levels inside the unit: pick the first level below the unit's own with at least 3 units.
  const lv = await overpass(`[out:json][timeout:180];rel(${hit.osm_id});out tags;rel(${hit.osm_id});map_to_area->.d;rel(area.d)["boundary"="administrative"]["admin_level"~"^([4-9]|10)$"];out tags;`);
  const own = +((lv.elements.find(e => e.id === hit.osm_id) || {}).tags || {}).admin_level || 5;
  const byLevel = {};
  lv.elements.filter(e => e.id !== hit.osm_id).forEach(e => { const l = +e.tags.admin_level; if (l > own) byLevel[l] = (byLevel[l] || 0) + 1; });
  const sub = Object.keys(byLevel).map(Number).sort((a, b) => a - b).find(l => byLevel[l] >= 3);
  u.admin_level = own; u.relations_by_level = byLevel; u.subdistrict_level = sub ?? null;
  // Sub-district polygons (simplified) from Nominatim, by relation id; a facility belongs to the one containing it.
  const subs = sub ? lv.elements.filter(e => +e.tags.admin_level === sub && e.id !== hit.osm_id) : [];
  const subPolys = [];
  for (let i = 0; i < subs.length; i += 40) {
    const ids = subs.slice(i, i + 40).map(e => "R" + e.id).join(",");
    const r = await getJSON("nominatim", `${NOMINATIM.replace("/search", "/lookup")}?osm_ids=${ids}&format=json&polygon_geojson=1&polygon_threshold=0.002`,
      {sanitize: v => v.map(x => ({osm_id: x.osm_id, name: x.name, lat: x.lat, lon: x.lon, geojson: x.geojson}))});
    for (const x of r) if (/Polygon/.test(x.geojson?.type || "")) {
      const tags = (subs.find(e => e.id === x.osm_id) || {}).tags || {};
      subPolys.push({name: tags["name:en"] || tags.name || x.name || `relation/${x.osm_id}`, geojson: x.geojson, inside: inPolygon(hit.geojson, +x.lon, +x.lat)});
    }
  }
  // Facility candidates, in small queries, merged by id.
  const byId = new Map();
  for (const g of FILTER_GROUPS) {
    const q = `[out:json][timeout:300];rel(${hit.osm_id});map_to_area->.d;(${g.map(i => `${FILTERS[i]}(area.d);`).join("")});out tags center;`;
    const r = await overpass(q);
    for (const e of r.elements) byId.set(`${e.type}/${e.id}`, e);
  }
  const raw = [...byId.values()];
  const pw = await overpass(`[out:json][timeout:180];rel(${hit.osm_id});map_to_area->.d;way["power"="line"](area.d);out count;`);
  const powerLines = +((pw.elements.find(e => e.type === "count") || {}).tags || {}).ways || 0;
  u.osm_elements_pulled = raw.length;
  u.unclassifiable_non_latin_without_english = raw.filter(e => e.tags && nonLatin(e.tags.name) && !e.tags["name:en"] && !app.classifySite(e.tags)).length;
  const fac = dedupeFacilities(raw, app.classifySite).filter(f => f.type !== "town" && f.type !== "village" && f.type !== "agro_shop");
  fac.forEach(f => { f.subdistrict = (subPolys.find(p => inPolygon(p.geojson, f.lon, f.lat)) || {}).name || null; });
  u.facilities = fac;
  const label = new Set(cfg.checklist.label_types), any = new Set(cfg.checklist.any_point_types);
  u.counts_by_type = fac.reduce((a, f) => { a[f.type] = (a[f.type] || 0) + 1; return a; }, {});
  u.positives = fac.filter(f => label.has(f.type)).length;
  u.positives_strict_rules = fac.filter(f => label.has(f.strict_type)).length;
  u.positive_label_sources = fac.filter(f => label.has(f.type)).reduce((a, f) => { const k = f.source || "(no source tag)"; a[k] = (a[k] || 0) + 1; return a; }, {});
  u.any_points = fac.filter(f => any.has(f.type)).length;
  u.positives_by_subdistrict = fac.filter(f => label.has(f.type)).reduce((a, f) => { const k = f.subdistrict || "(no sub-district)"; a[k] = (a[k] || 0) + 1; return a; }, {});
  u.subdistricts_total = subPolys.filter(p => p.inside).length;
  u.osm_power_line_ways = powerLines;
  u.subdistrict_polygons = subPolys;
  return u;
}

async function imagery(u, cfg, maxarEvents) {
  const label = new Set(cfg.checklist.label_types), pos = u.facilities.filter(f => label.has(f.type));
  const lat = (u.bbox[1] + u.bbox[3]) / 2, results = [];
  for (let page = 1; page <= 10; page++) {
    const r = await getJSON("oam", `${OAM}?bbox=${u.bbox.map(v => v.toFixed(4)).join(",")}&limit=500&page=${page}`,
      {sanitize: v => ({meta: v.meta, results: (v.results || []).map(x => ({_id: x._id, title: x.title, gsd: x.gsd, platform: x.platform, provider: x.provider,
        acquisition_start: x.acquisition_start, acquisition_end: x.acquisition_end, license: x.license || x.properties?.license || null, geojson: x.geojson}))})});
    results.push(...r.results);
    if (!r.meta || results.length >= r.meta.found || !r.results.length) break;
  }
  const L = cfg.checklist, train = new Set(L.training_licences);
  const imgs = results.map(x => ({id: x._id, title: x.title, platform: x.platform, provider: x.provider, date: (x.acquisition_start || "").slice(0, 10),
    gsd_m: gsdMetres(x.gsd, lat), licence: licenceId(x.license || "CC-BY 4.0"), licence_source: x.license ? "image" : "catalogue default (OpenAerialMap: CC-BY 4.0)",
    area_km2: +polygonAreaKm2(x.geojson).toFixed(3), geojson: x.geojson}));
  const covers = (maxGsd) => pos.filter(f => imgs.some(i => i.gsd_m !== null && i.gsd_m <= maxGsd && train.has(i.licence) && inPolygon(i.geojson, f.lon, f.lat))).length;
  const inter = (a, b) => a[0] <= b[2] && a[2] >= b[0] && a[1] <= b[3] && a[3] >= b[1];
  const maxar = maxarEvents.filter(ev => ev.bboxes.some(b => inter(b, u.bbox))).map(ev => ({event: ev.id, title: ev.title, interval: ev.interval, licence: ev.licence,
    positives_in_extent_bbox: pos.filter(f => ev.bboxes.some(b => f.lon >= b[0] && f.lon <= b[2] && f.lat >= b[1] && f.lat <= b[3])).length}));
  return {openaerialmap: {images: imgs.length, best_gsd_m: imgs.reduce((m, i) => i.gsd_m !== null && i.gsd_m < m ? i.gsd_m : m, Infinity),
      le_1m: imgs.filter(i => i.gsd_m !== null && i.gsd_m <= 1).length, footprint_km2_sum: +imgs.reduce((a, i) => a + i.area_km2, 0).toFixed(2),
      dates: imgs.length ? [imgs.map(i => i.date).sort()[0], imgs.map(i => i.date).sort().slice(-1)[0]] : null,
      licences: [...new Set(imgs.map(i => i.licence))], list: imgs.map(({geojson, ...rest}) => rest)},
    maxar_open_data: maxar,
    positives_covered_open_licence_le_1m: covers(L.detector_max_gsd_m),
    positives_covered_open_licence_le_0_6m: covers(L.detector_small_asset_max_gsd_m)};
}

async function maxarCatalog() {
  const cat = await getJSON("maxar", MAXAR + "catalog.json");
  const out = [];
  for (const l of cat.links.filter(l => l.rel === "child")) {
    const href = MAXAR + l.href.replace(/^\.\//, "");
    const c = await getJSON("maxar", href, {pause: 200, sanitize: v => ({id: v.id, title: v.title, license: v.license, extent: v.extent})});
    const all = (c.extent?.spatial?.bbox || []).filter(b => b.length === 4);
    // STAC: with several boxes the first is the union of the rest; intersect only the per-acquisition boxes.
    const bb = all.length > 1 ? all.slice(1) : all;
    out.push({id: c.id, title: c.title, interval: c.extent?.temporal?.interval?.[0] || null, licence: licenceId(c.license || cat.license), bboxes: bb});
  }
  return {licence: cat.license, events: out};
}

async function tileBuildings(app, z, x, y) {
  const key = `${z}/${x}/${y}`, hit = readCache("tiles", key); if (hit !== undefined) return hit;
  const e = 1e-7, area = {bbox: [x2lon(x, z) + e, y2lat(y + 1, z) + e, x2lon(x + 1, z) - e, y2lat(y, z) - e], polygon: null};
  const t = await app.O.theme(area, "buildings", z);
  if (t.failed) throw new Error("tile failed");
  const r = t.results[0] || {flat: [], area: []};
  const v = {flat: r.flat.map(c => +c.toFixed(5)), area: r.area};
  writeCache("tiles", key, v); return v;
}

async function buildings(u, cfg, app) {
  const S = cfg.sampling, z = S.zoom, label = new Set(cfg.checklist.label_types);
  const inside = tilesInside(u.geometry, u.bbox, z);
  const seed = S.seed + [...u.query].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 0);
  const sample = shuffled(inside, seed).slice(0, S.random_tiles_per_unit);
  const counts = [], areas = [], skipped = [];
  for (const [tz, tx, ty] of sample) {
    try { const t = await tileBuildings(app, tz, tx, ty); counts.push(t.area.length); areas.push(...t.area); }
    catch (e) { skipped.push(`${tz}/${tx}/${ty}: ${e.message}`); }
  }
  const mean = counts.length ? counts.reduce((a, b) => a + b, 0) / counts.length : null;
  // Roof at documented processing/storage points: largest footprint whose centre is within the radius.
  const facs = shuffled(u.facilities.filter(f => label.has(f.type)), seed + 1).slice(0, S.facility_tiles_per_unit);
  const atFac = [];
  for (const f of facs) {
    const x = Math.floor(lon2x(f.lon, z)), y = Math.floor(lat2y(f.lat, z));
    try {
      const t = await tileBuildings(app, z, x, y), kx = 111320 * Math.cos(f.lat * Math.PI / 180);
      let best = 0;
      for (let i = 0; i < t.area.length; i++) if (Math.hypot((t.flat[2 * i] - f.lon) * kx, (t.flat[2 * i + 1] - f.lat) * 110570) <= S.facility_roof_radius_m) best = Math.max(best, t.area[i]);
      atFac.push({id: f.id, type: f.type, name: f.name, largest_roof_m2: best});
    } catch (e) { skipped.push(`facility ${f.id}: ${e.message}`); }
  }
  return {overture_release: S.overture_release, zoom: z, tiles_inside: inside.length, tiles_sampled: counts.length,
    buildings_estimate: mean === null ? null : Math.round(mean * inside.length), buildings_per_tile_mean: mean,
    buildings_per_tile_range: counts.length ? [Math.min(...counts), Math.max(...counts)] : null,
    evidence: "ESTIMATED (mean of randomly sampled tiles x tiles inside the boundary)",
    roofs_in_sampled_tiles: roofStats(areas), roofs_at_documented_facilities: atFac,
    roofs_at_facilities_ge_600m2: atFac.filter(f => f.largest_roof_m2 >= 600).length, skipped};
}

// ------------------------------------------------------------------ report
const pct = v => (100 * v).toFixed(1) + "%";
function markdown(a) {
  const L = [];
  const C = a.config.checklist;
  L.push("# Second-site scouting: can the suggested tools run honestly somewhere else?", "",
    `Run ${a.run.finished_at.slice(0, 10)} with \`node scripts/scout-sites.mjs\` (config \`configs/second-site-candidates.json\`, SHA-256 \`${a.config_sha256.slice(0, 12)}…\`). ` +
    `Audit file: [audits/second-site-scouting.json](audits/second-site-scouting.json). Traffic: ${(a.run.bytes / 1e6).toFixed(1)} MB in ${a.run.requests} requests (cap ${a.config.sampling.traffic_cap_mb} MB).`, "",
    "## Decision", "");
  const c1 = a.candidates.filter(c => c.footprint_classifier_c1 === "PASS"), c2 = a.candidates.filter(c => c.image_detector_c2 === "PASS");
  L.push(c2.length ? `**Image detector (C2): ${c2.map(c => c.label).join("; ")} pass${c2.length === 1 ? "es" : ""} the checklist.**` :
    "**Image detector (YOLO-type, C2): no candidate passes.** None has open imagery at 1 m or finer, under a licence that allows training and publishing, covering the documented facilities.");
  L.push("", c1.length ? `**Footprint classifier (C1): ${c1.map(c => c.label).join("; ")} pass${c1.length === 1 ? "es" : ""}** (≥ ${C.min_positive_facilities} documented processing/storage points in ≥ ${C.min_subdistricts_with_positives} sub-districts, redistributable labels).` :
    `**Footprint classifier (C1): no candidate passes.** None has ≥ ${C.min_positive_facilities} documented processing/storage points from a redistributable source spread over ≥ ${C.min_subdistricts_with_positives} sub-districts.`, "");
  L.push("## Checklist by candidate", "",
    "| Candidate | Region | Documented processing/storage points (app rules + name:en) | strict app rules | Sub-districts with a point | Open imagery ≤ 1 m covering points | C1 footprint | C2 detector | Failed tests |",
    "|---|---|---:|---:|---:|---:|---|---|---|");
  for (const c of a.candidates) {
    const t = c.tests;
    L.push(`| ${c.label} | ${t.energy_access_region.value} | ${t.labelled_positives.value} | ${t.labelled_positives.strict_rules_value} | ${t.subdistrict_spread.value} | ${t.detector_imagery.value} | ${c.footprint_classifier_c1} | ${c.image_detector_c2} | ${c.failed_tests.join(", ") || "none"}${c.incomplete_units.length ? " (incomplete: " + c.incomplete_units.join("; ") + ")" : ""} |`);
  }
  L.push("");
  const why = {labelled_positives: t => `${t.value} documented processing/storage points (needs ${t.need})`, subdistrict_spread: t => `points in ${t.value} sub-districts (needs ${t.need})`,
    detector_imagery: t => `${t.value} points under open imagery at ≤ 1 m (needs ${t.need})`, energy_access_region: t => `region ${t.value}`, redistributable_labels: () => "labels not redistributable"};
  for (const c of a.candidates) {
    const fails = c.failed_tests.map(k => why[k](c.tests[k]));
    const src = a.units.filter(u => a.config.candidates.find(x => x.id === c.id).units.includes(u.query)).flatMap(u => Object.entries(u.positive_label_sources || {}));
    const total = src.reduce((x, [, n]) => x + n, 0), top = src.sort((x, y) => y[1] - x[1])[0];
    const head = c.footprint_classifier_c1 === "PASS" ? (fails.length ? "passes the footprint-classifier tests; the image detector fails on " + fails.join("; ") : "passes every test")
      : "fails on " + fails.join("; ");
    L.push(`- **${c.label}:** ${head}.` +
      (c.footprint_classifier_c1 === "PASS" && top ? ` Label provenance: ${top[1]} of ${total} points carry the source tag "${top[0]}".` : ""));
  }
  L.push("", `Pass rules (all required): an energy-access region (Africa or South Asia); ≥ ${C.min_positive_facilities} documented processing or storage points (${C.label_types.join(", ")}); spread over ≥ ${C.min_subdistricts_with_positives} sub-districts; labels redistributable (OpenStreetMap, ODbL). The detector additionally needs open imagery at ≤ ${C.detector_max_gsd_m} m (≤ ${C.detector_small_asset_max_gsd_m} m for small assets), under a licence that allows training and publishing (${C.training_licences.join(", ")}), covering ≥ ${C.detector_min_covered_positives} of those points.`, "");
  L.push("## By district", "", "| District (OSM relation) | Area km² | Points (any aggregation) | Processing/storage | By type | Sub-district level · units | Overture buildings (ESTIMATED) | Largest roofs in sample | Roof at sampled facilities ≥ 600 m² | OAM images (≤ 1 m) | Maxar Open Data events | OSM power-line ways |",
    "|---|---:|---:|---:|---|---|---:|---|---|---|---|---:|");
  for (const u of a.units) {
    if (u.error) { L.push(`| ${u.query} | | | | ${u.error} | | | | | | | |`); continue; }
    const b = u.buildings || {}, r = b.roofs_in_sampled_tiles || {}, im = u.imagery || {}, oam = im.openaerialmap || {};
    L.push(`| ${/[^ -ɏ]/.test(u.name) ? u.query.split(",")[0] : u.name} (${u.osm_relation}) | ${u.area_km2.toLocaleString("en")} | ${u.any_points} | ${u.positives} | ${Object.entries(u.counts_by_type).sort((x, y) => y[1] - x[1]).map(([k, v]) => `${k} ${v}`).join(", ") || "none"} | ${u.subdistrict_level ?? "none"} · ${u.subdistricts_total} | ` +
      `${b.buildings_estimate ? b.buildings_estimate.toLocaleString("en") + ` (${b.tiles_sampled}/${b.tiles_inside} tiles)` : "not sampled"} | ${r.buildings ? `max ${r.max_m2.toLocaleString("en")} m², p99 ${r.p99_m2} m², ${pct(r.share_ge_600m2)} ≥ 600 m²` : "–"} | ` +
      `${b.roofs_at_documented_facilities ? `${b.roofs_at_facilities_ge_600m2} of ${b.roofs_at_documented_facilities.length}` : "–"} | ${oam.images ?? 0} (${oam.le_1m ?? 0}) | ${(im.maxar_open_data || []).map(m => m.title).join("; ") || "none"} | ${u.osm_power_line_ways ?? "?"} |`);
  }
  L.push("", "## Imagery checked", "",
    `- **OpenAerialMap** (catalogue default licence CC-BY 4.0; per-image licence recorded where given): searched by each district's bounding box; images, resolution and dates are listed per district in the audit file. Coverage counts a documented point only if it lies inside an image footprint at the required resolution.`,
    `- **Maxar Open Data** (${a.maxar.events.length} events in the STAC catalogue; catalogue licence ${a.maxar.licence}): event extents intersected with each district. CC-BY-NC is non-commercial only, so it fails the training/publishing licence test for this project even where an event overlaps.`,
    ...a.other_imagery.map(o => `- **${o.name}**: ${o.finding}`), "");
  L.push("## Energy-access context (national, DOCUMENTED)", "", "| Country | Access to electricity, % of population | Rural, % of rural population | Year |", "|---|---:|---:|---|");
  for (const [k, v] of Object.entries(a.energy_access)) L.push(`| ${k} | ${v.total ?? "?"} | ${v.rural ?? "?"} | ${v.year ?? "?"} |`);
  L.push("", "District-level electrification was not found in an easily reusable public source; OSM power-line counts per district are listed above as mapped-grid context only (mapping completeness varies).", "");
  L.push("## Method and limits", "",
    "- Facilities: OpenStreetMap via Overpass, retrieved on the run date, classified with the app's own `classifySite` rules (same look-alike exclusions as Rwanda). " +
    "Where an element's `name` is in a non-Latin script and an English `name:en` exists, the rules read the English name (\"app rules + name:en\"); the strict count without that fallback is shown too. " +
    "Names only in Devanagari, Bengali or Amharic without an English tag cannot be classified by these rules; their number is in the audit file per district (`unclassifiable_non_latin_without_english`).",
    "- Duplicates (a node and a building for the same place) are merged with the app's rule: same type or same name within 80 m.",
    "- Sub-districts: the first administrative level below the district with at least 3 units in OpenStreetMap; a facility is counted in the sub-district whose area contains it.",
    "- Buildings: Overture Maps buildings (release " + a.config.sampling.overture_release + ") read from a seeded random sample of zoom-" + a.config.sampling.zoom + " tiles inside the boundary, scaled by the number of such tiles (ESTIMATED). Roof areas use the app's footprint-area code.",
    "- OpenStreetMap documents only some facilities; absence of a mapped facility is not absence of a facility. Counts are a lower bound of what exists and an upper bound of what is usable as labels.",
    "- No field verification (n = 0). This is a data-availability audit, not a model result.", "");
  return L.join("\n") + "\n";
}

// One unit rebuilt from the cache only (no network): boundary, sub-district polygons and classified facilities.
// Used by research/phase4n to work on exactly what the scouting audit counted.
export async function offlineUnit(query) {
  const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "configs/second-site-candidates.json"), "utf8"));
  meter.offline = true; installMeter();
  const app = loadApp();
  return {unit: await scoutUnit(query, cfg, app), cfg, app};
}

// ------------------------------------------------------------------ main
async function main() {
  const offline = process.argv.includes("--offline");
  const cfgText = fs.readFileSync(path.join(ROOT, "configs/second-site-candidates.json"), "utf8"), cfg = JSON.parse(cfgText);
  meter.cap = cfg.sampling.traffic_cap_mb * 1e6 - readLedger().bytes; meter.offline = offline;
  installMeter();
  const app = loadApp(), started = new Date().toISOString();
  // --warm: fill the facility cache from the end of the list, preferring the second Overpass server, then exit.
  // Run beside a normal run to halve wall time; the normal run reads what this one cached.
  if (process.argv.includes("--warm")) {
    OVERPASS.reverse();
    for (const q of cfg.candidates.flatMap(c => c.units).reverse()) {
      try { const u = await scoutUnit(q, cfg, app); console.log("warmed", q, u.error || u.positives); } catch (e) { console.log("warm failed", q, e.message); }
    }
    addTraffic("warm");
    return;
  }
  const units = [];
  for (const cand of cfg.candidates) for (const q of cand.units) {
    console.log("unit:", q);
    try { units.push(await scoutUnit(q, cfg, app)); } catch (e) { units.push({query: q, error: String(e.message || e)}); }
    const u = units[units.length - 1]; console.log(u.error ? "  error " + u.error : `  ${u.positives} processing/storage, ${u.any_points} any; sub-level ${u.subdistrict_level}; ${(meter.bytes / 1e6).toFixed(1)} MB`);
  }
  let maxar = {licence: null, events: []};
  try { maxar = await maxarCatalog(); } catch (e) { maxar.error = String(e.message || e); }
  for (const u of units.filter(u => !u.error)) {
    try { u.imagery = await imagery(u, cfg, maxar.events); } catch (e) { u.imagery = {error: String(e.message || e)}; }
  }
  const energy = {};
  for (const iso of [...new Set(cfg.candidates.map(c => c.country))]) {
    try {
      const get = async ind => (await getJSON("worldbank", `${WB}${iso}/indicator/${ind}?format=json&mrv=1`))[1]?.[0];
      const t = await get("EG.ELC.ACCS.ZS"), r = await get("EG.ELC.ACCS.RU.ZS");
      energy[iso] = {total: t?.value ?? null, rural: r?.value ?? null, year: t?.date || r?.date || null, source: "World Bank WDI EG.ELC.ACCS.ZS / EG.ELC.ACCS.RU.ZS"};
    } catch (e) { energy[iso] = {error: String(e.message || e)}; }
  }
  // Buildings last, round-robin, so the traffic cap (if reached) thins every district instead of starving the last ones.
  for (const u of units.filter(u => !u.error)) {
    try { u.buildings = await buildings(u, cfg, app); } catch (e) { u.buildings = {error: String(e.message || e)}; }
    console.log(`buildings ${u.name}: ${u.buildings.buildings_estimate ?? u.buildings.error}; ${(meter.bytes / 1e6).toFixed(1)} MB`);
  }
  const other = JSON.parse(fs.readFileSync(path.join(ROOT, "configs/second-site-imagery-notes.json"), "utf8")).sources;
  const ledger = offline ? readLedger() : addTraffic("run");
  const out = {schema: "enagis-second-site-scouting-v1",
    run: {started_at: started, finished_at: new Date().toISOString(), offline, bytes: ledger.bytes, requests: ledger.requests,
      note: "Traffic is cumulative over every live scouting process (restarts and the cache warmer), excluding about 3 MB of manual API probes made while writing the script.",
      processes: ledger.runs.length},
    config: cfg, config_sha256: crypto.createHash("sha256").update(cfgText).digest("hex"),
    candidates: cfg.candidates.map(c => evaluateCandidate(c, units.filter(u => c.units.includes(u.query)), cfg)),
    units: units.map(({geometry, facilities, subdistrict_polygons, ...u}) => ({...u, facilities_sample: (facilities || []).filter(f => cfg.checklist.label_types.includes(f.type)).slice(0, 25).map(f => ({id: f.id, type: f.type, lon: +f.lon.toFixed(5), lat: +f.lat.toFixed(5), subdistrict: f.subdistrict}))})),
    maxar: {licence: maxar.licence, events: maxar.events.map(e => ({id: e.id, title: e.title, interval: e.interval})), error: maxar.error},
    other_imagery: other, energy_access: energy};
  fs.writeFileSync(OUT_JSON, JSON.stringify(out, null, 1) + "\n");
  fs.writeFileSync(OUT_MD, markdown(out));
  console.log(`wrote ${path.relative(ROOT, OUT_JSON)} and ${path.relative(ROOT, OUT_MD)}; ${(meter.bytes / 1e6).toFixed(1)} MB, ${meter.requests} requests`);
  out.candidates.forEach(c => console.log(`${c.id}: C1 ${c.footprint_classifier_c1}, C2 ${c.image_detector_c2}; failed ${c.failed_tests.join(", ") || "none"}`));
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) await main();
