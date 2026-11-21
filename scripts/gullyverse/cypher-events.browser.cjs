const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

async function main() {
  const origin = process.env.BREEZE_PREVIEW_ORIGIN;
  assert.equal(new URL(origin).hostname, "127.0.0.1");
  const output = process.argv[2];
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN ?? "/usr/bin/chromium",
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  try {
    const page = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    const errors = [];
    page.on("pageerror", error => errors.push(String(error)));
    page.on("response", response => {
      if (response.status() >= 400 && /\/models\/gullyverse\//.test(response.url())) errors.push(response.url());
    });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
    await page.bringToFront();
    assert.equal((await page.goto(origin + "/runtime-preview/cypher?start=events", { timeout: 90_000 }))?.status(), 200);
    await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
    await page.locator(".native-canvas canvas").waitFor({ timeout: 90_000 });
    await page.evaluate(() => {
      window.eventsCanvas = document.querySelector("canvas");
      window.dispatchEvent(new Event("focus"));
    });
    const browse = page.getByRole("button", { name: "Browse event posters", exact: true });
    await browse.waitFor({ timeout: 180_000 });
    await browse.tap();

    const dialog = page.getByRole("dialog", { name: "Events wall" });
    const posterLinks = dialog.locator(".cypher-event-links li button");
    await dialog.waitFor({ timeout: 120_000 });
    const toFile = name => page.screenshot({ path: path.join(output, name), timeout: 90_000 });
    assert.equal(await posterLinks.count(), 8);
    assert.equal(await posterLinks.first().textContent(), "Fixture event 01");
    await toFile("01-events-first-page.png");
    await dialog.getByRole("button", { name: "Next", exact: true }).tap();
    assert.equal(await posterLinks.count(), 8);
    assert.equal(await posterLinks.first().textContent(), "Fixture event 09");
    await dialog.getByRole("button", { name: "Next", exact: true }).tap();
    assert.equal(await posterLinks.count(), 1);
    assert.equal(await posterLinks.first().textContent(), "Fixture event 17");
    await toFile("02-events-last-page.png");

    const viewport = page.viewportSize();
    await page.touchscreen.tap(Math.round(viewport.width * 0.242), Math.round(viewport.height * 0.521));
    await dialog.getByText("Registration closed", { exact: true }).waitFor();
    assert.match(await dialog.getByRole("link", { name: "Event details" }).getAttribute("href"), /^\/events\/[\da-f-]+$/);
    await toFile("03-events-details.png");
    await dialog.getByRole("button", { name: "Back to posters" }).tap();
    assert.equal(await posterLinks.first().textContent(), "Fixture event 17");
    await dialog.getByRole("button", { name: "Close Events" }).tap();
    await browse.waitFor({ timeout: 120_000 });
    assert.ok(await page.evaluate(() => document.activeElement?.textContent === "Browse event posters"));
    assert.ok(await page.evaluate(() => document.querySelector("canvas") === window.eventsCanvas));
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ pagination: [8, 8, 1], catalogDetails: true, closedRegistrationVisible: true, sameCanvas: true, errors }));
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
