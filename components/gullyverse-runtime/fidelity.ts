import * as THREE from "three";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { switchedOff } from "./shop-lights";
import { deviceBudget, type Budget } from "./device-tier";
import { classifySurface, gradeCode, gradeDeclare, SurfaceLibrary, type SurfaceClass } from "./gully-materials";
import { LightPools } from "./light-pools";
import { signWearCode, signWearDeclare, signWearRoughness } from "./sign-wear";
import { holeCode } from "./contact-booth";

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
 * - Lamp highlights: Blender light objects are invisible to camera rays, so the probes lack them. A fixed
 *   set of source lights per part of the gully drives a pool of spot lights that add specular only on
 *   lightmapped surfaces (the baked lightmap already holds their diffuse light, so it is not counted twice).
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

/**
 * Reflections and lamp highlights stay fixed while walking (user request, 26 November 2026). Choosing the
 * nearest probe and the nearest eight lamps as the camera moved swapped reflections and highlights whenever
 * the visitor passed a shop. Instead each part of the gully has one probe and one set of lamps, and the only
 * change is at the cypher gate, inside the wall (z = -15), with half a metre of hysteresis.
 */
type Zone = { id: "lane" | "plaza"; probe: string; lights: { desktop: string[]; mobile: string[] } };
const streetLamps = ["L01 local pool", "L03 local pool", "L04 local pool", "L06 local pool"];
const zones: Zone[] = [
  { id: "lane", probe: "market-north", lights: {
    desktop: [...streetLamps, "Warm open-shop spill 1.002", "Warm open-shop spill 2.002", "Warm open-shop spill 3.002",
      "C lane-end warm doorway spill"],
    mobile: streetLamps,
  } },
  { id: "plaza", probe: "plaza", lights: {
    desktop: ["Accommodation local wall illumination", "Contact house lamp 1", "Contact house lamp 2", "Signboard practical.002",
      "C lane-end warm doorway spill", "gentle LED case spill"],
    mobile: ["Accommodation local wall illumination", "Contact house lamp 1", "Contact house lamp 2", "Signboard practical.002"],
  } },
];
const gateZ = -15;

export class Fidelity {
  data!: FidelityData;
  private textures = new Map<string, THREE.Texture>();
  private probeEnvs: { probe: Probe; env: THREE.Texture }[] = [];
  private current = -1;
  private zone: Zone | null = null;
  private lightZone: Zone | null = null;
  private disposed = false;
  readonly ready: Promise<void>;
  readonly budget: Budget;
  /** Shared procedural surfaces (gully-materials.ts), generated while the chunks download. */
  surfaces: SurfaceLibrary | null = null;
  /** Diffuse light pools for fixtures added after the bake (light-pools.ts). */
  readonly pools: LightPools;
  constructor(private renderer: THREE.WebGLRenderer, private mobile: boolean, transcoderPath: string) {
    this.budget = deviceBudget(renderer.getContext());
    this.pools = new LightPools(this.budget);
    this.ready = this.load(transcoderPath);
    this.ready.catch(() => {}); // Loaders fall back to the exported surfaces.
  }

  private async load(transcoderPath: string) {
    const response = await fetch(root + "fidelity.json");
    if (!response.ok) throw Error(`Could not load surface data (${response.status}).`);
    this.data = await response.json();
    if (!this.disposed) this.surfaces = new SurfaceLibrary(this.budget);
    // Lamps that are switched off give no highlights (shop-lights.ts).
    this.data.lights = this.data.lights.filter(light => !switchedOff.test(light.name));
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
    // The two probes in use (lane, then plaza) stream in afterwards, so they never delay the world.
    void this.loadProbes().catch(() => {});
  }

  private async loadProbes() {
    const pmrem = new THREE.PMREMGenerator(this.renderer);
    const hdr = new RGBELoader();
    try {
      const used = zones.map(zone => this.data.probes.find(probe => probe.id === zone.probe)).filter((p): p is Probe => !!p);
      for (const probe of used) {
        if (this.disposed) return;
        // 512 x 256 panoramas everywhere (128-pixel PMREM cubes): with the matte roughness floor (0.75, metals
        // 0.5) reflections sample only the blurred levels, which this size fully covers. The 1024-wide files
        // (probe.file) cost 7 MB more per visit for a difference visible only in the sharpest puddles.
        // High-class devices take the 1024-wide panoramas: the wet puddles (roughness 0.12-0.18) sample sharp levels.
        const sky = await hdr.loadAsync(root + (this.budget.sharpProbes ? probe.file : probe.mobileFile));
        if (this.disposed) { sky.dispose(); return; }
        desaturateProbe(sky);
        sky.mapping = THREE.EquirectangularReflectionMapping;
        this.probeEnvs.push({ probe, env: pmrem.fromEquirectangular(sky).texture });
        sky.dispose();
        this.current = -1;
      }
    } finally { pmrem.dispose(); }
  }

  private lightPool: THREE.SpotLight[] = [];

  /** Keeps a fixed number of spot lights (no shader recompiles) on the lamps of the camera's part of the gully. */
  private updateLights(scene: THREE.Scene, camera: THREE.Camera) {
    if (!this.data?.lights?.length) return;
    if (!this.lightPool.length) {
      const count = this.budget.localLights;
      for (let i = 0; i < count; i++) {
        const light = new THREE.SpotLight(0xffffff, 0, 0, Math.PI / 2, 0.5, 2);
        light.castShadow = false;
        scene.add(light, light.target);
        this.lightPool.push(light);
      }
    }
    const zone = this.zoneFor(camera);
    if (zone === this.lightZone) return;
    this.lightZone = zone;
    const names = (this.budget.tier === "low" ? zone.lights.mobile : zone.lights.desktop).slice(0, this.budget.localLights);
    const sources = names.map(name => this.data.lights.find(light => light.name.endsWith(name))).filter((l): l is SourceLight => !!l);
    this.lightPool.forEach((light, i) => {
      const source = sources[i];
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

  /** The part of the gully the camera is in (lane or plaza), switching only across the gate wall. */
  private zoneFor(camera: THREE.Camera) {
    const z = camera.position.z, [lane, plaza] = zones;
    if (!this.zone) this.zone = z > gateZ ? lane : plaza;
    else if (this.zone === lane && z < gateZ - 0.5) this.zone = plaza;
    else if (this.zone === plaza && z > gateZ + 0.5) this.zone = lane;
    return this.zone;
  }

  /** Uses the probe of the part of the gully the camera is in for reflections. Call each frame with the camera. */
  updateEnvironment(scene: THREE.Scene, camera: THREE.Camera) {
    this.updateLights(scene, camera);
    this.pools.update(camera);
    if (!this.probeEnvs.length) return;
    const zone = this.zoneFor(camera);
    // Until its own probe has streamed in, the zone uses the other one (lane first, so it is never long).
    const found = this.probeEnvs.findIndex(({ probe }) => probe.id === zone.probe);
    const best = found >= 0 ? found : 0;
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
    const surface = this.surfaceOf(m);
    const look = `${surface && this.surfaces ? this.surfaces.key(surface) : "none"}-${this.graded(m) ? "grade" : "raw"}-${m.userData.breezeCollapsed ? "flat" : ""}`;
    return `fid-${this.data.version}-rough${m.userData.breezeMinRoughness ?? 0.75}-${arts}-${m.userData.breezeRoad ?? ""}-${look}-${this.pools.key()}-wear${m.userData.breezeSignWear ?? ""}${m.userData.breezeHole ? `-hole${(m.userData.breezeHole as unknown[]).length}` : ""}`;
  }

  /** Procedural surface class of a prepared material (decided at compile time, after every restyle). */
  surfaceOf(m: THREE.Material): SurfaceClass | null {
    if (m.userData.breezeArts?.length || m.userData.runtimeDecal || m.userData.runtimeSignInk || m.userData.breezeNoGrade) return null;
    if (m.userData.breezeRoad === "aggregate") return "road";
    return classifySurface(String(m.userData.breezeSourceName ?? m.name));
  }

  /** The palette grade applies to every lightmapped surface but the navigation board and sign lettering. */
  graded(m: THREE.Material) { return !m.userData.breezeNoGrade && !m.userData.runtimeSignInk; }

  /** World position and normal varyings for projections (idempotent). */
  private worldVaryings(shader: { vertexShader: string; fragmentShader: string }) {
    if (shader.vertexShader.includes("vBreezeWorld")) return;
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vBreezeWorld;\nvarying vec3 vBreezeNormal;")
      .replace("#include <project_vertex>", "#include <project_vertex>\nvBreezeWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;\nvBreezeNormal = normalize(mat3(modelMatrix) * objectNormal);");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vBreezeWorld;\nvarying vec3 vBreezeNormal;");
  }

  /** People (see person-shading.ts): full runtime lighting, only the matte roughness floor, plus the light pools. */
  patchPerson(shader: { vertexShader: string; fragmentShader: string; uniforms: Record<string, { value: unknown }> }, m: THREE.Material) {
    const floor = Number(m.userData.breezeMinRoughness ?? 0.75).toFixed(2);
    shader.fragmentShader = shader.fragmentShader.replace("#include <normal_fragment_begin>",
      `roughnessFactor = max(roughnessFactor, mix(${floor}, min(${floor}, 0.5), step(0.5, metalnessFactor)));\n#include <normal_fragment_begin>`);
    this.pools.patch(shader, false);
  }

  /** The Rocketbox crowd (runtime-lit standard materials): the light pools only. */
  patchCrowd(shader: { fragmentShader: string; uniforms: Record<string, { value: unknown }> }) {
    this.pools.patch(shader, false);
    // A faint ambient floor (realism rescue): with the darker night, people outside every pool still separate.
    shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_end>", "irradiance += vec3(0.018 * PI);\n#include <lights_fragment_end>");
  }

  /**
   * Props, steel and decals added after the bake (courtyard-dressing.ts): runtime lighting plus the light pools and,
   * optionally, a procedural surface (e.g. rust on the truss), projected in world space like the baked surfaces.
   */
  patchProp(shader: { vertexShader: string; fragmentShader: string; uniforms: Record<string, { value: unknown }> }, surface: SurfaceClass | null, fill = 0) {
    if (surface && this.surfaces) {
      const code = this.surfaces.shader(surface);
      shader.uniforms.breezeSurface = { value: this.surfaces.texture(surface) };
      if (surface === "plaster") shader.uniforms.breezeGroundSheet = { value: this.surfaces.texture("ground") };
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>\n${code.declare}`)
        .replace("#include <color_fragment>", `#include <color_fragment>\n${code.albedo}`)
        .replace("#include <normal_fragment_begin>", `${code.roughness}\n#include <normal_fragment_begin>`)
        .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>\n${code.normal}`);
      this.worldVaryings(shader);
    }
    this.pools.patch(shader, false);
    // The same night floor the baked surfaces get (night-look.ts), so unbaked props never crush to black.
    shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_end>",
      `irradiance += PI * vec3(0.89, 0.94, 1.0) * ${(0.022 + fill).toFixed(3)};\n#include <lights_fragment_end>`);
  }

  /** Program cache key for patchProp / patchCrowd materials. */
  propKey(surface: SurfaceClass | null, fill = 0) { return `breeze-prop-${surface && this.surfaces ? this.surfaces.key(surface) : "none"}-${this.pools.key()}-fill${fill}`; }

  patch(shader: { vertexShader: string; fragmentShader: string; uniforms: Record<string, { value: unknown }> }, m: THREE.Material) {
    // Baked lightmaps already hold every source light's diffuse contribution; runtime lights add specular.
    shader.fragmentShader = shader.fragmentShader.replace("#include <lights_fragment_end>",
      "#include <lights_fragment_end>\nreflectedLight.directDiffuse = vec3(0.0);");
    // Light pools add their diffuse through the irradiance (before lights_fragment_end, so it survives the line above).
    this.pools.patch(shader, true);
    // Roughness floor (after any artwork adjustments): plaster, concrete and asphalt stay matte, metal
    // reads as brushed rather than mirrored, water keeps a soft glint.
    const floor = Number(m.userData.breezeMinRoughness ?? 0.75).toFixed(2);
    if (m.userData.breezeCollapsed) {
      // Collapsed flat-colour materials (flat-collapse.ts): base colour arrives as vertex colour, roughness and
      // metalness as the breezeRM attribute.
      shader.vertexShader = shader.vertexShader
        .replace("#include <common>", "#include <common>\nattribute vec2 breezeRM;\nvarying vec2 vBreezeRM;")
        .replace("#include <project_vertex>", "#include <project_vertex>\nvBreezeRM = breezeRM;");
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", "#include <common>\nvarying vec2 vBreezeRM;")
        .replace("#include <metalnessmap_fragment>", "#include <metalnessmap_fragment>\nroughnessFactor = vBreezeRM.x;\nmetalnessFactor = vBreezeRM.y;");
    }
    shader.fragmentShader = shader.fragmentShader.replace("#include <normal_fragment_begin>",
      `roughnessFactor = max(roughnessFactor, mix(${floor}, min(${floor}, 0.5), step(0.5, metalnessFactor)));\n#include <normal_fragment_begin>`);
    // Procedural surface (gully-materials.ts) and the palette grade; both after the vertex colour.
    const surface = this.surfaceOf(m);
    if (surface && this.surfaces) {
      const code = this.surfaces.shader(surface);
      shader.uniforms.breezeSurface = { value: this.surfaces.texture(surface) };
      if (surface === "plaster") shader.uniforms.breezeGroundSheet = { value: this.surfaces.texture("ground") };
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>\n${code.declare}`)
        .replace("#include <color_fragment>", `#include <color_fragment>\n${code.albedo}`)
        .replace("#include <normal_fragment_begin>", `${code.roughness}\n#include <normal_fragment_begin>`)
        .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>\n${code.normal}`);
      // After the declarations: the varyings land directly below #include <common>, ahead of the code that reads them.
      this.worldVaryings(shader);
    }
    if (this.graded(m)) {
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>\n${gradeDeclare}`)
        .replace("#include <color_fragment>", `#include <color_fragment>\n${gradeCode(surface)}`);
    }
    // Openings cut in the shader (contact-booth.ts): the contact window through the facade, the accommodation doorway.
    const hole = m.userData.breezeHole as number[] | number[][] | undefined;
    if (hole) {
      shader.fragmentShader = shader.fragmentShader.replace("#include <clipping_planes_fragment>", `#include <clipping_planes_fragment>\n${holeCode(hole)}`);
      this.worldVaryings(shader);
    }
    // Weathered sign paint (sign-wear.ts): the navigation board's panels and lettering.
    const wear = m.userData.breezeSignWear as "paint" | "ink" | undefined;
    if (wear) {
      shader.fragmentShader = shader.fragmentShader
        .replace("#include <common>", `#include <common>\n${signWearDeclare}`)
        .replace("#include <color_fragment>", `#include <color_fragment>\n${signWearCode(wear)}`)
        .replace("#include <roughnessmap_fragment>", `#include <roughnessmap_fragment>\n${signWearRoughness}`);
      this.worldVaryings(shader);
    }
    const arts = ((m.userData.breezeArts as string[] | undefined) ?? [])
      .map(id => this.data.arts.find(a => a.id === id)!).filter(Boolean);
    if (!arts.length) return;
    this.worldVaryings(shader);
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
      .replace("#include <common>", `#include <common>\n${samplers.map(t => `uniform sampler2D breezeArt_${t.replace(/-/g, "_")};`).join("\n")}`)
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
    this.surfaces?.dispose();
  }
}

/**
 * The probes were rendered with the old saturated magenta screen glow; the wet puddles mirrored it as lavender.
 * Reflections keep 35% of their chroma (night palette: charcoal, sodium, one cool accent), and their highlights
 * are compressed. Works on the
 * loader's half-float (or float) RGB(A) data in place, before the PMREM is built.
 */
function desaturateProbe(texture: THREE.DataTexture) {
  const data = texture.image.data as unknown as Uint16Array | Float32Array | null;
  if (!data) return;
  const half = data instanceof Uint16Array;
  const read = (i: number) => half ? THREE.DataUtils.fromHalfFloat(data[i]) : data[i];
  const write = (i: number, v: number) => { data[i] = half ? THREE.DataUtils.toHalfFloat(v) : v; };
  const stride = texture.format === THREE.RGBAFormat ? 4 : 3;
  for (let i = 0; i + 2 < data.length; i += stride) {
    const r = read(i), g = read(i + 1), b = read(i + 2), l = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    // Highlights above 1.5 are compressed (x0.3), so wet ground does not mirror bright sky patches as white.
    const k = l > 1.5 ? (1.5 + (l - 1.5) * 0.3) / l : 1;
    write(i, (l + (r - l) * 0.35) * k); write(i + 1, (l + (g - l) * 0.35) * k); write(i + 2, (l + (b - l) * 0.35) * k);
  }
  texture.needsUpdate = true;
}

/** The lightmap supplies baked diffuse light; the probe adds only reflections. */
export const specularOnlyEnvironment = (chunk: string) =>
  chunk.replace("iblIrradiance += getIBLIrradiance( geometryNormal );", "");
