import assert from "node:assert/strict";
import {mkdir, writeFile, rename} from "node:fs/promises";
import {launch, context, ready, view, details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";
import {look} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/audit-common.mjs";
const root="reports/stage3a1-deep-rock-2026-10-21",browser=await launch();
await mkdir(root+"/videos",{recursive:true});const states=[],errors=[];let current;
async function record(page,label) {
  await page.waitForFunction(()=>window.__gullyverse?.runtime&&window.__wallPreview);
  const data=await page.evaluate(()=>({cave:window.__wallPreview.entranceDiagnostics(),composition:window.__wallPreview.compositionDiagnostics(),material:window.__wallPreview.materialDiagnostics(),state:window.__gullyverse.runtime.getSnapshot(),pose:{...window.__gullyverse.runtime.pose},url:location.href}));
  assert.equal(data.composition.enabled,true);assert.equal(data.composition.ready,true);assert.equal(data.material.scale,3);assert.equal(data.cave.ready,true);assert.equal(data.cave.visibleFixtures,0);assert.equal(data.cave.approvedTextureScale,3);assert.equal(new URL(data.url).searchParams.get("entranceReview"),"deep-rock");
  states.push({label,...data});console.log(label);
}
async function go(page,id) {
  await page.getByRole("button",{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse?.runtime?.getSnapshot().mapStage==="open");
  await record(page,"map open before "+id);
  await page.getByRole("button",{name:id==="hub"?"Gullyverse hub":"Aftermovie",exact:true}).click();
  await page.waitForFunction(id=>window.__gullyverse?.runtime?.getSnapshot().phase==="local"&&window.__gullyverse.runtime.getSnapshot().scene===id,id,{timeout:90000});await ready(page);
}
try {
  current=await context(browser,{deviceScaleFactor:.5,recordVideo:{dir:root+"/videos/raw",size:{width:1366,height:900}}});
  let page=await current.newPage();const video=page.video();
  await page.goto("http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=deep-rock");
  await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
  await page.waitForSelector('[data-phase="landing"]',{timeout:90000});
  await page.waitForFunction(()=>!window.__wallPreview.state.busy,null,{timeout:90000});
  await page.addStyleTag({content:"[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
  await record(page,"natural entrance ready; accepted C9 owner retained");await page.waitForTimeout(1000);
  await page.getByRole("button",{name:"Enter Gullyverse",exact:true}).click();await ready(page);await record(page,"natural 42m rock-vault journey to C9 hub");
  const canvas=await page.evaluateHandle(()=>document.querySelector("canvas"));
  await view(page,[-18,1.72,-55],[-46,6,-65],{fixed:false,quality:3});await record(page,"public visitor walk start");await page.waitForTimeout(2500);
  // Valid initial public position, then real held-key movement. The existing
  // collision registry alone controls the walk; no per-frame pose assignment.
  await look(page,[-18,1.72,-72]);
  await page.keyboard.down("KeyW");
  await page.waitForFunction(()=>window.__gullyverse.runtime.pose.z<=-62,null,{timeout:45000});
  await page.keyboard.up("KeyW");await look(page,[-44,4,-65]);await record(page,"actual keyboard walk along visitor boundary");await page.waitForTimeout(2000);
  await go(page,"aftermovie");await record(page,"original stage arrival with C9 selected");
  await page.getByRole("button",{name:"Play Aftermovie",exact:true}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.3,null,{timeout:30000});
  await record(page,"original Aftermovie playing");await page.waitForTimeout(2500);
  await page.getByRole("button",{name:"Exit Aftermovie",exact:true}).click();await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().movie);
  await go(page,"hub");await record(page,"return to C9 hub");assert.equal(await canvas.evaluate(c=>c===document.querySelector("canvas")),true);
  await view(page,[-18,1.72,-55],[-46,6,-65],{fixed:false,quality:3});await page.waitForTimeout(2000);await record(page,"selected C9 visible after full journey");
  await current.close();current=null;await rename(await video.path(),root+"/videos/visitor-journey.webm");

  current=await context(browser,{deviceScaleFactor:.5,recordVideo:{dir:root+"/videos/raw",size:{width:1366,height:900}}});page=await current.newPage();const lodVideo=page.video();
  await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=geology-fidelity&entranceReview=deep-rock");await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(page);
  await page.addStyleTag({content:"[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
  await view(page,[0,4,250],[-1,3,0],{fixed:true,quality:0});
  await page.evaluate(()=>{
    const r=window.__gullyverse.runtime,base=r.cameraPose(innerWidth/innerHeight),start=performance.now();
    const stops=[[0,4,250],[0,3,80],[0,1.72,12],[-1.65,1.72,-6],[-3.72,1.72,-11.2],[0,3,80],[0,4,250]],target=[-7.72,2.35,-11.2];
    r.cameraPose=()=>{const f=Math.min(5.999999,(performance.now()-start)/5000),i=Math.floor(f),t=f-i,a=stops[i],b=stops[i+1];
      const p=a.map((v,k)=>v+(b[k]-v)*t),dx=target[0]-p[0],dy=target[1]-p[1],dz=target[2]-p[2];
      return {...base,x:p[0],y:p[1],z:p[2],yaw:Math.atan2(-dx,-dz),pitch:Math.atan2(dy,Math.hypot(dx,dz))};};
  });
  const samples=[];
  for(let i=0;i<30;i++){await page.waitForTimeout(1000);samples.push({index:i,data:await details(page),composition:await page.evaluate(()=>window.__wallPreview.compositionDiagnostics())});}
  const selected=new Set(samples.map(s=>s.data.wall.lodSelections.Cave_Passage1));assert.ok([0,1,2].every(level=>selected.has(level)));
  await current.close();current=null;await rename(await lodVideo.path(),root+"/videos/automatic-lod-inspection.webm");
  await writeFile(root+"/raw/automatic-lod-walk.json",JSON.stringify({status:"PASS",samples,nonPublicInspection:true,automaticLODSelection:true,physicsOrNavigationChanged:false},null,2));
}catch(error){errors.push(String(error.stack));process.exitCode=1;}
finally {await current?.close();await browser.close();await writeFile(root+"/raw/browser-walkthrough.json",JSON.stringify({status:errors.length?"FAIL":"PASS",states,errors,method:"Actual browser recording. Public walk starts at a validated pose, uses real pointer look and held W keys, then actual map, original playback and return controls. Separate inspection is explicitly non-public with automatic screen-space LOD selection. SwiftShader footage, no retiming.",physicalHardware:false},null,2));}
