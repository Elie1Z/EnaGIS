/* Journey lifecycle tests. Search/data are explicit synthetic fixtures; imagery is unavailable. */
'use strict';
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const {makeSynthetic}=require('../../live/js/synthetic.js');
const fixture=makeSynthetic(7);
const root=path.resolve(__dirname,'../../live'),out=path.resolve(__dirname,'../../outputs/global-landing');
fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname.replace(/\/$/,'/index.html'));
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404);return res.end();}
  res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
let checks=0;
function check(name,condition){assert(condition,name);checks++;console.log('PASS '+name);}
(async()=>{
  await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
  try {
    browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH});
    const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    const [w,s,e,n]=fixture.area.bbox;
    await page.route('**/*',route=>{
      const url=route.request().url();
      if(url.includes('127.0.0.1'))return route.continue();
      if(url.includes('nominatim'))return route.fulfill({json:[{
        name:'Test valley',display_name:'Test valley, Tanzania (test fixture)',
        boundingbox:[String(s),String(n),String(w),String(e)],
        lat:String((s+n)/2),lon:String((w+e)/2),address:{country_code:'tz'},type:'town'
      }]});
      return route.abort();
    });
    await page.goto('http://127.0.0.1:'+server.address().port);
    await page.waitForFunction(()=>window.EnaApp?.map().getProjection()?.type==='globe');
    await page.waitForTimeout(800);
    await page.evaluate(input=>{
      window.testCanvas=EnaApp.map().getCanvas();
      window.testRequests=[];
      EnaSources.gather=(area,step)=>new Promise(resolve=>{
        step({id:'g_sites',status:'running',detail:'Controlled test response'});
        testRequests.push({area,finish:()=>{
          step({id:'g_sites',status:'done',detail:'Synthetic tagged places'});
          step({id:'g_pop',status:'failed',detail:'Synthetic unavailable population service'});
          resolve({...structuredClone(input),area,population:null});
        }});
      });
    },fixture);
    check('one real geographic canvas on landing',await page.evaluate(()=>document.querySelectorAll('#map canvas').length===1&&!document.getElementById('earth')));
    check('satellite fallback is labelled',await page.locator('#orbit-imagery').innerText().then(t=>t.includes('unavailable')));
    check('no energy calculation on entry',await page.evaluate(()=>EnaApp.state().result===null));
    await page.locator('#orbit-motion').click();
    const paused=await page.evaluate(()=>EnaApp.map().getCenter().lng);
    await page.waitForTimeout(250);
    check('pause stops rotation',Math.abs((await page.evaluate(()=>EnaApp.map().getCenter().lng))-paused)<.001);
    await page.screenshot({path:path.join(out,'landing-desktop.png')});
    await page.locator('#orbit-query').fill('Test valley');
    await page.locator('#orbit-search button').click();
    await page.locator('#orbit-results button').click();
    await page.waitForFunction(()=>document.body.classList.contains('earth-flight'));
    check('selection starts gathering without a second enter button',await page.evaluate(()=>testRequests.length===1&&EnaApp.state().exploring));
    const earlyZoom=await page.evaluate(()=>EnaApp.map().getZoom());
    await page.waitForTimeout(1600);
    const midZoom=await page.evaluate(()=>EnaApp.map().getZoom());
    check('camera advances during flight',midZoom>earlyZoom+.2);
    check('flight progress names the selected area',(await page.locator('#flight-place').innerText())==='Test valley');
    await page.screenshot({path:path.join(out,'place-selected.png')});
    await page.waitForFunction(()=>!document.body.classList.contains('landing-open'),{},{timeout:10000});
    check('same canvas survives arrival',await page.evaluate(()=>testCanvas===EnaApp.map().getCanvas()));
    check('map size does not jump at arrival',await page.evaluate(()=>{
      const r=EnaApp.map().getContainer().getBoundingClientRect();
      return r.width===innerWidth&&r.height===innerHeight;
    }));
    check('target is centered in the free map area',await page.evaluate(()=>{
      const a=EnaApp.state().area,b=a.bbox,p=EnaApp.map().project([(b[0]+b[2])/2,(b[1]+b[3])/2]);
      return Math.abs(p.x-895)<15&&Math.abs(p.y-510)<15;
    }));
    check('arrival retains chosen country and requires activity',await page.evaluate(()=>EnaApp.state().area.country_code==='tz'&&!document.getElementById('model').value&&EnaApp.state().result===null));
    check('selected area fills the available map without landing-padding shrinkage',await page.evaluate(()=>{
      const m=EnaApp.map(),b=EnaApp.state().area.bbox,a=m.project([b[0],b[1]]),c=m.project([b[2],b[3]]);
      return Math.max(Math.abs(c.x-a.x)/890,Math.abs(c.y-a.y)/800)>.85;
    }));
    await page.evaluate(()=>testRequests[0].finish());
    await page.waitForFunction(()=>!!EnaApp.state().input);
    check('unavailable evidence remains visible',(await page.locator('#drawer').innerText()).includes('1 unavailable'));
    check('gather alone does not rank sites',await page.evaluate(()=>EnaApp.state().result===null));
    await page.screenshot({path:path.join(out,'area-overview.png')});
    await page.locator('#model').selectOption('milling');
    await page.waitForFunction(()=>EnaApp.state().phase==='results',{},{timeout:30000});
    check('activity selection uses gathered inputs without refetching',await page.evaluate(()=>testRequests.length===1&&EnaApp.state().result.meta.area.country_code==='tz'));
    await page.evaluate(()=>{
      const OriginalMap=maplibregl.Map;
      maplibregl.Map=class extends OriginalMap {constructor(options){super(options);window.testComparison=this;}};
    });
    await page.locator('#compare').click();
    await page.waitForFunction(()=>window.testComparison?.getProjection()?.type==='globe');
    check('comparison retains the arrival camera padding',await page.evaluate(()=>{
      const center=EnaApp.map().getCenter(),a=EnaApp.map().project(center),b=testComparison.project(center);
      return Math.hypot(a.x-b.x,a.y-b.y)<1;
    }));
    check('comparison divider meets the imagery split',await page.evaluate(()=>Math.abs(document.getElementById('swipe').getBoundingClientRect().left-innerWidth/2)<2));
    await page.locator('#compare').click();
    await page.evaluate(()=>EnaLanding.show());
    const area={name:'New place',display_name:'New place',bbox:[34.72,-9.35,34.82,-9.25],country_code:'tz'};
    await page.evaluate(a=>EnaLanding.select(a),area);
    await page.locator('#flight-skip').click();
    check('skip flight arrives immediately',await page.evaluate(()=>!document.body.classList.contains('earth-flight')&&!document.body.classList.contains('landing-open')));
    await page.evaluate(()=>EnaLanding.show());
    await page.evaluate(()=>testRequests[1].finish());
    await page.waitForTimeout(150);
    check('late response cannot overwrite a new journey',await page.evaluate(()=>EnaApp.state().input===null&&EnaApp.state().area===null));
    await page.evaluate(()=>EnaLanding.select({name:'Continent overview',bbox:[-10,-20,50,50]}));
    await page.locator('#flight-skip').click();
    check('large regions remain an overview, without detailed gather',await page.evaluate(()=>testRequests.length===2&&!EnaApp.state().exploring));
    check('overview explains how to narrow the area',(await page.locator('#drawer').innerText()).includes('smaller study area'));
    await page.evaluate(()=>EnaLanding.show());
    await page.locator('#orbit-query').fill('95, 12');
    await page.locator('#orbit-search button').click();
    check('invalid coordinates are rejected',(await page.locator('#orbit-status').innerText()).includes('latitude'));
    await page.setViewportSize({width:390,height:844});
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.evaluate(()=>EnaLanding.show());
    check('reduced motion pauses globe',await page.locator('#orbit-motion').innerText().then(t=>t==='Resume rotation'));
    await page.screenshot({path:path.join(out,'landing-mobile.png')});
    check('mobile has no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    await page.locator('#orbit-query').fill('-9.3, 34.77');
    await page.locator('#orbit-search button').click();
    await page.waitForFunction(()=>!document.body.classList.contains('landing-open'));
    check('coordinate entry arrives directly with reduced motion',await page.evaluate(()=>EnaApp.state().area.kind==='view'&&!EnaApp.map().isMoving()));
    await page.evaluate(()=>testRequests[2].finish());
    await page.waitForFunction(()=>!!EnaApp.state().input);
    check('mobile journey also gathers data',await page.evaluate(()=>EnaApp.state().phase==='explore'&&EnaApp.state().input.area.name.startsWith('Around')));
    await page.screenshot({path:path.join(out,'area-mobile.png')});
    check('no browser JavaScript errors',errors.length===0);
    console.log(checks+' journey checks passed');
  } finally {if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
