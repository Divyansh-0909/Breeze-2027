import {launch,context,view,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const R='reports/cave-material-study-2026-10-22',browser=await launch(),ctx=await context(browser,{viewport:{width:1366,height:900},deviceScaleFactor:1}),p=await ctx.newPage(),shots=[],errors=[];
const poses=[['walking',[-6,1.72,-18.2],[-9.3,2.6,-21]],['side',[-6,1.72,-20],[-9.4,2.1,-20.8]],['along',[-7.6,1.72,-17.5],[-9.2,2.5,-23]],['parallax-a',[-6,1.72,-19.1],[-9.2,2.4,-20.5]],['parallax-b',[-6,1.72,-21.6],[-9.2,2.4,-20.5]],['upper',[-6,1.72,-20],[-8.6,4.3,-21]],['foot',[-6,1.72,-20],[-9.1,.35,-20]],['join-left',[-6,1.72,-15.4],[-9.1,2.5,-17]],['join-right',[-6,1.72,-23.7],[-9.1,2.5,-22.5]]];
p.on('pageerror',e=>errors.push(String(e.stack)));
async function ready(){await p.waitForFunction(()=>{const s=window.__wallPreview;return s?.studyDiagnostics().ready&&!s.state.busy&&s.entranceRoot?.deref()?.parent;},null,{timeout:90000});}
async function neutral(on,wire=false){await p.evaluate(({on,wire})=>{
 if(on){const root=window.__wallPreview.entranceRoot.deref();let scene=root;while(scene.parent)scene=scene.parent;window.__studyOldLights=[];window.__studyOldMats=[];window.__studyDebugMats=[];
 scene.traverse(o=>{if(o.isLight){window.__studyOldLights.push([o,o.visible]);o.visible=false;}});
 root.traverse(o=>{if(!o.isMesh)return;const m=o.material.clone();for(const key of ['map','normalMap','roughnessMap','metalnessMap','aoMap'])m[key]=null;m.vertexColors=false;m.color.set('#858585');m.roughness=1;m.metalness=0;m.onBeforeCompile=()=>{};m.customProgramCacheKey=()=>wire?'cave-study-wire':'cave-study-clay';m.wireframe=wire;window.__studyOldMats.push([o,o.material]);window.__studyDebugMats.push(m);o.material=m;});
 const h=window.__studyOldLights.find(([l])=>l.isHemisphereLight)[0].clone(),d=window.__studyOldLights.find(([l])=>l.isDirectionalLight)[0].clone();h.visible=true;h.color.set('#ffffff');h.groundColor.set('#858b95');h.intensity=.8;d.visible=true;d.color.set('#ffffff');d.intensity=3;d.position.set(-2,7,-17);scene.add(h,d);window.__studyDebugLights=[h,d];
 }else{window.__studyOldMats.forEach(([o,m])=>o.material=m);window.__studyDebugMats.forEach(m=>m.dispose());window.__studyDebugLights.forEach(l=>l.removeFromParent());window.__studyOldLights.forEach(([l,v])=>l.visible=v);}
},{on,wire});}
async function save(id,pose,material,geometry,condition,mobile=false){await view(p,pose[1],pose[2],{fixed:true,quality:0});await p.waitForTimeout(450);await p.waitForFunction(()=>window.__gullyverse.runtime.revealOpacity===0,null,{timeout:10000});const file=`screenshots/pilot/${geometry}-${material}-${condition}-${mobile?'mobile-':''}${id}.png`;await p.screenshot({path:R+'/'+file});shots.push({file,id,material,geometry,condition,mobileAspect:mobile,position:pose[1],target:pose[2],cameraClassification:'Protected route inspection; not free public hub camera',data:await details(p),study:await p.evaluate(()=>window.__wallPreview.studyDiagnostics())});console.log(file);await writeFile(R+'/raw/pilot-captures.json',JSON.stringify({status:'RUNNING',shots,errors},null,2));}
try{
 await mkdir(R+'/screenshots/pilot',{recursive:true});await p.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=material-study');await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await p.waitForSelector('[data-phase="landing"]',{timeout:90000});await ready();await p.addStyleTag({content:'[data-quarry-controls],[data-cave-study-controls],aside[class*=inspection]{visibility:hidden!important}'});
 for(const geometry of ['baseline','pilot']){
  await p.evaluate(enabled=>{window.__gullyverse.runtime.setQuality(3);window.__wallPreview.setStudyGeometry(enabled);},geometry==='pilot');await ready();assert.equal(await p.evaluate(()=>window.__wallPreview.studyDiagnostics().geometryMode),geometry);
  for(const material of ['control','rock_01','rock_05']){
   await p.evaluate(id=>{window.__gullyverse.runtime.setQuality(3);window.__wallPreview.setStudySelection(id,1);},material);await ready();
   for(const pose of material==='control'?poses:poses.filter(v=>['walking','side','along'].includes(v[0])))await save(pose[0],pose,material,geometry,'dusk');
  }
  await neutral(true);for(const pose of poses)await save(pose[0],pose,'clay',geometry,'neutral-no-maps');await p.setViewportSize({width:390,height:844});await save('walking',poses[0],'clay',geometry,'neutral-no-maps',true);await p.setViewportSize({width:1366,height:900});await neutral(false);
  await neutral(true,true);await save('side',poses[1],'wire',geometry,'wireframe-no-maps');await neutral(false);
 }
 const pairs=[];for(const shot of shots.filter(s=>s.geometry==='pilot')){const baseline=shots.find(s=>s.geometry==='baseline'&&s.id===shot.id&&s.material===shot.material&&s.condition===shot.condition&&s.mobileAspect===shot.mobileAspect);assert.ok(baseline);assert.deepEqual(shot.data.camera,baseline.data.camera);assert.deepEqual(shot.data.viewport,baseline.data.viewport);pairs.push({file:shot.file,control:baseline.file,matchedCamera:true});}
 await writeFile(R+'/raw/pilot-matches.json',JSON.stringify({status:'PASS',pairs},null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;}finally{await ctx.close();await browser.close();await writeFile(R+'/raw/pilot-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,errors,physicalHardware:false},null,2));}
