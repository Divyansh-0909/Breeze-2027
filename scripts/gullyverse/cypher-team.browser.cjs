const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN;
const output = process.argv[2];
const start = origin + "/runtime-preview/cypher?start=team";
const names = ["Organising Committee", "Content", "Design", "Marketing",
  "Public Relations", "Sponsorship", "Videography", "Web Development"];

async function load(page, url) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await page.bringToFront();
  assert.equal((await page.goto(url, { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".native-canvas canvas").waitFor({ timeout: 90_000 });
  await page.evaluate(() => {
    window.teamTestCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  const open = page.getByRole("button", { name: "View team murals", exact: true });
  try {
    await open.waitFor({ timeout: 180_000 });
  } catch (error) {
    console.error("Team preview state:", await page.locator("body").innerText({ timeout: 15_000 }));
    throw error;
  }
  return open;
}

async function select(dialog, index) {
  await dialog.getByRole("heading", { name: names[index], exact: true }).waitFor({ timeout: 45_000 });
  await dialog.getByRole("status").waitFor({ state: "hidden", timeout: 45_000 });
  assert.equal(await dialog.getByText(`${index + 1} / 8`, { exact: true }).count(), 1);
}

async function capture(page, filename) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.screenshot({ path: path.join(output, filename), timeout: 90_000 });
}

async function main() {
  assert.equal(new URL(origin).hostname, "127.0.0.1");
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN ?? "/usr/bin/chromium",
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  const errors = [];
  const watch = page => {
    page.on("pageerror", e => errors.push(String(e)));
    page.on("response", response => {
      if (response.status() >= 400 && /\/models\/gullyverse\//.test(response.url()) &&
        !response.url().endsWith("/design.webp")) errors.push(response.url());
    });
  };
  try {
    const desktop = await browser.newPage({ viewport: { width: 720, height: 540 }, reducedMotion: "reduce" });
    watch(desktop);
    const open = await load(desktop, start);
    await desktop.setViewportSize({ width: 1120, height: 700 });
    await open.click();
    const dialog = desktop.getByRole("dialog", { name: "Team murals" });
    await select(dialog, 0);
    await capture(desktop, "01-organising-committee.png");
    await desktop.keyboard.press("ArrowRight");
    await select(dialog, 1);
    await capture(desktop, "02-content.png");

    await desktop.route("**/locked-rev15z-team/design.webp", route => route.fulfill({ status: 503, body: "Test retry" }));
    const next = dialog.getByRole("button", { name: "Next mural" });
    await next.click();
    await dialog.getByText("The mural could not load.", { exact: true }).waitFor();
    assert.equal(await dialog.getByRole("heading", { name: "Content", exact: true }).count(), 1);
    await desktop.unroute("**/locked-rev15z-team/design.webp");
    await dialog.getByRole("button", { name: "Retry", exact: true }).click();
    for (let index = 2; index < names.length; index++) {
      await select(dialog, index);
      await capture(desktop, `${String(index + 1).padStart(2, "0")}-${names[index].toLowerCase().replaceAll(" ", "-")}.png`);
      if (index + 1 < names.length) await next.click();
    }
    const lastSlide = desktop.url();
    assert.equal(new URL(lastSlide).searchParams.get("team"), "7");
    await next.click();
    await select(dialog, 0);
    assert.equal(await desktop.locator(".native-canvas canvas").count(), 1);
    await desktop.keyboard.press("Escape");
    await open.waitFor({ timeout: 90_000 });
    await desktop.waitForFunction(() => document.activeElement?.textContent === "View team murals");
    assert.ok(await desktop.evaluate(() => document.querySelector("canvas") === window.teamTestCanvas));
    await desktop.close();
    console.log("Desktop verified all eight murals, retry, wraparound and return focus.");

    const phone = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    watch(phone);
    const mobileOpen = await load(phone, lastSlide);
    await mobileOpen.tap();
    const mobileDialog = phone.getByRole("dialog", { name: "Team murals" });
    await select(mobileDialog, 7);
    const touch = await phone.context().newCDPSession(phone);
    await touch.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: 320, y: 254 }] });
    await touch.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: 165, y: 254 }] });
    await touch.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: 53, y: 254 }] });
    await touch.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await select(mobileDialog, 0);
    await capture(phone, "09-phone-organising-committee.png");
    await mobileDialog.getByRole("button", { name: "Next mural" }).tap();
    await select(mobileDialog, 1);
    await capture(phone, "10-phone-content.png");
    await phone.setViewportSize({ width: 844, height: 390 });
    await capture(phone, "11-landscape-content.png");
    await mobileDialog.getByRole("button", { name: "Close team murals" }).tap();
    await mobileOpen.waitFor({ timeout: 90_000 });
    assert.ok(await phone.evaluate(() => document.querySelector("canvas") === window.teamTestCanvas));
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ status: "PASS", murals: names.length, sameCanvas: true,
      failureRecovery: true, keyboard: true, mobileSwipe: true, persistedLink: true, errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
