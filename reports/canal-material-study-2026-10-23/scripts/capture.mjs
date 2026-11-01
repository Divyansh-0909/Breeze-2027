import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {launch,context,view,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const R='reports/canal-material-study-2026-10-23';
const manifest=JSON.parse(await readFile('public/models/gullyverse/canal-material-study/materials.json','utf8'));
const browser=await launch(),ctx=await context(browser,{viewport:{width:1366,height:900},deviceScaleFactor:1}),page=await ctx.newPage(),cdp=await ctx.newCDPSession(page);
const previous=JSON.parse(await readFile(R+'/raw/captures.json','utf8').catch(()=>'{"shots":[],"assets":[],"performanceRows":[]}'));
const shots=previous.shots??[],errors=[],assets=previous.assets??[],performanceRows=previous.performanceRows??[];
const geometrySessions=previous.geometrySessions??(previous.geometry?[{id:1,geometry:previous.geometry}]:[]);
shots.forEach(s=>{s.captureSessionId??=1;});
let current='control',scale=1,baselineGeometry,sessionId;
const poses=[
 ['landing',[0,1.72,11.5],[0,1.72+Math.tan(.15)*11.5,0],'Actual approved landing pose, locked for comparison'],
 ['left-wall',[-3.15,1.72,-10],[-7.2,2.5,-11],'Protected centerline inspection, visitor eye height'],
 ['right-wall',[-3.15,1.72,-10],[.7,2.5,-11],'Protected centerline inspection, visitor eye height'],
 ['vault',[-4.575,1.72,-13],[-5.8,7,-17],'Protected centerline upward inspection'],
 ['walking-depth',[-6,1.72,-20],[-3,2,-33],'Protected centerline walking-depth inspection'],
 ['close-wall',[-5.32,1.72,-11.2],[-8.1,2.4,-14],'Lateral close inspection; diagnostic, not free public camera'],
];
page.on('pageerror',e=>errors.push(String(e.stack)));
const pending=[];page.on('response',r=>{if(/c9-cave-recovery\/cave-entrance.glb$/.test(r.url()))pending.push(r.body().then(b=>assets.push({url:r.url(),bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')})));});
const geometry=()=>page.evaluate(()=>{const root=window.__wallPreview.entranceRoot?.deref();const rows=[];root?.traverse(o=>{if(o.isMesh)rows.push({name:o.name,geometryUUID:o.geometry.uuid,positionCount:o.geometry.attributes.position.count,triangles:o.geometry.index.count/3});});return rows.sort((a,b)=>a.name.localeCompare(b.name));});
async function settle(){await page.waitForFunction(()=>{const s=window.__wallPreview;return s?.studyDiagnostics?.().ready&&!s.state.busy&&s.entranceRoot?.deref()?.parent;},null,{timeout:90000});}
async function save(id,p,t,extra={}){
 if(shots.some(s=>s.material===current&&s.scale===scale&&s.id===id))return;
 await view(page,p,t,{fixed:true,quality:0});await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 const file=`screenshots/${current}-${scale}x-${id}.png`;const png=await cdp.send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});await writeFile(R+'/'+file,Buffer.from(png.data,'base64'));
 const d=await page.evaluate(()=>{
  const s=window.__wallPreview,r=window.__gullyverse.runtime,v=r.cameraPose(innerWidth/innerHeight),geo=[];let scene=s.entranceRoot.deref();scene.traverse(o=>{if(o.isMesh)geo.push({name:o.name,geometryUUID:o.geometry.uuid,positionCount:o.geometry.attributes.position.count,triangles:o.geometry.index.count/3});});while(scene.parent)scene=scene.parent;const lights=[];scene.traverse(o=>{if(o.isLight)lights.push({type:o.type,colour:o.color?.getHexString(),intensity:o.intensity,visible:o.visible,position:o.position.toArray()});});
  return{geometry:geo.sort((a,b)=>a.name.localeCompare(b.name)),study:s.studyDiagnostics(),camera:{...v,near:.1,far:700,quaternion:[Math.sin(v.pitch/2)*Math.cos(v.yaw/2),Math.cos(v.pitch/2)*Math.sin(v.yaw/2),-Math.sin(v.pitch/2)*Math.sin(v.yaw/2),Math.cos(v.pitch/2)*Math.cos(v.yaw/2)]},viewport:{width:innerWidth,height:innerHeight,requestedDpr:devicePixelRatio},lighting:{lights},stats:window.__gullyverse.stats,renderer:window.__gullyverse.renderer,snapshot:r.getSnapshot(),contexts:window.__audit.contexts.map(c=>({renderer:c.renderer,stats:c.stats})),revealOpacity:r.revealOpacity};
 });const geo=d.geometry,study=d.study;assert.deepEqual(geo,baselineGeometry,'Material-only geometry changed');assert.equal(d.revealOpacity,0);assert.equal(study.error,null);assert.equal(study.active,current);assert.equal(study.quarrySamplerScale,3);assert.equal(study.geometryMode,'baseline');assert.equal(d.stats.dpr,1);assert.equal(d.snapshot.quality,0);
 const {camera,viewport,lighting,stats,renderer,snapshot,contexts}=d;
 shots.push({number:shots.length+1,file,id,material:current,scale,condition:'Approved dusk, no light/exposure/fog changes',position:p,target:t,...extra,camera,viewport,lighting,stats,renderer,snapshot,contexts:contexts.map(x=>({renderer:x.renderer,stats:x.stats})),study,geometryUnchanged:true,captureSessionId:sessionId});
 console.log(file);await writeFile(R+'/raw/captures.json',JSON.stringify({status:'RUNNING',shots,errors,assets,geometry:baselineGeometry,geometrySessions,performanceRows},null,2));
}
try{
 await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=canal-material&caveMaterial=control');
 await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await page.waitForSelector('[data-phase="landing"]',{timeout:90000});await settle();baselineGeometry=await geometry();assert.ok(baselineGeometry.length>0);
 if(previous.geometry){const shape=rows=>rows.map(({geometryUUID,...r})=>r);assert.deepEqual(shape(baselineGeometry),shape(previous.geometry));}
 sessionId=geometrySessions.length+1;geometrySessions.push({id:sessionId,geometry:baselineGeometry,build:(await readFile('.next/BUILD_ID','utf8')).trim()});
 await page.addStyleTag({content:'[data-quarry-controls],[data-canal-controls],aside[class*=inspection]{visibility:hidden!important}'});
 const finalists=['cracked_concrete_wall','plastered_stone_wall','scuffed_cement','chipped_concrete','concrete_wall_006','concrete_wall_008'];
 for(current of ['control',...manifest.materials.map(m=>m.id)])for(scale of finalists.includes(current)?[1,2]:[1]){
  if(shots.filter(s=>s.material===current&&s.scale===scale).length===8&&(scale===2||performanceRows.some(p=>p.material===current&&p.scale===scale)))continue;
  await page.evaluate(({id,scale})=>{window.__gullyverse.runtime.setQuality(3);window.__wallPreview.setStudySelection(id,scale);},{id:current,scale});await settle();
  await page.setViewportSize({width:1366,height:900});
  for(const[id,p,t,label]of poses)await save(id,p,t,{cameraClassification:label,mobileAspect:false});
  await page.setViewportSize({width:390,height:844});
  await save('mobile-landing',poses[0][1],poses[0][2],{mobileAspect:true,cameraClassification:'Approved landing pose, mobile aspect; not physical phone'});
  await save('mobile-tunnel',poses[4][1],poses[4][2],{mobileAspect:true,cameraClassification:'Protected centerline walking-depth inspection, mobile aspect'});
  await page.setViewportSize({width:1366,height:900});await view(page,poses[4][1],poses[4][2],{fixed:true,quality:0});
  if(scale===1&&!performanceRows.some(p=>p.material===current&&p.scale===scale)){const perf=await page.evaluate(async()=>{let t=performance.now(),frames=[];for(let i=0;i<32;i++){await new Promise(requestAnimationFrame);const n=performance.now();frames.push(n-t);t=n;}frames.sort((a,b)=>a-b);const q=p=>frames[Math.min(frames.length-1,Math.ceil(frames.length*p)-1)];return {frames:frames.length,p50:q(.5),p95:q(.95),p99:q(.99),fps:1000/(frames.reduce((a,b)=>a+b)/frames.length),stats:window.__gullyverse.stats,renderer:window.__gullyverse.renderer,memory:window.__gullyverse.memory.at(-1)};});performanceRows.push({material:current,scale,...perf,physicalHardware:false,settings:'1366x900 DPR1 quality0, identical walking-depth pose, 32 RAF intervals, unthrottled SwiftShader software diagnostic'});}
 }
 await Promise.all(pending);const pairs=[];
 for(const shot of shots){const control=shots.find(s=>s.material==='control'&&s.id===shot.id);for(const n of ['x','y','z','yaw','pitch','fov','near','far'])assert.ok(Number.isFinite(shot.camera[n]),n);for(const key of ['camera','viewport','lighting'])assert.deepEqual(JSON.parse(JSON.stringify(shot[key])),JSON.parse(JSON.stringify(control[key])),key);assert.equal(shot.snapshot.quality,control.snapshot.quality);pairs.push({material:shot.material,scale:shot.scale,id:shot.id,matched:true});}
 await writeFile(R+'/raw/matched-settings.json',JSON.stringify({status:'PASS',pairs},null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await ctx.close();await browser.close();await writeFile(R+'/raw/captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,errors,assets,geometry:baselineGeometry,geometrySessions,performanceRows,physicalHardware:false,captureMethod:'Lossless CDP actual compositor PNG after two animation-frame fences at each fixed camera. No offline render/upscale.'},null,2));}
