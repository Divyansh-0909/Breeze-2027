"use client";
import React, { useMemo } from "react";
import * as THREE from "three";
import { NIGHT } from "./palette";
import {
  makeAsphaltTexture,
  makeConcreteTexture,
  makeMudTexture,
  makePaverTexture,
} from "./textures";

/**
 * Ground plan: the gate stands at a CORNER of the rectangular paved ring that
 * surrounds the fest ground — on the ring's INNER edge, so you cross the full
 * width of the walkway and pass through the arch straight onto the ground
 * itself: packed mud, no paving. The two walkways leave the corner at 45°,
 * turning it on a true fillet (annulus sector, tangent into both bands), and
 * every paved edge is lined in cement kerb. Outside the ring: a cement
 * shoulder, then the road; grass everywhere else.
 */

const BAND_W = 9.0; // walkway width
const BAND_LEN = 40; // how far each side of the ring runs before the fog has it
const R_C = 6.1; // centreline turn radius — keeps the inner arc tight (1.6 m)
const KERB = 0.35; // cement edging width
const CEMENT = "#9aa1a8";

// The ring corner sits toward the camera so that the fillet's INNER edge
// passes right under the gate (which lives at z = 0): corner z − √2·R_C
// + inner radius = 0.
const ARC_IN = R_C - BAND_W / 2; // 1.6
const ARC_OUT = R_C + BAND_W / 2; // 10.6
const CORNER_Z = Math.SQRT2 * R_C - ARC_IN; // ≈ 7.03
const O_Z = CORNER_Z - Math.SQRT2 * R_C; // arc centre ≈ −1.6

// road + its cement shoulder, outside the ring's outer arc (apex ≈ z 9.0)
const ROAD_W = 5.5;
const ROAD_LEN = 64;
const SHOULDER_Z0 = O_Z + ARC_OUT; // 9.0 — outer arc apex
const SHOULDER_W = 1.5;

export default function Grounds(): React.ReactElement {
  // One paver tile spans 2.4 m → its 8 × 16 blocks land at a true-to-life
  // 0.30 × 0.15 m, identical on every strip of the ring.
  const TILE = 2.4;

  const paver = useMemo(() => {
    const t = makePaverTexture(false);
    t.repeat.set(BAND_LEN / TILE, BAND_W / TILE);
    return t;
  }, []);
  const paverB = useMemo(() => {
    const t = paver.clone();
    t.needsUpdate = true;
    return t;
  }, [paver]);
  const paverArc = useMemo(() => {
    // RingGeometry UVs are planar over ±outerR
    const t = paver.clone();
    t.needsUpdate = true;
    t.repeat.set((ARC_OUT * 2) / TILE, (ARC_OUT * 2) / TILE);
    return t;
  }, [paver]);

  const mud = useMemo(() => {
    const t = makeMudTexture();
    t.repeat.set(BAND_LEN / 3.2, BAND_LEN / 3.2); // one tile ≈ 3.2 m
    return t;
  }, []);

  const concrete = useMemo(() => {
    const t = makeConcreteTexture();
    t.repeat.set(ROAD_LEN / TILE, SHOULDER_W / TILE);
    return t;
  }, []);

  const asphalt = useMemo(() => {
    const t = makeAsphaltTexture();
    t.repeat.set(ROAD_LEN / 6.4, 1); // one asphalt tile ≈ 6.4 m of length
    return t;
  }, []);

  const bandMatA = useMemo(
    () => new THREE.MeshStandardMaterial({ map: paver, roughness: 0.88, metalness: 0.04 }),
    [paver]
  );
  const bandMatB = useMemo(
    () => new THREE.MeshStandardMaterial({ map: paverB, roughness: 0.88, metalness: 0.04 }),
    [paverB]
  );
  const arcMat = useMemo(
    () => new THREE.MeshStandardMaterial({ map: paverArc, roughness: 0.88, metalness: 0.04 }),
    [paverArc]
  );
  const mudMat = useMemo(
    () => new THREE.MeshStandardMaterial({ map: mud, roughness: 0.97, metalness: 0.0 }),
    [mud]
  );
  const kerbMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: CEMENT, roughness: 0.85, metalness: 0.02 }),
    []
  );
  const shoulderMat = useMemo(
    () => new THREE.MeshStandardMaterial({ map: concrete, roughness: 0.9, metalness: 0.02 }),
    [concrete]
  );
  const roadMat = useMemo(
    () => new THREE.MeshStandardMaterial({ map: asphalt, roughness: 0.94, metalness: 0.02 }),
    [asphalt]
  );

  return (
    <group>
      {/* base earth — fills the horizon under everything else */}
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.02, -10]} receiveShadow>
        <circleGeometry args={[90, 40]} />
        <meshStandardMaterial color={"#0a0d0b"} roughness={0.98} />
      </mesh>

      {/* grass everywhere outside the ring — under the bands, over the earth */}
      <mesh rotation-x={-Math.PI / 2} position={[0, 0.002, -8]} receiveShadow>
        <planeGeometry args={[90, 90]} />
        <meshStandardMaterial color={NIGHT.grass} roughness={0.97} />
      </mesh>

      {/* the ground interior: a mud square whose corner touches the ring
          corner, rotated 45° so its sides run with the two walkways — the
          90° wedge you step onto through the arch */}
      <mesh
        rotation-x={-Math.PI / 2}
        rotation-z={Math.PI / 4}
        position={[0, 0.006, CORNER_Z - Math.SQRT2 * (BAND_LEN / 2)]}
        receiveShadow
      >
        <planeGeometry args={[BAND_LEN, BAND_LEN]} />
        <primitive object={mudMat} attach="material" />
      </mesh>

      {/* cement shoulder between the ring and the road — the offset strip */}
      <mesh
        rotation-x={-Math.PI / 2}
        position={[0, 0.009, SHOULDER_Z0 + SHOULDER_W / 2]}
        receiveShadow
      >
        <planeGeometry args={[ROAD_LEN, SHOULDER_W]} />
        <primitive object={shoulderMat} attach="material" />
      </mesh>

      {/* the road, past the shoulder */}
      <mesh
        rotation-x={-Math.PI / 2}
        position={[0, 0.008, SHOULDER_Z0 + SHOULDER_W + ROAD_W / 2]}
        receiveShadow
      >
        <planeGeometry args={[ROAD_LEN, ROAD_W]} />
        <primitive object={roadMat} attach="material" />
      </mesh>

      {/* the corner: an annulus sector the same width as the walkways, running
          tangent-to-tangent, its cement kerbs following both edges as rings */}
      <group position={[0, 0, CORNER_Z - Math.SQRT2 * R_C]}>
        <mesh rotation-x={-Math.PI / 2} position-y={0.0115} receiveShadow>
          <ringGeometry args={[ARC_IN, ARC_OUT, 64, 1, (5 * Math.PI) / 4, Math.PI / 2]} />
          <primitive object={arcMat} attach="material" />
        </mesh>
        <mesh rotation-x={-Math.PI / 2} position-y={0.014} material={kerbMat}>
          <ringGeometry args={[ARC_IN - KERB, ARC_IN, 48, 1, (5 * Math.PI) / 4, Math.PI / 2]} />
        </mesh>
        <mesh rotation-x={-Math.PI / 2} position-y={0.014} material={kerbMat}>
          <ringGeometry args={[ARC_OUT, ARC_OUT + KERB, 64, 1, (5 * Math.PI) / 4, Math.PI / 2]} />
        </mesh>
      </group>

      {/* ---- the two straight walkways ----
          Each starts exactly at its tangent point with the corner arc (local
          x = R_C from the corner) and recedes inward at 45°, cement kerb
          strips lining both edges. */}
      {(
        [
          [(3 * Math.PI) / 4, bandMatA], // back-left
          [Math.PI / 4, bandMatB], // back-right
        ] as const
      ).map(([angle, mat], i) => (
        <group key={i} position={[0, 0.012, CORNER_Z]} rotation-y={angle}>
          <mesh rotation-x={-Math.PI / 2} position={[R_C + BAND_LEN / 2, 0, 0]} receiveShadow>
            <planeGeometry args={[BAND_LEN, BAND_W]} />
            <primitive object={mat} attach="material" />
          </mesh>
          {[-1, 1].map((s) => (
            <mesh
              key={s}
              rotation-x={-Math.PI / 2}
              position={[R_C + BAND_LEN / 2, 0.002, s * (BAND_W / 2 + KERB / 2)]}
              material={kerbMat}
            >
              <planeGeometry args={[BAND_LEN, KERB]} />
            </mesh>
          ))}
        </group>
      ))}
    </group>
  );
}
