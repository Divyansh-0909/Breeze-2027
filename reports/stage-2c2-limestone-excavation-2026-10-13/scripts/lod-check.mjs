import{launch,context,ready,view,unfix,details,root}from'./wall-browser-common.mjs';import{mkdir,writeFile,readFile}from'node:fs/promises';import assert from'node:assert/strict';
const b=await launch(),c=await context(b,{deviceScaleFactor:.5}),p=await c.newPage(),frames=[],errors=[];
const manifest=JSON.parse(await readFile('public/models/gullyverse/limestone-excavation/manifest.json','utf8')),
 targetArc=manifest.detailAreas[0].arcCenter,targetPart=manifest.variants.detailed.parts.find(p=>p.arc[0]<=targetArc&&p.arc[1]>=targetArc).id;
try{
 await mkdir(root+'/lod',{recursive:true});await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation');await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 // Far first establishes LOD2, so near-level hysteresis cannot invalidate
 // the subsequent medium-distance expectation.
 await view(p,[20,1.72,-94],[-45,12,-72],{fixed:true,quality:3});
 for(const[name,pos,target,wanted]of[['middle',[-18,2,-66],[-46,10,-70],1],['near',[-42,5,-69],[-46,8,-70],0]]){
  await view(p,pos,target,{fixed:true,quality:3});await p.waitForTimeout(500);const d=await details(p);
  assert.equal(d.wall.lodSelections[targetPart],wanted);
  await p.screenshot({path:root+'/lod/'+name+'.png'});frames.push({name,wanted,details:d});
 }
 await unfix(p);await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.pose={x:0,y:1.72,z:-51,yaw:0,pitch:.1};r.setQuality(3);});
 await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});await p.waitForTimeout(400);const d=await details(p);
 assert.equal(d.wall.lodSelections[targetPart],2);await p.screenshot({path:root+'/lod/distant-map.png'});frames.push({name:'distant-map',wanted:2,details:d});
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await writeFile(root+'/raw/lod-runtime.json',JSON.stringify({status:errors.length?'FAIL':'PASS',frames,errors,method:'Actual runtime selection, screen-space/quality/hysteresis active. Fixed near/medium inspection views and public distant aerial map. No forced LOD visibility override.'},null,2));await c.close();await b.close();}
