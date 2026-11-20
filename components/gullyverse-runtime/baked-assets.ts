import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";

export type BakedAsset = { scene: THREE.Group; dispose(): void };
/** Leases cancel ownership immediately and dispose late results after the last release. */
export class BakedAssetPool {
  private entries = new Map<string, { users: number; promise: Promise<BakedAsset> }>();
  constructor(private renderer: THREE.WebGLRenderer) {}
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
    const ktx = new KTX2Loader().setTranscoderPath(base + "transcoders/").detectSupport(this.renderer);
    const loader = new GLTFLoader().setKTX2Loader(ktx).setMeshoptDecoder(MeshoptDecoder);
    const geometries = new Set<THREE.BufferGeometry>(), materials = new Set<THREE.Material>(), textures = new Set<THREE.Texture>();
    const dispose = () => { geometries.forEach(g => g.dispose()); materials.forEach(m => m.dispose()); textures.forEach(t => t.dispose()); ktx.dispose(); };
    try {
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
      const light = baseline ? await new RGBELoader().loadAsync(base + "lightmap.hdr") : await ktx.loadAsync(base + "lightmap.ktx2");
      textures.add(light);
      light.flipY = false; light.generateMipmaps = baseline; light.minFilter = THREE.LinearMipmapLinearFilter;
      light.magFilter = THREE.LinearFilter; light.colorSpace = THREE.NoColorSpace;
      gltf.scene.traverse((o: any) => {
        if (!o.isMesh) return;
        o.castShadow = false;
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
            if (!baseline || signInk) m.onBeforeCompile = (shader: any) => {
              const from = "vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;";
              if (!THREE.ShaderChunk.lights_fragment_maps.includes(from)) throw Error("Lighting shader contract changed");
              const decoded = baseline ? "lightMapTexel.rgb" : `lightMapTexel.rgb * lightMapTexel.a * ${Number(bake.range).toFixed(1)}`;
              // The sign faces share a practical light. A single diffuse
              // value for their white ink avoids uneven atlas coverage on
              // small letters, while the green panels retain baked shading.
              const irradiance = signInk ? "vec3(0.25, 0.216, 0.172)" : decoded;
              shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_maps>",
                THREE.ShaderChunk.lights_fragment_maps.replace(from, `vec3 lightMapIrradiance = ${irradiance} * lightMapIntensity;`));
            };
            m.customProgramCacheKey = () => `breeze-${baseline ? "hdr" : "rgbm-" + bake.range}-v1${signInk ? "-sign-ink" : ""}`;
            m.needsUpdate = true;
          }
        }
      });
      return { scene: gltf.scene, dispose };
    } catch (error) { dispose(); throw error; }
  }
}
