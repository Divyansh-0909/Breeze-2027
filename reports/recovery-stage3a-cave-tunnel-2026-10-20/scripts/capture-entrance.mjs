import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {launch,context,view,details,unfix} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const root='reports/recovery-stage3a-cave-tunnel-2026-10-20', browser=await launch(),shots=[],errors=[];
const poses=[['landing',[0,1.72,11.5],[0,3.5,0]],['entrance-diagonal',[7,1.72,8],[0,3,0]],['mouth-left',[-8,2,5],[-3,4,0]],['mouth-right',[8,2,5],[3,4,0]],['tunnel-first',[-.825,1.72,-3],[-4,2.3,-12]],['tunnel-mid',[-6,1.72,-22],[-2.6,2.4,-34]],['tunnel-bend',[-4.64,1.72,-28],[0,3.1,-42]],['exit',[-1.3,1.72,-38],[0,7.4,-70]],['look-back',[0,1.72,-47],[0,3,-35]],['hub',[0,1.72,-51],[0,6.6,-92.7]]];
let current;
try{
 for(const mobile of[false,true]){
  current=await context(browser,{deviceScaleFactor:1,viewport:mobile?{width:390,height:844}:{width:1366,height:900},isMobile:mobile,hasTouch:mobile});const page=await current.newPage();
  page.on('pageerror',e=>errors.push(String(e.stack)));
  await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave');
  await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
  await page.waitForSelector('[data-phase="landing"]',{timeout:90000});
  await page.waitForFunction(()=>!window.__wallPreview.state.busy&&window.__wallPreview.entranceRoot?.deref()?.parent,null,{timeout:90000});
  await page.addStyleTag({content:'[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}'});
  const folder=(process.env.GULLYVERSE_CAVE_CAPTURE_GROUP||'working')+(mobile?'-mobile':'-desktop');await mkdir(root+'/screenshots/'+folder,{recursive:true});
  for(const[id,p,t]of mobile?poses.filter(p=>['landing','tunnel-first','hub'].includes(p[0])):poses){
   await view(page,p,t,{fixed:true,quality:0});await page.waitForTimeout(300);
   const file='screenshots/'+folder+'/'+id+'.png';await page.screenshot({path:root+'/'+file});
   shots.push({file,id,position:p,target:t,view:await details(page),entrance:await page.evaluate(()=>window.__wallPreview.entranceDiagnostics())});console.log(file);
   await writeFile(root+'/raw/entrance-captures.json',JSON.stringify({status:'RUNNING',shots,errors},null,2));
  }
  await current.close();current=null;
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await current?.close();await browser.close();await writeFile(root+'/raw/entrance-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',scope:'Entrance-only checkpoint; not full Stage3A completion or art approval',build:(await readFile('.next/BUILD_ID','utf8')).trim(),shots,errors},null,2));}
