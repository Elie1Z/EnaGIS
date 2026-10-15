"use strict";
// Siting model (Phase 4R): metric correctness, training, leave-one-district-out evaluation, engine wiring.
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
require(path.join(__dirname, "../../live/js/config.js"));
const S = require(path.join(__dirname, "../../live/js/siting.js"));
const E = require(path.join(__dirname, "../../live/js/engine.js"));
const {makeFixture} = require("./fixture.cjs");

function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

test("captured() counts ties at the cut-off fractionally", () => {
  // 10 cells, top 10% = 1 cell; three cells tie at the top, one of them positive -> expected 1/3.
  const s = [5, 5, 5, 1, 1, 1, 1, 1, 1, 1], y = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1];
  assert.ok(Math.abs(S.captured(s, y, 0.1) - 1 / 3) < 1e-12);
  // Top 50% = 5 cells: the three 5s plus two of the seven 1s; positive among 1s is 1 of 7 -> 1 + 2/7.
  assert.ok(Math.abs(S.captured(s, y, 0.5) - (1 + 2 / 7)) < 1e-12);
});

test("auc() handles ties (Mann-Whitney)", () => {
  assert.equal(S.auc([3, 2, 1], [1, 0, 0]), 1);
  assert.equal(S.auc([1, 2, 3], [1, 0, 0]), 0);
  assert.equal(S.auc([1, 1, 1, 1], [1, 0, 1, 0]), 0.5);
});

test("logistic fit recovers the direction of a real signal", () => {
  const r = rng(3), X = [], y = [];
  for (let i = 0; i < 3000; i++) { const a = r() * 4 - 2, b = r() * 4 - 2; X.push([a, b]); y.push(r() < 1 / (1 + Math.exp(-(2 * a - 3))) ? 1 : 0); }
  const m = S.fit(X, y, {lambda: 1});
  assert.ok(m.coef[0] > 0.5, "positive weight on the true signal");
  assert.ok(Math.abs(m.coef[1]) < 0.3, "near-zero weight on noise");
});

function synthRows(seed, signal) {
  // Six districts; facilities sit in cells with large roofs near major roads (when signal), else at random.
  const r = rng(seed), rows = [];
  ["A", "B", "C", "D", "E", "F", "G"].forEach(d => {
    for (let k = 0; k < 400; k++) {
      const nb = Math.floor(r() * 300), n200 = r() < 0.15 ? 1 + Math.floor(r() * 6) : 0, dmaj = r() * 8000;
      const z = signal ? -5 + 1.2 * n200 - dmaj / 2500 + nb / 300 : -3;
      const yv = r() < 1 / (1 + Math.exp(-z)) ? 1 : 0;
      rows.push({district: d, nb, nbN: nb * 20, n200, n600: n200 > 3 ? 1 : 0, amax: n200 ? 400 + n200 * 100 : 80, maj_km: dmaj < 500 ? 1 : 0, min_km: r() * 3,
        d_maj: dmaj, d_pow: r() * 10000, d_set: r() * 6000, urb: r() * 0.2, y: yv, y_any: yv});
    }
  });
  return rows;
}

test("evaluation: a real roof signal beats the single-signal baselines; pure noise does not", () => {
  const good = S.evaluate(synthRows(11, true), {draws: 300});
  assert.ok(good.positive_cells >= 60 && good.positive_districts >= 6, "gate met");
  assert.equal(good.verdict, "KEEP");
  assert.ok(good.margin[0].point > 0);
  const noise = S.evaluate(synthRows(12, false), {draws: 300});
  assert.notEqual(noise.verdict, "KEEP", "no signal must not pass the keep rule");
});

test("evaluation reports FEASIBILITY when documented positives are too few", () => {
  const rows = synthRows(13, true).map((r, i) => ({...r, y: i % 97 === 0 ? 1 : 0}));
  const ev = S.evaluate(rows.filter(r => r.district < "D"), {draws: 50});
  assert.equal(ev.verdict, "FEASIBILITY");
});

test("engine: siting rows and in-app prediction run on the fixture", () => {
  const input = makeFixture();
  // Give the fixture's buildings footprint areas (a few large roofs near the mill).
  const b = input.osm.buildings, flat = [], areas = [];
  b.elements.forEach((el, i) => { flat.push(el.center.lon, el.center.lat); areas.push(i % 50 === 0 ? 450 : 60); });
  input.osm.buildings = {compact: "flat", flat, areas, provider: "overture", sources: {"Google Open Buildings": flat.length / 2}};
  const t = E.sitingRows(input, "Fixture");
  assert.ok(t.cells > 100 && t.roofs && t.roads && t.power);
  assert.ok(t.positives >= 1, "the fixture's mill/warehouse label their cells");
  const model = S.train(t.rows.concat(t.rows.map(r => ({...r, district: "Copy"}))));
  global.EnaSitingModel = {model, verdict: "TEST", version: "test"};
  try {
    const res = E.analyze(input, {model: "maize_milling", draws: 40});
    assert.equal(res.siting.status, "ok");
    assert.ok(res.siting.layer.features.length > 0);
    assert.ok(res.sites.some(s => s.siting_pct !== null));
    res.siting.candidates.forEach(c => assert.ok(c.percentile >= 0 && c.percentile <= 1));
    assert.equal(res.steps.find(s => s.id === "siting").status, "done");
  } finally { delete global.EnaSitingModel; }
});

test("cell features measure distances from the cell centre (primary road at lat -1.50)", () => {
  const input = makeFixture();
  const flat = [], areas = [];
  input.osm.buildings.elements.forEach(el => { flat.push(el.center.lon, el.center.lat); areas.push(60); });
  input.osm.buildings = {compact: "flat", flat, areas, provider: "overture"};
  const t = E.sitingRows(input, "Fixture");
  // Cell centres sit 500 m either side of the road (it runs along a cell edge); skip cells past the road's ends.
  const onRoad = t.rows.filter(r => Math.abs(r.lat + 1.50) < 0.0047 && r.lon > 29.505 && r.lon < 29.695), far = t.rows.filter(r => Math.abs(r.lat + 1.50) > 0.03 && Math.abs(r.lon - 29.60) > 0.03);
  assert.ok(onRoad.length > 5 && far.length > 5);
  onRoad.forEach(r => assert.ok(r.d_maj < 600, `cell on the primary road is ${r.d_maj} m from it`));
  far.forEach(r => assert.ok(r.d_maj > 2500, `cell 3+ km from both major roads is only ${r.d_maj} m away`));
  assert.ok(onRoad.filter(r => r.lat > -1.50).every(r => r.maj_km > 0.5), "road length counted in the cells on the edge's north side");
});

test("engine: without footprint sizes the siting step says what is missing", () => {
  global.EnaSitingModel = {model: S.train(synthRows(5, true)), verdict: "TEST"};
  try {
    const res = E.analyze(makeFixture(), {model: "maize_milling", draws: 40});
    assert.equal(res.siting.status, "missing_inputs");
    assert.ok(res.siting.missing.includes("building footprint sizes"));
  } finally { delete global.EnaSitingModel; }
});

test("the shipped Phase 4R model loads, matches the features and records its registered verdict", () => {
  const fs = require("node:fs");
  const ctx = {window: {}};
  new Function("window", fs.readFileSync(path.join(__dirname, "../../live/js/siting-model.js"), "utf8"))(ctx.window);
  const M = ctx.window.EnaSitingModel;
  assert.ok(M && M.model, "model present");
  assert.deepEqual(M.model.features, S.FEATURES.map(f => f.id));
  assert.ok(["KEEP", "KILL", "FEASIBILITY"].includes(M.verdict));
  const model = M.evaluation.arms.find(a => a.arm === "model"), best = M.evaluation.arms.find(a => a.arm === M.evaluation.best_baseline[0]);
  assert.ok(Math.abs(M.evaluation.margin[0].point - (model.recall[0].point - best.recall[0].point)) < 1e-6, "margin = model - best baseline");
  assert.equal(M.verdict === "KEEP", M.evaluation.margin[0].ci[0] > 0, "verdict follows the registered keep rule");
  const audit = JSON.parse(fs.readFileSync(path.join(__dirname, "../../docs/audits/phase4r-evaluation.json"), "utf8"));
  assert.equal(audit.verdict, M.verdict);
  assert.equal(audit.model.intercept, M.model.intercept, "app model = audited model");
});
