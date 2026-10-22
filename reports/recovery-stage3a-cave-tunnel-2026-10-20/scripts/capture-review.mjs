import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {launch,context,view,details,unfix,ready} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const root='reports/recovery-stage3a-cave-tunnel-2026-10-20',browser=await launch(),shots=[],errors=[],downloads=[];let current;
if(process.env.GULLYVERSE_REVIEW_RESUME==='1'){const prior=JSON.parse(await readFile(root+'/raw/review-captures.json','utf8'));assert.ok(prior.shots.every(s=>!s.candidate),'Only unchanged baseline captures may be resumed across the isolated loading-policy change');shots.push(...prior.shots.map(s=>({...s,capturedBuild:prior.build,reuseEvidence:'All accepted C9/C8/registry/light files remain byte-identical per preservation.json'})));downloads.push(...prior.downloads);}
const manifest=JSON.parse(await readFile('public/models/gullyverse/c9-cave-recovery/manifest.json','utf8'));
const poses=[
 ['landing','Entrance front',[0,1.72,11.5],[0,3.5,0],true],
 ['entrance-diagonal','Entrance diagonal',[7,1.72,8],[0,3,0],true],
 ['mouth-left','Left geological connection',[-8,2,5],[-3,4,0],false],
 ['mouth-right','Right geological connection',[8,2,5],[3,4,0],false],
 ['upper-rim','Upper entrance rock',[0,2,10],[0,11,-2],false],
 ['ground-contact','Entrance rock foot',[1.5,1.72,4],[-3.5,.5,-1],true],
 ['raised-rock','Raised rock inspection',[-2.3,1.72,3],[-4.1,2.2,0],false],
 ['tunnel-first','First tunnel section',[-.825,1.72,-3],[-4,2.3,-12],true],
 ['tunnel-deeper','Looking into the passage',[-1.65,1.72,-6],[-4.3,2.8,-15],true],
 ['tunnel-mid','Mid passage',[-6,1.72,-22],[-2.6,2.4,-34],true],
 ['rock-vault','Natural rock vault',[-6,1.72,-22],[-5,5,-25],true],
 ['bend-before','Before the bend',[-6,1.72,-23],[-3,2.5,-33],true],
 ['tunnel-bend','After the bend',[-4.64,1.72,-28],[0,3.1,-42],true],
 ['entry-look-back','Looking back toward entry',[-4.1,1.72,-12],[0,2,8],true],
 ['final-enclosed','Final passage section',[-1.3,1.72,-38],[0,3,-44],true],
 ['exit','Quarry reveal',[-1.3,1.72,-38],[0,7.4,-70],true],
 ['look-back','Quarry looking into tunnel',[0,1.72,-47],[0,3,-35],true],
 ['hub','Hub and scaffold',[0,1.72,-51],[0,6.6,-92.7],true],
 ['scaffold','Scaffold branding preserved',[0,1.72,-58],[0,8,-70],true],
 ['c9-visitor','Accepted C9 wall',[-18,1.72,-55],[-44,6,-65],true]
];
async function save(page,folder,id,title,meta={}){
 const file=`screenshots/${folder}/${id}.png`;if(shots.some(s=>s.file===file))return;await page.screenshot({path:root+'/'+file});const data=await details(page);
 const row={id,title,file,capturedBuild:(await readFile('.next/BUILD_ID','utf8')).trim(),...meta,data,cave:await page.evaluate(()=>window.__wallPreview.entranceDiagnostics?.()??null)};shots.push(row);assert.equal(data.viewport.requestedDpr,1);assert.equal(data.stats.dpr,1);assert.equal(data.snapshot.quality,0);
 await writeFile(root+'/raw/review-captures.json',JSON.stringify({status:'RUNNING',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,downloads,errors},null,2));console.log(file);
}
try{
 for(const candidate of [false,true])for(const mobile of [false,true]){
  current=await context(browser,{deviceScaleFactor:1,viewport:mobile?{width:390,height:844}:{width:1366,height:900},isMobile:mobile,hasTouch:mobile});
  const page=await current.newPage();page.on('pageerror',e=>errors.push(String(e.stack)));
  const bodyPromises=[];page.on('response',r=>{if(r.url().endsWith('/c9-cave-recovery/cave-entrance.glb'))bodyPromises.push(r.body().then(b=>downloads.push({url:r.url(),bytes:b.length,sha256:createHash('sha256').update(b).digest('hex')})));});
  await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity'+(candidate?'&entranceReview=natural-cave':''));
  await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await page.waitForSelector('[data-phase="landing"]',{timeout:90000});await page.waitForFunction(()=>!window.__wallPreview.state.busy,null,{timeout:90000});
  if(candidate)await page.waitForFunction(()=>window.__wallPreview.entranceRoot?.deref()?.parent,null,{timeout:90000});
  await page.addStyleTag({content:'[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}'});
  const folder='review-'+(candidate?'after':'before')+(mobile?'-mobile':'-desktop');await mkdir(root+'/screenshots/'+folder,{recursive:true});
  await page.evaluate(()=>window.__gullyverse.runtime.setQuality(0));await page.waitForTimeout(500);await save(page,folder,'landing-ui','Actual landing interface',{candidate,mobile,publicCamera:true,inspection:false});
  for(const[id,title,p,t,valid]of mobile?poses.filter(p=>['landing','tunnel-first','tunnel-mid','hub'].includes(p[0])):poses){await view(page,p,t,{fixed:true,quality:0});await page.waitForTimeout(300);await save(page,folder,id,title,{candidate,mobile,position:p,target:t,publicWalkingPosition:valid,inspection:true,lighting:'Approved dusk; candidate uses local opening response only inside cave'});}
  await unfix(page);await page.evaluate(()=>{const r=window.__gullyverse.runtime;r.inspect(null);r.setQuality(3);});await page.getByRole('button',{name:'Enter Gullyverse',exact:true}).click();await ready(page);
  await page.getByRole('button',{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open');await page.evaluate(()=>window.__gullyverse.runtime.setQuality(0));await page.waitForTimeout(500);await save(page,folder,'aerial-map','Actual GTA-style map',{candidate,mobile,publicCamera:true,inspection:false});
  if(!mobile){await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await page.getByRole('button',{name:'Aftermovie',exact:true}).click();await page.waitForFunction(()=>window.__gullyverse?.runtime?.getSnapshot().scene==='aftermovie'&&window.__gullyverse?.runtime?.getSnapshot().phase==='local',null,{timeout:90000});await ready(page);await view(page,[-10.5,1.72,-110.8],[-12,5.9,-128.3],{fixed:true,quality:0});await save(page,folder,'stage','Original Aftermovie stage',{candidate,mobile,position:[-10.5,1.72,-110.8],target:[-12,5.9,-128.3],publicWalkingPosition:true,inspection:true});}
  await Promise.all(bodyPromises);await current.close();current=null;
 }
 assert.ok(downloads.length===2&&downloads.every(d=>d.sha256===manifest.runtimeSHA256&&d.bytes===manifest.runtimeBytes),'Browser loaded different asset bytes from frozen manifest');
 // Matched comparisons are checked from actual renderer/camera metadata.
 const pairs=[];
 // JSON round-trip canonicalizes IEEE signed zero only, without rounding or
 // admitting any numeric tolerance. The source metadata retains raw values.
 const canonical=v=>JSON.parse(JSON.stringify(v));
 for(const after of shots.filter(s=>s.candidate)){const before=shots.find(s=>!s.candidate&&s.mobile===after.mobile&&s.id===after.id);assert.ok(before);for(const k of['viewport','camera'])assert.deepEqual(canonical(after.data[k]),canonical(before.data[k]));assert.deepEqual(after.data.lighting,before.data.lighting);assert.equal(after.data.snapshot.quality,before.data.snapshot.quality);pairs.push({id:after.id,mobile:after.mobile,before:before.file,after:after.file,actualCameraFovDprQualityLightsIdentical:true,signedZeroCanonicalized:true});}
 await writeFile(root+'/matched-pose-verification.json',JSON.stringify({status:'PASS',pairs},null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await current?.close();await browser.close();await writeFile(root+'/raw/review-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,downloads,errors,physicalHardware:false,lighting:'Global approved lighting preserved. Local analytical opening response affects candidate interior only.',artApproval:'PENDING_USER'},null,2));}
