"use client";
import {useEffect,useLayoutEffect,useMemo,useRef,useSyncExternalStore} from "react";
import {useFrame,useThree} from "@react-three/fiber";
import * as THREE from "three";
import {chooseWallLOD,projectedWallPixels,QUARRY,type WallPreviewSession} from "./wallSection";
import {RefinedQuarrySession,refinementParts} from "./RefinedQuarrySession";
import {LimestoneExcavationSession} from "./LimestoneExcavationSession";

/** Shared approved material; one screen-space LOD per fitted quarry part. */
export default function QuarryPerimeter({session,quality,lighting}:{session:WallPreviewSession;quality:number;lighting:string}) {
  const state=useSyncExternalStore(session.subscribe,session.snapshot,session.snapshot),{gl,scene,camera}=useThree();
  const refined=session instanceof RefinedQuarrySession?session:null;
  const excavation=session instanceof LimestoneExcavationSession?session:null;
  const enabled=!!refined?.refinementEnabled&&!!refined.refinement;
  const clone=useMemo(()=>excavation?excavation.cloneForRendering():refined?refined.cloneForRendering():session.asset?.scene.clone(true)??null,[session.asset,excavation,refined,refined?.refinement,enabled]);
  const parts=useMemo(()=>clone?(excavation?excavation.partsForRendering():refined?refinementParts(enabled):QUARRY.parts).map(part=>({id:String(part.id),center:new THREE.Vector3().fromArray(part.center),radius:part.radius,lods:part.nodes.map(name=>clone.getObjectByName(name) as THREE.Mesh),level:2})):[],[clone,enabled,refined,excavation]);
  const size=useRef(new THREE.Vector2()),warm=useRef({compiled:false,frames:0,revision:0,start:0});
  useLayoutEffect(()=>{
    if(clone)clone.traverse(o=>{if(o instanceof THREE.Mesh){o.visible=o.name!=="Wall_Collision";o.castShadow=false;o.receiveShadow=false;o.frustumCulled=true;}});
    parts.forEach(part=>part.lods.forEach((o,i)=>{o.visible=i===2;}));
    if(state.mode!=="off"&&clone){session.retainConsumer();return()=>session.releaseConsumer();}
  },[clone,parts,state.mode,session]);
  useEffect(()=>{if(!state.busy&&state.mode!=="off"&&!session.preparedLighting.has(lighting))session.setMode(state.mode);},[lighting,session,state.busy,state.mode]);
  useEffect(()=>{
    const restored=()=>{session.preparedLighting.clear();session.setMode(session.state.mode);};
    gl.domElement.addEventListener("webglcontextrestored",restored);return()=>gl.domElement.removeEventListener("webglcontextrestored",restored);
  },[gl,session]);
  useEffect(()=>{
    if(!state.busy||(state.mode!=="off"&&(!clone||refined?.refinementEnabled&&!refined.refinement)))return;
    let alive=true;const revision=state.revision;warm.current={compiled:false,frames:0,revision,start:performance.now()};
    void(async()=>{
      if(gl.getContext().isContextLost())return;
      const textures=new Set<THREE.Texture>();if(state.mode!=="off"&&clone)clone.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])for(const v of Object.values(m))if(v instanceof THREE.Texture)textures.add(v);});
      const at=performance.now();textures.forEach(t=>gl.initTexture(t));session.record("texture-init",{count:textures.size,ms:performance.now()-at});
      const compile=performance.now();await gl.compileAsync(scene,camera);session.record("shader-compile",{ms:performance.now()-compile});
      if(alive&&revision===session.state.revision&&!gl.getContext().isContextLost())warm.current.compiled=true;
    })().catch(error=>{if(alive){session.record("preparation-error",{message:String(error)});session.setMode("off");}});
    return()=>{alive=false;};
  },[clone,gl,scene,camera,session,state.busy,state.mode,state.revision,lighting,refined]);
  useFrame(()=>{
    if(session.runtime.suspended||gl.getContext().isContextLost())return;
    const w=warm.current;
    if(session.state.busy){
      if(!w.compiled||w.revision!==session.state.revision)return;
      if(state.mode!=="off")parts.forEach(part=>part.lods.forEach((mesh,i)=>{mesh.visible=i===Math.min(2,w.frames);mesh.frustumCulled=false;}));
      gl.render(scene,camera);w.frames++;
      if(w.frames>=(state.mode==="off"?1:4)){
        parts.forEach(part=>{part.level=2;part.lods.forEach((mesh,i)=>{mesh.visible=i===2;mesh.frustumCulled=true;});});
        session.prepared(w.revision,performance.now()-w.start,lighting);
      }
      return;
    }
    if(state.mode==="off"||!clone||!(camera instanceof THREE.PerspectiveCamera))return;
    camera.updateMatrixWorld(true);gl.getDrawingBufferSize(size.current);
    for(const part of parts){
      const pixels=projectedWallPixels(part.center,part.radius,camera,size.current.y),next=chooseWallLOD(pixels,quality,part.level);
      if(next!==part.level){session.record("part-lod-change",{part:part.id,from:part.level,to:next,pixels,quality,dpr:gl.getPixelRatio()});part.level=next;}
      part.lods.forEach((mesh,i)=>{mesh.visible=i===next;});session.lodSelections[part.id]=next;session.lodPixels[part.id]=pixels;
    }
  },0);
  if(state.mode==="off"||!clone)return null;
  return <group name="Authored_Limestone_Quarry"><primitive object={clone} dispose={null}/></group>;
}
