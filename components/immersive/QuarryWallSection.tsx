"use client";
import {useEffect,useLayoutEffect,useMemo,useRef,useSyncExternalStore} from "react";
import {useFrame,useThree} from "@react-three/fiber";
import * as THREE from "three";
import {chooseWallLOD,originalWallFace,projectedWallPixels,wallTransform,CORRECTED_WALL,type WallPreviewSession} from "./wallSection";

export default function QuarryWallSection({session,quality,lighting}:{session:WallPreviewSession;quality:number;lighting:string}) {
  const state=useSyncExternalStore(session.subscribe,session.snapshot,session.snapshot),{gl,scene,camera}=useThree();
  const asset=session.asset;
  const clone=useMemo(()=>asset?.scene.clone(true)??null,[asset]);
  const lods=useMemo(()=>clone?[0,1,2].map(i=>clone.getObjectByName(`Wall_LOD${i}`) as THREE.Object3D):[],[clone]);
  const material=useMemo(()=>{let result:THREE.Material|undefined;lods[0]?.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.name.startsWith("Approved_Cool_Grey_Limestone_Family"))result=m;});return result;},[lods]);
  const face=useMemo(()=>state.mode==="reference"?originalWallFace():null,[state.mode]);
  useEffect(()=>()=>face?.dispose(),[face]);
  const transform=useMemo(wallTransform,[]);
  const detailSphere=useMemo(()=>{if(session.variant==="corrected")return new THREE.Sphere(new THREE.Vector3().fromArray(CORRECTED_WALL.detailSphere.center),CORRECTED_WALL.detailSphere.radius);if(lods[0] instanceof THREE.Mesh){lods[0].geometry.computeBoundingSphere();return lods[0].geometry.boundingSphere!.clone();}return new THREE.Sphere(new THREE.Vector3(),13);},[lods,session.variant]);
  const radius=detailSphere.radius,center=useMemo(()=>detailSphere.center.clone().applyQuaternion(transform.quaternion).add(transform.position),[detailSphere,transform]);
  const current=useRef(2),warming=useRef({compiled:false,frames:0,start:0,revision:0}),size=useRef(new THREE.Vector2());
  useLayoutEffect(()=>{
    if(clone)clone.traverse(o=>{if(o instanceof THREE.Mesh){o.visible=!o.name.includes("Collision");o.castShadow=false;o.receiveShadow=false;o.frustumCulled=true;}});
    lods.forEach((o,i)=>{o.visible=i===2;});
    if(state.mode!=="off"&&clone){session.retainConsumer();return()=>{session.releaseConsumer();};}
  },[clone,lods,state.mode,session]);
  useEffect(()=>{
    if(!state.busy&&state.mode!=="off"&&!session.preparedLighting.has(lighting))session.setMode(state.mode);
  },[session,state.busy,state.mode,lighting]);
  useEffect(()=>{
    const restore=()=>{session.preparedLighting.clear();session.setMode(session.state.mode);};
    gl.domElement.addEventListener("webglcontextrestored",restore);return()=>gl.domElement.removeEventListener("webglcontextrestored",restore);
  },[gl,session]);
  useEffect(()=>{
    if(!state.busy||(state.mode!=="off"&&!clone))return;
    let alive=true;const revision=state.revision,start=performance.now();warming.current={compiled:false,frames:0,start,revision};
    void(async()=>{
      if(gl.getContext().isContextLost())return;
      const textures=new Set<THREE.Texture>();if(material&&state.mode!=="off")for(const value of Object.values(material))if(value instanceof THREE.Texture)textures.add(value);
      const at=performance.now();textures.forEach(t=>gl.initTexture(t));session.record("texture-init",{ms:performance.now()-at,count:textures.size});
      const compile=performance.now();await gl.compileAsync(scene,camera);session.record("shader-compile",{ms:performance.now()-compile});
      if(alive&&revision===session.state.revision&&!gl.getContext().isContextLost())warming.current.compiled=true;
    })().catch(e=>{if(alive){session.record("preparation-error",{message:String(e)});session.setMode("off");}});
    return()=>{alive=false;};
  },[session,state.busy,state.revision,state.mode,clone,gl,scene,camera,material,lighting]);
  useFrame(()=>{
    if(session.runtime.suspended||gl.getContext().isContextLost())return;
    const warm=warming.current;
    if(session.state.busy) {
      if(!warm.compiled||warm.revision!==session.state.revision)return;
      // Sequentially upload every visual LOD beneath cover. Never overlapping visible copies.
      if(state.mode==="authored")lods.forEach((mesh,i)=>{mesh.visible=i===Math.min(2,warm.frames);mesh.traverse(o=>{if(o instanceof THREE.Mesh)o.frustumCulled=false;});});
      gl.render(scene,camera);warm.frames++;
      if(warm.frames>=(state.mode==="authored"?7:state.mode==="reference"?2:1)){lods.forEach((mesh,i)=>{mesh.visible=i===2;mesh.traverse(o=>{if(o instanceof THREE.Mesh)o.frustumCulled=true;});});current.current=2;session.prepared(warm.revision,performance.now()-warm.start,lighting);}
      return;
    }
    if(state.mode!=="authored"||!clone||!(camera instanceof THREE.PerspectiveCamera))return;
    camera.updateMatrixWorld(true);gl.getDrawingBufferSize(size.current);const pixels=projectedWallPixels(center,radius,camera,size.current.y),next=chooseWallLOD(pixels,quality,current.current);
    if(next!==current.current){session.record("lod-change",{from:current.current,to:next,pixels,quality,dpr:gl.getPixelRatio(),camera:camera.position.toArray()});current.current=next;}
    lods.forEach((mesh,i)=>{mesh.visible=i===current.current;});
    clone.userData.activeLOD=current.current;clone.userData.projectedPixels=pixels;
    session.activeLOD=current.current;session.projectedPixels=pixels;
    const label=gl.domElement.closest("section")?.querySelector("[data-wall-lod]");if(label&&label.textContent!==`LOD ${current.current}`)label.textContent=`LOD ${current.current}`;
  },0);
  if(state.mode==="off"||!clone)return null;
  if(state.mode==="reference")return <mesh name="Wall_Material_Reference" material={material} dispose={null}><primitive attach="geometry" object={face!} dispose={null}/></mesh>;
  return <group name="Integrated_Limestone_Wall" position={transform.position} quaternion={transform.quaternion}><primitive object={clone} dispose={null}/></group>;
}
