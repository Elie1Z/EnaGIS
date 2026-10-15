"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
require(path.join(__dirname, "../../live/js/config.js"));
const E = require(path.join(__dirname, "../../live/js/engine.js"));
const {makeFixture} = require("./fixture.cjs");

test("classifies facilities and excludes look-alikes", () => {
  assert.equal(E.classifySite({amenity: "marketplace"}), "market");
  assert.equal(E.classifySite({office: "cooperative"}), "cooperative");
  assert.equal(E.classifySite({name: "Koperative Twitezimbere"}), "cooperative");
  assert.equal(E.classifySite({name: "MCC Gicumbi milk collection centre"}), "milk_centre");
  assert.equal(E.classifySite({craft: "miller"}), "mill");
  assert.equal(E.classifySite({industrial: "sawmill"}), null);
  assert.equal(E.classifySite({amenity: "cafe", name: "Coffee"}), null);
  assert.equal(E.classifySite({shop: "supermarket", name: "Market Plaza"}), null);
  assert.equal(E.classifySite({place: "village"}), "village");
  assert.equal(E.classifySite({place: "hamlet"}), null);
  assert.equal(E.classifySite({highway: "residential", name: "Rue du Marché"}), null, "a street is not a market");
  assert.equal(E.classifySite({highway: "tertiary", name: "Mill Road"}), null, "a street is not a mill");
  assert.equal(E.classifySite({building: "yes", name: "Nyamata"}), null, "Nyamata is a town, not 'amata' (milk)");
  assert.equal(E.classifySite({amenity: "townhall", name: "Nyamata"}), null);
  assert.equal(E.classifySite({name: "Ikusanyirizo ry'amata Mukamira"}), "milk_centre");
  assert.equal(E.classifySite({amenity: "community_centre", name: "Isoko Imara Inyota Church"}), null, "a church named Isoko is not a market");
  assert.equal(E.classifySite({amenity: "marketplace", name: "Isoko rya Kinigi"}), "market");
  assert.equal(E.classifySite({man_made: "works", name: "Nshili Tea Factory"}), "tea_factory", "tea factories are their own type");
  assert.equal(E.classifySite({"enagis:type": "agro_shop", name: "x"}), "agro_shop", "Overture types are classified upstream");
  // Found in the real Rwanda data (UI check, 10 Oct 2026): none of these is a collection point.
  assert.equal(E.classifySite({building: "yes", name: "En: Vunga market's Public Toilet (rw: Ubwiherero rusange bw'isoko rya Vunga)"}), null, "a market's toilet is not a market");
  assert.equal(E.classifySite({amenity: "toilets", name: "Market toilets"}), null);
  assert.equal(E.classifySite({tourism: "hotel", name: "Hôtel des Mille Collines"}), null, "Mille is not a mill, and a hotel is not a facility");
  assert.equal(E.classifySite({building: "yes", name: "Mille Collines"}), null, "'Mille' does not match mill");
  assert.equal(E.classifySite({name: "Musha Rice Mill Ltd"}), "mill");
  assert.equal(E.classifySite({name: "Ameg Milling Machine"}), "mill");
  assert.equal(E.classifySite({building: "yes", name: "kabeza coffee shop"}), null, "a coffee shop is not a washing station");
  assert.equal(E.classifySite({name: "Simbi coffee washing station"}), "coffee_station");
  assert.equal(E.classifySite({building: "yes", name: "Gatare Tea Collection Centers"}), "tea_factory", "a tea-leaf collection centre is not a milk centre");
});

test("dijkstra finds shortest multi-source travel times", () => {
  // Path 0-1-2-3 with unit weights; sources at 0 and 3.
  const n = 4, start = new Int32Array([0, 1, 3, 5, 6]), adj = new Int32Array([1, 0, 2, 1, 3, 2]);
  const w = new Float32Array([1, 1, 1, 1, 1, 1]);
  const r = E.dijkstra({n, start, adj}, [{v: 0, site: 0, t: 0}, {v: 3, site: 1, t: 0.5}], w, 100);
  assert.deepEqual(Array.from(r.owner), [0, 0, 1, 1]);
  assert.equal(r.dist[2], 1.5);
});

test("full analysis runs, ranks and stays deterministic", () => {
  const a = E.analyze(makeFixture(), {model: "maize_milling", draws: 120});
  const b = E.analyze(makeFixture(), {model: "maize_milling", draws: 120});
  assert.deepEqual(a.sites.map(s => s.dry.rank), b.sites.map(s => s.dry.rank));
  assert.ok(a.sites.length >= 5, "eligible sites found");
  const ranks = a.sites.map(s => s.dry.rank).filter(Boolean).sort((x, y) => x - y);
  assert.deepEqual(ranks, ranks.map((_, i) => i + 1), "ranks are 1..n without gaps or ties");
  a.sites.forEach(s => {
    if (!s.dry.kwh_day) return;
    assert.ok(s.dry.kwh_day.p5 <= s.dry.kwh_day.p95);
    assert.ok(s.dry.kwh_day.central > 0);
    assert.ok(s.dry.p_top >= 0 && s.dry.p_top <= 1);
  });
  assert.ok(a.steps.every(st => st.status === "done"), JSON.stringify(a.steps));
  assert.ok(a.narrative.paragraphs.length >= 3);
  // Duplicate market merged, cafe excluded.
  assert.equal(a.sites.filter(s => s.name === "Isoko rya Centre").length + a.context.filter(s => s.name === "Isoko rya Centre").length, 1);
  assert.ok(!a.sites.concat(a.context).some(s => s.name === "Coffee Shop"));
});

test("rainy season never brings more people within reach overall", () => {
  const a = E.analyze(makeFixture(), {model: "potato_storage", draws: 50});
  const dry = a.sites.reduce((s, x) => s + x.dry.people, 0), rainy = a.sites.reduce((s, x) => s + x.rainy.people, 0);
  assert.ok(rainy <= dry + 1e-6, `rainy ${rainy} > dry ${dry}`);
});

test("unknown production stays UNKNOWN, never zero", () => {
  const a = E.analyze(makeFixture({country: "zz"}), {model: "milk_cooling", draws: 30});
  assert.equal(a.meta.per_capita.t, null);
  assert.ok(a.sites.every(s => s.dry.kwh_day === null && s.dry.rank === null));
  assert.equal(a.sites[0].evidence.need.label, "UNKNOWN");
  // A user-entered figure unlocks the estimate.
  const b = E.analyze(makeFixture({country: "zz"}), {model: "milk_cooling", draws: 30, per_capita_kg: {milk: 60}});
  assert.ok(b.sites.some(s => s.dry.rank === 1));
});

test("missing buildings degrade gracefully", () => {
  const a = E.analyze(makeFixture({noBuildings: true}), {model: "maize_drying", draws: 20});
  assert.equal(a.steps.find(s => s.id === "buildings").status, "failed");
  assert.ok(a.sites.every(s => s.dry.kwh_day === null));
  assert.equal(a.baseline, null);
});

test("supply context: line along the primary road is near the centre market", () => {
  const a = E.analyze(makeFixture(), {model: "maize_milling", draws: 20});
  const m = a.sites.find(s => s.name === "Isoko rya Centre");
  assert.equal(m.supply.state, "grid_near");
  assert.ok(m.solar && m.solar.kwp > 0);
});

test("Rwandan districts use district production; multi-district areas use the national figure", () => {
  const base = makeFixture();
  const at = (name, display, kind) => ({...base, area: {...base.area, name, display_name: display, kind, country_code: "rw"}});
  const ny = E.analyze(at("Nyabihu District", "Nyabihu, Western Province, Rwanda", "county"), {model: "potato_storage", draws: 40});
  assert.equal(ny.meta.per_capita.evidence.district, "Nyabihu");
  assert.ok(ny.meta.per_capita.t * 1000 > 500, "Nyabihu grows far more potatoes per person than the national average");
  const sector = E.analyze(at("Kinigi", "Kinigi, Musanze, Northern Province, Rwanda", "suburb"), {model: "potato_storage", draws: 40});
  assert.equal(sector.meta.per_capita.evidence.district, "Musanze");
  const prov = E.analyze(at("Northern Province", "Northern Province, Rwanda", "state"), {model: "potato_storage", draws: 40});
  assert.equal(prov.meta.per_capita.evidence.district, undefined);
  assert.ok(Math.abs(prov.meta.per_capita.t * 1000 - 62.5) < 1, "national 2024 average");
  const milk = E.analyze(at("Nyabihu District", "Nyabihu, Western Province, Rwanda", "county"), {model: "milk_cooling", draws: 40});
  assert.equal(milk.meta.per_capita.evidence.district, undefined, "no district milk series: national");
});

test("same-named sites are told apart (two villages called Cyamabuye)", () => {
  const fx = makeFixture();
  fx.osm.sites.elements.push({type: "node", id: 11, lat: -1.46, lon: 29.53, tags: {place: "village", name: "Cyamabuye"}},
    {type: "node", id: 12, lat: -1.47, lon: 29.66, tags: {place: "village", name: "Cyamabuye"}});
  const a = E.analyze(fx, {model: "potato_storage", draws: 30});
  const names = a.sites.filter(s => /^Cyamabuye/.test(s.name)).map(s => s.name).sort();
  assert.deepEqual(names, ["Cyamabuye (east)", "Cyamabuye (west)"]);
  const standIns = a.sites.filter(s => !s.named && /near/.test(s.name));
  standIns.forEach(s => assert.ok(!/ of \d/.test(s.name), "unnamed stand-ins are told apart by coordinates, not by count: " + s.name));
  assert.equal(new Set(a.sites.map(s => s.name)).size, a.sites.length, "every site name is unique");
});
