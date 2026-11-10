'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
require('../../live/js/config-v2.js');
const C = global.EnaConfig;
const E = require('../../live/js/engine-v2.js');
const {makeFixture} = require('./fixture.cjs');

const equipment = {schema: 'enagis-equipment-evidence-v1', source: 'Synthetic equipment specification',
  source_date: '2026-11-10', licence: 'Synthetic fixture', label: 'INFERRED'};
function run(model, options = {}, input = makeFixture()) {
  return E.analyze(input, {model, scenario: C.resolveScenario({recipe: model}), draws: 20, ...options});
}

test('service totals include disjoint reported categories beyond the legacy commodity', () => {
  const input = makeFixture();
  input.area.name = 'Synthetic national proxy';
  input.area.display_name = 'Synthetic national proxy';
  const result = run('milling', {}, input);
  const components = result.meta.service.components;
  assert.deepEqual(components.map(item => item.crop), ['maize', 'sorghum', 'wheat', 'paddy_rice']);
  assert.equal(result.meta.per_capita.t, (627086 + 187766 + 16416 + 141932) / C.COUNTRIES.RW.population.value);
  assert.equal(new Set(components.map(item => item.crop)).size, components.length);
  assert.ok(result.sites.some(site => site.dry.kwh_day?.central > 0));
});

test('local and national components declare their distinct spatial basis', () => {
  const input = makeFixture();
  input.area.name = 'Nyabihu'; input.area.display_name = 'Nyabihu District, Rwanda';
  const result = run('cold_storage', {}, input);
  assert.match(result.meta.service.components[0].scope, /Nyabihu/);
  assert.equal(result.meta.service.components[1].scope, 'National proxy');
  assert.equal(result.meta.service.coverage, 'partial');
});

test('each service can run without a user crop choice', () => {
  for (const model of Object.keys(C.SERVICES)) {
    const result = run(model);
    assert.equal(result.meta.model.id, model);
    assert.ok(result.sites.length);
    assert.ok(result.meta.service.boundary);
    assert.equal(result.meta.scenario.recipe_version, 'service-v1');
  }
});

test('missing equipment intensity preserves production and candidates without zero energy or ranks', () => {
  for (const model of ['shelling', 'oil_pressing', 'feed_preparation']) {
    const result = run(model);
    assert.equal(result.meta.service.energy_ready, false);
    assert.ok(result.sites.some(site => site.dry.production_t > 0));
    for (const site of result.sites) {
      assert.equal(site.dry.kwh_day, null);
      assert.equal(site.dry.rank, null);
      assert.equal(site.dry.tier, null);
    }
  }
});

test('sourced equipment intensity enables a dimensional electricity estimate', () => {
  const result = run('oil_pressing', {overrides: {specific_energy: [10, 20, 30]}, energy_evidence: {oil_pressing: equipment}});
  assert.equal(result.meta.service.energy_ready, true);
  for (const site of result.sites) {
    assert.equal(site.dry.kwh_day.central, site.dry.throughput_t_day * 20);
  }
  assert.equal(result.meta.service.energy_evidence.source, equipment.source);
  assert.throws(() => run('oil_pressing', {overrides: {specific_energy: [10, 20, 30]}}), /source/);
});

test('outside the production pack coverage remains unknown, and sourced service totals work', () => {
  const input = makeFixture(); input.area.country_code = 'tz';
  const result = run('cold_storage', {}, input);
  assert.equal(result.meta.per_capita.t, null);
  assert.ok(result.meta.service.components.every(item => item.annual_t === null));
  assert.ok(result.sites.every(site => site.dry.kwh_day === null));
  const record = {schema: 'enagis-production-input-v1', value: 150, unit: 'kg/person/year',
    source: 'Synthetic eligible produce report', source_date: '2026-11-10', licence: 'Fixture', label: 'ESTIMATED'};
  const supplied = run('cold_storage', {production_records: {produce_for_storage: record}}, input);
  assert.equal(supplied.meta.per_capita.t, .15);
  assert.equal(supplied.meta.service.coverage, 'user_reported');
});

test('service input validation rejects nonphysical ranges and version mismatches', () => {
  for (const overrides of [{cop: [0, 1, 2]}, {capture_share: [0, 1, 2]}, {run_hours: [2, 25, 26]}, {specific_energy: [30, 20, 10]}]) {
    assert.throws(() => run('cold_storage', {overrides}));
  }
  assert.throws(() => C.resolveScenario({recipe: 'milling', recipe_version: 'future'}));
  assert.throws(() => C.resolveScenario({recipe: 'milling', commodity: 'irish_potato'}));
  assert.throws(() => run('cooling', {overrides: {storage_days: [1, 2, 3]}}));
});

test('true zero service production is retained', () => {
  const record = {schema: 'enagis-production-input-v1', value: 0, unit: 'kg/person/year',
    source: 'Synthetic zero report', source_date: '2026-11-10', licence: 'Fixture', label: 'OBSERVED'};
  const result = run('milling', {production_records: {grain_for_milling: record}});
  assert.equal(result.meta.per_capita.t, 0);
  assert.ok(result.sites.every(site => site.dry.kwh_day.central === 0));
});

test('service capture cannot exceed the available catchment production', () => {
  const result = run('milling', {overrides: {capture_share: [1, 1, 1], type_mill: [2, 2, 2]}});
  for (const site of result.sites) {
    assert.ok(site.dry.throughput_t_day * 300 <= site.dry.production_t + 1e-9);
  }
});
