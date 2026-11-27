/**
 * Prints the per-chunk / per-material draw-call breakdown (gully-diagnostics.tsx drawBreakdown) for map stops.
 *   CHROME_PATH=... node -r ./perf/results-2026-11-26-gtx1650/gpu-flag.cjs scripts/draw-breakdown.mjs approach,plaza [mobile]
 */
import { chromium } from "playwright";

const base = process.env.BREEZE_BASE_URL ?? "http://127.0.0.1:3001";
const stops = (process.argv[2] ?? "approach,plaza").split(",");
const mobile = process.argv[3] === "mobile";
const browser = await chromium.launch({ args: ["--ignore-gpu-blocklist"] });
for (const stop of stops) {
  const context = await browser.newContext(mobile
    ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true }
    : { viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto(`${base}/runtime-preview/cypher?start=${stop}&diagnostics`, { waitUntil: "domcontentloaded" });
  await page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout: 600000 });
  await page.waitForTimeout(5000);
  const result = await page.evaluate(() => ({ breakdown: window.__breezePerf.breakdown(), calls: window.__breezePerf.stats().calls, wings: window.__breezeWings && { objects: window.__breezeWings.objects.length, hidden: window.__breezeWings.hidden } }));
  console.log(`## ${stop}${mobile ? " (mobile)" : ""}: renderer calls ${result.calls} wings ${JSON.stringify(result.wings)}`);
  console.log(JSON.stringify(result.breakdown, null, 1));
  await context.close();
}
await browser.close();
