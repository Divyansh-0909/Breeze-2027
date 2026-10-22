import {mkdir, readFile, writeFile} from "node:fs/promises";
import {launch, context, ready, view, unfix, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const build = (await readFile(".next/BUILD_ID", "utf8")).trim();
const label = process.argv[2] || "corrected";
const root = "reports/recovery-quarry-fidelity-2026-10-19";
const selectors={c51:"",c8:"scanned-material-multi",recovered:"scanned-composition",material:"material-fidelity",corrected:"geology-fidelity"};
if(!(label in selectors))throw Error("Unknown mode "+label);
const url="http://127.0.0.1:3000/?arrival=hub&diagnostics"+(selectors[label]?"&quarryReview="+selectors[label]:"");
const browser = await launch();
const mapOnly = process.env.GULLYVERSE_MAP_ONLY === "1";
const previous = mapOnly ? JSON.parse(await readFile(`${root}/raw/${label}-captures.json`, "utf8")).captures : [];
const captures = previous.filter(c => !c.file.endsWith("mobile-aerial-map.png")), errors = [];
let current;
const views = [
  ["visitor-1", "Public visitor position 1", [-18, 1.72, -55], [-46, 8, -65], "Valid public walking location; controlled orientation toward the selected sector."],
  ["visitor-2", "Public visitor position 2", [-18, 1.72, -62], [-46, 8, -68], "Valid public location; existing stall occlusion is retained."],
  ["visitor-3", "Public visitor position 3", [-17, 1.72, -69], [-48, 9, -72], "Valid public location; existing stall occlusion is retained."],
  ["medium-inspection", "Medium-distance material inspection", [-32, 4, -59], [-45, 9, -66], "Non-public controlled inspection, approximately 15m; no walking boundary changed."],
  ["close-rock", "Close scanned mineral and physical detail", [-36, 4, -61], [-44, 4, -65], "Non-public close inspection; Corrected and recovered modes include native3D relief; material-only comparisons retain C5.1 geometry."],
  ["along-wall", "Along-wall physical depth", [-31, 3, -58], [-46, 4, -71], "Non-public front-side oblique inspection, avoiding the historical behind-cliff camera."],
  ["left-join", "Adjacent left material surface", [-25, 4, -70], [-50, 10, -77], "Non-public inspection of the existing Wall_14/Wall_15 material boundary."],
  ["right-join", "Adjacent right material surface", [-17, 1.72, -48], [-39, 11, -54], "Controlled orientation toward Wall_15's unchanged rim-side neighbour."],
  ["broad-upper", "Broad middle and upper wall", [-20, 1.72, -54], [-47, 20, -66], "Valid public view of the original35.557m study extent; framing retained across all modes."],
  ["upper-rim", "Upper rim", [-18, 1.72, -55], [-44, 32, -65], "Valid public location looking upward; Original sky retained; candidate rock documented separately."],
  ["wall-foot", "Rock-to-ground contact", [-33, 3, -66], [-47, 1, -69], "Non-public contact inspection; Original floor and scree unchanged."],
  ["hub-scaffold", "Hub and scaffold", [0, 1.72, -51], [0, 6.6, -92.7], "Original public hub spawn and Phase 1 scaffold composition."],
  ["scan-left-join", "Native scan left connection", [-32, 4, -71], [-46, 4, -70.7], "Non-public view of the scan/host annulus, distinct from the unchanged sector edge."],
  ["scan-right-join", "Native scan right connection", [-30, 4, -54], [-42, 4, -60.5], "Non-public view of the other native scan/host annulus."],
  ["historical-close", "Historical C8 close pose", [-42, 7, -62], [-46, 7.5, -65], "Non-public pose recorded in the approved historical C8 PDF, FOV58/Q0/DPR1."],
  ["historical-tunnel", "Historical tunnel-exit orientation", [0, 1.72, -43], [-46, 9.46, -65.47], "Entrance pose matching historical yaw1.1165/pitch0.1510 to rounding; entrance unchanged."],
  ["behind-left-stalls", "Behind-left-stalls inspection", [-27, 1.72, -64], [-46, 8, -68], "Historical behind-stall pose, outside public walking bounds; existing stalls retained."],
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
    return {composition: owner.compositionDiagnostics?.(), scanned: owner.materialDiagnostics?.(), wallResources: {geometries: geometry.size,
      materials: materials.size, wrappers: textures.size, uniqueImages: images.size,
      decodedRGBA8MipBytes: [...images].reduce((bytes, image) => bytes + image.width * image.height * 4 * 4 / 3, 0)},
      canvas: {width: canvas.width, height: canvas.height, cssWidth: innerWidth, cssHeight: innerHeight,
        effectiveDpr: canvas.width / innerWidth}, url: location.href};
  });
  await page.screenshot({path: root + "/" + file, scale: "css"});
  captures.push({label, file, title, note, lighting, requestedQuality: 0, requestedDpr: 1, ...extra, data});
  await mkdir(root + "/raw", {recursive: true});
  await writeFile(`${root}/raw/${label}-captures.json`, JSON.stringify({status: "RUNNING", build, captures, errors}, null, 2));
  console.log(file, extra.canvas.effectiveDpr);
}

try {
  for (const mobile of mapOnly ? [true] : [false, true]) {
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
    for (const [id, title, position, target, note] of mapOnly ? [] : mobile ? views.filter(view => ["visitor-1", "hub-scaffold", "tunnel-exit"].includes(view[0])) : views) {
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
        const root = window.__wallRoots.at(-1).deref(), saved = [], materials = [];
        root.traverse(object => { if (object.isMesh) {
          const material = (Array.isArray(object.material) ? object.material[0] : object.material).clone();
          for (const key of ["map", "normalMap", "roughnessMap", "aoMap", "metalnessMap"]) material[key] = null;
          material.vertexColors = false; material.color.set(0x777777); material.roughness = .92;
          saved.push([object, object.material]); materials.push(material); object.material = material;
        }}); window.__clay = {saved, materials};
      });
      await shot(page, prefix, "neutral-geometry", "Neutral geometry only", "Temporary neutral diagnostic with all fine textures/normals and vertex colours disabled; actual runtime geometry.", "temporary neutral geometry only");
      await page.evaluate(() => { const {saved, materials} = window.__clay; saved.forEach(([object, material]) => object.material = material); materials.forEach(material => material.dispose()); delete window.__clay; });
      await page.evaluate(() => {
        const {scene, lights, h, d} = window.__neutral;
        scene.remove(h, d, d.target); h.dispose(); d.dispose(); lights.forEach(([object, visible]) => { object.visible = visible; }); delete window.__neutral;
      });
    }
    await unfix(page);
    await page.evaluate(() => { const r = window.__gullyverse.runtime; r.clearInput(); r.pose = {x: 0, y: 1.72, z: -51, yaw: 0, pitch: 0.1}; r.setQuality(0); });
    await page.getByRole("button", {name: /^Map/}).click();
    await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().mapStage === "open", null, {timeout: 60000});
    // Browser-only capture control: the adaptive tier could change during map ascent.
    // Pin its already requested Q0 for this still, leaving production code unchanged.
    await page.evaluate(() => { const r=window.__gullyverse.runtime, original=r.setQuality.bind(r); r.setQuality=()=>original(0); original(0); });
    await shot(page, prefix, "aerial-map", "Aerial map", "Actual approved map opening and camera; original coordinates and markers.");
    await current.close(); current = null;
  }
} catch (error) { errors.push(String(error.stack)); process.exitCode = 1; }
finally {
  await current?.close(); await browser.close();
  await mkdir(root + "/raw", {recursive: true});
  await writeFile(`${root}/raw/${label}-captures.json`, JSON.stringify({status: errors.length ? "FAIL" : "PASS", build, browser: browser.version(), captures, errors}, null, 2));
}
