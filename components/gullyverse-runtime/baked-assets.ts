import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { specularOnlyEnvironment, type Fidelity } from "./fidelity";
import { batchStatic } from "./static-batching";
import { applyPeopleMask, isPerson, smoothSeams, type PeopleMask } from "./person-shading";

export type BakedAsset = { scene: THREE.Group; rgbmRange?: number; dispose(): void };
/** Leases cancel ownership immediately and dispose late results after the last release. */
export class BakedAssetPool {
  private entries = new Map<string, { users: number; promise: Promise<BakedAsset> }>();
  private sharedImages = new Map<string, Promise<THREE.Texture>>();
  private ktx?: KTX2Loader;
  /** Releases the shared transcoder workers (after every lease has been released). */
  dispose() { this.ktx?.dispose(); this.ktx = undefined; this.sharedImages.clear(); }
  /** `batch`: chunk URLs whose plain static meshes are merged per material (see static-batching.ts). */
  constructor(private renderer: THREE.WebGLRenderer, private workerLimit = 4, private fidelity?: Fidelity, private batch?: RegExp) {}
  get size() { return this.entries.size; }
  acquire(base: string, mobile: boolean, bake: { range: number }, baseline = false) {
    const url = base + (baseline ? "contact-frontage.png.glb" : mobile ? "contact-frontage.mobile.glb" : "contact-frontage.optimized.glb");
    let entry = this.entries.get(url);
    if (!entry) {
      entry = { users: 0, promise: this.load(url, base, bake, baseline) };
      this.entries.set(url, entry);
      const owned = entry;
      entry.promise.catch(() => { if (this.entries.get(url) === owned) this.entries.delete(url); });
    }
    entry.users++;
    let released = false;
    return {
      promise: entry.promise,
      release: () => {
        if (released) return;
        released = true;
        if (--entry!.users === 0) {
          if (this.entries.get(url) === entry) this.entries.delete(url);
          void entry!.promise.then(asset => asset.dispose(), () => {});
        }
      },
    };
  }
  private async load(url: string, base: string, bake: { range: number }, baseline: boolean): Promise<BakedAsset> {
    // One transcoder (and its workers) for every chunk: the chunks ship identical copies of it.
    const ktx = this.ktx ??= new KTX2Loader().setTranscoderPath(base + "transcoders/").setWorkerLimit(this.workerLimit).detectSupport(this.renderer);
    const loader = new GLTFLoader().setKTX2Loader(ktx).setMeshoptDecoder(MeshoptDecoder);
    // Images referenced by URI (road textures every chunk shares, see share-textures.mjs) are fetched,
    // transcoded and uploaded once per pool: every chunk gets a clone sharing the same source.
    const absolute = new URL(url, window.location.href);
    loader.register(parser => {
      const original = parser.loadImageSource.bind(parser);
      parser.loadImageSource = (index: number, imageLoader: unknown) => {
        const uri: string | undefined = parser.json.images?.[index]?.uri;
        if (!uri || uri.startsWith("data:")) return original(index, imageLoader);
        const key = new URL(uri, absolute).href;
        let shared = this.sharedImages.get(key);
        if (!shared) {
          shared = original(index, imageLoader) as Promise<THREE.Texture>;
          this.sharedImages.set(key, shared);
          shared.catch(() => { if (this.sharedImages.get(key) === shared) this.sharedImages.delete(key); });
        }
        return shared.then(texture => texture.clone());
      };
      return { name: "BREEZE_shared_images" };
    });
    const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>(), textures = new Set<THREE.Texture>();
    const dispose = () => { geometries.forEach(g => g.dispose()); materials.forEach(m => m.dispose()); textures.forEach(t => t.dispose()); };
    try {
      // Optional: chunks without people have no mask file.
      const peopleMaskRequest = /locked-rev15z-cypher-(approach|plaza|audience)\//.test(base)
        ? fetch(base + "people-mask.json").then(r => r.ok ? r.json() as Promise<PeopleMask> : null, () => null) : Promise.resolve(null);
      const gltf = await loader.loadAsync(url);
      // Collect ownership before the second asynchronous load, including failure paths.
      gltf.scene.traverse((o: any) => {
        if (!o.isMesh) return;
        geometries.add(o.geometry);
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
          materials.add(m);
          for (const value of Object.values(m)) if (value instanceof THREE.Texture) textures.add(value);
        }
      });
      // Surface restoration is optional: without it the chunk still renders as exported.
      const fidelity = this.fidelity && await this.fidelity.ready.then(() => this.fidelity, () => undefined);
      fidelity?.prepare(gltf.scene);
      // People: skin hidden under clothing, smoothed seams, and smooth runtime lighting (probe + lamps)
      // instead of the starved lightmap; see person-shading.ts.
      const peopleMask: PeopleMask | null = await peopleMaskRequest;
      const people: THREE.Object3D[] = [];
      gltf.scene.traverse(o => { if (isPerson(o)) people.push(o); });
      for (const person of people) {
        const meshes: THREE.Mesh[] = [];
        person.traverse(o => { if ((o as THREE.Mesh).isMesh) meshes.push(o as THREE.Mesh); });
        applyPeopleMask(person, meshes, peopleMask);
        for (const mesh of meshes) {
          mesh.userData.breezePersonMesh = true;
          smoothSeams(mesh.geometry);
          for (const m of (Array.isArray(mesh.material) ? mesh.material : [mesh.material]) as any[]) {
            if (m.userData.breezePerson) continue;
            m.userData.breezePerson = true;
            for (const value of Object.values(m)) if (value instanceof THREE.Texture) value.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
            if (fidelity) {
              m.onBeforeCompile = (shader: any) => fidelity.patchPerson(shader, m);
              m.customProgramCacheKey = () => `breeze-person-v1-${fidelity.key(m)}`;
            }
            m.needsUpdate = true;
          }
        }
      }
      const light = baseline ? await new RGBELoader().loadAsync(base + "lightmap.hdr") : await ktx.loadAsync(base + "lightmap.ktx2");
      textures.add(light);
      light.flipY = false; light.generateMipmaps = baseline; light.minFilter = THREE.LinearMipmapLinearFilter;
      light.magFilter = THREE.LinearFilter; light.colorSpace = THREE.NoColorSpace;
      gltf.scene.traverse((o: any) => {
        if (!o.isMesh) return;
        o.castShadow = false;
        if (o.userData.breezePersonMesh) return; // people are prepared below
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
          for (const value of Object.values(m)) if (value instanceof THREE.Texture) value.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
          if (m.userData.runtimeDecal) {
            m.transparent = true; m.depthWrite = false; m.alphaTest = 1 / 255;
            m.polygonOffset = true; m.polygonOffsetFactor = -1; m.polygonOffsetUnits = -1;
          }
          const channel = Number(m.userData.runtimeLightmapChannel);
          if (!Number.isInteger(channel) || !o.geometry.getAttribute(channel === 0 ? "uv" : `uv${channel}`)) throw Error("Missing native lighting UV");
          // glTF deduplicates some materials; don't create a new unused clone per binding.
          if (!m.lightMap) {
            const lm = light.clone(); lm.channel = channel; lm.needsUpdate = true; textures.add(lm);
            m.lightMap = lm; m.lightMapIntensity = Math.PI;
            const signInk = m.userData.runtimeSignInk === true;
            if (!baseline || signInk || fidelity) m.onBeforeCompile = (shader: any) => {
              const from = "vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;";
              if (!THREE.ShaderChunk.lights_fragment_maps.includes(from)) throw Error("Lighting shader contract changed");
              const decoded = baseline ? "lightMapTexel.rgb" : `lightMapTexel.rgb * lightMapTexel.a * ${Number(bake.range).toFixed(1)}`;
              // The sign faces share a practical light. A single diffuse
              // value for their white ink avoids uneven atlas coverage on
              // small letters, while the green panels retain baked shading.
              const irradiance = signInk ? "vec3(0.25, 0.216, 0.172)" : decoded;
              shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_maps>",
                specularOnlyEnvironment(THREE.ShaderChunk.lights_fragment_maps.replace(from, `vec3 lightMapIrradiance = ${irradiance} * lightMapIntensity;`)));
              fidelity?.patch(shader, m);
            };
            m.customProgramCacheKey = () => `breeze-${baseline ? "hdr" : "rgbm-" + bake.range}-v2${signInk ? "-sign-ink" : ""}${fidelity ? "-" + fidelity.key(m) : ""}`;
            m.needsUpdate = true;
          }
        }
      });
      if (this.batch?.test(url)) {
        const batched = batchStatic(gltf.scene);
        batched.geometries.forEach(geometry => geometries.add(geometry));
        gltf.scene.userData.batching = { meshesBefore: batched.before, meshesAfter: batched.after };
      }
      return { scene: gltf.scene, rgbmRange: baseline ? undefined : bake.range, dispose };
    } catch (error) { dispose(); throw error; }
  }
}
