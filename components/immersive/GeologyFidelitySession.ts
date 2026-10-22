import * as THREE from "three";
import {GLTFLoader, type GLTF} from "three/examples/jsm/loaders/GLTFLoader.js";
import fidelity from "@/public/models/gullyverse/quarry-fidelity-correction/manifest.json";
import {ScannedMaterialFidelitySession} from "./ScannedMaterialFidelitySession";
import type {ImmersiveRuntime} from "./runtime";

export const FIDELITY_GEOMETRY_URL = "/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb";
export const FIDELITY_NORMAL_URL = "/models/gullyverse/quarry-fidelity-correction/fidelity-bake.glb";

/** One local35.557m region borrows the preserved C5.1/C8 owners. Historical
 * recovered C9 is a separate comparison, never an additional loaded world. */
export class GeologyFidelitySession extends ScannedMaterialFidelitySession {
  compositionEnabled = true;
  compositionPreparing = true;
  compositionRevision = 0;
  private local: GLTF | null = null;
  private bake: GLTF | null = null;
  private geometryNormal: THREE.Texture | null = null;
  private bakedMaterial: THREE.MeshStandardMaterial | null = null;
  private geometryPending: Promise<void> | null = null;
  private operationPending: Promise<void> | null = null;
  private fidelityGeneration = 0;
  private fidelityRequest = 0;

  constructor(runtime: ImmersiveRuntime) { super(runtime); }

  setComposition = (enabled: boolean) => {
    this.compositionEnabled = enabled;
    this.compositionPreparing = true;
    this.fidelityRequest++;
    this.preparedLighting.clear();
    this.record("fidelity-request", {enabled, scale: 3});
    this.setScannedMaterial(true, 3);
  };

  private async geometry() {
    if (this.local && this.bake) return;
    if (this.geometryPending) return this.geometryPending;
    const generation = this.fidelityGeneration, start = performance.now();
    this.geometryPending = Promise.allSettled([
      new GLTFLoader().loadAsync(FIDELITY_GEOMETRY_URL),
      new GLTFLoader().loadAsync(FIDELITY_NORMAL_URL)
    ]).then(results => {
      if (results.some(result => result.status === "rejected")) {
        for (const result of results) if (result.status === "fulfilled")
          this.record("fidelity-unpublished-disposal", disposeLocal(result.value));
        throw new Error("Local fidelity geometry or normal failed");
      }
      const [local, bake] = results.map(result => (result as PromiseFulfilledResult<GLTF>).value);
      if (this.disposed || generation !== this.fidelityGeneration) {
        this.record("fidelity-abandoned-disposal", disposeLocal(local));
        this.record("fidelity-bake-abandoned-disposal", disposeLocal(bake));
        throw new Error("Fidelity owner retired during loading");
      }
      try {
        const names = new Set(fidelity.parts.flatMap(part => part.nodes));
        let count = 0;
        local.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          count++;
          if (!names.has(object.name) || !["normal", "uv", "uv1", "tangent"]
            .every(name => object.geometry.getAttribute(name))) throw new Error("Invalid fidelity mesh contract");
          for (const material of Array.isArray(object.material) ? object.material : [object.material])
            if (Object.values(material).some(value => value instanceof THREE.Texture))
              throw new Error("Fidelity geometry must not duplicate shared PBR maps");
        });
        if (count !== names.size) throw new Error("Incomplete fidelity LOD set");
        let normal: THREE.Texture | null = null;
        const images = new Set<unknown>();
        bake.scene.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
            if (material instanceof THREE.MeshStandardMaterial) normal = material.normalMap;
            for (const value of Object.values(material)) if (value instanceof THREE.Texture) images.add(value.image);
          }
        });
        const atlas = normal as THREE.Texture | null;
        if (!atlas || atlas.channel !== 1 || atlas.colorSpace !== THREE.NoColorSpace || images.size !== 1)
          throw new Error("Invalid fidelity normal atlas owner");
        this.geometryNormal = atlas;
      } catch (error) {
        this.record("fidelity-rejected-disposal", disposeLocal(local));
        this.record("fidelity-bake-rejected-disposal", disposeLocal(bake));
        throw error;
      }
      this.local = local;
      this.bake = bake;
      this.record("fidelity-local-ready", {ms: performance.now() - start,
        bytes: fidelity.runtimeBytes, newPBRImages: 0, regionMetres: fidelity.regionLengthM});
    }).finally(() => { this.geometryPending = null; });
    return this.geometryPending;
  }

  override async load() {
    if (this.disposed || this.state.mode === "off") return;
    if (this.operationPending) return this.operationPending;
    this.operationPending = (async () => {
      while (!this.disposed && this.state.mode !== "off") {
        const request = this.fidelityRequest;
        const [base, local] = await Promise.allSettled([
          super.load(), this.compositionEnabled ? this.geometry() : Promise.resolve()
        ]);
        if (this.disposed) return;
        if (request !== this.fidelityRequest) continue;
        if (base.status === "rejected") throw base.reason;
        let error = this.state.error;
        if (local.status === "rejected") {
          this.compositionEnabled = false;
          error = "Fidelity geometry unavailable; material-only 35.557m comparison retained. Retry is available.";
          this.record("fidelity-load-failed", {message: String(local.reason)});
        }
        this.compositionPreparing = false;
        this.compositionRevision++;
        this.publish({revision: this.state.revision + 1, error});
        break;
      }
    })().finally(() => { this.operationPending = null; });
    return this.operationPending;
  }

  override partsForRendering() {
    const parts = super.partsForRendering();
    if (!this.compositionEnabled || !this.local || !this.foundationEnabled || !this.scannedEnabled) return parts;
    // Visual partition only. World/collision/navigation registry is unchanged.
    return parts.filter(part => !["Wall_14", "Wall_16"].includes(String(part.id))).map(part => {
      const replacement = fidelity.parts.find(local => local.id === part.id);
      return replacement ? {...part, center: replacement.center, radius: replacement.radius} : part;
    });
  }

  override cloneForRendering() {
    const clone = super.cloneForRendering(), material = this.borrowScannedMaterial();
    if (clone && material && this.compositionEnabled && this.local && this.foundationEnabled && this.scannedEnabled) {
      if (!this.bakedMaterial && this.geometryNormal) {
        this.bakedMaterial = material.clone();
        this.bakedMaterial.name = "Fidelity_C8_3x_Geometry_Normal";
        this.bakedMaterial.normalMap = this.geometryNormal;
        this.bakedMaterial.normalScale.set(1, 1);
      }
      for (const part of fidelity.parts) for (const [level, name] of part.nodes.entries()) {
        const source = this.local.scene.getObjectByName(name);
        const target = clone.getObjectByName(`Foundation_${part.id}_LOD${level}`);
        if (!(source instanceof THREE.Mesh) || !(target instanceof THREE.Mesh)) throw new Error("Fidelity host missing");
        target.geometry = source.geometry;
        target.material = level > 0 && this.bakedMaterial ? this.bakedMaterial : material;
      }
      for (const id of ["Wall_14", "Wall_16"]) for (const level of [0, 1, 2])
        clone.getObjectByName(`Foundation_${id}_LOD${level}`)?.removeFromParent();
    }
    return clone;
  }

  compositionDiagnostics() {
    return {fidelityGeology: true, enabled: this.compositionEnabled, preparing: this.compositionPreparing,
      ready: !!this.local, revision: this.compositionRevision, sourceUniformScale: 0.9,
      additionalSourceUniformScales: fidelity.sourceModels.map(source => source.uniformScale),
      textureScale: this.textureScale, geometryURL: FIDELITY_GEOMETRY_URL,
      hostParts: fidelity.replacedHostParts, localGeometries: this.local ? 3 : 0,
      newPBRImages: 0, geometryNormalImages: this.geometryNormal ? 1 : 0,
      geometryNormal: this.geometryNormal ? {uuid: this.geometryNormal.uuid,
        source: this.geometryNormal.source.uuid, channel: this.geometryNormal.channel,
        repeat: this.geometryNormal.repeat.toArray(), width: this.geometryNormal.image.width,
        height: this.geometryNormal.image.height} : null,
      regionLengthMetres: fidelity.regionLengthM, LODs: fidelity.LODs, runtimeSHA256: fidelity.runtimeSHA256};
  }

  override materialDiagnostics() {
    const layer = super.materialDiagnostics();
    const active = this.compositionEnabled && !!this.local && this.foundationEnabled && this.scannedEnabled;
    return {...layer, materialLayerGeometryChanged: false, geometryChanged: active,
      host: active ? "fidelity visual region; unchanged authoritative collision registry" : layer.host,
      selectedNodes: active ? [0, 1, 2].map(level => `Foundation_Wall_15_LOD${level}`) : layer.selectedNodes};
  }

  private releaseLocal() {
    this.fidelityGeneration++;
    this.bakedMaterial?.dispose();
    this.bakedMaterial = null;
    if (this.local) this.record("fidelity-owner-disposal", disposeLocal(this.local));
    if (this.bake) this.record("fidelity-bake-owner-disposal", disposeLocal(this.bake));
    this.local = null; this.bake = null; this.geometryNormal = null;
  }
  override retire() { super.retire(); this.releaseLocal(); }
  override dispose() { this.releaseLocal(); super.dispose(); }
}

function disposeLocal(owner: GLTF) {
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
  geometry.forEach(item => item.dispose());
  textures.forEach(item => { if (item.image?.close) images.add(item.image); item.dispose(); });
  images.forEach(item => item.close());
  materials.forEach(item => item.dispose());
  return {geometries: geometry.size, materials: materials.size, textures: textures.size, images: images.size};
}
