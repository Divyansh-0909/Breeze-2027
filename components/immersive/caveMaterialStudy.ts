import * as THREE from 'three';
import {CaveEntranceSession} from './CaveEntranceSession';
import {CaveTextureSampling} from './caveTextureSampling';
import {installCaveLightResponse} from './caveLightResponse';
import type {ImmersiveRuntime} from './runtime';
import {GLTFLoader,type GLTF} from 'three/examples/jsm/loaders/GLTFLoader.js';
import pilotManifest from '@/public/models/gullyverse/cave-material-study/pilot-manifest.json';

export const CAVE_STUDY_MATERIALS = ['control','rock_01','rock_2','rock_3','worn_rock_natural_01',
  'rock_face_03','rock_face','dark_rock_02','quarry_wall','rock_05','ambientcg_Rock041'] as const;
export type CaveStudyMaterial = typeof CAVE_STUDY_MATERIALS[number];
export function caveStudyMaterial(value: string | null): CaveStudyMaterial {
  return CAVE_STUDY_MATERIALS.find(id => id === value) ?? 'control';
}
const period = 5.395311; // Current C8 primary source period, independently cave-local.
type Family = {id: CaveStudyMaterial; outside: THREE.MeshStandardMaterial; inside: THREE.MeshStandardMaterial;
  textures: THREE.Texture[]; images: ImageBitmap[]; sampling?: CaveTextureSampling};
function release(family: Family) {
  family.outside.dispose(); family.inside.dispose(); family.sampling?.dispose();
  new Set(family.textures).forEach(texture => texture.dispose());
  new Set(family.images).forEach(image => image.close());
}

/** One selected cave-only family, never a new quarry material owner. Previous
 * families retire only after covered preparation has replaced their consumers.
 * All material-only comparisons use the exact historical Stage3A geometry. */
export class CaveMaterialStudySession extends CaveEntranceSession {
  private selected: CaveStudyMaterial;
  private featureScale: 1 | 2;
  private studyFamily: Family | null = null;
  private retired: Family[] = [];
  private studyAbort: AbortController | null = null;
  private studyGeneration = 0;
  private studyPending: Promise<void> | null = null;
  private studyReady = false;
  private studyRevision = 0;
  private studyError: string | null = null;
  private pilotWanted = false;
  private pilotAsset: GLTF | null = null;
  private pilotPending: Promise<void> | null = null;
  private pilotFailed = false;
  private pilotGeneration = 0;
  override get entranceRevision() { return super.entranceRevision + this.studyRevision; }

  constructor(runtime: ImmersiveRuntime, material: CaveStudyMaterial = 'control', scale: 1 | 2 = 1, pilot = false) {
    super(runtime, 'stage3a');
    this.selected = material; this.featureScale = scale;
    this.pilotWanted = pilot;
  }
  override async load() {
    if (this.disposed || this.state.mode === 'off') return;
    // Preserve historical direct-stage deferral, rather than preparing an
    // invisible material comparison before playback can start.
    const visible = this.entranceDiagnostics().visibilityLoading.requested;
    const local = visible ? this.loadStudy() : Promise.resolve();
    await super.load();
    await local;
    if (visible && this.pilotWanted) await this.loadPilot();
    if (!this.disposed && visible && this.selected === 'control' && !this.studyFamily) this.adoptControl();
  }
  private async loadPilot() {
    if (this.pilotAsset || this.pilotFailed || this.disposed) return;
    if (this.pilotPending) return this.pilotPending;
    const generation = this.pilotGeneration;
    this.pilotPending = new GLTFLoader().loadAsync('/models/gullyverse/cave-material-study/emboss-pilot.glb').then(asset => {
      if (this.disposed || generation !== this.pilotGeneration) { disposePilot(asset); return; }
      const nodes: string[] = [];
      try {
        asset.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          nodes.push(object.name);
          if (!pilotManifest.replaceNodes.includes(object.name) || !['uv','normal','tangent','color'].every(key => object.geometry.getAttribute(key))) throw new Error('Invalid study pilot geometry contract');
          for (const material of Array.isArray(object.material) ? object.material : [object.material])
            if (Object.values(material).some(value => value instanceof THREE.Texture)) throw new Error('Pilot must not own PBR maps');
        });
        if (nodes.length !== 3) throw new Error('Incomplete pilot LODs');
      } catch (error) { disposePilot(asset); throw error; }
      this.pilotAsset = asset;
      this.record('cave-study-pilot-ready',{bytes:pilotManifest.runtimeBytes,sourceScale:.85,regionLengthM:9});
      if (this.pilotWanted) {this.studyRevision++;this.publish({revision:this.state.revision + 1,busy:true});}
    }).catch(error => {
      if (!this.disposed && generation === this.pilotGeneration) { this.pilotFailed=true;this.record('cave-study-pilot-failed',{error:String(error)});this.publish({revision:this.state.revision + 1}); }
    }).finally(() => { if(generation === this.pilotGeneration)this.pilotPending=null; });
    return this.pilotPending;
  }
  setStudyGeometry = (enabled: boolean) => {
    this.pilotWanted=enabled;this.studyRevision++;
    this.publish({revision:this.state.revision + 1,busy:true});
    if (enabled) void this.loadPilot();
  };
  private adoptControl() {
    const borrowed = super.borrowCaveMaterial();
    if (!borrowed || this.disposed) return;
    const outside = borrowed.clone(), sampling = new CaveTextureSampling();
    sampling.apply(outside, this.featureScale);
    const inside = outside.clone(); installCaveLightResponse(inside, this.caveLightResponse);
    this.adopt({id:'control',outside,inside,sampling,textures:[],images:[]});
  }
  private adopt(next: Family) {
    if (this.studyFamily) this.retired.push(this.studyFamily);
    this.studyFamily = next; this.studyReady = true; this.studyRevision++;
    this.record('cave-study-ready', {material:next.id,scale:this.featureScale,newImages:next.images.length,
      geometry:this.entranceURL,quarryScale:this.textureScale});
    this.publish({revision:this.state.revision + 1,busy:true});
  }
  private loadStudy(): Promise<void> {
    if (this.studyReady && this.studyFamily?.id === this.selected) return Promise.resolve();
    if (this.studyPending) return this.studyPending;
    if (this.selected === 'control') return Promise.resolve();
    const id = this.selected, generation = this.studyGeneration;
    const controller = this.studyAbort = new AbortController(), images: ImageBitmap[] = [], textures: THREE.Texture[] = [];
    this.studyPending = (async () => {
      try {
        const results = await Promise.allSettled(['basecolor.jpg','normal.png','orm.png'].map(async name => {
          const response = await fetch('/models/gullyverse/cave-material-study/' + id + '/' + name,{signal:controller.signal});
          if (!response.ok) throw new Error('Cave study map ' + response.status);
          const bitmap = await createImageBitmap(await response.blob(),{premultiplyAlpha:'none',imageOrientation:'none'});
          images.push(bitmap);
          const texture = new THREE.Texture(bitmap); textures.push(texture);
          texture.name = 'Cave_Study_' + id + '_' + name;
          texture.colorSpace = name === 'basecolor.jpg' ? THREE.SRGBColorSpace : THREE.NoColorSpace;
          texture.flipY = false; texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
          texture.repeat.set(2 / period / this.featureScale,2 / period * (id === 'ambientcg_Rock041' ? 2 : 1) / this.featureScale);
          texture.needsUpdate = true;
          return texture;
        }));
        if (results.some(row => row.status === 'rejected')) throw new Error('Selected cave material maps incomplete');
        if (this.disposed || generation !== this.studyGeneration || controller.signal.aborted) throw new Error('Study superseded');
        const [map,normalMap,orm] = results.map(row => (row as PromiseFulfilledResult<THREE.Texture>).value);
        const outside = new THREE.MeshStandardMaterial({name:'Cave_Study_'+id,map,normalMap,
          normalScale:new THREE.Vector2(.7,.7),roughnessMap:orm,metalnessMap:orm,metalness:0,
          roughness:1,vertexColors:true,side:THREE.FrontSide});
        const inside = outside.clone(); installCaveLightResponse(inside,this.caveLightResponse);
        this.studyError = null;
        this.adopt({id,outside,inside,textures,images});
      } catch (error) {
        new Set(textures).forEach(texture => texture.dispose());
        new Set(images).forEach(image => image.close());
        if (!this.disposed && generation === this.studyGeneration) {
          this.studyError = String(error); this.studyReady = true;
          this.record('cave-study-failed',{material:id,message:this.studyError,retained:'Baseline cave and C9'});
          this.publish({revision:this.state.revision + 1,busy:true});
        }
      } finally {
        if (generation === this.studyGeneration) this.studyPending = null;
      }
    })();
    return this.studyPending;
  }
  setStudySelection = (id: CaveStudyMaterial, scale: 1 | 2 = this.featureScale) => {
    this.runtime.clearInput();
    if (id === this.selected && this.studyReady && this.studyFamily?.id === id) {
      this.featureScale = scale;
      const family = this.studyFamily;
      if (family.sampling) {
        family.sampling.apply(family.outside,scale);
        for (const key of ['map','normalMap','roughnessMap','metalnessMap','aoMap'] as const) family.inside[key] = family.outside[key];
      } else for (const texture of family.textures) {
        texture.repeat.set(2 / period / scale,2 / period * (id === 'ambientcg_Rock041' ? 2 : 1) / scale); texture.updateMatrix();
      }
      this.record('cave-study-scale',{material:id,scale,quarryScale:this.textureScale});
      this.publish({revision:this.state.revision + 1,busy:true}); return;
    }
    this.studyGeneration++; this.studyAbort?.abort(); this.studyAbort = null; this.studyPending = null;
    this.selected = id; this.featureScale = scale; this.studyReady = false; this.studyError = null;
    if (id === 'control') this.adoptControl();
    this.publish({revision:this.state.revision + 1,busy:true}); void this.load();
  };
  override prepared(revision: number, ms: number, lighting: string) {
    if (this.entranceDiagnostics().visibilityLoading.requested && (!this.studyReady || this.studyPending || this.pilotWanted && (this.pilotPending || !this.pilotAsset && !this.pilotFailed))) return;
    super.prepared(revision,ms,lighting);
    if (!this.state.busy) { this.retired.forEach(release); this.retired = []; }
  }
  override borrowCaveMaterial() { return this.studyFamily?.outside ?? super.borrowCaveMaterial(); }
  override cloneEntrance() {
    const clone = super.cloneEntrance(), family = this.studyFamily;
    if (clone && family) clone.traverse(object => {
      if (!(object instanceof THREE.Mesh) || object.name.startsWith('Cave_Floor_')) return;
      object.material = /^Cave_(Throat|Passage)/.test(object.name) ? family.inside : family.outside;
    });
    if (clone && this.pilotWanted && this.pilotAsset) for (const name of pilotManifest.replaceNodes) {
      const target=clone.getObjectByName(name),source=this.pilotAsset.scene.getObjectByName(name);
      if (target instanceof THREE.Mesh && source instanceof THREE.Mesh) target.geometry=source.geometry;
    }
    return clone;
  }
  studyDiagnostics() {
    return {selected:this.selected,featureScale:this.featureScale,ready:this.studyReady,error:this.studyError,
      active:this.studyFamily?.id ?? null,geometryMode:this.pilotWanted && this.pilotAsset?'pilot':'baseline',geometryURL:this.entranceURL,
      pilot:{requested:this.pilotWanted,ready:!!this.pilotAsset,failed:this.pilotFailed,bytes:pilotManifest.runtimeBytes,sha256:pilotManifest.runtimeSHA256,sourceScale:.85,regionLengthM:9},
      geometrySHA256:this.descriptor.runtimeSHA256,quarrySamplerScale:this.textureScale,
      studySourceImages:this.studyFamily?.images.length ?? 0,retiredFamilies:this.retired.length,
      textureWrappers:this.studyFamily?.textures.length ?? 0,decodedRGBA8MipEstimateBytes:
        this.studyFamily?.images.reduce((sum,image)=>sum+image.width*image.height*4*4/3,0) ?? 0,
      maps:this.studyFamily?.textures.map(texture=>({name:texture.name,uuid:texture.uuid,source:texture.source.uuid,
        repeat:texture.repeat.toArray(),channel:texture.channel,colorSpace:texture.colorSpace,flipY:texture.flipY})),
      publicDefaultChanged:false,newDynamicLights:0};
  }
  private releaseStudy() {
    this.studyGeneration++; this.studyAbort?.abort(); this.studyAbort=null; this.studyPending=null;
    if (this.studyFamily) release(this.studyFamily); this.studyFamily=null;
    this.retired.forEach(release); this.retired=[]; this.studyReady=false;
    this.pilotGeneration++;this.pilotPending=null;
    if (this.pilotAsset) disposePilot(this.pilotAsset);this.pilotAsset=null;this.pilotFailed=false;
  }
  override retire() {
    if (this.state.mode !== 'off' || this.state.busy || this.consumers) throw new Error('Retire study only after inactive covered restore');
    this.releaseStudy(); super.retire();
  }
  override dispose() { this.releaseStudy(); super.dispose(); }
}
function disposePilot(asset: GLTF) {
  const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>();
  asset.scene.traverse(object=>{if(object instanceof THREE.Mesh){geometries.add(object.geometry);for(const material of Array.isArray(object.material)?object.material:[object.material])materials.add(material);}});
  const textures=new Set<THREE.Texture>(),images=new Set<ImageBitmap>();
  for(const material of materials)for(const value of Object.values(material))if(value instanceof THREE.Texture){textures.add(value);if(value.image?.close)images.add(value.image);}
  geometries.forEach(geometry=>geometry.dispose());materials.forEach(material=>material.dispose());
  textures.forEach(texture=>texture.dispose());images.forEach(image=>image.close());
}
