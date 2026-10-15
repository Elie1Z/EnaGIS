/* First freeze: node live/tools/build-hero.cjs --freeze
 * Subsequent presentation rebuild: node live/tools/build-hero.cjs
 * Expected ranking is never silently overwritten. */
'use strict';
const fs = require('node:fs'), path = require('node:path'), zlib = require('node:zlib'), assert = require('node:assert/strict');
const {ROOT,DIR,sha,read,engine,options,ranking,validateInput} = require('./hero-contract.cjs');
const V = require('../js/hero-verification.js'), HR = require('../js/hero-report.js');
const input = read('input.json'); validateInput(input);
const result = engine().analyze(input,{...options,trace:true});
const expected = ranking(result), expectation = path.join(DIR,'expected.json');
if (!fs.existsSync(expectation)) {
  if (!process.argv.includes('--freeze')) throw new Error('First freeze requires --freeze');
  fs.writeFileSync(expectation,JSON.stringify(expected));
} else assert.ok(JSON.stringify(expected) === JSON.stringify(read('expected.json')),'Ranking differs; review before any new freeze');
const write = (name,value) => fs.writeFileSync(path.join(DIR,name),JSON.stringify(value,null,2));
const report = HR.report(result); report.ranking_sensitivity = result.ranking_sensitivity;
write('sensitivity.json',report);
write('production.json',{label:'ESTIMATED',source:'NISR 2024 Season A area × yield shares scaled to annual national total; census 2022',
  crs:'EPSG:4326', district:'Nyabihu', row:require('../../data/rwanda/district_production_2024.json').Nyabihu,
  config:require('../js/config.js').COUNTRIES.RW.districts.Nyabihu});
const csvLines = fs.readFileSync(path.join(ROOT,'data/rwanda/district_production_2024.csv'),'utf8').trim().split(/\r?\n/);
fs.writeFileSync(path.join(DIR,'production-row.csv'),csvLines[0]+'\n'+csvLines.find(l=>l.startsWith('Nyabihu,'))+'\n');
const sum = require('../../data/rwanda/district_summaries.json'), districts = Object.values(sum);
const context = {label:'DOCUMENTED',date:'2026-10-10',source:'data/rwanda/district_summaries.json',
  footprints:districts.reduce((n,d)=>n+d.buildings,0), documented:districts.reduce((n,d)=>n+(d.documented_sites ?? d.models.potato_storage.documented),0),
  note:'Harvested source records; not a census of cold rooms. Different observation units, not a numerical capacity gap.'};
write('national-context.json',context);
const protocol = JSON.parse(fs.readFileSync(path.join(DIR,'../verification-protocol.json'),'utf8'));
assert.equal(protocol.sha256,sha(fs.readFileSync(path.join(ROOT,'docs/hero-verification-protocol.md'))));
const targets = result.sites.filter(s=>s.dry.rank && s.dry.rank<=10).sort((a,b)=>a.dry.rank-b.dry.rank).map(s=>({id:s.id,name:s.name,rank:s.dry.rank,lon:s.lon,lat:s.lat,documented:s.documented,predicted:s.siting_pct!==null,kind:'ranked'}))
  .concat((result.siting?.candidates || []).slice(0,5).map(s=>({id:'lookalike-'+s.rank,name:'Look-alike ?'+s.rank,rank:s.rank,lon:s.lon,lat:s.lat,documented:false,predicted:true,kind:'look-alike'})));
write('verification-targets.json',targets);
const kit = path.join(DIR,'../phone-kit'); fs.mkdirSync(kit,{recursive:true});
const esc = s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const question = 'At this exact location, did your organisation aggregate or store potatoes during the most recent completed potato season, and how many tonnes did it handle in that season?';
targets.forEach((s,i)=>{
  const stem=String(i+1).padStart(2,'0'), row=Object.fromEntries(V.PHONE.map(k=>[k,''])); row.site_id=s.id; row.protocol_sha256=protocol.sha256;
  // Templates are not observations. Rerunning must not overwrite a human-completed local file.
  if (!fs.existsSync(path.join(kit,stem+'.csv'))) fs.writeFileSync(path.join(kit,stem+'.csv'),V.csv(V.PHONE,[row]));
  fs.writeFileSync(path.join(kit,stem+'.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><title>${esc(s.name)} — phone check</title><style>body{font:14px/1.45 system-ui;max-width:760px;margin:35px auto;color:#142c37}h1{font-size:25px}h2{font-size:17px}p{margin:12px 0}small{overflow-wrap:anywhere}table{width:100%;border-collapse:collapse}td{border-bottom:1px solid #ccc;padding:9px}@page{size:A4;margin:16mm}.logo{display:block;margin:14px 0 10px}@media print{body{margin:0}button{display:none}}</style><button onclick="print()">Print one page</button><img class="logo" src="../../../../live/assets/brand/enagis-wordmark.png" alt="EnaGIS" height="34"><h1>${esc(s.name)}</h1><p>${s.kind==='ranked'?'ESTIMATED dry rank':'PREDICTED look-alike'} ${s.rank} · ${s.documented?'DOCUMENTED map record':'No documented facility'}<br>EPSG:4326 longitude ${s.lon}, latitude ${s.lat}<br>Stable target: ${esc(s.id)}</p><h2>Ask one question</h2><p><strong>${question}</strong></p><h2>English introduction</h2><p>Hello, I am [name] from Team Dynamis. We are checking a map lead for an agricultural energy study. We are not offering funding. May I record a brief anonymised answer? Are you directly familiar with operations at this exact location?</p><h2>Kinyarwanda — Elie to review wording</h2><p>Muraho. Nitwa [izina], ndi mu itsinda Dynamis. Turagenzura amakuru ari ku ikarita; ntabwo dusezeranya inkunga. Mwatwemerera kwandika igisubizo tutagaragaje amazina yanyu? Muzi neza ibikorwa bikorerwa aha hantu? Mu gihembwe giheruka kurangira, kuri aha hantu mwakusanyije cyangwa mwabitse ibirayi? Byari toni zingahe? Ni ikihe gihembwe muvuga?</p><h2>Decision fixed before calls</h2><p>Confirmed activity: consent + direct knowledge + exact site + potato aggregation/storage + named completed season + reported volume &gt;0 tonnes. Explicit no activity or zero tonnes: rejected. Unknown volume/location/knowledge: inconclusive. No answer: attempt only. This does not confirm refrigeration, capacity or energy demand.</p><table><tr><td>Reviewer alias / UTC date</td><td>__________________________</td></tr><tr><td>Consent / direct knowledge / exact site</td><td>__________________________</td></tr><tr><td>Season / original amount and unit / tonnes</td><td>__________________________</td></tr><tr><td>Outcome, including misses</td><td>__________________________</td></tr></table><p>Keep names, phone numbers and raw notes in data/validation_private/hero/. Public copies contain anonymised outcomes only. Phone/site visits completed initially: 0.</p><small>Protocol frozen ${protocol.frozen_at}<br>SHA-256 ${protocol.sha256}</small></html>`);
});
const pkg={format:'enagis-live-package-v1',saved_at:input.retrieved_at,synthetic:false,options,input};
write('saved-analysis.json',pkg);
const runtimeFiles=['live/js/config.js','live/js/engine.js','live/js/siting.js','live/js/siting-model.js','live/js/hero-report.js','live/js/hero-verification.js'];
const dirFiles=fs.readdirSync(DIR).filter(n=>n.endsWith('.json')||n.endsWith('.csv')).filter(n=>n!=='MANIFEST.json');
const files=dirFiles.map(n=>'data/rwanda/hero/nyabihu-potato/'+n).concat(runtimeFiles,
  ['data/rwanda/hero/verification-protocol.json','docs/hero-verification-protocol.md','docs/hero-verification-protocol.sha256','data/rwanda/district_summaries.json','docs/spec/phase4r-protocol.md','docs/spec/phase4r-protocol.sha256']);
const manifest={schema:'enagis-hero-manifest-v1',frozen_at:input.retrieved_at,engine_version:'live-v1 + optional-reporting-v1',
  crs:'EPSG:4326',coordinate_order:'longitude, latitude',seed:options.seed,draws:options.draws,release:'2026-09-23.1',
  evidence:'ESTIMATED ranking; DOCUMENTED source records; field visits 0',sources:input.sources,
  files:files.map(file=>({path:file,bytes:fs.statSync(path.join(ROOT,file)).size,sha256:sha(fs.readFileSync(path.join(ROOT,file)))}))};
write('MANIFEST.json',manifest);
const bundle={pkg,manifest,assumptions:read('assumptions.json'),report,targets,protocol,context};
const bytes=Buffer.from(JSON.stringify(bundle)), compressed=zlib.gzipSync(bytes,{level:9});
const bundleDir=path.join(ROOT,'live/hero');fs.mkdirSync(bundleDir,{recursive:true});
fs.writeFileSync(path.join(bundleDir,'nyabihu-potato.js'),`/* Generated local replay bundle. Rebuild with live/tools/build-hero.cjs. */\nwindow.ENA_HERO_BUNDLE=${JSON.stringify({sha256:sha(bytes),encoding:'gzip-base64',data:compressed.toString('base64')})};\n`);
console.log('Frozen hero:',targets.length,'targets;',result.sites.length,'sites;',compressed.length,'compressed bytes;',result.sites.find(s=>s.dry.rank===1).name);
