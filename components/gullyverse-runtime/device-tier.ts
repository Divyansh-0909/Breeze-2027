import { Vector3 } from "three";
import type * as THREE from "three";

/**
 * Device class and render budgets, decided once per visit (docs/runtime/PHASE1-NIGHT-GULLY-PLAN.md).
 *
 *   high    discrete or Apple-silicon GPU on a desktop pointer
 *   medium  integrated laptop GPUs (Intel UHD / Iris, AMD Radeon Graphics) and unknown desktops
 *   low     phones and tablets (coarse pointer or narrow screen), ≤ 4 cores, ≤ 4 GB, software renderers
 *
 * `?device=high|medium|low` pins the class. The budgets bound every later phase: the DPR governor's top step,
 * shadow casters (the bake holds all shadows today, so none cast), runtime lamp highlights, procedural texture
 * size, haze planes and whether post-processing is allowed.
 */
export type DeviceTier = "high" | "medium" | "low";
export type Budget = {
  tier: DeviceTier;
  dprCap: number;
  shadowCasters: number;
  shadowMapSize: number;
  localLights: number;
  textureSize: number;
  anisotropy: number;
  bump: number;
  hazePlanes: number;
  bloom: boolean;
  fogDensity: number;
  sharpProbes: boolean;
  /** Distinct crowd avatars (each is 2-3 draw calls and one download). */
  crowdAvatars: number;
};

const budgets: Record<DeviceTier, Omit<Budget, "tier">> = {
  high: { dprCap: 1.75, shadowCasters: 2, shadowMapSize: 1024, localLights: 8, textureSize: 1024, anisotropy: 16, bump: 0.42,
    hazePlanes: 4, bloom: true, fogDensity: 0.011, sharpProbes: true, crowdAvatars: 15 },
  medium: { dprCap: 1.5, shadowCasters: 1, shadowMapSize: 1024, localLights: 6, textureSize: 512, anisotropy: 8, bump: 0.38,
    hazePlanes: 3, bloom: false, fogDensity: 0.011, sharpProbes: false, crowdAvatars: 15 },
  low: { dprCap: 1.25, shadowCasters: 1, shadowMapSize: 512, localLights: 4, textureSize: 512, anisotropy: 4, bump: 0.08,
    hazePlanes: 2, bloom: false, fogDensity: 0.012, sharpProbes: false, crowdAvatars: 8 },
};

const software = /swiftshader|llvmpipe|softpipe|software|basic render/i;
const weakMobileGpu = /mali-[34]|mali-t|adreno \(tm\) [3-5]\d\d|powervr|sgx/i;
const integrated = /intel|uhd|iris|radeon\(tm\) graphics|radeon graphics|vega \d+ graphics|adreno|mali/i;

/** Classifies from the renderer string and device hints. Pure, for tests. */
export function classifyDevice(hints: {
  renderer: string; coarse: boolean; narrow: boolean; cores: number; memory?: number;
}): DeviceTier {
  if (software.test(hints.renderer)) return "low";
  if (hints.coarse || hints.narrow || weakMobileGpu.test(hints.renderer)) return "low";
  if (hints.cores > 0 && hints.cores <= 4) return "low";
  if (hints.memory !== undefined && hints.memory <= 4) return "low";
  if (integrated.test(hints.renderer)) return "medium";
  if (/nvidia|geforce|rtx|gtx|quadro|radeon (rx|pro)|apple m\d|apple gpu/i.test(hints.renderer)) return "high";
  return "medium";
}

let decided: Budget | null = null;

/** The visit's budget (decided on first call; `gl` supplies the unmasked renderer string). */
export function deviceBudget(gl?: WebGLRenderingContext | WebGL2RenderingContext): Budget {
  if (decided) return decided;
  const requested = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("device") : null;
  let tier: DeviceTier;
  if (requested === "high" || requested === "medium" || requested === "low") tier = requested;
  else if (typeof window === "undefined") tier = "medium";
  else {
    let renderer = "";
    try {
      const context = gl ?? document.createElement("canvas").getContext("webgl2");
      const debug = context?.getExtension("WEBGL_debug_renderer_info");
      renderer = String(context?.getParameter(debug ? debug.UNMASKED_RENDERER_WEBGL : context.RENDERER) ?? "");
    } catch { /* unknown renderer: medium */ }
    tier = classifyDevice({
      renderer,
      coarse: window.matchMedia("(pointer: coarse)").matches,
      narrow: window.matchMedia("(max-width: 699px)").matches,
      cores: navigator.hardwareConcurrency ?? 0,
      memory: (navigator as Navigator & { deviceMemory?: number }).deviceMemory,
    });
  }
  decided = { tier, ...budgets[tier] };
  return decided;
}

/** Test hook: forget the decided budget. */
export function resetDeviceBudget() { decided = null; }

/**
 * Keeps at most `budget.shadowCasters` shadow-casting lights (nearest the camera first) at `budget.shadowMapSize`.
 * Returns how many cast after the cap. Run whenever lights are added (chunk mounts, later-phase fixtures).
 */
export function enforceShadowBudget(scene: THREE.Object3D, camera: THREE.Camera, budget: Budget) {
  const casters: THREE.Light[] = [];
  scene.traverse(object => {
    const light = object as THREE.Light;
    if (light.isLight && light.castShadow) casters.push(light);
  });
  if (!casters.length) return 0;
  const at = new Vector3();
  const distance = new Map(casters.map(light => [light, light.getWorldPosition(at).distanceToSquared(camera.position)]));
  casters.sort((a, b) => distance.get(a)! - distance.get(b)!);
  casters.forEach((light, index) => {
    if (index >= budget.shadowCasters) { light.castShadow = false; return; }
    const shadow = (light as THREE.Light & { shadow?: THREE.LightShadow }).shadow;
    if (shadow && (shadow.mapSize.x > budget.shadowMapSize || shadow.mapSize.y > budget.shadowMapSize)) {
      shadow.mapSize.set(budget.shadowMapSize, budget.shadowMapSize);
      shadow.map?.dispose();
      shadow.map = null;
    }
  });
  return Math.min(casters.length, budget.shadowCasters);
}
