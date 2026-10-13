import * as THREE from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import manifest from "@/public/models/gullyverse/first-wall-section/manifest.json";
import correctedManifest from "@/public/models/gullyverse/first-wall-corrected/manifest.json";
import quarryManifest from "@/public/models/gullyverse/quarry-rollout/manifest.json";
import { quarryGeometry } from "./blockoutGeometry";
import {currentQuarryConnectionFits} from "./quarryRollout";
import type { ImmersiveRuntime } from "./runtime";

export const WALL_URL = "/models/gullyverse/first-wall-corrected/first-wall-corrected.glb";
export const PREVIOUS_WALL_URL = "/models/gullyverse/first-wall-section/first-wall-section.glb";
export const QUARRY_URL = "/models/gullyverse/quarry-rollout/quarry-limestone.glb";
export const QUARRY = quarryManifest;
export const CORRECTED_WALL = correctedManifest;
export type WallVariant = "corrected" | "previous" | "quarry";
export type WallReplacement = "face" | "volume" | null;
export const WALL = manifest;
export type WallMode = "off" | "reference" | "authored";
export function wallTransform() {
  const basis = new THREE.Matrix4().makeBasis(new THREE.Vector3().fromArray(WALL.uAxis), new THREE.Vector3().fromArray(WALL.vAxis), new THREE.Vector3().fromArray(WALL.normal));
  return { position: new THREE.Vector3().fromArray(WALL.anchor), quaternion: new THREE.Quaternion().setFromRotationMatrix(basis) };
}
/** Copy only; original generator and all other triangles are preserved byte for byte. */
export function quarryWithoutWallFace(replacement:WallReplacement="face") {
  const original = quarryGeometry(), result = new THREE.BufferGeometry();
  const ranges=replacement==="volume"?[CORRECTED_WALL.hostRange,...CORRECTED_WALL.joinRanges].sort((a,b)=>a.start-b.start):[{start:WALL.vertexStart,count:WALL.vertexCount}];
  for (const [name, attribute] of Object.entries(original.attributes)) {
    const n = attribute.itemSize, data = attribute.array as Float32Array, kept:number[]=[];let cursor=0;
    for(const {start,count} of ranges){kept.push(...data.slice(cursor*n,start*n));cursor=start+count;}
    kept.push(...data.slice(cursor*n));result.setAttribute(name,new THREE.BufferAttribute(new Float32Array(kept),n));
  }
  result.computeBoundingBox(); result.computeBoundingSphere(); original.dispose(); return result;
}
export function currentWallAnchorFits(variant:WallVariant="corrected") {
  const geometry=quarryGeometry(),positions=geometry.getAttribute("position");
  if(variant==="quarry") {
    const fits=positions.count===QUARRY.parts.filter(p=>typeof p.id==="number").length*108&&QUARRY.parts.every(part=>{
      if(typeof part.id!=="number"||!("sourceCorners" in part))return true;
      const start=(part.id-2)*108;
      return part.sourceCorners.every(p=>Array.from({length:108},(_,i)=>new THREE.Vector3().fromBufferAttribute(positions,start+i)).some(q=>q.distanceTo(new THREE.Vector3().fromArray(p))<2e-5));
    });
    geometry.dispose();return fits&&currentQuarryConnectionFits();
  }
  const points=Array.from({length:WALL.vertexCount},(_,i)=>new THREE.Vector3().fromBufferAttribute(positions,WALL.vertexStart+i));
  const wholePoints=Array.from({length:CORRECTED_WALL.hostRange.count},(_,i)=>new THREE.Vector3().fromBufferAttribute(positions,CORRECTED_WALL.hostRange.start+i));
  const joinFits=CORRECTED_WALL.joiningContacts.every(join=>{const points=join.sourceRanges.flatMap(({start,count})=>Array.from({length:count},(_,i)=>new THREE.Vector3().fromBufferAttribute(positions,start+i)));const ids=new Set(join.selectedFaces.flatMap(face=>join.faces[face]));return [...ids].every(i=>points.some(p=>p.distanceTo(new THREE.Vector3().fromArray(join.vertices[i]))<2e-5));});
  const hostFits=variant==="previous"||(joinFits&&CORRECTED_WALL.hostVerticesWorld.every(p=>wholePoints.some(q=>q.distanceTo(new THREE.Vector3().fromArray(p))<2e-5)));
  const fits=hostFits&&WALL.boundaryWorld.every(p=>points.some(q=>q.distanceTo(new THREE.Vector3().fromArray(p))<2e-5));geometry.dispose();return fits;
}
export function originalWallFace() {
  const original = quarryGeometry(), result = new THREE.BufferGeometry(), transform = wallTransform();
  const data = original.getAttribute("position"), positions: number[] = [], uv: number[] = [], fineUV:number[]=[], normals: number[] = [];
  for (let i=WALL.vertexStart;i<WALL.vertexStart+WALL.vertexCount;i++) {
    const p = new THREE.Vector3().fromBufferAttribute(data,i); positions.push(...p.toArray());
    p.sub(transform.position).applyQuaternion(transform.quaternion.clone().invert());
    const lowX = Math.min(...WALL.boundaryLocal.map(p=>p[0])), highX = Math.max(...WALL.boundaryLocal.map(p=>p[0]));
    const lowY = Math.min(...WALL.boundaryLocal.map(p=>p[1])), highY = Math.max(...WALL.boundaryLocal.map(p=>p[1]));
    uv.push((p.x-lowX)/(highX-lowX),(p.y-lowY)/(highY-lowY));fineUV.push((p.x+6)/12,(p.y+5)/10); normals.push(...WALL.normal);
  }
  result.setAttribute("position", new THREE.Float32BufferAttribute(positions,3)); result.setAttribute("normal",new THREE.Float32BufferAttribute(normals,3)); result.setAttribute("uv",new THREE.Float32BufferAttribute(uv,2)); result.setAttribute("uv1",new THREE.Float32BufferAttribute(fineUV,2));result.computeBoundingSphere(); original.dispose(); return result;
}
export function chooseWallLOD(pixels: number, quality: number, previous: number): number {
  if (!Number.isFinite(pixels) || pixels<=0) return 2;
  const factor = quality>=2?1.5:quality===1?1.15:1;
  const near=720*factor, middle=220*factor;
  if (previous===0 && pixels>=near*.78) return 0;
  if (pixels>=near) return 0;
  if (previous===1 && pixels>=middle*.72) return 1;
  return pixels>=middle?1:2;
}
export function projectedWallPixels(center:THREE.Vector3,radius:number,camera:THREE.PerspectiveCamera,height:number) {
  const view=center.clone().applyMatrix4(camera.matrixWorldInverse), forward=-view.z;
  if (!Number.isFinite(forward)||!Number.isFinite(radius)||forward<-radius||height<=0) return 0;
  const value=radius*height/(Math.tan(THREE.MathUtils.degToRad(camera.fov)*.5)*Math.max(camera.near,forward));
  return Number.isFinite(value)?value:0;
}
function disposeAsset(gltf:GLTF) {
  const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>(),textures=new Set<THREE.Texture>(),bitmaps=new Set<ImageBitmap>();
  gltf.scene.traverse(o=>{if(!(o instanceof THREE.Mesh))return;geometries.add(o.geometry);for(const m of Array.isArray(o.material)?o.material:[o.material]){materials.add(m);for(const v of Object.values(m))if(v instanceof THREE.Texture)textures.add(v);}});
  textures.forEach(t=>{if(t.image?.close)bitmaps.add(t.image);t.dispose();});bitmaps.forEach(b=>b.close());materials.forEach(m=>m.dispose());geometries.forEach(g=>g.dispose());
  return {geometries:geometries.size,materials:materials.size,textures:textures.size,imageBitmaps:bitmaps.size};
}
export type WallState = { mode:WallMode; busy:boolean; assetReady:boolean; revision:number; error:string|null };
/** One bounded, explicitly owned optional asset cache per immersive shell. No shared-stage eviction. */
export class WallPreviewSession {
  asset:GLTF|null=null; consumers=0; disposed=false; private pending:Promise<void>|null=null;
  private ownerLeases=0;
  private cacheGeneration=0;
  activeLOD=2; projectedPixels=0;
  lodSelections:Record<string,number>={};
  lodPixels:Record<string,number>={};
  preparedLighting=new Set<string>();
  private listeners=new Set<()=>void>();
  state:WallState;
  trace:{at:number;event:string;[key:string]:unknown}[]=[];
  constructor(public runtime:ImmersiveRuntime,mode:WallMode,public variant:WallVariant="corrected") {this.state={mode,busy:true,assetReady:false,revision:0,error:null};}
  subscribe=(fn:()=>void)=>{this.listeners.add(fn);return()=>this.listeners.delete(fn);};
  snapshot=()=>this.state;
  record(event:string,data:Record<string,unknown>={}) {this.trace.push({at:performance.now(),event,...data});if(this.trace.length>2000)this.trace.splice(0,200);}
  protected publish(p:Partial<WallState>) {if(this.disposed)return;this.state={...this.state,...p};this.listeners.forEach(f=>f());}
  setMode=(mode:WallMode)=>{this.runtime.clearInput();this.publish({mode,busy:true,revision:this.state.revision+1,error:null});this.record("mode-request",{mode});if(mode!=="off")void this.load();};
  async load() {
    if(this.asset||this.pending||this.disposed)return;
    if(!currentWallAnchorFits(this.variant)){this.publish({mode:"off",busy:true,error:"Wall anchor no longer matches current quarry; original retained",revision:this.state.revision+1});return;}
    const at=performance.now(),generation=this.cacheGeneration;this.record("load-start");
    const loader=new GLTFLoader(),parse=loader.parse.bind(loader);
    loader.parse=(data,path,onLoad,onError)=>{const start=performance.now();parse(data,path,gltf=>{this.record("parse-ready",{ms:performance.now()-start,decodedBytes:typeof data==="string"?data.length:data.byteLength});onLoad(gltf);},onError);};
    this.pending=loader.loadAsync(this.variant==="quarry"?QUARRY_URL:this.variant==="previous"?PREVIOUS_WALL_URL:WALL_URL).then(gltf=>{
      if(this.disposed||generation!==this.cacheGeneration){this.record("abandoned-load-disposal",disposeAsset(gltf));return;}
      const required=[...(this.variant==="quarry"?["Quarry_LOD0","Quarry_LOD1","Quarry_LOD2",...QUARRY.parts.flatMap(p=>p.nodes)]:["Wall_LOD0","Wall_LOD1","Wall_LOD2"]),"Wall_Collision"];
      if(!required.every(name=>gltf.scene.getObjectByName(name))){disposeAsset(gltf);throw new Error("Wall asset has invalid named nodes");}
      this.asset=gltf;this.record("load-ready",{ms:performance.now()-at});this.publish({assetReady:true});
    }).catch(error=>{if(!this.disposed){this.record("load-failed",{message:String(error)});this.publish({mode:"off",busy:true,error:String(error),revision:this.state.revision+1});}}).finally(()=>{this.pending=null;if(!this.disposed&&generation!==this.cacheGeneration&&this.state.mode!=="off")void this.load();});
    await this.pending;
  }
  prepared(revision:number,ms:number,lighting:string) {if(revision!==this.state.revision||this.disposed)return;this.preparedLighting.add(lighting);this.record("covered-ready",{revision,ms,lighting});this.publish({busy:false});}
  retainOwner(){this.ownerLeases++;}
  releaseOwner(){this.ownerLeases--;this.collect();}
  retainConsumer(){this.consumers++;}
  releaseConsumer(){this.consumers--;this.collect();}
  private collect(){queueMicrotask(()=>{if(!this.ownerLeases&&!this.consumers&&!this.disposed)this.dispose();});}
  retire() {
    if(this.state.mode!=="off"||this.state.busy||this.consumers)throw new Error("Unmount all wall consumers and finish covered restore before retiring its cache");
    this.cacheGeneration++;this.preparedLighting.clear();
    if(this.asset){this.record("cache-disposal",disposeAsset(this.asset));this.asset=null;this.publish({assetReady:false});}
  }
  dispose() {this.disposed=true;if(this.asset){this.record("owner-disposal",disposeAsset(this.asset));this.asset=null;}this.listeners.clear();}
}
declare global {interface Window {__wallPreview?:WallPreviewSession}}
