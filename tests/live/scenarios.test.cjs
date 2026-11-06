'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm');
const C=require('../../live/js/config-v2.js'),E=require('../../live/js/engine-v2.js');
const {makeFixture}=require('./fixture.cjs');

test('crop-first and energy-use-first resolve the same declared recipe',()=>{
  const a=C.resolveScenario({commodity:'maize',process:'milling'}),b=C.resolveScenario({recipe:'maize_milling'});
  assert.deepEqual(a,b);assert.equal(a.evidence_status,'legacy_screening');
  assert.equal(C.MODELS.potato_storage.params.cp_kj_per_kg_k,C.COMMODITIES.irish_potato.properties.cp_kj_per_kg_k);
  assert.equal(C.MODELS.potato_storage.compute,C.PROCESSES.refrigerated_storage.compute);
});
test('unsupported combinations, mismatches and versions fail before calculating',()=>{
  for(const spec of [{commodity:'maize',process:'liquid_cooling'},{recipe:'tomato_storage'},{recipe:'toString'},
    {recipe:'milk_cooling',commodity:'maize'},{recipe:'milk_cooling',process:'milling'},
    {recipe:'milk_cooling',registry_version:'future'},{recipe:'milk_cooling',recipe_version:'future'}]) assert.throws(()=>C.resolveScenario(spec));
  assert.throws(()=>E.analyze(makeFixture(),{model:'potato_storage',scenario:{recipe:'maize_milling'}}),/disagree/);
});
test('versioned scenario and legacy model calculate identical results',()=>{
  for(const id of Object.keys(C.RECIPES)) {
    const old=E.analyze(makeFixture(),{model:id,draws:30}),next=E.analyze(makeFixture(),{scenario:C.resolveScenario({recipe:id}),draws:30});
    assert.equal(next.meta.scenario.recipe,id);delete next.meta.scenario;old.meta.elapsed_ms=next.meta.elapsed_ms=0;
    assert.deepEqual(next,old);
  }
});
test('self-contained worker factory resolves registries without a new dependency',()=>{
  const worker=vm.runInNewContext(`(${globalThis.enaConfigFactory.toString()})()`);
  assert.equal(worker.resolveScenario({recipe:'milk_cooling'}).process,'liquid_cooling');
  const q=Object.fromEntries(Object.entries(C.MODELS.milk_cooling.params).map(([k,v])=>[k,v.range[1]]));
  assert.equal(worker.MODELS.milk_cooling.compute(100,q).kwh_day,C.MODELS.milk_cooling.compute(100,q).kwh_day);
});
test('new recipes cannot inherit the legacy review exception',()=>{
  const recipe=structuredClone(C.RECIPES.maize_milling);
  assert.throws(()=>C.compileRecipe(recipe),/review/);
  recipe.evidence_status='reviewed';recipe.review={reviewer:'Test reviewer (fixture only)',date:'2026-11-06'};
  assert.throws(()=>C.compileRecipe(recipe),/sourced evidence/);
  Object.values(recipe.params).forEach(p=>Object.assign(p,{source:'Synthetic fixture, not a scientific source',source_date:'2026-11-06',licence:'test only'}));
  recipe.params.run_hours.unit='kWh';assert.throws(()=>C.compileRecipe(recipe),/unit/);
  recipe.params.run_hours.unit='h/day';recipe.params.run_hours.range=[0,8,10];assert.throws(()=>C.compileRecipe(recipe),/domain/);
});
test('runtime edits cannot mutate the registered recipe definitions',()=>{
  assert.throws(()=>{C.RECIPES.maize_milling.params.run_hours.range[0]=0;},TypeError);
});
