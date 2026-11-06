/* Browser integration with synthetic inputs; no external datasets are fetched. */
'use strict';
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright'),{makeSynthetic}=require('../../live/js/synthetic.js');
const root=path.resolve(__dirname,'../../live'),out=path.resolve(__dirname,'../../outputs/scenario-foundation');
fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname.replace(/\/$/,'/index.html'));
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404);return res.end();}
  res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
let count=0;
function check(name,condition){assert(condition,name);count++;console.log('PASS '+name);}
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
  try {
    browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH});
    const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',r=>r.request().url().includes('127.0.0.1')?r.continue():r.abort());
    await page.goto('http://127.0.0.1:'+server.address().port);
    await page.waitForFunction(()=>!!window.EnaApp);
    const legacy={format:'enagis-live-package-v1',input:makeSynthetic(7),options:{model:'maize_milling'},synthetic:true};
    await page.evaluate(pkg=>EnaApp.openPackage(new File([JSON.stringify(pkg)],'fixture.json')),legacy);
    await page.waitForFunction(()=>EnaApp.state().phase==='results');
    check('legacy files open through the versioned registry',await page.evaluate(()=>EnaApp.state().result.meta.scenario.recipe==='maize_milling'));
    const original=await page.evaluate(()=>EnaApp.state().result.meta.per_capita.t);
    await page.click('#assumptions');await page.fill('#percap','200');await page.click('#apply-assumptions');
    check('missing source is blocked in the interface',(await page.locator('#toast').innerText()).includes('source'));
    check('invalid form does not change production',await page.evaluate(()=>EnaApp.state().result.meta.per_capita.t)===original);
    await page.fill('#production-source','Synthetic report <strong>literal</strong>');
    await page.fill('#production-date','2026-10-01');await page.fill('#production-licence','Synthetic fixture only');
    await page.selectOption('#production-label','ESTIMATED');await page.click('#apply-assumptions');
    await page.waitForFunction(()=>EnaApp.state().result.meta.per_capita.t===.2);
    check('worker keeps the source evidence',await page.evaluate(()=>EnaApp.engine().worker&&EnaApp.state().result.meta.per_capita.evidence.source_date==='2026-10-01'));
    await page.locator('#panel').evaluate(el=>el.scrollTop=0);
    await page.screenshot({path:path.join(out,'production-evidence-desktop.png')});
    await page.click('[data-close-panel]');await page.click('#sources');
    check('sources view contains user evidence as text',(await page.locator('#panel').innerText()).includes('<strong>literal</strong>'));
    check('source strings are not injected as markup',await page.locator('#panel strong').allTextContents().then(texts=>!texts.includes('literal')));
    await page.click('[data-close-panel]');
    const [saved]=await Promise.all([page.waitForEvent('download'),page.click('#save')]);
    const savedPath=path.join(out,'provenance-roundtrip.json');await saved.saveAs(savedPath);
    const pkg=JSON.parse(fs.readFileSync(savedPath,'utf8'));
    check('new saves use version 2 and retain production evidence',pkg.format==='enagis-live-package-v2'&&pkg.options.production_records.maize.source_date==='2026-10-01');
    check('new saves retain recipe and registry versions',pkg.options.scenario.recipe_version==='legacy-v1'&&pkg.options.scenario.registry_version==='enagis-scenarios-v1');
    const [csv]=await Promise.all([page.waitForEvent('download'),page.click('#export-csv')]);
    const csvPath=path.join(out,'provenance.csv');await csv.saveAs(csvPath);
    const csvText=fs.readFileSync(csvPath,'utf8');
    check('CSV carries provenance fields and source text',csvText.includes('production_source_date')&&csvText.includes('Synthetic report <strong>literal</strong>'));
    await page.evaluate(()=>EnaLanding.show());
    await page.evaluate(pkg=>EnaApp.openPackage(new File([JSON.stringify(pkg)],'roundtrip.json')),pkg);
    await page.waitForFunction(()=>EnaApp.state().phase==='results'&&EnaApp.state().result?.meta.per_capita.t===.2);
    check('saved evidence and estimates survive reopening',await page.evaluate(()=>EnaApp.state().result.meta.per_capita.evidence.label==='ESTIMATED'&&EnaApp.state().productionRecords.maize.value===200));
    const bad=structuredClone(pkg);bad.options.scenario.registry_version='future-version';
    await page.evaluate(pkg=>EnaApp.openPackage(new File([JSON.stringify(pkg)],'bad.json')),bad);
    check('unknown saved versions are rejected',(await page.locator('#toast').innerText()).includes('Unsupported scenario registry'));
    check('rejected file leaves current analysis intact',await page.evaluate(()=>EnaApp.state().result.meta.per_capita.t===.2));
    const old=structuredClone(legacy);old.options.per_capita_kg={maize:123};
    await page.evaluate(pkg=>EnaApp.openPackage(new File([JSON.stringify(pkg)],'old.json')),old);
    await page.waitForFunction(()=>EnaApp.state().result?.meta.per_capita.t===.123);
    check('old numeric-only production remains explicitly unsourced',await page.evaluate(()=>EnaApp.state().result.meta.per_capita.evidence.label==='INFERRED'&&Object.keys(EnaApp.state().productionRecords).length===0));
    const outside=structuredClone(legacy);outside.input.area.country_code='tz';outside.input.area.name='Outside training scope (synthetic)';
    await page.evaluate(pkg=>EnaApp.openPackage(new File([JSON.stringify(pkg)],'outside.json')),outside);
    await page.waitForFunction(()=>EnaApp.state().result?.meta.area.country_code==='tz');
    await page.click('[data-lens="likely"]');
    check('outside-scope lens explains that predictions are withheld',(await page.locator('#drawer').innerText()).includes('Not validated here'));
    check('outside-scope result contains no prediction grid',await page.evaluate(()=>EnaApp.state().result.siting.status==='not_validated'&&!EnaApp.state().result.siting.layer));
    check('another area does not inherit manual production',await page.evaluate(()=>EnaApp.state().result.meta.per_capita.t===null));
    await page.screenshot({path:path.join(out,'siting-not-validated.png')});
    await page.setViewportSize({width:390,height:844});await page.click('#assumptions');
    await page.screenshot({path:path.join(out,'production-evidence-mobile.png')});
    check('mobile evidence form fits the viewport',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.evaluate(input=>{
      window.pendingInputs=[];
      EnaSources.gather=(area,step)=>new Promise(resolve=>pendingInputs.push(()=>{
        step({id:'g_sites',status:'done',detail:area.name});resolve({...input,area});
      }));
      const base=EnaApp.state().area;
      EnaApp.runArea({...base,name:'Old request'},[]);
      EnaApp.runArea({...base,name:'Current request'},[]);
      pendingInputs[1]();
    },outside.input);
    await page.waitForFunction(()=>EnaApp.state().result?.meta.area.name==='Current request');
    await page.evaluate(()=>pendingInputs[0]());await page.waitForTimeout(100);
    check('late data cannot replace the current analysis or its evidence',await page.evaluate(()=>EnaApp.state().input.area.name==='Current request'&&EnaApp.state().result.meta.area.name==='Current request'));
    await page.evaluate(()=>{
      window.pendingSearches=[];
      EnaSources.geocode=q=>new Promise(resolve=>pendingSearches.push(()=>resolve([{...EnaApp.state().area,name:q,display_name:q}])));
      EnaApp.search('Old search');EnaApp.search('Current search');pendingSearches[1]();
    });
    await page.waitForFunction(()=>EnaApp.state().area.name==='Current search');
    await page.evaluate(()=>pendingSearches[0]());await page.waitForTimeout(100);
    check('late search results cannot replace a newer location',await page.evaluate(()=>EnaApp.state().area.name==='Current search'));
    check('no browser JavaScript errors',errors.length===0);
    console.log(count+' scenario interface checks passed');
  } finally {if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
