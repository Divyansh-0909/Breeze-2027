import {mkdir, writeFile} from "node:fs/promises";
import {launch, context, ready, view, unfix, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const label = process.argv[2] || "c8-3x";
const root = "reports/recovery-phase2-c8-material-2026-10-19";
const url = "http://127.0.0.1:3000/?arrival=hub&diagnostics" + (label === "c51" ? "" : "&quarryReview=scanned-material-multi");
const browser = await launch();
const captures = [], errors = [];
let current;
const views = [
  ["visitor-1", "Public visitor position 1", [-18, 1.72, -55], [-44, 8, -65], "Valid public walking location; controlled orientation toward the selected sector."],
  ["visitor-2", "Public visitor position 2", [-18, 1.72, -62], [-46, 8, -68], "Valid public location; existing stall occlusion is retained."],
  ["visitor-3", "Public visitor position 3", [-17, 1.72, -69], [-48, 9, -72], "Valid public location; existing stall occlusion is retained."],
  ["medium-inspection", "Medium-distance material inspection", [-32, 4, -59], [-45, 9, -66], "Non-public controlled inspection, approximately 15m; no walking boundary changed."],
  ["close-rock", "Close scanned mineral detail", [-39, 5, -62], [-44, 7, -65], "Non-public close inspection; material depth comes from the scan normal, not new rock geometry."],
  ["along-wall", "Along-wall view", [-35, 4, -54], [-49, 9, -74], "Non-public oblique inspection; unchanged C5.1 relief."],
  ["left-join", "Adjacent left material surface", [-25, 4, -70], [-50, 10, -77], "Non-public inspection of the existing Wall_14/Wall_15 material boundary."],
  ["right-join", "Adjacent right material surface", [-17, 1.72, -48], [-39, 11, -54], "Controlled orientation toward Wall_15's unchanged rim-side neighbour."],
  ["upper-rim", "Upper rim", [-18, 1.72, -55], [-44, 32, -65], "Valid public location looking upward; original geometry and sky retained."],
  ["wall-foot", "Rock-to-ground contact", [-33, 3, -66], [-47, 1, -69], "Non-public contact inspection; no floor or scree geometry altered."],
  ["hub-scaffold", "Hub and scaffold", [0, 1.72, -51], [0, 6.6, -92.7], "Original public hub spawn and Phase 1 scaffold composition."],
  ["tunnel-exit", "Tunnel exit and quarry reveal", [-1.3, 1.72, -38], [0, 7.4, -70], "Original protected tunnel-exit pose; entrance/tunnel reconstruction is out of scope."]
];

async function shot(page, prefix, id, title, note, lighting = "approved dusk") {
  await page.waitForTimeout(350);
  const file = `screenshots/${label}/${prefix}-${id}.png`;
  const data = await details(page);
  const extra = await page.evaluate(() => {
    const owner = window.__wallPreview;
    const clone = window.__wallRoots.at(-1)?.deref();
    const textures = new Set(), materials = new Set(), geometry = new Set();
    clone?.traverse(object => {
      if (!object.isMesh) return;
      geometry.add(object.geometry);
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        materials.add(material);
        for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
      }
    });
    const images = new Set([...textures].map(texture => texture.image));
    const canvas = document.querySelector("canvas");
    return {scanned: owner.materialDiagnostics?.(), wallResources: {geometries: geometry.size,
      materials: materials.size, wrappers: textures.size, uniqueImages: images.size,
      decodedRGBA8MipBytes: [...images].reduce((bytes, image) => bytes + image.width * image.height * 4 * 4 / 3, 0)},
      canvas: {width: canvas.width, height: canvas.height, cssWidth: innerWidth, cssHeight: innerHeight,
        effectiveDpr: canvas.width / innerWidth}, url: location.href};
  });
  await page.screenshot({path: root + "/" + file, scale: "css"});
  captures.push({label, file, title, note, lighting, requestedQuality: 0, requestedDpr: 1, ...extra, data});
  await mkdir(root + "/raw", {recursive: true});
  await writeFile(`${root}/raw/${label}-captures.json`, JSON.stringify({status: "RUNNING", captures, errors}, null, 2));
  console.log(file, extra.canvas.effectiveDpr);
}

try {
  for (const mobile of [false, true]) {
    const prefix = mobile ? "mobile" : "desktop";
    await mkdir(`${root}/screenshots/${label}`, {recursive: true});
    current = await context(browser, {viewport: mobile ? {width: 390, height: 844} : {width: 1366, height: 900},
      deviceScaleFactor: 1, isMobile: mobile, hasTouch: mobile});
    const page = await current.newPage();
    await page.goto(url);
    await page.waitForFunction(() => window.__gullyverse?.runtime);
    await page.evaluate(() => window.__gullyverse.runtime.setQuality(3));
    await ready(page);
    await page.addStyleTag({content: "[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
    for (const [id, title, position, target, note] of mobile ? views.filter(view => ["visitor-1", "hub-scaffold", "tunnel-exit"].includes(view[0])) : views) {
      await view(page, position, target, {fixed: true, quality: 0});
      await shot(page, prefix, id, title, note);
    }
    if (!mobile) {
      await view(page, [-32, 4, -59], [-45, 9, -66], {fixed: true, quality: 0});
      await page.evaluate(() => {
        let scene = window.__wallRoots.at(-1).deref(); while (scene.parent) scene = scene.parent;
        const lights = []; scene.traverse(object => { if (object.isLight) lights.push([object, object.visible]); });
        const hemi = lights.find(([object]) => object.isHemisphereLight)[0];
        const direction = lights.find(([object]) => object.isDirectionalLight)[0];
        const h = new hemi.constructor(0xffffff, 0x757575, 1.5), d = new direction.constructor(0xffffff, 1.1);
        d.position.set(-30, 30, -50); d.target.position.set(-44, 10, -65);
        lights.forEach(([object]) => { object.visible = false; });
        scene.add(h, d, d.target); window.__neutral = {scene, lights, h, d};
      });
      await shot(page, prefix, "neutral-material", "Neutral material inspection", "Temporary browser-only neutral lights; same maps, exposure, fog and geometry.", "temporary neutral diagnostic");
      await page.evaluate(() => {
        const {scene, lights, h, d} = window.__neutral;
        scene.remove(h, d, d.target); h.dispose(); d.dispose(); lights.forEach(([object, visible]) => { object.visible = visible; }); delete window.__neutral;
      });
    }
    await unfix(page);
    await page.evaluate(() => { const r = window.__gullyverse.runtime; r.clearInput(); r.pose = {x: 0, y: 1.72, z: -51, yaw: 0, pitch: 0.1}; r.setQuality(0); });
    await page.getByRole("button", {name: /^Map/}).click();
    await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().mapStage === "open", null, {timeout: 60000});
    await shot(page, prefix, "aerial-map", "Aerial map", "Actual approved map opening and camera; original coordinates and markers.");
    await current.close(); current = null;
  }
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1; }
finally {
  await current?.close(); await browser.close();
  await mkdir(root + "/raw", {recursive: true});
  await writeFile(`${root}/raw/${label}-captures.json`, JSON.stringify({status: errors.length ? "FAIL" : "PASS", browser: browser.version(), captures, errors}, null, 2));
}
