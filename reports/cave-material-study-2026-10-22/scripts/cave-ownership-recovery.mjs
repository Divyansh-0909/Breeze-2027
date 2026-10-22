import assert from "node:assert/strict";
import {mkdir, readFile, writeFile} from "node:fs/promises";
import {launch, context, ready, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";
const root = "reports/cave-material-study-2026-10-22", url = "http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=rock_01";
const browser = await launch(), checks = []; let current, page;
await mkdir(root + "/raw", {recursive: true});
async function check(name, action) {
  try { checks.push({name, status: "PASS", evidence: await action()}); }
  catch (error) { checks.push({name, status: "FAIL", error: String(error.stack)}); process.exitCode = 1; }
  console.log(name, checks.at(-1).status);
  await writeFile(root + "/raw/composition-browser-checks.json", JSON.stringify({checks, physicalHardware: false}, null, 2));
}
async function open() {
  await current?.close(); current = await context(browser, {deviceScaleFactor: .25});
  await current.addInitScript(() => {
    window.__shaderLinks = [];
    const get = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, ...args) {
      const gl = get.call(this, type, ...args);
      if (gl && ["webgl", "webgl2"].includes(type) && !gl.__c9LinkAudit) {
        gl.__c9LinkAudit = true; const link = gl.linkProgram.bind(gl);
        gl.linkProgram = function(program) { const value = link(program); window.__shaderLinks.push({gl, program:new WeakRef(program)}); return value; };
      }
      return gl;
    };
    window.__bitmapCloses = {count: 0, duplicate: 0};
    const original = ImageBitmap.prototype.close, closed = new WeakSet();
    ImageBitmap.prototype.close = function() { window.__bitmapCloses.count++; if (closed.has(this)) window.__bitmapCloses.duplicate++; closed.add(this); return original.call(this); };
  }); page = await current.newPage();
}
const info = () => page.evaluate(() => ({composition: window.__wallPreview.compositionDiagnostics(), material: window.__wallPreview.materialDiagnostics(), state: window.__wallPreview.state}));
async function active() {
  await ready(page); const data = await info();
  assert.equal(data.composition.ready, true); assert.equal(data.composition.enabled, true);
  assert.equal(data.composition.sourceUniformScale, .9); assert.equal(data.material.scale, 3);
  assert.equal(data.material.enabled, true); assert.equal(data.material.uniqueImages, 3);
  assert.equal(data.composition.geometryNormalImages, 1); assert.equal(data.composition.geometryNormal.channel, 1);
  for (const texture of data.material.textures) assert.ok(texture.repeat.every(n => Math.abs(n - 2 / 10.790622 / 3) < 1e-8));
  return data;
}
const resources = () => page.evaluate(() => performance.getEntriesByType("resource").map(entry => ({url: entry.name, bytes: entry.transferSize})));
try {
  await open(); await page.goto(url);
  await check("Fidelity uses the original35.557m local region, shared C8 maps and unchanged non-target geometry", async () => {
    const data = await active();
    const parts = await page.evaluate(() => {
      const owner = window.__wallPreview, clone = window.__wallRoots.at(-1).deref(), family = owner.borrowScannedMaterial(), nodes = [];
      clone.traverse(object => { if (!object.isMesh) return; const baseline = owner.asset.scene.getObjectByName(object.name); const material = object.material;
        nodes.push({name: object.name, sameGeometry: object.geometry === baseline.geometry, geo: object.geometry.uuid,
          albedoShared: material.map === family.map, roughnessShared: material.roughnessMap === family.roughnessMap,
          normalChannel: material.normalMap?.channel, vertexColours: material.vertexColors}); }); return nodes;
    });
    assert.deepEqual(parts.filter(part => !part.sameGeometry).map(part => part.name).sort(), [...[0,1,2].map(n => `Foundation_Wall_15_LOD${n}`),...['1_2','2_2'].flatMap(tile=>[0,1,2].map(n=>`Foundation_Terrain_${tile}_LOD${n}`))].sort());
    for (const part of parts.filter(part => !part.sameGeometry && part.name.startsWith("Foundation_Wall_"))) { assert.equal(part.albedoShared, true); assert.equal(part.roughnessShared, true); assert.equal(part.normalChannel, part.name.endsWith("LOD0") ? 0 : 1); assert.equal(part.vertexColours, false); }
    const requested = await resources();
    for (const suffix of ["quarry-foundation-refined/foundation-geometry.glb", "quarry-fidelity-correction/fidelity-region.glb", "quarry-fidelity-correction/fidelity-bake.glb"])
      assert.equal(requested.filter(row => row.url.endsWith(suffix)).length, 1);
    assert.ok(!requested.some(row => /licensed-source|coastal_cliff_01_2k|scanned-relief|site-scale-cliff|calibrated-region|recovered-c9-composition/.test(row.url)));
    assert.equal(data.composition.fidelityGeology,true);assert.ok(Math.abs(data.composition.regionLengthMetres-35.55718478296376)<1e-8);
    assert.ok(!parts.some(part=>/^Foundation_Wall_(14|16)_/.test(part.name)));
    const shaders = await page.evaluate(() => window.__shaderLinks.flatMap(({gl, program}) => {
      const p=program.deref();return p&&gl.isProgram(p)?[{linked:gl.getProgramParameter(p,gl.LINK_STATUS),log:gl.getProgramInfoLog(p)}]:[];
    }));
    assert.ok(shaders.length>0 && shaders.every(shader=>shader.linked));
    return {data, parts, requested, shaders};
  });
  await check("Ten C8/C9 cycles plateau; native geometry and shared image IDs are reused", async () => {
    const initial = await active(), samples = [];
    for (let i=0;i<10;i++) {
      await page.evaluate(() => window.__wallPreview.setComposition(false)); await ready(page);
      assert.equal((await info()).composition.enabled, false);
      await page.evaluate(() => window.__wallPreview.setComposition(true)); const next = await active();
      assert.deepEqual(next.material.textures.map(t => t.uuid), initial.material.textures.map(t => t.uuid));
      assert.equal(next.composition.geometryNormal.uuid, initial.composition.geometryNormal.uuid);
      samples.push({cycle:i, data:await details(page)});
    }
    const a=samples[1].data,b=samples.at(-1).data;
    assert.ok(b.stats.textures<=a.stats.textures && b.stats.geometries<=a.stats.geometries);
    assert.ok(b.contexts[0].stats.Program.active<=a.contexts[0].stats.Program.active);
    assert.equal((await page.evaluate(() => window.__bitmapCloses)).duplicate, 0);
    return {initial,samples,resources:await resources()};
  });
  await check("Actual context loss/recovery preserves C9, pose, images and Canvas", async () => {
    const before=await details(page),old=await active(),canvas=await page.evaluateHandle(()=>document.querySelector("canvas"));
    await page.evaluate(()=>{window.__loss=document.querySelector("canvas").getContext("webgl2").getExtension("WEBGL_lose_context");window.__loss.loseContext();});
    await page.waitForSelector('[data-phase="context-lost"]');await page.waitForTimeout(250);
    await page.evaluate(()=>window.__loss.restoreContext()); const next=await active(),after=await details(page);
    assert.equal(await canvas.evaluate(c=>c===document.querySelector("canvas")),true);
    assert.equal(next.composition.geometryNormal.uuid,old.composition.geometryNormal.uuid);
    assert.deepEqual(next.material.textures.map(t=>t.uuid),old.material.textures.map(t=>t.uuid));
    assert.ok(Math.hypot(before.pose.x-after.pose.x,before.pose.y-after.pose.y,before.pose.z-after.pose.z)<1e-6);
    return {before,after,old,next};
  });
  await check("Explicit inactive retirement and reload free only owned C9 resources", async () => {
    const old=await active();await page.evaluate(()=>window.__wallPreview.setMode("off"));await ready(page);
    const disposed=await page.evaluate(()=>{const o=window.__wallPreview;o.retire();return {composition:o.compositionDiagnostics(),trace:o.trace,consumers:o.consumers};});
    assert.equal(disposed.consumers,0);assert.equal(disposed.composition.ready,false);
    assert.ok(disposed.trace.some(e=>e.event==="fidelity-owner-disposal"&&e.geometries===3&&e.images===0));
    assert.ok(disposed.trace.some(e=>e.event==="fidelity-bake-owner-disposal"&&e.images===1));
    await page.evaluate(()=>window.__wallPreview.setComposition(true));const next=await active();
    assert.notEqual(next.composition.geometryNormal.uuid,old.composition.geometryNormal.uuid);
    assert.equal((await page.evaluate(()=>window.__bitmapCloses)).duplicate,0);
    return {old,disposed,next};
  });
  await check("Complete fallback unmount releases local geometry and one bake without double-close", async () => {
    const owner=await page.evaluateHandle(()=>window.__wallPreview);
    await page.getByRole("button",{name:"Use without 3D",exact:true}).click();await page.waitForFunction(()=>!document.querySelector("canvas"));
    const data=await owner.evaluate(o=>({disposed:o.disposed,consumers:o.consumers,composition:o.compositionDiagnostics(),material:!!o.borrowScannedMaterial(),trace:o.trace}));
    assert.equal(data.disposed,true);assert.equal(data.consumers,0);assert.equal(data.composition.ready,false);assert.equal(data.material,false);
    const closes=await page.evaluate(()=>window.__bitmapCloses);assert.equal(closes.duplicate,0);return {data,closes};
  });
  for (const file of ["fidelity-region.glb","fidelity-bake.glb"]) {
    await open();await page.route("**/quarry-fidelity-correction/"+file,route=>route.abort());
    await check(`Failed ${file} retains C8 and retries without another complete quarry download`,async()=>{
      await page.goto(url);await ready(page);const failed=await info();assert.equal(failed.composition.enabled,false);assert.equal(failed.material.enabled,true);assert.match(failed.state.error,/Fidelity geometry unavailable/);
      await page.unroute("**/quarry-fidelity-correction/"+file);await page.evaluate(()=>window.__wallPreview.setComposition(true));const next=await active();
      const requests=await resources();assert.equal(requests.filter(r=>r.url.endsWith("quarry-foundation-refined/foundation-geometry.glb")).length,1);
      assert.equal((await page.evaluate(()=>window.__bitmapCloses)).duplicate,0);return {failed,next,requests};
    });
  }
  await open();const invalid=await readFile("public/models/gullyverse/recovered-c8-material/scanned-materials.glb");
  await page.route("**/quarry-fidelity-correction/fidelity-region.glb",route=>route.fulfill({body:invalid,contentType:"model/gltf-binary"}));
  await check("Invalid local geometry with embedded PBR images is rejected and its own images closed",async()=>{
    await page.goto(url);await ready(page);const data=await info();assert.equal(data.composition.enabled,false);assert.equal(data.material.enabled,true);
    const trace=await page.evaluate(()=>window.__wallPreview.trace);assert.ok(trace.some(e=>e.event==="fidelity-rejected-disposal"&&e.images===3));
    assert.equal((await page.evaluate(()=>window.__bitmapCloses)).duplicate,0);return {data,trace};
  });
  await open();await page.route("**/quarry-fidelity-correction/fidelity-region.glb",async route=>{await new Promise(resolve=>setTimeout(resolve,3500));await route.continue();});
  await check("Delayed local geometry stays covered until both material and local owners are ready",async()=>{
    await page.goto(url);await page.waitForFunction(()=>window.__wallPreview);await page.waitForTimeout(1000);
    const pending=await info();assert.equal(pending.composition.preparing,true);assert.equal(pending.state.busy,true);
    assert.equal(await page.locator('[data-wall-cover]').count(),1);const final=await active();return {pending,final};
  });
  await open();await page.route("**/quarry-fidelity-correction/fidelity-region.glb",async route=>{await new Promise(resolve=>setTimeout(resolve,3000));await route.continue().catch(()=>{});});
  await check("Unmount during delayed local loading drains unpublished resources",async()=>{
    const requested=page.waitForRequest("**/quarry-fidelity-correction/fidelity-region.glb");await page.goto(url);await requested;await page.waitForFunction(()=>window.__wallPreview);const owner=await page.evaluateHandle(()=>window.__wallPreview);
    await page.getByRole("button",{name:"Use without 3D",exact:true}).click();await page.waitForFunction(()=>!document.querySelector("canvas"));await page.waitForTimeout(5000);
    const data=await owner.evaluate(o=>({disposed:o.disposed,consumers:o.consumers,composition:o.compositionDiagnostics(),trace:o.trace}));
    assert.equal(data.disposed,true);assert.equal(data.composition.ready,false);assert.ok(data.trace.some(e=>e.event==="fidelity-abandoned-disposal"||e.event==="fidelity-unpublished-disposal"));
    assert.equal((await page.evaluate(()=>window.__bitmapCloses)).duplicate,0);return data;
  });
  for (const file of ["c9-cave-recovery/cave-entrance.glb","c9-cave-recovery/entry-clearance.glb"]) {
    await open();await page.route("**/"+file,route=>route.abort());
    await check(`Failed local ${file} preserves accepted C9 and retries`,async()=>{
      await page.goto(url);await active();const failed=await page.evaluate(()=>window.__wallPreview.entranceDiagnostics());assert.equal(failed.ready,false);assert.equal(failed.failed,true);
      await page.unroute("**/"+file);await page.getByRole("button",{name:"Retry cave preview",exact:true}).click();await active();await page.waitForFunction(()=>window.__wallPreview.entranceRoot?.deref()?.parent);
      const next=await page.evaluate(()=>window.__wallPreview.entranceDiagnostics());assert.equal(next.ready,true);assert.equal(next.approvedTextureScale,3);
      const requests=await resources();assert.equal(requests.filter(r=>r.url.endsWith("quarry-foundation-refined/foundation-geometry.glb")).length,1);return {failed,next,requests};
    });
  }
  await open();await page.route("**/c9-cave-recovery/cave-entrance.glb",route=>route.fulfill({body:invalid,contentType:"model/gltf-binary"}));
  await check("Unexpected embedded cave textures are rejected and closed without touching shared C8",async()=>{
    await page.goto(url);await active();const data=await page.evaluate(()=>({cave:window.__wallPreview.entranceDiagnostics(),trace:window.__wallPreview.trace}));
    assert.equal(data.cave.ready,false);assert.ok(data.trace.some(e=>e.event==="cave-rejected-disposal"&&e.images===3));assert.equal((await page.evaluate(()=>window.__bitmapCloses)).duplicate,0);return data;
  });
  await open();await page.route("**/c9-cave-recovery/cave-entrance.glb",async route=>{await new Promise(resolve=>setTimeout(resolve,3000));await route.continue().catch(()=>{});});
  await check("Unmount during delayed cave loading drains unpublished geometry",async()=>{
    await page.goto(url);await page.waitForFunction(()=>window.__wallPreview);const owner=await page.evaluateHandle(()=>window.__wallPreview);
    await page.getByRole("button",{name:"Use without 3D",exact:true}).click();await page.waitForFunction(()=>!document.querySelector("canvas"));await page.waitForTimeout(5000);
    const data=await owner.evaluate(o=>({disposed:o.disposed,cave:o.entranceDiagnostics(),trace:o.trace}));assert.equal(data.disposed,true);assert.equal(data.cave.ready,false);assert.ok(data.trace.some(e=>e.event==="cave-abandoned-disposal"));return data;
  });
  await open();
  await check("Ordinary public URL remains C5.1 without C8/C9 assets or controls",async()=>{
    await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics");await ready(page);
    const data=await page.evaluate(()=>({class:window.__wallPreview.constructor.name,composition:!!window.__wallPreview.compositionDiagnostics,material:!!window.__wallPreview.materialDiagnostics}));
    assert.equal(data.composition,false);assert.equal(data.material,false);assert.equal(await page.locator('[data-scanned-composition-controls]').count(),0);
    const requests=await resources();assert.ok(!requests.some(r=>/recovered-c[89]-|quarry-fidelity-correction|c9-cave-recovery|c9-cave-deep-relief/.test(r.url)));return {data,requests};
  });
} finally {await current?.close();await browser.close();}
