import * as THREE from "three";

export type RockTextureScale = 1 | 2 | 3 | 4;
export const APPROVED_ROCK_TEXTURE_SCALE: RockTextureScale = 3;
export const SCANNED_MATERIAL_SELECTOR = "scanned-material-multi";

export function rockTextureScale(value: string | null): RockTextureScale {
  return value === "1" || value === "2" || value === "3" || value === "4"
    ? Number(value) as RockTextureScale : APPROVED_ROCK_TEXTURE_SCALE;
}

/** Preserve only the authorized private material mode across world URLs.
 * Ordinary URLs retain the exact existing navigation behavior. */
export function carryScannedMaterialReview(href: string, search: string, allowed: boolean) {
  const current = new URLSearchParams(search);
  const selector = current.get("quarryReview");
  if (!allowed || ![SCANNED_MATERIAL_SELECTOR, "scanned-composition", "material-fidelity", "geology-fidelity"].includes(selector ?? "")) return href;
  const [path, query = ""] = href.split("?");
  const next = new URLSearchParams(query);
  next.set("quarryReview", selector!);
  if (selector === SCANNED_MATERIAL_SELECTOR && current.has("rockTextureScale")) next.set("rockTextureScale", String(rockTextureScale(current.get("rockTextureScale"))));
  return path + "?" + next.toString();
}

/** Cache immutable authored repeats, so 3→4→1→3 never accumulates scaling.
 * Geometry-derived normals on UV1 are deliberately excluded. */
export class ScannedRockSampling {
  private originals = new Map<THREE.Texture, THREE.Vector2>();

  apply(material: THREE.MeshStandardMaterial, scale: RockTextureScale) {
    const maps = new Set([material.map, material.normalMap, material.roughnessMap,
      material.metalnessMap, material.aoMap].filter((texture): texture is THREE.Texture => !!texture));
    for (const texture of maps) {
      if (texture.channel !== 0) continue;
      if (!this.originals.has(texture)) this.originals.set(texture, texture.repeat.clone());
      const original = this.originals.get(texture)!;
      texture.repeat.set(original.x / scale, original.y / scale);
      texture.updateMatrix();
    }
  }
}
