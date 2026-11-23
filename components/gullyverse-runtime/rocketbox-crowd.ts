import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";

/**
 * The festival crowd: Microsoft Rocketbox avatars (MIT) in hoodies and jackets, baked into static poses
 * (idle, cheer, clap, dance; scripts/gullyverse/crowd-rocketbox.py) and placed at the 189 Rev15Z crowd
 * positions (crowd.json; scripts/gullyverse/crowd-placements.py). They replace the exported Rev13A people.
 *
 * Each avatar x pose x detail level x material is one InstancedMesh, so the whole crowd is a few dozen
 * draws. Detail follows distance (full under 12 m, ~30% to 25 m, ~10% beyond) and is re-sorted only when
 * the camera has moved half a metre. Lighting is runtime (probe + lamps), like the rest of the people.
 */
const root = "/models/gullyverse/crowd-rocketbox/";
type Placement = { avatar: string; pose: string; position: [number, number, number]; yaw: number; height: number };
type CrowdData = { avatars: Record<string, { file: string; mobileFile: string }>; lods: { name: string; until: number }[]; placements: Placement[] };
type Part = { geometry: THREE.BufferGeometry; material: THREE.Material };

export type Crowd = { group: THREE.Group; update(camera: THREE.Camera): void; dispose(): void };

export async function loadRocketboxCrowd(renderer: THREE.WebGLRenderer, mobile: boolean, transcoders: string, signal: AbortSignal): Promise<Crowd> {
  const response = await fetch(root + "crowd.json", { signal });
  if (!response.ok) throw new Error("crowd.json unavailable");
  const data = (await response.json()) as CrowdData;
  const ktx = new KTX2Loader().setTranscoderPath(transcoders).setWorkerLimit(2).detectSupport(renderer);
  const loader = new GLTFLoader().setKTX2Loader(ktx).setMeshoptDecoder(MeshoptDecoder);
  const used = [...new Set(data.placements.map(p => p.avatar))];
  const owned = { geometries: new Set<THREE.BufferGeometry>(), materials: new Set<THREE.Material>(), textures: new Set<THREE.Texture>() };
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
          const geometry = (object.geometry as THREE.BufferGeometry).clone();
          geometry.applyMatrix4(object.matrixWorld);
          owned.geometries.add(geometry); (object.geometry as THREE.BufferGeometry).dispose();
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
      parts.set(avatar, byNode);
    }));
  } finally {
    ktx.dispose();
  }
  signal.throwIfAborted();

  // One InstancedMesh per avatar x pose x lod x primitive, sized for every placement of that avatar x pose.
  const group = new THREE.Group(); group.name = "Rocketbox crowd";
  const slots = new Map<string, { placements: number[]; meshes: Map<string, THREE.InstancedMesh[]> }>();
  data.placements.forEach((p, i) => {
    const key = `${p.avatar}|${p.pose}`;
    const slot = slots.get(key) ?? { placements: [], meshes: new Map() };
    slot.placements.push(i); slots.set(key, slot);
  });
  for (const [key, slot] of slots) {
    const [avatar, pose] = key.split("|");
    for (const { name: lod } of data.lods) {
      const list = parts.get(avatar)?.get(`${pose}|${lod}`) ?? [];
      const meshes = list.map(part => {
        const mesh = new THREE.InstancedMesh(part.geometry, part.material, slot.placements.length);
        mesh.count = 0; mesh.name = `${key}|${lod}`; mesh.frustumCulled = true;
        group.add(mesh);
        return mesh;
      });
      slot.meshes.set(lod, meshes);
    }
  }
  const matrices = data.placements.map(p => new THREE.Matrix4().compose(
    new THREE.Vector3(...p.position),
    new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), p.yaw),
    new THREE.Vector3().setScalar(p.height / (heights.get(p.avatar) || 1.8))));
  const last = new THREE.Vector3(Infinity, 0, 0), position = new THREE.Vector3();

  function update(camera: THREE.Camera) {
    camera.getWorldPosition(position);
    if (position.distanceToSquared(last) < 0.25) return;
    last.copy(position);
    for (const slot of slots.values()) {
      const counts = new Map<string, number>();
      for (const index of slot.placements) {
        const p = data.placements[index].position;
        const d = Math.hypot(p[0] - position.x, p[2] - position.z);
        const lod = data.lods.find(l => d < l.until)!.name;
        const n = counts.get(lod) ?? 0;
        for (const mesh of slot.meshes.get(lod) ?? []) mesh.setMatrixAt(n, matrices[index]);
        counts.set(lod, n + 1);
      }
      for (const [lod, meshes] of slot.meshes) for (const mesh of meshes) {
        mesh.count = counts.get(lod) ?? 0;
        mesh.visible = mesh.count > 0;
        if (mesh.count) { mesh.instanceMatrix.needsUpdate = true; mesh.computeBoundingSphere(); }
      }
    }
  }

  return {
    group, update,
    dispose() {
      group.removeFromParent();
      group.traverse(object => { if (object instanceof THREE.InstancedMesh) object.dispose(); });
      owned.geometries.forEach(g => g.dispose()); owned.materials.forEach(m => m.dispose()); owned.textures.forEach(t => t.dispose());
    },
  };
}
