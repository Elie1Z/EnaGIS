/* EnaGIS harvest: build the Phase 4R training table and district summaries in a browser.
 * Loads after config.js, enagis-tiles.js, engine.js, siting.js, sources.js and overture.js.
 * For each district: find the boundary (Nominatim) -> gather open data (Overture + OpenStreetMap + WorldPop +
 * Open-Meteo, exactly as the app does) -> siting rows (1 km cells, features, labels) -> the app's analysis for
 * each value chain (for district comparison). Everything is cached in IndexedDB, so a rerun is fast.
 * Usage (browser console): EnaHarvest.run(EnaHarvest.RWANDA) ; poll EnaHarvest.status()
 */
(function (root) {
  "use strict";
  const RWANDA = ["Nyarugenge", "Gasabo", "Kicukiro",
    "Nyanza", "Gisagara", "Nyaruguru", "Huye", "Nyamagabe", "Ruhango", "Muhanga", "Kamonyi",
    "Karongi", "Rutsiro", "Rubavu", "Nyabihu", "Ngororero", "Rusizi", "Nyamasheke",
    "Rulindo", "Gakenke", "Musanze", "Burera", "Gicumbi",
    "Rwamagana", "Nyagatare", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Bugesera"];
  const S = {running: false, queue: [], done: {}, failed: {}, current: null, step: null, log: [], started: null};
  const db = () => root.EnaSources.db;
  const log = (m) => { S.log.push(new Date().toISOString().slice(11, 19) + " " + m); if (S.log.length > 300) S.log.shift(); };

  async function findDistrict(name) {
    const cands = await root.EnaSources.geocode(`${name} District, Rwanda`);
    const ok = cands.filter(a => a.polygon && a.country_code === "rw" && /relation/.test(a.osm || ""));
    const pick = ok.find(a => /district/i.test(a.display_name.split(",")[0]) || a.kind === "county" || a.kind === "state_district") || ok[0];
    if (!pick) throw new Error("no district boundary found");
    pick.name = `${name} District`;
    return pick;
  }

  function summarize(name, input, t) {
    const E = root.EnaEngine, out = {district: name, cells: t.cells, positives: t.positives, documented_processing: t.documented,
      buildings: t.buildings, roofs: t.roofs, settlements: t.settlements, population: input.population ? Math.round(input.population.total) : null,
      area_km2: Math.round(E.areaOf(input.area)), sources: (input.sources || []).map(s => s.label), models: {}};
    ["potato_storage", "milk_cooling", "maize_milling", "maize_drying"].forEach(m => {
      try {
        const r = E.analyze(input, {model: m, draws: 300});
        const top = r.sites.filter(s => s.dry.rank && s.dry.rank <= 10).sort((a, b) => a.dry.rank - b.dry.rank);
        out.models[m] = {eligible: r.sites.length, documented: r.sites.filter(s => s.documented).length, ranked: top.length,
          robust: top.filter(s => s.dry.tier === "Robust").length, coverage: r.coverage.class,
          top_kwh: top.reduce((a, s) => a + (s.dry.kwh_day ? s.dry.kwh_day.central : 0), 0),
          top3: top.slice(0, 3).map(s => `${s.name} (${s.type_label})`), baseline_overlap: r.baseline ? r.baseline.overlap : null};
      } catch (e) { out.models[m] = {error: String(e.message || e)}; }
    });
    return out;
  }

  async function one(name) {
    S.current = name; S.step = "boundary"; const t0 = Date.now();
    const area = await findDistrict(name);
    S.step = "gather";
    const input = await root.EnaSources.gather(area, (st) => { if (st.status === "running") S.step = `${st.id}: ${st.detail || ""}`; });
    S.step = "rows";
    const t = root.EnaEngine.sitingRows(input, name);
    await db().set(`harvest:rows:${name}`, t);
    S.step = "analysis";
    const sum = summarize(name, input, t);
    sum.seconds = Math.round((Date.now() - t0) / 1000);
    sum.release = (input.sources || []).filter(s => /Overture/.test(s.label)).map(s => s.label).join(" | ");
    await db().set(`harvest:sum:${name}`, sum);
    // The gathered tiles and queries stay in the browser cache, so gathering this district again (for a demo pack) is fast.
    return sum;
  }

  async function run(names, opts) {
    if (S.running) return "already running";
    S.running = true; S.queue = names.slice(); S.started = new Date().toISOString(); S.opts = opts || {};
    (async () => {
      while (S.queue.length) {
        const name = S.queue.shift();
        if (!S.opts.force) { const hit = await db().get(`harvest:sum:${name}`); if (hit) { S.done[name] = hit.v; log(`${name}: cached`); continue; } }
        for (let attempt = 1; attempt <= 2; attempt++) {
          try { const s = await one(name); S.done[name] = s; delete S.failed[name]; log(`${name}: ${s.cells} cells, ${s.positives} positive, ${s.seconds}s`); break; }
          catch (e) { S.failed[name] = String(e.message || e); log(`${name}: attempt ${attempt} failed: ${S.failed[name]}`); }
        }
      }
      S.running = false; S.current = null; S.step = null; log("finished");
    })();
    return "started";
  }

  function status() {
    return {running: S.running, current: S.current, step: S.step, done: Object.keys(S.done).length, queued: S.queue.length,
      failed: S.failed, last: S.log.slice(-6)};
  }
  async function rows(names) {
    const out = [];
    for (const n of names) { const h = await db().get(`harvest:rows:${n}`); if (h) out.push(...h.v.rows); }
    return out;
  }
  async function facilities(names) {
    const out = [];
    for (const n of names) { const h = await db().get(`harvest:rows:${n}`); if (h) h.v.facilities.forEach(f => out.push({district: n, ...f})); }
    return out;
  }
  async function summaries(names) {
    const out = {};
    for (const n of names) { const h = await db().get(`harvest:sum:${n}`); if (h) out[n] = h.v; }
    return out;
  }
  function toCSV(rs) {
    if (!rs.length) return "";
    const cols = Object.keys(rs[0]);
    const q = v => (typeof v === "string" && /[",\n]/.test(v)) ? `"${v.replace(/"/g, '""')}"` : v;
    return [cols.join(",")].concat(rs.map(r => cols.map(c => q(r[c])).join(","))).join("\n");
  }
  root.EnaHarvest = {RWANDA, run, status, rows, summaries, facilities, toCSV, findDistrict, state: S};
})(typeof window !== "undefined" ? window : globalThis);
