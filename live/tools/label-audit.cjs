#!/usr/bin/env node
/* Phase 4R post-hoc label audit: rerun the registered evaluation with labels found to be wrong corrected.
 * Usage: node live/tools/label-audit.cjs [data/rwanda/siting_cells.csv]
 * Reads docs/audits/phase4r-label-audit.json (flagged facilities and the squares they change), writes its
 * "sensitivity" section. The registered verdict in docs/audits/phase4r-evaluation.json is not touched.
 */
"use strict";
const fs = require("fs"), path = require("path"), crypto = require("crypto");
const ROOT = path.join(__dirname, "..", "..");
const S = require(path.join(ROOT, "live/js/siting.js"));
const file = process.argv[2] || path.join(ROOT, "data/rwanda/siting_cells.csv");
const auditPath = path.join(ROOT, "docs/audits/phase4r-label-audit.json");
const audit = JSON.parse(fs.readFileSync(auditPath, "utf8"));
const text = fs.readFileSync(file, "utf8");
const sha = crypto.createHash("sha256").update(text).digest("hex");
if (sha !== audit.input.sha256) throw new Error(`input sha256 ${sha} does not match the audited table ${audit.input.sha256}`);

const lines = text.split(/\r?\n/).filter(Boolean), head = lines[0].split(",");
const NUM = new Set(["lon", "lat", "nb", "nbN", "n200", "n600", "amax", "maj_km", "min_km", "d_maj", "d_pow", "d_set", "urb", "y", "y_any"]);
const parse = (line) => {
  const cells = []; let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) { if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; } else if (ch === '"') q = false; else cur += ch; }
    else if (ch === '"') q = true; else if (ch === ",") { cells.push(cur); cur = ""; } else cur += ch;
  }
  cells.push(cur);
  const r = {}; head.forEach((h, k) => { r[h] = NUM.has(h) ? +cells[k] : cells[k]; }); return r;
};
const base = lines.slice(1).map(parse);

function corrected(changes) {
  const rows = base.map(r => ({...r}));
  changes.forEach(c => {
    const hit = rows.filter(r => r.district === c.district && Math.abs(r.lon - c.lon) < 1e-5 && Math.abs(r.lat - c.lat) < 1e-5);
    if (hit.length !== 1) throw new Error(`square ${c.district} ${c.lon},${c.lat} matched ${hit.length} rows`);
    if (hit[0].y !== c.y[0] || hit[0].y_any !== c.y_any[0]) throw new Error(`square ${c.district} ${c.lon},${c.lat} labels differ from the audit`);
    hit[0].y = c.y[1]; hit[0].y_any = c.y_any[1];
  });
  return rows;
}
const brief = (ev) => {
  const m = ev.arms.find(a => a.arm === "model"), b = ev.arms.find(a => a.arm === ev.best_baseline[0]);
  return {positive_cells: ev.positive_cells, positive_districts: ev.positive_districts, gate: ev.gate, verdict_descriptive: ev.verdict,
    model_recall10: m.recall[0], best_baseline: ev.best_baseline[0], baseline_recall10: b.recall[0], margin10: ev.margin[0], margin20: ev.margin[1],
    model_auc: m.auc, roof_gain10: ev.roof_gain[0]};
};
const t0 = Date.now();
const scenarios = {
  registered: base,
  clear_errors_removed: corrected(audit.cell_changes.clear),
  clear_and_uncertain_removed: corrected(audit.cell_changes.clear.concat(audit.cell_changes.clear_and_uncertain_extra)),
  // Not a label question but the obvious challenge: is the model just finding the capital? Drop Kigali's three districts.
  clear_errors_removed_without_kigali: corrected(audit.cell_changes.clear).filter(r => !["Nyarugenge", "Gasabo", "Kicukiro"].includes(r.district))
};
const out = {};
for (const [k, rows] of Object.entries(scenarios)) {
  out[k] = brief(S.evaluate(rows, {label: "y_any"}));
  const o = out[k], p = v => (v * 100).toFixed(1);
  console.log(`${k.padEnd(28)} positives ${o.positive_cells}  model ${p(o.model_recall10.point)}%  ${o.best_baseline} ${p(o.baseline_recall10.point)}%  margin ${p(o.margin10.point)} [${p(o.margin10.ci[0])}, ${p(o.margin10.ci[1])}]  -> ${o.verdict_descriptive}`);
}
audit.sensitivity = {generated_at: new Date().toISOString(), seconds: (Date.now() - t0) / 1000, label: "y_any",
  note: "Descriptive only. The same registered protocol (leave-one-district-out, 2000 cluster-bootstrap draws, seed 20261011) is rerun on corrected labels.",
  scenarios: out};
fs.writeFileSync(auditPath, JSON.stringify(audit, null, 1));
console.log("wrote docs/audits/phase4r-label-audit.json");

// The app shows one line about the audit under the registered result. Append it to the frozen model file
// (replacing any earlier audit line); the registered model and evaluation above it are untouched.
const modelPath = path.join(ROOT, "live/js/siting-model.js");
const clearCells = audit.cell_changes.clear.filter(c => c.y_any[0] === 1 && c.y_any[1] === 0).length;
const c = out.clear_errors_removed, r1 = v => Math.round(v * 1000) / 10;
const line = `window.EnaSitingModel.audit = ${JSON.stringify({file: "docs/audits/phase4r-label-audit.json", clear_cells: clearCells,
  examples: "a hotel, a football club, a café, shops", margin_point: r1(c.margin10.point), margin_ci: c.margin10.ci.map(r1),
  verdict_descriptive: c.verdict_descriptive})}; /* post-hoc label audit, appended by live/tools/label-audit.cjs */\n`;
const kept = fs.readFileSync(modelPath, "utf8").split("\n").filter(l => l && !l.startsWith("window.EnaSitingModel.audit")).join("\n") + "\n";
fs.writeFileSync(modelPath, kept + line);
console.log("appended the audit line to live/js/siting-model.js");
