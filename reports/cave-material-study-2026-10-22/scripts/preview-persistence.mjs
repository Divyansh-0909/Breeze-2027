import assert from "node:assert/strict";
import {mkdir, writeFile} from "node:fs/promises";
import {launch, context, ready, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const root = "reports/cave-material-study-2026-10-22", browser = await launch();
await mkdir(root + "/raw", {recursive: true});
let current, page;
const states = [], errors = [];
async function record(label) {
  await page.waitForFunction(() => window.__gullyverse?.runtime);
  await page.evaluate(() => { window.__lastPersistenceDiagnostic = window.__gullyverse; window.__lastPersistenceOwner = window.__wallPreview; });
  await page.waitForFunction(() => { const r = window.__gullyverse || window.__lastPersistenceDiagnostic, s = r?.runtime.getSnapshot(); return s?.phase === "error" || s?.phase === "local" && !window.__wallPreview?.state.busy; }, null, {timeout:90000});
  assert.notEqual(await page.evaluate(() => window.__lastPersistenceDiagnostic.runtime.getSnapshot().phase), "error");
  await ready(page);
  const data = await page.evaluate(() => ({material: window.__wallPreview.materialDiagnostics(),
    composition: window.__wallPreview.compositionDiagnostics(), cave: window.__wallPreview.entranceDiagnostics(), state: window.__gullyverse.runtime.getSnapshot(), url: location.href}));
  assert.equal(data.composition.enabled, true); assert.equal(data.composition.ready, true); assert.equal(data.material.enabled, true); assert.equal(data.material.scale, 3);
  assert.equal(new URL(data.url).searchParams.get("quarryReview"), "geology-fidelity");
  assert.ok(data.cave.ready || (data.state.scene==="aftermovie"&&!data.state.map&&data.cave.visibilityLoading.deferredWhileOffscreen));assert.equal(new URL(data.url).searchParams.get("entranceReview"),"material-study");
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
  await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=rock_01");
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
  await page.screenshot({path: root + "/screenshots/c9-stage-playing.png"});
  await page.getByRole("button", {name: "Exit Aftermovie", exact: true}).click();
  await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().movie); await record("playback stopped");
  await go("hub"); await record("returned hub");
  assert.equal(await canvas.evaluate(canvas => canvas === document.querySelector("canvas")), true);
  for (const state of states) assert.deepEqual(state.material.textures.map(texture => texture.source), initialImages);
  await page.goBack(); await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().scene === "aftermovie"); await record("history back");
  await page.goForward(); await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().scene === "hub"); await record("history forward");
  await page.reload(); await record("hard reload preserves private selector");
  await page.goto("http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=rock_01"); await record("direct stage URL");
  for (let cycle = 0; cycle < 3; cycle++) {
    await go("aftermovie"); await record("repeat stage arrival " + cycle);
    await page.getByRole("button", {name:"Play Aftermovie", exact:true}).click();
    await page.waitForFunction(() => window.__gullyverse.runtime.movieActions.status().currentTime > .2, null, {timeout:30000});
    await record("repeat playback " + cycle);
    await page.getByRole("button", {name:"Exit Aftermovie", exact:true}).click();
    await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().movie);
    await go("hub"); await record("repeat hub return " + cycle);
  }
  await current.close();
  current = await context(browser, {deviceScaleFactor: 0.25}); page = await current.newPage();
  await page.route("**/aftermovie-stage.glb", route => route.abort());
  await page.goto("http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=rock_01");
  await page.waitForFunction(() => !document.querySelector("canvas") && document.querySelector("video"), null, {timeout: 90000});
  states.push({label: "critical original stage failure retains native video fallback", videos: await page.locator("video").count()});
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1;
  const failure = await page?.evaluate(() => { const d=window.__gullyverse||window.__lastPersistenceDiagnostic,o=window.__wallPreview||window.__lastPersistenceOwner; return {state:d?.runtime.getSnapshot(),preparations:d?.preparations,phases:d?.phases,frames:d?.timeline?.slice(-40),wall:o?.state,trace:o?.trace,nativeFallback:!document.querySelector("canvas")&&!!document.querySelector("video")}; }).catch(() => null);
  await writeFile(root+"/raw/preview-persistence-failure-diagnostic.json",JSON.stringify(failure,null,2));
}
finally {
  await current?.close(); await browser.close();
  await writeFile(root + "/raw/preview-persistence.json", JSON.stringify({status: errors.length ? "FAIL" : "PASS", states, errors, physicalHardware: false}, null, 2));
}
