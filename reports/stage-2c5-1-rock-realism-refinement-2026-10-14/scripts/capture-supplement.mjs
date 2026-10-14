import {writeFile} from 'node:fs/promises';
import {launch,context,ready,view,details,root} from './wall-browser-common.mjs';
const label=process.argv[2]||'after',b=await launch(),c=await context(b,{deviceScaleFactor:1}),p=await c.newPage(),captures=[],errors=[];
const frames=[
 ['21-broken-fracture',[-48.628,8.5,-99.888],[-54.627,10.5,-99.784]],
 ['22-bed-fault-intersection',[-44.88,9.6,-78.573],[-50.63,11.6,-76.856]],
 ['23-rim-contact',[-45.921,29,-82.657],[-51.732,30.882,-81.165]],
 ['24-ground-contact',[-46.327,1.72,-92.225],[-52.256,0,-91.301]],
];
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview='+(label==='before'?'foundation':'foundation-refined'));
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 for(const[name,pos,target]of frames){
  await view(p,pos,target,{fixed:true,quality:0});await p.waitForTimeout(400);
  const file=label+'/desktop-'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});
  captures.push({file,note:'Actual browser inspection, matched poses outside locomotion bounds; original Hub lighting.',data:await details(p)});console.log(file);
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c.close();await b.close();await writeFile(root+'/raw/'+label+'-supplement-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',captures,errors},null,2));}
