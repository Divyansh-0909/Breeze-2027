import * as THREE from "three";
import {GLTFLoader, type GLTF} from "three/examples/jsm/loaders/GLTFLoader.js";
import composition from "@/public/models/gullyverse/recovered-c9-composition/manifest.json";
import {ScannedRockMaterialSession} from "./ScannedRockMaterialSession";
import type {ImmersiveRuntime} from "./runtime";

export const RECOVERED_C9_URL = "/models/gullyverse/recovered-c9-composition/composition-region.glb";
export const RECOVERED_C9_BAKE_URL = "/models/gullyverse/recovered-c9-composition/composition-bake.glb";

/** Local geometry only. Scene clones borrow the existing foundation and C8
 * image owners. No full-world copy or source-resolution scan reaches visitors. */
export class ScannedCompositionSession extends ScannedRockMaterialSession {
  compositionEnabled = true;
  compositionPreparing = true;
  compositionRevision = 0;
  private localGeometry: GLTF | null = null;
  private localBake: GLTF | null = null;
  private geometryNormal: THREE.Texture | null = null;
  private bakedMaterial: THREE.MeshStandardMaterial | null = null;
  private geometryPending: Promise<void> | null = null;
  private compositionOperation: Promise<void> | null = null;
  private compositionGeneration = 0;
  private compositionRequest = 0;
  constructor(runtime: ImmersiveRuntime) { super(runtime, 3); }

  setComposition = (enabled: boolean) => {
    this.compositionEnabled = enabled; this.compositionPreparing = true; this.compositionRequest++;
    this.preparedLighting.clear();
    this.record("scanned-composition-request", {enabled, uniformScale: 0.9, textureScale: 3});
    this.setScannedMaterial(true, 3);
  };

  private async getLocalGeometry() {
    if (this.localGeometry && this.localBake) return;
    if (this.geometryPending) return this.geometryPending;
    const generation = this.compositionGeneration, start = performance.now();
    this.geometryPending = Promise.allSettled([
      new GLTFLoader().loadAsync(RECOVERED_C9_URL), new GLTFLoader().loadAsync(RECOVERED_C9_BAKE_URL)
    ]).then(results => {
      if (results.some(result => result.status === "rejected")) {
        results.forEach(result => { if (result.status === "fulfilled") this.record("composition-unpublished-disposal", disposeLocal(result.value)); });
        throw new Error("C9 geometry or geometric normal failed to load");
      }
      const [owner, bake] = results.map(result => (result as PromiseFulfilledResult<GLTF>).value);
      if (this.disposed || generation !== this.compositionGeneration) {
        this.record("composition-abandoned-disposal", disposeLocal(owner));
        this.record("composition-bake-abandoned-disposal", disposeLocal(bake));
        throw new Error("C9 owner retired during loading");
      }
      try {
        const expected = new Set(composition.parts.flatMap(part => part.nodes)); let count = 0;
        owner.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return; count++;
          if (!expected.has(object.name) || !["uv", "uv1", "normal", "tangent"].every(name => object.geometry.getAttribute(name)))
            throw new Error("Invalid C9 geometry/UV/tangent contract");
          for (const material of Array.isArray(object.material) ? object.material : [object.material])
            if (Object.values(material).some(value => value instanceof THREE.Texture))
              throw new Error("C9 local geometry must not duplicate shared PBR images");
        });
        if (count !== expected.size) throw new Error("Incomplete C9 local LOD set");
        let normal: THREE.Texture | null = null;
        const images = new Set<unknown>();
        bake.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
            if (material instanceof THREE.MeshStandardMaterial) normal = material.normalMap;
            for (const value of Object.values(material)) if (value instanceof THREE.Texture) images.add(value.image);
          }
        });
        // Geometry UV1 is never rescaled with the approved UV0 PBR maps.
        const bakedNormal = normal as THREE.Texture | null;
        if (!bakedNormal || images.size !== 1 || bakedNormal.channel !== 1 ||
            bakedNormal.colorSpace !== THREE.NoColorSpace) throw new Error("Invalid C9 geometry-normal owner");
        this.geometryNormal = bakedNormal;
      } catch (error) {
        this.record("composition-rejected-disposal", disposeLocal(owner));
        this.record("composition-bake-rejected-disposal", disposeLocal(bake)); throw error;
      }
      this.localGeometry = owner; this.localBake = bake;
      this.record("scanned-composition-ready", {ms: performance.now() - start,
        geometryBytes: composition.runtimeBytes, sourceUniformScale: 0.9, newPBRImages: 0,
        host: composition.hostPart, geometryNormalImages: 1, completeWorldCopies: 0});
    }).finally(() => { this.geometryPending = null; });
    return this.geometryPending;
  }

  override async load() {
    if (this.disposed || this.state.mode === "off") return;
    if (this.compositionOperation) return this.compositionOperation;
    this.compositionOperation = (async () => {
      while (!this.disposed && this.state.mode !== "off") {
        const request = this.compositionRequest; this.textureScale = 3;
        const [base, local] = await Promise.allSettled([
          super.load(), this.compositionEnabled ? this.getLocalGeometry() : Promise.resolve()
        ]);
        if (this.disposed) return;
        if (request !== this.compositionRequest) continue;
        if (base.status === "rejected") throw base.reason;
        let error = this.state.error;
        if (local.status === "rejected") {
          this.compositionEnabled = false;
          error = "C9 geometry unavailable; recovered C8 3× retained. Retry is available.";
          this.record("scanned-composition-load-failed", {message: String(local.reason)});
        }
        this.compositionPreparing = false; this.compositionRevision++;
        this.publish({revision: this.state.revision + 1, error}); break;
      }
    })().finally(() => { this.compositionOperation = null; });
    return this.compositionOperation;
  }

  override partsForRendering() {
    const parts = super.partsForRendering();
    if (!this.compositionEnabled || !this.localGeometry || !this.foundationEnabled || !this.scannedEnabled) return parts;
    return parts.map(part => {
      const replacement = composition.parts.find(local => local.id === part.id);
      return replacement ? {...part, center: replacement.center, radius: replacement.radius} : part;
    });
  }

  override cloneForRendering() {
    const clone = super.cloneForRendering(), material = this.borrowScannedMaterial();
    if (clone && material && this.foundationEnabled && this.scannedEnabled && this.compositionEnabled && this.localGeometry) {
      if (!this.bakedMaterial && this.geometryNormal) {
        this.bakedMaterial = material.clone();
        this.bakedMaterial.name = "Recovered_C9_C8_3x_Geometry_Normal";
        this.bakedMaterial.normalMap = this.geometryNormal;
        this.bakedMaterial.normalScale.set(1, 1);
      }
      for (const part of composition.parts) for (const [level, name] of part.nodes.entries()) {
        const source = this.localGeometry.scene.getObjectByName(name);
        const target = clone.getObjectByName(`Foundation_${part.id}_LOD${level}`);
        if (!(source instanceof THREE.Mesh) || !(target instanceof THREE.Mesh)) throw new Error("C9 host interface missing");
        target.geometry = source.geometry; target.material = level > 0 && this.bakedMaterial ? this.bakedMaterial : material;
      }
    }
    return clone;
  }

  compositionDiagnostics() {
    return {enabled: this.compositionEnabled, preparing: this.compositionPreparing,
      ready: !!this.localGeometry, revision: this.compositionRevision, sourceUniformScale: 0.9,
      textureScale: this.textureScale, geometryURL: RECOVERED_C9_URL, hostPart: composition.hostPart,
      localGeometries: this.localGeometry ? composition.parts.reduce((n, p) => n + p.nodes.length, 0) : 0,
      newPBRImages: 0, geometryNormalImages: this.geometryNormal ? 1 : 0,
      geometryNormal: this.geometryNormal ? {uuid: this.geometryNormal.uuid, source: this.geometryNormal.source.uuid,
        channel: this.geometryNormal.channel, repeat: this.geometryNormal.repeat.toArray(), width: this.geometryNormal.image.width,
        height: this.geometryNormal.image.height} : null,
      LODs: composition.LODs, runtimeSHA256: composition.runtimeSHA256};
  }
  private releaseComposition() {
    this.compositionGeneration++;
    this.bakedMaterial?.dispose(); this.bakedMaterial = null;
    if (this.localGeometry) this.record("scanned-composition-owner-disposal", disposeLocal(this.localGeometry));
    if (this.localBake) this.record("scanned-composition-bake-owner-disposal", disposeLocal(this.localBake));
    this.localGeometry = null; this.localBake = null; this.geometryNormal = null;
  }
  override retire() { super.retire(); this.releaseComposition(); }
  override dispose() { this.releaseComposition(); super.dispose(); }
}

function disposeLocal(owner: GLTF) {
  const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>(), images = new Set<ImageBitmap>();
  owner.scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return; geometries.add(object.geometry);
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      materials.add(material);
      for (const value of Object.values(material)) if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  geometries.forEach(geometry => geometry.dispose());
  textures.forEach(texture => { if (texture.image?.close) images.add(texture.image); texture.dispose(); });
  images.forEach(image => image.close()); materials.forEach(material => material.dispose());
  return {geometries: geometries.size, materials: materials.size, textures: textures.size, images: images.size};
}
