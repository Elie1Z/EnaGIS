// Second-site scouting: pure helpers and the checklist decision. No network.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import {fileURLToPath} from "node:url";
import * as S from "../../scripts/scout-sites.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "configs/second-site-candidates.json"), "utf8"));
const root = {};
for (const f of ["config.js", "siting.js", "engine.js"]) vm.runInNewContext(fs.readFileSync(path.join(ROOT, "live/js", f), "utf8"), {window: root, console});
const classify = root.EnaEngine.classifySite;

test("polygon helpers: holes excluded, area of a 1-degree box near the equator", () => {
  const sq = {type: "Polygon", coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], [[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6], [0.4, 0.4]]]};
  assert.equal(S.inPolygon(sq, 0.2, 0.2), true);
  assert.equal(S.inPolygon(sq, 0.5, 0.5), false);
  assert.equal(S.inPolygon(sq, 1.5, 0.5), false);
  const box = {type: "Polygon", coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]};
  assert.ok(Math.abs(S.polygonAreaKm2(box) - 111.32 * 110.57) < 50);
});

test("tile sampling is deterministic and stays inside the boundary", () => {
  const g = {type: "Polygon", coordinates: [[[29.5, -1.7], [29.7, -1.7], [29.7, -1.5], [29.5, -1.5], [29.5, -1.7]]]};
  const t = S.tilesInside(g, [29.5, -1.7, 29.7, -1.5], 14);
  assert.ok(t.length > 50);
  assert.deepEqual(S.shuffled(t, 7).slice(0, 5), S.shuffled(t, 7).slice(0, 5));
  for (const [z, x, y] of t) assert.ok(S.inPolygon(g, S.x2lon(x + 0.5, z), S.y2lat(y + 0.5, z)));
});

test("OpenAerialMap gsd in degrees is converted to metres; licences normalised", () => {
  assert.ok(Math.abs(S.gsdMetres(1.857e-7, 0) - 0.0207) < 0.001);
  assert.equal(S.gsdMetres(0.05, 10), 0.05);
  assert.equal(S.gsdMetres(0, 10), null);
  assert.equal(S.licenceId("CC-BY 4.0"), "CC-BY-4.0");
  assert.equal(S.licenceId("CC-BY-NC-4.0"), "CC-BY-NC-4.0");
});

test("facilities use the app's rules; non-Latin names fall back to name:en and duplicates merge", () => {
  const els = [
    {type: "node", id: 1, lat: 27.1, lon: 78.0, tags: {name: "Shri Ram Cold Storage"}},
    {type: "way", id: 2, center: {lat: 27.10003, lon: 78.00003}, tags: {name: "Shri Ram Cold Storage", building: "yes"}},
    {type: "node", id: 3, lat: 27.2, lon: 78.1, tags: {name: "आगरा शीतगृह", "name:en": "Agra Cold Store"}},
    {type: "node", id: 4, lat: 27.3, lon: 78.2, tags: {name: "City Supermarket", shop: "supermarket"}},
    {type: "node", id: 5, lat: 27.4, lon: 78.3, tags: {name: "Hotel Mill View"}}
  ];
  const f = S.dedupeFacilities(els, classify);
  assert.equal(f.length, 2);
  assert.deepEqual(f[0].ids, ["node/1", "way/2"]);
  assert.equal(f[1].type, "cold_store");
  assert.equal(f[1].strict_type, null);
});

test("checklist: C1 needs all four tests, C2 also needs open sub-metre imagery covering the points", () => {
  const mk = (n, subs, covered) => ({query: "u", facilities: Array.from({length: n}, (_, i) => ({type: "cold_store", strict_type: "cold_store"})),
    positives_by_subdistrict: Object.fromEntries(Array.from({length: subs}, (_, i) => ["s" + i, 1])), imagery: {positives_covered_open_licence_le_1m: covered}});
  const cand = {id: "x", label: "X", region: "South Asia", units: ["u"]};
  const pass = S.evaluateCandidate(cand, [mk(320, 7, 0)], cfg);
  assert.equal(pass.footprint_classifier_c1, "PASS");
  assert.equal(pass.image_detector_c2, "FAIL");
  assert.deepEqual(pass.failed_tests, ["detector_imagery"]);
  assert.equal(S.evaluateCandidate(cand, [mk(320, 7, 310)], cfg).image_detector_c2, "PASS");
  assert.equal(S.evaluateCandidate(cand, [mk(299, 7, 310)], cfg).footprint_classifier_c1, "FAIL");
  assert.equal(S.evaluateCandidate(cand, [mk(320, 5, 310)], cfg).image_detector_c2, "FAIL");
  assert.equal(S.evaluateCandidate({...cand, region: "Europe"}, [mk(320, 7, 310)], cfg).footprint_classifier_c1, "FAIL");
  assert.equal(S.evaluateCandidate(cand, [{query: "u", error: "no boundary"}], cfg).footprint_classifier_c1, "FAIL");
});

test("recorded audit (if present) agrees with its own checklist", {skip: !fs.existsSync(path.join(ROOT, "docs/audits/second-site-scouting.json"))}, () => {
  const a = JSON.parse(fs.readFileSync(path.join(ROOT, "docs/audits/second-site-scouting.json"), "utf8"));
  assert.equal(a.candidates.length, cfg.candidates.length);
  for (const c of a.candidates) {
    const t = c.tests;
    assert.equal(t.labelled_positives.pass, t.labelled_positives.value >= cfg.checklist.min_positive_facilities);
    assert.equal(t.subdistrict_spread.pass, t.subdistrict_spread.value >= cfg.checklist.min_subdistricts_with_positives);
    if (c.image_detector_c2 === "PASS") assert.equal(c.footprint_classifier_c1, "PASS");
  }
  assert.ok(a.run.bytes <= cfg.sampling.traffic_cap_mb * 1e6 * 1.05);
  assert.doesNotMatch(JSON.stringify(a), /"contact"/);
  const md = fs.readFileSync(path.join(ROOT, "docs/second-site-scouting.md"), "utf8");
  for (const c of a.candidates) assert.ok(md.includes(c.label));
});
