'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const C=require('../../live/js/config-v2.js');require('../../live/js/engine-v2.js');
const {makeFixture}=require('./fixture.cjs');
test('outside the training setting, siting is withheld before any feature scoring',()=>{
  const E=globalThis.enaEngineFactory({EnaConfig:C,EnaSitingModel:{model:{}},EnaSiting:{cells(){throw Error('Scoring must not run');}}});
  for(const country of ['ca','tz','zz',null]) {
    const input=makeFixture();input.area.country_code=country;
    const result=E.analyze(input,{model:'maize_milling',draws:10,per_capita_kg:{maize:200}});
    assert.equal(result.siting.status,'not_validated');assert.equal(result.siting.layer,undefined);
    assert(result.sites.every(s=>s.siting_pct==null));
    assert(result.sites.some(s=>s.dry.kwh_day),'supported demand calculations remain available');
    assert.match(result.steps.find(s=>s.id==='siting').detail,/Not validated here/);
  }
});
test('inside the declared training setting the existing siting branch is retained',()=>{
  let called=false;
  const E=globalThis.enaEngineFactory({EnaConfig:C,EnaSitingModel:{model:{}},EnaSiting:{cells(){called=true;return {};},apply(){return {status:'missing_inputs',missing:['fixture footprint sizes']};}}});
  const input=makeFixture();input.area.country_code='RW';
  E.analyze(input,{model:'maize_milling',draws:10});assert(called);
});
