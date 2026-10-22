import * as THREE from 'three';
import {GLTFLoader, type GLTF} from 'three/examples/jsm/loaders/GLTFLoader.js';
import manifest from '@/public/models/gullyverse/c9-cave-recovery/manifest.json';
import deepManifest from '@/public/models/gullyverse/c9-cave-deep-relief/manifest.json';
import entry from '@/public/models/gullyverse/c9-cave-recovery/entry-clearance.json';
import {GeologyFidelitySession} from './GeologyFidelitySession';
import type {ImmersiveRuntime} from './runtime';
import {installCaveLightResponse} from './caveLightResponse';
import {CaveTextureSampling} from './caveTextureSampling';

export const CAVE_ENTRANCE_URL = '/models/gullyverse/c9-cave-recovery/cave-entrance.glb';
export const CAVE_ENTRY_CLEARANCE_URL = '/models/gullyverse/c9-cave-recovery/entry-clearance.glb';
export const CAVE_DEEP_RELIEF_URL = '/models/gullyverse/c9-cave-deep-relief/cave-deep-pilot.glb';
/** A private local visual owner. The selected C9 owner and material are inherited
 * unchanged. This cache owns geometry/placeholder materials only, never PBR maps. */
export class CaveEntranceSession extends GeologyFidelitySession {
  private entrance: GLTF | null = null;
  private clearance: GLTF | null = null;
  private entrancePending: Promise<void> | null = null;
  private entranceGeneration = 0;
  private entranceFailed = false;
  private caveRequested = false;
  private entranceMaterial: THREE.MeshStandardMaterial | null = null;
  private floorMaterial: THREE.MeshStandardMaterial | null = null;
  private innerMaterial: THREE.MeshStandardMaterial | null = null;
  readonly caveLightResponse = {value: 1};
  private readonly caveSampling = new CaveTextureSampling();
  private caveFeatureScale: 1 | 2;
  readonly descriptor: Pick<typeof manifest, 'parts' | 'runtimeBytes' | 'runtimeSHA256' | 'source' | 'interiorStatus'>;
  readonly entranceURL: string;
  get entranceParts() { return this.descriptor.parts; }
  entranceRoot: WeakRef<THREE.Object3D> | null = null;
  get entranceReady() { return !!this.entrance; }
  constructor(runtime: ImmersiveRuntime, readonly edition: 'stage3a' | 'stage3a1' = 'stage3a') {
    super(runtime);
    this.descriptor = edition === 'stage3a1' ? deepManifest : manifest;
    this.entranceURL = edition === 'stage3a1' ? CAVE_DEEP_RELIEF_URL : CAVE_ENTRANCE_URL;
    this.caveFeatureScale = edition === 'stage3a1' ? 2 : 1;
    // Direct stage entry has no cave pixels. Preserve its existing cold-start
    // budget; landing/hub still prepare the complete cave before revealing it.
    this.caveRequested = runtime.getSnapshot().scene !== 'aftermovie';
  }
  requireCave = () => {
    if (this.caveRequested || this.disposed || this.state.mode === 'off') return;
    this.caveRequested = true;
    this.record('cave-visibility-request', {scene: this.runtime.getSnapshot().scene});
    this.setMode('authored');
  };
  override prepared(revision: number, ms: number, lighting: string) {
    if (this.state.mode !== 'off' && this.caveRequested && !this.entrance && !this.entranceFailed) return;
    super.prepared(revision, ms, lighting);
  }

  private async loadEntrance() {
    if (this.entrance || this.entranceFailed || this.disposed) return;
    if (this.entrancePending) return this.entrancePending;
    const generation = this.entranceGeneration, at = performance.now();
    this.entrancePending = new GLTFLoader().loadAsync(this.entranceURL).then(async asset => {
      if (this.disposed || generation !== this.entranceGeneration) { this.record('cave-abandoned-disposal', disposeGeometry(asset)); return; }
      let clearance: GLTF | null = null;
      try {
        const expected = new Set(this.descriptor.parts.flatMap(part => part.nodes));
        let count = 0;
        asset.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          count++;
          if (!expected.has(object.name) || !['normal', 'uv', 'tangent', 'color'].every(key => object.geometry.getAttribute(key)))
            throw new Error('Invalid cave geometry/UV/tangent/colour contract');
          for (const material of Array.isArray(object.material) ? object.material : [object.material])
            if (Object.values(material).some(value => value instanceof THREE.Texture))
              throw new Error('Cave geometry must not embed duplicate shared PBR images');
        });
        if (count !== expected.size) throw new Error('Incomplete cave LOD set');
        clearance = await new GLTFLoader().loadAsync(CAVE_ENTRY_CLEARANCE_URL);
        let terrainCount = 0;
        clearance.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          terrainCount++;
          if (!entry.runtimeNodes.includes(object.name) || !['normal', 'uv', 'tangent', 'color'].every(key => object.geometry.getAttribute(key)))
            throw new Error('Invalid local entrance-clearance geometry contract');
          for (const material of Array.isArray(object.material) ? object.material : [object.material])
            if (Object.values(material).some(value => value instanceof THREE.Texture)) throw new Error('Unexpected clearance texture owner');
        });
        if (terrainCount !== entry.runtimeNodes.length) throw new Error('Incomplete local clearance LOD set');
        if (this.disposed || generation !== this.entranceGeneration) {
          this.record('cave-abandoned-disposal', disposeGeometry(asset));
          this.record('cave-clearance-abandoned-disposal', disposeGeometry(clearance)); return;
        }
        this.entrance = asset;
        this.clearance = clearance;
        if (this.state.mode !== 'off') this.publish({revision: this.state.revision + 1, busy: true});
        this.record('cave-entrance-ready', {ms: performance.now() - at, bytes: this.descriptor.runtimeBytes,
          textureScale: 3, tunnelFeatureScale: this.caveFeatureScale, newImages: 0, runtimeSHA256: this.descriptor.runtimeSHA256});
      } catch (error) {
        this.record('cave-rejected-disposal', disposeGeometry(asset));
        if (clearance) this.record('cave-clearance-rejected-disposal', disposeGeometry(clearance));
        throw error;
      }
    }).catch(error => {
      if (generation !== this.entranceGeneration || this.disposed) return;
      this.entranceFailed = true;
      this.record('cave-entrance-failed', {message: String(error), retained: 'original functional entrance'});
      this.publish({revision: this.state.revision + 1});
    }).finally(() => { this.entrancePending = null; });
    return this.entrancePending;
  }
  override async load() {
    if (this.disposed || this.state.mode === 'off') return;
    if (!this.caveRequested) { await super.load(); return; }
    const generation = this.entranceGeneration;
    await this.loadEntrance();
    if (!this.disposed && generation === this.entranceGeneration) await super.load();
  }
  retryEntrance = () => { this.entranceFailed = false; this.setMode('authored'); };

  override cloneForRendering() {
    const clone = super.cloneForRendering();
    if (clone && this.entrance && this.clearance) for (let index = 0; index < entry.targetNodes.length; index++) {
      const target = clone.getObjectByName(entry.targetNodes[index]);
      const source = this.clearance.scene.getObjectByName(entry.runtimeNodes[index]);
      if (!(target instanceof THREE.Mesh) || !(source instanceof THREE.Mesh)) throw new Error('Private entry-clearance host missing');
      target.geometry = source.geometry;
    }
    return clone;
  }

  cloneEntrance() {
    const material = this.borrowCaveMaterial();
    if (!this.entrance || !material) return null;
    const clone = this.entrance.scene.clone(true);
    clone.traverse(object => {
      if (!(object instanceof THREE.Mesh)) return;
      object.material = object.name.startsWith('Cave_Floor_') ? this.borrowFloorMaterial() ?? material :
        /^Cave_(Throat|Passage)/.test(object.name) ? this.borrowInnerMaterial() ?? material : material;
      object.castShadow = object.receiveShadow = false;
      object.frustumCulled = true;
    });
    this.entranceRoot = new WeakRef(clone);
    return clone;
  }

  borrowCaveMaterial() {
    const borrowed = this.borrowScannedMaterial();
    if (!borrowed) return null;
    if (!this.entranceMaterial) {
      this.entranceMaterial = borrowed.clone();
      this.entranceMaterial.name = 'Cave_Borrowed_C8_3x';
      this.entranceMaterial.side = THREE.FrontSide;
      this.entranceMaterial.vertexColors = true;
    }
    return this.entranceMaterial;
  }
  private borrowFloorMaterial() {
    if (this.floorMaterial) return this.floorMaterial;
    const terrain = this.asset?.scene.getObjectByName('Foundation_Terrain_1_2_LOD0');
    const source = terrain instanceof THREE.Mesh && !Array.isArray(terrain.material) ? terrain.material : null;
    if (!(source instanceof THREE.MeshStandardMaterial)) return null;
    this.floorMaterial = source.clone();
    this.floorMaterial.name = 'Cave_Borrowed_Existing_Dry_Terrain';
    this.floorMaterial.side = THREE.FrontSide;
    this.floorMaterial.vertexColors = true;
    this.floorMaterial.transparent = true;
    this.floorMaterial.depthWrite = false;
    installCaveLightResponse(this.floorMaterial, this.caveLightResponse);
    return this.floorMaterial;
  }
  private borrowInnerMaterial() {
    const source = this.borrowCaveMaterial();
    if (!source) return null;
    if (!this.innerMaterial) {
      this.innerMaterial = source.clone();
      this.innerMaterial.name = this.edition === 'stage3a1' ? 'Cave_Local_2x_Enclosed_Stone' : 'Cave_Borrowed_C8_3x_Enclosed_Stone';
      if (this.edition === 'stage3a1') this.caveSampling.apply(this.innerMaterial, this.caveFeatureScale);
      installCaveLightResponse(this.innerMaterial, this.caveLightResponse);
    }
    return this.innerMaterial;
  }
  /** Development comparison changes only these scene-owned sampler wrappers. */
  setCaveTextureFeatureScale(scale: 1 | 2) {
    if (this.edition !== 'stage3a1') return;
    this.caveFeatureScale = scale;
    if (this.innerMaterial) this.caveSampling.apply(this.innerMaterial, scale);
    this.record('cave-local-texture-scale', {scale, quarryScaleUnchanged: this.textureScale});
  }
  entranceDiagnostics() {
    return {ready: this.entranceReady, failed: this.entranceFailed, bytes: this.descriptor.runtimeBytes,
      runtimeSHA256: this.descriptor.runtimeSHA256, parts: this.descriptor.parts, source: this.descriptor.source,
      edition: this.edition, tunnelTextureFeatureScale: this.caveFeatureScale,
      localTextureSampling: this.edition === 'stage3a1' ? this.caveSampling.diagnostics() : null,
      approvedTextureScale: this.textureScale, newImages: 0, visibleFixtures: 0,
      visibilityLoading: {requested: this.caveRequested, deferredWhileOffscreen: !this.caveRequested,
        policy: 'Direct stage defers local cave until first hub/map; existing preparation cover gates adoption'},
      localTerrainClearance: this.clearance ? entry : null,
      lighting: {newDynamicLights: 0, visibleFixtures: 0, globalLightingChanged: false,
        localOpeningResponse: this.caveLightResponse.value, method: 'Analytical local overburden/spill proxy, not baked GI'},
      completeStage3A: false, interiorStatus: this.descriptor.interiorStatus};
  }
  private releaseEntrance() {
    this.entranceGeneration++;
    this.entranceMaterial?.dispose(); this.entranceMaterial = null;
    this.floorMaterial?.dispose(); this.floorMaterial = null;
    this.innerMaterial?.dispose(); this.innerMaterial = null;
    this.caveSampling.dispose();
    if (this.entrance) this.record('cave-owner-disposal', disposeGeometry(this.entrance));
    if (this.clearance) this.record('cave-clearance-disposal', disposeGeometry(this.clearance));
    this.clearance = null;
    this.entrance = null; this.entranceFailed = false; this.entranceRoot = null;
  }
  override retire() {
    if (this.state.mode !== 'off' || this.state.busy || this.consumers)
      throw new Error('Unmount cave consumers and finish covered restore before retirement');
    this.releaseEntrance(); super.retire();
  }
  override dispose() { this.releaseEntrance(); super.dispose(); }
}
function disposeGeometry(owner: GLTF) {
  const geometry = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>(), images = new Set<ImageBitmap>();
  owner.scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    geometry.add(object.geometry);
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      materials.add(material);
      for (const value of Object.values(material)) if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  geometry.forEach(item => item.dispose()); materials.forEach(item => item.dispose());
  // Valid geometry has no images. Rejected malformed payloads still own their
  // unexpected images; rendered clones never replace this owner's materials.
  textures.forEach(texture => { if (texture.image?.close) images.add(texture.image); texture.dispose(); });
  images.forEach(item => item.close());
  return {geometries: geometry.size, materials: materials.size, textures: textures.size, images: images.size};
}
