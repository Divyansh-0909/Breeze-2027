import assert from "node:assert/strict";
import {mkdir, writeFile} from "node:fs/promises";
import {launch, context, ready, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";

const root = "reports/recovery-phase2-c8-material-2026-10-19";
const url = "http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=scanned-material-multi";
await mkdir(root + "/raw", {recursive: true});
const browser = await launch(), checks = [];
let current, page;
async function check(name, action) {
  try { checks.push({name, status: "PASS", evidence: await action()}); }
  catch (error) { checks.push({name, status: "FAIL", error: String(error.stack)}); process.exitCode = 1; }
  await writeFile(root + "/raw/material-browser-checks.json", JSON.stringify({checks, physicalHardware: false}, null, 2));
  console.log(name, checks.at(-1).status);
}
async function open() {
  current = await context(browser, {deviceScaleFactor: 0.25});
  await current.addInitScript(() => {
    window.__bitmapCloses = {count: 0, duplicate: 0};
    const old = ImageBitmap.prototype.close, closed = new WeakSet();
    ImageBitmap.prototype.close = function() {
      window.__bitmapCloses.count++;
      if (closed.has(this)) window.__bitmapCloses.duplicate++;
      closed.add(this); return old.call(this);
    };
  });
  page = await current.newPage();
}
const material = () => page.evaluate(() => window.__wallPreview.materialDiagnostics());
async function assertActive() {
  await ready(page);
  const data = await material();
  assert.equal(data.enabled, true);
  assert.equal(data.scale, 3);
  assert.equal(data.uniqueImages, 3);
  assert.equal(Math.round(data.decodedRGBA8MipBytes), 33554432);
  for (const texture of data.textures) {
    assert.equal(texture.channel, 0);
    for (const repeat of texture.repeat) assert.ok(Math.abs(repeat - 2 / 10.790622 / 3) < 1e-8);
  }
  return data;
}

try {
  await open(); await page.goto(url);
  await check("Private default is aligned approved 3x; clones reuse exact baseline geometry", async () => {
    const initial = await assertActive();
    const geometry = await page.evaluate(() => {
      const owner = window.__wallPreview, clone = window.__wallRoots.at(-1).deref();
      return owner.materialDiagnostics().selectedNodes.map(name => {
        const a = owner.asset.scene.getObjectByName(name), b = clone.getObjectByName(name);
        return {name, sameGeometry: a.geometry === b.geometry, baselineMaterial: a.material.name,
          cloneMaterial: b.material.name, vertexColoursUsed: b.material.vertexColors,
          hasBaselineColourAttribute: !!a.geometry.getAttribute("color")};
      });
    });
    assert.ok(geometry.every(node => node.sameGeometry && node.baselineMaterial === "Foundation_Dark_Rock_PBR" &&
      node.cloneMaterial === "Recovered_C8_Scanned_Multi_PBR" && !node.vertexColoursUsed && node.hasBaselineColourAttribute));
    const requested = await page.evaluate(() => performance.getEntriesByType("resource").map(entry => entry.name));
    assert.equal(requested.filter(name => name.endsWith("/quarry-foundation-refined/foundation-geometry.glb")).length, 1);
    assert.ok(!requested.some(name => /rock-calibration|scanned-relief|site-scale-cliff|calibrated-region/.test(name)));
    return {initial, geometry, requested};
  });
  await check("Ten covered material/scale cycles preserve images, geometry and bounded allocations", async () => {
    const first = await material(), samples = [];
    const geometryIDs = await page.evaluate(() => {
      const values = []; window.__wallPreview.asset.scene.traverse(object => { if (object.isMesh) values.push(object.geometry.uuid); }); return values;
    });
    for (let cycle = 0; cycle < 10; cycle++) {
      await page.evaluate(() => window.__wallPreview.setScannedMaterial(false)); await ready(page);
      for (const scale of [4, 1, 3]) {
        await page.evaluate(scale => window.__wallPreview.setScannedMaterial(true, scale), scale); await ready(page);
        const state = await material();
        assert.deepEqual(state.textures.map(texture => texture.uuid), first.textures.map(texture => texture.uuid));
        assert.deepEqual(state.textures.map(texture => texture.source), first.textures.map(texture => texture.source));
        assert.equal(state.uniqueImages, 3);
        assert.equal(state.scale, scale);
      }
      samples.push({cycle, data: await details(page)});
    }
    const finalIDs = await page.evaluate(() => { const values = []; window.__wallPreview.asset.scene.traverse(object => { if (object.isMesh) values.push(object.geometry.uuid); }); return values; });
    assert.deepEqual(finalIDs, geometryIDs);
    const a = samples[1].data, b = samples.at(-1).data;
    assert.ok(a.stats && b.stats);
    assert.ok(b.stats.textures <= a.stats.textures && b.stats.geometries <= a.stats.geometries);
    assert.ok(b.contexts[0].stats.Program.active <= a.contexts[0].stats.Program.active);
    assert.equal((await page.evaluate(() => window.__bitmapCloses)).duplicate, 0);
    return {first, samples, final: await material()};
  });
  await check("Actual context loss/recovery retains material, pose and persistent Canvas", async () => {
    const canvas = await page.evaluateHandle(() => document.querySelector("canvas"));
    const before = await details(page), old = await material();
    await page.evaluate(() => { window.__loss = document.querySelector("canvas").getContext("webgl2").getExtension("WEBGL_lose_context"); window.__loss.loseContext(); });
    await page.waitForSelector('[data-phase="context-lost"]'); await page.waitForTimeout(250);
    await page.evaluate(() => window.__loss.restoreContext()); await assertActive();
    const after = await details(page), next = await material();
    assert.equal(await canvas.evaluate(canvas => canvas === document.querySelector("canvas")), true);
    assert.deepEqual(next.textures.map(texture => texture.uuid), old.textures.map(texture => texture.uuid));
    assert.ok(Math.hypot(before.pose.x - after.pose.x, before.pose.y - after.pose.y, before.pose.z - after.pose.z) < 1e-6);
    return {before, after, old, next};
  });
  await check("Complete fallback unmount closes only owned images, once", async () => {
    const owner = await page.evaluateHandle(() => window.__wallPreview);
    await page.getByRole("button", {name: "Use without 3D", exact: true}).click();
    await page.waitForFunction(() => !document.querySelector("canvas"));
    const result = await owner.evaluate(owner => ({disposed: owner.disposed, consumers: owner.consumers,
      hasAsset: !!owner.asset, material: !!owner.borrowScannedMaterial(), trace: owner.trace}));
    assert.equal(result.disposed, true); assert.equal(result.consumers, 0); assert.equal(result.hasAsset, false); assert.equal(result.material, false);
    assert.ok(result.trace.some(event => event.event === "scanned-material-owner-disposal" && event.images === 3));
    const closes = await page.evaluate(() => window.__bitmapCloses); assert.equal(closes.duplicate, 0);
    return {result, closes};
  });
  await current.close();
  await open(); await page.route("**/recovered-c8-material/scanned-materials.glb", route => route.abort());
  await check("Failed scanned holder falls back to C5.1 and retries without reloading world geometry", async () => {
    await page.goto(url); await ready(page);
    const failed = await material(); assert.equal(failed.enabled, false); assert.equal(failed.uniqueImages, 0);
    await page.unroute("**/recovered-c8-material/scanned-materials.glb");
    await page.evaluate(() => window.__wallPreview.setScannedMaterial(true, 3));
    const retry = await assertActive();
    const requests = await page.evaluate(() => performance.getEntriesByType("resource").filter(entry => entry.name.endsWith("/quarry-foundation-refined/foundation-geometry.glb")).length);
    assert.equal(requests, 1);
    return {failed, retry, geometryRequests: requests};
  });
  await current.close();
  await open(); await page.route("**/recovered-c8-material/scanned-materials.glb", route => route.fulfill({path: "public/models/gullyverse/quarry-foundation-refined/foundation-materials.glb", contentType: "model/gltf-binary"}));
  await check("Invalid scanned material family is rejected and its owned resources disposed", async () => {
    await page.goto(url); await ready(page);
    const failed = await material(); assert.equal(failed.enabled, false);
    const disposal = await page.evaluate(() => window.__wallPreview.trace.find(event => event.event === "scanned-material-rejected-disposal"));
    assert.ok(disposal?.textures > 0 && disposal?.images > 0);
    assert.equal((await page.evaluate(() => window.__bitmapCloses)).duplicate, 0);
    return {failed, disposal};
  });
  await current.close();
  for (const file of ["foundation-geometry.glb", "foundation-materials.glb"]) {
    await open(); await page.route("**/quarry-foundation-refined/" + file, route => route.abort());
    await check("Failed " + file + " retains the connected shell and retries with C8", async () => {
      await page.goto(url); await ready(page);
      const failed = await details(page);
      assert.equal(await page.evaluate(() => window.__wallPreview.foundationEnabled), false);
      assert.equal(failed.wall.selectedNodes.length, 18);
      await page.unroute("**/quarry-foundation-refined/" + file);
      await page.evaluate(() => window.__wallPreview.setFoundation(true));
      await assertActive();
      const retry = await details(page); assert.equal(retry.wall.selectedNodes.length, 35);
      return {failed, retry};
    });
    await current.close();
  }
  await open();
  let releaseDelayedMaterial;
  const materialGate = new Promise(resolve => { releaseDelayedMaterial = resolve; });
  await page.route("**/recovered-c8-material/scanned-materials.glb", async route => { await materialGate; await route.continue().catch(() => {}); });
  await check("Delayed new material stays covered; unmount retires unpublished resources safely", async () => {
    await page.goto(url);
    await page.waitForFunction(() => window.__wallPreview?.materialPreparing &&
      window.__wallPreview.trace.some(event => event.event === "foundation-asset-ready"), null, {timeout: 30000});
    assert.ok(await page.locator("[data-wall-cover]").count());
    assert.equal(await page.evaluate(() => window.__wallPreview.state.busy), true);
    const owner = await page.evaluateHandle(() => window.__wallPreview);
    await page.getByRole("button", {name: "Use without 3D", exact: true}).click();
    await page.waitForFunction(() => !document.querySelector("canvas"));
    releaseDelayedMaterial(); await page.waitForTimeout(3500);
    const result = await owner.evaluate(owner => ({disposed: owner.disposed, asset: !!owner.asset,
      material: !!owner.borrowScannedMaterial(), trace: owner.trace}));
    assert.equal(result.disposed, true); assert.equal(result.asset, false); assert.equal(result.material, false);
    assert.equal((await page.evaluate(() => window.__bitmapCloses)).duplicate, 0);
    return {...result, baselinePreparedWhileMaterialBlocked: true};
  });
  releaseDelayedMaterial();
  await current.close(); await open();
  await check("Public default keeps C5.1 and downloads no recovered material", async () => {
    await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics"); await ready(page);
    assert.equal(await page.locator("[data-scanned-material-controls]").count(), 0);
    const result = await page.evaluate(() => ({isScanned: typeof window.__wallPreview.materialDiagnostics === "function",
      requests: performance.getEntriesByType("resource").map(entry => entry.name),
      material: window.__wallPreview.asset.scene.getObjectByName("Foundation_Wall_15_LOD0").material.name}));
    assert.equal(result.isScanned, false); assert.equal(result.material, "Foundation_Dark_Rock_PBR");
    assert.ok(!result.requests.some(name => name.includes("/recovered-c8-material/")));
    return result;
  });
} finally {
  await current?.close(); await browser.close();
  await writeFile(root + "/raw/material-browser-checks.json", JSON.stringify({checks, physicalHardware: false}, null, 2));
}
