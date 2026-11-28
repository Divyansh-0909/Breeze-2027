import * as THREE from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import type { Fidelity } from "./fidelity";
import type { Cone } from "./light-pools";
import { blobTexture, decalAtlas, emissiveAtlas, hazeTexture, propAtlas, type Region } from "./dressing-textures";

/**
 * Phase 2 courtyard dressing (docs/runtime/PHASE2-COURTYARD-SCREEN-PLAN.md): overhead cables, the screen truss and
 * lamp housings, lived-in windows and lamp lenses, lamp glow, grounded props with contact shadows, wall stencils and
 * flyers, and dust haze in front of the screen. Each family is merged into one mesh (one draw call). New fixtures
 * light the courtyard through the shared light pools (light-pools.ts); the screen pool and the haze follow the
 * film's average colour, sampled from an 8 × 8 canvas twice a second.
 *
 * All positions come from ray-cast surveys of the locked scene (plaza floor y = 7.2; facades left x ≈ −15.7 … −17.3
 * stepping back per floor, right x ≈ 15.5 … 16.3, back z ≈ −50.3 … −51.8; screen centre (0, 11.59, −45.72)).
 */
export const FLOOR = 7.2;
export const SODIUM = new THREE.Color("#c4883e"), TUBE = new THREE.Color("#dbeaee"), TUNGSTEN = new THREE.Color("#ffb870");
export type V = [number, number, number];
export const vec = (p: V) => new THREE.Vector3(...p);

// ---------------------------------------------------------------- geometry helpers

/** A sagging wire: parabola between two anchors (sag as a fraction of the span), as a thin 4-sided tube. */
export function wire(a: V, b: V, sag: number, radius: number) {
  const A = vec(a), B = vec(b), span = A.distanceTo(B), drop = span * sag;
  const points = Array.from({ length: 9 }, (_, i) => {
    const t = i / 8;
    return new THREE.Vector3().lerpVectors(A, B, t).add(new THREE.Vector3(0, -4 * drop * t * (1 - t), 0));
  });
  const segments = span > 15 ? 18 : 12;
  return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points), segments, radius, 4, false);
}
/** A bundle of `count` wires between nearby anchors with small, deterministic spread. */
function bundle(a: V, b: V, count: number, sag: number, spread: number, radius: [number, number], out: THREE.BufferGeometry[], salt: number) {
  for (let i = 0; i < count; i++) {
    const j = (k: number) => Math.sin(salt * 12.9898 + i * 78.233 + k * 37.719) * spread;
    out.push(wire([a[0] + j(1) * 0.3, a[1] + j(2), a[2] + j(3)], [b[0] + j(4) * 0.3, b[1] + j(5), b[2] + j(6)],
      sag * (0.85 + 0.3 * Math.abs(Math.sin(salt + i))), radius[0] + (radius[1] - radius[0]) * Math.abs(Math.sin(salt * 3 + i * 1.7))));
  }
}
/** A straight pipe between two points (open cylinder, 4 sides). */
export function strut(a: THREE.Vector3, b: THREE.Vector3, radius: number) {
  const dir = new THREE.Vector3().subVectors(b, a), length = dir.length();
  const g = new THREE.CylinderGeometry(radius, radius, length, 4, 1, true);
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize()));
  g.translate((a.x + b.x) / 2, (a.y + b.y) / 2, (a.z + b.z) / 2);
  return g;
}
/** Remaps a geometry's 0..1 UVs into an atlas region. */
export function toRegion(g: THREE.BufferGeometry, r: Region) {
  const uv = g.getAttribute("uv") as THREE.BufferAttribute;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, r[0] + uv.getX(i) * (r[2] - r[0]), r[1] + uv.getY(i) * (r[3] - r[1]));
  return g;
}
/** A box whose six faces map to atlas regions (+x, −x, +y, −y, +z, −z). */
export function atlasBox(w: number, h: number, d: number, faces: Region[]) {
  const g = new THREE.BoxGeometry(w, h, d);
  const uv = g.getAttribute("uv") as THREE.BufferAttribute;
  for (let f = 0; f < 6; f++) for (let k = 0; k < 4; k++) {
    const i = f * 4 + k, r = faces[f];
    uv.setXY(i, r[0] + uv.getX(i) * (r[2] - r[0]), r[1] + uv.getY(i) * (r[3] - r[1]));
  }
  return g.toNonIndexed();
}
/** A flat quad facing `normal`, centred at `centre`, with UVs in `region` and an optional vertex brightness. */
export function quad(centre: THREE.Vector3, normal: THREE.Vector3, width: number, height: number, region: Region, brightness = 1, roll = 0) {
  const g = toRegion(new THREE.PlaneGeometry(width, height), region);
  if (roll) g.rotateZ(roll);
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  g.translate(centre.x, centre.y, centre.z);
  const n = g.getAttribute("position").count;
  g.setAttribute("color", new THREE.Float32BufferAttribute(new Array(n * 3).fill(brightness), 3));
  return g.toNonIndexed();
}
/** Merge helper: every part as non-indexed with the same attribute set. */
function merge(parts: THREE.BufferGeometry[], keep: string[]) {
  const ready = parts.map(p => {
    const g = p.index ? p.toNonIndexed() : p;
    for (const name of Object.keys(g.attributes)) if (!keep.includes(name)) g.deleteAttribute(name);
    return g;
  });
  const merged = mergeGeometries(ready, false)!;
  ready.forEach(g => g.dispose()); parts.forEach(g => g.dispose());
  merged.computeBoundingSphere(); merged.computeBoundingBox();
  return merged;
}

/** Finds the facing surface along a ray (nearest hit on visible chunk meshes). */
export function surfaceAt(root: THREE.Object3D, origin: V, direction: V, skipGlass = true) {
  const ray = new THREE.Raycaster(vec(origin), vec(direction).normalize(), 0.05, 14);
  const usable = (m: THREE.Material | THREE.Material[]) => {
    const material = Array.isArray(m) ? m[0] : m;
    if (!material || material.transparent) return false;
    return !skipGlass || !/glaz/i.test(`${material.name} ${material.userData.breezeSourceName ?? ""}`);
  };
  const hits = ray.intersectObject(root, true).filter(h => h.object.visible && usable((h.object as THREE.Mesh).material));
  return hits[0] ? { point: hits[0].point, normal: vec(direction).negate().normalize() } : null;
}

// ---------------------------------------------------------------- layout (surveyed)

const truss = { x: 7.9, z: -45.7, depth: 0.45, top: 15.2, chord: 0.025, lacing: 0.016 };
/** Lamps: position (housing on the wall), pool centre and radius, colour, kind. Index = light pool index. */
/**
 * `bulb`: a bare hanging tungsten bulb (cord up to height `cord`); `practical`: an existing baked fixture that only gains a
 * glow and a pool. `active` limits the lamp's pool to the camera's zone (light-pools.ts registry).
 */
export type Lamp = { kind: "sodium" | "tube" | "bulb" | "practical"; housing: V; facing: V; pool: V; radius: number; colour: THREE.Color;
  intensity: number; soffitFrom?: V; soffit?: number; cord?: number; active?: (eye: THREE.Vector3) => boolean; label?: string; glow?: [number, number]; cone?: Cone };
const lampSpecs: Lamp[] = [
  // Right-wing balcony building: the overhangs reach only ~0.9 m from the wall (to x ≈ 15.1–15.4; probed). The lamps hang
  // just inside the edge, under the roof eave (sodium, ~19.0) and the floor-2 overhang (cool tube, ~15.9), found by a ray
  // cast straight up at mount (soffitFrom); from street level the edge then does not hide them.
  { kind: "sodium", housing: [15.65, 19.1, -29.0], facing: [-1, 0, 0], pool: [14.5, 18.4, -29.2], radius: 14, colour: SODIUM, intensity: 2.6, soffitFrom: [15.15, 17.3, -29.0] },
  { kind: "tube", housing: [15.65, 16.0, -25.6], facing: [-1, 0, 0], pool: [14.5, 15.3, -25.8], radius: 12, colour: TUBE, intensity: 1.3, soffitFrom: [15.3, 14.1, -24.0] },
  { kind: "tube", housing: [-11.5, 13.9, -50.35], facing: [0, 0, 1], pool: [-11.5, 13.6, -49.2], radius: 9, colour: TUBE, intensity: 0.75 },
];
/** Resolves soffit-hung lamps against the scene (falls back to the authored position when nothing is above). */
function placeLamps(plaza: THREE.Object3D): Lamp[] {
  return lampSpecs.map(spec => {
    if (!spec.soffitFrom) return spec;
    const hit = surfaceAt(plaza, spec.soffitFrom, [0, 1, 0], false);
    if (!hit || hit.point.y - spec.soffitFrom[1] > 3) return spec;
    const [x, , z] = spec.soffitFrom, y = hit.point.y;
    const hang = spec.kind === "sodium" ? 0.35 : 0.22;
    return { ...spec, housing: [x, y - hang, z], pool: [x - 0.95, y - 0.9, z], soffit: y };
  });
}
/** Lived-in windows: glazed panes / recesses (plane coordinate, facing, rect), variant 0..3 and brightness. */
const windows: { at: V; normal: V; w: number; h: number; variant: number; brightness: number }[] = [
  { at: [15.77, 11.78, -36.25], normal: [-1, 0, 0], w: 1.44, h: 1.29, variant: 0, brightness: 0.62 },
  { at: [16.24, 14.78, -28.85], normal: [-1, 0, 0], w: 1.44, h: 1.29, variant: 1, brightness: 0.5 },
  { at: [12.02, 14.78, -51.22], normal: [0, 0, 1], w: 1.22, h: 1.29, variant: 2, brightness: 0.55 },
  { at: [12.02, 17.78, -51.67], normal: [0, 0, 1], w: 1.36, h: 1.29, variant: 3, brightness: 0.6 },
  { at: [-10.0, 14.78, -50.95], normal: [0, 0, 1], w: 1.0, h: 1.29, variant: 1, brightness: 0.45 },
  { at: [NaN, 11.78, -24.8], normal: [1, 0, 0], w: 0.85, h: 1.29, variant: 3, brightness: 0.55 },
  { at: [NaN, 14.78, -31.5], normal: [1, 0, 0], w: 1.44, h: 1.29, variant: 1, brightness: 0.55 },
  { at: [NaN, 17.78, -31.5], normal: [1, 0, 0], w: 1.44, h: 1.29, variant: 0, brightness: 0.62 },
  { at: [NaN, 14.78, -38.5], normal: [1, 0, 0], w: 1.2, h: 1.29, variant: 2, brightness: 0.6 },
];
/** Cross-courtyard bundles (anchors snapped to the facades, y 16.5–20.5), gate wires, local runs, screen feeds. */
function cableGeometry(out: THREE.BufferGeometry[], anchor: (p: V) => V) {
  bundle(anchor([-16.7, 19.6, -22.0]), anchor([15.9, 19.1, -27.0]), 5, 0.06, 0.22, [0.016, 0.024], out, 1);
  bundle(anchor([-16.9, 18.8, -38.5]), anchor([16.1, 20.1, -41.0]), 4, 0.055, 0.2, [0.016, 0.022], out, 2);
  bundle(anchor([-16.6, 19.6, -29.5]), [11.5, 18.9, -50.7], 4, 0.05, 0.18, [0.016, 0.022], out, 3);
  bundle([-7.5, 18.3, -15.4], anchor([15.8, 18.7, -19.5]), 4, 0.06, 0.2, [0.016, 0.026], out, 4);
  // Above the gate (lane side and plaza side of the compound wall), short, lower, wall to wall.
  bundle([-3.6, 13.1, -14.7], [3.6, 12.7, -15.3], 5, 0.07, 0.15, [0.016, 0.022], out, 5);
  bundle([-3.6, 14.2, -13.8], [3.6, 14.6, -13.2], 3, 0.06, 0.12, [0.016, 0.02], out, 6);
  // Power drops hanging in the gaps between the centre and side LED panels.
  for (const side of [-1, 1]) for (let k = 0; k < 2; k++) {
    const x = side * (4.5 + k * 0.12);
    out.push(wire([x, truss.top - 0.05, -45.35], [x + side * 0.05, 8.6, -45.3 + k * 0.03], 0.06, 0.032 + 0.01 * k));
  }
  // Screen power feeds: from the top beam down into the PA stacks at both sides.
  for (const side of [-1, 1]) for (let k = 0; k < 3; k++) {
    const x = side * (truss.x + 0.15 + k * 0.08);
    out.push(wire([x, truss.top - 0.05, truss.z + 0.1 + k * 0.06], [side * (8.75 + k * 0.12), FLOOR + 1.9, -45.05 + k * 0.08], 0.09 + k * 0.03,
      0.03 + 0.007 * k));
  }
}

// ---------------------------------------------------------------- materials

function propMaterial(fidelity: Fidelity, parameters: THREE.MeshStandardMaterialParameters, surface: "rust" | null, fill = 0) {
  const material = new THREE.MeshStandardMaterial(parameters);
  material.onBeforeCompile = shader => fidelity.patchProp(shader, surface, fill);
  material.customProgramCacheKey = () => fidelity.propKey(surface, fill) + (parameters.map ? "-map" : "") + (parameters.vertexColors ? "-vc" : "");
  return material;
}

const glowVertex = `
attribute vec3 glowColour;
attribute vec2 glowSize;
varying vec2 vUv;
varying vec3 vColour;
void main() {
  vUv = uv; vColour = glowColour;
  vec4 centre = modelViewMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0);
  centre.xy += position.xy * glowSize;
  centre.z += 0.02; // just in front of the lens (0.15 pulled wide tube halos through the soffit)
  gl_Position = projectionMatrix * centre;
}`;
const glowFragment = `
varying vec2 vUv;
varying vec3 vColour;
void main() {
  float r = length(vUv - 0.5) * 2.0;
  // Realism rescue: a tight core plus a wide soft lobe (light scattering in the night air).
  float a = exp(-r * r * 6.5) * (1.0 - smoothstep(0.25, 1.0, r)) + 0.12 * exp(-r * r * 2.5) * (1.0 - smoothstep(0.5, 1.0, r));
  gl_FragColor = vec4(vColour * a, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}`;
const hazeVertex = `
attribute vec2 hazeSize;
attribute float hazeSeed;
varying vec2 vUv;
varying float vSeed;
#include <fog_pars_vertex>
void main() {
  vUv = uv; vSeed = hazeSeed;
  vec3 centre = (modelMatrix * instanceMatrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
  vec3 toCamera = cameraPosition - centre; toCamera.y = 0.0;
  vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), normalize(toCamera + vec3(1e-4, 0.0, 0.0))));
  vec3 world = centre + right * position.x * hazeSize.x + vec3(0.0, 1.0, 0.0) * position.y * hazeSize.y;
  vec4 mvPosition = viewMatrix * vec4(world, 1.0);
  gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
}`;
const hazeFragment = `
uniform sampler2D hazeNoise;
uniform vec3 hazeColour;
uniform float hazeAlpha;
uniform float hazeTime;
varying vec2 vUv;
varying float vSeed;
#include <fog_pars_fragment>
void main() {
  vec2 p = vUv * vec2(2.2, 1.0) + vec2(hazeTime * 0.006 + vSeed, hazeTime * 0.002);
  float n = texture2D(hazeNoise, p).r * 0.65 + texture2D(hazeNoise, p * 2.3 + vec2(0.37, vSeed)).r * 0.35;
  vec2 e = (vUv - 0.5) * 2.0;
  float edge = 1.0 - smoothstep(0.55, 1.0, length(e * vec2(0.9, 1.15)));
  float bottom = smoothstep(0.0, 0.25, vUv.y);
  gl_FragColor = vec4(hazeColour, hazeAlpha * n * edge * bottom);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  #include <fog_fragment>
}`;

// ---------------------------------------------------------------- mount

export type CourtyardDressing = { group: THREE.Group; update(delta: number, camera: THREE.Camera, video: HTMLVideoElement | null, reduced: boolean): void; dispose(): void };

/**
 * Where zone dressing (zone-dressing.ts, Phase 3) adds its parts: they are merged into the courtyard's families, so
 * a zone costs no extra draw calls. `laneDecals` is a second decal mesh on the gate's lane side (shown only from the
 * lane, where the plaza's props and decals are hidden).
 */
export type DressingSink = {
  plaza: THREE.Object3D; fidelity: Fidelity; lamps: Lamp[];
  steel: THREE.BufferGeometry[]; glow: THREE.BufferGeometry[]; props: THREE.BufferGeometry[]; blobs: THREE.BufferGeometry[];
  decals: THREE.BufferGeometry[]; laneDecals: THREE.BufferGeometry[];
  atlas: { emissive: ReturnType<typeof emissiveAtlas>; props: ReturnType<typeof propAtlas>; decals: ReturnType<typeof decalAtlas> };
};
export type ZoneHooks = { update?(camera: THREE.Camera): void; dispose?(): void };

/** While the camera is in the lane (outside the gate), the plaza's props, their shadows and its wall decals are hidden. */
export const inLane = (camera: THREE.Camera) => camera.position.z > -13.5;

export function mountCourtyardDressing(plaza: THREE.Object3D, fidelity: Fidelity, zones?: (sink: DressingSink) => ZoneHooks): CourtyardDressing {
  const budget = fidelity.budget, size = budget.textureSize;
  const lamps = placeLamps(plaza);
  const group = new THREE.Group(); group.name = "Courtyard dressing";
  const disposables: { dispose(): void }[] = [];
  const add = (mesh: THREE.Object3D, name: string) => { mesh.name = name; group.add(mesh); return mesh; };
  const sink: DressingSink = {
    plaza, fidelity, lamps, steel: [], glow: [], props: [], blobs: [], decals: [], laneDecals: [],
    atlas: { emissive: emissiveAtlas(size), props: propAtlas(size), decals: decalAtlas(size) },
  };
  const hooks = zones?.(sink) ?? {};

  // Cables: one merged mesh. Facade anchors are snapped to the wall surface (upper floors step back).
  const anchor = (p: V): V => {
    const side = Math.sign(p[0]);
    const hit = surfaceAt(plaza, [side * 12, p[1], p[2]], [side, 0, 0], false);
    return hit ? [hit.point.x - side * 0.03, p[1], p[2]] : p;
  };
  const cableParts: THREE.BufferGeometry[] = []; cableGeometry(cableParts, anchor);
  // Service runs to the soffit-hung lamps: along the underside of the overhang, from the wall to each lamp.
  for (const lamp of lamps) if (lamp.soffit !== undefined) {
    const [x, , z] = lamp.housing, y = lamp.soffit - 0.04;
    cableParts.push(wire(anchor([16.4, y, z - 1.4]), [x, y, z], 0.03, 0.012));
  }
  const cableGeometryMerged = merge(cableParts, ["position", "normal"]);
  const cableMaterial = propMaterial(fidelity, { color: 0x0d0e0f, roughness: 0.55, metalness: 0 }, null);
  add(new THREE.Mesh(cableGeometryMerged, cableMaterial), "Overhead cables");
  disposables.push(cableGeometryMerged, cableMaterial);

  // Steel: the screen truss (two towers and a top box beam, 48 mm chords, 32 mm lacing) and lamp housings and cages.
  const steel = sink.steel;
  const half = truss.depth / 2;
  const corners = (x: number) => [[x - half, truss.z - half], [x + half, truss.z - half], [x + half, truss.z + half], [x - half, truss.z + half]];
  for (const side of [-1, 1]) {
    const cx = side * truss.x, c = corners(cx);
    for (const [x, z] of c) steel.push(strut(vec([x, FLOOR, z]), vec([x, truss.top + half, z]), truss.chord));
    for (let y = FLOOR, k = 0; y < truss.top; y += truss.depth, k++) for (let f = 0; f < 4; f++) {
      const [x0, z0] = c[f], [x1, z1] = c[(f + 1) % 4];
      steel.push(strut(vec([x0, y + (k % 2 ? truss.depth : 0), z0]), vec([x1, y + (k % 2 ? 0 : truss.depth), z1]), truss.lacing));
      steel.push(strut(vec([x0, y, z0]), vec([x1, y, z1]), truss.lacing));
    }
  }
  const beamY = truss.top;
  const beam = [[beamY - half, truss.z - half], [beamY - half, truss.z + half], [beamY + half, truss.z + half], [beamY + half, truss.z - half]];
  for (const [y, z] of beam) steel.push(strut(vec([-truss.x - half, y, z]), vec([truss.x + half, y, z]), truss.chord));
  for (let x = -truss.x, k = 0; x < truss.x - 1e-3; x += truss.depth, k++) for (let f = 0; f < 4; f++) {
    const [y0, z0] = beam[f], [y1, z1] = beam[(f + 1) % 4];
    const x1 = Math.min(x + truss.depth, truss.x);
    steel.push(strut(vec([k % 2 ? x1 : x, y0, z0]), vec([k % 2 ? x : x1, y1, z1]), truss.lacing));
  }
  // Lamp housings: caged work lamp (box + cage hoops + wall arm), tube fittings (slim box + two brackets).
  for (const lamp of lamps) {
    const at = vec(lamp.housing), out = vec(lamp.facing);
    if (lamp.soffit !== undefined) { // hanger from the fitting (the tube's centre, the work lamp's arm) up to the overhang
      const base = lamp.kind === "tube" ? at.clone().addScaledVector(out, 0.1).add(new THREE.Vector3(0, 0.035, 0)) : at;
      steel.push(strut(base, vec([base.x, lamp.soffit, base.z]), 0.012));
    }
    if (lamp.kind === "practical") continue;
    if (lamp.kind === "bulb") { // cord up to the ceiling and a small socket
      steel.push(strut(at.clone().add(new THREE.Vector3(0, 0.05, 0)), vec([at.x, lamp.cord ?? at.y + 0.4, at.z]), 0.005));
      const socket = new THREE.CylinderGeometry(0.018, 0.022, 0.05, 6); socket.translate(at.x, at.y + 0.055, at.z); steel.push(socket);
      continue;
    }
    if (lamp.kind === "sodium") {
      const head = at.clone().addScaledVector(out, 0.42);
      const box = new THREE.BoxGeometry(0.34, 0.2, 0.26); box.translate(head.x, head.y, head.z); steel.push(box);
      steel.push(strut(at, head.clone().add(new THREE.Vector3(0, 0.05, 0)), 0.018));
      for (let k = 0; k < 4; k++) {
        const o = (k - 1.5) * 0.08, side = new THREE.Vector3(-out.z, 0, out.x);
        const p = head.clone().addScaledVector(side, o);
        steel.push(strut(p.clone().add(new THREE.Vector3(0, -0.1, 0)), p.clone().add(new THREE.Vector3(0, -0.26, 0)).addScaledVector(out, 0.08), 0.006));
      }
    } else {
      const side = new THREE.Vector3(-out.z, 0, out.x);
      const box = new THREE.BoxGeometry(1.25, 0.07, 0.12);
      box.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1, 0, 0), side));
      const centre = at.clone().addScaledVector(out, 0.1); box.translate(centre.x, centre.y, centre.z); steel.push(box);
      for (const s of [-0.5, 0.5]) steel.push(strut(at.clone().addScaledVector(side, s), centre.clone().addScaledVector(side, s), 0.012));
    }
  }
  const steelGeometry = merge(steel, ["position", "normal"]);
  const steelMaterial = propMaterial(fidelity, { color: 0x7a7d80, roughness: 0.6, metalness: 0.6, envMapIntensity: 1.6 }, "rust");
  add(new THREE.Mesh(steelGeometry, steelMaterial), "Screen truss and lamp housings");
  disposables.push(steelGeometry, steelMaterial);

  // Lived-in windows and lamp lenses: one emissive atlas, one draw.
  const emissive = sink.atlas.emissive;
  const glowParts = sink.glow;
  const windowGlow: { at: THREE.Vector3; normal: THREE.Vector3; w: number; h: number; brightness: number }[] = [];
  for (const w of windows) {
    const normal = vec(w.normal);
    let at = vec(w.at);
    if (Number.isNaN(at.x)) {
      const hit = surfaceAt(plaza, [-12, w.at[1], w.at[2]], [-1, 0, 0], false);
      if (!hit || hit.point.x > -15.2) continue; // a railing or balcony edge, not the facade
      at = hit.point;
    }
    glowParts.push(quad(at.clone().addScaledVector(normal, 0.015), normal, w.w, w.h, emissive.windows[w.variant], w.brightness));
    windowGlow.push({ at, normal, w: w.w, h: w.h, brightness: w.brightness });
  }
  for (const lamp of lamps) {
    const out = vec(lamp.facing);
    if (lamp.kind === "practical") continue;
    if (lamp.kind === "bulb") { // a small glowing box standing in for the bulb
      const bulb = atlasBox(0.06, 0.08, 0.06, Array(6).fill(emissive.sodiumLens)), at = vec(lamp.housing);
      bulb.translate(at.x, at.y, at.z);
      bulb.setAttribute("color", new THREE.Float32BufferAttribute(new Array(bulb.getAttribute("position").count * 3).fill(1), 3));
      glowParts.push(bulb);
      continue;
    }
    if (lamp.kind === "sodium") {
      const lens = vec(lamp.housing).addScaledVector(out, 0.42).add(new THREE.Vector3(0, -0.105, 0));
      glowParts.push(quad(lens, new THREE.Vector3(0, -1, 0), 0.28, 0.2, emissive.sodiumLens, 1.0));
      glowParts.push(quad(lens.clone().addScaledVector(out, 0.175).add(new THREE.Vector3(0, 0.1, 0)), out, 0.28, 0.12, emissive.sodiumLens, 0.9));
    } else {
      const lens = vec(lamp.housing).addScaledVector(out, 0.1).add(new THREE.Vector3(0, -0.036, 0));
      // The tube runs along its wall: on a wall facing ±x the down-facing quad turns a quarter about the lens.
      const g = quad(lens, new THREE.Vector3(0, -1, 0), 1.15, 0.05, emissive.tubeLens, 1.0);
      glowParts.push(Math.abs(out.x) > 0.5 ? rotateAbout(g, lens, Math.PI / 2) : g);
      glowParts.push(quad(lens.clone().addScaledVector(out, 0.065).add(new THREE.Vector3(0, 0.03, 0)), out, 1.15, 0.05, emissive.tubeLens, 0.9));
    }
  }
  const glowGeometry = merge(glowParts, ["position", "normal", "uv", "color"]);
  const glowMaterial = new THREE.MeshBasicMaterial({ map: emissive.texture, vertexColors: true, toneMapped: true, fog: true });
  add(new THREE.Mesh(glowGeometry, glowMaterial), "Lived-in windows and lamp lenses");
  disposables.push(glowGeometry, glowMaterial, emissive.texture);

  // Lamp glow sprites: one instanced additive billboard per lamp.
  const spriteGeometry = new THREE.PlaneGeometry(1, 1);
  const spriteMaterial = new THREE.ShaderMaterial({ vertexShader: glowVertex, fragmentShader: glowFragment, transparent: true,
    blending: THREE.AdditiveBlending, depthWrite: false });
  const spriteCount = lamps.length + windowGlow.length;
  const sprites = new THREE.InstancedMesh(spriteGeometry, spriteMaterial, spriteCount);
  const colours = new Float32Array(spriteCount * 3), sizes = new Float32Array(spriteCount * 2);
  // Window spill: the recessed windows are seen at grazing angles from the forecourt, so a soft warm halo 0.35 m in
  // front of each one carries the "lived-in" glow into the courtyard air.
  const warm = new THREE.Color("#ffb870");
  windowGlow.forEach((w, k) => {
    const i = lamps.length + k, at = w.at.clone().addScaledVector(w.normal, 0.2);
    sprites.setMatrixAt(i, new THREE.Matrix4().makeTranslation(at.x, at.y, at.z));
    const c = warm.clone().multiplyScalar(0.08 * w.brightness / 0.55);
    colours.set([c.r, c.g, c.b], i * 3); sizes.set([w.w * 1.25, w.h * 1.2], i * 2);
  });
  lamps.forEach((lamp, i) => {
    const out = vec(lamp.facing);
    const bare = lamp.kind === "bulb" || lamp.kind === "practical";
    const at = bare ? vec(lamp.housing)
      : vec(lamp.housing).addScaledVector(out, lamp.kind === "sodium" ? 0.5 : 0.18).add(new THREE.Vector3(0, -0.12, 0));
    sprites.setMatrixAt(i, new THREE.Matrix4().makeTranslation(at.x, at.y, at.z));
    const c = lamp.colour.clone().multiplyScalar(lamp.kind === "sodium" ? 0.32 : lamp.kind === "bulb" ? 0.26 : 0.18);
    colours.set([c.r, c.g, c.b], i * 3);
    sizes.set(lamp.glow ?? (lamp.kind === "sodium" ? [0.95, 0.95] : lamp.kind === "bulb" ? [0.5, 0.5] : [1.25, 0.28]), i * 2);
  });
  spriteGeometry.setAttribute("glowColour", new THREE.InstancedBufferAttribute(colours, 3));
  spriteGeometry.setAttribute("glowSize", new THREE.InstancedBufferAttribute(sizes, 2));
  sprites.frustumCulled = false; sprites.renderOrder = 2;
  add(sprites, "Lamp glow");
  disposables.push(spriteGeometry, spriteMaterial, sprites);

  // Grounded props: PA stacks at the screen sides and in the cypher corner (replacing the DJ table), an oil drum,
  // stacked crates. One lit atlas; one contact-shadow draw (not on the low tier).
  const props = sink.atlas.props;
  const propParts = sink.props, blobs = sink.blobs;
  const speakerFaces = (front: "+z" | "+x" | "-x"): Region[] => {
    const faces: Region[] = Array(6).fill(props.speakerSide);
    faces[{ "+x": 0, "-x": 1, "+z": 4 }[front]] = props.speakerFront;
    return faces;
  };
  const place = (g: THREE.BufferGeometry, x: number, y: number, z: number, yaw: number, tone = 1) => {
    g.rotateY(yaw); g.translate(x, y, z);
    g.setAttribute("color", new THREE.Float32BufferAttribute(new Array(g.getAttribute("position").count * 3).fill(tone), 3));
    propParts.push(g);
  };
  const blob = (x: number, z: number, r: number) => {
    const g = new THREE.PlaneGeometry(r * 2, r * 2); g.rotateX(-Math.PI / 2); g.translate(x, FLOOR + 0.006, z); blobs.push(g);
  };
  // Screen-side stacks: three boxes each, facing the crowd.
  for (const side of [-1, 1]) {
    const x = side * 8.85, z = -44.95;
    // Tone 0.7: these stand in the screen's spill, so the prop fill (meant for the unlit corner) is held back.
    place(atlasBox(0.72, 0.95, 0.6, speakerFaces("+z")), x, FLOOR + 0.475, z, side * 0.12, 0.7);
    place(atlasBox(0.72, 0.95, 0.6, speakerFaces("+z")), x, FLOOR + 1.425, z, side * 0.08, 0.7);
    place(atlasBox(0.6, 0.5, 0.5, speakerFaces("+z")), x, FLOOR + 2.15, z + 0.02, side * 0.15, 0.7);
    blob(x, z, 0.75);
  }
  // Cypher corner (where the DJ table stood): two-box stack, oil drum, crates.
  place(atlasBox(0.64, 0.85, 0.52, speakerFaces("+z")), -10.25, FLOOR + 0.425, -23.35, 2.0); // facing into the plaza
  place(atlasBox(0.56, 0.62, 0.46, speakerFaces("+z")), -10.27, FLOOR + 1.16, -23.33, 1.92);
  blob(-10.25, -23.35, 0.65);
  {
    const side = toRegion(new THREE.CylinderGeometry(0.29, 0.29, 0.88, 16, 1, true), props.drum);
    const top = toRegion(new THREE.CircleGeometry(0.29, 16), [props.drum[0], props.drum[1], props.drum[0] + (props.drum[2] - props.drum[0]) * 0.4, props.drum[1] + (props.drum[3] - props.drum[1]) * 0.4]);
    top.rotateX(-Math.PI / 2); top.translate(0, 0.44, 0);
    for (const part of [side, top]) place(part, -8.55, FLOOR + 0.44, -22.15, 0.3);
    blob(-8.55, -22.15, 0.5);
  }
  for (let k = 0; k < 3; k++) place(atlasBox(0.55, 0.3, 0.38, Array(6).fill(props.crate)), -9.45 + (k === 2 ? 0.06 : 0), FLOOR + 0.15 + k * 0.3, -21.75, 0.2 + k * 0.17);
  place(atlasBox(0.55, 0.3, 0.38, Array(6).fill(props.crate)), -8.95, FLOOR + 0.15, -21.2, -0.4);
  blob(-9.3, -21.5, 0.7);
  const propGeometry = merge(propParts, ["position", "normal", "uv", "color"]);
  // Unbaked props see only the dim night probe: twice its intensity keeps them as readable as the baked surfaces.
  // Fill 0.05: the cypher corner is out of reach of every light pool and props have no bake.
  const propsMaterial = propMaterial(fidelity, { map: props.texture, vertexColors: true, roughness: 0.65, metalness: 0.05, envMapIntensity: 2.2 }, null, 0.06);
  const propsMesh = add(new THREE.Mesh(propGeometry, propsMaterial), "Grounded props");
  disposables.push(propGeometry, propsMaterial, props.texture);
  let blobMesh: THREE.Object3D | null = null;
  if (budget.tier !== "low") {
    const blobGeometry = merge(blobs, ["position", "uv"]);
    const blobMap = blobTexture();
    const blobMaterial = new THREE.MeshBasicMaterial({ map: blobMap, color: 0x000000, transparent: true, opacity: 0.6, depthWrite: false,
      polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
    blobMesh = add(new THREE.Mesh(blobGeometry, blobMaterial), "Prop contact shadows");
    disposables.push(blobGeometry, blobMaterial, blobMap);
  } else blobs.forEach(g => g.dispose());

  // Wall stencils and flyers on the left wing's plain ground-floor walls, placed on the surveyed wall surface.
  const decals = sink.atlas.decals;
  const decalParts = sink.decals;
  const onWall = (z: number, y: number, w: number, h: number, region: Region, brightness: number, roll = 0) => {
    const hit = surfaceAt(plaza, [-12.5, y, z], [-1, 0, 0]);
    if (!hit) return;
    decalParts.push(quad(hit.point.clone().addScaledVector(hit.normal, 0.012), hit.normal, w, h, region, brightness, roll));
  };
  // Atlas aspect ratios: GULLY VERSE 4.76:1, BREEZE '27 4.6:1, flyers 0.93:1.
  // The plain stretch between the two ground-floor windows runs z −44.3 … −47.3 (measured from a capture).
  onWall(-45.8, 8.85, 2.6, 2.6 / 4.76, decals.gullyVerse, 0.2);
  onWall(-45.8, 8.15, 1.4, 1.4 / 4.6, decals.breeze, 0.18);
  // Flyers: around the stencils, and a few on the plain wall by the cypher corner (between its window and door).
  const flyerSpots: [number, number, number][] = [[-42.0, 8.45, 0.04], [-41.35, 8.8, -0.03], [-24.75, 8.6, -0.02]]; // z −21.25 clipped the accommodation corner
  flyerSpots.forEach(([z, y, roll], i) => onWall(z, y, 0.56, 0.6, decals.flyers[i % decals.flyers.length], 0.3 + 0.05 * (i % 2), roll));
  const decalMaterial = new THREE.MeshBasicMaterial({ map: decals.texture, vertexColors: true, transparent: true, alphaTest: 0.02, depthWrite: false,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2, toneMapped: true, fog: true });
  // Lit by the lamp pools on top of their fixed (bake-standing) brightness (light-pools.ts patchUnlit).
  decalMaterial.onBeforeCompile = shader => fidelity.pools.patchUnlit(shader);
  decalMaterial.customProgramCacheKey = () => `breeze-decal-${fidelity.pools.key()}`;
  disposables.push(decalMaterial);
  let decalMesh: THREE.Object3D | null = null, laneDecalMesh: THREE.Object3D | null = null;
  if (decalParts.length) {
    const decalGeometry = merge(decalParts, ["position", "normal", "uv", "color"]);
    decalMesh = add(new THREE.Mesh(decalGeometry, decalMaterial), "Wall stencils and flyers");
    disposables.push(decalGeometry);
  }
  if (sink.laneDecals.length) {
    const laneGeometry = merge(sink.laneDecals, ["position", "normal", "uv", "color"]);
    laneDecalMesh = add(new THREE.Mesh(laneGeometry, decalMaterial), "Lane stencils and flyers");
    disposables.push(laneGeometry);
  }
  disposables.push(decals.texture);

  // Dust haze in front of the screen: soft y-billboards, faintly tinted by the film.
  const hazeCount = budget.hazePlanes;
  const noise = hazeTexture();
  const hazeGeometry = new THREE.PlaneGeometry(1, 1); hazeGeometry.translate(0, 0.5, 0);
  const hazeUniforms = THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
    hazeNoise: { value: noise }, hazeColour: { value: new THREE.Color(0.62, 0.64, 0.66) },
    hazeAlpha: { value: budget.tier === "low" ? 0.22 : 0.2 }, hazeTime: { value: 0 },
  }]);
  hazeUniforms.hazeNoise.value = noise;
  const hazeMaterial = new THREE.ShaderMaterial({ vertexShader: hazeVertex, fragmentShader: hazeFragment, uniforms: hazeUniforms, transparent: true,
    depthWrite: false, fog: true });
  const haze = new THREE.InstancedMesh(hazeGeometry, hazeMaterial, hazeCount);
  const hazeSizes = new Float32Array(hazeCount * 2), hazeSeeds = new Float32Array(hazeCount);
  for (let i = 0; i < hazeCount; i++) {
    const z = -44.4 + (i / Math.max(1, hazeCount - 1)) * 5.6, x = (i % 2 ? 1.5 : -1.2); // ahead of the viewing spot (z −35.5)
    haze.setMatrixAt(i, new THREE.Matrix4().makeTranslation(x, FLOOR + 0.05, z));
    hazeSizes.set([15 - i * 0.6, 4.6 + (i % 2) * 0.8], i * 2); hazeSeeds[i] = i * 0.37;
  }
  hazeGeometry.setAttribute("hazeSize", new THREE.InstancedBufferAttribute(hazeSizes, 2));
  hazeGeometry.setAttribute("hazeSeed", new THREE.InstancedBufferAttribute(hazeSeeds, 1));
  haze.frustumCulled = false; haze.renderOrder = 3;
  add(haze, "Screen dust haze");
  disposables.push(hazeGeometry, hazeMaterial, noise, haze);

  // Light pools: the three lamps (the low tier has three pools: the back tube is dropped) and the screen spill (pool 0).
  // Registered (light-pools.ts): the registry binds the nearest few per frame, so zone pools can join.
  const pools = fidelity.pools;
  const core = budget.tier === "low" ? 4 : 0; // phones keep the plaza's own pools ahead of the zones' while in the plaza
  const screenPool = pools.add({ x: 0, y: 11.0, z: -43.4 }, 15.5, "#9aa4b0", 0.28, { label: "screen spill", bias: core });
  const registered = [screenPool, ...lamps.map((lamp, i) => pools.add(vec(lamp.pool), lamp.radius, lamp.colour, lamp.intensity,
    { label: lamp.label ?? `courtyard ${lamp.kind} ${i}`, bias: lamp.active ? 0 : core, active: lamp.active, cone: lamp.cone }))];

  // Film colour: 8 × 8 canvas average every 0.5 s, eased per frame.
  const sampler = document.createElement("canvas"); sampler.width = sampler.height = 8;
  const sample = sampler.getContext("2d", { willReadFrequently: true });
  const target = new THREE.Color(0.5, 0.52, 0.55), current = target.clone(), neutral = new THREE.Color("#9aa4b0");
  const spill = new THREE.Color(), hazeBase = new THREE.Color(0.62, 0.64, 0.66);
  let since = 0, time = 0;

  return {
    group,
    update(delta, camera, video, reduced) {
      const lane = inLane(camera);
      for (const mesh of [propsMesh, blobMesh, decalMesh]) if (mesh) mesh.visible = !lane;
      if (laneDecalMesh) laneDecalMesh.visible = camera.position.z > -24;
      hooks.update?.(camera);
      time += reduced ? 0 : delta;
      hazeUniforms.hazeTime.value = time;
      since += delta;
      if (since > 0.5 && video && sample && video.readyState >= 2 && camera.position.z < -15) {
        since = 0;
        try {
          sample.drawImage(video, 0, 0, 8, 8);
          const data = sample.getImageData(0, 0, 8, 8).data;
          let r = 0, g = 0, b = 0;
          for (let i = 0; i < data.length; i += 4) { r += data[i]; g += data[i + 1]; b += data[i + 2]; }
          target.setRGB(r / 64 / 255, g / 64 / 255, b / 64 / 255, THREE.SRGBColorSpace);
        } catch { /* a tainted or not-yet-decoded frame: keep the last colour */ }
      }
      const k = 1 - Math.exp(-delta * 2);
      current.lerp(target, reduced ? 1 : k);
      spill.copy(neutral).lerp(current, 0.6);
      screenPool.colour.copy(spill);
      screenPool.intensity = 0.28 + 0.28 * (current.r * 0.2126 + current.g * 0.7152 + current.b * 0.0722);
      hazeUniforms.hazeColour.value.copy(hazeBase).lerp(current, 0.48);
    },
    dispose() {
      group.removeFromParent();
      disposables.forEach(d => d.dispose());
      registered.forEach(spec => pools.remove(spec));
      hooks.dispose?.();
    },
  };
}

/** Rotates a geometry about a point around the world Y axis. */
function rotateAbout(g: THREE.BufferGeometry, pivot: THREE.Vector3, angle: number) {
  g.translate(-pivot.x, -pivot.y, -pivot.z); g.rotateY(angle); g.translate(pivot.x, pivot.y, pivot.z);
  return g;
}
