import * as THREE from "three";
import type { Budget } from "./device-tier";

/**
 * Light pools (docs/runtime/PHASE2-COURTYARD-SCREEN-PLAN.md): local, unshadowed lights for fixtures added after
 * the bake. Runtime three.js lights only add specular on lightmapped surfaces (fidelity.ts discards their direct
 * diffuse so the bake is not counted twice), so a new lamp would glow without lighting its wall. Pools add their
 * own diffuse to the baked irradiance, and highlights through three's RE_Direct.
 *
 * One uniform block shared by every patched material: fixed length (4 high / 4 medium / 3 low), so no shader ever
 * recompiles when pools change. Positions are converted to view space on the CPU each frame and compared with
 * three's view-space geometryPosition / geometryNormal, so the same code lights meshes, instances and the
 * BatchedMesh crowd. Falloff: max(0, 1 − d²/r²)². `colour` is in irradiance/π units: a value of 1 lights a white,
 * square-on surface to full white (as a lightmap texel of 1 does).
 */
export type Pool = { position: THREE.Vector3; radius: number; colour: THREE.Color; intensity: number };

/**
 * A registered pool (Phase 3 registry). Any number may be registered; each frame the `count` best for the camera
 * are bound to the shader slots. Score = distance − radius, minus 5 m for pools within 10 m (so a wide pool far
 * away never crowds out the small practical beside the viewer) and minus `bias`. `active` gates a pool to its zone.
 * Callers may mutate position / colour / intensity at any time.
 */
export type PoolSpec = Pool & { bias?: number; active?: (eye: THREE.Vector3) => boolean; label?: string; cone?: Cone };
/** A spot pool: light leaves along `direction` (world), full inside `angle` (radians, half-angle), soft edge `penumbra`. */
export type Cone = { direction: THREE.Vector3; angle: number; penumbra: number };

type Slot = { spec: PoolSpec | null; weight: number };

const fadeIn = 0.35, fadeOut = 0.2, hysteresis = 1.5;

export class LightPools {
  readonly count: number;
  readonly uniforms: { breezePoolPos: { value: THREE.Vector4[] }; breezePoolColour: { value: THREE.Color[] }; breezePoolDir: { value: THREE.Vector4[] }; breezePoolInner: { value: number[] } };
  private specs: PoolSpec[] = [];
  private slots: Slot[];
  private view = new THREE.Vector3();
  private axis = new THREE.Vector3();
  private inner: number[] = [];
  private eye = new THREE.Vector3();
  private last = 0;

  constructor(budget: Budget) {
    this.count = budget.tier === "low" ? 3 : 4;
    this.slots = Array.from({ length: this.count }, () => ({ spec: null, weight: 0 }));
    this.uniforms = {
      breezePoolPos: { value: Array.from({ length: this.count }, () => new THREE.Vector4(0, -1000, 0, 1)) },
      breezePoolColour: { value: Array.from({ length: this.count }, () => new THREE.Color(0, 0, 0)) },
      // xyz: view-space cone axis, w: cos(outer angle); w < -1 marks an omni pool.
      breezePoolDir: { value: Array.from({ length: this.count }, () => new THREE.Vector4(0, -1, 0, -2)) },
      breezePoolInner: { value: Array.from({ length: this.count }, () => 1) },
    };
  }

  /** Registers a pool; returns the live spec (mutate it to animate). */
  add(position: THREE.Vector3Like, radius: number, colour: THREE.ColorRepresentation, intensity: number,
    options: { bias?: number; active?: (eye: THREE.Vector3) => boolean; label?: string; cone?: Cone } = {}): PoolSpec {
    const spec: PoolSpec = { position: new THREE.Vector3(position.x, position.y, position.z), radius, colour: new THREE.Color(colour), intensity, ...options };
    this.specs.push(spec);
    return spec;
  }

  remove(spec: PoolSpec) {
    this.specs = this.specs.filter(s => s !== spec);
    for (const slot of this.slots) if (slot.spec === spec) { slot.spec = null; slot.weight = 0; }
  }

  /** The pools bound right now (diagnostics). */
  bound() { return this.slots.map(s => ({ label: s.spec?.label ?? null, weight: Number(s.weight.toFixed(2)) })); }

  private score(spec: PoolSpec) {
    const d = spec.position.distanceTo(this.eye);
    return d - spec.radius - (d < 10 ? 5 : 0) - (spec.bias ?? 0);
  }

  /** Picks the best pools for the camera, fades swaps, converts to view space. Call once per frame before rendering. */
  update(camera: THREE.Camera, step?: number) {
    const now = performance.now() / 1000, delta = step ?? (this.last ? Math.min(0.1, now - this.last) : 1);
    this.last = now;
    camera.updateMatrixWorld();
    this.eye.setFromMatrixPosition(camera.matrixWorld);
    const candidates = this.specs.filter(s => s.intensity > 0 && (!s.active || s.active(this.eye)))
      .map(spec => ({ spec, score: this.score(spec) - (this.slots.some(slot => slot.spec === spec) ? hysteresis : 0) }))
      .sort((a, b) => a.score - b.score).slice(0, this.count).map(c => c.spec);
    for (const slot of this.slots) {
      if (slot.spec && !candidates.includes(slot.spec)) {
        slot.weight = Math.max(0, slot.weight - delta / fadeOut);
        if (slot.weight === 0) slot.spec = null;
      }
    }
    for (const spec of candidates) {
      if (this.slots.some(slot => slot.spec === spec)) continue;
      const free = this.slots.find(slot => !slot.spec);
      if (free) { free.spec = spec; free.weight = 0; }
    }
    this.slots.forEach((slot, i) => {
      const spec = slot.spec;
      if (spec && candidates.includes(spec)) slot.weight = Math.min(1, slot.weight + delta / fadeIn);
      if (!spec) {
        this.uniforms.breezePoolPos.value[i].set(0, -1000, 0, 1);
        this.uniforms.breezePoolColour.value[i].setRGB(0, 0, 0);
        return;
      }
      const dir = this.uniforms.breezePoolDir.value[i];
      if (spec.cone) {
        this.axis.copy(spec.cone.direction).transformDirection(camera.matrixWorldInverse);
        dir.set(this.axis.x, this.axis.y, this.axis.z, Math.cos(spec.cone.angle * (1 + spec.cone.penumbra)));
        dir.w = Math.max(dir.w, -0.99);
        this.inner[i] = Math.cos(spec.cone.angle);
      } else { dir.set(0, -1, 0, -2); this.inner[i] = 1; }
      this.uniforms.breezePoolInner.value[i] = this.inner[i];
      this.view.copy(spec.position).applyMatrix4(camera.matrixWorldInverse);
      this.uniforms.breezePoolPos.value[i].set(this.view.x, this.view.y, this.view.z, Math.max(spec.radius, 0.01));
      this.uniforms.breezePoolColour.value[i].copy(spec.colour).multiplyScalar(spec.intensity * slot.weight);
    });
  }

  /**
   * Adds the pools to an unlit MeshBasicMaterial (decals: stencils, chalk boards, flyers): their fixed brightness stands
   * in for the bake, and the pools add lamp light on top (Lambert on the decal's own colour), so a stencil under the
   * tube or the streetlamp brightens with the wall around it.
   */
  patchUnlit(shader: { vertexShader: string; fragmentShader: string; uniforms: Record<string, { value: unknown }> }) {
    if (shader.fragmentShader.includes("breezePoolPos")) return;
    for (const key of ["breezePoolPos", "breezePoolColour", "breezePoolDir", "breezePoolInner"] as const) shader.uniforms[key] = this.uniforms[key];
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", `#include <common>
varying vec3 vBreezeDecalP;
varying vec3 vBreezeDecalN;`)
      .replace("#include <project_vertex>", `#include <project_vertex>
vBreezeDecalP = mvPosition.xyz;
vBreezeDecalN = normalize(normalMatrix * normal);`);
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>
varying vec3 vBreezeDecalP;
varying vec3 vBreezeDecalN;
uniform vec4 breezePoolPos[${this.count}];
uniform vec3 breezePoolColour[${this.count}];
uniform vec4 breezePoolDir[${this.count}];
uniform float breezePoolInner[${this.count}];`)
      .replace("#include <map_fragment>", `#include <map_fragment>
vec3 breezeAlbedo = diffuseColor.rgb;`)
      .replace("vec3 outgoingLight = reflectedLight.indirectDiffuse;", `vec3 outgoingLight = reflectedLight.indirectDiffuse;
{
  vec3 n = normalize(vBreezeDecalN);
  for (int i = 0; i < ${this.count}; i++) {
    vec3 toPool = breezePoolPos[i].xyz - vBreezeDecalP;
    float d2 = dot(toPool, toPool);
    float window = max(0.0, 1.0 - d2 / (breezePoolPos[i].w * breezePoolPos[i].w));
    if (window <= 0.0) continue;
    vec3 l = toPool * inversesqrt(max(d2, 1e-6));
    float cone = breezePoolDir[i].w < -1.0 ? 1.0 : smoothstep(breezePoolDir[i].w, breezePoolInner[i], dot(-l, breezePoolDir[i].xyz));
    outgoingLight += breezeAlbedo * breezePoolColour[i] * window * window * cone * max(dot(n, l), 0.0);
  }
}`);
  }

  /** Program cache key part. */
  key() { return `pools${this.count}`; }

  /**
   * Adds the pools to a standard/physical shader, before lights_fragment_end. `lightmapped`: diffuse goes into the
   * irradiance (the material's direct diffuse is discarded later by fidelity.ts); otherwise RE_Direct lights fully.
   */
  patch(shader: { fragmentShader: string; uniforms: Record<string, { value: unknown }> }, lightmapped: boolean) {
    if (shader.fragmentShader.includes("breezePoolPos")) return;
    shader.uniforms.breezePoolPos = this.uniforms.breezePoolPos;
    shader.uniforms.breezePoolColour = this.uniforms.breezePoolColour;
    shader.uniforms.breezePoolDir = this.uniforms.breezePoolDir;
    shader.uniforms.breezePoolInner = this.uniforms.breezePoolInner;
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>
uniform vec4 breezePoolPos[${this.count}];
uniform vec3 breezePoolColour[${this.count}];
uniform vec4 breezePoolDir[${this.count}];
uniform float breezePoolInner[${this.count}];`)
      .replace("#include <lights_fragment_end>", `for (int i = 0; i < ${this.count}; i++) {
  vec3 toPool = breezePoolPos[i].xyz - geometryPosition;
  float d2 = dot(toPool, toPool);
  float window = max(0.0, 1.0 - d2 / (breezePoolPos[i].w * breezePoolPos[i].w));
  if (window <= 0.0) continue;
  IncidentLight pool;
  pool.direction = toPool * inversesqrt(max(d2, 1e-6));
  float cone = breezePoolDir[i].w < -1.0 ? 1.0
    : smoothstep(breezePoolDir[i].w, breezePoolInner[i], dot(-pool.direction, breezePoolDir[i].xyz));
  if (cone <= 0.0) continue;
  pool.color = PI * breezePoolColour[i] * window * window * cone;
  pool.visible = true;
  ${lightmapped ? "irradiance += pool.color * saturate(dot(geometryNormal, pool.direction));" : ""}
  RE_Direct(pool, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight);
}
#include <lights_fragment_end>`);
  }
}
