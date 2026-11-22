const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN;
const output = process.argv[2];
const preview = origin + "/runtime-preview/cypher?start=plaza";
const stops = ["Market lane", "Navigation board", "Accommodation", "Contact", "Cypher plaza", "Events", "Team", "Aftermovie"];

async function ready(page) {
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await page.bringToFront();
  assert.equal((await page.goto(preview, { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".native-canvas canvas").waitFor({ timeout: 90_000 });
  await page.evaluate(() => {
    window.mapCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  await page.getByRole("button", { name: "Map", exact: true }).waitFor({ timeout: 240_000 });
}

async function capture(page, file) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.screenshot({ path: path.join(output, file), timeout: 90_000 });
}

/** Every stop label is on screen, inside the viewport and not overlapping another label. */
async function openMap(page, open) {
  await open();
  const map = page.getByRole("region", { name: "Cypher map" });
  await map.waitFor({ timeout: 30_000 });
  await page.waitForFunction(() => document.querySelector(".cypher-map")?.dataset.stage === "open", null, { timeout: 30_000 });
  await page.waitForFunction(() => Number(getComputedStyle(document.querySelector(".cypher-map-markers")).opacity) > 0.99);
  const boxes = await page.evaluate(() => [...document.querySelectorAll(".cypher-map-stop, .cypher-map-here")].map(node => {
    const box = node.getBoundingClientRect();
    return { label: node.textContent, visible: getComputedStyle(node).visibility, x: box.x, y: box.y, w: box.width, h: box.height };
  }));
  const viewport = page.viewportSize();
  assert.deepEqual(boxes.filter(box => box.label !== "You are here").map(box => box.label), stops);
  for (const box of boxes) {
    assert.equal(box.visible, "visible", box.label);
    assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.w <= viewport.width && box.y + box.h <= viewport.height, box.label);
  }
  // Labels and their dots stay clear of the map header and the walking toolbar.
  const band = await page.evaluate(() => ({
    top: document.querySelector(".cypher-map-header").getBoundingClientRect().bottom,
    bottom: document.querySelector(".gate-controls").getBoundingClientRect().top,
    dots: [...document.querySelectorAll(".cypher-map-dot")].map(node => {
      const box = node.getBoundingClientRect();
      return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
    }),
  }));
  for (const box of boxes) assert.ok(box.y >= band.top && box.y + box.h <= band.bottom, `${box.label} leaves the map band`);
  for (const dot of band.dots) assert.ok(dot.y >= band.top && dot.y <= band.bottom, `a marker dot at ${dot.y} leaves the map band`);
  // Labels never cover a marker dot.
  for (const dot of band.dots) for (const box of boxes) {
    assert.ok(!(dot.x > box.x && dot.x < box.x + box.w && dot.y > box.y && dot.y < box.y + box.h), `${box.label} covers a marker`);
  }
  for (const a of boxes) for (const b of boxes) {
    if (a === b) continue;
    const overlap = a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
    assert.ok(!overlap, `${a.label} overlaps ${b.label}`);
  }
  // Keyboard focus starts on the stop nearest the visitor.
  assert.equal(await page.evaluate(() => document.activeElement?.classList.contains("cypher-map-stop")), true);
  return map;
}

async function landed(page, start, button) {
  await page.waitForFunction(() => !document.querySelector(".cypher-map"), null, { timeout: 30_000 });
  const expected = start === "market" ? null : start;
  await page.waitForFunction(value => new URL(location.href).searchParams.get("start") === value, expected, { timeout: 30_000 });
  if (button) await page.waitForFunction(name => document.activeElement?.textContent === name, button, { timeout: 30_000 });
  assert.ok(await page.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
    document.querySelector("canvas") === window.mapCanvas));
}

async function main() {
  assert.equal(new URL(origin).hostname, "127.0.0.1");
  const browser = await chromium.launch({
    ...(process.env.CHROMIUM_BIN ? { executablePath: process.env.CHROMIUM_BIN } : {}),
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
    const desktop = await browser.newPage({ viewport: { width: 1120, height: 700 }, reducedMotion: "reduce" });
    watch(desktop);
    await ready(desktop);
    await openMap(desktop, () => desktop.keyboard.press("m"));
    await capture(desktop, "01-laptop-map.png");
    await desktop.getByRole("button", { name: "Team", exact: true }).click();
    await landed(desktop, "team", "View team murals");
    await capture(desktop, "02-laptop-team-arrival.png");
    await openMap(desktop, () => desktop.getByRole("button", { name: "Map", exact: true }).click());
    await desktop.getByRole("button", { name: "Aftermovie", exact: true }).focus();
    await desktop.keyboard.press("Enter");
    await landed(desktop, "aftermovie", "Play Aftermovie");
    await openMap(desktop, () => desktop.keyboard.press("m"));
    await desktop.getByRole("button", { name: "Market lane", exact: true }).click();
    await landed(desktop, "market");
    await capture(desktop, "03-laptop-market-arrival.png");
    await openMap(desktop, () => desktop.keyboard.press("m"));
    await desktop.keyboard.press("Escape");
    await desktop.waitForFunction(() => !document.querySelector(".cypher-map"));
    await desktop.waitForFunction(() => document.activeElement?.textContent === "Map");
    await desktop.close();
    console.log("Laptop: M, button and Enter opened travel; Team and Aftermovie focused their actions; Escape returned to Map.");

    const phone = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    watch(phone);
    await ready(phone);
    await openMap(phone, () => phone.getByRole("button", { name: "Map", exact: true }).tap());
    await capture(phone, "04-phone-portrait-map.png");
    await phone.getByRole("button", { name: "Contact", exact: true }).tap();
    await landed(phone, "contact", "Leave a message");
    await capture(phone, "05-phone-contact-arrival.png");
    await phone.setViewportSize({ width: 844, height: 390 });
    await openMap(phone, () => phone.getByRole("button", { name: "Map", exact: true }).tap());
    await capture(phone, "06-phone-landscape-map.png");
    await phone.getByRole("button", { name: "Accommodation", exact: true }).tap();
    await landed(phone, "accommodation", "View accommodation");
    await phone.reload();
    await phone.getByRole("button", { name: "View accommodation" }).waitFor({ timeout: 240_000 });
    await phone.close();
    console.log("Phone: portrait and landscape maps fit; touch travel reached Contact and Accommodation; refresh kept the stop.");
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ status: "PASS", stops: stops.length, keyboard: true, touch: true, portrait: true,
      landscape: true, sameCanvas: true, focusHandoff: true, refreshKeepsStop: true, errors }));
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
