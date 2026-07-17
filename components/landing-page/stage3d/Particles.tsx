"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/** Drifting haze dust — a single Points cloud, additive, ~500 verts. */
export default function Particles(): React.ReactElement {
  const ref = useRef<THREE.Points>(null!);

  const geometry = useMemo(() => {
    const count = 500;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 44;
      positions[i * 3 + 1] = Math.random() * 15 + 0.5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 30 + 3;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return g;
  }, []);

  const material = useMemo(() => {
    const m = new THREE.PointsMaterial({
      color: "#8fd4ef",
      size: 0.07,
      transparent: true,
      opacity: 0.4,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    m.toneMapped = false;
    return m;
  }, []);

  useFrame(({ clock }, dt) => {
    ref.current.rotation.y += dt * 0.012;
    ref.current.position.y = Math.sin(clock.elapsedTime * 0.15) * 0.4;
  });

  return <points ref={ref} geometry={geometry} material={material} frustumCulled={false} />;
}
