/** Revision 2 review cameras and public map/edge UI; separate from performance. */
import assert from "node:assert/strict";
import { mkdir,readFile,writeFile,unlink } from "node:fs/promises";
import { chromium } from "playwright";
const base=process.env.GULLYVERSE_BASE_URL ?? "http://localhost:3000";
const dir=".gullyverse-artifacts/stage-1-revision-2";
const world=JSON.parse(await readFile(new URL("../public/models/gullyverse/blockout.layout.json",import.meta.url),"utf8"));
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH ?? "C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
const captures=[],errors=[],mutations=[];
const waitLocal=(p,id)=>p.waitForSelector(`[data-phase="local"][data-location="${id}"]`,{timeout:60000});
const desktopViews=["landing","tunnel-near","tunnel-mid","tunnel-first-exit-reveal","exit","scaffold-front","scaffold-diagonal","quarry","left-stalls","right-stalls","overview","stage-front","stage-return"];
const mobileViews=[['landing','landing'],['tunnel','tunnel-mid'],['exit','exit'],['scaffold','scaffold-front'],['quarry','quarry']];
async function capture(page,profile,id,camera=null,note="") {
  if(camera) await page.locator('[data-inspection] > aside').evaluate(el=>{el.style.visibility="hidden";});
  const evidence=()=>page.evaluate(()=>({renderer:window.__gullyverse.renderer,stats:{...window.__gullyverse.stats},pose:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),savedWalkingPose:{...window.__gullyverse.runtime.pose},snapshot:window.__gullyverse.runtime.getSnapshot(),mapProgress:window.__gullyverse.runtime.mapProgress,canvasCount:document.querySelectorAll("canvas").length}));
  const before=await evidence(),file=profile+"-"+id+".png";
  await page.screenshot({path:dir+"/"+file});
  const after=await evidence();
  captures.push({profile,viewport:page.viewportSize(),id,camera,file,note,...before,afterReadback:{pose:after.pose,mapProgress:after.mapProgress,mapStage:after.snapshot.mapStage}});
}
async function closeMap(page) {await page.keyboard.press("Escape");await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().map,{timeout:10000});}
try {
  for (const profile of ["desktop","mobile"]) {
    const viewport=profile==="desktop"?{width:1366,height:768}:{width:390,height:844};
    const context=await browser.newContext({viewport,deviceScaleFactor:1,hasTouch:profile==="mobile"});
    const page=await context.newPage();
    page.on("pageerror",e=>errors.push(e.message));
    await page.route("**/api/**",route=>{
      if(!["GET","HEAD"].includes(route.request().method())){mutations.push(route.request().url());return route.abort();}
      return route.continue();
    });
    await page.goto(base+"/?diagnostics",{waitUntil:"domcontentloaded"});
    await page.waitForSelector('[data-phase="landing"]',{timeout:60000});
    const views=profile==="desktop"?desktopViews.map(id=>[id,id]):mobileViews;
    for(const [name,id] of views) {
      if(id==="stage-front") {
        await page.evaluate(()=>window.__gullyverse.runtime.inspect(null));
        await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
      }
      const camera=world.cameras.find(c=>c.id===id);assert.ok(camera,"Missing registry authoring camera "+id);
      assert.equal(await page.evaluate(id=>window.__gullyverse.runtime.inspect(id),id),true,"Use local authoring preview NEXT_PUBLIC_GULLYVERSE_INSPECTION=1");
      await page.waitForTimeout(400);
      await capture(page,profile,name,camera,"Fixed review camera; visitor pose retained. New compositions intentionally differ from prior Stage 1.");
    }
    await page.evaluate(()=>window.__gullyverse.runtime.inspect(null));
    await page.goto(base+"/?diagnostics",{waitUntil:"domcontentloaded"});
    await page.waitForSelector('[data-phase="landing"]',{timeout:60000});
    await page.getByRole("button",{name:"Enter Gullyverse",exact:true}).click();await waitLocal(page,"hub");
    // Each moment replays the same continuous rise from the same unchanged visitor pose.
    // Readback can advance animation; captures.json records camera both sides of it.
    for(const [moment,progress] of [["early",.18],["middle",.5],["late",.82]]) {
      await page.keyboard.press("KeyM");
      await page.waitForFunction(p=>window.__gullyverse.runtime.mapProgress>=p,progress,{timeout:10000});
      await capture(page,profile,"map-ascent-"+moment,null,"Public M control; separate repeat of the same rise, not a teleported camera.");
      await closeMap(page);
    }
    await page.getByRole("button",{name:/^Map/}).click();
    await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open",{timeout:10000});
    await page.getByRole("region",{name:"Festival aerial map"}).waitFor();await page.waitForTimeout(250);
    await capture(page,profile,profile==="desktop"?"map-with-markers":"map",null,"Public fullscreen same-world map with aligned destination markers.");
    await closeMap(page);
    await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
    await page.keyboard.down("KeyS");
    await page.getByRole("dialog",{name:"Where to next?"}).waitFor({timeout:10000});await page.keyboard.up("KeyS");
    await page.waitForTimeout(500);await capture(page,profile,"aftermovie-boundary-menu",null,"Actual rear-boundary contact through public walking controls; no automatic navigation.");
    await context.close();
  }
  assert.deepEqual(errors,[]);assert.deepEqual(mutations,[]);
  await writeFile(dir+"/captures.json",JSON.stringify({capturedAt:new Date().toISOString(),mode:"local production authoring preview; no physical mobile certification",captures,errors,mutations},null,2));
  const refs={landing:"01-entrance/irregular-rock-opening.jpeg","tunnel-near":"02-rocky-graffiti-tunnel/tunnel-wall-graffiti-1.jpeg","tunnel-mid":"02-rocky-graffiti-tunnel/natural-rock-exit-graffiti.jpeg",tunnel:"02-rocky-graffiti-tunnel/tunnel-wall-graffiti-1.jpeg","tunnel-first-exit-reveal":"02-rocky-graffiti-tunnel/natural-rock-exit-graffiti.jpeg",exit:"04-exit-wayfinding/scaffold-sign-and-stage-composition.jpeg","scaffold-front":"04-exit-wayfinding/scaffold-hero-sign-closeup.jpeg",scaffold:"04-exit-wayfinding/scaffold-hero-sign-closeup.jpeg","scaffold-diagonal":"04-exit-wayfinding/scaffold-sign-and-stage-composition.jpeg",quarry:"03-open-roof-quarry/quarry-open-sky-geometry.jpeg","left-stalls":"05-left-right-stalls/festival-stall-lane.jpeg","right-stalls":"05-left-right-stalls/tent-vendor-clusters.jpeg",overview:"08-aerial-map/aerial-map-markers-layout.jpeg","stage-front":"baselines/original-website/05-original-stage-near.png","stage-return":"09-aftermovie/stage-offset-and-wayfinding.jpeg","aftermovie-boundary-menu":"baselines/original-website/03-original-menu.png","map-with-markers":"08-aerial-map/aerial-map-markers-layout.jpeg",map:"08-aerial-map/aerial-map-markers-layout.jpeg"};
  const oldIds={tunnel:"tunnel-mid","tunnel-first-exit-reveal":"tunnel-mid","scaffold-front":"scaffold","scaffold-diagonal":"scaffold",scaffold:"scaffold","stage-front":"aftermovie","aftermovie-boundary-menu":"aftermovie","map-with-markers":"overview",map:"overview"};
  const esc=s=>String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll('"',"&quot;");
  const cards=captures.map(c=>{
    const oldId=c.id.startsWith("map-ascent-")?"overview":oldIds[c.id]??c.id,oldProfile=c.profile==="mobile"?"mobile-aspect":"desktop";
    const prior=["landing","exit","quarry","overview"].includes(oldId)||c.profile==="desktop"?`../stage-1/${oldProfile}-${oldId}.png`:c.id==="tunnel"?"../stage-1/mobile-emulated-tunnel-blockout.png":c.id==="scaffold"?"../stage-1/mobile-emulated-hub.png":"../stage-1/mobile-emulated-aftermovie.png";
    const transition=c.id.startsWith("map-ascent-");const ref=refs[c.id]??"08-aerial-map/gta-camera-rise-transition.jpeg";
    return `<article><h2>${esc(c.profile)} / ${esc(c.id)}</h2><p>Rendered camera ${esc(JSON.stringify(c.pose))}; ${c.viewport.width} × ${c.viewport.height}. ${esc(c.note)} ${transition?"Map progress "+Number(c.mapProgress).toFixed(3):""}</p><div class="grid"><figure><a href="${prior}"><img src="${prior}"></a><figcaption>Previous Stage 1. ${["scaffold-front","scaffold-diagonal","landing","tunnel-near","tunnel-mid","tunnel-first-exit-reveal","tunnel","scaffold","overview","map","map-with-markers"].includes(c.id)?"Camera/geometry changed intentionally; this is composition comparison, not pixel-aligned measurement.":"Nearest available previous view; the prior implementation had no aerial ascent or perimeter typography menu."}</figcaption></figure><figure><img src="../../design/references/${ref}"><figcaption>Relevant reference direction. Reference photograph pixels are not runtime textures. Original menu only documents prior navigation/content.</figcaption></figure><figure><a href="${c.file}"><img src="${c.file}"></a><figcaption>Revision 2 actual browser capture. Blockout assets remain subject to human visual review.</figcaption></figure></div></article>`;
  }).join("");
  await writeFile(dir+"/review.html",`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse Stage 1 Revision 2 review</title><style>body{font:15px/1.55 system-ui;background:#151a24;color:#ece4d5;margin:28px}h1{font-size:30px}article{border-top:1px solid #49505d;padding:24px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}figure{margin:0}img{width:100%;max-height:670px;object-fit:contain;background:#090c12}figcaption{font-size:12px;color:#c7bca8;margin:8px 0}a{color:#efc678}</style><h1>BREEZE 2027 / GULLYVERSE — Stage 1 Revision 2</h1><p>15 desktop and 7 portrait review views, plus 6 actual camera-ascent moments. New landing/tunnel/scaffold/overhead compositions intentionally revise rejected Stage 1 framing. This is a blockout correction, not final photorealistic art or user visual approval. Portrait screenshots use the same desktop Intel GPU.</p><p><a href="captures.json">Actual camera / renderer metadata</a> · <a href="results.json">Separate live performance journey</a> · <a href="browser-checks.json">Public-control interaction evidence</a></p>${cards}</html>`);
  console.log(JSON.stringify({captures:captures.length,requiredViews:22,ascentMoments:6,errors,mutations,review:dir+"/review.html"}));
  await unlink(dir+"/capture-failure.txt").catch(error=>{if(error.code!=="ENOENT")throw error;});
} catch(error) {await writeFile(dir+"/capture-failure.txt",String(error.stack??error));throw error;}
finally {await browser.close();}
