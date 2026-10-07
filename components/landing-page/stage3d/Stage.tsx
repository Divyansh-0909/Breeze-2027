"use client";
import React from "react";
import BlenderAsset from "../../three/BlenderAsset";

/**
 * Static architecture: stage deck, thrust runway (matches the reference's
 * arrow-shaped catwalk) and ground.
 */

export default function Stage(): React.ReactElement {
  return (
    <group>
      {/* Ground */}
      <mesh rotation-x={-Math.PI / 2} position-y={-0.01}>
        <circleGeometry args={[70, 48]} />
        <meshStandardMaterial color="#07080b" roughness={0.9} metalness={0.1} />
      </mesh>

      <BlenderAsset url="/models/breeze/aftermovie-stage.glb" />
    </group>
  );
}
