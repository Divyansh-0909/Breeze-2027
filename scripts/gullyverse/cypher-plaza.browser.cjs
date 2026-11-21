const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN ?? "http://127.0.0.1:8898";
const route = origin + "/runtime-preview/cypher?start=approach";
const output = process.argv[2];
const plaza = "Cypher plaza";
const approach = "Navigation approach";

async function openRoute(page) {
  await page.bringToFront();
  assert.equal((await page.goto(route, { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.getByText(approach, { exact: true }).waitFor({ timeout: 180_000 });
  await page.evaluate(() => {
    window.plazaCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  await page.waitForFunction(() => (
    Number(getComputedStyle(document.querySelector(".native-curtain")).opacity) < 0.02
  ), null, { timeout: 120_000 });
}

async function walkTo(page, key, label) {
  await page.keyboard.down(key);
  try {
    await page.getByText(label, { exact: true }).waitFor({ timeout: 180_000 });
  } finally {
    await page.keyboard.up(key);
  }
}

async function look(page, dx, dy = 0) {
  await page.mouse.move(560, 300);
  await page.mouse.down();
  await page.mouse.move(560 + dx, 300 + dy, { steps: 4 });
  await page.mouse.up();
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
}

function watchAssets(page) {
  const files = new Set();
  const errors = [];
  page.on("pageerror", error => errors.push(String(error)));
  page.on("console", message => {
    if (message.type() === "error" && /WebGLProgram|Shader Error/.test(message.text())) errors.push(message.text());
  });
  page.on("response", response => {
    const file = new URL(response.url()).pathname;
    if (!file.startsWith("/models/gullyverse/")) return;
    if (response.status() >= 400) errors.push(`${response.status()} ${file}`);
    else if (response.ok()) files.add(file);
  });
  return { files, errors };
}

async function main() {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN,
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  try {
    const desktop = await browser.newPage({ viewport: { width: 720, height: 450 } });
    const loaded = watchAssets(desktop);
    const capture = name => desktop.screenshot({ path: path.join(output, name + ".png"), timeout: 120_000 });
    await openRoute(desktop);
    await walkTo(desktop, "w", plaza);
    console.log("The gate led into the expanded plaza.");
    for (const zone of ["plaza", "audience"]) {
      assert.ok([...loaded.files].some(file => file.endsWith(`/locked-rev15z-cypher-${zone}/contact-frontage.optimized.glb`)));
    }
    await desktop.setViewportSize({ width: 1120, height: 700 });
    await look(desktop, 0, 59);
    await capture("01-plaza-screen");
    await look(desktop, -325);
    await capture("02-events-frontage");
    await look(desktop, 325);
    await look(desktop, 325);
    await capture("03-team-frontage");
    await look(desktop, -325);
    await desktop.setViewportSize({ width: 720, height: 450 });
    await walkTo(desktop, "s", approach);
    assert.ok(await desktop.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
      document.querySelector("canvas") === window.plazaCanvas));
    assert.deepEqual(loaded.errors, []);
    await desktop.close();
    console.log("Desktop return and canvas identity verified.");

    const mobile = await browser.newPage({ ...devices["iPhone 13"] });
    const phone = watchAssets(mobile);
    await openRoute(mobile);
    const forward = await mobile.getByRole("button", { name: "Walk forward" }).boundingBox();
    assert.ok(forward);
    const input = await mobile.context().newCDPSession(mobile);
    await input.send("Input.dispatchTouchEvent", {
      type: "touchStart", touchPoints: [{ x: forward.x + forward.width / 2, y: forward.y + forward.height / 2 }],
    });
    try {
      await mobile.getByText(plaza, { exact: true }).waitFor({ timeout: 180_000 });
    } finally {
      await input.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    }
    for (const zone of ["plaza", "audience"]) {
      assert.ok([...phone.files].some(file => file.endsWith(`/locked-rev15z-cypher-${zone}/contact-frontage.mobile.glb`)));
    }
    assert.ok(await mobile.evaluate(() => document.querySelector("canvas") === window.plazaCanvas));
    assert.deepEqual(phone.errors, []);
    console.log(JSON.stringify({ desktopRoundTrip: true, phoneTouchToPlaza: true, sameCanvas: true, assetErrors: [] }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
