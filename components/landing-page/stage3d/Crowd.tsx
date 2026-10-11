"use client";
import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import { disposeUnpublishedPoses } from "./poseResources";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";

/**
 * Blacked-out crowd built from the real character models (Man.glb +
 * Animated-Woman.glb). Both models are SKINNED, and InstancedMesh cannot
 * skin per-instance — so we bake two idle-animation frames per model into
 * static geometry (CPU skinning once at startup) and instance those.
 * 4 pose variants → 4 InstancedMeshes → 4 draw calls for the whole crowd.
 */

const COUNT = 900;
const MAN_SHARE = 0.6; // men are ~3x cheaper (1.8k vs 6.1k tris)
const POSE_TIMES = [0.35, 1.35]; // two different idle frames per model

// deterministic PRNG so the crowd doesn't reshuffle on hot reloads
function mulberry32(seed: number) {
  let a = seed;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Pose the skinned model at `time` seconds into its idle clip, then bake the
 * skinned vertices into one static, normalized BufferGeometry
 * (feet at y=0, centered on x/z, exactly 1 unit tall).
 */
function bakePose(root: THREE.Object3D, clips: THREE.AnimationClip[], time: number): THREE.BufferGeometry {
  const clip =
    clips.find((c) => /idle_neutral/i.test(c.name)) ??
    clips.find((c) => /idle/i.test(c.name)) ??
    clips[0];
  const mixer = new THREE.AnimationMixer(root);
  if (clip) {
    mixer.clipAction(clip).play();
    mixer.update(time);
  }
  root.updateMatrixWorld(true);

  const geoms: THREE.BufferGeometry[] = [];
  let merged: THREE.BufferGeometry | null = null;
  try {
    const v = new THREE.Vector3();
    root.traverse((o) => {
      const sm = o as THREE.SkinnedMesh;
      if (!sm.isSkinnedMesh) return;
      sm.skeleton.update();
      const src = sm.geometry, pos = src.attributes.position as THREE.BufferAttribute;
      const baked = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i); sm.applyBoneTransform(i, v); v.applyMatrix4(sm.matrixWorld);
        baked.set([v.x, v.y, v.z], i * 3);
      }
      const geometry = new THREE.BufferGeometry(); geoms.push(geometry);
      geometry.setAttribute("position", new THREE.BufferAttribute(baked, 3));
      if (src.index) geometry.setIndex(src.index.clone());
    });
    merged = mergeGeometries(geoms, false);
    if (!merged) throw new Error("Crowd pose could not be merged");
    merged.computeVertexNormals(); merged.computeBoundingBox();
    const bb = merged.boundingBox!, height = bb.max.y - bb.min.y;
    if (!Number.isFinite(height) || height <= 0) throw new Error("Invalid crowd pose height");
    merged.translate(-(bb.min.x + bb.max.x) / 2, -bb.min.y, -(bb.min.z + bb.max.z) / 2);
    merged.scale(1 / height, 1 / height, 1 / height);
    return merged;
  } catch (error) { merged?.dispose(); throw error; }
  finally { geoms.forEach(geometry => geometry.dispose()); mixer.stopAllAction(); mixer.uncacheRoot(root); }
}

type Person = { x: number; z: number; h: number; yaw: number; variant: number };

/**
 * Module-level cache of the four baked pose variants, so the expensive work
 * can be done ONCE, anywhere, ahead of time — the landing page warms it while
 * the visitor reads "click anywhere to continue", and by the time the stage
 * mounts on the aftermovie route the crowd costs nothing at all. Survives
 * client-side navigation precisely because it lives at module scope.
 */
let warmBaked: THREE.BufferGeometry[] | null = null;
function publishPoses(out: THREE.BufferGeometry[]) {
  if (!warmBaked) warmBaked = out;
  else if (warmBaked !== out) disposeUnpublishedPoses(out, warmBaked);
  return warmBaked;
}
function bakeAll(man: GLTF, woman: GLTF) {
  const out: THREE.BufferGeometry[] = [];
  try { for (const gltf of [man, woman]) for (const time of POSE_TIMES) out.push(bakePose(gltf.scene, gltf.animations, time)); return publishPoses(out); }
  catch (error) { disposeUnpublishedPoses(out, warmBaked); throw error; }
}

/** Pre-bake the crowd off the critical path. Safe to call repeatedly. */
let warming: Promise<void> | null = null;
export function warmCrowd(): Promise<void> {
  if (warmBaked) return Promise.resolve();
  if (warming) return warming;
  warming = (async () => {
    const loader = new GLTFLoader();
    const [man, woman] = await Promise.all([
      loader.loadAsync("/models/Man.glb"),
      loader.loadAsync("/models/Animated-Woman.glb"),
    ]);
    const jobs: [GLTF, number][] = [
      [man, POSE_TIMES[0]],
      [man, POSE_TIMES[1]],
      [woman, POSE_TIMES[0]],
      [woman, POSE_TIMES[1]],
    ];
    const out: THREE.BufferGeometry[] = [];
    try {
      for (const [gltf, t] of jobs) {
        await new Promise((r) => setTimeout(r, 150));
        out.push(bakePose(gltf.scene, gltf.animations, t));
      }
      publishPoses(out);
    } finally { disposeUnpublishedPoses(out, warmBaked); }
  })().catch(() => {
    warming = null; // a failed warm-up must not poison later attempts
  }) as Promise<void>;
  return warming;
}

export default function Crowd({
  immediate = false,
  count = COUNT,
  onReady,
  clearApproach = false,
  bakeDelayMs = 150,
  onBake,
}: {
  count?: number;
  onReady?: () => void;
  /** Shared quarry needs a continuous walking lane through the viewing enclosure. */
  clearApproach?: boolean;
  /** Covered preparation can yield without pacing delays; standalone behavior stays unchanged. */
  bakeDelayMs?: number;
  onBake?: (ms: number) => void;
  /**
   * Bake all four pose variants synchronously on mount. Right for contexts
   * that must have the full crowd on their first frame (the flythrough
   * recorder). The default spreads the baking across tasks — one variant at
   * a time with breathing room between — because the whole ~quarter-second
   * burst in one frame is a visible hitch in anything playing over the
   * scene while it warms up.
   */
  immediate?: boolean;
}): React.ReactElement {
  const [manGltf, womanGltf] = useLoader(GLTFLoader, ["/models/Man.glb", "/models/Animated-Woman.glb"]);

  // 4 baked pose variants: man × 2 idle frames, woman × 2 idle frames.
  // The warm cache wins over everything — if the landing page already did
  // this work, both paths below are skipped entirely.
  const syncVariants = useMemo(
    () =>
      warmBaked ??
      (immediate
        ? bakeAll(manGltf, womanGltf)
        : null),
    [immediate, manGltf, womanGltf]
  );

  const [chunked, setChunked] = useState<THREE.BufferGeometry[]>([]);
  const [bakeError, setBakeError] = useState<Error | null>(null);
  useEffect(() => {
    if (immediate || syncVariants) return;
    let alive = true;
    const jobs: [typeof manGltf, number][] = [
      [manGltf, POSE_TIMES[0]],
      [manGltf, POSE_TIMES[1]],
      [womanGltf, POSE_TIMES[0]],
      [womanGltf, POSE_TIMES[1]],
    ];
    const out: THREE.BufferGeometry[] = [];
    void (async () => {
      try {
        for (const [gltf, t] of jobs) {
          await new Promise((resolve) => setTimeout(resolve, bakeDelayMs));
          if (!alive) return;
          const start = performance.now();
          out.push(bakePose(gltf.scene, gltf.animations, t));
          onBake?.(performance.now() - start);
        }
        if (alive) setChunked(publishPoses(out));
      } catch (error) { if (alive) setBakeError(error instanceof Error ? error : new Error(String(error))); }
      finally { disposeUnpublishedPoses(out, warmBaked); }
    })();
    return () => { alive = false; disposeUnpublishedPoses(out, warmBaked); };
  }, [immediate, syncVariants, manGltf, womanGltf, bakeDelayMs, onBake]);

  // instanced meshes mount per-variant as bakes land, spreading the GPU
  // uploads the same way the CPU work is spread
  const variants = syncVariants ?? chunked;
  useEffect(() => {
    if (variants.length === 4) {
      publishPoses(variants);
      onReady?.();
    }
  }, [variants, onReady]);

  const people = useMemo<Person[]>(() => {
    const rand = mulberry32(2027);
    const out: Person[] = [];
    while (out.length < count) {
      const x = (rand() * 2 - 1) * 22;
      const z = 4.5 + rand() * 18;
      if (Math.abs(x) < 3.7 && (clearApproach || z < 15.2)) continue;
      // far rows (near the stage) read as pure silhouette — lean harder on
      // the 3x-cheaper man mesh there; near rows keep the full mix
      const isMan = rand() < (z < 14 ? 0.8 : MAN_SHARE);
      out.push({
        x,
        z,
        h: (isMan ? 1.72 : 1.62) + rand() * 0.18,
        yaw: Math.PI + (rand() - 0.5) * 0.7, // models face +z; the crowd faces the stage (-z)
        variant: (isMan ? 0 : 2) + (rand() < 0.5 ? 0 : 1),
      });
    }
    return out;
  }, [count,clearApproach]);

  const refs = useRef<(THREE.InstancedMesh | null)[]>([]);

  useLayoutEffect(() => {
    const mat = new THREE.Matrix4();
    const quat = new THREE.Quaternion();
    const scale = new THREE.Vector3();
    const pos = new THREE.Vector3();
    const euler = new THREE.Euler();
    const counters = variants.map(() => 0);
    for (const p of people) {
      const mesh = refs.current[p.variant];
      if (!mesh) continue;
      euler.set(0, p.yaw, 0);
      quat.setFromEuler(euler);
      pos.set(p.x, 0, p.z);
      scale.setScalar(p.h); // baked geometry is exactly 1 unit tall
      mat.compose(pos, quat, scale);
      mesh.setMatrixAt(counters[p.variant]++, mat);
    }
    refs.current.forEach((mesh, vi) => {
      if (!mesh) return;
      mesh.count = counters[vi];
      mesh.instanceMatrix.needsUpdate = true;
    });
  }, [people, variants]);
  useLayoutEffect(() => {
    const instances = refs.current.filter((mesh): mesh is THREE.InstancedMesh => mesh !== null);
    // dispose=null protects shared baked geometry, but each mesh still owns
    // its instance buffers and must release those on density change/unmount.
    return () => instances.forEach((mesh) => mesh.dispose());
  }, [variants, count]);

  // Lambert, not Standard: near-black silhouettes show no specular anyway,
  // and PBR × ~3M crowd triangles × every dynamic light is the frame budget
  const silhouette = useMemo(() => new THREE.MeshLambertMaterial({ color: "#05060a" }), []);
  useEffect(() => () => silhouette.dispose(), [silhouette]);

  if (bakeError) throw bakeError;
  return (
    <group>
      {variants.map((geo, vi) => (
        <instancedMesh
          key={vi}
          ref={(el) => {
            refs.current[vi] = el;
          }}
          args={[geo, silhouette, count]}
          dispose={null}
          frustumCulled={false}
        />
      ))}
    </group>
  );
}
