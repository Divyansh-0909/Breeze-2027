import {mkdir, readFile, writeFile} from "node:fs/promises";
import {launch, context} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";
const root = "reports/recovery-quarry-fidelity-2026-10-19", browser = await launch(), runs = [];
const build = (await readFile(".next/BUILD_ID", "utf8")).trim();
await mkdir(root + "/raw", {recursive: true});
try {
  for (const [mode, quality] of [["c51", null], ["c8", null], ["recovered", null], ["corrected", null], ["corrected", 3]]) {
    const c = await context(browser, {deviceScaleFactor: 0.25});
    await c.addInitScript(() => {
      let diagnostic;
      Object.defineProperty(window, "__gullyverse", {configurable: true, get: () => diagnostic,
        set: value => { diagnostic = value; window.__lastStageDiagnostic = value; }});
    });
    const page = await c.newPage(), errors = []; page.on("pageerror", error => errors.push(error.message));
    const started = Date.now();
    await page.goto("http://127.0.0.1:3000/aftermovie?diagnostics" + (mode === "c8" ? "&quarryReview=scanned-material-multi" : mode === "recovered" ? "&quarryReview=scanned-composition" : mode === "corrected" ? "&quarryReview=geology-fidelity" : ""));
    if (quality !== null) {
      await page.waitForFunction(() => window.__gullyverse?.runtime);
      await page.evaluate(quality => window.__gullyverse.runtime.setQuality(quality), quality);
    }
    await page.waitForFunction(() => {
      const d = window.__gullyverse || window.__lastStageDiagnostic, s = d?.runtime.getSnapshot();
      return s?.phase === "error" || s?.phase === "local" && window.__wallPreview && !window.__wallPreview.state.busy;
    }, null, {timeout: 100000}).catch(error => errors.push(String(error)));
    const data = await page.evaluate(() => {
      const d = window.__gullyverse || window.__lastStageDiagnostic;
      return {state: d?.runtime.getSnapshot(), preparations: d?.preparations,
        phases: d?.phases, stats: d?.stats, frames: d?.timeline?.slice(-30),
        material: window.__wallPreview?.materialDiagnostics?.(), wallTrace: window.__wallPreview?.trace,
        nativeFallback: !document.querySelector("canvas") && !!document.querySelector("video")};
    });
    const boot=data.phases?.find(x=>x.phase==="boot"), local=data.phases?.find(x=>x.phase==="local"); const preparationWallMs=boot&&local?local.at-boot.at:null; runs.push({mode, initialQualityOverride: quality, milliseconds: Date.now() - started, preparationWallMs, conservativeDeadlineMarginMs:preparationWallMs===null?null:45000-preparationWallMs, marginNote:"Observed boot-to-local wall time; deadline excludes suspended/hidden time. Fresh isolated context, no application timeout change.", data, errors});
    await writeFile(root + "/raw/cold-stage-diagnostic.json", JSON.stringify({build, runs, physicalHardware: false}, null, 2));
    console.log(mode, quality, data.state?.phase, data.state?.error, Date.now() - started);
    await c.close();
  }
} finally { await browser.close(); }
