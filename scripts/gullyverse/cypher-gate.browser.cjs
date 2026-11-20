const assert = require("node:assert/strict");
const path = require("node:path");
const sharp = require("sharp");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN ?? "http://127.0.0.1:8898";
const output = process.argv[2];
const route = origin + "/runtime-preview/cypher?start=approach";
const approach = "Navigation approach";
const gate = "Cypher gate";
const forecourt = "Cypher forecourt";

async function sponsorPixels(page) {
  const screen = await page.screenshot({ clip: { x: 460, y: 565, width: 520, height: 130 } });
  return sharp(screen).removeAlpha().raw().toBuffer();
}

function changedRedPixels(before, after) {
  let changed = 0;
  for (let i = 0; i < before.length; i += 3) {
    const red = Math.max(before[i], after[i]);
    const green = Math.max(before[i + 1], after[i + 1]);
    if (red > 90 && red > 1.5 * green && Math.abs(before[i] - after[i]) > 18) changed++;
  }
  return changed;
}

async function waitForReveal(page) {
  await page.waitForFunction(() => {
    const curtain = document.querySelector(".native-curtain");
    return curtain && Number(getComputedStyle(curtain).opacity) < 0.02;
  }, null, { timeout: 40_000 });
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN,
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    desktop.on("pageerror", error => errors.push(String(error)));
    desktop.on("console", message => {
      if (message.type() === "error" && /WebGLProgram|Shader Error/.test(message.text())) {
        errors.push(message.text());
      }
    });
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
    await controls.getByText(approach, { exact: true }).waitFor();
    await desktop.evaluate(() => {
      window.firstGateCanvas = document.querySelector("canvas");
      window.dispatchEvent(new Event("focus"));
    });
    await waitForReveal(desktop);
    await desktop.screenshot({ path: path.join(output, "01-laptop-approach.png") });
    const firstDisplay = await sponsorPixels(desktop);
    await desktop.waitForTimeout(900);
    const movedDisplay = await sponsorPixels(desktop);
    const scrollingPixels = changedRedPixels(firstDisplay, movedDisplay);
    assert.ok(scrollingPixels > 20, `Visible red LED pixels should move (${scrollingPixels})`);
    await desktop.emulateMedia({ reducedMotion: "reduce" });
    await desktop.waitForTimeout(250);
    const restingDisplay = await sponsorPixels(desktop);
    await desktop.waitForTimeout(600);
    assert.equal(changedRedPixels(restingDisplay, await sponsorPixels(desktop)), 0);
    await desktop.emulateMedia({ reducedMotion: "no-preference" });
    console.log("Sponsor display and reduced motion verified.");

    // Keep the software-rendered locomotion check small. The approach still
    // above uses the full laptop viewport.
    await desktop.setViewportSize({ width: 960, height: 600 });
    await desktop.keyboard.down("w");
    await controls.getByText(gate, { exact: true }).waitFor({ timeout: 75_000 });
    await desktop.keyboard.up("w");
    await desktop.mouse.move(420, 280);
    await desktop.mouse.down();
    await desktop.mouse.move(420, 370, { steps: 3 });
    await desktop.mouse.up();
    await desktop.screenshot({ path: path.join(output, "02-laptop-gate.png") });
    await desktop.keyboard.down("w");
    await controls.getByText(forecourt, { exact: true }).waitFor({ timeout: 40_000 });
    await desktop.keyboard.up("w");
    await desktop.screenshot({ path: path.join(output, "03-laptop-forecourt.png") });
    await desktop.keyboard.down("s");
    await controls.getByText(approach, { exact: true }).waitFor({ timeout: 50_000 });
    await desktop.keyboard.up("s");
    assert.ok(await desktop.evaluate(() => (
      document.querySelectorAll("canvas").length === 1 &&
      document.querySelector("canvas") === window.firstGateCanvas
    )));
    assert.deepEqual(errors, []);
    console.log("Laptop round trip verified on the same canvas.");
    await desktop.close();

    const mobile = await browser.newPage({ ...devices["iPhone 13"] });
    await mobile.bringToFront();
    assert.equal((await mobile.goto(route))?.status(), 200);
    const forward = mobile.getByRole("button", { name: "Walk forward" });
    await forward.waitFor({ timeout: 90_000 });
    await mobile.evaluate(() => window.dispatchEvent(new Event("focus")));
    await waitForReveal(mobile);
    await mobile.screenshot({ path: path.join(output, "04-phone-approach.png") });
    const rect = await forward.boundingBox();
    assert.ok(rect, "Phone forward control is visible");
    const session = await mobile.context().newCDPSession(mobile);
    try {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchStart", touchPoints: [{ x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 }],
      });
      await mobile.getByText(forecourt, { exact: true }).waitFor({ timeout: 90_000 });
    } finally {
      await session.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    }
    assert.equal(await mobile.locator("canvas").count(), 1);
    await mobile.close();

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
    console.log(JSON.stringify({
      desktopApproachGateRoundTrip: true, sameCanvas: true, phoneTouchCrossing: true,
      sponsorDisplayChangedRedPixels: scrollingPixels, reducedMotionPausedSponsorDisplay: true,
      noWebGLFallback: true, runtimeAssetErrors: errors,
    }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
