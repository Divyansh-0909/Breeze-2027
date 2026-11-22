const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium, devices } = require("playwright");

const origin = process.env.BREEZE_PREVIEW_ORIGIN;
const output = process.argv[2];
const preview = origin + "/runtime-preview/cypher?start=aftermovie";
const media = origin + "/after-movie.mp4";
const watchName = "Play Aftermovie";

async function ready(page) {
  await page.addInitScript(() => {
    const create = document.createElement;
    window.cypherTestVideos = [];
    document.createElement = function (name, ...options) {
      const element = create.call(this, name, ...options);
      if (name.toLowerCase() === "video") window.cypherTestVideos.push(element);
      return element;
    };
  });
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setFocusEmulationEnabled", { enabled: true });
  await page.bringToFront();
  assert.equal((await page.goto(preview, { timeout: 90_000 }))?.status(), 200);
  await page.addStyleTag({ content: "nextjs-portal { display: none !important; }" });
  await page.locator(".native-canvas canvas").waitFor({ timeout: 90_000 });
  await page.evaluate(() => {
    window.afterCanvas = document.querySelector("canvas");
    window.dispatchEvent(new Event("focus"));
  });
  const play = page.getByRole("button", { name: watchName, exact: true });
  await play.waitFor({ timeout: 180_000 });
  return play;
}

async function capture(page, file) {
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.screenshot({ path: path.join(output, file), timeout: 90_000 });
}

async function playing(page, time) {
  await page.waitForFunction(({ media, time }) => {
    const video = window.cypherTestVideos.find(item => item.src === media);
    return video?.videoWidth === 1920 && video.videoHeight === 1080 && !video.paused && video.currentTime >= time;
  }, { media, time }, { timeout: 90_000, polling: 100 });
}

async function seek(page, time) {
  await page.evaluate(({ media, time }) => {
    const video = window.cypherTestVideos.find(item => item.src === media);
    video.currentTime = time === "end" ? video.duration - 0.3 : time;
  }, { media, time });
}

async function backToScene(page, play) {
  await play.waitFor({ timeout: 120_000 });
  await page.waitForFunction(() => document.activeElement?.textContent === "Play Aftermovie");
  assert.ok(await page.evaluate(() => document.querySelectorAll("canvas").length === 1 &&
    document.querySelector("canvas") === window.afterCanvas &&
    window.cypherTestVideos.every(video => !video.hasAttribute("src") && video.paused)));
}

async function main() {
  assert.equal(new URL(origin).hostname, "127.0.0.1");
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN ?? "/usr/bin/chromium",
    args: ["--enable-webgl", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--no-sandbox"],
  });
  const errors = [];
  const setup = page => {
    let requests = 0;
    page.on("response", r => {
      if (r.url() === media) requests++;
      if (r.status() >= 400 && /\/models\/gullyverse\//.test(r.url())) errors.push(r.url());
    });
    page.on("pageerror", error => { errors.push(String(error)); console.error(error); });
    return () => requests;
  };
  try {
    const desktop = await browser.newPage({ viewport: { width: 720, height: 540 }, reducedMotion: "reduce" });
    const requests = setup(desktop);
    const play = await ready(desktop);
    assert.equal(requests(), 0);
    await desktop.setViewportSize({ width: 1120, height: 700 });
    await capture(desktop, "01-laptop-idle.png");
    await play.click();
    const screen = desktop.getByRole("region", { name: "Aftermovie playback" });
    await screen.getByRole("button", { name: "Enable sound", exact: true }).waitFor({ timeout: 90_000 });
    await playing(desktop, 0.3);
    assert.equal(await desktop.evaluate(url => window.cypherTestVideos.filter(video => video.src === url).length, media), 1);
    assert.ok(await desktop.evaluate(url => window.cypherTestVideos.find(video => video.src === url).muted, media));
    await screen.getByRole("button", { name: "Enable sound", exact: true }).click();
    assert.equal(await desktop.evaluate(url => window.cypherTestVideos.find(video => video.src === url).muted, media), false);
    await screen.getByRole("button", { name: "Mute sound", exact: true }).click();
    await seek(desktop, 8);
    await playing(desktop, 8.1);
    await capture(desktop, "02-laptop-playing.png");

    await seek(desktop, "end");
    await backToScene(desktop, play);
    console.log("The original 1080p video played and restored the viewing pose at the end.");
    await desktop.route("**/after-movie.mp4", route => route.fulfill({ status: 503, body: "Test media failure" }));
    await play.click();
    const failure = desktop.getByText("The Aftermovie could not play.", { exact: false });
    await failure.waitFor({ timeout: 90_000 });
    await backToScene(desktop, play);
    assert.equal(await desktop.getByRole("link", { name: "open the video", exact: true }).getAttribute("href"), "/after-movie.mp4");
    await desktop.unroute("**/after-movie.mp4");
    await play.click();
    await playing(desktop, 0.3);
    await desktop.keyboard.press("Escape");
    await backToScene(desktop, play);
    await desktop.close();

    const phone = await browser.newPage({ ...devices["iPhone 13"], reducedMotion: "reduce" });
    const phoneRequests = setup(phone);
    const mobilePlay = await ready(phone);
    assert.equal(phoneRequests(), 0);
    await mobilePlay.tap();
    await seek(phone, 8).catch(() => {});
    await playing(phone, 8.2);
    await capture(phone, "03-phone-portrait.png");
    await phone.setViewportSize({ width: 844, height: 390 });
    await capture(phone, "04-phone-landscape.png");
    await phone.getByRole("button", { name: "Exit Aftermovie", exact: true }).tap();
    await backToScene(phone, mobilePlay);
    const fallback = await browser.newPage();
    await fallback.addInitScript(() => {
      const original = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (kind, ...args) {
        return kind === "webgl2" ? null : original.call(this, kind, ...args);
      };
    });
    assert.equal((await fallback.goto(preview))?.status(), 200);
    assert.equal(await fallback.getByRole("link", {name: "Watch the Aftermovie", exact: true}).getAttribute("href"), "/after-movie.mp4");
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({status:"PASS", originalVideo:true, loadedOnPlay:true, soundToggle:true, ended:true,
      escape:true, failureRetry:true, portrait:true, landscape:true, sameCanvas:true, noWebGLFallback:true, errors}));
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
