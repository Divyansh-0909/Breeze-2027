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

export class LightPools {
  readonly count: number;
  readonly pools: Pool[];
  readonly uniforms: { breezePoolPos: { value: THREE.Vector4[] }; breezePoolColour: { value: THREE.Color[] } };
  private view = new THREE.Vector3();

  constructor(budget: Budget) {
    this.count = budget.tier === "low" ? 3 : 4;
    this.pools = Array.from({ length: this.count }, () => ({ position: new THREE.Vector3(), radius: 1, colour: new THREE.Color(0, 0, 0), intensity: 0 }));
    this.uniforms = {
      breezePoolPos: { value: Array.from({ length: this.count }, () => new THREE.Vector4(0, -1000, 0, 1)) },
      breezePoolColour: { value: Array.from({ length: this.count }, () => new THREE.Color(0, 0, 0)) },
    };
  }

  /** Sets pool `index` (ignored past the tier's count). */
  set(index: number, position: THREE.Vector3Like, radius: number, colour: THREE.ColorRepresentation, intensity: number) {
    const pool = this.pools[index];
    if (!pool) return;
    pool.position.set(position.x, position.y, position.z); pool.radius = radius; pool.colour.set(colour); pool.intensity = intensity;
  }

  /** Converts the pools to the camera's view space. Call once per frame before rendering. */
  update(camera: THREE.Camera) {
    camera.updateMatrixWorld();
    this.pools.forEach((pool, i) => {
      this.view.copy(pool.position).applyMatrix4(camera.matrixWorldInverse);
      this.uniforms.breezePoolPos.value[i].set(this.view.x, this.view.y, this.view.z, Math.max(pool.radius, 0.01));
      this.uniforms.breezePoolColour.value[i].copy(pool.colour).multiplyScalar(pool.intensity);
    });
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
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", `#include <common>
uniform vec4 breezePoolPos[${this.count}];
uniform vec3 breezePoolColour[${this.count}];`)
      .replace("#include <lights_fragment_end>", `for (int i = 0; i < ${this.count}; i++) {
  vec3 toPool = breezePoolPos[i].xyz - geometryPosition;
  float d2 = dot(toPool, toPool);
  float window = max(0.0, 1.0 - d2 / (breezePoolPos[i].w * breezePoolPos[i].w));
  if (window <= 0.0) continue;
  IncidentLight pool;
  pool.direction = toPool * inversesqrt(max(d2, 1e-6));
  pool.color = PI * breezePoolColour[i] * window * window;
  pool.visible = true;
  ${lightmapped ? "irradiance += pool.color * saturate(dot(geometryNormal, pool.direction));" : ""}
  RE_Direct(pool, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight);
}
#include <lights_fragment_end>`);
  }
}
