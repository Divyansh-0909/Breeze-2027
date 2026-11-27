/**
 * Captures one frame per gully zone (paired with references/<zone>.*) plus renderer counters, for the
 * Antigravity visual review loop (CLAUDE.md).
 *
 *   CHROME_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe" \
 *   node -r ./perf/results-2026-11-26-gtx1650/gpu-flag.cjs scripts/capture-zones.mjs <phase> [profile] [extra query]
 *
 * profile: desktop (1440x900, the default) or mobile (390x844, DPR 3, touch). Writes
 * screenshots/<phase>/<zone>[-mobile].png and screenshots/<phase>/metrics[-mobile].json.
 */
import { mkdir, writeFile } from "node:fs/promises";
import { chromium } from "playwright";

const base = process.env.BREEZE_BASE_URL ?? "http://127.0.0.1:3000";
const phase = process.argv[2] ?? "baseline";
const profile = process.argv[3] ?? "desktop";
const extra = process.argv[4] ?? "";
const zones = (process.env.BREEZE_ZONES ?? "01-entrance-gate:approach,02-courtyard-plaza:plaza,03-triptych-screen:aftermovie,04-accommodation:accommodation,05-organising-mural:team,06-events-wall:events,07-contact-desk:contact")
  .split(",").map(pair => pair.split(":"));
const out = `screenshots/${phase}`;
await mkdir(out, { recursive: true });
const options = profile === "mobile"
  ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }
  : { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 };
const suffix = profile === "mobile" ? "-mobile" : "";
const browser = await chromium.launch({ args: ["--autoplay-policy=no-user-gesture-required", "--ignore-gpu-blocklist"] });
const metrics = { phase, profile, base, at: new Date().toISOString(), zones: {} };
for (const [zone, start] of zones) {
  const context = await browser.newContext(options);
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(String(e).slice(0, 300)));
  page.on("console", m => { if (m.type() === "error") errors.push(m.text().slice(0, 300)); });
  try {
    await page.goto(`${base}/runtime-preview/cypher?start=${start}&diagnostics${extra ? "&" + extra : ""}`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".gully-controls", { timeout: 300000 });
    await page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout: 300000 });
    // Settle (curtain fade, probes streaming in), then sample frames for the counters.
    await page.waitForTimeout(6000);
    await page.evaluate(() => window.__breezePerf?.reset());
    const since = await page.evaluate(() => performance.now());
    await page.waitForTimeout(4000);
    const stats = await page.evaluate(since => {
      const perf = window.__breezePerf;
      if (!perf) return null;
      const s = perf.summary(since);
      return { renderer: perf.renderer, stats: perf.stats(), fps: s.presentation.effectiveFps, p95Ms: s.presentation.p95Ms,
        gpuP50Ms: s.gpu.frames ? s.gpu.p50Ms : null, maxCalls: Math.max(...perf.frames.filter(f => f.at >= since).map(f => f.calls)) };
    }, since);
    await page.screenshot({ path: `${out}/${zone}${suffix}.png` });
    metrics.zones[zone] = { start, ...stats, errors };
    console.log(zone, stats ? `calls ${stats.stats.calls} (max ${stats.maxCalls}) tris ${Math.round(stats.stats.triangles / 1000)}k fps ${stats.fps.toFixed(1)} tier ${stats.stats.tier}` : "no stats", errors.length ? `errors ${errors.length}` : "");
  } catch (error) {
    metrics.zones[zone] = { start, error: String(error), errors };
    console.log(zone, "FAILED", String(error).slice(0, 200));
  }
  await context.close();
}
await writeFile(`${out}/metrics${suffix}.json`, JSON.stringify(metrics, null, 1));
await browser.close();
