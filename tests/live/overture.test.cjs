"use strict";
/* Tests for the Overture / WorldPop data paths (no network: converters and engine only). */
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
require(path.join(__dirname, "../../live/js/config.js"));
const E = require(path.join(__dirname, "../../live/js/engine.js"));
require(path.join(__dirname, "../../live/js/overture.js"));
const OV = globalThis.EnaOverture;
const {makeFixture} = require("./fixture.cjs");

const place = (name, primary, conf, hier) => ({"@name": name, confidence: conf,
  taxonomy: JSON.stringify({primary, hierarchy: hier || ["services_and_business", primary]})});

test("Overture places: agricultural listings kept, look-alikes dropped", () => {
  assert.equal(OV.classifyPlace(place("Musanze Market", "flea_market", 0.77)).type, "market");
  assert.equal(OV.classifyPlace(place("APF Rwanda Network", "agricultural_service", 0.53)).type, "agro_shop");
  assert.equal(OV.classifyPlace(place("Agriresearch club,ur CVM busogo campus", "agricultural_service", 0.53)), null, "a campus club is not a farm shop");
  assert.equal(OV.classifyPlace(place("Pfunda Tourism Cooperative", "flea_market", 0.7)), null, "a tourism cooperative is not a market");
  assert.equal(OV.classifyPlace(place("Nyamata United F.C", "dairy_farm", 0.7)), null, "a football club is not a milk centre");
  assert.equal(OV.classifyPlace(place("Shagasha Tea Company", "tea_manufacturer", 0.8)).type, "tea_factory");
  assert.equal(OV.classifyPlace(place("Koperative Twitezimbere", "professional_service", 0.6)).type, "cooperative");
  assert.equal(OV.classifyPlace(place("Techno Market", "printing_service", 0.69)), null);
  assert.equal(OV.classifyPlace(place("Kwetu Market", "professional_service", 0.13)), null, "low confidence");
  assert.equal(OV.classifyPlace(place("Simba Supermarket", "department_store", 0.74)), null);
  assert.equal(OV.classifyPlace(place("Kivu Choice", "fish_farm", 0.9)), null);
  assert.equal(OV.classifyPlace(place("Hotel des Mille Collines", "hotel", 0.99)), null);
});

test("Overture roads: pieces cut at a tile edge are joined into one network", () => {
  // One segment split across two tiles (cut ends 20 m apart), plus a side road meeting it.
  const a = {id: "seg1", hw: "secondary", surface: "paved", name: null, coords: [[30.0000, -1.5], [30.0100, -1.5]], cut: [false, true]};
  const b = {id: "seg1", hw: "secondary", surface: "paved", name: null, coords: [[30.0102, -1.5], [30.0200, -1.5]], cut: [true, false]};
  const c = {id: "seg2", hw: "track", surface: null, name: null, coords: [[30.0200, -1.5], [30.0200, -1.49]], cut: [false, false]};
  const json = OV.roadsJSON([[a], [b, c]]);
  assert.equal(json.links, 2, "both cut ends linked");
  const P = E.projector([29.99, -1.51, 30.03, -1.48]);
  const G = E.parseRoads(json, P);
  // Every vertex reachable from the west end.
  const r = E.dijkstra(G, [{v: 0, site: 0, t: 0}], G.wDry, 1e9);
  assert.ok(Array.from(r.owner).every(o => o === 0), "network is connected");
  assert.equal(G.provider, "overture");
  assert.ok(G.lengthM > 3000 && G.lengthM < 3400, `length ${G.lengthM} excludes link stubs`);
});

test("Overture power: pylons count as evidence of a line", () => {
  const json = OV.powerJSON([[{k: "tower", coords: [[30.0, -1.5]]}, {k: "point", power: "substation", name: "S", coords: [[30.05, -1.5]]}]]);
  const PW = E.parsePower(json, E.projector([29.9, -1.6, 30.1, -1.4]));
  assert.equal(PW.towers, 1);
  assert.equal(PW.points.length, 1);
  assert.ok(PW.index.nearest(E.projector([29.9, -1.6, 30.1, -1.4]).x(30.001), E.projector([29.9, -1.6, 30.1, -1.4]).y(-1.5), 500));
});

function flatFixture(extra) {
  const fx = makeFixture();
  const flat = [];
  fx.osm.buildings.elements.forEach(el => flat.push(el.center.lon, el.center.lat));
  fx.osm.buildings = {compact: "flat", flat, sources: {"Google Open Buildings": 6000, "OpenStreetMap": 1400, "Microsoft ML Buildings": 100}, provider: "overture"};
  return Object.assign(fx, extra || {});
}

test("flat buildings + WorldPop calibrate people per building", () => {
  const nB = 7500;
  const a = E.analyze(flatFixture({population: {total: 3 * nB, year: 2020, dataset: "wpgppop"}}), {model: "maize_milling", draws: 60});
  assert.equal(a.coverage.buildings, nB);
  assert.equal(a.assumptions.persons_per_building.calibrated, true);
  assert.deepEqual(a.assumptions.persons_per_building.range, [2.4, 3, 3.6]);
  assert.equal(a.population.per_building, 3);
  assert.equal(a.building_sources[0].name, "Google Open Buildings");
  assert.ok(a.sites.some(s => s.dry.rank === 1), "ranking produced");
  assert.match(a.sites[0].evidence.people.text, /WorldPop/);
  // Same data without WorldPop falls back to the assumption range.
  const b = E.analyze(flatFixture(), {model: "maize_milling", draws: 60});
  assert.equal(b.assumptions.persons_per_building.calibrated, false);
  assert.equal(b.population, null);
});

test("Overture places join the candidate list with their provenance", () => {
  const fx = flatFixture();
  fx.osm.sites.elements.push({type: "overture", id: "abc-123", lon: 29.66, lat: -1.46,
    tags: {name: "Koperative Imbaraga", "enagis:type": "cooperative", "enagis:source": "overture", "enagis:category": "agricultural_service", "enagis:confidence": 0.71}});
  const a = E.analyze(fx, {model: "maize_milling", draws: 30});
  const s = a.sites.find(x => x.name === "Koperative Imbaraga");
  assert.ok(s, "listed");
  assert.equal(s.source, "overture");
  assert.match(s.osm_url, /explore\.overturemaps\.org/);
  assert.match(s.evidence.location.text, /Overture Maps places/);
});

test("real Gasabo look-alikes are rejected (Oct 2026 data)", () => {
  // From the live Gasabo run: a church named "Isoko ...", stores filed as warehouses, a consultancy, a government agency.
  assert.equal(OV.classifyPlace(place("Isoko Imara Inyota Church", "religious_organization", 0.67)), null);
  assert.equal(OV.classifyPlace(place("Ceramica Verdi Rwanda", "warehouse_club_store", 0.55)), null);
  assert.equal(OV.classifyPlace(place("AutoXpress", "warehouse", 0.95)), null, "warehouse needs an agricultural name");
  assert.equal(OV.classifyPlace(place("Rwanda Grain Warehouse", "warehouse", 0.7)).type, "warehouse");
  assert.equal(OV.classifyPlace(place("Education Development Consult", "farm_equipment_and_supply", 0.85)), null);
  assert.equal(OV.classifyPlace(place("Rwanda Cooperative Agency-RCA", "government_office", 0.59)), null);
  assert.equal(OV.classifyPlace(place("Kigali farmers' and artisans' market", "farmers_market", 0.68)).type, "market");
  assert.equal(OV.classifyPlace(place("Umutima Cooperative", "shopping", 0.86)).type, "cooperative");
  // OpenStreetMap side.
  assert.equal(E.classifySite({man_made: "works", name: "Deutsche Welle"}), null);
  assert.equal(E.classifySite({man_made: "works", name: "Rwanda Mountain Tea Packing and Blending Facility"}), "agro_factory");
  assert.equal(E.classifySite({office: "government", name: "RRA RSSB One Stop Collection Centre"}), null);
  assert.equal(E.classifySite({name: "Marine Super Market"}), null);
  assert.equal(E.classifySite({amenity: "marketplace", name: "Kimironko Market"}), "market");
});
