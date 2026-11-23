import type { BufferGeometry, Object3D } from "three";

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
