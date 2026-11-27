import { BufferAttribute, BufferGeometry, Matrix4, Mesh, type Material, type Object3D } from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";

/**
 * userData keys the runtime reads to find or animate a mesh (lamps, LED, contact window, team mural, people,
 * events, accommodation, navigation and gate parts). A mesh carrying any of them stays a separate object. Every
 * other key is export bookkeeping (source names, chunk, lightmap layout, authoring notes). Meshes found by their
 * source name (aftermovie panels, poster slots, accommodation artwork) are named by the caller's `keep`.
 */
const liveKeys = new Set(["streetLampPart", "streetLampId", "lampState", "emissionBase", "ledScreen", "contactPart", "carouselSlide",
  "artKind", "archetype", "breezePersonMesh", "wallEventId", "accommodationPart", "navigationLabel", "navigationDirection",
  "entryGatePart"]);

/** A plain static mesh: export bookkeeping only, one opaque material, nothing animated or projected. */
export function isPlainStatic(mesh: Mesh) {
  const material = mesh.material as Material;
  return !Array.isArray(mesh.material) && mesh.visible && !(mesh as { isSkinnedMesh?: boolean }).isSkinnedMesh &&
    !(mesh as { isInstancedMesh?: boolean }).isInstancedMesh && !material.transparent && !material.userData.runtimeDecal &&
    !Object.keys(mesh.userData).some(key => liveKeys.has(key)) &&
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
  // A mirroring transform reverses triangle winding: restore it, or front-side faces would cull inside out.
  if (matrix.determinant() < 0) {
    if (copy.index) {
      const index = copy.index.array as Uint32Array;
      for (let i = 0; i + 2 < index.length; i += 3) { const t = index[i + 1]; index[i + 1] = index[i + 2]; index[i + 2] = t; }
    } else {
      for (const attribute of Object.values(copy.attributes) as BufferAttribute[]) {
        const a = attribute.array as Float32Array, n = attribute.itemSize;
        for (let i = 0; i + 2 < attribute.count; i += 3) for (let c = 0; c < n; c++) {
          const t = a[(i + 1) * n + c]; a[(i + 1) * n + c] = a[(i + 2) * n + c]; a[(i + 2) * n + c] = t;
        }
      }
    }
  }
  return copy;
}

/**
 * Merges plain static meshes that share a material into one mesh per material and attribute layout, in the
 * chunk root's space. (Splitting into 10, 20 or 30 m cells measured 728 draws at the market arrival against 656
 * for whole-chunk batches, and saved only 17 at the navigation board: GTX 1650, 26 Nov 2026.) Lightmap UVs, materials and shaders are unchanged; anything named,
 * interactive, animated, transparent or projected stays a separate object, as does anything `keep` names. Returns the new geometries
 * (for disposal) and the draw-call counts before and after.
 */
export function batchStatic(root: Object3D, keep?: (mesh: Mesh) => boolean) {
  root.updateMatrixWorld(true);
  const toRoot = new Matrix4().copy(root.matrixWorld).invert();
  const groups = new Map<string, Mesh[]>();
  let before = 0;
  root.traverse(object => {
    if (!(object instanceof Mesh)) return;
    before++;
    if (!isPlainStatic(object) || keep?.(object)) return;
    const key = (object.material as Material).uuid + "|" + signature(object.geometry);
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
