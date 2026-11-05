/* Browser regression checks. All network responses are controlled test data. */
const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../../live'),out=path.resolve(__dirname,'../../outputs/global-landing');fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname.replace(/\/$/,'/index.html'));if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404);return res.end();}res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css','.png':'image/png','.ttf':'font/ttf'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
(async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;try{
browser=await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH});
const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.route('**/*',route=>{const url=route.request().url();if(url.includes('127.0.0.1'))return route.continue();if(url.includes('nominatim'))return route.fulfill({json:[{name:'Test valley',display_name:'Test valley, Tanzania',boundingbox:['-9.35','-9.25','34.72','34.82'],lat:'-9.3',lon:'34.77',address:{country_code:'tz'},type:'town'}]});return route.abort();});
await page.goto(`http://127.0.0.1:${server.address().port}`);await page.waitForTimeout(900);
await page.screenshot({path:path.join(out,'landing-desktop.png')});
assert(await page.locator('#landing').isVisible());assert.equal(await page.evaluate(()=>EnaApp.state().result),null);
await page.locator('#orbit-query').fill('Test valley');await page.locator('#orbit-search button').click();await page.locator('#orbit-results button').click();await page.waitForTimeout(1500);
assert(await page.locator('#orbit-selection').isVisible());await page.screenshot({path:path.join(out,'place-selected.png')});
await page.locator('#orbit-enter').click();await page.waitForTimeout(900);
assert.equal(await page.evaluate(()=>EnaApp.state().phase),'explore');assert.equal(await page.evaluate(()=>EnaApp.state().result),null);assert.equal(await page.locator('#model').inputValue(),'');assert.equal(await page.evaluate(()=>EnaApp.state().area.country_code),'tz');
await page.locator('#analyze-view').click();assert((await page.locator('#toast').innerText()).includes('Choose an activity'));
await page.screenshot({path:path.join(out,'area-overview.png')});
await page.locator('#explore-home').click();assert(await page.locator('#landing').isVisible());
await page.locator('#orbit-query').fill('95, 12');await page.locator('#orbit-search button').click();assert((await page.locator('#orbit-status').innerText()).includes('latitude'));
await page.setViewportSize({width:390,height:844});await page.emulateMedia({reducedMotion:'reduce'});await page.evaluate(()=>EnaLanding.show());await page.waitForTimeout(300);
assert.equal(await page.locator('#orbit-motion').innerText(),'Resume rotation');assert(await page.locator('#orbit-query').isVisible());await page.screenshot({path:path.join(out,'landing-mobile.png')});
assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
await page.locator('#orbit-query').fill('-9.3, 34.77');await page.locator('#orbit-search button').click();await page.locator('#orbit-results button').click();assert(await page.locator('#orbit-selection').isVisible());
assert.deepEqual(errors,[]);console.log('PASS: desktop, place search, area preview without demand, input guards, mobile, reduced motion, coordinates; no browser errors');
}finally{if(browser)await browser.close();server.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
