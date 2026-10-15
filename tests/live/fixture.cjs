/* Deterministic synthetic area for testing the live engine. Not real data. */
"use strict";
function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

function makeFixture(opts = {}) {
  const r = rng(opts.seed || 42);
  const bbox = [29.50, -1.60, 29.70, -1.40]; // ~22 x 22 km
  let nid = 1, wid = 1;
  const nodeIds = new Map();
  const roads = [];
  const nodeAt = (lon, lat) => { const k = lon.toFixed(5) + "," + lat.toFixed(5); if (!nodeIds.has(k)) nodeIds.set(k, nid++); return nodeIds.get(k); };
  const way = (pts, tags) => {
    roads.push({type: "way", id: wid++, nodes: pts.map(([lo, la]) => nodeAt(lo, la)), geometry: pts.map(([lon, lat]) => ({lon, lat})), tags});
  };
  // A paved primary road west-east, secondary north-south, and a grid of unpaved tracks.
  const line = (x0, y0, x1, y1, n) => Array.from({length: n + 1}, (_, i) => [+(x0 + (x1 - x0) * i / n).toFixed(5), +(y0 + (y1 - y0) * i / n).toFixed(5)]);
  way(line(29.50, -1.50, 29.70, -1.50, 40), {highway: "primary", surface: "asphalt"});
  way(line(29.60, -1.60, 29.60, -1.40, 40), {highway: "secondary"});
  for (let k = 0; k <= 8; k++) {
    const y = -1.60 + k * 0.025, x = 29.50 + k * 0.025;
    if (Math.abs(y + 1.50) > 1e-6) way(line(29.50, y, 29.70, y, 40), {highway: k % 2 ? "track" : "unclassified", surface: k % 2 ? "dirt" : undefined});
    if (Math.abs(x - 29.60) > 1e-6) way(line(x, -1.60, x, -1.40, 40), {highway: "path"});
  }
  // Buildings: rural scatter, denser in the north-west, plus a dense town at the crossroads.
  const buildings = [];
  let bid = 1;
  for (let i = 0; i < (opts.buildings || 6000); i++) {
    const nw = r() < 0.5;
    const lon = nw ? 29.50 + r() * 0.10 : 29.50 + r() * 0.20, lat = nw ? -1.50 + r() * 0.10 : -1.60 + r() * 0.20;
    buildings.push({type: "way", id: 900000 + bid++, center: {lon: +lon.toFixed(6), lat: +lat.toFixed(6)}});
  }
  for (let i = 0; i < 1500; i++) {
    buildings.push({type: "way", id: 900000 + bid++, center: {lon: +(29.598 + r() * 0.004).toFixed(6), lat: +(-1.502 + r() * 0.004).toFixed(6)}});
  }
  const sites = [
    {type: "node", id: 1, lat: -1.50, lon: 29.60, tags: {amenity: "marketplace", name: "Isoko rya Centre"}},
    {type: "way", id: 2, center: {lat: -1.45, lon: 29.55}, tags: {office: "cooperative", name: "Koperative Abahinzi"}},
    {type: "node", id: 3, lat: -1.55, lon: 29.65, tags: {craft: "miller", name: "Maize Mill East"}},
    {type: "node", id: 4, lat: -1.42, lon: 29.68, tags: {building: "warehouse", name: "Post-harvest store"}},
    {type: "node", id: 5, lat: -1.58, lon: 29.52, tags: {place: "village", name: "Gisozi-South"}},
    {type: "node", id: 6, lat: -1.47, lon: 29.52, tags: {name: "Milk Collection Centre Kinigi", amenity: "marketplace"}},
    {type: "node", id: 7, lat: -1.50, lon: 29.6001, tags: {amenity: "marketplace", name: "Isoko rya Centre"}}, // duplicate
    {type: "node", id: 8, lat: -1.44, lon: 29.62, tags: {amenity: "cafe", name: "Coffee Shop"}}, // excluded
    {type: "node", id: 9, lat: -1.53, lon: 29.58, tags: {place: "village", name: "Rural Village"}},
    {type: "node", id: 10, lat: -1.41, lon: 29.51, tags: {place: "town", name: "North Town"}}
  ];
  const power = [
    {type: "way", id: 7001, tags: {power: "line", voltage: "30000"}, geometry: line(29.50, -1.503, 29.70, -1.503, 20).map(([lon, lat]) => ({lon, lat}))},
    {type: "node", id: 7002, lat: -1.506, lon: 29.61, tags: {power: "substation", name: "Centre substation"}},
    {type: "node", id: 7003, lat: -1.43, lon: 29.55, tags: {power: "generator", "generator:source": "solar"}}
  ];
  const days = [];
  const tmax = [], tmean = [], rain = [], sw = [];
  const start = Date.UTC(2024, 0, 1);
  for (let d = 0; d < 366; d++) {
    const date = new Date(start + d * 86400000).toISOString().slice(0, 10);
    const m = +date.slice(5, 7);
    days.push(date);
    tmax.push(24 + (m === 8 ? 3 : 0) + Math.sin(d / 20));
    tmean.push(19 + Math.sin(d / 25));
    rain.push([3, 4, 5, 11].includes(m) ? 6 : 1);
    sw.push(16 + (m === 4 ? -3 : 0));
  }
  const climate = {latitude: -1.5, longitude: 29.6, elevation: 1850,
    daily: {time: days, temperature_2m_max: tmax, temperature_2m_mean: tmean, precipitation_sum: rain, shortwave_radiation_sum: sw}};
  return {
    area: {name: "Synthetic District", display_name: "Synthetic District, Testland", bbox, polygon: null, country_code: opts.country || "rw"},
    osm: {sites: {elements: sites}, roads: {elements: roads}, buildings: opts.noBuildings ? null : {elements: buildings}, power: {elements: power}},
    climate, retrieved_at: "2026-10-09T00:00:00Z", sources: [{id: "synthetic", label: "Synthetic test fixture"}]
  };
}
module.exports = {makeFixture};
