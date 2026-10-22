import {mkdir, readFile, writeFile} from "node:fs/promises";
import {launch, context, ready, view, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";
const root = "reports/recovery-phase2-c8-material-2026-10-19", browser = await launch(), frames = [], errors = [];
const build = (await readFile(".next/BUILD_ID", "utf8")).trim();
let current;
try {
  await mkdir(root + "/screenshots/final-controls", {recursive: true});
  for (const mode of ["c51", "c8-3x"]) {
    current = await context(browser, {viewport: {width: 1366, height: 900}, deviceScaleFactor: 1});
    const page = await current.newPage();
    await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics" + (mode === "c51" ? "" : "&quarryReview=scanned-material-multi"));
    await page.waitForFunction(() => window.__gullyverse?.runtime); await page.evaluate(() => window.__gullyverse.runtime.setQuality(3)); await ready(page);
    await page.addStyleTag({content: "[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
    for (const scale of mode === "c51" ? [0] : [3, 1, 4, 3]) {
      if (scale) { await page.evaluate(scale => window.__wallPreview.setScannedMaterial(true, scale), scale); await ready(page); }
      await view(page, [-18, 1.72, -55], [-44, 8, -65], {fixed: true, quality: 0});
      const file = `screenshots/final-controls/${build}-${mode}-${scale}-${frames.length}.png`;
      await page.screenshot({path: root + "/" + file});
      frames.push({mode, scale, file, build, data: await details(page), material: await page.evaluate(() => window.__wallPreview.materialDiagnostics?.())});
    }
    await current.close(); current = null;
  }
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1; }
finally {
  await current?.close(); await browser.close();
  await writeFile(root + "/raw/final-visual-controls.json", JSON.stringify({status: errors.length ? "FAIL" : "PASS", build, frames, errors}, null, 2));
}
