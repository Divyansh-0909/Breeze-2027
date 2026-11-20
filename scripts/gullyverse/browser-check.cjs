/** Real private GLB import/lifecycle checks; uses software WebGL, never live messages. */
const { chromium } = require("playwright");
const fs = require("node:fs/promises");
const path = require("node:path");
const assert = require("node:assert/strict");
const report =
  process.env.GULLYVERSE_REPORT ??
  "/dev/shm/art-lock-implementation-2026-11-14";
const url = process.env.GULLYVERSE_PILOT_URL ?? "http://127.0.0.1:8893/";
const result = {
  environment:
    "Chromium SwiftShader software WebGL; mobile viewport emulation, not physical hardware",
  errors: [],
  networkFailures: [],
  checks: {},
  measurements: {},
};
(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM ?? "/usr/bin/chromium",
    headless: true,
    args: [
      "--no-sandbox",
      "--enable-unsafe-swiftshader",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--disable-crash-reporter",
      "--disable-breakpad",
    ],
  });
  async function page(viewport) {
    const p = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    p.on("pageerror", (e) => result.errors.push(String(e)));
    p.on("console", (m) => {
      if (m.type() === "error") result.errors.push(m.text());
    });
    p.on("requestfailed", (r) => result.networkFailures.push(r.url()));
    return p;
  }
  async function ready(p, mode) {
    await p.waitForFunction(
      (m) =>
        window.__lockedPilot?.ready() &&
        (!m || window.__lockedPilot.stats().mode === m),
      mode,
      { timeout: 120000 },
    );
    await p.waitForTimeout(200);
  }
  async function sample(p, key) {
    await p.waitForFunction(
      () => window.__lockedPilot.stats().frameSamples >= 80,
      null,
      { timeout: 120000 },
    );
    result.measurements[key] = await p.evaluate(() =>
      window.__lockedPilot.stats(),
    );
    assert.equal(result.measurements[key].glError, 0);
    assert.equal(result.measurements[key].canvasCount, 1);
    assert.equal(result.measurements[key].triangles, 5745);
  }
  async function shot(p, key) {
    await p.screenshot({ path: path.join(report, "renders", key + ".png") });
  }
  try {
    const p = await page({ width: 1440, height: 900 });
    await p.goto(url, { waitUntil: "networkidle" });
    await ready(p, "png");
    await p.evaluate(
      () => (window.__initialCanvas = document.querySelector("canvas")),
    );
    await sample(p, "desktopBaseline");
    await shot(p, "m1-baseline-laptop");
    await p
      .getByRole("button", { name: "KTX2 + Meshopt", exact: true })
      .click();
    await ready(p, "compressed");
    await sample(p, "desktopCompressed");
    await shot(p, "m1-compressed-laptop");
    assert.equal(
      await p.evaluate(
        () => window.__initialCanvas === document.querySelector("canvas"),
      ),
      true,
    );
    result.checks.singleCanvasIdentityAcrossAssetSwap = true;
    result.measurements.compressedInitialCache = await p.evaluate(() =>
      window.__lockedPilot.cache(),
    );
    await p.getByRole("button", { name: "Change view", exact: true }).click();
    await p.waitForTimeout(500);
    await shot(p, "m1-context-laptop");
    await p.getByRole("button", { name: "Change view", exact: true }).click();
    for (let i = 0; i < 2; i++) {
      await p
        .getByRole("button", { name: "PNG baseline", exact: true })
        .click();
      await ready(p, "png");
      await p
        .getByRole("button", { name: "KTX2 + Meshopt", exact: true })
        .click();
      await ready(p, "compressed");
    }
    await p.waitForTimeout(500);
    const cache = await p.evaluate(() => window.__lockedPilot.cache());
    assert.equal(cache.entries, 1);
    assert.equal(cache.users, 1);
    assert.equal(
      cache.gpu.textures,
      result.measurements.compressedInitialCache.gpu.textures,
    );
    result.measurements.compressedAfterCyclesCache = cache;
    result.checks.noTextureCountGrowthAfterTwoCycles = true;
    for (const [name, value] of Object.entries({
      name: "Private Test",
      email: "private@example.test",
      phone: "9999999999",
      message: "Local preview validation only.",
    }))
      await p.locator(`[name=${name}]`).fill(value);
    let requests = 0;
    p.on("request", (r) => {
      if (r.url().includes("/api/contact")) requests++;
    });
    await p.getByRole("button", { name: "Send message", exact: true }).click();
    await p.locator(".form-status[data-state=error]").waitFor();
    assert.equal(
      await p.locator("[name=message]").inputValue(),
      "Local preview validation only.",
    );
    assert.equal(requests, 0);
    result.checks.privateFormRetainsFailedMessageWithoutSending = true;
    await p.reload({ waitUntil: "networkidle" });
    await ready(p, "png");
    assert.equal(await p.locator("canvas").count(), 1);
    result.checks.reload = true;
    await p.close();
    const phone = await page({ width: 390, height: 844 });
    await phone.goto(url, { waitUntil: "networkidle" });
    await ready(phone, "png");
    await phone
      .getByRole("button", { name: "KTX2 + Meshopt", exact: true })
      .click();
    await ready(phone, "mobile");
    await sample(phone, "phoneCompressed");
    await shot(phone, "m1-compressed-phone");
    assert.equal(
      await phone.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    await phone
      .getByRole("button", { name: "Close contact form", exact: true })
      .click();
    assert.equal(await phone.locator("#form-host").isVisible(), false);
    await phone.getByRole("button", { name: "Show form", exact: true }).click();
    assert.equal(await phone.locator("#form-host").isVisible(), true);
    result.checks.phoneFitAndCloseReopen = true;
    await phone.close();
    // Fail the compressed model once; exercise an explicit baseline recovery path.
    const failed = await browser.newPage({
      viewport: { width: 1024, height: 768 },
    });
    let expectedFailure = false;
    await failed.route("**/contact-frontage.optimized.glb", (route) => {
      expectedFailure = true;
      return route.abort("failed");
    });
    await failed.goto(url, { waitUntil: "networkidle" });
    await ready(failed, "png");
    await failed
      .getByRole("button", { name: "KTX2 + Meshopt", exact: true })
      .click();
    await failed
      .getByRole("button", { name: "Retry PNG fallback", exact: true })
      .waitFor({ timeout: 120000 });
    await failed
      .getByRole("button", { name: "Retry PNG fallback", exact: true })
      .click();
    await ready(failed, "png");
    assert.equal(expectedFailure, true);
    result.checks.assetFailureBaselineRecovery = true;
    await failed.close();
    assert.deepEqual(result.errors, []);
    assert.deepEqual(result.networkFailures, []);
    result.status = "PASS";
  } catch (e) {
    result.status = "FAIL";
    result.failure = String(e);
    process.exitCode = 1;
  } finally {
    await browser.close();
    await fs.writeFile(
      path.join(report, "evidence/browser-check.json"),
      JSON.stringify(result, null, 2) + "\n",
    );
    console.log(
      JSON.stringify({
        status: result.status,
        checks: result.checks,
        failure: result.failure,
        measurements: Object.fromEntries(
          Object.entries(result.measurements).map(([k, v]) => [
            k,
            {
              triangles: v.triangles,
              drawCalls: v.drawCalls,
              frameMs: v.frameMs,
              frameSamples: v.frameSamples,
              gpuTextureBytesProxy: v.gpuTextureBytesProxy,
            },
          ]),
        ),
      }),
    );
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
