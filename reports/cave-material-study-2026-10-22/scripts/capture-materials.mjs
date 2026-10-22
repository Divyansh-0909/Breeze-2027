import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {launch,context,view,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const R='reports/cave-material-study-2026-10-22', manifest=JSON.parse(await readFile('public/models/gullyverse/cave-material-study/materials.json','utf8'));
const browser=await launch(),ctx=await context(browser,{viewport:{width:1366,height:900},deviceScaleFactor:1}),page=await ctx.newPage();
const shots=[],errors=[],assets=[],baselineGeometry=[];let current='control',scale=1;
const poses=[
 ['entrance-front',[0,1.72,11.5],[0,3.5,0],'Existing landing camera inspection'],
 ['wall-left',[-3.15,1.72,-10],[-7.2,2.5,-11],'Protected tunnel-route inspection'],
 ['wall-right',[-3.15,1.72,-10],[.7,2.5,-11],'Protected tunnel-route inspection'],
 ['mid-tunnel',[-6,1.72,-20],[-9.2,2.5,-23],'Protected tunnel-route inspection'],
 ['oblique-close',[-5.32,1.72,-11.2],[-8.1,2.4,-14],'Lateral inspection, not a free public hub camera'],
];
page.on('pageerror',e=>errors.push(String(e.stack)));
const bodies=[];page.on('response',r=>{if(/c9-cave-recovery\/cave-entrance.glb$|cave-material-study\/emboss-pilot.glb$/.test(r.url()))bodies.push(r.body().then(b=>assets.push({url:r.url(),bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')})));});
const geometry=()=>page.evaluate(()=>{const root=window.__wallPreview.entranceRoot?.deref();return root?(()=>{const rows=[];root.traverse(o=>{if(o.isMesh)rows.push({name:o.name,geometryUUID:o.geometry.uuid,positionCount:o.geometry.attributes.position.count,triangles:o.geometry.index.count/3});});return rows.sort((a,b)=>a.name.localeCompare(b.name));})():[];});
async function settle(){await page.waitForFunction(()=>{const s=window.__wallPreview;return s?.studyDiagnostics?.().ready&&!s.state.busy&&s.entranceRoot?.deref()?.parent;},null,{timeout:90000});}
async function save(id,p,t,extra={}){
 await view(page,p,t,{fixed:true,quality:0});await page.waitForTimeout(450);
 await page.waitForFunction(()=>window.__gullyverse.runtime.revealOpacity===0,null,{timeout:10000});
 const file=`screenshots/materials/${current}-${scale}x-${id}.png`;await page.screenshot({path:R+'/'+file});
 const data=await details(page),geo=await geometry();assert.deepEqual(geo,baselineGeometry,'Material-only geometry owner changed');
 const row={file,id,material:current,scale,condition:'Approved dusk, unchanged global lighting',position:p,target:t,...extra,data,study:await page.evaluate(()=>window.__wallPreview.studyDiagnostics()),geometry:geo};
 assert.equal(data.viewport.requestedDpr,1);assert.equal(data.stats.dpr,1);assert.equal(row.study.quarrySamplerScale,3);assert.equal(row.study.geometryMode,'baseline');
 shots.push(row);console.log(file);await writeFile(R+'/raw/material-captures.json',JSON.stringify({status:'RUNNING',shots,errors,assets},null,2));
}
try{
 await mkdir(R+'/screenshots/materials',{recursive:true});
 await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=control');
 await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await page.waitForSelector('[data-phase="landing"]',{timeout:90000});await settle();baselineGeometry.push(...await geometry());assert.ok(baselineGeometry.length>0);
 await page.addStyleTag({content:'[data-quarry-controls],[data-cave-study-controls],aside[class*=inspection]{visibility:hidden!important}'});
 for(current of ['control',...manifest.materials.map(m=>m.id)])for(scale of [1,2]){
  await page.evaluate(({id,scale})=>{window.__gullyverse.runtime.setQuality(3);window.__wallPreview.setStudySelection(id,scale);},{id:current,scale});await settle();
  await page.setViewportSize({width:1366,height:900});
  for(const[id,p,t,label]of poses)await save(id,p,t,{cameraClassification:label,mobileAspect:false});
  await page.setViewportSize({width:390,height:844});
  await save('mobile-entrance',poses[0][1],poses[0][2],{mobileAspect:true,cameraClassification:'Landing camera, mobile aspect only; not physical phone'});
  await save('mobile-mid',poses[3][1],poses[3][2],{mobileAspect:true,cameraClassification:'Protected route inspection, mobile aspect only'});
 }
 await Promise.all(bodies);
 const pairs=[];for(const shot of shots){const control=shots.find(s=>s.material==='control'&&s.scale===shot.scale&&s.id===shot.id);assert.deepEqual(shot.data.camera,control.data.camera);assert.deepEqual(shot.data.viewport,control.data.viewport);assert.deepEqual(shot.data.lighting,control.data.lighting);assert.equal(shot.data.snapshot.quality,control.data.snapshot.quality);pairs.push({material:shot.material,scale:shot.scale,id:shot.id,matchedPoseFovDPRQualityLightsAndGeometry:true});}
 await writeFile(R+'/raw/material-matched-pose-checks.json',JSON.stringify({status:'PASS',pairs},null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await ctx.close();await browser.close();await writeFile(R+'/raw/material-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,errors,assets,physicalHardware:false,geometryMode:'UNCHANGED baseline cave, no failed historical pilot',renderSettings:'1366x900 /390x844, actual DPR1, quality0 for final stills; tier3 preparation labelled diagnostics, not default cold-start acceptance'},null,2));}
