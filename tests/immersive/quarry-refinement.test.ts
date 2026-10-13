import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import type {GLTF} from "three/examples/jsm/loaders/GLTFLoader.js";
import {ImmersiveRuntime} from "../../components/immersive/runtime";
import {QUARRY} from "../../components/immersive/wallSection";
import {RefinedQuarrySession,REFINED_QUARRY,refinementParts} from "../../components/immersive/RefinedQuarrySession";

function fixture(names:string[],material:THREE.Material){const scene=new THREE.Group();for(const name of names){const mesh=new THREE.Mesh(new THREE.BoxGeometry(),material);mesh.name=name;scene.add(mesh);}return{scene}as unknown as GLTF;}
test("two-section substitution retains all other quarry/tunnel nodes and borrows the exact shared material",()=>{
  const session=new RefinedQuarrySession(new ImmersiveRuntime("hub",()=>{},false)),material=new THREE.MeshStandardMaterial();
  session.asset=fixture(QUARRY.parts.flatMap(p=>p.nodes),material);session.refinement=fixture(REFINED_QUARRY.parts.flatMap(p=>p.nodes),material);
  const refined=session.cloneForRendering()!;
  for(const p of QUARRY.parts)for(const node of p.nodes)assert.equal(!!refined.getObjectByName(node),!REFINED_QUARRY.selectedParts.includes(p.id as number));
  for(const p of REFINED_QUARRY.parts)for(const name of p.nodes){const mesh=refined.getObjectByName(name)as THREE.Mesh;assert.equal(mesh.material,material);}
  assert.equal(refinementParts(true).length,QUARRY.parts.length-1);
  session.refinementEnabled=false;const baseline=session.cloneForRendering()!;
  for(const p of QUARRY.parts)for(const name of p.nodes)assert.ok(baseline.getObjectByName(name));
  session.dispose();
});
test("retiring the refinement cannot dispose borrowed limestone resources or an active candidate",()=>{
  const session=new RefinedQuarrySession(new ImmersiveRuntime("hub",()=>{},false)),material=new THREE.MeshStandardMaterial();let disposed=0;material.addEventListener("dispose",()=>disposed++);
  session.asset=fixture(QUARRY.parts.flatMap(p=>p.nodes),material);session.refinement=fixture(REFINED_QUARRY.parts.flatMap(p=>p.nodes),material);let geometryDisposed=0;session.refinement.scene.traverse(o=>{if(o instanceof THREE.Mesh)o.geometry.addEventListener("dispose",()=>geometryDisposed++);});
  assert.throws(()=>session.retireRefinement());session.refinementEnabled=false;session.state={...session.state,busy:false};session.retireRefinement();
  assert.equal(geometryDisposed,3);assert.equal(disposed,0);assert.ok(session.asset);assert.equal(session.refinement,null);session.dispose();assert.equal(disposed,1);
});
