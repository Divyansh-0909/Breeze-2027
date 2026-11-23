import * as THREE from "three";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";

/**
 * Restores Rev15Z surfaces the baked exports lost, using data extracted from the locked Blender master
 * (see docs/runtime/M2M-BLENDER-FIDELITY.md):
 *
 * - Road base colour: the export baked aggregate × RoadTint into a coarse shared atlas (~10 cm texels),
 *   which turned the fine asphalt grain into blotches. The source multiplies the tiling detail texture
 *   (RoadDetailUV) by the RoadTint vertex colours; both survive in the GLBs, so the runtime rebinds them.
 * - Object-linked world-projected artwork (three shutter murals and five supporting graffiti pieces):
 *   the exporter only read mesh-level materials, so these per-object materials were dropped. Each
 *   projection is evaluated here with the exact Blender node constants, only on its own surface.
 * - Reflection probes: Cycles panoramas rendered from the master at street level provide the specular
 *   environment the baked diffuse lightmaps cannot (wet road, galvanised metal, glass). The background
 *   stays near-black so unbuilt space fades to darkness.
 *   Lightmapped surfaces keep their baked diffuse light and take only specular from the probe.
 * - Lamp highlights: Blender light objects are invisible to camera rays, so the probes lack them. The
 *   nearest source lights drive a fixed pool of spot lights that add specular only on lightmapped
 *   surfaces (the baked lightmap already holds their diffuse light, so it is not counted twice).
 */

type Op = [string, number, boolean];
type Chain = { axis: "X" | "Y" | "Z" | "Value" | "Alpha"; ops: Op[] };
export type ArtSpec = {
  id: string; texture: string; kind: "shutter" | "wall"; target: string;
  lo: [number, number, number]; hi: [number, number, number];
  u: Chain; v: Chain; normal: Chain & { threshold: number }; rect: { u: Chain; v: Chain } | null;
  paint: [number, number, number] | null;
};
export type Probe = { id: string; position: [number, number, number]; file: string; mobileFile: string; intensity: number };
export type SourceLight = {
  name: string; type: string; position: [number, number, number]; direction: [number, number, number];
  color: [number, number, number]; intensity: number; angle: number; penumbra: number;
};
export type FidelityData = {
  version: string;
  road: { materials: Record<string, "aggregate" | "mud">; mud: [number, number, number] };
  textures: Record<string, { file: string; mobileFile: string }>;
  arts: ArtSpec[];
  probes: Probe[];
  lights: SourceLight[];
  sky: { color: [number, number, number] };
};

const root = "/models/gullyverse/locked-rev15z-fidelity/";
const axisIndex = { X: "x", Y: "y", Z: "z" } as const;

function glslChain(chain: Chain, vector: string) {
  if (!(chain.axis in axisIndex)) throw Error(`Unsupported projection axis ${chain.axis}`);
  let expr = `${vector}.${axisIndex[chain.axis as keyof typeof axisIndex]}`;
  for (const [op, c, first] of chain.ops) {
    const k = c.toFixed(6);
    const [a, b] = first ? [expr, k] : [k, expr];
    if (op === "SUBTRACT") expr = `(${a} - ${b})`;
    else if (op === "ADD") expr = `(${a} + ${b})`;
    else if (op === "MULTIPLY") expr = `(${a} * ${b})`;
    else throw Error(`Unsupported projection operation ${op}`);
  }
  return expr;
}

export class Fidelity {
  data!: FidelityData;
  private textures = new Map<string, THREE.Texture>();
  private probeEnvs: { probe: Probe; env: THREE.Texture }[] = [];
  private current = -1;
  private disposed = false;
  readonly ready: Promise<void>;
  constructor(private renderer: THREE.WebGLRenderer, private mobile: boolean, transcoderPath: string) {
    this.ready = this.load(transcoderPath);
    this.ready.catch(() => {}); // Loaders fall back to the exported surfaces.
  }

  private async load(transcoderPath: string) {
    const response = await fetch(root + "fidelity.json");
    if (!response.ok) throw Error(`Could not load surface data (${response.status}).`);
    this.data = await response.json();
    const ktx = new KTX2Loader().setTranscoderPath(transcoderPath).setWorkerLimit(2).detectSupport(this.renderer);
    try {
      await Promise.all(Object.entries(this.data.textures).map(async ([id, t]) => {
        const texture = await ktx.loadAsync(root + (this.mobile ? t.mobileFile : t.file));
        texture.wrapS = texture.wrapT = id === "aggregate" ? THREE.RepeatWrapping : THREE.ClampToEdgeWrapping;
        texture.anisotropy = Math.min(8, this.renderer.capabilities.getMaxAnisotropy());
        texture.colorSpace = THREE.SRGBColorSpace;
        this.textures.set(id, texture);
      }));
    } finally { ktx.dispose(); }
    // Probes stream in afterwards, nearest-first along the route, so they never delay the world.
    void this.loadProbes().catch(() => {});
  }

  private async loadProbes() {
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    const hdr = new RGBELoader();
    try {
      for (const probe of this.data.probes) {
        if (this.disposed) return;
        // 512 x 256 panoramas everywhere (128-pixel PMREM cubes): with the matte roughness floor (0.75, metals
        // 0.5) reflections sample only the blurred levels, which this size fully covers. The 1024-wide files
        // (probe.file) cost 7 MB more per visit for a difference visible only in the sharpest puddles.
        const sky = await hdr.loadAsync(root + probe.mobileFile);
        if (this.disposed) { sky.dispose(); return; }
        sky.mapping = THREE.EquirectangularReflectionMapping;
        this.probeEnvs.push({ probe, env: pmrem.fromEquirectangular(sky).texture });
        sky.dispose();
        this.current = -1;
      }
    } finally { pmrem.dispose(); }
  }

  private lightPool: THREE.SpotLight[] = [];
  private lightOrder: SourceLight[] = [];
  private lightCheck = new THREE.Vector3(Infinity, 0, 0);

  /** Keeps a fixed number of spot lights (no shader recompiles) on the source lights nearest the camera. */
  private updateLights(scene: THREE.Scene, camera: THREE.Camera) {
    if (!this.data?.lights?.length) return;
    if (!this.lightPool.length) {
      const count = this.mobile ? 4 : 8;
      for (let i = 0; i < count; i++) {
        const light = new THREE.SpotLight(0xffffff, 0, 0, Math.PI / 2, 0.5, 2);
        light.castShadow = false;
        scene.add(light, light.target);
        this.lightPool.push(light);
      }
    }
    // Re-sort only after the camera moves half a metre.
    if (camera.position.distanceToSquared(this.lightCheck) < 0.25) return;
    this.lightCheck.copy(camera.position);
    const { x, y, z } = camera.position;
    this.lightOrder = [...this.data.lights].sort((a, b) =>
      (a.position[0] - x) ** 2 + (a.position[1] - y) ** 2 + (a.position[2] - z) ** 2 -
      ((b.position[0] - x) ** 2 + (b.position[1] - y) ** 2 + (b.position[2] - z) ** 2));
    this.lightPool.forEach((light, i) => {
      const source = this.lightOrder[i];
      if (!source) { light.intensity = 0; return; }
      light.position.set(...source.position);
      light.target.position.set(source.position[0] + source.direction[0], source.position[1] + source.direction[1],
        source.position[2] + source.direction[2]);
      light.target.updateMatrixWorld();
      light.color.setRGB(...source.color);
      light.intensity = source.intensity;
      light.angle = Math.min(source.angle, Math.PI / 2);
      light.penumbra = source.penumbra;
    });
  }

  /** Chooses the nearest street-level probe for reflections and sky. Call each frame with the camera. */
  updateEnvironment(scene: THREE.Scene, camera: THREE.Camera) {
    this.updateLights(scene, camera);
    if (!this.probeEnvs.length) return;
    let best = 0, bestDistance = Infinity;
    this.probeEnvs.forEach(({ probe }, i) => {
      const [x, y, z] = probe.position;
      const d = (camera.position.x - x) ** 2 + (camera.position.y - y) ** 2 + (camera.position.z - z) ** 2;
      if (d < bestDistance) { bestDistance = d; best = i; }
    });
    if (best === this.current) return;
    this.current = best;
    const { env, probe } = this.probeEnvs[best];
    scene.environment = env;
    scene.environmentIntensity = probe.intensity;
    // The background stays the near-black void (set by the scene): beyond the lane ends and around the
    // map's edges the world fades into darkness, which the night-sky colour washed out (user preference).
  }

  /** Review diagnostics: which materials took road colour or artwork (private preview only). */
  readonly report: { road: string[]; arts: Record<string, string[]> } = { road: [], arts: {} };

  /** Rebinds road colour and records which artworks touch each material. Call before compiling materials. */
  prepare(sceneRoot: THREE.Object3D) {
    if (typeof window !== "undefined" && window.location.pathname.startsWith("/runtime-preview")) {
      (window as unknown as { __breezeFidelity?: Fidelity }).__breezeFidelity = this;
    }
    sceneRoot.updateMatrixWorld(true);
    const box = new THREE.Box3();
    sceneRoot.traverse((o: any) => {
      if (!o.isMesh) return;
      for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
        // Matte by default: the export left many surfaces fairly smooth, which mirrored the probes as
        // faceted chrome on the cypher balconies and polished the road. Water keeps a soft glint.
        const water = /water/i.test(m.name);
        m.userData.breezeMinRoughness = water ? 0.35 : 0.75;
        if (!water && "clearcoat" in m && m.clearcoat > 0) { m.clearcoat = 0; m.needsUpdate = true; }
        const road = this.data.road.materials[m.name];
        if (road) {
          const tint = o.geometry.getAttribute("color_1");
          if (tint) o.geometry.setAttribute("color", tint);
          m.vertexColors = true;
          if (road === "aggregate") {
            m.map = this.textures.get("aggregate")!; m.map!.channel = 1;
            m.color.setRGB(1, 1, 1);
          } else {
            m.map = null; m.color.setRGB(...this.data.road.mud);
          }
          m.userData.breezeRoad = road;
          this.report.road.push(`${o.name} :: ${m.name}`);
          m.needsUpdate = true;
        }
        box.setFromObject(o);
        // Three.js (x, y, z) -> Blender (x, -z, y)
        const lo = [box.min.x, -box.max.z, box.min.y], hi = [box.max.x, -box.min.z, box.max.y];
        // GLTFLoader sanitises node names (spaces -> "_", "/" "." ":" removed); multi-material
        // nodes become a group of primitives, so the parent carries the name.
        const names = `${o.name}|${o.parent?.name ?? ""}`;
        for (const art of this.data.arts) {
          if (!names.includes(THREE.PropertyBinding.sanitizeNodeName(art.target))) continue;
          if ([0, 1, 2].some(i => hi[i] < art.lo[i] || lo[i] > art.hi[i])) continue;
          const ids: string[] = m.userData.breezeArts ?? (m.userData.breezeArts = []);
          if (!ids.includes(art.id)) ids.push(art.id);
          (this.report.arts[art.id] ??= []).push(`${o.name} :: ${m.name}`);
        }
      }
    });
  }

  /** Program cache key suffix for a prepared material. */
  key(m: THREE.Material) {
    const arts = (m.userData.breezeArts as string[] | undefined)?.join("+") ?? "";
    return `fid-${this.data.version}-rough${m.userData.breezeMinRoughness ?? 0.75}-${arts}-${m.userData.breezeRoad ?? ""}`;
  }

  /** Adds artwork projection to a standard-material shader. */
  patch(shader: { vertexShader: string; fragmentShader: string; uniforms: Record<string, { value: unknown }> }, m: THREE.Material) {
    // Baked lightmaps already hold every source light's diffuse contribution; runtime lights add specular.
    shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_end>",
      "#include <lights_fragment_end>\nreflectedLight.directDiffuse = vec3(0.0);");
    // Roughness floor (after any artwork adjustments): plaster, concrete and asphalt stay matte, metal
    // reads as brushed rather than mirrored, water keeps a soft glint.
    const floor = Number(m.userData.breezeMinRoughness ?? 0.75).toFixed(2);
    shader.fragmentShader = shader.fragmentShader.replace("#include <normal_fragment_begin>",
      `roughnessFactor = max(roughnessFactor, mix(${floor}, min(${floor}, 0.5), step(0.5, metalnessFactor)));\n#include <normal_fragment_begin>`);
    const arts = ((m.userData.breezeArts as string[] | undefined) ?? [])
      .map(id => this.data.arts.find(a => a.id === id)!).filter(Boolean);
    if (!arts.length) return;
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vBreezeWorld;\nvarying vec3 vBreezeNormal;")
      .replace("#include <project_vertex>", "#include <project_vertex>\nvBreezeWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;\nvBreezeNormal = normalize(mat3(modelMatrix) * objectNormal);");
    const samplers = [...new Set(arts.map(a => a.texture))];
    samplers.forEach(t => { shader.uniforms[`breezeArt_${t.replace(/-/g, "_")}`] = { value: this.textures.get(t) }; });
    const body = arts.map(a => {
      const s = `breezeArt_${a.texture.replace(/-/g, "_")}`;
      const inside = `step(vec3(${a.lo.map(v => v.toFixed(3)).join(",")}), bw) * step(bw, vec3(${a.hi.map(v => v.toFixed(3)).join(",")}))`;
      const rect = a.rect ? (() => {
        const ru = glslChain(a.rect.u, "bw"), rv = glslChain(a.rect.v, "bw");
        return `* step(0.0, ${ru}) * step(${ru}, 1.0) * step(0.0, ${rv}) * step(${rv}, 1.0)`;
      })() : "";
      const facing = `step(${a.normal.threshold.toFixed(6)} + 1e-6, ${glslChain(a.normal, "bn")})`;
      const lines = [
        `{ vec3 inBox = ${inside};`,
        `  vec2 uv = vec2(${glslChain(a.u, "bw")}, 1.0 - ${glslChain(a.v, "bw")});`,
        `  vec4 art = texture2D(${s}, uv);`,
        `  float m = art.a * inBox.x * inBox.y * inBox.z * ${facing} ${rect};`,
      ];
      if (a.kind === "shutter") {
        // Blender: enamel paint under the mural, metallic 0.32 where bare, roughness 0.7 -> 0.82 under paint.
        lines.push(`  float onShutter = inBox.x * inBox.y * inBox.z * ${facing};`,
          `  diffuseColor.rgb = mix(diffuseColor.rgb, mix(vec3(${a.paint!.map(v => v.toFixed(4)).join(",")}), art.rgb, art.a), onShutter);`,
          `  breezeShutter = max(breezeShutter, onShutter); breezePaint = max(breezePaint, m); }`);
      } else {
        lines.push(`  diffuseColor.rgb = mix(diffuseColor.rgb, art.rgb, m * 0.95); breezePaint = max(breezePaint, m); }`);
      }
      return lines.join("\n");
    }).join("\n");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>\nvarying vec3 vBreezeWorld;\nvarying vec3 vBreezeNormal;\n${samplers.map(t => `uniform sampler2D breezeArt_${t.replace(/-/g, "_")};`).join("\n")}`)
      .replace("#include <map_fragment>", `#include <map_fragment>
float breezeShutter = 0.0, breezePaint = 0.0;
{
  vec3 bw = vec3(vBreezeWorld.x, -vBreezeWorld.z, vBreezeWorld.y);
  vec3 bn = normalize(vec3(vBreezeNormal.x, -vBreezeNormal.z, vBreezeNormal.y));
${body}
}`)
      .replace("#include <roughnessmap_fragment>", `#include <roughnessmap_fragment>
roughnessFactor = mix(roughnessFactor, mix(0.7, 0.82, breezePaint), breezeShutter);
roughnessFactor = mix(roughnessFactor, 0.82, breezePaint * (1.0 - breezeShutter));`)
      .replace("#include <metalnessmap_fragment>", `#include <metalnessmap_fragment>
metalnessFactor = mix(metalnessFactor, 0.32 * (1.0 - breezePaint), breezeShutter);
metalnessFactor *= 1.0 - breezePaint * (1.0 - breezeShutter);`);
  }

  dispose() {
    this.disposed = true;
    this.lightPool.forEach(light => { light.removeFromParent(); light.target.removeFromParent(); light.dispose(); });
    this.textures.forEach(t => t.dispose());
    this.probeEnvs.forEach(p => p.env.dispose());
  }
}

/** The lightmap supplies baked diffuse light; the probe adds only reflections. */
export const specularOnlyEnvironment = (chunk: string) =>
  chunk.replace("iblIrradiance += getIBLIrradiance( geometryNormal );", "");
