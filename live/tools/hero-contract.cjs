'use strict';
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto'), vm = require('node:vm');
const {ROOT} = require('./local-server.cjs');
const DIR = path.join(ROOT, 'data/rwanda/hero/nyabihu-potato');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const read = name => JSON.parse(fs.readFileSync(path.join(DIR, name), 'utf8'));
function engine() {
  const root = {};
  for (const f of ['config.js', 'siting.js', 'siting-model.js', 'engine.js']) vm.runInNewContext(fs.readFileSync(path.join(ROOT, 'live/js', f), 'utf8'), {window:root, console});
  return root.EnaEngine;
}
const options = {model:'potato_storage', seed:20261026, draws:300, overrides:{}, per_capita_kg:{}};
function ranking(result) {
  return {schema:'enagis-hero-ranking-v1', label:'ESTIMATED', seed:result.meta.seed, draws:result.meta.draws,
    seasons:Object.fromEntries(['dry','rainy'].map(season => [season, result.sites.slice().sort((a,b) => a[season].rank - b[season].rank).map(s => ({
      id:s.id, name:s.name, lon:s.lon, lat:s.lat, documented:s.documented, ...s[season]}))]))};
}
function validateInput(input) {
  if (input.area.name !== 'Nyabihu District' || input.area.country_code !== 'rw' || !input.area.polygon) throw new Error('Wrong or missing hero boundary');
  for (const key of ['sites','roads','buildings','power']) if (!input.osm[key]) throw new Error('Missing input ' + key);
  if (!input.population || !input.climate) throw new Error('Population and climate must be present for a complete snapshot');
  for (const theme of ['buildings','transportation','base','places']) {
    const s = input.sources.find(s => s.id === 'overture-' + theme);
    if (!s || !s.label.includes('2026-09-23.1') || /[1-9]\d* failed/.test(s.label)) throw new Error('Incomplete or unpinned Overture ' + theme);
  }
  if (!input.sources.some(s => s.id === 'osm-sites')) throw new Error('Missing Overpass source');
}
function verifyManifest() {
  const m = read('MANIFEST.json');
  for (const f of m.files) {
    const p = path.resolve(ROOT, f.path);
    if (!p.startsWith(ROOT + path.sep) || sha(fs.readFileSync(p)) !== f.sha256) throw new Error('Hash mismatch: ' + f.path);
  }
  return m;
}
module.exports = {ROOT, DIR, sha, read, engine, options, ranking, validateInput, verifyManifest};
