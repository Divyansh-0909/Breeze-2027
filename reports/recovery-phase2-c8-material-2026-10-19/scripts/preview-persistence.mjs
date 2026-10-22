import assert from "node:assert/strict";
import {mkdir, writeFile} from "node:fs/promises";
import {launch, context, ready, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const root = "reports/recovery-phase2-c8-material-2026-10-19", browser = await launch();
await mkdir(root + "/raw", {recursive: true});
let current, page;
const states = [], errors = [];
async function record(label) {
  await ready(page);
  const data = await page.evaluate(() => ({material: window.__wallPreview.materialDiagnostics(),
    state: window.__gullyverse.runtime.getSnapshot(), url: location.href}));
  assert.equal(data.material.enabled, true); assert.equal(data.material.scale, 3);
  assert.equal(new URL(data.url).searchParams.get("quarryReview"), "scanned-material-multi");
  states.push({label, ...data}); console.log(label, "PASS");
}
async function go(id) {
  await page.getByRole("button", {name: /^Map/}).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().mapStage === "open");
  await page.getByRole("button", {name: id === "hub" ? "Gullyverse hub" : "Aftermovie", exact: true}).click();
  await page.waitForFunction(id => window.__gullyverse?.runtime?.getSnapshot().phase === "local" && window.__gullyverse.runtime.getSnapshot().scene === id, id, {timeout: 90000});
}
try {
  current = await context(browser, {deviceScaleFactor: 0.25}); page = await current.newPage();
  await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=scanned-material-multi");
  await record("default 3x hub"); const canvas = await page.evaluateHandle(() => document.querySelector("canvas"));
  const initialImages = states[0].material.textures.map(texture => texture.source);
  await page.getByRole("button", {name: /^Map/}).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().mapStage === "open");
  await record("map open");
  await page.getByRole("button", {name: "Close map", exact: true}).click();
  await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().map); await record("map closed");
  await go("aftermovie"); await record("stage arrival");
  await page.getByRole("button", {name: "Play Aftermovie", exact: true}).click();
  await page.waitForFunction(() => window.__gullyverse.runtime.movieActions.status().currentTime > 0.2, null, {timeout: 30000});
  await record("Aftermovie playing");
  await page.screenshot({path: root + "/screenshots/c8-stage-playing.png"});
  await page.getByRole("button", {name: "Exit Aftermovie", exact: true}).click();
  await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().movie); await record("playback stopped");
  await go("hub"); await record("returned hub");
  assert.equal(await canvas.evaluate(canvas => canvas === document.querySelector("canvas")), true);
  for (const state of states) assert.deepEqual(state.material.textures.map(texture => texture.source), initialImages);
  await page.goBack(); await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().scene === "aftermovie"); await record("history back");
  await page.goForward(); await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().scene === "hub"); await record("history forward");
  await page.reload(); await record("hard reload preserves private selector");
  await page.goto("http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=scanned-material-multi"); await record("direct stage URL");
  await current.close();
  current = await context(browser, {deviceScaleFactor: 0.25}); page = await current.newPage();
  await page.route("**/aftermovie-stage.glb", route => route.abort());
  await page.goto("http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=scanned-material-multi");
  await page.waitForFunction(() => !document.querySelector("canvas") && document.querySelector("video"), null, {timeout: 90000});
  states.push({label: "critical original stage failure retains native video fallback", videos: await page.locator("video").count()});
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1; }
finally {
  await current?.close(); await browser.close();
  await writeFile(root + "/raw/preview-persistence.json", JSON.stringify({status: errors.length ? "FAIL" : "PASS", states, errors, physicalHardware: false}, null, 2));
}
