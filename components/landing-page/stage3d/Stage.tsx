"use client";
import React from "react";
import { PALETTE, STAGE } from "./palette";

/**
 * Static architecture: stage deck, thrust runway (matches the reference's
 * arrow-shaped catwalk) and ground.
 */

export default function Stage(): React.ReactElement {
  const { topY, halfW, frontZ, backZ } = STAGE;
  const deckH = topY;

  return (
    <group>
      {/* Ground */}
      <mesh rotation-x={-Math.PI / 2} position-y={-0.01}>
        <circleGeometry args={[70, 48]} />
        <meshStandardMaterial color="#07080b" roughness={0.9} metalness={0.1} />
      </mesh>

      {/* Main platform */}
      <mesh position={[0, deckH / 2, (frontZ + backZ) / 2]}>
        <boxGeometry args={[halfW * 2, deckH, frontZ - backZ]} />
        <meshStandardMaterial color={PALETTE.carbon} roughness={0.55} metalness={0.35} />
      </mesh>

      {/* Thrust runway toward the audience */}
      <mesh position={[0, deckH / 2, frontZ + 5]}>
        <boxGeometry args={[6, deckH, 10]} />
        <meshStandardMaterial color={PALETTE.carbon} roughness={0.55} metalness={0.35} />
      </mesh>

    </group>
  );
}
