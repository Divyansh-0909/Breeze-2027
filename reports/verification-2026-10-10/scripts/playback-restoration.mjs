import {launch,instrument,local,key,pose,snapshot,save,base} from './audit-common.mjs';
import assert from 'node:assert/strict';
const b=await launch(),c=await b.newContext({viewport:{width:1366,height:900},deviceScaleFactor:.25});await instrument(c);const p=await c.newPage(),checks=[];
try{
await p.goto(base+'/aftermovie?diagnostics');await local(p,'aftermovie');
for(const moving of [false,true]){
 if(moving)await key(p,'KeyD',700);
 const beforeClickRead=await pose(p);
 await p.evaluate(()=>{const r=window.__gullyverse.runtime;window.__movieStartPose=new Promise(resolve=>{const off=r.subscribe(()=>{if(r.getSnapshot().movie){off();resolve({...r.pose});}});});});
 await p.getByRole('button',{name:'Play Aftermovie',exact:true}).click();const activationPose=await p.evaluate(()=>window.__movieStartPose);await p.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.2,null,{timeout:60000});
 await p.keyboard.down('KeyD');const rejectedInput=await p.evaluate(()=>({...window.__gullyverse.runtime.input}));await p.keyboard.up('KeyD');assert.equal(rejectedInput.strafe,0);
 await p.keyboard.press('Escape');const at=Date.now();await p.waitForFunction(target=>{const r=window.__gullyverse.runtime;return !r.getSnapshot().movie&&Math.hypot(r.pose.x-target.x,r.pose.y-target.y,r.pose.z-target.z)<.00001;},activationPose,{timeout:30000});const after=await pose(p),restoreWallMs=Date.now()-at;
 await key(p,'KeyA',500);const freshMovement=await pose(p);assert.ok(Math.abs(freshMovement.x-after.x)>.1);
 checks.push({name:moving?'Movie restores activation pose after moving (inertia accounted)':'Movie restores stable activation pose',status:'PASS',beforeClickRead,activationPose,after,restoreWallMs,rejectedInput,freshMovement,afterSnapshot:await snapshot(p)});await save('playback-restoration.json',{checks});console.log(checks.at(-1).name,'PASS',restoreWallMs);
 // Return to a clean public stage spawn using real map travel for the second case.
 if(!moving){await p.goto(base+'/aftermovie?diagnostics');await local(p,'aftermovie');}
}
}catch(e){checks.push({name:'restoration probe',status:'FAIL',error:String(e.stack||e),state:await snapshot(p).catch(()=>null)});process.exitCode=1;}finally{await save('playback-restoration.json',{checks});await b.close();}
