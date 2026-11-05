import * as THREE from 'three';
import {CaveEntranceSession} from './CaveEntranceSession';
import {CaveTextureSampling} from './caveTextureSampling';
import {installCaveLightResponse} from './caveLightResponse';
import type {ImmersiveRuntime} from './runtime';

export const CANAL_MATERIALS = ['control','cracked_concrete_wall','concrete_wall_006','worn_plaster_wall',
  'plastered_stone_wall','plaster_stone_wall_02','rock_embedded_concrete_wall',
  'concrete_wall_008','scuffed_cement','chipped_concrete','quarry_wall'] as const;
export type CanalMaterial = typeof CANAL_MATERIALS[number];
export function canalMaterial(value: string | null): CanalMaterial {
  return CANAL_MATERIALS.find(id => id === value) ?? 'control';
}
// Existing entrance projection islands were authored at 8 / approvedUVRepeat.
// Fit 128 whole tiles to that offset, so both 1× and 2× preserve chart phase.
// This changes only cave-local map transforms, never vertices or the C8 sampler.
export const CANAL_CHART_PERIOD_UV = 129.487464;
export const CANAL_TILE_PERIOD_M = 2 * CANAL_CHART_PERIOD_UV / 128;
const period = CANAL_TILE_PERIOD_M;
type Family = {id: CanalMaterial; outside: THREE.MeshStandardMaterial; inside: THREE.MeshStandardMaterial;
  textures: THREE.Texture[]; images: ImageBitmap[]; sampling?: CaveTextureSampling};
function release(family: Family) {
  family.outside.dispose(); family.inside.dispose(); family.sampling?.dispose();
  new Set(family.textures).forEach(texture => texture.dispose());
  new Set(family.images).forEach(image => image.close());
}

/** Private material-only canal comparison. No geometry replacement exists.
 * One selected cave-only family, never a new quarry material owner. Previous
 * families retire only after covered preparation has replaced their consumers.
 * All material-only comparisons use the exact historical Stage3A geometry. */
export class CanalMaterialSession extends CaveEntranceSession {
  private selected: CanalMaterial;
  private featureScale: 1 | 2;
  private studyFamily: Family | null = null;
  private retired: Family[] = [];
  private studyAbort: AbortController | null = null;
  private studyGeneration = 0;
  private studyPending: Promise<void> | null = null;
  private studyReady = false;
  private studyRevision = 0;
  private studyError: string | null = null;
  override get entranceRevision() { return super.entranceRevision + this.studyRevision; }

  constructor(runtime: ImmersiveRuntime, material: CanalMaterial = 'control', scale: 1 | 2 = 1) {
    super(runtime, 'stage3a');
    this.selected = material; this.featureScale = scale;
  }
  override async load() {
    if (this.disposed || this.state.mode === 'off') return;
    // Preserve historical direct-stage deferral, rather than preparing an
    // invisible material comparison before playback can start.
    const visible = this.entranceDiagnostics().visibilityLoading.requested;
    const local = visible ? this.loadStudy() : Promise.resolve();
    await super.load();
    await local;
    if (!this.disposed && visible && this.selected === 'control' && !this.studyFamily) this.adoptControl();
  }
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
    this.record('canal-study-ready', {material:next.id,scale:this.featureScale,newImages:next.images.length,
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
          const response = await fetch('/models/gullyverse/canal-material-study/' + id + '/' + name,{signal:controller.signal});
          if (!response.ok) throw new Error('Cave study map ' + response.status);
          const bitmap = await createImageBitmap(await response.blob(),{premultiplyAlpha:'none',imageOrientation:'none'});
          images.push(bitmap);
          const texture = new THREE.Texture(bitmap); textures.push(texture);
          texture.name = 'Canal_Study_' + id + '_' + name;
          texture.colorSpace = name === 'basecolor.jpg' ? THREE.SRGBColorSpace : THREE.NoColorSpace;
          texture.flipY = false; texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
          texture.repeat.set(2 / period / this.featureScale,2 / period / this.featureScale);
          texture.needsUpdate = true;
          return texture;
        }));
        if (results.some(row => row.status === 'rejected')) throw new Error('Selected cave material maps incomplete');
        if (this.disposed || generation !== this.studyGeneration || controller.signal.aborted) throw new Error('Study superseded');
        const [map,normalMap,orm] = results.map(row => (row as PromiseFulfilledResult<THREE.Texture>).value);
        const outside = new THREE.MeshStandardMaterial({name:'Canal_Study_'+id,map,normalMap,
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
          this.record('canal-study-failed',{material:id,message:this.studyError,retained:'Baseline cave and C9'});
          this.publish({revision:this.state.revision + 1,busy:true});
        }
      } finally {
        if (generation === this.studyGeneration) this.studyPending = null;
      }
    })();
    return this.studyPending;
  }
  setStudySelection = (id: CanalMaterial, scale: 1 | 2 = this.featureScale) => {
    this.runtime.clearInput();
    if (id === this.selected && this.studyReady && this.studyFamily?.id === id) {
      this.featureScale = scale;
      const family = this.studyFamily;
      if (family.sampling) {
        family.sampling.apply(family.outside,scale);
        for (const key of ['map','normalMap','roughnessMap','metalnessMap','aoMap'] as const) family.inside[key] = family.outside[key];
      } else for (const texture of family.textures) {
        texture.repeat.set(2 / period / scale,2 / period / scale); texture.updateMatrix();
      }
      this.studyRevision++;
      this.record('canal-study-scale',{material:id,scale,quarryScale:this.textureScale});
      this.publish({revision:this.state.revision + 1,busy:true}); return;
    }
    this.studyGeneration++; this.studyAbort?.abort(); this.studyAbort = null; this.studyPending = null;
    this.selected = id; this.featureScale = scale; this.studyReady = false; this.studyError = null;
    if (id === 'control') this.adoptControl();
    this.publish({revision:this.state.revision + 1,busy:true}); void this.load();
  };
  override prepared(revision: number, ms: number, lighting: string) {
    if (this.entranceDiagnostics().visibilityLoading.requested && (!this.studyReady || this.studyPending)) return;
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
    return clone;
  }
  studyDiagnostics() {
    return {selected:this.selected,featureScale:this.featureScale,ready:this.studyReady,error:this.studyError,
      active:this.studyFamily?.id ?? null,geometryMode:'baseline',geometryURL:this.entranceURL,
      comparisonTilePeriodM: this.selected === 'control' ? null : period * this.featureScale, hostUVMetresPerUnit:2,
      baselineSamplingUnchanged:this.selected==='control',
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
  }
  override retire() {
    if (this.state.mode !== 'off' || this.state.busy || this.consumers) throw new Error('Retire study only after inactive covered restore');
    this.releaseStudy(); super.retire();
  }
  override dispose() { this.releaseStudy(); super.dispose(); }
}
