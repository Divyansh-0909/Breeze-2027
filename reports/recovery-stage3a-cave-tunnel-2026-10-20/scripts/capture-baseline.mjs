import {mkdir,writeFile} from 'node:fs/promises';
import {launch,context,view,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const root='reports/recovery-stage3a-cave-tunnel-2026-10-20';
const browser=await launch(),c=await context(browser,{deviceScaleFactor:1});const page=await c.newPage();let shots=[],errors=[];
try{
 await page.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity');
 await page.waitForFunction(()=>window.__gullyverse?.runtime);
 await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await page.waitForSelector('[data-phase="landing"]',{timeout:90000});
 await page.waitForFunction(()=>!window.__wallPreview.state.busy,null,{timeout:90000});
 await page.addStyleTag({content:'[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}'});
 await mkdir(root+'/screenshots/before',{recursive:true});
 const poses=[['landing',[0,1.72,11.5],[0,3.5,0]],['entrance-diagonal',[7,1.72,8],[0,3,0]],['mouth-left',[-8,2,5],[-3,4,0]],['mouth-right',[8,2,5],[3,4,0]],['tunnel-first',[-.825,1.72,-3],[-4,2.3,-12]],['tunnel-mid',[-6,1.72,-22],[-2.6,2.4,-34]],['tunnel-bend',[-4.64,1.72,-28],[0,3.1,-42]],['exit',[-1.3,1.72,-38],[0,7.4,-70]],['look-back',[0,1.72,-47],[0,3,-35]],['hub',[0,1.72,-51],[0,6.6,-92.7]]];
 for(const[id,p,t]of poses){await view(page,p,t,{fixed:true,quality:0});await page.waitForTimeout(500);const f='screenshots/before/'+id+'.png';await page.screenshot({path:root+'/'+f});shots.push({file:f,position:p,target:t,details:await details(page)});console.log(id);}
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await writeFile(root+'/raw/baseline-browser.json',JSON.stringify({status:errors.length?'FAIL':'PASS',shots,errors},null,2));await c.close();await browser.close();}
