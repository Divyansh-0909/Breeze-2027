"use client";
import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";
import { GLTFLoader, type GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
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
  const v = new THREE.Vector3();
  root.traverse((o) => {
    const sm = o as THREE.SkinnedMesh;
    if (!sm.isSkinnedMesh) return;
    sm.skeleton.update();
    const src = sm.geometry;
    const pos = src.attributes.position as THREE.BufferAttribute;
    const baked = new Float32Array(pos.count * 3);
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      sm.applyBoneTransform(i, v); // CPU skinning at this animation frame
      v.applyMatrix4(sm.matrixWorld);
      baked.set([v.x, v.y, v.z], i * 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(baked, 3));
    if (src.index) g.setIndex(src.index.clone());
    geoms.push(g);
  });
  mixer.stopAllAction();

  const merged = mergeGeometries(geoms, false)!;
  merged.computeVertexNormals();
  merged.computeBoundingBox();
  const bb = merged.boundingBox!;
  const height = bb.max.y - bb.min.y;
  merged.translate(-(bb.min.x + bb.max.x) / 2, -bb.min.y, -(bb.min.z + bb.max.z) / 2);
  merged.scale(1 / height, 1 / height, 1 / height);
  return merged;
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
    for (const [gltf, t] of jobs) {
      // spaced out so the page hosting the warm-up never feels it
      await new Promise((r) => setTimeout(r, 150));
      out.push(bakePose(gltf.scene, gltf.animations, t));
    }
    warmBaked = out;
  })().catch(() => {
    warming = null; // a failed warm-up must not poison later attempts
  }) as Promise<void>;
  return warming;
}

export default function Crowd({
  immediate = false,
}: {
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
        ? [
            ...POSE_TIMES.map((t) => bakePose(manGltf.scene, manGltf.animations, t)),
            ...POSE_TIMES.map((t) => bakePose(womanGltf.scene, womanGltf.animations, t)),
          ]
        : null),
    [immediate, manGltf, womanGltf]
  );

  const [chunked, setChunked] = useState<THREE.BufferGeometry[]>([]);
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
      for (const [gltf, t] of jobs) {
        // a real gap, not just a yield: each bake ends with a GPU buffer
        // upload when its mesh mounts, and those need room to drain too
        await new Promise((r) => setTimeout(r, 150));
        if (!alive) return;
        out.push(bakePose(gltf.scene, gltf.animations, t));
        setChunked([...out]);
      }
      warmBaked = out; // whoever baked it, everyone after gets it for free
    })();
    return () => {
      alive = false;
    };
  }, [immediate, syncVariants, manGltf, womanGltf]);

  // instanced meshes mount per-variant as bakes land, spreading the GPU
  // uploads the same way the CPU work is spread
  const variants = syncVariants ?? chunked;

  const people = useMemo<Person[]>(() => {
    const rand = mulberry32(2027);
    const out: Person[] = [];
    while (out.length < COUNT) {
      const x = (rand() * 2 - 1) * 22;
      const z = 4.5 + rand() * 18;
      if (Math.abs(x) < 3.7 && z < 15.2) continue; // keep the runway clear
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
  }, []);

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

  // Lambert, not Standard: near-black silhouettes show no specular anyway,
  // and PBR × ~3M crowd triangles × every dynamic light is the frame budget
  const silhouette = useMemo(() => new THREE.MeshLambertMaterial({ color: "#05060a" }), []);

  return (
    <group>
      {variants.map((geo, vi) => (
        <instancedMesh
          key={vi}
          ref={(el) => {
            refs.current[vi] = el;
          }}
          args={[geo, silhouette, COUNT]}
          frustumCulled={false}
        />
      ))}
    </group>
  );
}
