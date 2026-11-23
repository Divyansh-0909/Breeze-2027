import { Box3, BufferAttribute, BufferGeometry, Matrix4, Mesh, Vector3, type Material, type Object3D } from "three";

/**
 * Merged groups are also split into horizontal cells of this size (metres), so each batch stays local
 * and frustum culling still drops the parts of the lane behind the visitor. Whole-chunk batches drew
 * more than the separate meshes from the navigation board looking back down the lane.
 */
const cellMetres = 10;
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";

/** userData keys of plain, static, non-interactive geometry (export bookkeeping only). */
const plainKeys = new Set(["name", "runtimeOriginalSource", "runtimeChunk", "runtimeLightmapChannel", "runtimeLightmap",
  "runtimeLightmapUV", "shopId", "referenceAuthored", "sourceObjectName"]);

function plain(mesh: Mesh) {
  const material = mesh.material as Material;
  return !Array.isArray(mesh.material) && mesh.visible && !(mesh as { isSkinnedMesh?: boolean }).isSkinnedMesh &&
    !(mesh as { isInstancedMesh?: boolean }).isInstancedMesh && !material.transparent && !material.userData.runtimeDecal &&
    !material.userData.breezeArts && !material.userData.runtimeSignInk && Object.keys(mesh.userData).every(key => plainKeys.has(key)) &&
    !Object.keys(mesh.geometry.morphAttributes).length;
}

function signature(geometry: BufferGeometry) {
  const names = Object.keys(geometry.attributes).sort();
  return names.map(name => `${name}:${geometry.attributes[name].itemSize}`).join(",") + (geometry.index ? "|i" : "|n");
}

/** A float copy of the geometry in `matrix` space (quantised attributes are expanded first). */
function bake(geometry: BufferGeometry, matrix: Matrix4) {
  const copy = new BufferGeometry();
  for (const [name, attribute] of Object.entries(geometry.attributes)) {
    const source = attribute as BufferAttribute;
    const out = new Float32Array(source.count * source.itemSize);
    for (let i = 0; i < source.count; i++) for (let c = 0; c < source.itemSize; c++) out[i * source.itemSize + c] = source.getComponent(i, c);
    copy.setAttribute(name, new BufferAttribute(out, source.itemSize));
  }
  if (geometry.index) copy.setIndex(new BufferAttribute(Uint32Array.from(geometry.index.array as ArrayLike<number>), 1));
  copy.applyMatrix4(matrix);
  return copy;
}

/**
 * Merges plain static meshes that share a material into one mesh per material, attribute layout and
 * 10 m cell, in the chunk root's space. Lightmap UVs, materials and shaders are unchanged; anything named,
 * interactive, animated, transparent or projected stays a separate object. Returns the new geometries
 * (for disposal) and the draw-call counts before and after.
 */
export function batchStatic(root: Object3D) {
  root.updateMatrixWorld(true);
  const toRoot = new Matrix4().copy(root.matrixWorld).invert();
  const groups = new Map<string, Mesh[]>();
  const box = new Box3(), centre = new Vector3();
  let before = 0;
  root.traverse(object => {
    if (!(object instanceof Mesh)) return;
    before++;
    if (!plain(object)) return;
    if (!object.geometry.boundingBox) object.geometry.computeBoundingBox();
    box.copy(object.geometry.boundingBox!).applyMatrix4(object.matrixWorld).getCenter(centre);
    const cell = `${Math.floor(centre.x / cellMetres)},${Math.floor(centre.z / cellMetres)}`;
    const key = (object.material as Material).uuid + "|" + signature(object.geometry) + "|" + cell;
    const list = groups.get(key) ?? [];
    list.push(object);
    groups.set(key, list);
  });
  const created: BufferGeometry[] = [];
  let removed = 0;
  for (const meshes of groups.values()) {
    if (meshes.length < 2) continue;
    const parts = meshes.map(mesh => bake(mesh.geometry, new Matrix4().multiplyMatrices(toRoot, mesh.matrixWorld)));
    const merged = mergeGeometries(parts, false);
    parts.forEach(part => part.dispose());
    if (!merged) continue;
    merged.computeBoundingSphere(); merged.computeBoundingBox();
    const batch = new Mesh(merged, meshes[0].material);
    batch.name = `batched ${meshes.length} × ${(meshes[0].material as Material).name}`;
    batch.userData = { batchedFrom: meshes.length };
    batch.frustumCulled = true;
    root.add(batch);
    for (const mesh of meshes) mesh.removeFromParent();
    created.push(merged);
    removed += meshes.length - 1;
  }
  return { geometries: created, before, after: before - removed };
}
