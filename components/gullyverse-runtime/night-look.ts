import * as THREE from "three";
import type { Budget } from "./device-tier";

/**
 * Global night-gully look (docs/runtime/PHASE1-NIGHT-GULLY-PLAN.md, agreed with the Antigravity review):
 * AgX at exposure 1.10, exponential-squared fog in the near-black void colour (the background matches, so
 * unbuilt space and distance fade into the same darkness), and a cool night floor in the lightmap decode
 * (baked-assets.ts) so shaded walls bottom out at deep charcoal instead of pure black.
 *
 * The fog thins to nothing while the aerial map is open (its camera is 60 m and more from the street).
 */
export const voidColour = "#050709";
export const exposure = 1.1;
/** Added to decoded lightmap irradiance before lightMapIntensity (GLSL vec3). */
// Realism rescue (27 Nov): 0.022 -> 0.011 (0.0045 lost the plaza buildings), so unlit corners and upper walls sink to deep charcoal (#0c0e12).
export const nightFloor = "vec3(0.82, 0.89, 1.0) * 0.011";

export function applyNightLook(gl: THREE.WebGLRenderer, scene: THREE.Scene, budget: Budget) {
  gl.toneMapping = THREE.AgXToneMapping;
  gl.toneMappingExposure = exposure;
  scene.background = new THREE.Color(voidColour);
  // Fog stays attached for the whole visit (density only changes) so no material ever recompiles.
  const fog = new THREE.FogExp2(voidColour, budget.fogDensity);
  scene.fog = fog;
  return {
    fog,
    /** Eases the fog density toward its walking value, or to zero on the map. Call every frame. */
    update(mapOpen: boolean, delta: number, reduced: boolean) {
      const target = mapOpen ? 0 : budget.fogDensity;
      fog.density = reduced ? target : THREE.MathUtils.damp(fog.density, target, 4, Math.min(delta, 0.2));
    },
  };
}
