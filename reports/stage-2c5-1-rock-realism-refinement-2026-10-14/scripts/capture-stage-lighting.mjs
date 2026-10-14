import {writeFile} from 'node:fs/promises';
import {launch,context,ready,view,details,root} from './wall-browser-common.mjs';
const b=await launch(),captures=[],errors=[];
for(const label of ['before','after']){
 const c=await context(b,{deviceScaleFactor:1}),p=await c.newPage();
 try{
  await p.goto('http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview='+(label==='before'?'foundation':'foundation-refined'));
  await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
  await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
  await view(p,[-10.5,1.72,-110.8],[-51,14,-90],{fixed:true,quality:0});await p.waitForTimeout(500);
  const file=label+'/desktop-20-regions-under-stage-lighting.png';await p.screenshot({path:root+'/'+file,scale:'css'});
  captures.push({file,note:'Same original Aftermovie player spawn, rotated toward the two art regions; existing Aftermovie lighting/fog unchanged.',data:await details(p)});console.log(file);
 }catch(e){errors.push(String(e.stack));process.exitCode=1;}finally{await c.close();}
}
await b.close();await writeFile(root+'/raw/stage-lighting-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',captures,errors},null,2));
