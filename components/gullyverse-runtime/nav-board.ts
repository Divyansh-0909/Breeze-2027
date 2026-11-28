import * as THREE from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";

/**
 * Navigation board (user request, 26 November 2026): squircle corners on every panel and inset line, larger
 * GULLYVERSE lettering; restyled in Phase 3 as a weathered hand-painted sign (see the colours below). The exported panels are boxes and the lines rectangular frames, so both are rebuilt here at
 * the same size and place; the lettering and arrows are the exported ones.
 */
const panel = /Reused sign hierarchy|EXISTING GULLYVERSE hero raster$|Past Sponsors plaque/;
const border = /White inset border/;
const title = /Highway Gullyverse title/;
/** The direction labels and arrows (exported with the title's and the arrow's materials). */
const lettering = /^REV15Z \/ REV15L \/ (Navigation \/|Past Sponsors label)|white diagonal arrow|Aftermovie upward arrow/;
// Phase 3 (user decision, 27 Nov): a weathered hand-painted gully sign in the night palette instead of a highway
// sign: faded rust-brown header, dull charcoal-teal direction panels, chalk lettering; only a faint glow is kept
// (emissive 0.08) so the paint still reads under the entrance streetlamp and does not drop to black.
const rust = new THREE.Color("#7a4a2e"), teal = new THREE.Color("#2f4542"), chalk = new THREE.Color("#d3ccbc");
const glow = 0.08;
/** Title lettering scale (it stays well inside its white line). */
const titleScale = 1.25;

/** A rounded rectangle whose corners are superellipse quadrants (exponent 5): curvature eases in. */
function squircle(width: number, height: number, radius: number, path: THREE.Path = new THREE.Shape()) {
  const w = width / 2, h = height / 2, r = Math.min(radius, w, h), n = 5, steps = 10;
  const corner = (cx: number, cy: number, from: number) => {
    for (let i = 0; i <= steps; i++) {
      const t = from + (i / steps) * Math.PI / 2;
      const c = Math.cos(t), s = Math.sin(t);
      const x = cx + r * Math.sign(c) * Math.abs(c) ** (2 / n), y = cy + r * Math.sign(s) * Math.abs(s) ** (2 / n);
      if (i === 0 && from === 0) path.moveTo(x, y); else path.lineTo(x, y);
    }
  };
  corner(w - r, h - r, 0);
  corner(-w + r, h - r, Math.PI / 2);
  corner(-w + r, -h + r, Math.PI);
  corner(w - r, -h + r, Math.PI * 1.5);
  path.closePath();
  return path;
}

type Fit = Map<string, { size: number; coefficients: number[][] }>;

/**
 * Every attribute but position/normal (lighting UVs etc.) as an affine function of the position across the
 * original front face, fitted by least squares, so a rebuilt panel keeps its baked light where it was.
 */
function fit(mesh: THREE.Mesh, centre: THREE.Vector3): Fit {
  const geometry = mesh.geometry, position = geometry.getAttribute("position"), normal = geometry.getAttribute("normal");
  const rows: [number, number][] = [], index: number[] = [];
  const p = new THREE.Vector3(), n = new THREE.Vector3(), normalMatrix = new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld);
  for (let i = 0; i < position.count; i++) {
    if (normal && n.fromBufferAttribute(normal, i).applyMatrix3(normalMatrix).normalize().z < 0.5) continue;
    p.fromBufferAttribute(position, i).applyMatrix4(mesh.matrixWorld).sub(centre);
    rows.push([p.x, p.y]); index.push(i);
  }
  // Normal equations for value = a x + b y + c.
  const m = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
  for (const [x, y] of rows) { const r = [x, y, 1]; for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) m[a][b] += r[a] * r[b]; }
  const inverse = new THREE.Matrix3().set(m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2], m[2][0], m[2][1], m[2][2]);
  const solvable = Math.abs(inverse.determinant()) > 1e-12;
  if (solvable) inverse.invert();
  const out: Fit = new Map();
  for (const [name, attribute] of Object.entries(geometry.attributes)) {
    if (name === "position" || name === "normal") continue;
    const coefficients: number[][] = [];
    for (let c = 0; c < attribute.itemSize; c++) {
      const v = [0, 0, 0];
      let mean = 0;
      rows.forEach(([x, y], k) => { const value = attribute.getComponent(index[k], c); v[0] += x * value; v[1] += y * value; v[2] += value; mean += value; });
      mean /= Math.max(1, rows.length);
      if (!solvable) { coefficients.push([0, 0, mean]); continue; }
      const e = inverse.elements; // column-major
      coefficients.push([0, 1, 2].map(r => e[r] * v[0] + e[3 + r] * v[1] + e[6 + r] * v[2]));
    }
    out.set(name, { size: attribute.itemSize, coefficients });
  }
  return out;
}

function withFit(geometry: THREE.BufferGeometry, values: Fit) {
  const position = geometry.getAttribute("position"), n = position.count;
  for (const [name, { size, coefficients }] of values) {
    const data = new Float32Array(n * size);
    for (let i = 0; i < n; i++) {
      const x = position.getX(i), y = position.getY(i);
      for (let c = 0; c < size; c++) { const [a, b, k] = coefficients[c]; data[i * size + c] = a * x + b * y + k; }
    }
    geometry.setAttribute(name, new THREE.BufferAttribute(data, size));
  }
  geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  return geometry;
}

/** World-space box of a mesh, and the mesh re-placed at its centre with unit scale. */
function recentre(mesh: THREE.Mesh) {
  const box = new THREE.Box3().setFromObject(mesh);
  const centre = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
  mesh.parent!.updateMatrixWorld(true);
  mesh.position.copy(mesh.parent!.worldToLocal(centre.clone()));
  mesh.quaternion.identity();
  mesh.scale.set(1, 1, 1);
  return { centre, size };
}

/** Restyles the board if this chunk holds it. Returns the geometries it made (for disposal). */
export function restyleNavigationBoard(root: THREE.Object3D) {
  const panels: THREE.Mesh[] = [], borders: THREE.Mesh[] = [], titles: THREE.Mesh[] = [], labels: THREE.Mesh[] = [];
  root.traverse(o => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const source = String(mesh.userData.runtimeOriginalSource ?? mesh.name);
    if (border.test(source)) borders.push(mesh);
    else if (panel.test(source)) panels.push(mesh);
    else if (title.test(source)) titles.push(mesh);
    else if (lettering.test(source)) labels.push(mesh);
  });
  if (!panels.length) return null;
  root.updateMatrixWorld(true);
  const made: THREE.BufferGeometry[] = [], materials: THREE.Material[] = [];
  /** The GULLYVERSE header panel is painted rust; the direction panels charcoal-teal. */
  const header = (mesh: THREE.Mesh) => /EXISTING GULLY/.test(String(mesh.userData.runtimeOriginalSource ?? mesh.name));
  // One restyled copy per original material, so meshes that shared a material still share one (and batch).
  // Keyed by role too: header, panels and lettering are restyled differently.
  const copies = new Map<string, THREE.MeshStandardMaterial>();
  const own = (mesh: THREE.Mesh, role: "header" | "panel" | "ink") => {
    const original = mesh.material as THREE.MeshStandardMaterial;
    let copy = copies.get(role + original.uuid);
    if (!copy) { copy = original.clone(); copies.set(role + original.uuid, copy); materials.push(copy); }
    mesh.material = copy;
    return copy;
  };
  const radiusFor = (height: number) => Math.min(0.24, height * 0.34);

  const placed: { centre: THREE.Vector3; size: THREE.Vector3; radius: number }[] = [];
  for (const mesh of panels) {
    const values = fit(mesh, new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()));
    const { centre, size } = recentre(mesh);
    placed.push({ centre, size, radius: radiusFor(size.y) });
    const shape = squircle(size.x, size.y, radiusFor(size.y)) as THREE.Shape;
    const geometry = new THREE.ExtrudeGeometry(shape, { depth: size.z, bevelEnabled: false, curveSegments: 1 });
    geometry.translate(0, 0, -size.z / 2);
    geometry.deleteAttribute("uv");
    mesh.geometry = withFit(geometry, values);
    made.push(mesh.geometry);
    // The rebuilt panels can't reuse the box's baked light layout, so every panel takes the board's shared
    // sign light (as the lettering does): the green panels stay evenly lit as before.
    const paint = header(mesh) ? rust : teal;
    const material = own(mesh, header(mesh) ? "header" : "panel");
    material.color.copy(paint);
    material.map = null;
    material.roughness = Math.max(material.roughness, 0.85); // flat sign paint, not sheeting
    material.userData.runtimeSignInk = true;
    material.emissive.copy(paint);
    material.emissiveIntensity = glow;
    material.userData.breezeSignWear = "paint"; // chipped, faded, rust-streaked (sign-wear.ts)
  }
  for (const mesh of borders) {
    // The exported frame: outer edge = its box; the line width = gap between its outer and inner edges.
    const position = mesh.geometry.getAttribute("position");
    const xs = new Set<number>();
    const v = new THREE.Vector3();
    for (let i = 0; i < position.count; i++) xs.add(+v.fromBufferAttribute(position, i).applyMatrix4(mesh.matrixWorld).x.toFixed(4));
    const values = fit(mesh, new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3()));
    const { centre, size } = recentre(mesh);
    const sorted = [...xs].sort((a, b) => a - b);
    const line = sorted.length > 2 ? Math.min(0.05, Math.max(0.012, sorted[1] - sorted[0])) : 0.025;
    // Concentric with its panel's corners: the panel radius less the margin between panel and line.
    const host = placed.reduce((best, p) => p.centre.distanceTo(centre) < best.centre.distanceTo(centre) ? p : best, placed[0]);
    const margin = Math.max(0, Math.min(host.size.x - size.x, host.size.y - size.y) / 2);
    const radius = Math.max(0.02, host.radius - margin);
    const outer = squircle(size.x, size.y, radius) as THREE.Shape;
    outer.holes.push(squircle(size.x - 2 * line, size.y - 2 * line, Math.max(0.008, radius - line), new THREE.Path()));
    const geometry = new THREE.ShapeGeometry(outer, 1);
    geometry.translate(0, 0, size.z / 2);
    geometry.deleteAttribute("uv");
    mesh.geometry = withFit(geometry, values);
    made.push(mesh.geometry);
  }
  for (const mesh of titles) {
    const box = new THREE.Box3().setFromObject(mesh), centre = box.getCenter(new THREE.Vector3());
    mesh.scale.multiplyScalar(titleScale);
    mesh.updateMatrixWorld(true);
    const moved = new THREE.Box3().setFromObject(mesh).getCenter(new THREE.Vector3());
    const shift = centre.sub(moved);
    mesh.position.add(mesh.parent!.worldToLocal(mesh.getWorldPosition(new THREE.Vector3()).add(shift)).sub(mesh.position));
  }
  // Chalk-white brushed lettering and lines (no retroreflective glow).
  for (const mesh of [...titles, ...borders, ...labels]) {
    const ink = own(mesh, "ink");
    ink.color.copy(chalk);
    ink.emissive.copy(chalk);
    ink.emissiveIntensity = glow * 1.5;
    ink.userData.breezeSignWear = "ink";
  }
  // The board keeps its sign colours: no palette grade or procedural surface (fidelity.ts).
  for (const mesh of [...panels, ...borders, ...titles, ...labels]) {
    for (const material of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) material.userData.breezeNoGrade = true;
  }
  root.updateMatrixWorld(true);
  // Phase 3 entrance budget: board parts that share a material become one mesh (the lettering and lines are
  // transparent decals, which the static batching leaves alone): ~16 draws become ~4.
  const merged = mergeByMaterial([...panels, ...borders, ...titles, ...labels], made);
  return { geometries: made, materials, panels: panels.length, borders: borders.length, titles: titles.length, merged };
}

/**
 * Merges meshes that share a material into the first of them (geometry re-expressed in its local space). Groups whose
 * geometries do not share one attribute layout are left alone. Returns how many meshes were folded away.
 */
function mergeByMaterial(meshes: THREE.Mesh[], made: THREE.BufferGeometry[]) {
  const groups = new Map<THREE.Material, THREE.Mesh[]>();
  for (const mesh of meshes) {
    if (Array.isArray(mesh.material) || !mesh.parent) continue;
    groups.set(mesh.material, [...(groups.get(mesh.material) ?? []), mesh]);
  }
  let folded = 0;
  for (const list of groups.values()) {
    if (list.length < 2) continue;
    const host = list[0];
    const toHost = host.matrixWorld.clone().invert();
    const parts = list.map(mesh => toFloat(mesh.geometry).applyMatrix4(new THREE.Matrix4().multiplyMatrices(toHost, mesh.matrixWorld)));
    const layout = (g: THREE.BufferGeometry) => Object.keys(g.attributes).sort().join() + (g.index ? "+i" : "");
    const geometry = parts.every(g => layout(g) === layout(parts[0])) ? mergeGeometries(parts, false) : null;
    parts.forEach(g => g.dispose());
    if (!geometry) continue;
    for (const mesh of list) if (!made.includes(mesh.geometry)) made.push(mesh.geometry); // the originals, for disposal
    host.geometry = geometry; made.push(geometry);
    list.slice(1).forEach(mesh => mesh.removeFromParent());
    folded += list.length - 1;
  }
  return folded;
}

/**
 * A copy of the geometry with every attribute as plain float32 (the exported meshes are quantized, the rebuilt
 * panels are not; mergeGeometries needs one array type per attribute).
 */
function toFloat(source: THREE.BufferGeometry) {
  const g = new THREE.BufferGeometry();
  if (source.index) g.setIndex(Array.from(source.index.array as ArrayLike<number>));
  for (const [name, attribute] of Object.entries(source.attributes)) {
    const size = attribute.itemSize, out = new Float32Array(attribute.count * size);
    const read = [attribute.getX, attribute.getY, attribute.getZ, attribute.getW];
    for (let i = 0; i < attribute.count; i++) for (let c = 0; c < size; c++) out[i * size + c] = read[c].call(attribute, i);
    g.setAttribute(name, new THREE.BufferAttribute(out, size));
  }
  return g;
}
