/* Exports the SYNTHETIC demo area as Overture-like GeoJSON layers, for make_test_tiles.py. Not real data. */
"use strict";
const fs = require("node:fs"), path = require("node:path");
const {makeSynthetic} = require("../../live/js/synthetic.js");
const s = makeSynthetic(7);
const OUT = path.join(__dirname, "tiles");
const SRC = ["Google Open Buildings", "OpenStreetMap", "Google Open Buildings", "Microsoft ML Buildings"];
const D = 0.00004; // ~4.5 m half-size squares (about 81 m²); every 40th is a large roof (~26 m side, about 700 m²)
const buildings = s.osm.buildings.elements.map((b, i) => {
  const c = b.center || {lon: b.lon, lat: b.lat}, d = i % 40 === 0 ? 0.000118 : D;
  return {type: "Feature", properties: {id: "b" + i, "@geometry_source": SRC[i % 4], is_underground: false},
    geometry: {type: "Polygon", coordinates: [[[c.lon - d, c.lat - d], [c.lon + d, c.lat - d], [c.lon + d, c.lat + d], [c.lon - d, c.lat + d], [c.lon - d, c.lat - d]]]}};
});
const CLASS = {primary: "primary", secondary: "secondary", tertiary: "tertiary", unclassified: "unclassified", residential: "residential", track: "track", path: "path", footway: "footway"};
const segments = s.osm.roads.elements.map(w => ({type: "Feature",
  properties: {id: "seg-" + w.id, subtype: "road", class: CLASS[w.tags.highway] || "unknown",
    ...(w.tags.surface ? {road_surface: JSON.stringify([{value: /asphalt|paved/.test(w.tags.surface) ? "paved" : w.tags.surface}])} : {})},
  geometry: {type: "LineString", coordinates: w.geometry.map(g => [g.lon, g.lat])}}));
const infra = [];
(s.osm.power.elements || []).forEach((e, i) => {
  const t = e.tags || {};
  if (e.type === "way" && /line/.test(t.power || "")) {
    infra.push({type: "Feature", properties: {subtype: "power", class: t.power === "line" ? "power_line" : "minor_line", source_tags: JSON.stringify({power: t.power, voltage: t.voltage || ""})},
      geometry: {type: "LineString", coordinates: e.geometry.map(g => [g.lon, g.lat])}});
    e.geometry.filter((_, k) => k % 3 === 0).forEach(g => infra.push({type: "Feature", properties: {subtype: "power", class: "power_tower", source_tags: "{\"power\":\"tower\"}"},
      geometry: {type: "Point", coordinates: [g.lon, g.lat]}}));
  } else if (t.power) {
    const lon = e.lon || (e.center && e.center.lon), lat = e.lat || (e.center && e.center.lat);
    const q = 0.0003;
    infra.push({type: "Feature", properties: {subtype: "power", class: t.power, "@name": t.name || "", source_tags: JSON.stringify({power: t.power, "generator:source": t["generator:source"] || ""})},
      geometry: {type: "Polygon", coordinates: [[[lon - q, lat - q], [lon + q, lat - q], [lon + q, lat + q], [lon - q, lat + q], [lon - q, lat - q]]]}});
  }
});
const [W, S, E, N] = s.area.bbox, cx = (W + E) / 2, cy = (S + N) / 2;
const tax = (primary, hier) => JSON.stringify({primary, hierarchy: hier});
const places = [
  {name: "Synthetic Agro Supplies", primary: "agricultural_service", conf: 0.8, lon: cx + 0.07, lat: cy + 0.06},
  {name: "Koperative Synthetic Imbuto", primary: "professional_service", conf: 0.7, lon: cx - 0.08, lat: cy - 0.07},
  {name: "Isoko Synthetic Church", primary: "religious_organization", conf: 0.9, lon: cx - 0.05, lat: cy + 0.08},
  {name: "Synthetic Phone Market", primary: "electronics_store", conf: 0.9, lon: cx + 0.02, lat: cy + 0.02}
].map((p, i) => ({type: "Feature", properties: {id: "pl" + i, "@name": p.name, confidence: p.conf, basic_category: p.primary,
  taxonomy: tax(p.primary, ["services_and_business", p.primary])}, geometry: {type: "Point", coordinates: [p.lon, p.lat]}}));
fs.mkdirSync(OUT, {recursive: true});
fs.writeFileSync(path.join(OUT, "layers.json"), JSON.stringify({bbox: s.area.bbox, buildings, segments, infra, places}));
console.log("buildings", buildings.length, "segments", segments.length, "infra", infra.length, "places", places.length);
