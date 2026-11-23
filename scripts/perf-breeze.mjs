/**
 * Breeze 2027 gully performance runner (production build).
 *
 *   npm run build && GULLYVERSE_RUNTIME_PREVIEW=1 npm start        # in another shell, with preview env
 *   BREEZE_BASE_URL=http://127.0.0.1:3000 npm run perf:breeze -- --label baseline
 *
 * Options (environment): BREEZE_PROFILES=desktop,mobile-emulated  BREEZE_RUNS=3  BREEZE_SAMPLE_SECONDS=30
 *   BREEZE_STOPS=market,approach,plaza,events,team,aftermovie  BREEZE_CYCLES=10  BREEZE_SUITES=load,poses,journey,cycles
 *   BREEZE_OUT=perf-results  BREEZE_COMPARE=<baseline json>  CHROME_PATH=<browser>
 *
 * What it measures, per profile:
 * - load: cold (fresh browser context, empty HTTP cache) and warm (same context, reload) visits to `/`:
 *   transfer bytes by type (CDP encodedDataLength), navigation timing, `breeze:*` marks (each chunk,
 *   world ready, walking ready), request failures and console errors.
 * - poses: each map stop on /runtime-preview/cypher?start=<stop>&diagnostics (fixed spawn pose, no
 *   input): after a 5 s settle, BREEZE_SAMPLE_SECONDS of rAF presentation intervals, CPU render-submit time,
 *   GPU timer samples where available, renderer counters and scene memory estimates.
 * - journey: walk (W) then sprint (Shift+W) from the market spawn, sampling frames.
 * - cycles: BREEZE_CYCLES map round trips market -> events -> team -> aftermovie -> market, recording
 *   JS heap, renderer geometries/textures/programs and scene estimates after each cycle.
 * Raw results are written in full; failed runs are kept. The renderer string is recorded: SwiftShader
 * (software) frame times are not GPU performance and must not be compared with hardware runs.
 */
import { mkdir, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import { chromium, devices } from "playwright";

const base = process.env.BREEZE_BASE_URL ?? "http://127.0.0.1:3000";
const label = process.argv.includes("--label") ? process.argv[process.argv.indexOf("--label") + 1] : "run";
const profiles = (process.env.BREEZE_PROFILES ?? "desktop,mobile-emulated").split(",");
const runs = Number(process.env.BREEZE_RUNS ?? 3);
const sampleSeconds = Number(process.env.BREEZE_SAMPLE_SECONDS ?? 30);
const stops = (process.env.BREEZE_STOPS ?? "market,approach,plaza,events,team,aftermovie").split(",");
const cycles = Number(process.env.BREEZE_CYCLES ?? 10);
const suites = new Set((process.env.BREEZE_SUITES ?? "load,poses,journey,cycles").split(","));
const out = process.env.BREEZE_OUT ?? "perf-results";
await mkdir(out, { recursive: true });

const profileOptions = {
  desktop: { viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 },
  "mobile-emulated": { ...devices["Pixel 7"] },
};
const browser = await chromium.launch({ ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}), args: ["--enable-precise-memory-info", "--autoplay-policy=no-user-gesture-required"] });
const environment = { label, startedAt: new Date().toISOString(), base, browser: browser.version(), os: `${os.type()} ${os.release()}`, cpus: os.cpus()[0]?.model, cpuCount: os.cpus().length, sampleSeconds, runs };
const results = { environment, load: [], poses: [], journey: [], cycles: [], errors: [] };

const kind = (url, type) => /\.glb(\?|$)/.test(url) ? "glb" : /\.ktx2(\?|$)/.test(url) ? "ktx2" : /\.hdr(\?|$)/.test(url) ? "hdr"
  : /\.(mp4|webm)(\?|$)/.test(url) ? "video" : /\.(mp3|wav|ogg)(\?|$)/.test(url) ? "audio" : /\.wasm(\?|$)/.test(url) ? "wasm"
  : type === "Script" ? "js" : type === "Stylesheet" ? "css" : type === "Font" ? "font" : type === "Image" ? "image" : type === "Document" ? "html" : "other";

async function track(page, context) {
  const cdp = await context.newCDPSession(page);
  await cdp.send("Network.enable");
  const requests = new Map(), errors = [];
  cdp.on("Network.requestWillBeSent", e => requests.set(e.requestId, { url: e.request.url, type: e.type, start: e.timestamp }));
  cdp.on("Network.responseReceived", e => { const r = requests.get(e.requestId); if (r) { r.status = e.response.status; r.fromCache = e.response.fromDiskCache || e.response.fromServiceWorker || e.response.fromPrefetchCache; r.type = e.type; } });
  cdp.on("Network.loadingFinished", e => { const r = requests.get(e.requestId); if (r) { r.bytes = e.encodedDataLength; r.end = e.timestamp; } });
  cdp.on("Network.loadingFailed", e => { const r = requests.get(e.requestId); if (r) { r.failed = e.errorText; r.canceled = e.canceled; } });
  page.on("console", m => { if (m.type() === "error") errors.push(m.text().slice(0, 300)); });
  page.on("pageerror", e => errors.push(String(e).slice(0, 300)));
  return { requests, errors, cdp };
}
function byKind(requests) {
  const totals = {};
  for (const r of requests.values()) {
    const k = kind(r.url, r.type);
    totals[k] ??= { requests: 0, bytes: 0, cached: 0 };
    totals[k].requests++; totals[k].bytes += r.bytes ?? 0; if (r.fromCache) totals[k].cached++;
  }
  totals.total = Object.values(totals).reduce((a, t) => ({ requests: a.requests + t.requests, bytes: a.bytes + t.bytes, cached: a.cached + t.cached }), { requests: 0, bytes: 0, cached: 0 });
  return totals;
}
const marks = page => page.evaluate(() => Object.fromEntries(performance.getEntriesByType("mark").filter(m => m.name.startsWith("breeze:")).map(m => [m.name, Math.round(m.startTime)])));
/** Walking controls are shown; for pose and cycle tests also wait until every chunk has joined the scene. */
const waitWalking = (page, timeout = 300000) => page.waitForSelector(".gully-controls", { timeout });
async function waitWorld(page, timeout = 900000) {
  await waitWalking(page, timeout);
  await page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout });
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

async function loadSuite(profile) {
  for (let run = 0; run < runs; run++) {
    const context = await browser.newContext(profileOptions[profile]);
    const page = await context.newPage();
    const { requests, errors } = await track(page, context);
    const entry = { profile, run, cold: null, warm: null };
    try {
      for (const visit of ["cold", "warm"]) {
        if (visit === "warm") requests.clear();
        const t0 = Date.now();
        await page.goto(base + "/?diagnostics&tier=balanced", { waitUntil: "domcontentloaded" });
        const html = Date.now() - t0;
        await waitWalking(page);
        const walkingAt = Date.now() - t0;
        const atWalking = byKind(requests);
        await page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout: 900000 });
        const worldMs = Date.now() - t0;
        await page.waitForTimeout(5000);
        const nav = await page.evaluate(() => { const n = performance.getEntriesByType("navigation")[0]; return n && { domContentLoaded: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd), transferSize: n.transferSize }; });
        entry[visit] = { htmlMs: html, walkingMs: walkingAt, worldMs, marks: await marks(page), navigation: nav, bytesAtWalking: atWalking, bytesAfter5s: byKind(requests),
          failed: [...requests.values()].filter(r => r.failed && !r.canceled).map(r => ({ url: r.url, error: r.failed })),
          largest: [...requests.values()].sort((a, b) => (b.bytes ?? 0) - (a.bytes ?? 0)).slice(0, 15).map(r => ({ url: r.url.replace(base, ""), bytes: r.bytes, cached: !!r.fromCache })) };
      }
    } catch (error) { entry.error = String(error); }
    entry.errors = errors;
    results.load.push(entry);
    console.log(`load ${profile} #${run}`, entry.error ?? `cold walking ${entry.cold?.walkingMs} ms (${(entry.cold?.bytesAtWalking.total.bytes / 1e6).toFixed(1)} MB), world ${entry.cold?.worldMs} ms (${(entry.cold?.bytesAfter5s.total.bytes / 1e6).toFixed(1)} MB); warm walking ${entry.warm?.walkingMs} ms`);
    await context.close();
  }
}

async function sample(page, seconds) {
  await page.evaluate(() => window.__breezePerf.reset());
  const since = await page.evaluate(() => performance.now());
  await page.waitForTimeout(seconds * 1000);
  return page.evaluate(since => ({ summary: window.__breezePerf.summary(since), snapshot: window.__breezePerf.snapshot() }), since);
}

async function poseSuite(profile) {
  // One load per run, then the map's own travel to each stop: every stop is sampled from its fixed arrival pose.
  for (let run = 0; run < runs; run++) {
    const context = await browser.newContext(profileOptions[profile]);
    const page = await context.newPage();
    const { errors } = await track(page, context);
    try {
      await page.goto(`${base}/runtime-preview/cypher?diagnostics&tier=balanced`, { waitUntil: "domcontentloaded" });
      await waitWorld(page);
      await page.waitForTimeout(3000);
    } catch (error) { results.poses.push({ profile, run, error: String(error), errors }); await context.close(); continue; }
    for (const stop of stops) {
      const entry = { profile, run, stop };
      try {
        if (stop !== "market") entry.arrivedAt = await travel(page, stop);
        await page.waitForTimeout(5000);
        Object.assign(entry, await sample(page, sampleSeconds));
        if (run === 0) await page.screenshot({ path: `${out}/${label}-${profile}-${stop}.png`, timeout: 120000 }).catch(e => { entry.screenshotError = String(e).slice(0, 200); });
      } catch (error) { entry.error = String(error); }
      entry.errors = [...errors];
      results.poses.push(entry);
      const p = entry.summary?.presentation;
      console.log(`pose ${profile} ${stop} #${run}`, entry.error ?? `p50 ${p.p50Ms.toFixed(1)} p95 ${p.p95Ms.toFixed(1)} p99 ${p.p99Ms.toFixed(1)} ms, ${p.frames} frames, calls ${entry.snapshot.stats.calls}, tris ${entry.snapshot.stats.triangles}, programs ${entry.snapshot.stats.programs}`);
    }
    await context.close();
  }
}

async function journeySuite(profile) {
  if (profile !== "desktop") return; // keyboard journey
  for (let run = 0; run < runs; run++) {
    const context = await browser.newContext(profileOptions[profile]);
    const page = await context.newPage();
    const { errors } = await track(page, context);
    const entry = { profile, run };
    try {
      await page.goto(`${base}/runtime-preview/cypher?diagnostics&tier=balanced`, { waitUntil: "domcontentloaded" });
      await waitWorld(page);
      await page.waitForTimeout(5000);
      await page.mouse.click(640, 200);
      await page.evaluate(() => window.__breezePerf.reset());
      const t0 = await page.evaluate(() => performance.now());
      await page.keyboard.down("KeyW"); await page.waitForTimeout(sampleSeconds * 500);
      const t1 = await page.evaluate(() => performance.now());
      await page.keyboard.down("Shift"); await page.waitForTimeout(sampleSeconds * 500);
      await page.keyboard.up("Shift"); await page.keyboard.up("KeyW");
      entry.walk = await page.evaluate(([a, b]) => window.__breezePerf.summary(a) && { presentation: (() => { const f = window.__breezePerf.frames.filter(x => x.at >= a && x.at < b).map(x => x.ms); return f; })() }, [t0, t1]);
      entry.walk = { frames: entry.walk.presentation.length, ...summ(entry.walk.presentation) };
      entry.sprint = await page.evaluate(b => window.__breezePerf.summary(b), t1);
      entry.endZ = await page.evaluate(() => window.__breezePerf.snapshot().pose.z);
    } catch (error) { entry.error = String(error); }
    entry.errors = errors;
    results.journey.push(entry);
    console.log(`journey ${profile} #${run}`, entry.error ?? `walk p95 ${entry.walk.p95Ms.toFixed(1)}, sprint p95 ${entry.sprint.presentation.p95Ms.toFixed(1)} ms, end z ${entry.endZ.toFixed(1)}`);
    await context.close();
  }
}
function summ(ms) {
  const s = [...ms].sort((a, b) => a - b), q = p => s[Math.min(s.length - 1, Math.floor(s.length * p))] ?? 0, mean = ms.reduce((a, b) => a + b, 0) / Math.max(1, ms.length);
  return { meanMs: mean, effectiveFps: mean ? 1000 / mean : 0, p50Ms: q(0.5), p95Ms: q(0.95), p99Ms: q(0.99), maxMs: s.at(-1) ?? 0, over50: ms.filter(v => v > 50).length };
}

async function travel(page, stop) {
  // Direct DOM clicks: at software-rendering frame rates the projected map labels never look "stable"
  // to Playwright's actionability checks, though they are on screen and clickable.
  await page.keyboard.press("KeyM");
  await page.waitForSelector(`[data-map-stop="${stop}"]`, { state: "attached", timeout: 180000 });
  await page.waitForTimeout(2000);
  await page.evaluate(id => document.querySelector(`[data-map-stop="${id}"]`).click(), stop);
  await page.waitForSelector(".cypher-map", { state: "detached", timeout: 300000 });
  await page.waitForTimeout(3000);
  return page.evaluate(() => window.__breezePerf.snapshot().pose);
}
async function cycleSuite(profile) {
  if (profile !== "desktop") return;
  const context = await browser.newContext(profileOptions[profile]);
  const page = await context.newPage();
  const { errors } = await track(page, context);
  const entry = { profile, snapshots: [] };
  try {
    await page.goto(`${base}/runtime-preview/cypher?diagnostics&tier=balanced`, { waitUntil: "domcontentloaded" });
    await waitWorld(page);
    await page.waitForTimeout(5000);
    const snap = async (cycle) => { const s = await page.evaluate(() => window.__breezePerf.snapshot()); entry.snapshots.push({ cycle, jsHeap: s.jsHeap, stats: s.stats, scene: s.scene }); };
    await snap(0);
    for (let cycle = 1; cycle <= cycles; cycle++) {
      for (const stop of ["events", "team", "aftermovie", "market"]) await travel(page, stop);
      await page.evaluate(() => window.gc?.());
      await snap(cycle);
      const last = entry.snapshots.at(-1);
      console.log(`cycle ${cycle}: heap ${(last.jsHeap?.used / 1e6).toFixed(1)} MB, geometries ${last.stats.geometries}, textures ${last.stats.textures}, programs ${last.stats.programs}`);
    }
  } catch (error) { entry.error = String(error); console.log("cycles failed", entry.error); }
  entry.errors = errors;
  results.cycles.push(entry);
  await context.close();
}

for (const profile of profiles) {
  if (suites.has("load")) await loadSuite(profile);
  if (suites.has("poses")) await poseSuite(profile);
  if (suites.has("journey")) await journeySuite(profile);
  if (suites.has("cycles")) await cycleSuite(profile);
}
await browser.close();
results.environment.finishedAt = new Date().toISOString();
const file = `${out}/${label}.json`;
await writeFile(file, JSON.stringify(results, null, 1));
console.log("wrote", file);

if (process.env.BREEZE_COMPARE) {
  const before = JSON.parse(await readFile(process.env.BREEZE_COMPARE, "utf8"));
  const median = values => { const s = values.filter(Number.isFinite).sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : NaN; };
  const rows = [];
  for (const profile of profiles) {
    const load = (r, visit, f) => median(r.load.filter(e => e.profile === profile && e[visit]).map(e => f(e[visit])));
    rows.push([profile, "cold MB at walking", load(before, "cold", v => v.bytesAtWalking.total.bytes / 1e6), load(results, "cold", v => v.bytesAtWalking.total.bytes / 1e6)]);
    rows.push([profile, "cold walking ms", load(before, "cold", v => v.walkingMs), load(results, "cold", v => v.walkingMs)]);
    rows.push([profile, "warm walking ms", load(before, "warm", v => v.walkingMs), load(results, "warm", v => v.walkingMs)]);
    for (const stop of stops) {
      const pose = (r, f) => median(r.poses.filter(e => e.profile === profile && e.stop === stop && e.summary).map(f));
      rows.push([profile, `${stop} p95 ms`, pose(before, e => e.summary.presentation.p95Ms), pose(results, e => e.summary.presentation.p95Ms)]);
      rows.push([profile, `${stop} draw calls`, pose(before, e => e.snapshot.stats.calls), pose(results, e => e.snapshot.stats.calls)]);
      rows.push([profile, `${stop} triangles`, pose(before, e => e.snapshot.stats.triangles), pose(results, e => e.snapshot.stats.triangles)]);
    }
  }
  console.log("\n| profile | metric | before | after |\n|---|---|---|---|");
  for (const [p, m, a, b] of rows) console.log(`| ${p} | ${m} | ${Number.isFinite(a) ? +a.toFixed(1) : "n/a"} | ${Number.isFinite(b) ? +b.toFixed(1) : "n/a"} |`);
}
