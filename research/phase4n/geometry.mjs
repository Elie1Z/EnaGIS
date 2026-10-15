// Footprint shape measures for Phase 4N (pure; units are those of the input ring, here metres).
// Footprint geometry: area and perimeter (shoelace, metres), minimum rotated rectangle (convex hull + rotating calipers).
export function hull(pts) {
  const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.reverse()) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
export function shape(ring) {
  let a2 = 0, per = 0;
  for (let k = 0, j = ring.length - 1; k < ring.length; j = k++) { a2 += ring[j][0] * ring[k][1] - ring[k][0] * ring[j][1]; per += Math.hypot(ring[k][0] - ring[j][0], ring[k][1] - ring[j][1]); }
  const area = Math.abs(a2) / 2, h = hull(ring);
  let best = null;
  for (let i = 0; i < h.length; i++) {
    const [x0, y0] = h[i], [x1, y1] = h[(i + 1) % h.length], L = Math.hypot(x1 - x0, y1 - y0); if (!L) continue;
    const ux = (x1 - x0) / L, uy = (y1 - y0) / L;
    let a0 = Infinity, a1 = -Infinity, b0 = Infinity, b1 = -Infinity;
    for (const [x, y] of h) { const u = x * ux + y * uy, v = -x * uy + y * ux; a0 = Math.min(a0, u); a1 = Math.max(a1, u); b0 = Math.min(b0, v); b1 = Math.max(b1, v); }
    const w = a1 - a0, d = b1 - b0;
    if (!best || w * d < best.area) best = {area: w * d, long: Math.max(w, d), short: Math.min(w, d)};
  }
  return {area, perimeter: per, elongation: best && best.short > 0 ? best.long / best.short : 1, rectangularity: best && best.area > 0 ? Math.min(1, area / best.area) : 1};
}

