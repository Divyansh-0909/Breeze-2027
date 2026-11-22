const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN;
const output = process.argv[2];
const preview = origin + "/runtime-preview/cypher?start=accommodation";
const visitName = "View accommodation";
const backName = "Back to walking";

async function ready(page) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await page.bringToFront();
  assert.equal((await page.goto(preview, { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".native-canvas canvas").waitFor({ timeout: 90_000 });
  await page.evaluate(() => {
    window.accommodationCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  await page.getByRole("button", { name: visitName }).waitFor({ timeout: 180_000 });
}

async function capture(page, file) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.screenshot({ path: path.join(output, file), timeout: 90_000 });
}

async function focusedWall(page) {
  const region = page.getByRole("region", { name: "Accommodation" });
  await region.waitFor({ timeout: 90_000 });
  assert.match(await region.ariaSnapshot(), /paragraph: Coming soon/);
  assert.equal(await page.getByRole("heading", { name: "Accommodation" }).count(), 0);
  await page.waitForFunction(name => document.activeElement?.textContent === name, backName);
}

async function restored(page) {
  await page.getByRole("button", { name: visitName }).waitFor({ timeout: 90_000 });
  await page.waitForFunction(name => document.activeElement?.textContent === name, visitName);
  assert.equal(await page.getByRole("region", { name: "Accommodation" }).count(), 0);
  assert.ok(await page.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
    document.querySelector("canvas") === window.accommodationCanvas));
}

async function main() {
  assert.equal(new URL(origin).hostname, "127.0.0.1");
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN ?? "/usr/bin/chromium",
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  const errors = [];
  const watch = page => {
    page.on("pageerror", error => errors.push(String(error)));
    page.on("response", response => {
      if (response.status() >= 400 && response.url().includes("/models/gullyverse/")) errors.push(response.url());
    });
    page.on("console", message => {
      if (message.type() === "error" && /WebGLProgram|Shader Error/.test(message.text())) errors.push(message.text());
    });
  };
  try {
    const desktop = await browser.newPage({ viewport: { width: 720, height: 540 }, reducedMotion: "reduce" });
    watch(desktop);
    await ready(desktop);
    await desktop.setViewportSize({ width: 1120, height: 700 });
    await capture(desktop, "01-laptop-approach.png");
    const visit = desktop.getByRole("button", { name: visitName });
    await visit.focus();
    await desktop.keyboard.press("Enter");
    await focusedWall(desktop);
    await capture(desktop, "02-laptop-wall.png");
    await desktop.keyboard.press("Escape");
    await restored(desktop);
    await desktop.mouse.click(560, 350);
    await focusedWall(desktop);
    await desktop.getByRole("button", { name: backName }).click();
    await restored(desktop);
    await desktop.close();
    console.log("Keyboard and graffiti click opened the wall. Escape and Back restored focus on the original canvas.");

    const phone = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    watch(phone);
    await ready(phone);
    await phone.getByRole("button", { name: visitName }).tap();
    await focusedWall(phone);
    await capture(phone, "03-phone-portrait.png");
    await phone.setViewportSize({ width: 844, height: 390 });
    await capture(phone, "04-phone-landscape.png");
    await phone.getByRole("button", { name: backName }).tap();
    await restored(phone);
    await phone.close();

    const fallback = await browser.newPage({ viewport: { width: 390, height: 664 } });
    watch(fallback);
    await fallback.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
        return kind === "webgl2" ? null : original.call(this, kind, ...args);
      };
    });
    assert.equal((await fallback.goto(preview, { timeout: 90_000 }))?.status(), 200);
    const status = fallback.getByRole("region", { name: "Accommodation" });
    await status.getByRole("heading", { name: "Accommodation" }).waitFor();
    assert.equal(await status.getByText("Coming soon", { exact: true }).isVisible(), true);
    assert.equal(await fallback.locator("canvas").count(), 0);
    await fallback.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
    await capture(fallback, "05-text-fallback.png");
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ status: "PASS", keyboard: true, graffitiClick: true, landscape: true,
      portrait: true, sameCanvas: true, restoredFocus: true, noWebGLFallback: true, errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
