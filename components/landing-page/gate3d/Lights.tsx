"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { GATE } from "./palette";

/**
 * The ENTIRE scene is lit by two ground flood fixtures standing on the paving
 * in front of the gate, aimed up at the top board — no moon, no ambient, no
 * hidden fills. What their cones touch glows; everything else falls to the
 * night sky's silhouette. Both cast shadows, so the pillars, the overhanging
 * boughs and anyone crossing the beam of light print onto the facade.
 *
 * The fixtures are diegetic: visible housings with a glowing lens, ramping
 * with `powerRef` like real floods warming up.
 */

// tight against the stand — one unit at each pillar's front corner, so both
// are inside even the zoomed desktop crop. The steep up-angle is the classic
// event-uplighter look.
// centred on each pillar (GATE.pillarX ≈ 3.29 with the poster-sized boards)
// and standing on the paving just in front of the facade
const FIXTURES = [
  { pos: [-3.3, 0, 1.6] as const, aim: [-2.4, 0, 0] as const },
  { pos: [3.3, 0, 1.6] as const, aim: [2.4, 0, 0] as const },
];

export default function Lights({
  powerRef,
}: {
  powerRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const beamMidY = GATE.pillarTopY + GATE.beamH / 2;

  // spotlight targets must live in the scene graph to be respected
  const targets = useMemo(
    () =>
      FIXTURES.map((f) => {
        const o = new THREE.Object3D();
        o.position.set(f.aim[0], beamMidY, 0);
        return o;
      }),
    [beamMidY]
  );

  // orient each fixture head at its target
  const headQuats = useMemo(
    () =>
      FIXTURES.map((f, i) => {
        const head = new THREE.Vector3(f.pos[0], 0.38, f.pos[2]);
        const dir = targets[i].position.clone().sub(head).normalize();
        return new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 0, 1),
          dir
        );
      }),
    [targets]
  );

  const spots = useRef<(THREE.SpotLight | null)[]>([]);
  const spills = useRef<(THREE.PointLight | null)[]>([]);
  const lensMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#1b1d21",
        emissive: new THREE.Color("#ffe9c4"),
        emissiveIntensity: 0,
        roughness: 0.4,
        toneMapped: false,
      }),
    []
  );
  const bodyMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({ color: "#26292e", roughness: 0.7, metalness: 0.5 }),
    []
  );

  useFrame(() => {
    const p = powerRef.current;
    spots.current.forEach((l) => {
      if (l) l.intensity = p * 38;
    });
    spills.current.forEach((l) => {
      if (l) l.intensity = p * 5.5;
    });
    lensMat.emissiveIntensity = p * 3.0;
  });

  return (
    <group>
      {FIXTURES.map((f, i) => (
        <group key={i}>
          <primitive object={targets[i]} />

          {/* fixture: base plate + aimed head with glowing lens */}
          <group position={[f.pos[0], 0, f.pos[2]]}>
            <mesh position={[0, 0.05, 0]} material={bodyMat} castShadow>
              <boxGeometry args={[0.34, 0.1, 0.34]} />
            </mesh>
            <group position={[0, 0.38, 0]} quaternion={headQuats[i]}>
              {/* cylinder axis is local Y — lay it along local Z, the aim axis */}
              <mesh material={bodyMat} rotation-x={Math.PI / 2} castShadow>
                <cylinderGeometry args={[0.13, 0.16, 0.34, 12]} />
              </mesh>
              {/* lens at the head's mouth, facing the board */}
              <mesh position={[0, 0, 0.18]}>
                <circleGeometry args={[0.11, 16]} />
                <primitive object={lensMat} attach="material" />
              </mesh>
            </group>
            {/* stem */}
            <mesh position={[0, 0.22, 0]} material={bodyMat}>
              <cylinderGeometry args={[0.035, 0.035, 0.26, 8]} />
            </mesh>
          </group>

          {/* low backscatter off each unit: lifts the paving around the
              fixtures so the path reads a step brighter than the rest of
              the environment, while the fiction stays "two lights" */}
          <pointLight
            ref={(l) => {
              spills.current[i] = l;
            }}
            position={[f.pos[0], 0.5, f.pos[2]]}
            color={"#ffe3b8"}
            intensity={0}
            distance={15}
            decay={1.7}
          />

          <spotLight
            ref={(l) => {
              spots.current[i] = l;
            }}
            target={targets[i]}
            position={[f.pos[0], 0.42, f.pos[2]]}
            color={"#ffedc8"}
            intensity={0}
            angle={0.52}
            penumbra={0.6}
            distance={30}
            decay={1.35}
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
            shadow-camera-near={0.5}
            shadow-camera-far={30}
            shadow-bias={-0.0004}
          />
        </group>
      ))}
    </group>
  );
}
