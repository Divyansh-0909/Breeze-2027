import * as THREE from "three";
import manifest from "@/public/models/gullyverse/quarry-rollout/manifest.json";
import {exitGeometry,tunnelGeometry} from "./blockoutGeometry";

/** Leave the passage, entrance-facing roof, paint and source generator intact. */
export function tunnelOutsideQuarryRear() {
  const original=tunnelGeometry(),result=new THREE.BufferGeometry();
  for(const [name,attribute]of Object.entries(original.attributes)){
    const values=attribute.array as Float32Array,kept:number[]=[];let cursor=0;
    for(const {start,count}of manifest.tunnelRearRanges){kept.push(...values.slice(cursor*attribute.itemSize,start*attribute.itemSize));cursor=start+count;}
    kept.push(...values.slice(cursor*attribute.itemSize));result.setAttribute(name,new THREE.BufferAttribute(new Float32Array(kept),attribute.itemSize));
  }
  result.computeBoundingBox();result.computeBoundingSphere();original.dispose();return result;
}
export function currentQuarryConnectionFits() {
  const tunnel=tunnelGeometry(),exit=exitGeometry();
  try{
    if(tunnel.attributes.position.count!==manifest.sourceTunnelVertexCount||exit.attributes.position.count!==manifest.sourceExitVertexCount)return false;
    const rear=manifest.tunnelRearRanges.flatMap(({start,count})=>Array.from({length:count},(_,i)=>new THREE.Vector3().fromBufferAttribute(tunnel.attributes.position,start+i).toArray()));
    return rear.every((p,i)=>p.every((v,j)=>Math.abs(v-manifest.sourceRearPositions[i][j])<2e-5))&&manifest.sourceExitPositions.every((p,i)=>p.every((v,j)=>Math.abs(v-exit.attributes.position.array[i*3+j])<2e-5));
  }finally{tunnel.dispose();exit.dispose();}
}
