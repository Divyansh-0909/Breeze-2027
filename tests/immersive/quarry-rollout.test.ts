import test from "node:test";
import assert from "node:assert/strict";
import {tunnelGeometry,quarryGeometry} from "../../components/immersive/blockoutGeometry";
import {tunnelOutsideQuarryRear,currentQuarryConnectionFits} from "../../components/immersive/quarryRollout";
import {QUARRY,currentWallAnchorFits} from "../../components/immersive/wallSection";
import {world} from "../../components/immersive/world";

test("rollout retains every passage/entrance-facing tunnel attribute exactly",()=>{
  const old=tunnelGeometry(),current=tunnelOutsideQuarryRear();
  try{
    const interior=56*(world.tunnel.profile.length-1)*3*6;
    for(const name of Object.keys(old.attributes)){
      const a=old.attributes[name],b=current.attributes[name];
      assert.deepEqual(Array.from(b.array.slice(0,interior*a.itemSize)),Array.from(a.array.slice(0,interior*a.itemSize)),name);
      const survivors:number[]=[];
      for(let i=0;i<a.count;i++)if(!QUARRY.tunnelRearRanges.some(r=>i>=r.start&&i<r.start+r.count))survivors.push(...Array.from(a.array.slice(i*a.itemSize,(i+1)*a.itemSize)));
      assert.deepEqual(Array.from(b.array),survivors,name);
    }
  }finally{old.dispose();current.dispose();}
});
test("all existing quarry anchors and the current tunnel connections fit the rollout",()=>{
  assert.equal(currentWallAnchorFits("quarry"),true);assert.equal(currentQuarryConnectionFits(),true);
  assert.deepEqual(QUARRY.parts.filter(p=>typeof p.id==="number").map(p=>p.id),Array.from({length:25},(_,i)=>i+2));
  const original=quarryGeometry();try{original.computeBoundingBox();const box=original.boundingBox!;assert.deepEqual([0,1,2].map(i=>[box.min.getComponent(i),box.max.getComponent(i)]),QUARRY.sourceQuarryBounds);}finally{original.dispose();}
});
