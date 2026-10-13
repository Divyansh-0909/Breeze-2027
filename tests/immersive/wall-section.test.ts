import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {quarryGeometry} from '../../components/immersive/blockoutGeometry';
import {WALL,CORRECTED_WALL,chooseWallLOD,projectedWallPixels,quarryWithoutWallFace,originalWallFace,wallTransform} from '../../components/immersive/wallSection';

test('one face is removed while every other authored attribute remains exact',()=>{
 const whole=quarryGeometry(),cut=quarryWithoutWallFace();
 for(const [name,a] of Object.entries(whole.attributes)){
  const b=cut.getAttribute(name);assert.equal(b.count,a.count-9);const expected=[...a.array.slice(0,WALL.vertexStart*a.itemSize),...a.array.slice((WALL.vertexStart+9)*a.itemSize)];assert.deepEqual(Array.from(b.array),expected);
 }
 const face=originalWallFace();assert.equal(face.attributes.position.count,9);
 assert.deepEqual(Array.from(face.attributes.position.array),Array.from(whole.attributes.position.array.slice(WALL.vertexStart*3,(WALL.vertexStart+9)*3)));
 whole.dispose();cut.dispose();face.dispose();
});
test('wall placement is a rigid right-handed metric basis matching the existing rim',()=>{
 const {position,quaternion}=wallTransform();
 for(let i=0;i<WALL.boundaryLocal.length;i++){
  const p=new THREE.Vector3(...WALL.boundaryLocal[i],0).applyQuaternion(quaternion).add(position),expected=new THREE.Vector3().fromArray(WALL.boundaryWorld[i]);assert.ok(p.distanceTo(expected)<2e-6);
 }
 assert.ok(Math.abs(quaternion.length()-1)<1e-10);
});
test('screen-space LOD hysteresis prevents oscillation at both distance thresholds',()=>{
 assert.equal(chooseWallLOD(730,0,1),0);assert.equal(chooseWallLOD(690,0,0),0);assert.equal(chooseWallLOD(550,0,0),1);
 assert.equal(chooseWallLOD(230,0,2),1);assert.equal(chooseWallLOD(210,0,1),1);assert.equal(chooseWallLOD(150,0,1),2);
 assert.equal(chooseWallLOD(730,3,1),1);assert.equal(chooseWallLOD(1100,3,1),0);
});
test('LOD projection respects rendered resolution/FOV and safely handles invisible/invalid inputs',()=>{
 const c=new THREE.PerspectiveCamera(58,16/9,.1,700);c.updateMatrixWorld();const center=new THREE.Vector3(0,0,-20);
 const pixels=projectedWallPixels(center,2,c,720);assert.ok(Math.abs(pixels-2*720/(Math.tan(29*Math.PI/180)*20))<1e-8);
 assert.equal(projectedWallPixels(center,2,c,1440),pixels*2);assert.equal(projectedWallPixels(new THREE.Vector3(0,0,20),2,c,720),0);
 assert.equal(chooseWallLOD(NaN,0,0),2);assert.equal(projectedWallPixels(center,NaN,c,720),0);
});

test('volumetric host and localized contacts preserve every unrelated quarry attribute',()=>{
 const original=quarryGeometry(),replacement=quarryWithoutWallFace('volume'),ranges=[CORRECTED_WALL.hostRange,...CORRECTED_WALL.joinRanges].sort((a,b)=>a.start-b.start),removed=ranges.reduce((n,r)=>n+r.count,0);
 assert.equal(CORRECTED_WALL.hostRange.start,216);assert.equal(CORRECTED_WALL.hostRange.count,108);assert.equal(removed,144);
 for(const [name,a]of Object.entries(original.attributes)){const b=replacement.getAttribute(name),expected=[];let cursor=0;for(const {start,count}of ranges){expected.push(...a.array.slice(cursor*a.itemSize,start*a.itemSize));cursor=start+count;}expected.push(...a.array.slice(cursor*a.itemSize));assert.equal(b.count,a.count-removed);assert.deepEqual(Array.from(b.array),expected);}
 original.dispose();replacement.dispose();
});
