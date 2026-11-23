/**
 * Functional regression checks for the performance changes (run separately from benchmarks):
 *   BREEZE_BASE_URL=http://127.0.0.1:3000 node scripts/perf-functional.mjs
 * 1. A late chunk that fails (plaza GLB blocked) leaves the visitor walking the arrival half.
 * 2. WebGL context loss and restore: the scene recovers and walking resumes.
 * 3. Touch (Pixel 7 emulation): the movement pad moves the visitor.
 * 4. The Aftermovie screen loops after the world streams; Watch restarts it from 0 at full quality.
 * WebM stands in for the MP4s: Playwright's Chromium has no H.264 decoder.
 */
import { chromium, devices } from "playwright";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";

const base = process.env.BREEZE_BASE_URL ?? "http://127.0.0.1:3000";
const webm = "perf-results/aftermovie-test.webm";
if (!existsSync(webm)) {
  mkdirSync("perf-results", { recursive: true });
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", "public/after-movie.mp4", "-t", "40", "-vf", "scale=480:-2", "-c:v", "libvpx-vp9", "-b:v", "300k",
    "-deadline", "realtime", "-cpu-used", "8", "-c:a", "libopus", "-b:a", "64k", webm]);
}
const browser = await chromium.launch();
const results = [];
const check = async (name, fn) => {
  const started = Date.now();
  try { const detail = await fn(); results.push({ name, ok: true, detail, seconds: (Date.now() - started) / 1000 }); console.log("PASS", name, JSON.stringify(detail)); }
  catch (error) { results.push({ name, ok: false, error: String(error).slice(0, 400) }); console.log("FAIL", name, String(error).slice(0, 400)); }
};
const walking = page => page.waitForSelector(".gully-controls", { timeout: 600000 });
const world = page => page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout: 900000 });
const pose = page => page.evaluate(() => window.__breezePerf.snapshot().pose);
async function open(options = { viewport: { width: 1280, height: 720 } }, path = "/runtime-preview/cypher?diagnostics&tier=balanced", setup) {
  const context = await browser.newContext(options), page = await context.newPage();
  await page.route("**/*.mp4", route => route.fulfill({ path: webm, contentType: "video/webm" }));
  if (setup) await setup(page);
  await page.goto(base + path, { waitUntil: "domcontentloaded" });
  return { context, page };
}

await check("a failed late chunk leaves the arrival half walkable", async () => {
  const { context, page } = await open(undefined, undefined, page => page.route("**/locked-rev15z-cypher-plaza/contact-frontage.*.glb", route => route.abort()));
  await walking(page);
  await page.waitForFunction(() => window.__breezePerf.snapshot().loads.chunks["cypher-plaza"]?.failed === true, null, { timeout: 600000 });
  const before = await pose(page);
  await page.mouse.click(640, 200);
  await page.keyboard.down("KeyW"); await page.waitForTimeout(4000); await page.keyboard.up("KeyW");
  const after = await pose(page), error = await page.locator(".native-loading").count();
  if (!(before.z - after.z > 0.5)) throw Error(`did not walk: ${before.z} -> ${after.z}`);
  if (error) throw Error("loading/error screen shown");
  await context.close();
  return { movedMetres: +(before.z - after.z).toFixed(2) };
});

await check("WebGL context loss and restore resumes walking", async () => {
  const { context, page } = await open();
  await walking(page);
  await page.evaluate(() => { const gl = document.querySelector("canvas").getContext("webgl2"); window.__lose = gl.getExtension("WEBGL_lose_context"); window.__lose.loseContext(); });
  await page.waitForTimeout(3000);
  await page.evaluate(() => window.__lose.restoreContext());
  await walking(page);
  const before = await pose(page);
  await page.mouse.click(640, 200);
  await page.keyboard.down("KeyW"); await page.waitForTimeout(4000); await page.keyboard.up("KeyW");
  const after = await pose(page);
  if (!(before.z - after.z > 0.5)) throw Error(`did not walk after restore: ${before.z} -> ${after.z}`);
  await context.close();
  return { movedMetres: +(before.z - after.z).toFixed(2) };
});

await check("touch movement pad walks on a phone viewport", async () => {
  const { context, page } = await open({ ...devices["Pixel 7"] });
  await walking(page);
  const before = await pose(page);
  const pad = page.locator('[data-move="forward"]');
  const box = await pad.boundingBox();
  const cdp = await context.newCDPSession(page);
  const point = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [point] });
  await page.waitForTimeout(4000);
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  const after = await pose(page);
  if (!(before.z - after.z > 0.3)) throw Error(`touch did not move: ${before.z} -> ${after.z}`);
  await context.close();
  return { movedMetres: +(before.z - after.z).toFixed(2), dpr: devices["Pixel 7"].deviceScaleFactor };
});

await check("screen loops the 720p film after streaming; Watch restarts the full film from 0", async () => {
  const { context, page } = await open(undefined, "/runtime-preview/cypher?start=aftermovie&diagnostics&tier=balanced", async page => {
    await page.addInitScript(() => {
      const create = document.createElement.bind(document); window.__videos = [];
      document.createElement = (tag, ...rest) => { const el = create(tag, ...rest); if (String(tag).toLowerCase() === "video") window.__videos.push(el); return el; };
    });
  });
  await walking(page);
  const early = await page.evaluate(() => window.__videos.filter(v => v.src).length);
  await world(page);
  await page.waitForFunction(() => window.__videos.some(v => v.src && !v.paused && v.currentTime > 1), null, { timeout: 600000 });
  const loop = await page.evaluate(() => { const v = window.__videos.find(v => v.src); return { src: v.src.split("/").pop(), loop: v.loop, t: v.currentTime }; });
  const pressed = await page.evaluate(() => {
    const v = window.__videos.find(v => v.src), before = v.currentTime;
    document.querySelector('.gully-controls button[aria-keyshortcuts="E"]').click();
    return { before, after: v.currentTime, src: v.src.split("/").pop() };
  });
  await context.close();
  if (early !== 0) throw Error("film started before the world streamed");
  if (loop.src !== "after-movie-720.mp4" || !loop.loop) throw Error("loop source " + JSON.stringify(loop));
  if (pressed.after > 0.5 || pressed.src !== "after-movie.mp4") throw Error("watch " + JSON.stringify(pressed));
  return { loop, pressed };
});

await browser.close();
console.log(JSON.stringify({ passed: results.filter(r => r.ok).length, failed: results.filter(r => !r.ok).length }));
process.writeSync?.(1, "");
import("node:fs").then(fs => fs.writeFileSync("perf-results/functional.json", JSON.stringify(results, null, 1)));
