'use strict';
// Plain GeoJSON (RFC 7946) of the Nyabihu potato cold-storage snapshot: every ranked site plus the five siting
// look-alikes, with evidence labels as properties. Rebuilt from the frozen input with the shipped engine and refused
// unless the ranking still equals expected.json. Deterministic: no wall-clock values. Offline.
// Usage: node live/tools/export-hero-geojson.cjs [--check]
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const H = require('./hero-contract.cjs'), V = require('../js/hero-verification.js');
const OUT = path.join(H.ROOT, 'data/rwanda/hero/export/nyabihu-potato-ranking.geojson');
const HERO = path.join(H.ROOT, 'data/rwanda/hero');

function verificationRecords() {
  const load = (name, cols) => {
    const parsed = V.parseCSV(fs.readFileSync(path.join(HERO, name), 'utf8'));
    assert.deepEqual(parsed.header, cols, 'Unexpected columns in ' + name);
    return parsed.rows;
  };
  return {desk: load('desk-check.csv', V.DESK), phone: load('phone-log.csv', V.PHONE)};
}

function build(result) {
  const manifest = H.read('MANIFEST.json'), targets = H.read('verification-targets.json');
  const protocol = JSON.parse(fs.readFileSync(path.join(HERO, 'verification-protocol.json'), 'utf8'));
  const records = verificationRecords();
  const round = (v, d) => v === null || v === undefined ? null : +v.toFixed(d);
  const checks = id => {
    const t = targets.find(x => x.id === id); if (!t) return {verification_target: false};
    const c = V.counts(t, records, protocol);
    return {verification_target: true, desk_checked: c.desk, phone_checked: c.phone, call_attempts: c.attempts,
      calls_confirmed_activity: c.confirmed, calls_rejected_activity: c.rejected, calls_inconclusive: c.inconclusive, field_visits: 0};
  };
  const season = (s, k) => {
    const v = s[k];
    return {[`rank_${k}`]: v.rank, [`tier_${k}`]: v.tier, [`p_top10_${k}`]: round(v.p_top, 4),
      [`people_${k}`]: round(v.people, 0), [`production_t_yr_${k}`]: round(v.production_t, 1),
      [`kwh_day_${k}`]: v.kwh_day ? round(v.kwh_day.central, 1) : null, [`kwh_day_p5_${k}`]: v.kwh_day ? round(v.kwh_day.p5, 1) : null,
      [`kwh_day_p95_${k}`]: v.kwh_day ? round(v.kwh_day.p95, 1) : null, [`kw_running_${k}`]: v.kw ? round(v.kw.central, 2) : null};
  };
  const sites = result.sites.slice().sort((a, b) => a.dry.rank - b.dry.rank).map(s => ({type: 'Feature',
    geometry: {type: 'Point', coordinates: [s.lon, s.lat]},
    properties: {id: s.id, name: s.name, feature_kind: 'ranked_site', site_type: s.type_label, documented: s.documented,
      location_evidence: s.evidence.location.label, location_note: s.evidence.location.text,
      ...season(s, 'dry'), ...season(s, 'rainy'),
      people_evidence: s.evidence.people.label, energy_evidence: s.evidence.need.label,
      grid_state: s.supply.state, grid_line_m: round(s.supply.line_m, 0), grid_evidence: s.evidence.supply.label,
      siting_percentile: round(s.siting_pct, 4), siting_evidence: s.siting_pct === null ? 'UNKNOWN' : 'PREDICTED',
      question: s.question, ...checks(s.id)}}));
  const lookalikes = result.siting.candidates.slice(0, 5).map(c => ({type: 'Feature',
    geometry: {type: 'Point', coordinates: [c.lon, c.lat]},
    properties: {id: 'lookalike-' + c.rank, name: 'Look-alike ?' + c.rank, feature_kind: 'siting_lookalike', documented: false,
      location_evidence: 'PREDICTED', location_note: 'Centre of a 1 km cell that resembles documented processing/storage sites (roofs, roads, grid, settlements); not a detected facility',
      siting_rank: c.rank, siting_percentile: round(c.percentile, 4), siting_evidence: 'PREDICTED', siting_reasons: c.why.join('; '),
      ...checks('lookalike-' + c.rank)}}));
  return {type: 'FeatureCollection',
    enagis: {schema: 'enagis-nyabihu-potato-geojson-v1', title: 'Nyabihu District · Irish potato cold storage · screening ranking',
      snapshot_frozen_at: manifest.frozen_at, overture_release: manifest.release, engine_version: manifest.engine_version,
      seed: result.meta.seed, draws: result.meta.draws, crs: 'EPSG:4326 (RFC 7946 longitude, latitude)',
      units: {people: 'effective catchment people', production_t_yr: 'tonnes per year', kwh_day: 'kWh per peak day', kw_running: 'kW while running', grid_line_m: 'metres to nearest mapped line'},
      evidence_labels: {OBSERVED: 'mapped record (OpenStreetMap or Overture); not field verified', INFERRED: 'derived from mapped context (settlement centre, grid proximity)',
        ESTIMATED: 'screening estimate with unapproved assumptions; ranges from the stated simulation', PREDICTED: 'registered Phase 4R siting model output',
        UNKNOWN: 'not available', 'DESK-CHECKED': 'count of completed satellite-imagery reviews; not field validation',
        'PHONE-CHECKED': 'count of completed calls under the pre-registered activity-only protocol; not energy validation'},
      verification_protocol_sha256: protocol.sha256,
      note: 'Screening results, not a feasibility study. Plain GeoJSON, loadable in QGIS or Energy Access Explorer; compatibility with any platform is not certified.',
      licence: 'Contains information from OpenStreetMap and Overture Maps (ODbL 1.0; Overture places CDLA-Permissive-2.0); WorldPop and Open-Meteo (CC BY 4.0). Share-alike obligations of ODbL apply to this derived database.'},
    features: sites.concat(lookalikes)};
}

if (require.main === module) {
  H.verifyManifest();
  const input = H.read('input.json'); H.validateInput(input);
  const result = H.engine().analyze(input, H.options);
  assert.equal(JSON.stringify(H.ranking(result)), JSON.stringify(H.read('expected.json')), 'Ranking differs from expected.json; export refused');
  const text = JSON.stringify(build(result), null, 1) + '\n';
  if (process.argv.includes('--check')) {
    assert.equal(fs.readFileSync(OUT, 'utf8'), text, 'Exported GeoJSON is stale; run node live/tools/export-hero-geojson.cjs');
    console.log('PASS hero-geojson: export matches the frozen ranking and the current verification logs.');
  } else {
    fs.mkdirSync(path.dirname(OUT), {recursive: true}); fs.writeFileSync(OUT, text);
    console.log(`Wrote ${path.relative(H.ROOT, OUT)}: ${JSON.parse(text).features.length} features.`);
  }
}
module.exports = {build, OUT};
