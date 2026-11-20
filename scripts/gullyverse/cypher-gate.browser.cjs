const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN ?? "http://127.0.0.1:8898";
const output = process.argv[2];
const route = origin + "/runtime-preview/cypher";

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN,
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    desktop.on("pageerror", error => errors.push(String(error)));
    desktop.on("requestfailed", request => errors.push(request.failure()?.errorText + " " + request.url()));
    desktop.on("response", response => {
      if (response.status() >= 400 && /\/models\/gullyverse\//.test(response.url())) {
        errors.push(`${response.status()} ${response.url()}`);
      }
    });
    await desktop.bringToFront();
    assert.equal((await desktop.goto(route))?.status(), 200);
    const controls = desktop.getByRole("region", { name: "Walk through the cypher gate" });
    await controls.waitFor({ timeout: 90_000 });
    await desktop.evaluate(() => {
      window.firstGateCanvas = document.querySelector("canvas");
      window.dispatchEvent(new Event("focus"));
    });
    await desktop.screenshot({ path: path.join(output, "01-laptop-gate.png") });
    await desktop.keyboard.down("w");
    await desktop.getByText("Cypher forecourt", { exact: true }).waitFor({ timeout: 25_000 });
    await desktop.keyboard.up("w");
    await desktop.screenshot({ path: path.join(output, "02-laptop-forecourt.png") });
    await desktop.keyboard.down("s");
    await desktop.getByText("Cypher gate", { exact: true }).waitFor({ timeout: 25_000 });
    await desktop.keyboard.up("s");
    assert.ok(await desktop.evaluate(() => (
      document.querySelectorAll("canvas").length === 1 &&
      document.querySelector("canvas") === window.firstGateCanvas
    )));
    assert.deepEqual(errors, []);

    const mobile = await browser.newPage({ ...devices["iPhone 13"] });
    await mobile.bringToFront();
    assert.equal((await mobile.goto(route))?.status(), 200);
    const forward = mobile.getByRole("button", { name: "Walk forward" });
    await forward.waitFor({ timeout: 90_000 });
    await mobile.evaluate(() => window.dispatchEvent(new Event("focus")));
    await mobile.screenshot({ path: path.join(output, "03-phone-gate.png") });
    const rect = await forward.boundingBox();
    assert.ok(rect, "Phone forward control is visible");
    const session = await mobile.context().newCDPSession(mobile);
    try {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchStart", touchPoints: [{ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 }],
      });
      await mobile.getByText("Cypher forecourt", { exact: true }).waitFor({ timeout: 30_000 });
    } finally {
      await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    }
    assert.equal(await mobile.locator("canvas").count(), 1);

    const fallback = await browser.newPage();
    await fallback.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type, ...args) {
        return type === "webgl2" ? null : original.call(this, type, ...args);
      };
    });
    await fallback.goto(route);
    await fallback.getByRole("link", { name: "Browse events" }).waitFor();
    assert.equal(await fallback.locator("canvas").count(), 0);
    console.log(JSON.stringify({ desktopGateRoundTrip: true, sameCanvas: true, phoneTouchCrossing: true, noWebGLFallback: true, runtimeAssetErrors: errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
