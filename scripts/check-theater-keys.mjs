/**
 * Checks Aftermovie theater mode (open with E, close with Escape and with a backdrop click) and the V / H / M HUD
 * keys, and fails on any console error. Drafted by Antigravity (Gemini 4 Hydrogen), reviewed before use.
 *   BREEZE_BASE_URL=http://127.0.0.1:3001 node -r ./perf/results-2026-11-26-gtx1650/gpu-flag.cjs scripts/check-theater-keys.mjs [folder]
 */
import { mkdir } from "node:fs/promises";
import { chromium } from "playwright";

const base = (process.env.BREEZE_BASE_URL || "http://127.0.0.1:3001").replace(/\/+$/, "");
const folder = `screenshots/${process.argv[2] ?? "phase2-r1"}`;

function pass(label, detail = "") { console.log(`PASS: ${label}${detail ? ` (${detail})` : ""}`); }
function fail(label, detail = "") { console.error(`FAIL: ${label}${detail ? ` (${detail})` : ""}`); process.exitCode = 1; }

async function run() {
  await mkdir(folder, { recursive: true });
  const errors = [];
  let browser;
  try {
    browser = await chromium.launch({ args: ["--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"] });
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    page.on("console", msg => { if (msg.type() === "error") errors.push(`console.error: ${msg.text()}`); });
    page.on("pageerror", err => errors.push(`pageerror: ${err?.stack || err?.message || String(err)}`));

    const url = `${base}/runtime-preview/cypher?start=aftermovie&diagnostics`;
    await page.goto(url);
    await page.locator(".gully-controls").waitFor({ state: "visible", timeout: 600000 });
    await page.waitForTimeout(4000);
    pass("Preview ready", url);

    // 1. Open theater with E.
    try {
      await page.locator('.hud-prompt[aria-label="Watch Aftermovie"]').waitFor({ state: "visible", timeout: 5000 });
      await page.keyboard.press("e");
      await page.locator(".cypher-theater").waitFor({ state: "visible", timeout: 10000 });
      if (!(await page.$(".cypher-theater-frame video"))) fail("Open theater (e)", "missing .cypher-theater-frame video");
      else {
        await page.waitForTimeout(1500);
        await page.screenshot({ path: `${folder}/theater-open.png` });
        pass("Open theater (e)", "theater visible with <video>");
      }
    } catch (err) { fail("Open theater (e)", err?.message || String(err)); }

    // 2. Close with Escape.
    try {
      await page.keyboard.press("Escape");
      await page.locator(".cypher-theater").waitFor({ state: "hidden", timeout: 5000 });
      await page.locator(".gully-controls").waitFor({ state: "visible", timeout: 5000 });
      await page.screenshot({ path: `${folder}/theater-closed.png` });
      pass("Close theater (Escape)", "theater hidden, walking HUD back");
    } catch (err) { fail("Close theater (Escape)", err?.message || String(err)); }

    // 3. Re-open with E, close with a backdrop click.
    try {
      await page.locator('.hud-prompt[aria-label="Watch Aftermovie"]').waitFor({ state: "visible", timeout: 8000 });
      await page.keyboard.press("e");
      await page.locator(".cypher-theater").waitFor({ state: "visible", timeout: 10000 });
      await page.mouse.click(20, 450);
      await page.locator(".cypher-theater").waitFor({ state: "hidden", timeout: 5000 });
      pass("Close theater (backdrop click)");
    } catch (err) { fail("Close theater (backdrop click)", err?.message || String(err)); }

    // 4. V toggles sound.
    try {
      const before = await page.locator('button[aria-label="Sound"]').getAttribute("aria-pressed");
      const expected = before === "true" ? "false" : "true";
      await page.keyboard.press("v");
      await page.waitForFunction(exp => document.querySelector('button[aria-label="Sound"]')?.getAttribute("aria-pressed") === exp, expected, { timeout: 3000 });
      pass("Key v (Sound)", `aria-pressed ${before} -> ${expected}`);
    } catch (err) { fail("Key v (Sound)", err?.message || String(err)); }

    // 5. H folds / unfolds the controls legend.
    try {
      const legend = await page.evaluate(() => Boolean(document.querySelector(".hud-legend")));
      await page.keyboard.press("h");
      await page.waitForFunction(was => Boolean(document.querySelector(".hud-legend")) !== was, legend, { timeout: 3000 });
      pass("Key h (legend)", legend ? "folded" : "unfolded");
    } catch (err) { fail("Key h (legend)", err?.message || String(err)); }

    // 6. M opens and closes the map.
    try {
      await page.locator('button[aria-label="Map"]').waitFor({ state: "attached", timeout: 5000 });
      await page.keyboard.press("m");
      await page.locator('button[aria-label="Close map"]').waitFor({ state: "attached", timeout: 5000 });
      await page.keyboard.press("m");
      await page.locator('button[aria-label="Map"]').waitFor({ state: "attached", timeout: 8000 });
      pass("Key m (Map)", "Map -> Close map -> Map");
    } catch (err) { fail("Key m (Map)", err?.message || String(err)); }

    if (errors.length === 0) pass("Console and page errors", "0 errors");
    else { fail("Console and page errors", `${errors.length} error(s)`); errors.forEach(e => console.error(`  - ${e.slice(0, 400)}`)); }
  } catch (err) {
    fail("Fatal script error", err?.stack || err?.message || String(err));
  } finally {
    await browser?.close();
  }
}
await run();
