import * as THREE from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import manifest from "@/public/models/gullyverse/limestone-excavation/manifest.json";
import originalRock from "@/public/models/gullyverse/rock-look-restore/manifest.json";
import { WallPreviewSession, QUARRY, QUARRY_URL, currentWallAnchorFits } from "./wallSection";
import type { ImmersiveRuntime } from "./runtime";

export const LIMESTONE_EXCAVATION = manifest;
export type ExcavationStyle = "baseline" | "macro" | "detailed";
export type ExcavationLook = "rock" | "limestone";
const directory = "/models/gullyverse/limestone-excavation/";

/** These caches belong only to this opt-in shell. No original-stage resource
 * is read, rewritten or evicted. Geometry exports borrow one exact pilot PBR
 * family; Stage2C is loaded only when explicitly requested for comparison. */
export class LimestoneExcavationSession extends WallPreviewSession {
  style: ExcavationStyle;
  readonly look: ExcavationLook;
  readonly assets = new Map<ExcavationStyle, GLTF>();
  private loads = new Map<ExcavationStyle, Promise<GLTF>>();
  private materialAsset: GLTF | null = null;
  private materialPending: Promise<THREE.Material> | null = null;
  private generation = 0;

  constructor(runtime: ImmersiveRuntime, style: ExcavationStyle = "detailed", look: ExcavationLook = "rock") {
    super(runtime, "authored", "quarry");
    this.style = style;
    this.look = look;
  }

  partsForRendering(): Array<{id:string|number;center:number[];radius:number;nodes:string[]}> {
    return this.style === "baseline" ? QUARRY.parts : manifest.variants[this.style].parts;
  }

  setExcavation = (style: ExcavationStyle) => {
    this.style = style;
    this.asset = null;
    this.preparedLighting.clear();
    this.lodSelections = {};
    this.lodPixels = {};
    this.publish({ assetReady: false });
    this.record("excavation-request", { style });
    this.setMode("authored");
  };

  private loader(event: string) {
    const loader = new GLTFLoader(), parse = loader.parse.bind(loader);
    loader.parse = (data, path, onLoad, onError) => {
      const at = performance.now();
      parse(data, path, gltf => {
        this.record(event + "-parse", { ms: performance.now() - at,
          bytes: typeof data === "string" ? data.length : data.byteLength });
        onLoad(gltf);
      }, onError);
    };
    return loader;
  }

  private async approvedMaterial() {
    const materialName = this.look === "rock" ? originalRock.material : manifest.material;
    const materialURL = this.look === "rock" ? originalRock.runtime : directory + "grey-limestone-material.glb";
    const find = (gltf: GLTF) => {
      let result: THREE.Material | undefined;
      gltf.scene.traverse(o => {
        if (o instanceof THREE.Mesh) {
          const material = Array.isArray(o.material) ? o.material[0] : o.material;
          if (material.name === materialName) result = material;
        }
      });
      if (!result) throw new Error("Requested excavation material is missing: " + materialName);
      return result;
    };
    if (this.materialAsset) return find(this.materialAsset);
    if (this.materialPending) return this.materialPending;
    const generation = this.generation, start = performance.now();
    this.materialPending = this.loader("approved-material").loadAsync(materialURL)
      .then(gltf => {
        if (this.disposed || generation !== this.generation) {
          disposeOwned(gltf, true);
          throw new Error("Material load abandoned by its owner");
        }
        let material: THREE.Material;
        try { material = find(gltf); } catch (error) { disposeOwned(gltf, true); throw error; }
        this.materialAsset = gltf;
        this.record("approved-material-ready", { ms: performance.now() - start,
          exactPilotFamily: true, holderMeshRendered: false, look: this.look, materialName,
          sourceGLB: this.look === "rock" ? originalRock.sourceGLB : manifest.materialSource });
        return material;
      }).finally(() => { this.materialPending = null; });
    return this.materialPending;
  }

  private async getAsset(style: ExcavationStyle): Promise<GLTF> {
    const cached = this.assets.get(style);
    if (cached) return cached;
    const pending = this.loads.get(style);
    if (pending) return pending;
    const generation = this.generation, start = performance.now();
    const promise = (async () => {
      const material = style === "baseline" ? null : await this.approvedMaterial();
      const url = style === "baseline" ? QUARRY_URL : directory + manifest.variants[style].runtime;
      const gltf = await this.loader("excavation-" + style).loadAsync(url);
      if (this.disposed || generation !== this.generation) {
        disposeOwned(gltf, true);
        throw new Error("Excavation load abandoned by its owner");
      }
      const parts = style === "baseline" ? QUARRY.parts : manifest.variants[style].parts;
      if (!parts.flatMap(p => p.nodes).every(name => gltf.scene.getObjectByName(name))) {
        disposeOwned(gltf, true);
        throw new Error("Excavation export has invalid section/LOD nodes");
      }
      if (material) {
        let embeddedTextures = false;
        gltf.scene.traverse(o => {
          if (o instanceof THREE.Mesh) for (const m of Array.isArray(o.material) ? o.material : [o.material])
            if (Object.values(m).some(v => v instanceof THREE.Texture)) embeddedTextures = true;
        });
        if (embeddedTextures) {
          disposeOwned(gltf, true);
          throw new Error("Excavation geometry contains duplicate maps; run the geometry/material pack step");
        }
        const placeholders = new Set<THREE.Material>();
        gltf.scene.traverse(o => {
          if (o instanceof THREE.Mesh) {
            for (const m of Array.isArray(o.material) ? o.material : [o.material]) placeholders.add(m);
            o.material = material;
          }
        });
        placeholders.forEach(m => m.dispose());
      }
      this.assets.set(style, gltf);
      this.record("excavation-asset-ready", { style, ms: performance.now() - start,
        geometryOnly: !!material, baselineRequested: style === "baseline" });
      return gltf;
    })().finally(() => { this.loads.delete(style); });
    this.loads.set(style, promise);
    return promise;
  }

  override async load() {
    if (this.disposed || this.state.mode === "off") return;
    const style = this.style;
    if (this.asset && this.assets.get(style) === this.asset) return;
    if (!currentWallAnchorFits("quarry")) {
      this.publish({ mode: "off", busy: true, error: "Current quarry/tunnel anchors differ; original retained",
        revision: this.state.revision + 1 });
      return;
    }
    try {
      const asset = await this.getAsset(style);
      if (this.disposed || this.snapshot().mode === "off") return;
      if (style !== this.style) { void this.load(); return; }
      this.asset = asset;
      this.record("load-ready", { style, optIn: true });
      this.publish({ assetReady: true, revision: this.state.revision + 1 });
    } catch (error) {
      if (this.disposed || style !== this.style) return;
      this.record("excavation-load-failed", { style, message: String(error) });
      if (style !== "baseline") {
        this.setExcavation("baseline");
        this.publish({ error: "Excavation unavailable; Stage 2C retained" });
      } else {
        this.publish({ mode: "off", assetReady: false, busy: true, error: String(error),
          revision: this.state.revision + 1 });
      }
    }
  }

  cloneForRendering() { return this.asset?.scene.clone(true) ?? null; }

  /** Explicit inactive-cache release; active consumers keep the shared maps. */
  retireExcavation() {
    if (this.style !== "baseline" || this.state.busy || this.loads.size)
      throw new Error("Finish the covered Stage2C restore before retiring the excavation cache");
    for (const style of ["macro", "detailed"] as const) {
      const asset = this.assets.get(style);
      if (asset) { this.record("excavation-cache-disposal", { style, ...disposeOwned(asset, false) }); this.assets.delete(style); }
    }
  }

  override retire() {
    if (this.state.mode !== "off" || this.state.busy || this.consumers)
      throw new Error("Unmount all consumers and finish covered restore before cache retirement");
    this.releaseCaches();
    this.publish({ assetReady: false });
  }

  private releaseCaches() {
    this.generation++;
    for (const [style, asset] of this.assets)
      this.record("excavation-owner-disposal", { style, ...disposeOwned(asset, style === "baseline") });
    this.assets.clear();
    if (this.materialAsset) {
      this.record("approved-material-owner-disposal", disposeOwned(this.materialAsset, true));
      this.materialAsset = null;
    }
    this.asset = null;
    this.preparedLighting.clear();
  }

  override dispose() {
    this.releaseCaches();
    super.dispose();
  }
}

function disposeOwned(gltf: GLTF, materials: boolean) {
  const geometry = new Set<THREE.BufferGeometry>(), mats = new Set<THREE.Material>(),
    textures = new Set<THREE.Texture>(), bitmaps = new Set<ImageBitmap>();
  gltf.scene.traverse(o => {
    if (!(o instanceof THREE.Mesh)) return;
    geometry.add(o.geometry);
    if (materials) for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
      mats.add(m);
      for (const v of Object.values(m)) if (v instanceof THREE.Texture) textures.add(v);
    }
  });
  geometry.forEach(g => g.dispose());
  textures.forEach(t => { if (t.image?.close) bitmaps.add(t.image); t.dispose(); });
  bitmaps.forEach(b => b.close());mats.forEach(m => m.dispose());
  return { geometries: geometry.size, materials: mats.size, textures: textures.size };
}
