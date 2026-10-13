import{launch,context,ready,details,root}from'./wall-browser-common.mjs';import{writeFile,mkdir}from'node:fs/promises';import assert from'node:assert/strict';
const b=await launch();await mkdir(root+'/recordings',{recursive:true});
const c=await context(b,{viewport:{width:1366,height:900},deviceScaleFactor:.5,recordVideo:{dir:root+'/recordings',size:{width:1366,height:900}}}),p=await c.newPage(),events=[],errors=[];
p.on('pageerror',e=>errors.push(e.message));
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation');await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls]{visibility:hidden!important}'});
 events.push({event:'initial visitor spawn',data:await details(p)});
 // Actual pointer-look and held public movement keys; no pose substitution.
 await p.mouse.move(620,320);await p.mouse.down();await p.mouse.move(860,345,{steps:18});await p.mouse.up();
 await p.keyboard.down('KeyW');await p.waitForTimeout(3500);await p.keyboard.up('KeyW');
 await p.keyboard.down('KeyD');await p.waitForTimeout(2200);await p.keyboard.up('KeyD');
 await p.waitForTimeout(1000);events.push({event:'public eye-height walking',data:await details(p)});
 assert.equal(events.at(-1).data.snapshot.scene,'hub');assert.equal(events.at(-1).data.pose.y,1.72);
 await p.getByRole('button',{name:/^Map/}).click();
 await p.waitForFunction(()=>window.__gullyverse.runtime.mapProgress>.25,null,{timeout:60000});
 await p.screenshot({path:root+'/recordings/map-ascent.png'});events.push({event:'public map ascent',data:await details(p)});
 await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});
 await p.waitForTimeout(2500);events.push({event:'public aerial map',data:await details(p)});
 await p.getByRole('button',{name:'Close map',exact:true}).click();
 await p.waitForFunction(()=>window.__gullyverse.runtime.mapProgress<.7,null,{timeout:60000});
 await p.screenshot({path:root+'/recordings/map-descent.png'});events.push({event:'public map descent',data:await details(p)});
 await p.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().map,null,{timeout:60000});await p.waitForTimeout(1500);
 assert.deepEqual(errors,[]);
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{const video=p.video();await c.close();await video.saveAs(root+'/recordings/visitor-walk-and-aerial.webm');await b.close();await writeFile(root+'/raw/walkthrough.json',JSON.stringify({status:errors.length?'FAIL':'PASS',method:'Actual browser recording, public mouse-look/WASD/Map controls, original visitor spawn and eye height. SwiftShader, DPR0.5 quality3; not physical GPU footage or an inspection-camera animation.',events,errors},null,2));}
