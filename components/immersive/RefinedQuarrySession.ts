import * as THREE from "three";
import {GLTFLoader,type GLTF} from "three/examples/jsm/loaders/GLTFLoader.js";
import manifest from "@/public/models/gullyverse/quarry-refinement/manifest.json";
import {WallPreviewSession,QUARRY} from "./wallSection";
import type {ImmersiveRuntime} from "./runtime";

export const REFINED_QUARRY=manifest;
export const REFINED_QUARRY_URL="/models/gullyverse/quarry-refinement/refined-pair.glb";
const replaced=new Set<number>(manifest.selectedParts);
export function refinementParts(enabled:boolean){return enabled?[...QUARRY.parts.filter(p=>typeof p.id!=="number"||!replaced.has(p.id)),...manifest.parts]:QUARRY.parts;}
function disposeGeometry(gltf:GLTF){const geometries=new Set<THREE.BufferGeometry>();gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh)geometries.add(o.geometry);});geometries.forEach(g=>g.dispose());return{geometries:geometries.size};}

/** Opt-in geometry-only proof. Its material is borrowed from the Stage 2C owner.
 * Baseline meshes/cache survive toggles. No stage resources or textures evicted.
 */
export class RefinedQuarrySession extends WallPreviewSession {
  refinement:GLTF|null=null;
  refinementEnabled=true;
  private refinementPending:Promise<void>|null=null;
  private refinementGeneration=0;
  constructor(runtime:ImmersiveRuntime){super(runtime,"authored","quarry");}
  setRefinement=(enabled:boolean)=>{
    this.refinementEnabled=enabled;this.preparedLighting.clear();this.record("refinement-request",{enabled});this.setMode("authored");
  };
  override async load(){
    await super.load();
    if(!this.asset||this.disposed||!this.refinementEnabled||this.state.mode==="off"||this.refinement)return;
    if(this.refinementPending){await this.refinementPending;return;}
    const generation=this.refinementGeneration,start=performance.now();this.record("refinement-load-start");
    const loader=new GLTFLoader(),parse=loader.parse.bind(loader);
    loader.parse=(data,path,onLoad,onError)=>{const at=performance.now();parse(data,path,gltf=>{this.record("refinement-parse-ready",{ms:performance.now()-at,bytes:typeof data==="string"?data.length:data.byteLength});onLoad(gltf);},onError);};
    this.refinementPending=loader.loadAsync(REFINED_QUARRY_URL).then(gltf=>{
      // The GLB has only a placeholder material, no image/texture payload.
      // Dispose that owner before rebinding to the exact cached baseline family.
      const placeholders=new Set<THREE.Material>();gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh)for(const m of Array.isArray(o.material)?o.material:[o.material])placeholders.add(m);});
      placeholders.forEach(m=>m.dispose());
      if(this.disposed||generation!==this.refinementGeneration){this.record("refinement-abandoned-disposal",disposeGeometry(gltf));return;}
      let shared:THREE.Material|undefined;this.asset!.scene.traverse(o=>{if(o instanceof THREE.Mesh){const m=Array.isArray(o.material)?o.material[0]:o.material;if(m.name===manifest.material)shared=m;}});
      if(!shared||!manifest.parts.flatMap(p=>p.nodes).every(name=>gltf.scene.getObjectByName(name))){disposeGeometry(gltf);throw new Error("Refined quarry nodes or shared limestone material missing");}
      gltf.scene.traverse(o=>{if(o instanceof THREE.Mesh)o.material=shared!;});
      this.refinement=gltf;this.record("refinement-load-ready",{ms:performance.now()-start,geometryOnly:true});this.publish({assetReady:true,revision:this.state.revision+1});
    }).catch(error=>{
      if(!this.disposed){this.record("refinement-load-failed",{message:String(error)});this.refinementEnabled=false;this.setMode("authored");this.publish({error:String(error)});}
    }).finally(()=>{this.refinementPending=null;});
    await this.refinementPending;
  }
  cloneForRendering(){
    if(!this.asset)return null;
    const clone=this.asset.scene.clone(true);
    if(this.refinementEnabled&&this.refinement){
      for(const part of QUARRY.parts)if(typeof part.id==="number"&&replaced.has(part.id))for(const name of part.nodes)clone.getObjectByName(name)?.removeFromParent();
      clone.add(this.refinement.scene.clone(true));
    }
    return clone;
  }
  retireRefinement(){
    if(this.refinementEnabled||this.state.busy)throw new Error("Finish the covered Stage 2C restore before retiring refinement geometry");
    this.refinementGeneration++;
    if(this.refinement){this.record("refinement-cache-disposal",disposeGeometry(this.refinement));this.refinement=null;}
  }
  override retire(){
    super.retire();this.refinementGeneration++;
    if(this.refinement){this.record("refinement-cache-disposal",disposeGeometry(this.refinement));this.refinement=null;}
  }
  override dispose(){
    this.refinementGeneration++;
    if(this.refinement){this.record("refinement-owner-disposal",disposeGeometry(this.refinement));this.refinement=null;}
    super.dispose();
  }
}
