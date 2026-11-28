import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";

/**
 * The festival crowd: Microsoft Rocketbox avatars (MIT) in hoodies and jackets, baked into static poses
 * (idle, cheer, clap, dance; scripts/gullyverse/crowd-rocketbox.py) and placed at the 189 Rev15Z crowd
 * positions (crowd.json; scripts/gullyverse/crowd-placements.py). They replace the exported Rev13A people.
 *
 * Each avatar material is one BatchedMesh holding every pose and detail level of that avatar, so the whole
 * crowd is one (multi-)draw per material (about 40) whatever the mix of poses and distances. Detail follows
 * distance (full under 12 m, ~30% to 25 m, ~10% beyond) by switching each person's geometry, re-sorted
 * only when the camera has moved half a metre. Lighting is runtime (probe + lamps), like the rest of the people.
 */
const root = "/models/gullyverse/crowd-rocketbox/";
export type Placement = { avatar: string; pose: string; position: [number, number, number]; yaw: number; height: number };
type CrowdData = { avatars: Record<string, { file: string; mobileFile: string }>; lods: { name: string; until: number }[]; placements: Placement[] };
type Part = { geometry: THREE.BufferGeometry; material: THREE.Material };

export type Crowd = { group: THREE.Group; update(camera: THREE.Camera): void; dispose(): void };

/**
 * A float copy of `geometry` in `matrix` space. The GLBs use KHR_mesh_quantization (normalised Int16 positions
 * and normals): transforming those arrays in place clamps every coordinate to [-1, 1], which flattened the
 * people above 1 m into pillars, so every attribute is expanded to Float32 first.
 */
function bake(geometry: THREE.BufferGeometry, matrix: THREE.Matrix4) {
  const copy = new THREE.BufferGeometry();
  for (const [name, source] of Object.entries(geometry.attributes)) {
    const attribute = source as THREE.BufferAttribute;
    const out = new Float32Array(attribute.count * attribute.itemSize);
    for (let i = 0; i < attribute.count; i++) for (let c = 0; c < attribute.itemSize; c++) out[i * attribute.itemSize + c] = attribute.getComponent(i, c);
    copy.setAttribute(name, new THREE.BufferAttribute(out, attribute.itemSize));
  }
  if (geometry.index) copy.setIndex(new THREE.BufferAttribute(Uint32Array.from(geometry.index.array as ArrayLike<number>), 1));
  copy.applyMatrix4(matrix);
  return copy;
}

/**
 * A seated pose bent from the standing idle mesh (no seated clip was baked; user request, 28 Nov: people sitting in
 * the contact booth). The mesh stands on y = 0, centred on the pelvis, facing +z. Everything above the hip joint
 * (≈ 0.52 h) drops by the thigh length; the thighs swing 90° forward about the hip; the shins hang straight below the
 * knee (≈ 0.285 h), moved forward to it. Short bands at both joints blend the two, so the creases stay closed. Hands
 * hanging below the hip end on the lap. The underside of the thighs ends ≈ 0.07 h below knee height (sitAt).
 */
export const sitAt = { knee: 0.285, under: 0.245 }; // fractions of the standing height: knee, and the seat under the thighs
function sitDown(source: THREE.BufferGeometry, height: number) {
  const g = source.clone();
  const pos = g.getAttribute("position") as THREE.BufferAttribute, nor = g.getAttribute("normal") as THREE.BufferAttribute | undefined;
  const hip = 0.52 * height, knee = sitAt.knee * height, L = hip - knee;
  const hipTop = hip + 0.02 * height, hipLow = hip - 0.045 * height, kneeTop = knee + 0.03 * height, kneeLow = knee - 0.02 * height;
  const smooth = (e0: number, e1: number, x: number) => { const t = Math.min(1, Math.max(0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t); };
  const v = new THREE.Vector3(), n = new THREE.Vector3(), thigh = new THREE.Vector3(), shin = new THREE.Vector3();
  const rotate = (out: THREE.Vector3, y: number, z: number, a: number) => out.set(0, y * Math.cos(a) - z * Math.sin(a), y * Math.sin(a) + z * Math.cos(a));
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    const a = -Math.PI / 2 * smooth(hipTop, hipLow, v.y); // 0 above the hip, −90° (down → forward) on the thigh
    rotate(thigh, v.y - hip, v.z, a); thigh.set(v.x, thigh.y + hip - L, thigh.z);
    shin.set(v.x, v.y, v.z + L);
    const w = smooth(kneeLow, kneeTop, v.y); // 0 on the shin, 1 on the thigh
    pos.setXYZ(i, v.x, shin.y + (thigh.y - shin.y) * w, shin.z + (thigh.z - shin.z) * w);
    if (nor) {
      n.fromBufferAttribute(nor, i);
      const r = rotate(new THREE.Vector3(), n.y, n.z, a * w);
      nor.setXYZ(i, n.x, r.y, r.z);
    }
  }
  pos.needsUpdate = true;
  if (nor) nor.needsUpdate = true;
  g.computeBoundingBox(); g.computeBoundingSphere();
  return g;
}

/**
 * Keeps at most `limit` avatars (alternating women and men, in crowd.json order) and gives every other placement
 * one of them, so low-tier devices draw and download fewer avatar materials (device-tier.ts `crowdAvatars`).
 * Placements keep their pose, position and height; only the person wearing them changes.
 */
export function limitAvatars(placements: Placement[], limit: number): Placement[] {
  const all = [...new Set(placements.map(p => p.avatar))];
  if (all.length <= limit) return placements;
  const women = all.filter(a => a.startsWith("Female")), men = all.filter(a => !a.startsWith("Female"));
  const kept: string[] = [];
  for (let i = 0; kept.length < limit && (i < women.length || i < men.length); i++) {
    if (i < women.length && kept.length < limit) kept.push(women[i]);
    if (i < men.length && kept.length < limit) kept.push(men[i]);
  }
  const keptWomen = kept.filter(a => a.startsWith("Female")), keptMen = kept.filter(a => !a.startsWith("Female"));
  return placements.map((p, index) => {
    if (kept.includes(p.avatar)) return p;
    const pool = p.avatar.startsWith("Female") ? keptWomen : keptMen;
    const choices = pool.length ? pool : kept;
    return { ...p, avatar: choices[index % choices.length] };
  });
}

/**
 * `extra`: placements added after the limit (e.g. the contact booth's clerk). Each wears its own avatar if that avatar is
 * already loaded for this tier, otherwise one of the kept avatars, so it costs no extra download.
 */
export async function loadRocketboxCrowd(renderer: THREE.WebGLRenderer, mobile: boolean, transcoders: string, signal: AbortSignal,
  maxAvatars = Infinity, extra: Placement[] = []): Promise<Crowd> {
  const response = await fetch(root + "crowd.json", { signal });
  if (!response.ok) throw new Error("crowd.json unavailable");
  const data = (await response.json()) as CrowdData;
  data.placements = limitAvatars(data.placements, maxAvatars);
  const present = [...new Set(data.placements.map(p => p.avatar))];
  for (const p of extra) {
    const same = present.filter(a => a.startsWith("Female") === p.avatar.startsWith("Female"));
    data.placements.push({ ...p, avatar: present.includes(p.avatar) ? p.avatar : (same[0] ?? present[0]) });
  }
  const ktx = new KTX2Loader().setTranscoderPath(transcoders).setWorkerLimit(2).detectSupport(renderer);
  const loader = new GLTFLoader().setKTX2Loader(ktx).setMeshoptDecoder(MeshoptDecoder);
  const used = [...new Set(data.placements.map(p => p.avatar))];
  const owned = { materials: new Set<THREE.Material>(), textures: new Set<THREE.Texture>() };
  // parts[avatar][pose|lod] = primitives; idle height per avatar for scaling.
  const parts = new Map<string, Map<string, Part[]>>(), heights = new Map<string, number>();
  try {
    await Promise.all(used.map(async avatar => {
      const entry = data.avatars[avatar];
      const gltf = await loader.loadAsync(root + (mobile ? entry.mobileFile : entry.file));
      signal.throwIfAborted();
      const byNode = new Map<string, Part[]>();
      gltf.scene.updateMatrixWorld(true);
      for (const node of gltf.scene.children) {
        const list: Part[] = [];
        node.traverse(object => {
          if (!(object instanceof THREE.Mesh)) return;
          const geometry = bake(object.geometry as THREE.BufferGeometry, object.matrixWorld);
          (object.geometry as THREE.BufferGeometry).dispose();
          const material = object.material as THREE.MeshStandardMaterial;
          owned.materials.add(material);
          for (const value of Object.values(material)) if (value instanceof THREE.Texture) { owned.textures.add(value); value.anisotropy = 4; }
          list.push({ geometry, material });
        });
        byNode.set(node.name, list);
        if (node.name.startsWith("idle") && node.name.endsWith("lod0")) {
          const box = new THREE.Box3();
          list.forEach(part => { part.geometry.computeBoundingBox(); box.union(part.geometry.boundingBox!); });
          heights.set(avatar, box.max.y - box.min.y);
        }
      }
      // A seated variant (sitDown) wherever this avatar is placed sitting.
      if (data.placements.some(p => p.avatar === avatar && p.pose === "sit")) {
        const h = heights.get(avatar) ?? 1.8;
        for (const [name, list] of [...byNode]) {
          if (name.startsWith("idle|")) byNode.set(`sit|${name.slice(5)}`, list.map(part => ({ geometry: sitDown(part.geometry, h), material: part.material })));
        }
      }
      parts.set(avatar, byNode);
    }));
  } finally {
    ktx.dispose();
  }
  signal.throwIfAborted();

  const group = new THREE.Group(); group.name = "Rocketbox crowd";
  const matrices = data.placements.map(p => new THREE.Matrix4().compose(
    new THREE.Vector3(...p.position),
    new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), p.yaw),
    new THREE.Vector3().setScalar(p.height / (heights.get(p.avatar) || 1.8))));
  // One BatchedMesh per avatar x material: geometry ids per pose|lod, one instance per placement of the avatar.
  type Batch = { mesh: THREE.BatchedMesh; ids: Map<string, number>; instances: { placement: number; instance: number }[] };
  const batches: Batch[] = [];
  for (const avatar of used) {
    const variants = parts.get(avatar)!;
    const placements = data.placements.flatMap((p, i) => p.avatar === avatar ? [i] : []);
    const byMaterial = new Map<THREE.Material, Map<string, THREE.BufferGeometry>>();
    for (const [variant, list] of variants) for (const { geometry, material } of list) {
      const geometries = byMaterial.get(material) ?? new Map<string, THREE.BufferGeometry>();
      geometries.set(variant, geometry);
      byMaterial.set(material, geometries);
    }
    for (const [material, geometries] of byMaterial) {
      let vertices = 0, indices = 0;
      for (const geometry of geometries.values()) { vertices += geometry.attributes.position.count; indices += geometry.index?.count ?? 0; }
      const mesh = new THREE.BatchedMesh(placements.length, vertices, Math.max(indices, 1), material);
      mesh.name = `${avatar}|${material.name}`;
      const ids = new Map<string, number>();
      for (const [variant, geometry] of geometries) { ids.set(variant, mesh.addGeometry(geometry)); geometry.dispose(); }
      const first = ids.values().next().value as number;
      const instances = placements.map(placement => {
        const instance = mesh.addInstance(first);
        mesh.setMatrixAt(instance, matrices[placement]);
        return { placement, instance };
      });
      group.add(mesh);
      batches.push({ mesh, ids, instances });
    }
  }
  const last = new THREE.Vector3(Infinity, 0, 0), position = new THREE.Vector3();
  // Crowd glimpse (Phase 3 entrance budget): from the lane only the people in the lane and the four nearest the
  // doorway inside the gate can be seen; the rest stand behind the compound wall. Avatars whose every instance is
  // hidden drop their draws entirely. The three in front of the lane's right-wall flyers step out of the lane view.
  const inLaneView = data.placements.flatMap((p, i) => {
    const [x, , z] = p.position;
    return z > -14.2 && !(x > 0.8 && x < 4.4) ? [i] : [];
  });
  const doorway = data.placements.map((p, i) => ({ i, x: p.position[0], z: p.position[2] }))
    .filter(p => p.z <= -14.2 && Math.abs(p.x) < 3).sort((a, b) => Math.hypot(a.x, a.z + 17.5) - Math.hypot(b.x, b.z + 17.5))
    .slice(0, maxAvatars <= 8 ? 2 : 4).map(p => p.i);
  const glimpse = new Set([...inLaneView, ...doorway]);
  let wasLane: boolean | null = null;

  function update(camera: THREE.Camera) {
    camera.getWorldPosition(position);
    const lane = position.z > -13.5;
    if (position.distanceToSquared(last) < 0.25 && lane === wasLane) return;
    last.copy(position); wasLane = lane;
    const lodOf = data.placements.map(p => data.lods.find(l => Math.hypot(p.position[0] - position.x, p.position[2] - position.z) < l.until)!.name);
    for (const { mesh, ids, instances } of batches) {
      let any = false;
      for (const { placement, instance } of instances) {
        const id = lane && !glimpse.has(placement) ? undefined : ids.get(`${data.placements[placement].pose}|${lodOf[placement]}`);
        mesh.setVisibleAt(instance, id !== undefined);
        if (id !== undefined) { mesh.setGeometryIdAt(instance, id); any = true; }
      }
      mesh.visible = any;
    }
  }

  return {
    group, update,
    dispose() {
      group.removeFromParent();
      for (const { mesh } of batches) mesh.dispose();
      owned.materials.forEach(m => m.dispose()); owned.textures.forEach(t => t.dispose());
    },
  };
}
