"use client";
import React, { useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { STAGE } from "./palette";

/**
 * Black crowd-control barriers on the ground: one line across the stage
 * front (split at the runway) and a wrap around the thrust runway. The
 * lines sit exactly on the crowd's exclusion boundary (|x| < 3.7, z < 15.2)
 * so nobody spawns inside the pit. One merged segment geometry, instanced.
 */

const SEG_W = 2.0; // nominal segment width along the run

/** One barrier segment: face panel + top rail + base plate toward the crowd (+z). */
function makeSegmentGeometry(): THREE.BufferGeometry {
  const panel = new THREE.BoxGeometry(SEG_W - 0.12, 1.0, 0.06);
  panel.translate(0, 0.62, 0);
  const rail = new THREE.BoxGeometry(SEG_W - 0.12, 0.09, 0.16);
  rail.translate(0, 1.16, 0);
  const base = new THREE.BoxGeometry(SEG_W - 0.12, 0.05, 0.85);
  base.translate(0, 0.025, 0.32);
  return mergeGeometries([panel, rail, base], false)!;
}

type Seg = { x: number; z: number; yaw: number; scaleX: number };

/** Fill a straight run with evenly spaced segments, stretched to fit exactly. */
function layRun(from: [number, number], to: [number, number], yaw: number, out: Seg[]): void {
  const dx = to[0] - from[0];
  const dz = to[1] - from[1];
  const len = Math.hypot(dx, dz);
  const n = Math.max(1, Math.round(len / SEG_W));
  const scaleX = len / n / SEG_W;
  for (let i = 0; i < n; i++) {
    const t = (i + 0.5) / n;
    out.push({ x: from[0] + dx * t, z: from[1] + dz * t, yaw, scaleX });
  }
}

export default function Barricades(): React.ReactElement {
  const geometry = useMemo(makeSegmentGeometry, []);
  const material = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#0a0b0e", roughness: 0.6, metalness: 0.35 }),
    []
  );

  const segments = useMemo<Seg[]>(() => {
    const { halfW, frontZ } = STAGE;
    const runwayHalfW = 3.55; // crowd keeps |x| > 3.7
    const frontLineZ = frontZ + 0.35;
    const runwayEndZ = 15.05; // crowd keeps z > 15.2 in the runway strip
    const out: Seg[] = [];
    // stage front, split around the runway (base plates face the crowd, +z)
    layRun([-(halfW + 0.4), frontLineZ], [-runwayHalfW, frontLineZ], 0, out);
    layRun([runwayHalfW, frontLineZ], [halfW + 0.4, frontLineZ], 0, out);
    // runway sides (facing outward) and the cap across its end
    layRun([-runwayHalfW, frontLineZ], [-runwayHalfW, runwayEndZ], -Math.PI / 2, out);
    layRun([runwayHalfW, frontLineZ], [runwayHalfW, runwayEndZ], Math.PI / 2, out);
    layRun([-runwayHalfW, runwayEndZ], [runwayHalfW, runwayEndZ], 0, out);
    return out;
  }, []);

  const ref = useRef<THREE.InstancedMesh | null>(null);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const mat = new THREE.Matrix4();
    const quat = new THREE.Quaternion();
    const euler = new THREE.Euler();
    const pos = new THREE.Vector3();
    const scale = new THREE.Vector3();
    segments.forEach((s, i) => {
      euler.set(0, s.yaw, 0);
      quat.setFromEuler(euler);
      pos.set(s.x, 0, s.z);
      scale.set(s.scaleX, 1, 1);
      mat.compose(pos, quat, scale);
      mesh.setMatrixAt(i, mat);
    });
    mesh.count = segments.length;
    mesh.instanceMatrix.needsUpdate = true;
  }, [segments]);

  return <instancedMesh ref={ref} args={[geometry, material, segments.length]} frustumCulled={false} />;
}
