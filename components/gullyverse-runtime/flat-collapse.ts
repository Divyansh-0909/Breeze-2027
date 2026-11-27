import * as THREE from "three";
import { classifySurface } from "./gully-materials";
import { isPlainStatic } from "./static-batching";

/**
 * Flat-colour collapse (docs/runtime/PHASE1-NIGHT-GULLY-PLAN.md): about half of each chunk's materials are plain
 * colour factors with no textures. Every chunk shares one lightmap, so those materials differ only in colour,
 * roughness and metalness. They are merged into one material per (lightmap channel, procedural surface class,
 * lamp scale, roughness floor, side): the colour moves to a vertex `color` attribute (linear, as Three stores
 * material colours) and roughness/metalness to a `breezeRM` attribute that fidelity.ts reads. The geometries
 * keep only position, normal and the lightmap UV, so static-batching.ts can then merge them into a few draws.
 *
 * Only plain static meshes are touched (static-batching.ts rules), never anything `keep` names (interactive
 * parts), never road, decal, art, sign or emissive materials, and never `exclude`d material names.
 */
export function collapseFlat(root: THREE.Object3D, keep: (mesh: THREE.Mesh) => boolean, exclude: (name: string) => boolean) {
  const groups = new Map<string, THREE.Mesh[]>();
  let flatMaterials = 0;
  const seen = new Set<THREE.Material>();
  root.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh || !isPlainStatic(mesh) || keep(mesh)) return;
    const m = mesh.material as THREE.MeshStandardMaterial;
    if (!flat(m) || exclude(m.name)) return;
    const channel = Number(m.userData.runtimeLightmapChannel);
    if (!Number.isInteger(channel) || !mesh.geometry.getAttribute(channel === 0 ? "uv" : `uv${channel}`)) return;
    if (!seen.has(m)) { seen.add(m); flatMaterials++; }
    const key = [channel, classifySurface(m.name) ?? "none", m.userData.breezeLightScale ?? 1, m.userData.breezeMinRoughness ?? 0.75,
      m.side, m.flatShading].join("|");
    const list = groups.get(key) ?? [];
    list.push(mesh);
    groups.set(key, list);
  });
  const materials: THREE.Material[] = [], geometries: THREE.BufferGeometry[] = [];
  let merged = 0;
  for (const meshes of groups.values()) {
    const distinct = new Set(meshes.map(mesh => mesh.material));
    if (distinct.size < 2) continue; // nothing to gain
    const first = meshes[0].material as THREE.MeshStandardMaterial;
    const channel = Number(first.userData.runtimeLightmapChannel);
    const lightUv = channel === 0 ? "uv" : `uv${channel}`;
    const material = new THREE.MeshStandardMaterial({ color: 0xffffff, vertexColors: true, roughness: 1, metalness: 0, side: first.side,
      flatShading: first.flatShading });
    material.name = `Collapsed flat × ${distinct.size} (${classifySurface(first.name) ?? "plain"}, uv${channel})`;
    material.userData = { ...structuredClone(first.userData), breezeCollapsed: true, breezeSourceName: first.name };
    materials.push(material);
    merged += distinct.size;
    for (const mesh of meshes) {
      const source = mesh.material as THREE.MeshStandardMaterial;
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", mesh.geometry.getAttribute("position"));
      const normal = mesh.geometry.getAttribute("normal");
      if (normal) geometry.setAttribute("normal", normal);
      geometry.setAttribute(lightUv, mesh.geometry.getAttribute(lightUv));
      if (mesh.geometry.index) geometry.setIndex(mesh.geometry.index);
      const count = geometry.getAttribute("position").count;
      const color = new Float32Array(count * 3), rm = new Float32Array(count * 2);
      for (let i = 0; i < count; i++) {
        color[i * 3] = source.color.r; color[i * 3 + 1] = source.color.g; color[i * 3 + 2] = source.color.b;
        rm[i * 2] = source.roughness; rm[i * 2 + 1] = source.metalness;
      }
      geometry.setAttribute("color", new THREE.BufferAttribute(color, 3));
      geometry.setAttribute("breezeRM", new THREE.BufferAttribute(rm, 2));
      geometry.boundingBox = mesh.geometry.boundingBox; geometry.boundingSphere = mesh.geometry.boundingSphere;
      mesh.geometry = geometry;
      mesh.material = material;
      geometries.push(geometry);
    }
  }
  return { materials, geometries, flatMaterials, merged };
}

/** An opaque, untextured, non-emissive standard material with nothing projected onto it. */
function flat(m: THREE.MeshStandardMaterial) {
  if (!m.isMeshStandardMaterial) return false;
  // glTF exports load as physical materials for IOR/specular alone; those collapse (only highlights shift slightly),
  // but not real physical features.
  const physical = m as THREE.MeshPhysicalMaterial;
  if (physical.isMeshPhysicalMaterial && (physical.transmission > 0 || physical.sheen > 0 || physical.clearcoat > 0 ||
      physical.iridescence > 0)) return false;
  if (m.transparent || m.alphaTest > 0 || m.opacity < 1 || m.vertexColors) return false;
  if (m.emissiveIntensity > 0 && (m.emissive.r > 0 || m.emissive.g > 0 || m.emissive.b > 0)) return false;
  if (m.userData.breezeArts?.length || m.userData.runtimeDecal || m.userData.runtimeSignInk || m.userData.breezeRoad ||
      m.userData.breezeNoGrade || m.userData.breezePerson) return false;
  for (const value of Object.values(m)) if (value instanceof THREE.Texture) return false;
  return true;
}
