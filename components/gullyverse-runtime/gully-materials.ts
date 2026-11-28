import * as THREE from "three";
import type { Budget } from "./device-tier";

/**
 * Shared procedural surfaces for the night gully (docs/runtime/PHASE1-NIGHT-GULLY-PLAN.md).
 *
 * Three tileable RGBA textures are generated once per visit (1024 px on high-class devices, 512 otherwise) and
 * reused by every classified material through world-space projection, so the baked lightmap UVs never change:
 *
 *   plaster  peeling lime-wash: R albedo detail, G roughness, B height, A damp streaks      (tile 4.0 m)
 *   ground   wet charcoal:      R albedo grain,  G roughness, B height, A puddle field      (tile 3.5 m)
 *   rust     rusted iron:       R albedo detail, G roughness, B pitting, A rust bloom      (tile 1.5 m)
 *
 * They are DataTextures (not canvas textures) so the alpha channel is stored exactly, not premultiplied.
 * A second, larger-scale lookup breaks up the tiling: puddles on every tier (ground fragments only), plaster
 * patches on high and medium.
 */
export type SurfaceClass = "plaster" | "ground" | "road" | "rust" | "shutter";
type Sheet = "plaster" | "ground" | "rust";
const sheetOf: Record<SurfaceClass, Sheet> = { plaster: "plaster", ground: "ground", road: "ground", rust: "rust", shutter: "rust" };
const tile: Record<Sheet, number> = { plaster: 4.0, ground: 3.5, rust: 1.5 };

/** The pinned night palette (linear values are derived in the shaders). */
export const palette = {
  charcoal: "#2b2e31", rust: "#6e4127", chalk: "#d3ccbc", sodium: "#c4883e", tube: "#dbeaee",
} as const;

// Classification by exported material name (the name audit is in the Phase 1 report).
const shutter = /rolling shutter|shutter slat|roll-?down/i;
const rust = /galvan|zinc|steel|iron|gate le|hinge|pipe|conduit|rainwater|gutter lip|downpipe|metal|rail(ing)?\b|grille|bracket/i;
const ground = /asphalt|road|ramp|apron|slab|ground|paving|pavement|kerb|curb|silt channel|drain/i;
const plaster = /render|plaster|lime|mineral concrete|house shell|building|parapet|coping|boundary wall|compound wall|pier cap|wall finish|column|plinth/i;
const excluded = /glaz|glass|window detail|sash|timber|shutter green|graffiti|poster|placeholder|sign|fascia|panel|lettering|title|led|screen|lamp|diffuser|tube|character|audience|person|people|crowd|water/i;

/** Surface class for a material name, or null for surfaces left as exported. */
export function classifySurface(name: string): SurfaceClass | null {
  if (excluded.test(name)) return null;
  if (shutter.test(name)) return "shutter";
  if (ground.test(name)) return "ground";
  if (rust.test(name)) return "rust";
  if (plaster.test(name)) return "plaster";
  return null;
}

/** Seeded PRNG (mulberry32): the same surfaces on every visit. */
function random(seed: number) {
  return () => {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Tileable value noise with `px` x `py` lattice cells across the texture, smoothstep-interpolated. */
function valueNoise(size: number, px: number, py: number, rand: () => number) {
  const lattice = new Float32Array(px * py);
  for (let i = 0; i < lattice.length; i++) lattice[i] = rand();
  const out = new Float32Array(size * size);
  const sx = px / size, sy = py / size;
  for (let y = 0; y < size; y++) {
    const fy = y * sy, iy = Math.floor(fy), ty = fy - iy, wy = ty * ty * (3 - 2 * ty);
    const row0 = (iy % py) * px, row1 = ((iy + 1) % py) * px;
    for (let x = 0; x < size; x++) {
      const fx = x * sx, ix = Math.floor(fx), tx = fx - ix, wx = tx * tx * (3 - 2 * tx);
      const x0 = ix % px, x1 = (ix + 1) % px;
      const a = lattice[row0 + x0] + (lattice[row0 + x1] - lattice[row0 + x0]) * wx;
      const b = lattice[row1 + x0] + (lattice[row1 + x1] - lattice[row1 + x0]) * wx;
      out[y * size + x] = a + (b - a) * wy;
    }
  }
  return out;
}

/** Fractal sum of tileable value noise, normalised to 0..1. */
function fbm(size: number, px: number, py: number, octaves: number, rand: () => number) {
  const out = new Float32Array(size * size);
  let amplitude = 1, total = 0;
  for (let o = 0; o < octaves; o++) {
    const layer = valueNoise(size, px << o, py << o, rand);
    for (let i = 0; i < out.length; i++) out[i] += layer[i] * amplitude;
    total += amplitude; amplitude *= 0.5;
  }
  let lo = Infinity, hi = -Infinity;
  for (let i = 0; i < out.length; i++) { out[i] /= total; lo = Math.min(lo, out[i]); hi = Math.max(hi, out[i]); }
  const span = Math.max(1e-6, hi - lo);
  for (let i = 0; i < out.length; i++) out[i] = (out[i] - lo) / span;
  return out;
}

/** Hairline cracks: wandering, occasionally branching random walks (wrapping, so the sheet still tiles). */
function cracks(size: number, count: number, rand: () => number) {
  const out = new Float32Array(size * size);
  const walk = (x: number, y: number, angle: number, length: number, strength: number, depth: number) => {
    for (let s = 0; s < length; s++) {
      angle += (rand() - 0.5) * 0.5;
      x += Math.cos(angle); y += Math.sin(angle);
      const ix = ((Math.round(x) % size) + size) % size, iy = ((Math.round(y) % size) + size) % size;
      out[iy * size + ix] = Math.max(out[iy * size + ix], strength * (1 - s / length * 0.6));
      if (depth < 2 && rand() < 0.006) walk(x, y, angle + (rand() < 0.5 ? 0.9 : -0.9), length * 0.4, strength * 0.7, depth + 1);
    }
  };
  for (let c = 0; c < count; c++) {
    walk(rand() * size, rand() * size, rand() * Math.PI * 2, size * (0.08 + rand() * 0.22), 0.6 + rand() * 0.4, 0);
  }
  return out;
}

const smooth = (a: number, b: number, x: number) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const byte = (v: number) => Math.max(0, Math.min(255, Math.round(v * 255)));

function plasterSheet(size: number) {
  const rand = random(0x9a1e);
  // Fine lime-wash grain, a soft tonal drift, small flakes of exposed render with lighter broken rims, thin
  // cracks, and vertical damp runs (A). No large blotches: the macro lookup in the shader adds the slow variation.
  const base = fbm(size, 8, 8, 5, rand), drift = fbm(size, 3, 3, 3, rand), peel = fbm(size, 8, 8, 5, rand);
  const streak = fbm(size, 32, 2, 3, rand), crack = cracks(size, Math.round(9 * size / 1024) + 4, rand);
  const data = new Uint8Array(size * size * 4);
  for (let i = 0; i < size * size; i++) {
    const flaked = smooth(0.66, 0.73, peel[i]), rim = Math.max(0, smooth(0.62, 0.68, peel[i]) - flaked) * 0.5;
    let albedo = 1 + 0.16 * (base[i] - 0.5) + 0.12 * (drift[i] - 0.5);
    // Peeled patches show darker render beneath; the lifted paint edge casts a thin shadow line and catches light.
    albedo = albedo * (1 - flaked) + (0.52 + 0.08 * base[i]) * flaked + 0.1 * rim - 0.16 * Math.max(0, smooth(0.64, 0.665, peel[i]) - smooth(0.665, 0.69, peel[i]));
    albedo *= 1 - 0.45 * crack[i];
    data[i * 4] = byte(albedo / 1.5);
    data[i * 4 + 1] = byte(0.35 + 0.35 * base[i] + 0.3 * flaked);
    data[i * 4 + 2] = byte(0.6 + 0.15 * base[i] - 0.4 * flaked + 0.18 * rim - 0.35 * crack[i]);
    data[i * 4 + 3] = byte(smooth(0.38, 0.8, streak[i]));
  }
  return data;
}

function groundSheet(size: number) {
  const rand = random(0x6a0d);
  const grain = fbm(size, 64, 64, 3, rand), stain = fbm(size, 3, 3, 4, rand), puddle = fbm(size, 2, 2, 5, rand);
  const data = new Uint8Array(size * size * 4);
  for (let i = 0; i < size * size; i++) {
    data[i * 4] = byte((0.9 + 0.36 * (grain[i] - 0.5) - 0.2 * (stain[i] - 0.5)) / 1.5);
    data[i * 4 + 1] = byte(grain[i]);
    data[i * 4 + 2] = byte(0.55 * grain[i] + 0.45 * (1 - puddle[i]));
    data[i * 4 + 3] = byte(puddle[i]);
  }
  return data;
}

function rustSheet(size: number) {
  const rand = random(0x4057);
  const pit = fbm(size, 24, 24, 3, rand), bloom = fbm(size, 4, 4, 5, rand), streak = fbm(size, 24, 2, 3, rand);
  const data = new Uint8Array(size * size * 4);
  for (let i = 0; i < size * size; i++) {
    data[i * 4] = byte((0.78 + 0.44 * pit[i]) / 1.5);
    data[i * 4 + 1] = byte(pit[i]);
    data[i * 4 + 2] = byte(pit[i]);
    data[i * 4 + 3] = byte(Math.min(1, bloom[i] * 0.85 + 0.3 * smooth(0.5, 0.9, streak[i]) - 0.05));
  }
  return data;
}

/** The three shared surface sheets for one visit. */
export class SurfaceLibrary {
  readonly textures: Record<Sheet, THREE.DataTexture>;
  readonly generationMs: number;
  constructor(private budget: Budget) {
    const started = performance.now();
    const size = budget.textureSize;
    const make = (data: Uint8Array) => {
      const texture = new THREE.DataTexture(data, size, size, THREE.RGBAFormat, THREE.UnsignedByteType);
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
      texture.magFilter = THREE.LinearFilter;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      texture.generateMipmaps = true;
      texture.anisotropy = budget.anisotropy;
      texture.colorSpace = THREE.NoColorSpace; // packed data, decoded in the shader
      texture.needsUpdate = true;
      return texture;
    };
    this.textures = { plaster: make(plasterSheet(size)), ground: make(groundSheet(size)), rust: make(rustSheet(size)) };
    this.generationMs = performance.now() - started;
  }
  texture(surface: SurfaceClass) { return this.textures[sheetOf[surface]]; }
  /** Program cache key part (the code differs by class and by whether bump and macro lookups are on). */
  key(surface: SurfaceClass) { return `${surface}-b${this.budget.bump}-m${this.budget.tier === "low" ? 0 : 1}`; }

  /**
   * Shader code for one material: `declare` (fragment globals), `albedo` (after vertex colour), `roughness` (after the
   * matte roughness floor) and `normal` (after the normal maps). Requires the vBreezeWorld / vBreezeNormal varyings.
   *
   * Plaster materials also take the ground sheet (`breezeGroundSheet`): the export reuses one concrete material for a
   * building's base walls and the walkway slab in front of them, so faces pointing up are treated as wet ground
   * (grain, puddles, wet roughness) and the rest as plaster.
   */
  shader(surface: SurfaceClass) {
    const scale = (1 / tile[sheetOf[surface]]).toFixed(4);
    const groundScale = (1 / tile.ground).toFixed(4);
    const macro = this.budget.tier !== "low";
    const bump = this.budget.bump;
    const declare = `uniform sampler2D breezeSurface;
${surface === "plaster" ? "uniform sampler2D breezeGroundSheet;" : ""}
float breezeHeight = 0.5, breezeWet = 0.0, breezeRust = 0.0, breezeFloor = 0.0, breezeKerb = 0.0;
// Walking-surface height (measured 27 Nov 2026): the plaza is flat at 7.2 m; the lane rises from 6.0 m along the
// 1:20 ramp to the gate (top at z = -14).
float breezeGroundY(float z) { return clamp(7.2 - (z + 14.0) * 0.05, 6.0, 7.2); }
// Vertical faces within ~30 cm of the walking surface (step risers, kerb fronts, building bases).
float breezeKerbBand(vec3 world, vec3 normal) {
  return (1.0 - smoothstep(0.18, 0.42, world.y - breezeGroundY(world.z))) * (1.0 - step(0.7, abs(normal.y)));
}
vec4 breezeSheet = vec4(0.5);
vec2 breezeSurfaceUv() {
  vec3 an = abs(normalize(vBreezeNormal));
  vec2 uv = an.y > 0.7 ? vBreezeWorld.xz : (an.x > an.z ? vBreezeWorld.zy : vBreezeWorld.xy);
  return uv * ${scale};
}
// Wet ground on any sheet: grain (optional), puddle field from a large-scale lookup (breaks the tile repeat on
// every tier), wet darkening. The puddle lookup is one extra fetch on ground fragments only.
void breezeGround(sampler2D sheet, vec2 uv, bool grain, inout vec3 albedo) {
  breezeSheet = texture2D(sheet, uv); breezeHeight = breezeSheet.b;
  float field = texture2D(sheet, uv * 0.26 + vec2(0.17, 0.53)).a * 0.7 + breezeSheet.a * 0.3;
  // The lane (z > -15) runs wetter than the plaza.
  breezeWet = smoothstep(0.54, 0.74, field + (breezeSheet.g - 0.5) * 0.08 + (vBreezeWorld.z > -15.0 ? 0.08 : 0.0));
  if (grain) albedo *= breezeSheet.r * 1.5;
  albedo *= mix(1.0, 0.36, breezeWet);
}
// Same convention as three.js perturbNormalArb (bumpmap_pars_fragment): normalised screen derivatives, so
// the bump reads alike at any texture scale; strength is budget.bump.
vec3 breezePerturb(vec3 surfPos, vec3 surfNorm, vec2 dHdxy, float faceDir) {
  vec3 dx = dFdx(surfPos), dy = dFdy(surfPos);
  float lx = length(dx), ly = length(dy);
  if (lx < 1e-8 || ly < 1e-8) return surfNorm; // degenerate quad: no bump (avoids NaN sparkles)
  vec3 sx = dx / lx, sy = dy / ly;
  vec3 r1 = cross(sy, surfNorm), r2 = cross(surfNorm, sx);
  float det = dot(sx, r1) * faceDir;
  vec3 grad = sign(det) * (dHdxy.x * r1 + dHdxy.y * r2);
  vec3 bumped = abs(det) * surfNorm - grad;
  float lb = length(bumped);
  return lb > 1e-8 ? bumped / lb : surfNorm;
}`;
    // Realism rescue: mirror-wet puddles (0.055 … 0.11; 0.10 floor on phones, whose probes are 512) against dry 0.88 … 0.94.
    const groundRoughness = `mix(mix(0.88, 0.94, breezeSheet.g), mix(${this.budget.tier === "low" ? "0.18, 0.22" : "0.055, 0.11"}, breezeSheet.g), breezeWet)`;
    let albedo = "", roughness = "";
    if (surface === "plaster") {
      albedo = `{ breezeFloor = step(0.7, normalize(vBreezeNormal).y);
  if (breezeFloor > 0.5) breezeGround(breezeGroundSheet, vBreezeWorld.xz * ${groundScale}, true, diffuseColor.rgb);
  else {
    vec2 suv = breezeSurfaceUv(); breezeSheet = texture2D(breezeSurface, suv); breezeHeight = breezeSheet.b;
    float detail = breezeSheet.r * 1.5;
    ${macro ? `// A second, rotated lookup blended by the macro field breaks the 4 m repeat of the peel blotches.
    detail = mix(detail, texture2D(breezeSurface, mat2(0.8, -0.6, 0.6, 0.8) * suv * 0.73 + vec2(0.37, 0.11)).r * 1.5,
      smoothstep(0.3, 0.7, texture2D(breezeSurface, suv * 0.23 + vec2(0.31, 0.17)).g));` : ""}
    ${macro ? `float big = texture2D(breezeSurface, suv * 0.23 + vec2(0.31, 0.17)).g; detail *= 0.86 + 0.24 * big; float damp = breezeSheet.a * smoothstep(0.35, 0.75, big);`
    : "float damp = breezeSheet.a * 0.6;"}
    detail *= mix(0.88, 1.0, breezeHeight);
    float plasterTone = detail * (1.0 - 0.58 * damp);
    // Step risers, kerb fronts and building bases share the concrete material: they read as damp ground concrete.
    breezeKerb = breezeKerbBand(vBreezeWorld, normalize(vBreezeNormal));
    float kerbTone = 1.0;
    if (breezeKerb > 0.001) {
      vec4 kerbSheet = texture2D(breezeGroundSheet, suv * ${(tile.plaster / tile.ground).toFixed(4)});
      kerbTone = kerbSheet.r * 1.5 * 0.7;
      breezeHeight = mix(breezeHeight, kerbSheet.b, breezeKerb);
    }
    diffuseColor.rgb *= mix(plasterTone, kerbTone, breezeKerb);
    // Contact occlusion at the wall-to-floor seam: the bottom 0.45 m darkens toward the floor (0.28 at the seam).
    diffuseColor.rgb *= mix(0.28, 1.0, smoothstep(0.0, 0.45, vBreezeWorld.y - breezeGroundY(vBreezeWorld.z)));
    breezeWet = damp * (1.0 - breezeKerb);
  } }`;
      roughness = `roughnessFactor = breezeFloor > 0.5 ? ${groundRoughness} : mix(clamp(mix(0.85, 0.97, breezeSheet.g) - 0.08 * breezeWet, 0.0, 1.0), 0.9, breezeKerb);`;
    } else if (surface === "ground" || surface === "road") {
      albedo = `{ breezeFloor = 1.0; breezeGround(breezeSurface, breezeSurfaceUv(), ${surface === "ground"}, diffuseColor.rgb); }`;
      roughness = `roughnessFactor = ${groundRoughness};`;
    } else {
      albedo = `{ vec2 suv = breezeSurfaceUv(); breezeSheet = texture2D(breezeSurface, suv); breezeHeight = breezeSheet.b;
  breezeRust = smoothstep(0.55, 0.84, breezeSheet.a);
  vec3 rustTone = vec3(0.157, 0.052, 0.020) * (0.7 + 0.6 * breezeSheet.r * 1.5);
  diffuseColor.rgb = mix(diffuseColor.rgb * breezeSheet.r * 1.5, rustTone, breezeRust * 0.78);
  ${surface === "shutter" ? "breezeHeight = mix(breezeHeight, 0.5 + 0.5 * sin(vBreezeWorld.y * 83.776), 0.75);" : ""} }`;
      roughness = `roughnessFactor = mix(roughnessFactor, mix(0.78, 0.92, breezeSheet.g), breezeRust);
metalnessFactor = max(metalnessFactor * (1.0 - 0.85 * breezeRust), 0.35 * (1.0 - breezeRust));`;
    }
    const normal = bump > 0
      ? `normal = breezePerturb(-vViewPosition, normal, vec2(dFdx(breezeHeight), dFdy(breezeHeight)) * ${(bump * (surface === "shutter" ? 1.6 : 1)).toFixed(3)} * (1.0 - breezeWet), faceDirection);`
      : "";
    return { declare, albedo, roughness, normal };
  }

  dispose() { Object.values(this.textures).forEach(texture => texture.dispose()); }
}

/**
 * The palette grade, applied to the albedo of lightmapped surfaces (not people, screens, LEDs or the
 * navigation board): saturation capped at 0.65 (keeps the pinned rust and sodium tones), magenta and cyan
 * attenuated by 70% and dimmed a little, on plaster terracotta attenuated by 85%, and on ground 60% of all chroma.
 */
export const gradeDeclare = `vec3 breezeRgb2hsv(vec3 c) {
  vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
  vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
  vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
  float d = q.x - min(q.w, q.y);
  return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
}
vec3 breezeHsv2rgb(vec3 c) {
  vec3 p = abs(fract(c.xxx + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
  return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}`;
/**
 * `surface`: plaster also loses terracotta (only where it is saturated enough to be terracotta), and its up-facing
 * faces are graded as ground; ground and road lose 60% of all chroma (wet charcoal, not brown).
 */
export function gradeCode(surface: SurfaceClass | null) {
  const plasterOnly = surface === "plaster", ground = surface === "ground" || surface === "road";
  return `{
  vec3 hsv = breezeRgb2hsv(sqrt(max(diffuseColor.rgb, vec3(0.0))));
  float magenta = smoothstep(0.76, 0.80, hsv.x) * (1.0 - smoothstep(0.975, 0.995, hsv.x));
  float cyan = smoothstep(0.42, 0.45, hsv.x) * (1.0 - smoothstep(0.58, 0.61, hsv.x));
  float attenuate = 0.7 * max(magenta, cyan);
  float floorFacing = ${plasterOnly ? "max(step(0.7, normalize(vBreezeNormal).y), breezeKerbBand(vBreezeWorld, normalize(vBreezeNormal)))" : "0.0"};
  float terra = ${plasterOnly ? "(1.0 - smoothstep(0.10, 0.14, hsv.x)) * step(hsv.x, 0.5) * smoothstep(0.08, 0.2, hsv.y) * (1.0 - floorFacing)" : "0.0"};
  attenuate = max(attenuate, 0.85 * terra);
  ${ground ? "attenuate = max(attenuate, 0.6);" : plasterOnly ? "attenuate = max(attenuate, 0.6 * floorFacing);" : ""}
  ${surface === "ground" ? "hsv.z *= 0.78;" : surface === "road" ? "hsv.z *= 0.85;" : plasterOnly ? "hsv.z *= mix(1.0, 0.6, floorFacing);" : ""}
  hsv.y = min(hsv.y * (1.0 - attenuate), 0.65);
  hsv.z *= (1.0 - 0.12 * magenta) * (1.0 - 0.15 * terra);
  vec3 graded = breezeHsv2rgb(hsv);
  diffuseColor.rgb = graded * graded;
}`;
}
