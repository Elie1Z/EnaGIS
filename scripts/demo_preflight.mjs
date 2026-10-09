// Demo-day preflight: drives app/index.html in headless Edge/Chrome through the presenter path.
// Usage: node scripts/demo_preflight.mjs [app/index.html] [outputs/demo-preflight]
// Uses only Node built-ins (Node 22+). Set BROWSER to a Chromium executable if not auto-found.
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const page = resolve(process.argv[2] || "app/index.html");
const out = resolve(process.argv[3] || "outputs/demo-preflight");
const candidates = [
  process.env.BROWSER,
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/usr/bin/microsoft-edge",
].filter(Boolean);
const browser = candidates.find(existsSync);
if (!browser) { console.error("No Chromium browser found; set BROWSER=/path/to/chrome"); process.exit(2); }
if (!existsSync(page)) { console.error(`Missing ${page}; run the MVP build first.`); process.exit(2); }
mkdirSync(out, { recursive: true });

const sleep = ms => new Promise(r => setTimeout(r, ms));
const profile = mkdtempSync(join(tmpdir(), "enagis-preflight-"));
const port = 9300 + Math.floor(Math.random() * 500);
const proc = spawn(browser, [`--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, "--headless=new",
  "--window-size=1440,900", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-first-run", "about:blank"]);
let target;
for (let i = 0; i < 75 && !target; i++) {
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find(t => t.type === "page"); }
  catch { await sleep(200); }
}
if (!target) { console.error("Browser did not start"); proc.kill(); process.exit(2); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const errors = [];
ws.addEventListener("message", ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); }
  if (m.method === "Runtime.exceptionThrown") errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
  if (m.method === "Runtime.consoleAPICalled" && m.params.type === "error") errors.push(m.params.args.map(a => a.value ?? a.description).join(" "));
});
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async expression => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true }))?.result?.value;
const open = async (query = "", wait = 5000) => { await send("Page.navigate", { url: pathToFileURL(page).href + query }); await sleep(wait); };
const shot = async name => { const r = await send("Page.captureScreenshot", { format: "png" }); writeFileSync(join(out, name), Buffer.from(r.data, "base64")); };
const results = [];
const check = (name, ok, detail = "") => { results.push({ name, ok: Boolean(ok), detail }); console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? ` — ${detail}` : ""}`); };

await send("Runtime.enable"); await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await open();
const home = await evaluate(`(()=>{const pins=[...document.querySelectorAll('.map-pin')].map(p=>p.getBoundingClientRect());
  const box=s=>document.querySelector(s).getBoundingClientRect();const hits=b=>pins.filter(p=>p.left<b.right&&p.right>b.left&&p.top<b.bottom&&p.bottom>b.top).length;
  let overlaps=0;for(let i=0;i<pins.length;i++)for(let j=i+1;j<pins.length;j++){const a=pins[i],b=pins[j];if(a.left<b.right-2&&b.left<a.right-2&&a.top<b.bottom-2&&b.top<a.bottom-2)overlaps++;}
  const stage=box('.map-stage');const logo=document.querySelector('.brand img');
  return {pins:pins.length,overlaps,covered:['.layer-chips','.map-heading','.list-drawer','.detail-sheet','.map-key'].map(s=>hits(box(s))).reduce((a,b)=>a+b,0),
    offstage:pins.filter(p=>p.bottom>stage.bottom||p.top<stage.top).length,logo:logo&&logo.complete&&logo.naturalWidth>0,
    map:document.getElementById('map-status').textContent,rows:document.querySelectorAll('.site-row').length,card:document.getElementById('site-card').innerText.slice(0,80)}})()`);
check("Brand wordmark loads", home.logo);
check("Map ready", /ready|loaded/i.test(home.map), home.map);
check("Ten shortlisted sites listed and pinned", home.rows === 10 && home.pins === 10, `${home.rows} rows, ${home.pins} pins`);
check("Pins do not overlap each other", home.overlaps === 0, `${home.overlaps} overlaps`);
check("Pins clear of panels, chips and heading", home.covered === 0 && home.offstage === 0, `${home.covered} covered, ${home.offstage} off-map`);
check("Hero site card opens on Dixon", /Dixon/.test(home.card));
await shot("1-where-first.png");

await evaluate("document.querySelector('[data-lens=sure]').click()"); await sleep(1000);
const sure = await evaluate("document.getElementById('lens-panel').innerText");
check("How sure shows the registered KILL verdict", /KILL/.test(sure));
check("How sure shows the baseline comparison bars", /Production only/.test(sure));
await shot("2-how-sure.png");

await evaluate("document.querySelector('[data-lens=first]').click();const i=document.getElementById('place-search');i.focus();i.value='Kigali';i.dispatchEvent(new Event('input',{bubbles:true}))");
await sleep(700);
await evaluate("document.querySelector('.search-option')?.click()"); await sleep(2500);
const kigali = await evaluate("({label:document.getElementById('area-label').textContent,card:document.getElementById('site-card').innerText})");
check("Worldwide search selects Kigali", /Kigali/i.test(kigali.label), kigali.label);
check("Uncovered area stays UNKNOWN, no invented numbers", /unknown/i.test(kigali.card) && !/\d+\s*kW/.test(kigali.card));
await shot("3-kigali.png");

await evaluate("document.getElementById('home').click()"); await sleep(1500);
await evaluate("document.querySelector('[data-lens=travel]').click()"); await sleep(800);
check("How to get there lens renders", /Unknown|Access/i.test(await evaluate("document.getElementById('lens-panel').innerText")));
await shot("4-travel.png");
await evaluate("document.querySelector('[data-lens=works]').click()"); await sleep(800);
check("How it works lens renders", (await evaluate("document.querySelectorAll('[data-story]').length")) === 5);
await shot("4b-how-it-works.png");

await open("?map=flat", 4000);
check("Flat backup map (no WebGL) renders pins", (await evaluate("document.querySelectorAll('.fallback-pin').length")) === 10);
await shot("5-flat-backup.png");

await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await open("", 4500);
check("Phone layout renders the list", (await evaluate("document.querySelectorAll('.site-row').length")) === 10);
await shot("6-phone.png");

check("No console errors or exceptions", errors.length === 0, errors.slice(0, 3).join(" | "));
writeFileSync(join(out, "preflight.json"), JSON.stringify({ page, browser, at: new Date().toISOString(), results, errors }, null, 2));
ws.close(); proc.kill();
await sleep(300);
try { rmSync(profile, { recursive: true, force: true }); } catch { /* browser may still hold the profile */ }
const failed = results.filter(r => !r.ok).length;
console.log(failed ? `\n${failed} check(s) FAILED — screenshots in ${out}` : `\nAll ${results.length} checks passed — screenshots in ${out}`);
process.exit(failed ? 1 : 0);
