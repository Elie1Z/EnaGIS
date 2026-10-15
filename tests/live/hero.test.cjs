'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm');
const H=require('../../live/tools/hero-contract.cjs'), R=require('../../live/js/hero-report.js'),V=require('../../live/js/hero-verification.js');
const {makeFixture}=require('./fixture.cjs');
test('hero snapshot has complete inputs, hashed sources and byte-identical ranking twice',()=>{
  H.verifyManifest();const E=H.engine(),input=H.read('input.json');H.validateInput(input);
  const a=JSON.stringify(H.ranking(E.analyze(input,H.options))),b=JSON.stringify(H.ranking(E.analyze(input,H.options)));
  assert.equal(a,b);assert.equal(a,JSON.stringify(H.read('expected.json')));
});
test('optional reporting leaves every scientific result unchanged',()=>{
  const E=H.engine(),input=makeFixture();const plain=E.analyze(input,H.options),traced=E.analyze(input,{...H.options,trace:true});
  assert.deepEqual(H.ranking(plain),H.ranking(traced));assert.equal(traced.simulation_trace.seasons.dry.length,300);
  assert.equal(traced.simulation_trace.seasons.rainy.length,300);
  assert.ok(traced.ranking_sensitivity.checks.length>0);
});
test('variance allocation identifies a known signal, keeps contributions nonnegative and includes residual',()=>{
  const x=Array.from({length:300},(_,i)=>Math.sin(i)),z=x.map((_,i)=>Math.cos(i*1.73));
  const r=R.varianceContributions({signal:x,irrelevant:z},x.map(v=>4*v+8));
  assert.equal(r.rows[0].key,'signal');assert.ok(r.rows[0].fraction>.999);
  assert.ok(r.rows.every(v=>v.fraction>=0));assert.ok(Math.abs(r.rows.reduce((s,v)=>s+v.fraction,0)+r.residual-1)<1e-9);
  const real=H.read('sensitivity.json');assert.ok(real.variance.rows.length>=10);
  assert.ok(Math.abs(real.variance.rows.reduce((s,v)=>s+v.fraction,0)+real.variance.residual-1)<1e-8);
  assert.ok(!real.variance.rows.some(r=>r.key==='run_hours'));
});
test('browser bundle matches frozen input, manifest, expected options and assumption configuration',()=>{
  const root={};vm.runInNewContext(fs.readFileSync(path.join(H.ROOT,'live/hero/nyabihu-potato.js'),'utf8'),{window:root});
  const raw=zlib.gunzipSync(Buffer.from(root.ENA_HERO_BUNDLE.data,'base64'));assert.equal(H.sha(raw),root.ENA_HERO_BUNDLE.sha256);
  const b=JSON.parse(raw);assert.deepEqual(b.pkg.input,H.read('input.json'));assert.deepEqual(b.manifest,H.read('MANIFEST.json'));assert.deepEqual(b.pkg.options,H.options);
  const C=require('../../live/js/config.js');for(const [k,v] of Object.entries({...C.MODELS.potato_storage.params,...C.SHARED}))assert.deepEqual(b.assumptions.rows.find(r=>r.id===k).range,v.range);
  assert.equal(b.assumptions.rows.find(r=>r.id==='loss_rate').label,'UNKNOWN');assert.equal(b.targets.length,15);
});
test('verification never counts empty templates, invented confirmations, pre-protocol calls or wrong hashes',()=>{
  const p=JSON.parse(fs.readFileSync(path.join(H.DIR,'../verification-protocol.json'),'utf8'));
  const empty={desk:[],phone:[]};assert.equal(V.counts({id:'test',documented:false,predicted:true},empty,p).phone,0);
  const r={site_id:'test',reviewer:'test-alias',checked_at:new Date(Date.parse(p.frozen_at)+1000).toISOString(),protocol_sha256:p.sha256,status:'completed',consent:'yes',direct_knowledge:'yes',exact_site:'yes',season:'2026 A',potato_activity:'yes',tonnes:'2',outcome:'CONFIRMED_ACTIVITY'};
  assert.ok(V.validatePhone(r,p));assert.ok(!V.validatePhone({...r,checked_at:'2000-01-01'},p));assert.ok(!V.validatePhone({...r,protocol_sha256:'wrong'},p));
  assert.equal(V.outcome({...r,tonnes:''}),'INCONCLUSIVE');assert.equal(V.outcome({...r,tonnes:'0'}),'REJECTED_ACTIVITY');assert.equal(V.outcome({...r,status:'attempt'}),'ATTEMPT');
  assert.ok(!V.validatePhone({...r,tonnes:''},p));assert.ok(!V.validateDesk({site_id:'test'}));
  assert.equal(p.sha256,H.sha(fs.readFileSync(path.join(H.ROOT,'docs/hero-verification-protocol.md'))));
});
test('CSV round-trip preserves quoted multiline evidence notes and rejects malformed records',()=>{
  const row=Object.fromEntries(V.DESK.map(k=>[k,'']));Object.assign(row,{site_id:'node/1',reviewer:'alias',notes:'line 1, "quote"\nline 2'});
  const parsed=V.parseCSV(V.csv(V.DESK,[row]));assert.deepEqual(parsed.rows,[row]);assert.deepEqual(parsed.header,V.DESK);
  assert.throws(()=>V.parseCSV('a,a\n1,2'));assert.throws(()=>V.parseCSV('a,b\n1'));assert.throws(()=>V.parseCSV('a\n"unclosed'));
});
test('page wording is the product, not the presentation: no demo/hero/frozen labels and no default step bar',()=>{
  const words=/\b(demo|hero|frozen|presenter|guided)\b/i,text=h=>h.replace(/<[^>]*>/g,' ');
  const load=search=>{const root={location:{search},EnaHeroVerification:{}};vm.runInNewContext(fs.readFileSync(path.join(H.ROOT,'live/js/hero-ui.js'),'utf8'),{window:root,URLSearchParams});return root.EnaHeroUI;};
  const U=load('');assert.doesNotMatch(text(U.introHTML()),words);
  for(const s of U.steps)assert.doesNotMatch(s.title+' '+s.caption,words);
  const html=fs.readFileSync(path.join(H.ROOT,'live/index.html'),'utf8');
  assert.match(html,/<nav id="hero-stepper"[^>]*hidden>/);assert.doesNotMatch(text(html.replace(/<script[\s\S]*?<\/script>/g,'')),words);
  // Button labels, headings and status/toast strings in the app and the snapshot panels.
  for(const f of ['live/js/app.js','live/js/hero-ui.js']){
    const src=fs.readFileSync(path.join(H.ROOT,f),'utf8');
    const visible=[...src.matchAll(/>([^<>${}\n'"();=]*[A-Za-z][^<>${}\n'"();=]*)</g),...src.matchAll(/\b(?:status|toast)\(\s*[`"]([^`"]*)/g)].map(m=>m[1]);
    for(const v of visible)assert.doesNotMatch(v,words,f+': '+v);
  }
});
test('GeoJSON export is current, labelled, coordinate-ordered and honest about verification counts',()=>{
  const X=require('../../live/tools/export-hero-geojson.cjs'),g=JSON.parse(fs.readFileSync(X.OUT,'utf8'));
  const result=H.engine().analyze(H.read('input.json'),H.options);
  assert.equal(JSON.stringify(X.build(result),null,1)+'\n',fs.readFileSync(X.OUT,'utf8'));
  const ranked=g.features.filter(f=>f.properties.feature_kind==='ranked_site'),looks=g.features.filter(f=>f.properties.feature_kind==='siting_lookalike');
  assert.equal(ranked.length,result.sites.length);assert.equal(looks.length,5);
  assert.deepEqual(ranked.map(f=>f.properties.rank_dry),ranked.map((_,i)=>i+1));
  const labels=new Set(['OBSERVED','INFERRED','ESTIMATED','PREDICTED','UNKNOWN']);
  for(const f of g.features){const [lon,lat]=f.geometry.coordinates;assert.ok(lon>29&&lon<30&&lat>-2&&lat<-1.3,'lon,lat order');
    for(const [k,v] of Object.entries(f.properties))if(k.endsWith('_evidence'))assert.ok(labels.has(v),k+'='+v);}
  const targets=g.features.filter(f=>f.properties.verification_target);assert.equal(targets.length,15);
  const logged=['desk-check.csv','phone-log.csv'].map(n=>V.parseCSV(fs.readFileSync(path.join(H.ROOT,'data/rwanda/hero',n),'utf8')).rows.length);
  if(logged.every(n=>n===0))assert.ok(targets.every(f=>f.properties.desk_checked===0&&f.properties.phone_checked===0&&f.properties.field_visits===0));
  assert.doesNotMatch(JSON.stringify(g),/validated/i);
});
