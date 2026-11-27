import * as THREE from "three";

/**
 * Navigation board (user request, 26 November 2026): squircle corners on every panel and white inset line,
 * and the GULLYVERSE header as a blue Indian highway sign with larger lettering; the direction panels keep
 * their green. The exported panels are boxes and the lines rectangular frames, so both are rebuilt here at
 * the same size and place; the lettering and arrows are the exported ones.
 */
const panel = /Reused sign hierarchy|EXISTING GULLYVERSE hero raster$|Past Sponsors plaque/;
const border = /White inset border/;
const title = /Highway Gullyverse title/;
const blue = new THREE.Color("#1659a6");
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
  const panels: THREE.Mesh[] = [], borders: THREE.Mesh[] = [], titles: THREE.Mesh[] = [];
  root.traverse(o => {
    const mesh = o as THREE.Mesh;
    if (!mesh.isMesh) return;
    const source = String(mesh.userData.runtimeOriginalSource ?? mesh.name);
    if (border.test(source)) borders.push(mesh);
    else if (panel.test(source)) panels.push(mesh);
    else if (title.test(source)) titles.push(mesh);
  });
  if (!panels.length) return null;
  root.updateMatrixWorld(true);
  const made: THREE.BufferGeometry[] = [], materials: THREE.Material[] = [];
  /** The GULLYVERSE header (its panel, line and lettering) is the only blue part; the rest keep their green. */
  const header = (mesh: THREE.Mesh) => /EXISTING GULLY/.test(String(mesh.userData.runtimeOriginalSource ?? mesh.name));
  // One restyled copy per original material, so meshes that shared a material still share one (and batch).
  // Keyed by role too: the blue header and the white lettering are restyled differently.
  const copies = new Map<string, THREE.MeshStandardMaterial>();
  const own = (mesh: THREE.Mesh, role: "header" | "ink") => {
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
    (mesh.material as THREE.Material).userData.runtimeSignInk = true;
    if (header(mesh)) {
      const material = own(mesh, "header");
      material.color.copy(blue);
      material.map = null;
      // Retroreflective sheeting: even light across the panel (as its lettering has) and a little glow,
      // so the blue reads at night under the warm lamps instead of turning brown.
      material.userData.runtimeSignInk = true;
      material.emissive.copy(blue);
      material.emissiveIntensity = 0.32;
    }
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
  // White lettering and line on the blue header, as on retroreflective highway signs (the sign light is warm).
  for (const mesh of [...titles, ...borders.filter(header)]) {
    const ink = own(mesh, "ink");
    ink.emissive.setRGB(1, 1, 1);
    ink.emissiveIntensity = 0.38;
  }
  // The board keeps its sign colours: no palette grade or procedural surface (fidelity.ts).
  for (const mesh of [...panels, ...borders, ...titles]) {
    for (const material of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) material.userData.breezeNoGrade = true;
  }
  root.updateMatrixWorld(true);
  return { geometries: made, materials, panels: panels.length, borders: borders.length, titles: titles.length };
}
