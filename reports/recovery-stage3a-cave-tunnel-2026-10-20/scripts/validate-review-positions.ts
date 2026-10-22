/** Classify evidence against actual movement boundaries, not camera appearance. */
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {constrain, type Pose} from '../../../components/immersive/navigation';
import {world,tunnelCenter} from '../../../components/immersive/world';
const root='reports/recovery-stage3a-cave-tunnel-2026-10-20';
const capture=JSON.parse(fs.readFileSync(root+'/raw/review-captures.json','utf8'));
const rows=capture.shots.filter((s:{candidate:boolean})=>s.candidate).map((s:any)=>{
 const c=s.data.camera,p:Pose={x:c.x,y:c.y,z:c.z,yaw:c.yaw,pitch:c.pitch};
 if(!s.inspection)return{id:s.id,mobile:s.mobile,classification:'ACTUAL_PUBLIC_INTERFACE_CAMERA',publicWalking:false,note:'Actual landing or map controls; no inspection pose.'};
 const bounded={...p};constrain(s.id==='stage'?'aftermovie':'hub',bounded);
 const correctionM=Math.hypot(bounded.x-p.x,bounded.z-p.z);
 if(correctionM<1e-6&&Math.abs(p.y-world.eyeHeight)<1e-6)return{id:s.id,mobile:s.mobile,classification:'VALID_PUBLIC_WALKING_POSITION_FIXED_INSPECTION_ORIENTATION',publicWalking:true,correctionM,note:'Position passes unchanged movement/collision registry; orientation is a matched inspection.'};
 const inCorridor=p.z<=world.portal.position[2]&&p.z>=world.tunnel.endZ&&Math.abs(p.x-tunnelCenter(p.z))<=world.tunnel.walkHalfWidth&&Math.abs(p.y-world.eyeHeight)<1e-6;
 return{id:s.id,mobile:s.mobile,classification:inCorridor?'EXISTING_PUBLIC_ENTRY_ROUTE_FIXED_INSPECTION_CAMERA':'NON_PUBLIC_INSPECTION_CAMERA',publicWalking:false,correctionM,note:inCorridor?'Within the protected public entry corridor. Entry choreography passes here; this is not an ordinary controllable hub walking location.':'Temporary art/forecourt/reveal inspection, not asserted as an ordinary walking viewpoint.'};
});
assert.ok(rows.some((s:any)=>s.id==='c9-visitor'&&s.publicWalking));
assert.ok(rows.some((s:any)=>s.id==='hub'&&s.publicWalking));
fs.writeFileSync(root+'/review-position-classification.json',JSON.stringify({status:'PASS',toleranceM:1e-6,registryUnchanged:true,rows},null,2));
console.log(JSON.stringify(rows));
