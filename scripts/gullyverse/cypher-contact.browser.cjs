const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN;
const output = process.argv[2];
const route = start => `${origin}/runtime-preview/cypher?start=${start}`;
const endpoint = `${origin}/api/preview-contact`;
const openName = "Leave a message";
const regionName = "Walk through the cypher gate";
const fixture = name => ({
  name, email: "preview@example.invalid", phone: "9999999999",
  message: "This is a disposable cypher integration test.",
});

async function ready(page, start) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await page.bringToFront();
  assert.equal((await page.goto(route(start), { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.getByRole("region", { name: regionName }).waitFor({ timeout: 180_000 });
  await page.evaluate(() => {
    window.contactCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  await page.waitForFunction(() => Number(getComputedStyle(document.querySelector(".native-curtain")).opacity) < 0.02,
    null, { timeout: 120_000, polling: 100 });
}

async function fill(dialog, name) {
  const data = fixture(name);
  for (const label of ["Name", "Email", "Phone", "Message"]) {
    await dialog.getByRole("textbox", { name: label, exact: true }).fill(data[label.toLowerCase()]);
  }
}

async function sameCanvas(page) {
  assert.ok(await page.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
    document.querySelector("canvas") === window.contactCanvas));
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
      if (response.status() >= 400 && /\/models\/gullyverse\//.test(response.url())) errors.push(response.url());
    });
  };
  try {
    const desktop = await browser.newPage({ viewport: { width: 720, height: 360 }, reducedMotion: "reduce" });
    watch(desktop);
    const invalid = await desktop.request.post(endpoint, { data: { ...fixture("A"), email: "invalid" } });
    assert.equal(invalid.status(), 400);
    await ready(desktop, "plaza");
    console.log("Desktop plaza ready.");
    const enter = desktop.getByRole("button", { name: openName, exact: true });
    assert.equal(await enter.count(), 0);
    await desktop.keyboard.down("d");
    try {
      await enter.waitFor({ timeout: 180_000 });
    } finally {
      await desktop.keyboard.up("d");
    }
    await desktop.setViewportSize({ width: 1120, height: 700 });
    await enter.click();
    const dialog = desktop.getByRole("dialog", { name: "Contact enquiry" });
    await dialog.waitFor({ timeout: 120_000 });
    assert.equal(await dialog.getAttribute("data-flat"), "false");
    const rect = await dialog.boundingBox();
    assert.ok(rect && rect.width > 850 && rect.height > 180 && rect.x > 30);
    await desktop.screenshot({ path: path.join(output, "01-contact-laptop.png"), timeout: 120_000 });
    assert.equal(await desktop.evaluate(() => document.activeElement?.getAttribute("name")), "name");
    await fill(dialog, "Cypher Desktop Fixture");
    await dialog.getByRole("button", { name: "Send message" }).click();
    await dialog.getByText("Message received. We’ll get back to you.").waitFor({ timeout: 75_000 });
    console.log("Window projection and desktop submission verified.");

    await desktop.route("**/api/preview-contact", request => request.fulfill({
      status: 503, contentType: "application/json", body: JSON.stringify({ success: false }),
    }));
    await fill(dialog, "Draft after failed send");
    await dialog.getByRole("button", { name: "Send message" }).click();
    await dialog.getByText("Your draft is still here.", { exact: false }).waitFor({ timeout: 75_000 });
    assert.equal(await dialog.getByRole("textbox", { name: "Name", exact: true }).inputValue(), "Draft after failed send");
    await dialog.getByRole("button", { name: "Close contact form" }).focus();
    await desktop.keyboard.press("Shift+Tab");
    assert.equal(await desktop.evaluate(() => document.activeElement?.textContent), "Send message");
    await desktop.keyboard.press("Tab");
    assert.equal(await desktop.evaluate(() => document.activeElement?.getAttribute("aria-label")), "Close contact form");
    await dialog.getByRole("textbox", { name: "Name", exact: true }).focus();
    await desktop.keyboard.press("Escape");
    await dialog.waitFor({ state: "hidden", timeout: 75_000 });
    await enter.waitFor({ timeout: 120_000 });
    await desktop.waitForFunction(() => document.activeElement?.textContent === "Leave a message");
    await sameCanvas(desktop);
    await enter.click();
    await dialog.waitFor({ timeout: 75_000 });
    assert.equal(await dialog.getByRole("textbox", { name: "Name", exact: true }).inputValue(), "Draft after failed send");
    await desktop.close();
    console.log("Draft retention, keyboard dismissal and canvas identity verified.");

    const mobile = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    watch(mobile);
    await ready(mobile, "contact");
    await mobile.getByRole("button", { name: openName }).tap();
    const sheet = mobile.getByRole("dialog", { name: "Contact enquiry" });
    await sheet.waitFor({ timeout: 120_000 });
    assert.equal(await sheet.getAttribute("data-flat"), "true");
    assert.ok(await sheet.evaluate(element => element.clientWidth <= innerWidth && element.scrollWidth <= element.clientWidth));
    await mobile.screenshot({ path: path.join(output, "02-contact-phone.png"), timeout: 120_000 });
    await fill(sheet, "Cypher Phone Fixture");
    await sheet.getByRole("button", { name: "Send message" }).tap();
    await sheet.getByText("Message received. We’ll get back to you.").waitFor({ timeout: 75_000 });
    await sheet.getByRole("button", { name: "Close contact form" }).tap();
    await sheet.waitFor({ state: "hidden", timeout: 75_000 });
    await sameCanvas(mobile);
    await mobile.close();

    const fallback = await browser.newPage();
    await fallback.addInitScript(() => {
      const getContext = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
        return kind === "webgl2" ? null : getContext.call(this, kind, ...args);
      };
    });
    await fallback.goto(route("contact"));
    const link = fallback.getByRole("link", { name: "Contact us", exact: true });
    assert.equal(await link.getAttribute("href"), "/get-in-touch");
    assert.equal(await fallback.locator("canvas").count(), 0);
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ desktopWalkIn: true, windowProjection: true, phoneTouch: true,
      draftRetention: true, keyboardFocus: true, sameCanvas: true, noWebGLFallback: true, errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
