/** Production browser regression + R3F-rendered-frame measurements for the vertical slice.
 * GULLYVERSE_BASE_URL=http://localhost:3000 GULLYVERSE_MODE=production node scripts/perf-gullyverse.mjs
 * GULLYVERSE_PROFILES=desktop,mobile-emulated (default). Mobile emulation is NOT real device certification.
 */
import assert from "node:assert/strict";
import { mkdir, unlink, writeFile } from "node:fs/promises";
import os from "node:os";
import { chromium } from "playwright";

const base = process.env.GULLYVERSE_BASE_URL ?? "http://localhost:3000";
const profiles = (process.env.GULLYVERSE_PROFILES ?? "desktop,mobile-emulated").split(",");
const artifactDir = process.env.GULLYVERSE_ARTIFACT_DIR ?? ".gullyverse-artifacts";
await mkdir(artifactDir, { recursive: true });
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH ?? "C:/Program Files/Google/Chrome/Application/chrome.exe",
  headless: true,
});
const results = [];
const quantile = (sorted, q) => sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * q))] ?? 0;
function summarize(samples) {
  const ms = samples.map((s) => s.ms).sort((a, b) => a - b);
  const mean = ms.reduce((sum, n) => sum + n, 0) / Math.max(1, ms.length);
  return { frames: ms.length, meanMs: mean, meanFps: mean ? 1000 / mean : 0, p50Ms: quantile(ms, 0.5), p95Ms: quantile(ms, 0.95), p99Ms: quantile(ms, 0.99), maxMs: ms.at(-1) ?? 0, over16_67ms: ms.filter((v) => v > 16.67).length, over34ms: ms.filter((v) => v > 34).length, over50ms: ms.filter((v) => v > 50).length };
}
function executionSummary(samples, property) {
  const summary = summarize(samples.filter((s) => Number.isFinite(s[property])).map((s) => ({ ms: s[property] })));
  return { samples: summary.frames, meanMs: summary.meanMs, p95Ms: summary.p95Ms, p99Ms: summary.p99Ms, maxMs: summary.maxMs };
}
function phaseReport(diagnostics, longTasks) {
  const label = (s) => s.phase === "entrance" ? s.poseZ > -3 ? "entrance-framing" : s.poseZ > -38 ? "tunnel-travel" : "quarry-exit" : `${s.scene}:${s.phase}`;
  const groups = Object.groupBy(diagnostics.timeline, label);
  return Object.fromEntries(Object.entries(groups).map(([name, samples]) => [name, {
    frames: summarize(samples), cpuRenderSubmission: executionSummary(samples, "cpuRenderMs"), cpuCameraUpdate: executionSummary(samples, "cpuUpdateMs"),
    gpuRender: executionSummary(diagnostics.gpu.filter((s) => label(s) === name), "ms"),
    longTasks: longTasks.filter((task) => {
      const preceding = diagnostics.timeline.findLast((p) => p.at <= task.at);
      return preceding && label(preceding) === name;
    }),
  }]));
}
const waitLocal = (page, id) => page.waitForSelector(`[data-phase="local"][data-location="${id}"]`, { timeout: 60000 });
const pose = (page) => page.evaluate(() => ({ ...window.__gullyverse.runtime.pose }));
async function key(page, code, duration) { await page.keyboard.down(code); await page.waitForTimeout(duration); await page.keyboard.up(code); }
async function mapTravel(page, id) {
  await page.getByRole("button", { name: /^Map/ }).click();
  await page.getByRole("button", { name: id === "hub" ? "Gullyverse hub" : "Aftermovie Travel" }).click();
  await waitLocal(page, id);
}
async function capture(page, name) {
  return page.evaluate((name) => {
    const d = window.__gullyverse;
    const samples = d.frames.filter((s) => s.phase === "local"); d.frames.length = 0;
    return { name, samples, stats: { ...d.stats }, quality: d.runtime.getSnapshot().quality };
  }, name);
}
async function measureMovement(page, name) {
  await page.evaluate(() => { window.__gullyverse.frames.length = 0; });
  for (const [code, duration] of [["KeyD", 800], ["KeyA", 1600], ["KeyD", 1600], ["KeyA", 1600]]) await key(page, code, duration);
  const data = await capture(page, name);
  return { name, ...summarize(data.samples), cpuRenderSubmission: executionSummary(data.samples, "cpuRenderMs"), stats: data.stats, quality: data.quality };
}
async function measureResponse(page) {
  // Arm the listener before sending the key; otherwise CDP can deliver the
  // event before an asynchronous page.evaluate installs its listener.
  await page.evaluate(() => { window.__responsePromise = new Promise((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error("Movement did not respond")), 5000);
    window.addEventListener("keydown", function onKey(event) {
      if (event.code !== "KeyD") return;
      window.removeEventListener("keydown", onKey);
      const start = performance.now(), x = window.__gullyverse.runtime.pose.x;
      let frames = 0;
      const sample = () => {
        frames++;
        if (Math.abs(window.__gullyverse.runtime.pose.x - x) > 0.00001) { clearTimeout(timeout); resolve({ ms: performance.now() - start, observationFrames: frames }); }
        else requestAnimationFrame(sample);
      };
      requestAnimationFrame(sample);
    });
  }); });
  await page.keyboard.down("KeyD"); const result = await page.evaluate(() => window.__responsePromise); await page.keyboard.up("KeyD"); return result;
}
async function run(profile) {
  console.log(`[${profile}] cold load and entrance`);
  const mobile = profile === "mobile-emulated";
  const context = await browser.newContext(mobile ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { viewport: { width: 1366, height: 768 }, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const errors = [];
  const expectedLocalTelemetry404s = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() !== "error") return;
    const url = message.location().url ?? "";
    // Existing Vercel analytics scripts are supplied by Vercel's edge, not
    // `next start`. Record those known localhost 404s separately; do not
    // suppress missing scene assets, shader errors or application errors.
    if (["localhost", "127.0.0.1"].includes(new URL(base).hostname) && /\/_vercel\/(insights|speed-insights)\/script\.js$/.test(url)) expectedLocalTelemetry404s.push(url);
    else errors.push(`${message.text()} ${url}`);
  });
  const cdp = await context.newCDPSession(page);
  if (mobile) await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  await page.addInitScript(() => {
    window.__flow = { phases: [], longTasks: [], lifecycle: [], starts: performance.now() };
    for (const name of ["visibilitychange", "freeze", "resume"]) document.addEventListener(name, () => window.__flow.lifecycle.push({ name, hidden: document.hidden, at: performance.now() }));
    new PerformanceObserver((list) => { for (const entry of list.getEntries()) window.__flow.longTasks.push({ at: entry.startTime, ms: entry.duration }); }).observe({ type: "longtask", buffered: true });
  });
  const start = Date.now();
  await page.goto(`${base}/?diagnostics`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector('[data-phase="landing"]', { timeout: 60000 });
  const landingMs = Date.now() - start;
  await page.evaluate(() => {
    const runtime = window.__gullyverse.runtime;
    const record = () => window.__flow.phases.push({ at: performance.now(), ...runtime.getSnapshot() });
    record(); runtime.subscribe(record);
  });
  const originalCanvas = await page.locator("canvas").evaluateHandle((c) => c);
  await page.keyboard.down("KeyW"); await page.waitForTimeout(150); await page.keyboard.up("KeyW"); assert.equal((await pose(page)).z, 8);
  await page.screenshot({ path: `${artifactDir}/${profile}-landing.png` });
  const enterAt = Date.now();
  if (mobile) await page.getByRole("button", { name: "Enter Gullyverse" }).tap();
  else await page.keyboard.press("Enter");
  await waitLocal(page, "hub");
  const entranceMs = Date.now() - enterAt;
  await page.screenshot({ path: `${artifactDir}/${profile}-hub.png` });
  const movement = [await measureMovement(page, "hub-movement")];
  const inputResponse = { hub: await measureResponse(page) };
  console.log(`[${profile}] physical Aftermovie route`);
  // Recenter laterally; this is ordinary movement, not test teleportation.
  const position = await pose(page);
  if (Math.abs(position.x) > 0.4) await key(page, position.x > 0 ? "KeyA" : "KeyD", Math.abs(position.x) / 4.2 * 1000);
  const routeAt = Date.now();
  await page.keyboard.down("KeyW");
  await page.waitForSelector('[data-phase="departure"]', { timeout: 12000 });
  await page.keyboard.up("KeyW");
  const committedAt = Date.now();
  await waitLocal(page, "aftermovie");
  const coldTravelMs = Date.now() - committedAt;
  const approachMs = committedAt - routeAt;
  assert.equal(new URL(page.url()).pathname, "/aftermovie");
  assert.equal(await page.evaluate((c) => document.querySelector("canvas") === c, originalCanvas), true);
  await page.waitForTimeout(10000); // measurement stabilization, never part of navigation
  movement.push(await measureMovement(page, "aftermovie-movement"));
  inputResponse.aftermovie = await measureResponse(page);
  await page.screenshot({ path: `${artifactDir}/${profile}-aftermovie.png` });
  const beforePlay = await pose(page);
  console.log(`[${profile}] playback, return, repeat travel and history`);
  let rangeRequest = null;
  const recordMovie = (request) => { if (request.url().endsWith("/after-movie.mp4")) rangeRequest = request.headers()["range"] ?? "no range header"; };
  page.on("request", recordMovie);
  await page.getByRole("button", { name: "Play Aftermovie", exact: true }).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.movieActions?.status().currentTime > 0.1, null, { timeout: 30000 });
  await page.keyboard.press("Escape");
  await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().movie);
  await page.waitForTimeout(1000);
  assert.ok(Math.abs((await pose(page)).x - beforePlay.x) < 0.01);
  assert.ok(Math.abs((await pose(page)).y - beforePlay.y) < 0.01);
  assert.ok(rangeRequest, "Preserved movie should request media only after play");
  page.off("request", recordMovie);
  // Walk through the deliberately bounded return route.
  const after = await pose(page);
  if (Math.abs(after.x) > 3) await key(page, after.x > 0 ? "KeyA" : "KeyD", (Math.abs(after.x) - 1) / 4.2 * 1000);
  await page.keyboard.down("KeyS"); await page.waitForSelector('[data-phase="departure"]', { timeout: 10000 }); await page.keyboard.up("KeyS");
  await waitLocal(page, "hub"); assert.equal(new URL(page.url()).pathname, "/");
  const mapAt = Date.now(); await mapTravel(page, "aftermovie"); const warmMapTravelMs = Date.now() - mapAt;
  await page.goBack(); await waitLocal(page, "hub");
  await page.goForward(); await waitLocal(page, "aftermovie");
  assert.equal(await page.evaluate((c) => document.querySelector("canvas") === c, originalCanvas), true);
  await page.setViewportSize(mobile ? { width: 844, height: 390 } : { width: 1024, height: 700 });
  await page.waitForTimeout(400);
  const statsAfterRepeat = await page.evaluate(() => ({ ...window.__gullyverse.stats }));
  // Interrupted held input must not resume after a blur/focus without a fresh press.
  await page.keyboard.down("KeyD"); await page.waitForTimeout(100);
  await page.evaluate(() => window.dispatchEvent(new Event("blur")));
  const blurPose = await pose(page); await page.waitForTimeout(250);
  assert.equal((await pose(page)).x, blurPose.x);
  await page.evaluate(() => window.dispatchEvent(new Event("focus"))); await page.waitForTimeout(250);
  assert.equal((await pose(page)).x, blurPose.x); await page.keyboard.up("KeyD");
  // Actual background/foreground lifecycle with a second tab.
  // Playwright enables focused-page emulation by default; disable it here or
  // bringToFront never produces a meaningful page visibility test.
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: false });
  await page.keyboard.down("KeyD"); await page.waitForTimeout(100);
  const tab = await context.newPage(); await tab.goto("about:blank"); await tab.bringToFront(); await page.waitForTimeout(400);
  const backgroundVisibilityObserved = await page.evaluate(() => document.hidden);
  const backgroundPose = await pose(page);
  await page.waitForTimeout(250);
  if (backgroundVisibilityObserved) assert.equal((await pose(page)).x, backgroundPose.x);
  // Request actual freezing while the document is in the background, not visible.
  await cdp.send("Page.setWebLifecycleState", { state: "frozen" });
  await new Promise((resolve) => setTimeout(resolve, 400));
  await cdp.send("Page.setWebLifecycleState", { state: "active" });
  await page.bringToFront(); await tab.close();
  const lifecycle = await page.evaluate(() => window.__flow.lifecycle);
  const freezeObserved = lifecycle.some((e) => e.name === "freeze");
  const resumeObserved = lifecycle.some((e) => e.name === "resume");
  const resumed = await pose(page);
  await page.waitForTimeout(300);
  if (backgroundVisibilityObserved || freezeObserved) assert.equal((await pose(page)).x, resumed.x, "A held key must clear on observed browser background/freeze/resume");
  await page.keyboard.up("KeyD");
  // Listener regression is still checked even if a browser cannot expose true freezing.
  await page.keyboard.down("KeyD"); await page.waitForTimeout(100);
  await page.evaluate(() => document.dispatchEvent(new Event("freeze")));
  const syntheticFrozen = await pose(page); await page.waitForTimeout(250); assert.equal((await pose(page)).x, syntheticFrozen.x);
  await page.evaluate(() => document.dispatchEvent(new Event("resume")));
  await page.waitForTimeout(250); assert.equal((await pose(page)).x, syntheticFrozen.x); await page.keyboard.up("KeyD");
  if (mobile) {
    const before = await pose(page); const button = page.getByRole("button", { name: "Walk left" }); const box = await button.boundingBox();
    assert.ok(box);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: box.x + box.width / 2, y: box.y + box.height / 2 }] });
    await page.waitForTimeout(450);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    assert.ok((await pose(page)).x < before.x - 0.5, "Touch movement must reach shared input axes");
    await page.getByRole("button", { name: /^Map/ }).tap(); await page.getByRole("button", { name: "Close map" }).tap();
    const beforeLook = await pose(page);
    await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: 420, y: 160 }] });
    await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: 475, y: 170 }] });
    await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await page.waitForTimeout(100);
    assert.ok(Math.abs((await pose(page)).yaw - beforeLook.yaw) > 0.05, "Touch drag must reach the look axes");
  }
  const main = await page.evaluate(() => {
    const d = window.__gullyverse;
    return { renderer: d.renderer, flow: window.__flow, heapMB: performance.memory?.usedJSHeapSize / 1048576,
      diagnostics: { timeline: d.timeline, gpu: d.gpu, phases: d.phases, preparations: d.preparations, memory: d.memory, gpuTimer: d.gpuTimer, discardedGpuQueries: d.discardedGpuQueries },
      resources: performance.getEntriesByType("resource").filter((r) => /\.(glb|webp|png|jpe?g|js)(\?|$)/.test(r.name)).map((r) => ({ name: new URL(r.name).pathname, at: r.startTime, durationMs: r.duration, requestMs: r.responseEnd - r.requestStart, transferBytes: r.transferSize, encodedBodyBytes: r.encodedBodySize, decodedBodyBytes: r.decodedBodySize })),
    };
  });
  const coldCompile = main.diagnostics.preparations.find((p) => p.name === "shader-compilation" && p.scene === "aftermovie" && p.serial === 1);
  const coldDraw = main.diagnostics.timeline.find((f) => f.scene === "aftermovie" && f.phase === "covered" && Number.isFinite(f.cpuRenderMs));
  assert.ok(coldCompile && coldDraw && coldDraw.at >= coldCompile.at + coldCompile.ms, "Critical shaders must finish before the destination's first actual draw");
  console.log(`[${profile}] direct URL, reduced motion and fallback`);
  await originalCanvas.dispose();
  // Warm direct URL: short loading/arrival; no landing/entrance phase.
  const directAt = Date.now(); await page.goto(`${base}/aftermovie?diagnostics`, { waitUntil: "domcontentloaded" }); await waitLocal(page, "aftermovie");
  const directMs = Date.now() - directAt;
  const directFrames = await page.evaluate(() => window.__gullyverse.frames.map((f) => f.phase));
  assert.equal(directFrames.includes("entrance"), false);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await mapTravel(page, "hub"); await mapTravel(page, "aftermovie");
  assert.ok(await page.evaluate(() => window.__gullyverse.runtime.reduced));
  await page.getByRole("button", { name: "Use without 3D" }).click(); assert.equal(await page.locator("canvas").count(), 0);
  assert.equal(await page.locator("video[controls]").count(), 1);
  assert.equal(await page.getByRole("navigation", { name: "Festival information" }).count(), 1);
  const result = { profile, mode: process.env.GULLYVERSE_MODE ?? "unspecified", viewport: mobile ? "390x844; landscape 844x390" : "1366x768; resize 1024x700", cpuThrottle: mobile ? 4 : 1, renderer: main.renderer, browser: browser.version(), cpu: os.cpus()[0]?.model, platform: `${os.platform()} ${os.release()}`, timings: { landingMs, entranceMs, approachMs, coldTravelMs, warmMapTravelMs, directMs }, inputResponse, backgroundVisibilityObserved, movement, statsAfterRepeat, mediaRange: rangeRequest, heapMB: main.heapMB, longTasks: { count: main.flow.longTasks.length, maxMs: Math.max(0, ...main.flow.longTasks.map((t) => t.ms)) }, phases: main.flow.phases, errors, checks: ["cold landing", "controlled entrance", "hub movement", "physical Aftermovie threshold", "hidden handoff", "bounded Aftermovie movement", "video playback + Escape", "physical hub return", "map", "repeat navigation", "persistent Canvas", "back/forward", "warm direct URL", "resize", "blur/focus held-key interruption", "background tab/restore", "reduced motion", "2D fallback", ...(mobile ? ["tap entrance", "touch movement", "touch drag look", "touch map"] : [])] };
  result.expectedLocalTelemetry404s = expectedLocalTelemetry404s;
  result.phasePerformance = phaseReport(main.diagnostics, main.flow.longTasks);
  result.preparation = main.diagnostics.preparations;
  result.memoryTrend = main.diagnostics.memory;
  result.gpuTiming = { capability: main.diagnostics.gpuTimer, samples: main.diagnostics.gpu.length, discarded: main.diagnostics.discardedGpuQueries };
  result.resources = main.resources;
  result.lifecycle = { backgroundVisibilityObserved, freezeObserved, resumeObserved, events: lifecycle };
  result.checks.push("freeze/resume listener regression", ...(backgroundVisibilityObserved ? ["actual tab visibility clears held input"] : []), ...(freezeObserved && resumeObserved ? ["actual browser freeze/resume"] : []));
  result.checks.push("first destination draw waits for shader preparation");
  await writeFile(`${artifactDir}/${profile}-diagnostics.json`, JSON.stringify(main, null, 2));
  assert.deepEqual(errors, [], "Browser errors must be resolved");
  await context.close(); return result;
}
async function edgeCases() {
  console.log("[edge cases] cold direct URL, delayed/failing assets, interrupted travel, residency and context loss");
  const context = await browser.newContext({ viewport: { width: 1366, height: 768 } });
  const page = await context.newPage();
  await page.route("**/models/Man.glb", async (route) => { await new Promise((resolve) => setTimeout(resolve, 2500)); await route.continue(); });
  await page.goto(`${base}/aftermovie?diagnostics`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector('[data-phase="boot"]'); await page.waitForTimeout(300);
  assert.equal(await page.evaluate(() => window.__gullyverse?.runtime.opacity ?? 1), 1, "Cold destination stays covered");
  await page.evaluate(() => {
    window.__earlyContextExtension = document.querySelector("canvas").getContext("webgl2").getExtension("WEBGL_lose_context");
    if (!window.__earlyContextExtension) throw new Error("Context loss extension unavailable");
    window.__earlyContextExtension.loseContext();
  });
  await page.waitForSelector('[data-phase="context-lost"]');
  await page.evaluate(() => window.__earlyContextExtension.restoreContext());
  assert.equal(await page.evaluate(() => window.__gullyverse.runtime.opacity), 1, "Restoring an incomplete scene stays covered");
  await waitLocal(page, "aftermovie");
  assert.equal(await page.getByRole("button", { name: "Enter Gullyverse" }).count(), 0);
  await page.unroute("**/models/Man.glb");
  await mapTravel(page, "hub");
  await page.getByRole("button", { name: /^Map/ }).click(); await page.getByRole("button", { name: "Aftermovie Travel" }).click();
  // A URL change supersedes an already committed trip through the shared model.
  await page.evaluate(() => { history.pushState(null, "", "/?diagnostics"); window.dispatchEvent(new PopStateEvent("popstate")); });
  await waitLocal(page, "hub");
  const counts = [];
  const cdp = await context.newCDPSession(page); await cdp.send("Performance.enable");
  for (let i = 0; i < 10; i++) {
    await mapTravel(page, "aftermovie"); await page.waitForTimeout(1200);
    const raw = await cdp.send("Performance.getMetrics");
    await cdp.send("HeapProfiler.collectGarbage");
    const collected = await cdp.send("Performance.getMetrics");
    const retained = await page.evaluate(() => {
      const d = window.__gullyverse;
      const snapshot = { memory: d.memory.at(-1), diagnosticSamples: { frames: d.frames.length, timeline: d.timeline.length, gpu: d.gpu.length, preparations: d.preparations.length, phases: d.phases.length, memory: d.memory.length } };
      // Record retained observer data before clearing it; a second GC reading
      // separates intentionally retained diagnostic samples from scene residency.
      for (const key of ["frames", "timeline", "gpu", "preparations", "phases", "memory"]) d[key].length = 0;
      d.currentFrame = null; return snapshot;
    });
    await cdp.send("HeapProfiler.collectGarbage");
    const cleared = await cdp.send("Performance.getMetrics");
    const heap = (metrics) => Object.fromEntries(metrics.metrics.filter((m) => ["JSHeapUsedSize", "JSHeapTotalSize", "Nodes", "Documents"].includes(m.name)).map((m) => [m.name, m.value]));
    counts.push(await page.evaluate(({ raw, collected, cleared, retained }) => ({ ...window.__gullyverse.stats, rawHeap: raw, collectedHeap: collected, clearedDiagnosticsHeap: cleared, ...retained }), { raw: heap(raw), collected: heap(collected), cleared: heap(cleared), retained }));
    await mapTravel(page, "hub");
  }
  await writeFile(`${artifactDir}/residency.json`, JSON.stringify(counts, null, 2));
  assert.ok(counts.at(-1).textures <= counts[0].textures + 1, "Textures must stay bounded across ten trips");
  assert.ok(counts.at(-1).geometries <= counts[0].geometries + 4, "Geometry residency must stay bounded across ten trips");
  const recoveredCanvas = await page.locator("canvas").evaluateHandle((c) => c);
  const beforeLoss = await pose(page);
  await page.evaluate(() => {
    window.__contextExtension = document.querySelector("canvas").getContext("webgl2").getExtension("WEBGL_lose_context");
    if (!window.__contextExtension) throw new Error("Context loss extension unavailable");
    window.__contextExtension.loseContext();
  });
  await page.waitForSelector('[data-phase="context-lost"]');
  assert.equal(await page.evaluate(() => window.__gullyverse.runtime.opacity), 1);
  await page.evaluate(() => window.__contextExtension.restoreContext());
  await waitLocal(page, "hub"); assert.deepEqual(await pose(page), beforeLoss);
  assert.equal(await page.evaluate((c) => document.querySelector("canvas") === c, recoveredCanvas), true);
  await mapTravel(page, "aftermovie");
  const beforeStageLoss = await pose(page);
  await page.getByRole("button", { name: "Play Aftermovie", exact: true }).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.movieActions?.status().currentTime > 0.1);
  await page.evaluate(() => window.__contextExtension.loseContext());
  await page.waitForSelector('[data-phase="context-lost"]');
  await page.evaluate(() => window.__contextExtension.restoreContext());
  await waitLocal(page, "aftermovie"); assert.deepEqual(await pose(page), beforeStageLoss);
  await page.getByRole("button", { name: "Play Aftermovie", exact: true }).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.movieActions?.status().currentTime > 0.1);
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Use without 3D" }).click();
  assert.equal(await page.locator("video[controls]").count(), 1);
  await recoveredCanvas.dispose();
  await context.close();
  const failureContext = await browser.newContext(); const failurePage = await failureContext.newPage();
  await failurePage.route("**/models/Man.glb", (route) => route.abort());
  await failurePage.goto(`${base}/aftermovie`, { waitUntil: "domcontentloaded" });
  await failurePage.waitForSelector('[data-phase="error"]', { timeout: 60000 });
  assert.equal(await failurePage.locator("video[controls]").count(), 1);
  await failureContext.close();
  return { checks: ["cold direct entry skips tunnel", "delayed critical asset stays covered", "context loss during delayed initial preparation restores behind cover", "superseding URL during travel", "ten round trips retain bounded textures/geometries", "raw and collected JS heap recorded over ten trips", "hub context loss restores same Canvas and pose", "stage context loss during playback restores walking pose", "playback works again after restoration", "manual 2D exit works after recovery", "failed critical asset offers 2D"], roundTrips: counts };
}
async function captureBlockoutViewpoints(profile) {
  // Screenshots can stall the main thread/read back the GPU. Capture moving
  // tunnel viewpoints in a separate journey, outside performance measurements.
  const mobile = profile === "mobile-emulated";
  const context = await browser.newContext(mobile ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true } : { viewport: { width: 1366, height: 768 } });
  try {
    const page = await context.newPage();
    await page.goto(`${base}/?diagnostics`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector('[data-phase="landing"]');
    await page.getByRole("button", { name: "Enter Gullyverse" }).click();
    await page.waitForFunction(() => window.__gullyverse.runtime.pose.z < -5);
    await page.screenshot({ path: `${artifactDir}/${profile}-tunnel-blockout.png` });
    await page.waitForFunction(() => window.__gullyverse.runtime.pose.z < -39);
    await page.screenshot({ path: `${artifactDir}/${profile}-exit-blockout.png` });
    await waitLocal(page, "hub");
  } finally { await context.close(); }
}
try {
  for (const profile of profiles) {
    const result = await run(profile); results.push(result);
    console.log(JSON.stringify(result));
    await writeFile(`${artifactDir}/results.json`, JSON.stringify(results, null, 2));
  }
  for (const profile of profiles) await captureBlockoutViewpoints(profile);
  const edges = await edgeCases();
  await writeFile(`${artifactDir}/edge-cases.json`, JSON.stringify(edges, null, 2));
  await unlink(`${artifactDir}/failure.txt`).catch((error) => { if (error.code !== "ENOENT") throw error; });
  console.log(JSON.stringify(edges));
} catch (error) { console.error(error); await writeFile(`${artifactDir}/failure.txt`, String(error.stack ?? error)); process.exitCode = 1; }
finally { await browser.close(); }
