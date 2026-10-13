"use client";
import React, { useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { PALETTE } from "./palette";

/**
 * PA system: sub stacks on the stage deck. All cabinets share one InstancedMesh.
 */

type Box = { pos: THREE.Vector3; rotX: number; size: [number, number, number] };

export default function Speakers(): React.ReactElement {
  const boxes = useMemo<Box[]>(() => {
    const out: Box[] = [];
    // sub stacks ON the stage deck at its front corners (deck top y=1.3) —
    // kept wide of the LED wall's sightline so they never occlude the panels
    for (const x of [-10.6, 10.6]) {
      out.push({ pos: new THREE.Vector3(x, 1.8, 2.8), rotX: 0, size: [2.4, 1.0, 1.5] });
      out.push({ pos: new THREE.Vector3(x, 2.8, 2.8), rotX: 0, size: [2.4, 1.0, 1.5] });
    }
    return out;
  }, []);

  const ref = useRef<THREE.InstancedMesh>(null!);
  useLayoutEffect(() => {
    const mat = new THREE.Matrix4();
    const quat = new THREE.Quaternion();
    const scale = new THREE.Vector3();
    boxes.forEach((b, i) => {
      quat.setFromEuler(new THREE.Euler(b.rotX, 0, 0));
      scale.set(...b.size);
      mat.compose(b.pos, quat, scale);
      ref.current.setMatrixAt(i, mat);
    });
    ref.current.instanceMatrix.needsUpdate = true;
  }, [boxes]);

  return (
    <instancedMesh ref={ref} args={[undefined, undefined, boxes.length]} frustumCulled={false}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#171b22" roughness={0.5} metalness={0.35} />
    </instancedMesh>
  );
}
