import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { specularOnlyEnvironment, type Fidelity } from "./fidelity";
import { batchStatic } from "./static-batching";
import { applyPeopleMask, isPerson, smoothSeams, type PeopleMask } from "./person-shading";
import { switchOffSignLamps } from "./shop-lights";
import { restyleNavigationBoard } from "./nav-board";
import zoneLight from "./zone-light.json";
import { collapseFlat } from "./flat-collapse";
import { nightFloor } from "./night-look";

/** Chunk layout rules (CypherGatePreview.tsx): interactive meshes and materials to keep out of merging. */
export type ChunkLayout = {
  keep(mesh: THREE.Mesh): boolean;
  excludeMaterial(name: string): boolean;
  /** Meshes to hide before merging (props a later phase replaces). */
  prune?(mesh: THREE.Mesh): boolean;
  /**
   * Materials that may share one representative before merging (key, or null to keep their own), per file tier
   * (`mobile`: the phone export). Meshes with the same key then merge into one draw.
   */
  share?(materialName: string, mobile: boolean): string | null;
};

export type BakedAsset = { scene: THREE.Group; rgbmRange?: number; dispose(): void };

/** Leases cancel ownership immediately and dispose late results after the last release. */
export class BakedAssetPool {
  private entries = new Map<string, { users: number; promise: Promise<BakedAsset> }>();
  private sharedImages = new Map<string, Promise<THREE.Texture>>();
  private ktx?: KTX2Loader;
  /** Releases the shared transcoder workers (after every lease has been released). */
  dispose() { this.ktx?.dispose(); this.ktx = undefined; this.sharedImages.clear(); }
  /** `batch`: chunk URLs whose plain static meshes are merged per material (see static-batching.ts). */
  /** `hidePeople`: hide the exported Rev13A people (the Rocketbox crowd stands in their places). */
  constructor(private renderer: THREE.WebGLRenderer, private workerLimit = 4, private fidelity?: Fidelity, private batch?: RegExp,
    private hidePeople = false, private layout?: ChunkLayout) {}
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
      const peopleMaskRequest = !this.hidePeople && /locked-rev15z-cypher-(approach|plaza|audience)\//.test(base)
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
        if (this.hidePeople) {
          // Replaced by the Rocketbox crowd (rocketbox-crowd.ts).
          person.visible = false;
          meshes.forEach(mesh => { mesh.userData.breezePersonMesh = true; });
          continue;
        }
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
      /** Gives a material the chunk's baked diffuse light on lighting UV `channel` (decoded RGBM or HDR). */
      const bindLight = (m: any, channel: number) => {
        const lm = light.clone(); lm.channel = channel; lm.needsUpdate = true; textures.add(lm);
        m.lightMap = lm; m.lightMapIntensity = Math.PI;
        const signInk = m.userData.runtimeSignInk === true;
        // Surfaces lit mostly by lamps that are now off keep only part of their bake (shop-lights.ts).
        const scale = Number(m.userData.breezeLightScale ?? 1);
        if (!baseline || signInk || fidelity || scale !== 1) m.onBeforeCompile = (shader: any) => {
          const from = "vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;";
          if (!THREE.ShaderChunk.lights_fragment_maps.includes(from)) throw Error("Lighting shader contract changed");
          const decoded = baseline ? "lightMapTexel.rgb" : `lightMapTexel.rgb * lightMapTexel.a * ${Number(bake.range).toFixed(1)}`;
          // The sign faces share a practical light. A single diffuse
          // value for their white ink avoids uneven atlas coverage on
          // small letters, while the green panels retain baked shading.
          const irradiance = signInk ? "vec3(0.25, 0.216, 0.172)" : decoded;
          // Night floor (night-look.ts): shaded surfaces bottom out at deep charcoal instead of black.
          const floor = signInk ? "" : ` + ${nightFloor}`;
          // Realism rescue (docs/runtime/REALISM-RESCUE-PLAN.md): the bake's soft fill is the "ambient wash", so its low end
          // is crushed (dim bounce light falls to near black, lamp-lit surfaces keep their value) and walls above the
          // first floor (y 10.5 … 17.5 m) fade toward the night sky. Sign ink keeps its flat practical light.
          const lit = signInk ? `${irradiance} * ${scale.toFixed(3)}` : `breezeCrush(${irradiance} * ${scale.toFixed(3)})`;
          if (!signInk) {
            shader.vertexShader = `varying vec3 vBreezeLmP;
${shader.vertexShader.replace("#include <project_vertex>", `#include <project_vertex>
vBreezeLmP = (modelMatrix * vec4(transformed, 1.0)).xyz;`)}`;
            shader.fragmentShader = `varying vec3 vBreezeLmP;
// Measured per-zone light levels (scripts/measure-look.py against references/; zone-light.json).
float breezeZoneGain(vec3 p) {
  // Soft boxes, blended in log space (equal steps read as equal ratios): no hard seams where zones meet.
  float lane = smoothstep(-15.1, -14.1, p.z) * (1.0 - smoothstep(-1.0, 1.0, p.z));
  float market = smoothstep(-1.0, 1.0, p.z);
  float below = 1.0 - smoothstep(10.2, 11.6, p.y);
  float events = (1.0 - smoothstep(-14.6, -12.8, p.x)) * smoothstep(-37.8, -36.0, p.z) * (1.0 - smoothstep(-25.5, -23.7, p.z)) * below;
  float stay = (1.0 - smoothstep(-15.0, -13.2, p.x)) * smoothstep(-23.7, -21.9, p.z) * (1.0 - smoothstep(-14.4, -13.0, p.z)) * below;
  float g = log(${zoneLight.plaza.toFixed(3)});
  g = mix(g, log(${zoneLight.events.toFixed(3)}), events * (1.0 - lane));
  g = mix(g, log(${zoneLight.stay.toFixed(3)}), stay * (1.0 - lane));
  g = mix(g, log(${zoneLight.lane.toFixed(3)}), lane);
  g = mix(g, 0.0, market);
  return exp(g);
}
vec3 breezeCrush(vec3 lm);
/** A decoded bake texel as the wall shows it: contrast curve, zone gain and night floor (used by patches too). */
vec3 breezeLit(vec3 lm) { return breezeCrush(lm) + ${nightFloor}; }
vec3 breezeCrush(vec3 lm) {
  vec3 raw = lm;
  float l = dot(lm, vec3(0.2126, 0.7152, 0.0722));
  lm *= 0.48 + 0.62 * smoothstep(0.01, 0.28, l);
  vec3 lit = lm * mix(1.0, 0.72, smoothstep(10.5, 17.5, vBreezeLmP.y)) * breezeZoneGain(vBreezeLmP);
  // The team mural wall keeps its baked light as painted (the rescue's curve and the plaza gain washed the mural out).
  vec3 p = vBreezeLmP;
  float mural = smoothstep(14.6, 14.95, p.x) * smoothstep(-36.4, -35.7, p.z) * (1.0 - smoothstep(-27.2, -26.5, p.z)) * (1.0 - smoothstep(11.3, 11.8, p.y));
  return mix(lit, raw, mural);
}
` + shader.fragmentShader;
          }
          shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_maps>",
            specularOnlyEnvironment(THREE.ShaderChunk.lights_fragment_maps.replace(from, `vec3 lightMapIrradiance = (${lit}${floor}) * lightMapIntensity;`)));
          fidelity?.patch(shader, m);
        };
        m.customProgramCacheKey = () => `breeze-${baseline ? "hdr" : "rgbm-" + bake.range}-v6-z${zoneLight.lane}-${zoneLight.events}-${zoneLight.stay}-${zoneLight.plaza}${signInk ? "-sign-ink" : ""}${scale !== 1 ? "-light" + scale : ""}${fidelity ? "-" + fidelity.key(m) : ""}`;
        m.needsUpdate = true;
      };
      // The sign-wash lamps above the shops are off; the shop tubes and street lights stay on.
      switchOffSignLamps(gltf.scene);
      // The navigation board as a weathered painted sign with squircle corners (nav-board.ts).
      const board = restyleNavigationBoard(gltf.scene);
      board?.geometries.forEach(geometry => geometries.add(geometry));
      board?.materials.forEach(material => materials.add(material));
      // Flat-colour collapse before the lighting is bound, so the merged materials are lit like the rest.
      const layout = this.layout;
      if (fidelity && layout && this.batch?.test(url)) {
        if (layout.prune) gltf.scene.traverse(o => { if ((o as THREE.Mesh).isMesh && layout.prune!(o as THREE.Mesh)) o.visible = false; });
        if (layout.share) {
          const mobileFile = url.endsWith(".mobile.glb"), representatives = new Map<string, THREE.Material>();
          gltf.scene.traverse(o => {
            const mesh = o as THREE.Mesh;
            if (!mesh.isMesh || Array.isArray(mesh.material)) return;
            const key = layout.share!(mesh.material.name, mobileFile);
            if (!key) return;
            const representative = representatives.get(key);
            if (representative) mesh.material = representative; else representatives.set(key, mesh.material);
          });
        }
        const flat = collapseFlat(gltf.scene, layout.keep, layout.excludeMaterial);
        flat.geometries.forEach(geometry => geometries.add(geometry));
        flat.materials.forEach(material => materials.add(material));
        gltf.scene.userData.collapse = { flatMaterials: flat.flatMaterials, merged: flat.merged, into: flat.materials.length };
      }
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
          if (!m.lightMap) bindLight(m, channel);
        }
      });
      if (this.batch?.test(url)) {
        const layout = this.layout;
        const batched = batchStatic(gltf.scene, layout?.keep);
        batched.geometries.forEach(geometry => geometries.add(geometry));
        gltf.scene.userData.batching = { meshesBefore: batched.before, meshesAfter: batched.after };
      }
      return { scene: gltf.scene, rgbmRange: baseline ? undefined : bake.range, dispose };
    } catch (error) { dispose(); throw error; }
  }
}
