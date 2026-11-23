import type { BufferGeometry, Mesh, Object3D } from "three";

/** Precomputed by scripts/gullyverse/people-mask.mts: skin triangles that poke through clothing. */
export type PeopleMask = { skins: Record<string, { triangles: number; hidden: string }> };

/**
 * Applies a chunk's people mask: each person's parts are its child meshes in primitive order, keyed by the
 * node's runtimeOriginalSource. Parts whose triangle count does not match are left untouched.
 */
export function applyPeopleMask(person: Object3D, meshes: Mesh[], mask: PeopleMask | null) {
  if (!mask) return 0;
  let hidden = 0;
  meshes.forEach((mesh, i) => {
    const entry = mask.skins[`${person.userData.runtimeOriginalSource}#${i}`], index = mesh.geometry.index;
    if (!entry || !index || index.count / 3 !== entry.triangles || mesh.geometry.userData.breezeSkinMasked) return;
    const bits = Uint8Array.from(atob(entry.hidden), c => c.charCodeAt(0)), keep: number[] = [];
    for (let t = 0; t < entry.triangles; t++) {
      if (bits[t >> 3] & (1 << (t & 7))) { hidden++; continue; }
      keep.push(index.getX(t * 3), index.getX(t * 3 + 1), index.getX(t * 3 + 2));
    }
    mesh.geometry.setIndex(keep);
    mesh.geometry.userData.breezeSkinMasked = true;
  });
  return hidden;
}

/**
 * The people (lane characters, plaza characters and the crowd; every node exported with an `archetype`)
 * are not lit from the chunk lightmaps: the dense area-weighted atlases give a whole lane character
 * well under one lightmap texel per triangle, and about a third of samples land on unbaked (black)
 * texels, which showed as dark patches and blocky shading. They take smooth runtime lighting instead:
 * diffuse and specular from the street-level probe, plus the nearby lamps.
 */
export const isPerson = (object: Object3D) => typeof object.userData.archetype === "string";

/**
 * Averages normals across split vertices (UV seams) whose faces meet at under `creaseDegrees`, so soft
 * forms shade smoothly while real edges (collars, cuffs, fingers) stay crisp. Writes into the existing
 * (possibly quantised) normal attribute; positions, UVs and indices are unchanged.
 */
export function smoothSeams(geometry: BufferGeometry, creaseDegrees = 60) {
  const position = geometry.getAttribute("position"), normal = geometry.getAttribute("normal");
  if (!position || !normal) return 0;
  const count = position.count, original = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const x = normal.getX(i), y = normal.getY(i), z = normal.getZ(i), length = Math.hypot(x, y, z) || 1;
    original[i * 3] = x / length; original[i * 3 + 1] = y / length; original[i * 3 + 2] = z / length;
  }
  const scale = 1e4, buckets = new Map<number, number[]>(), keys = new Int32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const kx = Math.round(position.getX(i) * scale), ky = Math.round(position.getY(i) * scale), kz = Math.round(position.getZ(i) * scale);
    keys[i * 3] = kx; keys[i * 3 + 1] = ky; keys[i * 3 + 2] = kz;
    const hash = (Math.imul(kx, 73856093) ^ Math.imul(ky, 19349663) ^ Math.imul(kz, 83492791)) >>> 0;
    const bucket = buckets.get(hash);
    if (bucket) bucket.push(i); else buckets.set(hash, [i]);
  }
  const limit = Math.cos(creaseDegrees * Math.PI / 180);
  let changed = 0;
  for (const bucket of buckets.values()) {
    if (bucket.length < 2) continue;
    for (const i of bucket) {
      let sx = 0, sy = 0, sz = 0, members = 0;
      for (const j of bucket) {
        if (keys[i * 3] !== keys[j * 3] || keys[i * 3 + 1] !== keys[j * 3 + 1] || keys[i * 3 + 2] !== keys[j * 3 + 2]) continue;
        const dot = original[i * 3] * original[j * 3] + original[i * 3 + 1] * original[j * 3 + 1] + original[i * 3 + 2] * original[j * 3 + 2];
        if (dot < limit) continue;
        sx += original[j * 3]; sy += original[j * 3 + 1]; sz += original[j * 3 + 2]; members++;
      }
      if (members < 2) continue;
      const length = Math.hypot(sx, sy, sz) || 1;
      normal.setXYZ(i, sx / length, sy / length, sz / length);
      changed++;
    }
  }
  if (changed) normal.needsUpdate = true;
  return changed;
}

type MeshLike = { geometry: BufferGeometry; material: { name?: string } | { name?: string }[] };
const slot = (mesh: MeshLike) => {
  const material = Array.isArray(mesh.material) ? mesh.material[0] : mesh.material;
  return Number(/material (\d+)$/.exec(material?.name ?? "")?.[1] ?? -1);
};
/** Library material slots: 0 skin, 1 top, 2 trousers, 3 hair, 4 shoes, 5 soles, 6-7 eyes, 8 shirt inner. */
const clothingSlots = new Set([1, 2, 4, 8]);

/**
 * Hides body (skin) triangles that poke through clothing. The crowd library models a full skin body with
 * clothes layered over it; on the chest and shoulders the body surface lies up to about 2 cm outside the
 * clothes, which showed as dark blocks on tops and trousers. A skin triangle is hidden when its centre
 * lies over a clothing triangle (projected inside it), between `under` below and `reach` above that
 * triangle's outward side, with no other skin between them, so hands and forearms resting on a shirt
 * stay. Distances are in object units. Index buffers only. Returns the number of hidden triangles.
 */
export function hideCoveredSkin(meshes: MeshLike[], reach: number, under = reach / 6) {
  const skins = meshes.filter(mesh => slot(mesh) === 0 && !mesh.geometry.userData.breezeSkinMasked && mesh.geometry.index);
  const clothes = meshes.filter(mesh => clothingSlots.has(slot(mesh)));
  if (!skins.length || !clothes.length) return 0;
  const cell = reach;
  type Soup = { tris: Float32Array; normals: Float32Array; cells: Map<number, number[]> };
  const key = (i: number, j: number, k: number) => ((i * 73856093) ^ (j * 19349663) ^ (k * 83492791)) | 0;
  const soup = (sources: MeshLike[], withNormals: boolean): Soup => {
    const tris: number[] = [], normals: number[] = [], cells = new Map<number, number[]>();
    for (const { geometry } of sources) {
      const p = geometry.getAttribute("position"), nrm = geometry.getAttribute("normal"), index = geometry.index;
      const count = index ? index.count : p.count;
      for (let t = 0; t + 2 < count; t += 3) {
        const id = tris.length / 9;
        let x0 = Infinity, y0 = Infinity, z0 = Infinity, x1 = -Infinity, y1 = -Infinity, z1 = -Infinity, nx = 0, ny = 0, nz = 0;
        for (let k = 0; k < 3; k++) {
          const v = index ? index.getX(t + k) : t + k, x = p.getX(v), y = p.getY(v), z = p.getZ(v);
          tris.push(x, y, z);
          if (withNormals && nrm) { nx += nrm.getX(v); ny += nrm.getY(v); nz += nrm.getZ(v); }
          x0 = Math.min(x0, x); y0 = Math.min(y0, y); z0 = Math.min(z0, z); x1 = Math.max(x1, x); y1 = Math.max(y1, y); z1 = Math.max(z1, z);
        }
        if (withNormals) { const l = Math.hypot(nx, ny, nz) || 1; normals.push(nx / l, ny / l, nz / l); }
        for (let i = Math.floor(x0 / cell); i <= Math.floor(x1 / cell); i++) for (let j = Math.floor(y0 / cell); j <= Math.floor(y1 / cell); j++)
          for (let k = Math.floor(z0 / cell); k <= Math.floor(z1 / cell); k++) {
            const h = key(i, j, k), list = cells.get(h);
            if (list) list.push(id); else cells.set(h, [id]);
          }
      }
    }
    return { tris: Float32Array.from(tris), normals: Float32Array.from(normals), cells };
  };
  const cloth = soup(clothes, true), skin = soup(skins, false);
  const near = (g: Soup, x: number, y: number, z: number, visit: (t: number) => boolean) => {
    const ci = Math.floor(x / cell), cj = Math.floor(y / cell), ck = Math.floor(z / cell), seen = new Set<number>();
    for (let i = ci - 1; i <= ci + 1; i++) for (let j = cj - 1; j <= cj + 1; j++) for (let k = ck - 1; k <= ck + 1; k++) {
      const list = g.cells.get(key(i, j, k));
      if (list) for (const t of list) { if (seen.has(t)) continue; seen.add(t); if (visit(t)) return true; }
    }
    return false;
  };
  /** Ray-triangle distance (Moller-Trumbore), or Infinity. */
  const hit = (tr: Float32Array, t: number, ox: number, oy: number, oz: number, dx: number, dy: number, dz: number) => {
    const a = t * 9;
    const e1x = tr[a + 3] - tr[a], e1y = tr[a + 4] - tr[a + 1], e1z = tr[a + 5] - tr[a + 2];
    const e2x = tr[a + 6] - tr[a], e2y = tr[a + 7] - tr[a + 1], e2z = tr[a + 8] - tr[a + 2];
    const hx = dy * e2z - dz * e2y, hy = dz * e2x - dx * e2z, hz = dx * e2y - dy * e2x, det = e1x * hx + e1y * hy + e1z * hz;
    if (Math.abs(det) < 1e-12) return Infinity;
    const f = 1 / det, sx = ox - tr[a], sy = oy - tr[a + 1], sz = oz - tr[a + 2], u = f * (sx * hx + sy * hy + sz * hz);
    if (u < 0 || u > 1) return Infinity;
    const qx = sy * e1z - sz * e1y, qy = sz * e1x - sx * e1z, qz = sx * e1y - sy * e1x, v = f * (dx * qx + dy * qy + dz * qz);
    if (v < 0 || u + v > 1) return Infinity;
    const d = f * (e2x * qx + e2y * qy + e2z * qz);
    return d > 0 ? d : Infinity;
  };
  /** Whether a point (on or near the triangle's plane) falls inside the triangle. */
  const inside = (tr: Float32Array, t: number, px: number, py: number, pz: number) => {
    const a = t * 9;
    const v0x = tr[a + 3] - tr[a], v0y = tr[a + 4] - tr[a + 1], v0z = tr[a + 5] - tr[a + 2];
    const v1x = tr[a + 6] - tr[a], v1y = tr[a + 7] - tr[a + 1], v1z = tr[a + 8] - tr[a + 2];
    const v2x = px - tr[a], v2y = py - tr[a + 1], v2z = pz - tr[a + 2];
    const d00 = v0x * v0x + v0y * v0y + v0z * v0z, d01 = v0x * v1x + v0y * v1y + v0z * v1z, d11 = v1x * v1x + v1y * v1y + v1z * v1z;
    const d20 = v2x * v0x + v2y * v0y + v2z * v0z, d21 = v2x * v1x + v2y * v1y + v2z * v1z, den = d00 * d11 - d01 * d01;
    if (Math.abs(den) < 1e-20) return false;
    const v = (d11 * d20 - d01 * d21) / den, w = (d00 * d21 - d01 * d20) / den;
    return v >= -0.02 && w >= -0.02 && v + w <= 1.02;
  };
  let hidden = 0, skinBase = 0;
  for (const { geometry } of skins) {
    const p = geometry.getAttribute("position"), index = geometry.index!;
    const keep: number[] = [];
    for (let t = 0; t + 2 < index.count; t += 3) {
      const ia = index.getX(t), ib = index.getX(t + 1), ic = index.getX(t + 2), self = skinBase + t / 3;
      const ox = (p.getX(ia) + p.getX(ib) + p.getX(ic)) / 3, oy = (p.getY(ia) + p.getY(ib) + p.getY(ic)) / 3, oz = (p.getZ(ia) + p.getZ(ib) + p.getZ(ic)) / 3;
      const covered = near(cloth, ox, oy, oz, c => {
        const nx = cloth.normals[c * 3], ny = cloth.normals[c * 3 + 1], nz = cloth.normals[c * 3 + 2], a = c * 9, tr = cloth.tris;
        const height = (ox - tr[a]) * nx + (oy - tr[a + 1]) * ny + (oz - tr[a + 2]) * nz;
        if (height > reach || height < -under) return false;
        // Project onto the clothing triangle: the skin must lie over it, not beside it.
        if (!inside(tr, c, ox - nx * height, oy - ny * height, oz - nz * height)) return false;
        if (height <= 0) return true;
        // Above the clothing: hidden unless other skin (a hand or forearm) lies between.
        return !near(skin, ox, oy, oz, s => s !== self && hit(skin.tris, s, ox, oy, oz, -nx, -ny, -nz) < height);
      });
      if (covered) hidden++; else keep.push(ia, ib, ic);
    }
    skinBase += index.count / 3;
    geometry.setIndex(keep);
    geometry.userData.breezeSkinMasked = true;
  }
  return hidden;
}
