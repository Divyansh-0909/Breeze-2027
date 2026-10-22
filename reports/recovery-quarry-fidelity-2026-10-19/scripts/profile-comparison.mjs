import {mkdir, readFile, writeFile} from "node:fs/promises";
import {launch, context, ready, view, unfix, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const root = "reports/recovery-quarry-fidelity-2026-10-19", browser = await launch();
await mkdir(root + "/raw", {recursive: true});
const build = (await readFile(".next/BUILD_ID", "utf8")).trim();
const loads = [], windows = [], lod = [], errors = [];
let current;
async function sample(page, mode, name) {
  const before = await details(page), start = await page.evaluate(() => performance.now());
  await page.waitForTimeout(8000);
  const end = await page.evaluate(() => performance.now());
  const frames = await page.evaluate(({start, end}) => window.__gullyverse.timeline.filter(frame => frame.at >= start && frame.at <= end), {start, end});
  const times = frames.map(frame => frame.ms).sort((a, b) => a - b), q = fraction => times[Math.floor((times.length - 1) * fraction)];
  windows.push({mode, name, count: times.length, duration: end - start, fps: times.length * 1000 / (end - start),
    p50: q(0.5), p95: q(0.95), p99: q(0.99), before, after: await details(page)});
  console.log(mode, name, windows.at(-1).fps);
}
try {
  for (const mode of ["c51", "c8", "recovered", "material", "corrected"]) {
    current = await context(browser, {viewport: {width: 1366, height: 900}, deviceScaleFactor: 0.5});
    await current.unrouteAll();
    const page = await current.newPage(), cdp = await current.newCDPSession(page);
    await cdp.send("Network.enable"); await cdp.send("Network.setCacheDisabled", {cacheDisabled: false});
    await cdp.send("Network.setBlockedURLs", {urls: ["*/api/*", "*recovery-verification.invalid/*", "*vercel-insights.com/*", "*google-analytics.com/*", "*googletagmanager.com/*"]});
    await cdp.send("Network.clearBrowserCache");
    const selectors={c51:"",c8:"scanned-material-multi",recovered:"scanned-composition",material:"material-fidelity",corrected:"geology-fidelity"};
    const url="http://127.0.0.1:3000/?arrival=hub&diagnostics"+(selectors[mode]?"&quarryReview="+selectors[mode]:"");
    for (const cache of ["cold", "warm"]) {
      const responses = [], listener = event => responses.push({url: event.response.url, fromDiskCache: event.response.fromDiskCache, status: event.response.status});
      cdp.on("Network.responseReceived", listener);
      const started = Date.now(); await page.goto(url);
      await page.waitForFunction(() => window.__gullyverse?.runtime);
      await page.evaluate(() => window.__gullyverse.runtime.setQuality(3)); await ready(page);
      const resources = await page.evaluate(() => performance.getEntriesByType("resource").map(entry => ({name: entry.name, transferSize: entry.transferSize, encodedBodySize: entry.encodedBodySize, duration: entry.duration})));
      const navigation = await page.evaluate(() => performance.getEntriesByType("navigation")[0].toJSON());
      loads.push({mode, cache, readyMs: Date.now() - started, totalTransferBytes: resources.reduce((n, row) => n + row.transferSize, navigation.transferSize),
        c8EncodedBytes: resources.filter(row => row.name.includes("/recovered-c8-material/")).reduce((n, row) => n + row.encodedBodySize, 0),
        resources, responses, preparations: await page.evaluate(() => window.__gullyverse.preparations), data: await details(page),
        material: await page.evaluate(() => window.__wallPreview.materialDiagnostics?.()), composition: await page.evaluate(() => window.__wallPreview.compositionDiagnostics?.())});
      cdp.off("Network.responseReceived", listener); console.log(mode, cache, loads.at(-1).totalTransferBytes);
    }
    await view(page, [-18, 1.72, -55], [-44, 8, -65], {fixed: true, quality: 3}); await sample(page, mode, "visitor-wall");
    await view(page, [0, 1.72, -51], [0, 6.6, -92.7], {fixed: true, quality: 3}); await sample(page, mode, "hub");
    await unfix(page); await page.evaluate(() => { const r = window.__gullyverse.runtime; r.pose = {x: 0, y: 1.72, z: -51, yaw: 0, pitch: 0.1}; r.clearInput(); r.setQuality(3); });
    await page.getByRole("button", {name: /^Map/}).click(); await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().mapStage === "open");
    await sample(page, mode, "aerial-map");
    await page.getByRole("button", {name: "Aftermovie", exact: true}).click();
    await page.waitForFunction(() => window.__gullyverse?.runtime?.getSnapshot().scene === "aftermovie" && window.__gullyverse.runtime.getSnapshot().phase === "local", null, {timeout: 90000});
    await ready(page); await view(page, [-10.5, 1.72, -110.8], [-12, 5.9, -128.3], {fixed: true, quality: 3}); await sample(page, mode, "aftermovie-stage");
    if (mode === "corrected") {
      // Deliberately non-public inspection cameras. Screen-space LOD selection
      // remains automatic, using original C5.1 thresholds and hysteresis.
      await page.goto(url); await ready(page);
      for (const [label, position] of [["far", [220, 55, 90]], ["middle", [15, 13, -40]], ["near", [-38, 7, -62]]]) {
        await view(page, position, [-45, 10, -66], {fixed: true, quality: 0});
        await page.waitForTimeout(400);
        const data = await details(page); lod.push({label, position, nonPublicInspection: true, data, material: await page.evaluate(() => window.__wallPreview.materialDiagnostics())});
        await page.addStyleTag({content: "[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
        await page.screenshot({path: `${root}/screenshots/automatic-lod-${label}.png`});
      }
    }
    await current.close(); current = null;
  }
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1; }
finally {
  await current?.close(); await browser.close();
  await writeFile(root + "/raw/matched-performance.json", JSON.stringify({status: errors.length ? "FAIL" : "PASS", build,
    method: "Actual production browser; 1366x900, requested/effective DPR 0.5, quality 3. Eight-second settled windows. HTTP cache enabled, cold cache explicitly cleared, API/analytics blocked through CDP. Run alone after all tests/authoring. Automatic LOD stills are separate non-public Q0 diagnostics.",
    limitations: "SwiftShader software diagnostics only; no physical GPU certification, Internet loading model, confidence intervals or 60 FPS claim.",
    browser: browser.version(), loads, windows, lod, errors}, null, 2));
}
