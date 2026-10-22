import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {launch,context,view,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const root='reports/stage3a1-deep-rock-2026-10-21',candidate=process.argv.includes('--candidate'),label=candidate?'pilot-final':'stage3a';
const browser=await launch(),shots=[],errors=[],downloads=[];let current;
const cx=z=>z>=-8?z*.275:z>=-16?-2.2+(-z-8)*(-3.8/8):-6;
const poses=[
 ['approach',[cx(-7),1.72,-7],[cx(-13)-2,2.3,-13]],
 ['normal-walking',[cx(-9),1.72,-9],[cx(-14)-2.8,2.5,-14]],
 ['side-fracture',[cx(-11.2),1.72,-11.2],[cx(-11.2)-4,2.35,-11.2]],
 ['along-wall',[cx(-8.5)-1.6,1.72,-8.5],[cx(-14)-3,2.5,-14]],
 ['parallax-a',[cx(-10.2),1.72,-10.2],[cx(-11.2)-4,2.2,-11.2]],
 ['parallax-b',[cx(-12.2),1.72,-12.2],[cx(-11.2)-4,2.2,-11.2]],
 ['vault',[cx(-11.2),1.72,-11.2],[cx(-12),4.8,-12]],
];
async function capture(page,id,pose,condition,mobile,scale){
 await view(page,pose[1],pose[2],{fixed:true,quality:0});await page.waitForTimeout(500);
 const file=`screenshots/pilot-gate-final/${label}-${mobile?'mobile':'desktop'}-${condition}-${id}.png`;await page.screenshot({path:root+'/'+file});
 shots.push({id,file,candidate,mobile,condition,scale,position:pose[1],target:pose[2],publicPosition:'Protected entry trajectory inspection; not free hub walking',data:await details(page),cave:await page.evaluate(()=>window.__wallPreview.entranceDiagnostics())});console.log(file);
}
async function neutral(page,enabled){
 await page.evaluate(enabled=>{
  if(enabled){
   const root=window.__wallPreview.entranceRoot.deref();let scene=root;while(scene.parent)scene=scene.parent;
   window.__pilotOriginals=[];window.__pilotLights=[];window.__pilotMaterials=[];
   scene.traverse(o=>{if(o.isLight){window.__pilotLights.push([o,o.visible]);o.visible=false;}});
   root.traverse(o=>{if(!o.isMesh)return;const m=o.material.clone();m.onBeforeCompile=()=>{};m.customProgramCacheKey=()=> 'stage3a1-neutral-true-geometry';for(const key of ['map','normalMap','roughnessMap','metalnessMap','aoMap'])m[key]=null;m.vertexColors=false;m.color.set('#858585');m.roughness=1;m.metalness=0;window.__pilotOriginals.push([o,o.material]);window.__pilotMaterials.push(m);o.material=m;});
   const h=window.__pilotLights.find(([o])=>o.isHemisphereLight)[0].clone(),d=window.__pilotLights.find(([o])=>o.isDirectionalLight)[0].clone();h.visible=true;h.color.set('#ffffff');h.groundColor.set('#858b95');h.intensity=.8;d.visible=true;d.color.set('#ffffff');d.intensity=3;d.position.set(2,8,-3);window.__pilotAdded=[h,d];scene.add(h,d);
  }else{window.__pilotOriginals.forEach(([o,m])=>o.material=m);window.__pilotMaterials.forEach(m=>m.dispose());window.__pilotAdded.forEach(l=>l.removeFromParent());window.__pilotLights.forEach(([o,v])=>o.visible=v);}
 },enabled);
}
try{
 await mkdir(root+'/screenshots/pilot-gate-final',{recursive:true});
 for(const mobile of[false]){
  current=await context(browser,{deviceScaleFactor:1,viewport:mobile?{width:390,height:844}:{width:1366,height:900},isMobile:mobile,hasTouch:mobile});const page=await current.newPage();page.on('pageerror',e=>errors.push(String(e.stack)));
  const bodies=[];page.on('response',r=>{if(/\/c9-cave-(recovery|deep-relief)\/.*\.glb$/.test(r.url()))bodies.push(r.body().then(b=>downloads.push({url:r.url(),bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')})));});
  await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview='+(candidate?'deep-rock':'natural-cave'));
  await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await page.waitForSelector('[data-phase="landing"]',{timeout:90000});await page.waitForFunction(()=>!window.__wallPreview.state.busy&&window.__wallPreview.entranceRoot?.deref()?.parent,null,{timeout:90000});
  await page.addStyleTag({content:'[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}'});
  for(const condition of candidate?['dusk-2x','neutral']:['dusk-1x','neutral']){
   const scale=condition==='dusk-1x'?1:candidate?2:1;
   if(candidate)await page.evaluate(scale=>window.__wallPreview.setCaveTextureFeatureScale(scale),scale);
   if(condition==='neutral')await neutral(page,true);
   for(const pose of poses.filter(p=>['normal-walking','side-fracture'].includes(p[0])))await capture(page,pose[0],pose,condition,mobile,scale);
   if(condition==='neutral')await neutral(page,false);
  }
  await Promise.all(bodies);assert.equal(await page.evaluate(()=>window.__wallPreview.textureScale),3);
  await current.close();current=null;
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await current?.close();await browser.close();await writeFile(root+'/raw/'+label+'-pilot-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,downloads,errors,physicalHardware:false},null,2));}
