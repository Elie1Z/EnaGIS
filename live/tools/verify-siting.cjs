/* Read-only frozen-result check. No fitting, changed labels or overwritten registered artifacts. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const {ROOT,sha}=require('./hero-contract.cjs');
const frozen=JSON.parse(fs.readFileSync(path.join(ROOT,'configs/hero-frozen-artifacts.json'),'utf8'));
for(const f of frozen)assert.equal(sha(fs.readFileSync(path.join(ROOT,f.path))),f.sha256,'Frozen artifact changed: '+f.path);
const ev=JSON.parse(fs.readFileSync(path.join(ROOT,'docs/audits/phase4r-evaluation.json'),'utf8'));
assert.equal(ev.protocol.sha256,sha(fs.readFileSync(path.join(ROOT,'docs/spec/phase4r-protocol.md'))));
assert.equal(ev.input.sha256,sha(fs.readFileSync(path.join(ROOT,'data/rwanda/siting_cells.csv'))));
assert.equal(ev.verdict,'KEEP');assert.equal(Math.round(ev.evaluation.margin[0].point*1000)/10,23.9);
const root={};vm.runInNewContext(fs.readFileSync(path.join(ROOT,'live/js/siting-model.js'),'utf8'),{window:root});
assert.equal(root.EnaSitingModel.verdict,ev.verdict);assert.equal(JSON.stringify(root.EnaSitingModel.model),JSON.stringify(ev.model));
console.log('PASS live-siting: frozen Rwanda KEEP +23.9, protocol/input/model hashes and Canadian result unchanged; no retraining.');
