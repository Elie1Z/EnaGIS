'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const C=require('../../live/js/config-v2.js'),E=require('../../live/js/engine-v2.js');
const {makeFixture}=require('./fixture.cjs');
const record=()=>({schema:'enagis-production-input-v1',value:200,unit:'kg/person/year',label:'ESTIMATED',source:'Synthetic agronomy report',source_date:'2026-10-01',licence:'Synthetic test fixture only'});
function analyze(value){return E.analyze(makeFixture({country:'zz'}),{model:'maize_milling',draws:10,production_records:{maize:value}});}
test('manual production keeps source, date, unit, label and reuse note',()=>{
  const r=analyze(record());assert.equal(r.meta.per_capita.t,.2);
  assert.equal(r.meta.per_capita.evidence.source,'Synthetic agronomy report');
  assert.equal(r.meta.per_capita.evidence.label,'ESTIMATED');
  assert.equal(r.meta.per_capita.evidence.source_date,'2026-10-01');
  assert.equal(r.meta.per_capita.evidence.verification,'user_supplied_not_independently_verified');
  assert.equal(r.meta.per_capita.evidence.licence,record().licence);
});
test('missing evidence and malformed values fail instead of borrowing defaults',()=>{
  for(const patch of [{source:''},{source_date:'2026-02-30'},{source_date:'2026-10'},{licence:''},{label:'PREDICTED'},
    {value:NaN},{value:Infinity},{value:-1},{value:null},{value:'200'},{unit:'tonnes/year'},{schema:'future'}]) {
    assert.throws(()=>analyze({...record(),...patch}));
  }
  assert.throws(()=>analyze(null));
  assert.throws(()=>E.analyze(makeFixture(),{model:'maize_milling',production_records:{maize:{value:200}}}));
});
test('zero is preserved, both in manual records and district statistics',()=>{
  assert.equal(analyze({...record(),value:0}).meta.per_capita.t,0);
  const input=makeFixture();input.area.name='Nyamasheke District';input.area.display_name='Nyamasheke District, Rwanda';
  const r=E.analyze(input,{model:'potato_storage',draws:10});
  assert.equal(r.meta.per_capita.t,0);assert.equal(r.meta.per_capita.evidence.district,'Nyamasheke');
});
test('legacy numeric entries keep their value but are not promoted to OBSERVED',()=>{
  const r=E.analyze(makeFixture({country:'zz'}),{model:'maize_milling',draws:10,per_capita_kg:{maize:200}});
  assert.equal(r.meta.per_capita.t,.2);assert.equal(r.meta.per_capita.evidence.label,'INFERRED');
  assert.match(r.meta.per_capita.evidence.source,/missing/);
  for(const value of [-1,NaN,Infinity,'bad',true,'   ']) assert.throws(()=>E.analyze(makeFixture(),{model:'maize_milling',per_capita_kg:{maize:value}}));
});
test('conflicting old and new inputs cannot silently replace each other',()=>{
  assert.throws(()=>E.analyze(makeFixture(),{model:'maize_milling',production_records:{maize:record()},per_capita_kg:{maize:50}}),/Conflicting/);
});
