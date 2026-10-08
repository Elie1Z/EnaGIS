/* Browser acceptance checks; browser dependencies are supplied separately from runtime. */
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {pathToFileURL} = require("node:url");
const modules = process.argv[2];
if (!modules) throw Error("Usage: node scripts/check_mvp_ui.cjs <playwright module directory>");
const {chromium} = require(path.join(modules, "playwright"));
const root = path.resolve(__dirname, "..");
const output = path.join(root, "outputs/phase8-browser");
const screenshots = path.join(root, "docs/audits/phase8");
fs.mkdirSync(output, {recursive:true});fs.mkdirSync(screenshots,{recursive:true});
const url = pathToFileURL(path.join(root,"app/index.html")).href;

(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",args:["--allow-file-access-from-files","--enable-webgl","--use-angle=swiftshader"]});
  const report={date:"2026-10-09",environment:"Headless Edge on Windows; local file, network disabled; 4x CPU throttling",checks:[],errors:[],external_requests:[],screenshots:[]};
  const check=(name,value)=>{assert.ok(value,name);report.checks.push({name,status:"PASS"});};
  try {
    for(const [label,viewport] of [["desktop",{width:1440,height:900}],["mobile",{width:390,height:844}]]){
      const context=await browser.newContext({viewport,offline:true,reducedMotion:"reduce"});
      const page=await context.newPage();page.on("pageerror",e=>report.errors.push(e.message));
      page.on("request",request=>{if(/^https?:/.test(request.url()))report.external_requests.push(request.url());});
      const session=await context.newCDPSession(page);await session.send("Emulation.setCPUThrottlingRate",{rate:4});
      await page.goto(url);await page.waitForFunction(()=>window.EnaApp && document.querySelectorAll(".site-row").length===10);
      await page.waitForFunction(()=>document.querySelectorAll(".map-pin,.fallback-pin").length===10);
      const first=await page.evaluate(()=>performance.getEntriesByName("enagis-first-list")[0].startTime);
      report.checks.push({name:`${label}: initial top-10 render`,status:first<1000?"PASS":"FAIL",milliseconds:first});
      check(`${label}: only four lenses`,await page.locator("[data-lens]").count()===4);
      check(`${label}: no presenter controls`,await page.locator("#present,#guide,[data-demo]").count()===0);
      const contrasts=await page.evaluate(()=>{
        const rgba=str=>{const n=str.match(/[\d.]+/g)?.map(Number)||[];return n.length>=3?[...n.slice(0,3),n[3]??1]:[0,0,0,0];};
        const over=(a,b)=>[0,1,2].map(i=>a[i]*a[3]+b[i]*(1-a[3]));
        const lum=c=>c.slice(0,3).map(v=>{const n=v/255;return n<=.04045?n/12.92:Math.pow((n+.055)/1.055,2.4);}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
        const failures=[];let total=0;
        for(const el of document.querySelectorAll("body *")){
          if(["SCRIPT","STYLE","SVG","PATH"].includes(el.tagName)||!el.getClientRects().length||!Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim()))continue;
          const r=el.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight||r.right<0||r.left>innerWidth)continue;
          const style=getComputedStyle(el);if(style.visibility==="hidden")continue;
          const layers=[];for(let p=el;p;p=p.parentElement)layers.push(rgba(getComputedStyle(p).backgroundColor));
          let bg=[255,255,255];for(const c of layers.reverse())bg=over(c,bg);
          const fg=over(rgba(style.color),bg),a=lum(fg),b=lum(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
          const large=parseFloat(style.fontSize)>=24||(parseFloat(style.fontSize)>=18.66&&parseFloat(style.fontWeight)>=700);total++;
          if(ratio<(large?3:4.5))failures.push({text:el.innerText.slice(0,50),ratio});
        }return {total,failures};
      });
      report.checks.push({name:`${label}: visible text AA contrast`,status:contrasts.failures.length?"FAIL":"PASS",...contrasts});
      check(`${label}: offline fonts loaded`,await page.evaluate(async()=>{await Promise.all(['14px Inter','20px Fraunces','italic 19px Fraunces'].map(face=>document.fonts.load(face)));return document.fonts.check('14px Inter') && document.fonts.check('20px Fraunces') && document.fonts.check('italic 19px Fraunces');}));
      if(label==="mobile" && !await page.evaluate(()=>document.body.classList.contains("list-open")))await page.locator("#mobile-list-toggle").click();
      await page.locator(".site-row").nth(2).focus();await page.keyboard.press("Enter");
      check(`${label}: keyboard selects site`,(await page.evaluate(()=>EnaApp.state().selected))!==null);
      const selected=await page.evaluate(()=>EnaApp.state().selected);
      const camera=await page.evaluate(()=>EnaApp.state().camera);
      for(const lens of ["first","sure","travel","works"]){
        await page.locator(`[data-lens=${lens}]`).focus();await page.keyboard.press("Enter");
        check(`${label}: ${lens} keeps selection`,await page.evaluate(()=>EnaApp.state().selected)===selected);
        assert.deepEqual(await page.evaluate(()=>EnaApp.state().camera),camera,`${lens} camera changed`);
        const file=`${lens}-${label}.png`;await page.screenshot({path:path.join(screenshots,file)});report.screenshots.push(`docs/audits/phase8/${file}`);
      }
      check(`${label}: seasonal results unavailable, never fabricated`,await page.locator("[data-lens=travel]").click().then(()=>page.locator(".season-controls button:disabled").count())===2);
      if(label==="mobile"){
        await page.locator("#detail-toggle").click();
        await page.locator("#mobile-list-toggle").click();
        for(let i=0;i<3;i++)await page.locator("#detail-handle").click();
        check("mobile: three sheet snap states",await page.locator("#detail-sheet").getAttribute("data-snap")==="mid");
        const geo=await page.locator("#detail-sheet").boundingBox();check("mobile: sheet leaves map visible",geo.height<600);
      }
      await page.locator("#language").selectOption("fr");await page.reload();
      check(`${label}: language persists`,await page.locator("html").getAttribute("lang")==="fr");
      await page.locator("#language").selectOption("rw");check(`${label}: Kinyarwanda shell`,await page.locator("[data-lens=first]").innerText()==="Aho gutangirira");
      await page.locator("#language").selectOption("en");
      if(label==="desktop"){
        await page.locator("#detail-toggle").click();await page.reload();check("desktop: expert choice persists",await page.evaluate(()=>EnaApp.state().expert));
        for(const place of ["Kigali","Sydney","Reykjavik","Manaus","Longyearbyen"]){
          await page.locator("#place-search").fill(place);await page.keyboard.press("ArrowDown");await page.keyboard.press("Enter");
          const state=await page.evaluate(()=>EnaApp.state());check(`global search: ${place}`,state.area?.name.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase()===place.toLowerCase());
          check(`${place}: insufficient evidence stays unknown`,await page.locator("#site-card").innerText().then(text=>text.includes("Requirement unknown")&&!text.includes("0 kW")));
        }
        await page.locator("#place-search").fill("0, 0");await page.keyboard.press("Enter");check("zero coordinates accepted",await page.evaluate(()=>EnaApp.state().area.lat===0 && EnaApp.state().area.lon===0));
        await page.locator("#place-search").fill("-1.95, 30.06");await page.keyboard.press("Enter");check("coordinate search reaches any unindexed location",await page.evaluate(()=>EnaApp.state().area.lon===30.06));
        const requestDownload=page.waitForEvent("download");await page.locator("#area-export").click();check("location needs export",(await requestDownload).suggestedFilename()==="location-evidence-needs.json");
        const invalid=await page.evaluate(async()=>{const before=EnaApp.state().region;await EnaApp.importPackage(new File(['{"schema_version":"invented"}'],"bad.json"));return EnaApp.state().region===before;});check("invalid package preserves current analysis",invalid);
        const region=await page.evaluate(async()=>{
          const site=EnaView.fromNode(D.nodes[0]);
          const e={label:"ESTIMATED",as_of:"2026-10-09",licence:"MIT",method:"Synthetic browser fixture",source_ids:["fixture-source"],missing_reason:null};
          Object.assign(site,{id:"fixture:rw-node",name:"Synthetic collection point",operator:"Fixture",rank:1,province:"Test",lon:30.06,lat:-1.95,question:"Confirm this synthetic node",tier:null});
          site.need={value:12,range:[8,16],unit:"kW",evidence:e};site.location={value:{longitude:30.06,latitude:-1.95,crs:"EPSG:4326"},evidence:{...e,label:"OBSERVED"}};
          for(const [key,unit] of [["margin","kW"],["storage","t"],["throughput","t/year"]])site[key]={...EnaView.unknown("Synthetic unavailable field"),unit};
          site.supply_evidence={...e,label:"INFERRED"};delete site.trace;delete site.cycle;
          const pkg={schema_version:"enagis-region-view-v1",crs:"EPSG:4326",region_id:"fixture:rwanda",title:"Synthetic Rwanda fixture",run_id:"fixture:region-v1",purpose:"synthetic",limitations:["Synthetic fixture only"],sources:[{snapshot_id:"fixture-source",publisher:"Fixture",licence:"MIT",effective_on:"2026-10-09",redistribution:"permitted"}],sites:[site],coverage:{type:"FeatureCollection",features:[{type:"Feature",properties:{},geometry:{type:"Polygon",coordinates:[[[29,-3],[31,-3],[31,0],[29,0],[29,-3]]]}}]}};
          Object.assign(pkg,{commodity_id:"wheat_non_durum",service_id:"ambient_air_aeration",period_start:"2024-01-01",period_end:"2024-12-31"});
          await EnaApp.importPackage(new File([JSON.stringify(pkg)],"regional.json"));return EnaApp.state().region;
        });
        check("new region package replaces benchmark",region==="fixture:rwanda");
        check("synthetic region visibly labelled",await page.locator("#synthetic-ribbon").isVisible());
        await page.locator("[data-lens=first]").click();check("new region shows supplied interval",(await page.locator("#site-card").innerText()).includes("8–16 kW"));
        const regionalDownload=page.waitForEvent("download");await page.locator("#export-shortlist").click();const downloaded=await regionalDownload;
        check("imported region exports its own shortlist",downloaded.suggestedFilename()==="regional-shortlist.csv" && fs.readFileSync(await downloaded.path(),"utf8").includes("fixture:rw-node"));
        await page.evaluate(()=>EnaApp.restore());
        await page.locator("[data-lens=first]").click();
        await page.evaluate(()=>window.print=()=>{window.printCalled=true;});await page.locator("#site-brief").click();check("A4 site brief available",await page.evaluate(()=>window.printCalled && document.getElementById("print-brief").innerText.includes("Dixon")));
        await page.emulateMedia({media:"print"});await page.pdf({path:path.join(output,"site-brief.pdf"),format:"A4",printBackground:true,preferCSSPageSize:true});await page.emulateMedia({media:"screen"});
        const beforeText=await page.locator("#site-card .card-block p").first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
        await page.evaluate(()=>document.documentElement.style.fontSize="28px");
        check("200% text: body text actually doubles",await page.locator("#site-card .card-block p").first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize))===beforeText*2);
        check("200% text: no horizontal document overflow",await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        await page.evaluate(()=>document.documentElement.style.fontSize="");
      }
      check(`${label}: no horizontal page overflow`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      await context.close();
    }
    const flat=await browser.newContext({viewport:{width:1440,height:900},offline:true});const page=await flat.newPage();await page.goto(url+"?map=flat");
    await page.waitForSelector(".fallback-pin");check("WebGL-free map retains ten selectable sites",await page.locator(".fallback-pin").count()===10);
    await page.locator(".fallback-pin").nth(3).focus();await page.keyboard.press("Enter");check("flat map keyboard selection",await page.evaluate(()=>EnaApp.state().selected!==null));
    await page.locator("#place-search").fill("89.5, 120");await page.keyboard.press("Enter");check("flat map retains polar coordinates",await page.evaluate(()=>EnaApp.state().area.lat===89.5));
    await page.screenshot({path:path.join(screenshots,"polar-flat.png")});await flat.close();
    check("zero runtime external requests",report.external_requests.length===0);check("zero uncaught browser errors",report.errors.length===0);
    report.status=report.checks.some(c=>c.status==="FAIL")?"FAIL":"PASS";
  } catch(error){report.status="FAIL";report.failure=error.stack;throw error;}
  finally{fs.writeFileSync(path.join(output,"acceptance.json"),JSON.stringify(report,null,2));await browser.close();console.log(JSON.stringify(report,null,2));if(report.status!=="PASS")process.exitCode=1;}
})().catch(e=>{console.error(e);process.exitCode=1;});
