/** Fixed authoring cameras, separate from live movement/performance measurement. */
import assert from "node:assert/strict";
import { mkdir,readFile,writeFile } from "node:fs/promises";
import { chromium } from "playwright";
const base = process.env.GULLYVERSE_BASE_URL ?? "http://localhost:3000";
const dir = ".gullyverse-artifacts/stage-1";
const world = JSON.parse(await readFile(new URL("../public/models/gullyverse/blockout.layout.json",import.meta.url),"utf8"));
await mkdir(dir,{recursive:true});
const browser = await chromium.launch({executablePath:process.env.CHROME_PATH ?? "C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
const captures = [], errors = [];
try {
  for (const profile of ["desktop","mobile-aspect"]) {
    const viewport = profile==="desktop" ? {width:1366,height:768} : {width:390,height:844};
    const context = await browser.newContext({viewport,deviceScaleFactor:1});
    const page = await context.newPage();
    page.on("pageerror",(e)=>errors.push(e.message));
    await page.goto(base+"/?diagnostics",{waitUntil:"domcontentloaded"});
    await page.waitForSelector('[data-phase="landing"]',{timeout:60000});
    await page.waitForTimeout(700);
    await page.screenshot({path:dir+"/"+profile+"-landing-with-ui.png"});
    const cameras = profile==="desktop" ? world.cameras : world.cameras.filter((c)=>["landing","exit","quarry","overview"].includes(c.id));
    for (const camera of cameras) {
      assert.equal(await page.evaluate((id)=>window.__gullyverse.runtime.inspect(id),camera.id),true,"Build with NEXT_PUBLIC_GULLYVERSE_INSPECTION=1 for local authoring captures");
      await page.waitForTimeout(350);
      const file = profile+"-"+camera.id+".png";
      await page.screenshot({path:dir+"/"+file});
      const evidence = await page.evaluate(()=>({renderer:window.__gullyverse.renderer,stats:window.__gullyverse.stats,pose:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),savedWalkingPose:{...window.__gullyverse.runtime.pose},canvasCount:document.querySelectorAll("canvas").length}));
      captures.push({profile,viewport,camera,file,...evidence});
    }
    await context.close();
  }
  assert.deepEqual(errors,[]);
  await writeFile(dir+"/captures.json",JSON.stringify({captures,errors},null,2));
  const reference = {
    landing:"01-entrance/irregular-rock-opening.jpeg",
    "tunnel-near":"02-rocky-graffiti-tunnel/tunnel-wall-graffiti-1.jpeg",
    "tunnel-mid":"02-rocky-graffiti-tunnel/natural-rock-exit-graffiti.jpeg",
    exit:"04-exit-wayfinding/scaffold-sign-and-stage-composition.jpeg",
    scaffold:"04-exit-wayfinding/scaffold-hero-sign-closeup.jpeg",
    quarry:"03-open-roof-quarry/quarry-open-sky-geometry.jpeg",
    "left-stalls":"05-left-right-stalls/festival-stall-lane.jpeg",
    "right-stalls":"05-left-right-stalls/tent-vendor-clusters.jpeg",
    overview:"08-aerial-map/aerial-map-markers-layout.jpeg",
    "stage-return":"baselines/original-website/04-original-stage-distant.png"
  };
  const before = {landing:"01-landing.png","tunnel-near":"02-tunnel.png","tunnel-mid":"02-tunnel.png",exit:"03-hub.png",scaffold:"03-hub.png",quarry:"03-hub.png","stage-return":"04-stage-distance.png"};
  const cards = captures.map((c)=>'<article><h2>'+c.profile+' / '+c.camera.id+'</h2><p>Camera '+JSON.stringify(c.camera.position)+' → '+JSON.stringify(c.camera.target)+'; vertical FOV '+c.camera.fov+'°. Reference poses are inferred; this is a spatial blockout, awaiting review.</p><div class="grid">'+
    (before[c.camera.id]?'<figure><img src="../../design/references/baselines/current-implementation/'+before[c.camera.id]+'"><figcaption>Before: supplied current implementation baseline (different camera/layout)</figcaption></figure>':'')+
    '<figure><img src="../../design/references/'+reference[c.camera.id]+'"><figcaption>Direction / functional reference; no reference pixels used in the environment</figcaption></figure>'+
    '<figure><a href="'+c.file+'"><img src="'+c.file+'"></a><figcaption>Stage 1 rendered shared world. '+c.viewport.width+' × '+c.viewport.height+'</figcaption></figure></div></article>').join("");
  await writeFile(dir+"/review.html",'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse Stage 1 spatial review</title><style>body{font:15px/1.55 system-ui;background:#1d241f;color:#eee6d4;margin:32px}h1{font-size:32px}article{border-top:1px solid #626759;padding:24px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}figure{margin:0}img{width:100%;max-height:640px;object-fit:contain;background:#131714}figcaption{font-size:12px;color:#c2b8a1;margin:8px 0}a{color:#e6c58d}</style><h1>BREEZE 2027 / GULLYVERSE — Stage 1</h1><p>Review quarry proportions, portal and tunnel clearance, scaffold framing and stage distance before Stage 2. All captures show the same persistent 3D world. Authoring labels are inspection only. The map reference illustrates future behavior; Stage 1 implements no cinematic map.</p><p><a href="captures.json">Camera and renderer evidence</a> · <a href="results.json">Production regression/performance results</a></p>'+cards+'</html>');
  console.log(JSON.stringify({captures:captures.length,errors,review:dir+"/review.html"}));
} finally {await browser.close();}
