/* Check the actual Netlify output over HTTP, with external services blocked. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
const {serve} = require('../live/tools/local-server.cjs');
const ROOT = path.resolve(__dirname, '..');
const output = path.resolve(process.argv[2] || path.join(ROOT, 'outputs/netlify-drop'));
const {createHash} = require('node:crypto');

(async () => {
  const audit = JSON.parse(fs.readFileSync(path.join(output, 'package-audit.json')));
  const site = path.join(output, 'site');
  for (const row of audit.artifacts) {
    const hash = createHash('sha256').update(fs.readFileSync(path.join(site, row.path))).digest('hex');
    assert.equal(hash, row.sha256, row.path);
  }
  const {server, base} = await serve(site);
  let browser;
  const errors = [], badResponses = [], blocked = [], checks = [];
  const check = (name, condition) => {
    assert.ok(condition, name);
    checks.push(name);
  };
  try {
    browser = await chromium.launch({
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH,
      args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']
    });
    const context = await browser.newContext({viewport: {width: 1440, height: 900}});
    await context.route('**/*', route => {
      const url = route.request().url();
      if (url.startsWith(base + '/') || url.startsWith('blob:') || url.startsWith('data:')) {
        return route.continue();
      }
      blocked.push(url);
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => {
      if (response.url().startsWith(base) && response.status() >= 400) {
        badResponses.push({url: response.url(), status: response.status()});
      }
    });
    await page.goto(base + '/?hero=offline');
    check('root URL loads EnaGIS Live', await page.title() === 'EnaGIS Live');
    await page.click('#hero-replay');
    await page.waitForFunction(() => window.EnaApp?.state().phase === 'results', {}, {timeout: 90000});
    check('packaged Nyabihu analysis opens with ten sites', await page.locator('.site-row').count() === 10);
    check('registered Rwanda model included', await page.evaluate(() => window.EnaSitingModel.verdict === 'KEEP'));
    const ids = await page.evaluate(() => EnaApp.state().result.sites
      .filter(s => s.dry.rank !== null).sort((a, b) => a.dry.rank - b.dry.rank).map(s => s.id));
    const expected = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/rwanda/hero/nyabihu-potato/expected.json')));
    check('saved shortlist identities match source expectation',
      JSON.stringify(ids) === JSON.stringify(expected.seasons.dry.map(s => s.id)));
    await page.locator('.site-row').first().click();
    check('selected site card opens', await page.locator('#sheet').isVisible());
    await page.click('[data-lens="sure"]');
    check('uncertainty lens works', await page.evaluate(() => EnaApp.state().lens === 'sure'));
    await page.click('[data-lens="first"]');
    const download = page.waitForEvent('download');
    await page.click('#export-csv');
    const csv = await download;
    check('shortlist CSV downloads', csv.suggestedFilename().endsWith('.csv'));
    await page.screenshot({path: path.join(output, 'desktop-check.png')});
    await page.setViewportSize({width: 390, height: 844});
    check('mobile page has no horizontal overflow', await page.evaluate(() =>
      document.documentElement.scrollWidth <= window.innerWidth));
    await page.screenshot({path: path.join(output, 'mobile-check.png')});
    check('all same-origin assets return successfully', badResponses.length === 0);
    check('no uncaught JavaScript errors', errors.length === 0);
    check('saved analysis needs no external requests', blocked.length === 0);
    const report = {status: 'PASS', checks, errors, badResponses, blocked_external_requests: blocked};
    fs.writeFileSync(path.join(output, 'browser-check.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report, null, 2));
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
