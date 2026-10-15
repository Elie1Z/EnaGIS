/* Explicit acquisition only. Run after human download approval; never during replay or tests.
 * node live/tools/capture-hero.cjs --approved-max-mb=100
 * Uses the shipped gatherer and retains raw JSON responses plus request metadata.
 */
'use strict';
const fs = require('node:fs'), path = require('node:path');
const {chromium} = require('playwright');
const {ROOT, serve} = require('./local-server.cjs');
const limit = Number((process.argv.find(a => a.startsWith('--approved-max-mb=')) || '').split('=')[1]);
if (!(limit > 0)) throw new Error('Explicit human-approved download budget required.');
(async () => {
  const {server, base} = await serve();
  const browser = await chromium.launch({executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH});
  const page = await browser.newPage();
  const out = path.join(ROOT, 'data/rwanda/hero/nyabihu-potato');
  fs.mkdirSync(out, {recursive:true});
  if (fs.existsSync(path.join(out, 'input.json'))) {await browser.close();server.close();throw new Error('A frozen input already exists. Choose a separately reviewed snapshot before another acquisition.');}
  let bytes = 0, exceeded = false;
  const responses = [], tasks = [];
  // Browser route enforces the budget on decoded response bytes, before exposing each response
  // to the gatherer. Serialized requests avoid in-flight responses exceeding the approved budget.
  let queue = Promise.resolve();
  await page.route('https://**/*', route => {
    const work = queue.then(async () => {
      if (exceeded) return route.abort();
      const request = route.request();
      const response = await route.fetch({timeout:90000});
      const body = await response.body();
      bytes += body.length;
      if (bytes > limit * 1e6) { exceeded = true; await route.abort(); throw new Error('Download budget exceeded; acquisition stopped.'); }
      if (/nominatim|overpass|open-meteo|worldpop/.test(request.url())) {
        let json; try { json = JSON.parse(body.toString()); } catch { json = null; }
        if (json) responses.push({url:request.url(), method:request.method(), post_data:request.postData(),
          retrieved_at:new Date().toISOString(), status:response.status(), body:json});
      }
      await route.fulfill({response, body});
    });
    queue = work.catch(e => { console.error(String(e)); });
    return work;
  });
  try {
    await page.goto(base + '/live/index.html?hero=offline');
    await page.exposeFunction('captureProgress', st => { if (st.status !== 'running' || !/map tiles/.test(st.detail || '')) console.log(st.id, st.status, st.detail); });
    const input = await page.evaluate(async () => {
      const areas = await EnaSources.geocode('Nyabihu District, Rwanda');
      const area = areas.find(a => a.country_code === 'rw' && a.polygon && /district|county/.test(a.kind + ' ' + a.display_name.toLowerCase()));
      if (!area) throw new Error('Nyabihu district boundary missing');
      area.name = 'Nyabihu District';
      return EnaSources.gather(area, window.captureProgress);
    });
    await Promise.all(tasks); await queue;
    if (exceeded) throw new Error('Approval budget exceeded; no complete snapshot written');
    fs.writeFileSync(path.join(out, 'acquisition-responses.json'), JSON.stringify(responses));
    fs.writeFileSync(path.join(out, 'input.json'), JSON.stringify(input));
    fs.writeFileSync(path.join(out, 'acquisition.json'), JSON.stringify({retrieved_at:input.retrieved_at, bytes,
      approved_max_mb:limit, release:'2026-09-23.1', method:'Shipped browser gatherer; converted Overture geometry retains the exact engine inputs; raw JSON service responses retained separately.'}, null, 2));
    console.log('Saved input bundle', bytes, 'bytes transferred');
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
