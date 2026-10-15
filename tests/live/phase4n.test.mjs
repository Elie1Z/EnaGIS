// Phase 4N footprint shape measures (pure geometry; no network).
import test from "node:test";
import assert from "node:assert/strict";
import {shape, hull} from "../../research/phase4n/geometry.mjs";

const close = (a, b, e = 1e-9) => assert.ok(Math.abs(a - b) < e, `${a} vs ${b}`);

test("rectangle: area, perimeter, elongation 2, rectangularity 1", () => {
  const s = shape([[0, 0], [10, 0], [10, 5], [0, 5], [0, 0]]);
  close(s.area, 50); close(s.perimeter, 30); close(s.elongation, 2); close(s.rectangularity, 1);
});

test("rotated square: minimum rotated rectangle finds the rotation", () => {
  const c = Math.SQRT1_2 * 10, s = shape([[0, 0], [c, c], [0, 2 * c], [-c, c], [0, 0]]);
  close(s.area, 100, 1e-6); close(s.elongation, 1, 1e-9); close(s.rectangularity, 1, 1e-9);
});

test("L-shape is less rectangular than its box; hull drops the reflex corner", () => {
  const ring = [[0, 0], [10, 0], [10, 4], [4, 4], [4, 10], [0, 10], [0, 0]];
  const s = shape(ring);
  close(s.area, 64);
  assert.ok(s.rectangularity < 0.7 && s.rectangularity > 0.6);
  assert.equal(hull(ring).some(([x, y]) => x === 4 && y === 4), false);
});

test("degenerate rings do not produce NaN", () => {
  const s = shape([[0, 0], [5, 0], [0, 0]]);
  assert.ok([s.area, s.perimeter, s.elongation, s.rectangularity].every(Number.isFinite));
});
