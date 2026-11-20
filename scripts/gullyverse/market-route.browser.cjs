const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN ?? "http://127.0.0.1:8898";
const output = process.argv[2];

async function walkTo(page, key, zone) {
  await page.keyboard.down(key);
  try {
    await page.getByRole("region", { name: "Walk through the cypher gate" })
      .getByText(zone, { exact: true }).waitFor({ timeout: 180_000 });
  } finally {
    await page.keyboard.up(key);
  }
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN,
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1120, height: 700 } });
    const capture = name => page.screenshot({ path: path.join(output, name + ".png"), timeout: 90_000 });
    const errors = [];
    const assets = new Set();
    page.on("pageerror", error => errors.push(String(error)));
    page.on("console", message => {
      if (message.type() === "error" && /WebGLProgram|Shader Error/.test(message.text())) errors.push(message.text());
    });
    page.on("response", response => {
      if (!/\/models\/gullyverse\//.test(response.url())) return;
      if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
      else if (response.ok()) assets.add(new URL(response.url()).pathname);
    });
    await page.bringToFront();
    assert.equal((await page.goto(origin + "/runtime-preview/cypher?start=quarry", { timeout: 90_000 }))?.status(), 200);
    await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
    const entrance = page.getByRole("button", { name: "Enter Gullyverse" });
    try {
      await entrance.waitFor({ timeout: 120_000 });
    } catch (error) {
      console.error(await page.locator("body").innerText(), [...assets], errors);
      throw error;
    }
    assert.ok([...assets].some(url => url.endsWith("/c9-cave-recovery/cave-entrance.glb")), "The original C9 cave loaded");
    await page.evaluate(() => { window.routeCanvas = document.querySelector("canvas"); });
    console.log("Original quarry entrance ready.");
    await capture("01-quarry");
    await page.setViewportSize({ width: 960, height: 600 });
    await entrance.click();
    await page.locator('[data-world="quarry"][data-phase="entrance"]').waitFor();
    const arrival = page.locator('[data-world="market"]:is([data-phase="local"], [data-phase="error"])');
    await arrival.waitFor({ timeout: 180_000 });
    assert.equal(await arrival.getAttribute("data-phase"), "local", (await page.locator("body").innerText()) + "\n" + errors.join("\n"));
    await page.getByText("Market lane", { exact: true }).waitFor();
    await page.waitForFunction(() => Number(getComputedStyle(document.querySelector(".native-curtain")).opacity) < 0.02);
    assert.ok([...assets].some(url => url.includes("/locked-rev15z-market-south/") && url.endsWith(".glb")));
    assert.ok([...assets].some(url => url.includes("/locked-rev15z-market-north/") && url.endsWith(".glb")));
    await capture("02-market");
    console.log("The original entrance sequence reached the market.");

    await page.setViewportSize({ width: 960, height: 600 });
    await walkTo(page, "w", "Navigation approach");
    await capture("03-upper-lane");
    console.log("The market road connects to the navigation approach.");
    await walkTo(page, "w", "Cypher gate");
    await capture("04-gate");
    await walkTo(page, "w", "Cypher forecourt");
    await capture("05-forecourt");
    await walkTo(page, "s", "Market lane");
    assert.ok(await page.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
      document.querySelector("canvas") === window.routeCanvas));
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ originalQuarry: true, quarryHandoff: true, keyboardRoundTrip: true, sameCanvas: true, assetErrors: errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
