"use client";
import React, { useMemo } from "react";
import * as THREE from "three";
import { makeSkyTexture } from "./textures";

/** Night dome + starfield. Unfogged, so it stays as the true backdrop. */
export default function Sky(): React.ReactElement {
  const tex = useMemo(() => makeSkyTexture(), []);

  const stars = useMemo(() => {
    const n = 520;
    const arr = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      // upper hemisphere only — below the horizon there is nothing to see
      const a = Math.random() * Math.PI * 2;
      const b = Math.acos(Math.random() * 0.92 + 0.06);
      const r = 74;
      arr[i * 3] = Math.sin(b) * Math.cos(a) * r;
      arr[i * 3 + 1] = Math.abs(Math.cos(b)) * r * 0.85 + 4;
      arr[i * 3 + 2] = Math.sin(b) * Math.sin(a) * r;
    }
    return arr;
  }, []);

  return (
    <group>
      <mesh>
        <sphereGeometry args={[86, 32, 20]} />
        <meshBasicMaterial map={tex} side={THREE.BackSide} fog={false} depthWrite={false} />
      </mesh>
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            array={stars}
            count={stars.length / 3}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial
          color={"#cddcf7"}
          size={0.32}
          sizeAttenuation
          transparent
          opacity={0.7}
          depthWrite={false}
          fog={false}
        />
      </points>
    </group>
  );
}
