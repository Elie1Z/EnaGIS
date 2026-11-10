'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const {serve} = require('../../live/tools/local-server.cjs');
const {makeSynthetic} = require('../../live/js/synthetic.js');
const output = path.resolve(__dirname, '../../outputs/service-upgrade');
fs.mkdirSync(output, {recursive: true});
let checks = 0;
function check(name, condition) {
  assert.ok(condition, name);
  console.log('PASS ' + name);
  checks++;
}

(async () => {
  const {server, base} = await serve();
  let browser;
  try {
    browser = await chromium.launch({executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH});
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/*', route => route.request().url().includes('127.0.0.1') ? route.continue() : route.abort());
    await page.goto(base + '/live/index.html');
    await page.waitForFunction(() => !!window.EnaApp);
    const input = makeSynthetic(7);
    const legacy = {format: 'enagis-live-package-v1', input, options: {model: 'potato_storage'}, synthetic: true};
    await page.evaluate(pkg => EnaApp.openPackage(new File([JSON.stringify(pkg)], 'fixture.json')), legacy);
    await page.waitForFunction(() => EnaApp.state().phase === 'results');
    const legacyProduction = await page.evaluate(() => EnaApp.state().result.meta.per_capita.t);
    check('main menu offers seven services without crop selections', await page.locator('#model option:not([hidden]):not([disabled])').count() === 7);
    await page.selectOption('#model', 'cold_storage');
    await page.waitForFunction(() => EnaApp.state().result?.meta.model.id === 'cold_storage');
    check('cold storage includes produce beyond the previous potato input', await page.evaluate(previous => EnaApp.state().result.meta.per_capita.t > previous, legacyProduction));
    check('worker calculates a versioned service scenario', await page.evaluate(() => EnaApp.engine().worker && EnaApp.state().result.meta.scenario.recipe_version === 'service-v1'));
    await page.locator('#drawer .service-evidence summary').click();
    check('production coverage and product groups are disclosed', /vegetables/.test(await page.locator('#drawer .service-evidence').innerText()));
    await page.screenshot({path: path.join(output, 'cold-storage-service.png')});
    await page.selectOption('#model', 'drying');
    await page.waitForFunction(() => EnaApp.state().result?.meta.model.id === 'drying');
    check('drying explicitly describes the electricity and heat boundary', (await page.locator('#drawer').innerText()).includes('Drying heat'));
    await page.selectOption('#model', 'oil_pressing');
    await page.waitForFunction(() => EnaApp.state().result?.meta.model.id === 'oil_pressing');
    check('new service displays unranked candidates when equipment data is missing', (await page.locator('#drawer').innerText()).includes('Mapped places to investigate') && await page.locator('.site-row').count() > 0);
    check('missing energy is null, not an invented zero', await page.evaluate(() => EnaApp.state().result.sites.every(site => site.dry.kwh_day === null)));
    await page.click('#assumptions');
    for (const [index, value] of ['10', '20', '30'].entries()) {
      await page.locator(`[data-param="specific_energy"][data-i="${index}"]`).fill(value);
    }
    await page.click('#apply-assumptions');
    check('energy source is required before calculation', (await page.locator('#toast').innerText()).includes('source'));
    await page.fill('#equipment-source', 'Synthetic press specification');
    await page.fill('#equipment-date', '2026-11-10');
    await page.fill('#equipment-licence', 'Synthetic verification fixture');
    await page.click('#apply-assumptions');
    await page.waitForFunction(() => EnaApp.state().result?.meta.service.energy_ready);
    check('equipment evidence enables positive energy estimates', await page.evaluate(() => EnaApp.state().result.sites.some(site => site.dry.kwh_day?.central > 0)));
    await page.click('[data-close-panel]');
    const [download] = await Promise.all([page.waitForEvent('download'), page.click('#save')]);
    const savedPath = path.join(output, 'service-roundtrip.json');
    await download.saveAs(savedPath);
    const saved = JSON.parse(fs.readFileSync(savedPath, 'utf8'));
    check('save retains service version and equipment source', saved.options.scenario.recipe_version === 'service-v1' && saved.options.energy_evidence.oil_pressing.source === 'Synthetic press specification');
    const previous = await page.evaluate(() => EnaApp.state().result.sites.map(site => site.dry.kwh_day.central));
    await page.evaluate(pkg => EnaApp.openPackage(new File([JSON.stringify(pkg)], 'service.json')), saved);
    await page.waitForFunction(() => EnaApp.state().phase === 'results');
    check('service save reopens with identical estimates', await page.evaluate(values => JSON.stringify(EnaApp.state().result.sites.map(site => site.dry.kwh_day.central)) === JSON.stringify(values), previous));
    const [csv] = await Promise.all([page.waitForEvent('download'), page.click('#export-csv')]);
    const csvPath = path.join(output, 'service.csv');
    await csv.saveAs(csvPath);
    const csvText = fs.readFileSync(csvPath, 'utf8');
    check('export includes service boundary, components and equipment evidence', csvText.includes('service_boundary') && csvText.includes('groundnut') && csvText.includes('Synthetic press specification'));
    await page.selectOption('#model', 'milling');
    await page.waitForFunction(() => EnaApp.state().result?.meta.model.id === 'milling');
    check('service changes reset incompatible operating assumptions', await page.evaluate(() => !EnaApp.state().overrides.specific_energy));
    await page.setViewportSize({width: 390, height: 844});
    await page.screenshot({path: path.join(output, 'service-mobile.png')});
    check('service interface fits mobile width', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    check('no JavaScript errors', errors.length === 0);
    console.log(checks + ' service interface checks passed');
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
