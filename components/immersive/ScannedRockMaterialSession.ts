import * as THREE from "three";
import {GLTFLoader, type GLTF} from "three/examples/jsm/loaders/GLTFLoader.js";
import materialManifest from "@/public/models/gullyverse/recovered-c8-material/manifest.json";
import {QuarryFoundationSession} from "./QuarryFoundationSession";
import {ScannedRockSampling, type RockTextureScale} from "./scannedRockSampling";
import type {ImmersiveRuntime} from "./runtime";

export const RECOVERED_C8_MATERIAL_URL = "/models/gullyverse/recovered-c8-material/scanned-materials.glb";

/** Material-only recovery. C5.1 owns every wall vertex and its original family.
 * Private clones borrow this separate three-image owner on one existing sector.
 * No C6.2 fitting, new wall mesh, collider or full-world asset is introduced. */
export class ScannedRockMaterialSession extends QuarryFoundationSession {
  scannedEnabled = true;
  textureScale: RockTextureScale;
  materialRevision = 0;
  materialPreparing = true;
  private family: GLTF | null = null;
  private material: THREE.MeshStandardMaterial | null = null;
  private familyPending: Promise<void> | null = null;
  private operation: Promise<void> | null = null;
  private familyGeneration = 0;
  private requestGeneration = 0;
  private sampling = new ScannedRockSampling();

  constructor(runtime: ImmersiveRuntime, scale: RockTextureScale = 3) {
    super(runtime, true);
    this.textureScale = scale;
  }

  setScannedMaterial = (enabled: boolean, scale: RockTextureScale = 3) => {
    this.scannedEnabled = enabled;
    this.textureScale = scale;
    this.requestGeneration++;
    this.materialPreparing = true;
    this.preparedLighting.clear();
    this.record("scanned-material-request", {enabled, scale});
    this.setMode("authored");
  };

  private async loadFamily() {
    if (this.family) return;
    if (this.familyPending) return this.familyPending;
    const generation = this.familyGeneration, start = performance.now();
    this.familyPending = new GLTFLoader().loadAsync(RECOVERED_C8_MATERIAL_URL).then(owner => {
      if (this.disposed || generation !== this.familyGeneration) {
        this.record("scanned-material-abandoned-disposal", disposeFamily(owner));
        throw new Error("Scanned material owner retired during loading");
      }
      let selected: THREE.MeshStandardMaterial | undefined;
      owner.scene.traverse(object => {
        if (object instanceof THREE.Mesh) for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
          if (material.name === materialManifest.material && material instanceof THREE.MeshStandardMaterial) selected = material;
        }
      });
      if (!selected?.map || !selected.normalMap || !selected.roughnessMap || !selected.aoMap ||
          selected.map.colorSpace !== THREE.SRGBColorSpace || selected.normalMap.colorSpace !== THREE.NoColorSpace ||
          selected.roughnessMap.colorSpace !== THREE.NoColorSpace) {
        this.record("scanned-material-rejected-disposal", disposeFamily(owner));
        throw new Error("Scanned material map/colour-space contract is incomplete");
      }
      // The historical C8 holder did not use vertex colour. Keep the public
      // C5.1 vertex-colour material and geometry unchanged in their own owner.
      selected.vertexColors = false;
      selected.metalness = 0;
      selected.normalScale.set(0.7, 0.7);
      this.family = owner;
      this.material = selected;
      this.record("scanned-material-ready", {ms: performance.now() - start,
        uniqueRuntimeImages: 3, holderRendered: false, geometryOwner: "unchanged C5.1"});
    }).finally(() => { this.familyPending = null; });
    return this.familyPending;
  }

  override async load() {
    if (this.disposed || this.state.mode === "off") return;
    if (this.operation) return this.operation;
    this.operation = (async () => {
      while (!this.disposed && this.state.mode !== "off") {
        const request = this.requestGeneration;
        let materialError: string | null = null;
        // These owners are independent. Do not serialize the C5.1 world behind
        // the extra material download/decode. materialPreparing keeps the
        // borrowed clone covered until BOTH owners are ready.
        const [foundationResult, materialResult] = await Promise.allSettled([
          super.load(), this.scannedEnabled ? this.loadFamily() : Promise.resolve()
        ]);
        if (this.disposed) return;
        if (request !== this.requestGeneration) continue;
        if (foundationResult.status === "rejected") throw foundationResult.reason;
        if (materialResult.status === "rejected") {
          this.scannedEnabled = false;
          materialError = "Scanned material unavailable; unchanged C5.1 retained. Retry is available.";
          this.record("scanned-material-load-failed", {message: String(materialResult.reason)});
        }
        if (request !== this.requestGeneration) continue;
        if (this.material) this.sampling.apply(this.material, this.textureScale);
        // Parent fallback setters re-enter load(). Drain their finite fallback
        // chain here: returning the in-flight operation must not swallow the
        // request for the retained connected shell or its original baseline.
        for (let fallback = 0; fallback < 2 && !this.asset && this.snapshot().mode !== "off"; fallback++) {
          await super.load();
          if (this.disposed || this.asset || this.snapshot().mode === "off" || request !== this.requestGeneration) break;
        }
        if (this.disposed) return;
        if (request !== this.requestGeneration) continue;
        this.materialPreparing = false;
        this.materialRevision++;
        this.publish({revision: this.state.revision + 1, error: materialError ?? this.state.error});
        break;
      }
    })().finally(() => { this.operation = null; });
    return this.operation;
  }

  override cloneForRendering() {
    const clone = super.cloneForRendering();
    if (clone && this.foundationEnabled && this.scannedEnabled && this.material) {
      for (const name of materialManifest.selectedNodes) {
        const object = clone.getObjectByName(name);
        if (!(object instanceof THREE.Mesh)) throw new Error("C5.1 material host is missing: " + name);
        object.material = this.material;
      }
    }
    return clone;
  }

  /** Future local C9 geometry may borrow the same material while this scene
   * owner is leased. Borrowers never dispose it or its shared images. */
  borrowScannedMaterial() { return this.material; }

  materialDiagnostics() {
    const maps = new Set(this.material ? [this.material.map, this.material.normalMap,
      this.material.roughnessMap, this.material.metalnessMap, this.material.aoMap]
      .filter((texture): texture is THREE.Texture => !!texture) : []);
    const images = new Set([...maps].map(texture => texture.image));
    return {enabled: this.scannedEnabled, scale: this.textureScale, preparing: this.materialPreparing,
      geometryChanged: false, host: "C5.1", selectedNodes: materialManifest.selectedNodes,
      material: this.material?.name, normalScale: this.material?.normalScale.toArray(),
      uniqueImages: images.size, wrappers: maps.size,
      decodedRGBA8MipBytes: [...images].reduce((bytes, image) => bytes + image.width * image.height * 4 * 4 / 3, 0),
      textures: [...maps].map(texture => ({uuid: texture.uuid, source: texture.source.uuid,
        channel: texture.channel, repeat: texture.repeat.toArray(), offset: texture.offset.toArray(),
        rotation: texture.rotation, colourSpace: texture.colorSpace,
        width: texture.image.width, height: texture.image.height}))};
  }

  private releaseFamily() {
    this.familyGeneration++;
    if (this.family) this.record("scanned-material-owner-disposal", disposeFamily(this.family));
    this.family = null;
    this.material = null;
    this.sampling = new ScannedRockSampling();
  }

  override retire() {
    super.retire();
    this.releaseFamily();
  }

  override dispose() {
    this.releaseFamily();
    super.dispose();
  }
}

function disposeFamily(owner: GLTF) {
  const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>();
  const textures = new Set<THREE.Texture>(), images = new Set<ImageBitmap>();
  owner.scene.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    geometries.add(object.geometry);
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      materials.add(material);
      for (const value of Object.values(material)) if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  for (const geometry of geometries) geometry.dispose();
  for (const texture of textures) {
    if (texture.image?.close) images.add(texture.image);
    texture.dispose();
  }
  for (const image of images) image.close();
  for (const material of materials) material.dispose();
  return {geometries: geometries.size, materials: materials.size, textures: textures.size, images: images.size};
}
