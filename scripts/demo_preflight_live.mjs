// Offline acceptance path for the Nyabihu potato snapshot. No public services, no synthetic observations.
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {serve,ROOT}=require('../live/tools/local-server.cjs');
const {ranking}=require('../live/tools/hero-contract.cjs');
const out=path.resolve(process.argv[2]||'outputs/demo-preflight-live');fs.mkdirSync(out,{recursive:true});
const {server,base}=await serve();
const browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const ctx=await browser.newContext({viewport:{width:1600,height:1000}}),page=await ctx.newPage(),errors=[],requests=[];
page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url());});
await ctx.route('https://**/*',r=>r.abort());
const checks=[];const check=(name,ok)=>{assert.ok(ok,name);checks.push({name,pass:true});console.log('PASS',name);};
try{
  await page.goto(base+'/live/index.html?hero=offline');
  await page.waitForFunction(()=>window.EnaApp&&EnaApp.map().loaded());
  await page.screenshot({path:path.join(out,'00-start.png')});
  check('all four chains and district exploration retained',await page.locator('#model option').count()===4&&await page.locator('[data-example]').count()>=6);
  await ctx.setOffline(true);const before=requests.length;
  await page.click('#hero-replay');await page.waitForFunction(()=>EnaApp.state().phase==='results',{},{timeout:90000});
  if(requests.length!==before)console.log('Replay requests:',requests.slice(before));
  check('offline snapshot makes zero requests',requests.length===before);
  const actual=await page.evaluate(()=>{const r=EnaApp.state().result;return {sites:r.sites,meta:r.meta};});
  fs.writeFileSync(path.join(out,'browser-ranking.json'),JSON.stringify(ranking(actual)));
  const expectedRanking=JSON.parse(fs.readFileSync(path.join(ROOT,'data/rwanda/hero/nyabihu-potato/expected.json'),'utf8'));
  const browserRanking=ranking(actual);
  // Chrome and Node ship different V8/libm versions: allow only last-bit floating arithmetic
  // differences in continuous measures. IDs, order, ranks, tiers and draw counts remain exact.
  const same=(a,b,key='')=>typeof a==='number'&&typeof b==='number' ?
    (['rank','seed','draws'].includes(key)?a===b:Math.abs(a-b)<=1e-12*Math.max(1,Math.abs(b))) :
    a&&b&&typeof a==='object'&&typeof b==='object' ? Object.keys(a).length===Object.keys(b).length&&Object.keys(a).every(k=>same(a[k],b[k],k)) : a===b;
  check('browser agrees on frozen order, ranks and tiers; numerical difference <= 1e-12 relative',same(browserRanking,expectedRanking));
  await page.click('#hero-provenance');check('provenance contains release, hashes and engine',/2026-09-23.1/.test(await page.locator('#panel').innerText())&&await page.locator('#panel .hash').count()>5);
  await page.screenshot({path:path.join(out,'01-provenance.png')});await page.click('[data-close-panel]');
  await page.click('#hero-why');check('why case numbers retain evidence labels',/ESTIMATED/.test(await page.locator('#panel').innerText())&&/DOCUMENTED/.test(await page.locator('#panel').innerText()));await page.screenshot({path:path.join(out,'02-why.png')});await page.click('[data-close-panel]');
  const visibleWords=async pg=>(await pg.locator('body').innerText()).match(/(demo|hero|frozen|presenter|guided)/gi)||[];
  check('page shows no presentation wording or step controls',(await visibleWords(page)).length===0&&await page.locator('#hero-stepper').isHidden());
  const expected=['harvest','first','first','sure','access','likely'];
  for(let i=0;i<6;i++){
    await page.locator('#drawer h2').first().click();await page.keyboard.press(i%2?'ArrowRight':'PageDown');
    await page.waitForFunction(i=>document.body.dataset.heroStep===String(i),i);
    const s=await page.evaluate(()=>({lens:EnaApp.state().lens,season:EnaApp.state().season,selected:EnaApp.state().selected,cand:EnaApp.state().cand}));
    check('keyboard view '+(i+1),s.lens===expected[i]&&s.season===(i===4?'rainy':'dry')&&(i===5?s.cand===1:i<2?s.selected===null:!!s.selected)&&await page.locator('#hero-stepper').isHidden()&&(await visibleWords(page)).length===0);
    await page.waitForFunction(()=>!EnaApp.map().isMoving());
    await page.screenshot({path:path.join(out,`step-${i+1}.png`)});
  }
  await page.evaluate(()=>EnaHeroUI.go(2));
  check('rank card has linked numbers and honest zero check counts',await page.locator('#sheet [data-assumption]').count()>10&&/DESK-CHECKED 0 · PHONE-CHECKED 0/.test(await page.locator('#sheet').innerText()));
  await page.locator('#sheet [data-assumption="energy"]').first().click();check('number opens its evidence row',await page.locator('#assumption-energy').count()===1);await page.screenshot({path:path.join(out,'03-assumptions.png')});await page.click('[data-close-panel]');
  await page.click('#hero-sensitivity');check('tornado has residual and ranking finding',await page.locator('.hero-driver').count()>=10&&/What would change the ranking/.test(await page.locator('#panel').innerText()));await page.screenshot({path:path.join(out,'04-sensitivity.png')});await page.click('[data-close-panel]');
  await page.click('#hero-checks');check('15 real frozen targets and no fabricated calls',await page.locator('#hero-target option').count()===15&&/0 completed calls/.test(await page.locator('#panel').innerText()));
  await page.click('[data-hero-form="phone"]');check('phone form does not prefill confirmations',await page.locator('[name="potato_activity"]').inputValue()==='unclear');
  await page.fill('[name="reviewer"]','SYNTHETIC-TEST');await page.selectOption('[name="status"]','completed');
  await page.selectOption('[name="consent"]','yes');await page.selectOption('[name="direct_knowledge"]','yes');await page.selectOption('[name="exact_site"]','yes');
  await page.fill('[name="season"]','SYNTHETIC 2026 A');await page.selectOption('[name="potato_activity"]','yes');await page.fill('[name="tonnes"]','2');await page.click('#hero-review-form button[type="submit"]');
  check('local form derives activity outcome and updates card count',await page.evaluate(()=>JSON.parse(localStorage.getItem('enagis-hero-verification-v1')).phone[0].outcome==='CONFIRMED_ACTIVITY')&&/PHONE-CHECKED 1/.test(await page.locator('#sheet').innerText()));
  // Test data live only in this disposable browser profile. Remove before screenshots/final checks.
  await page.evaluate(()=>localStorage.removeItem('enagis-hero-verification-v1'));await page.click('[data-close-panel]');
  await page.evaluate(()=>EnaHeroUI.go(2));
  await page.keyboard.press('Escape');await page.click('[data-lens="energy"]');check('leaving the view sequence keeps free exploration',await page.evaluate(()=>document.body.dataset.heroStep==='-1')&&await page.evaluate(()=>EnaApp.state().lens==='energy'));
  check('complete view sequence stayed offline',requests.length===before);
  // Saved JSON fallback from a real local input, with the same paper map.
  await page.evaluate(async pkg=>{await EnaApp.openPackage({text:async()=>JSON.stringify(pkg)});},JSON.parse(fs.readFileSync(path.join(ROOT,'data/rwanda/hero/nyabihu-potato/saved-analysis.json'),'utf8')));
  await page.waitForFunction(()=>EnaApp.state().phase==='results');check('saved analysis fallback retains ranking',await page.evaluate(()=>EnaApp.state().result.sites.some(s=>s.name==='Kora Market'&&s.dry.rank===1)));
  check('zero console errors',errors.length===0);
  fs.copyFileSync(path.join(ROOT,'data/rwanda/hero/nyabihu-potato/saved-analysis.json'),path.join(out,'saved-analysis.json'));
  // file:// replay also works without a local server.
  const filePage=await ctx.newPage();await filePage.goto(new URL('../live/index.html',import.meta.url).href+'?hero=offline');await filePage.click('#hero-replay');await filePage.waitForFunction(()=>window.EnaApp&&EnaApp.state().phase==='results',{},{timeout:90000});check('file URL offline replay',await filePage.locator('.site-row').count()===10);
  await filePage.close();
  // Rehearsal-only controls appear only when the presenter opens ?presenter=1.
  const rehearsal=await ctx.newPage();await rehearsal.goto(new URL('../live/index.html',import.meta.url).href+'?hero=offline&presenter=1');await rehearsal.click('#hero-replay');await rehearsal.waitForFunction(()=>window.EnaApp&&EnaApp.state().phase==='results',{},{timeout:90000});
  await rehearsal.click('[data-hero-step="0"]');check('presenter=1 shows rehearsal controls and captions',await rehearsal.locator('#hero-stepper').isVisible()&&(await rehearsal.locator('#hero-caption').innerText()).length>25);
  await rehearsal.close();
  const shots=['00-start','02-why','01-provenance','step-1','step-2','step-3','03-assumptions','step-4','04-sensitivity','step-5','step-6'];
  fs.writeFileSync(path.join(out,'index.html'),`<!doctype html><html lang="en"><meta charset="utf-8"><title>Nyabihu offline backup deck</title><style>body{margin:0;background:#132c38;color:white;font:16px system-ui}header{padding:20px;position:sticky;top:0;background:#132c38}section{margin:25px auto;max-width:1440px}img{width:100%}a{color:#8ce1bb}@media print{section{break-after:page}header{position:static}}</style><header><strong>Nyabihu potato cold storage — screenshot backup</strong><p>Frozen 10 October 2026 · ESTIMATED screening results · real human checks 0 · <a href="saved-analysis.json">Saved analysis</a></p><p>Screenshot backup. The screen recording on the presenting laptop is still a human task.</p></header>${shots.map(s=>`<section><h2>${s}</h2><img src="${s}.png" alt="${s}"></section>`).join('')}</html>`);
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({status:'PASS',checks,errors,external_requests:requests.filter(u=>u.startsWith('https:'))},null,2));
}finally{await browser.close();server.close();}
