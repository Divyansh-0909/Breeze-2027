"use client";

import { useFrame, useThree } from "@react-three/fiber";
import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

import {
  makeMudTexture,
  makeTurfPatchTexture,
  makeTurfTexture,
} from "../landing-page/gate3d/textures";

export function FestivalEnvironment({ intensity = 0.18 }: { intensity?: number }) {
  const gl = useThree((state) => state.gl);
  const scene = useThree((state) => state.scene);

  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = intensity;

    return () => {
      scene.environment = null;
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, intensity, scene]);

  return null;
}

export function FestivalGround({
  width = 38,
  depth = 34,
  mudZ = 7.4,
}: {
  width?: number;
  depth?: number;
  mudZ?: number;
}) {
  const turf = useMemo(() => {
    const texture = makeTurfTexture();
    texture.repeat.set(width / 3, depth / 3);
    return texture;
  }, [depth, width]);

  const turfPatches = useMemo(
    () =>
      makeTurfPatchTexture({
        w: 1536,
        h: 1536,
        count: 260,
        minR: 7,
        maxR: 64,
        seed: 7714,
        feather: 120,
      }),
    [],
  );

  const mud = useMemo(() => {
    const texture = makeMudTexture();
    texture.repeat.set(1.6, 4.6);
    return texture;
  }, []);

  useEffect(
    () => () => {
      turf.dispose();
      turfPatches.dispose();
      mud.dispose();
    },
    [mud, turf, turfPatches],
  );

  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.035, 1.5]} receiveShadow>
        <planeGeometry args={[width + 4, depth + 4]} />
        <meshStandardMaterial color="#070907" roughness={0.99} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.02, 1.5]} receiveShadow>
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial map={turf} color="#66705c" roughness={0.98} metalness={0} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.012, 1.5]} receiveShadow>
        <planeGeometry args={[width - 2, depth - 2]} />
        <meshStandardMaterial map={turfPatches} transparent depthWrite={false} roughness={0.98} />
      </mesh>
      <mesh rotation-x={-Math.PI / 2} rotation-z={-0.015} position={[0.1, -0.004, mudZ]} receiveShadow>
        <planeGeometry args={[4.9, 14.5]} />
        <meshStandardMaterial map={mud} color="#7b6950" roughness={0.99} metalness={0} />
      </mesh>
    </group>
  );
}

export function FestivalNightLighting({
  warmFocus = [0, 3.4, 2.1],
  coolFill = [-5.2, 4.2, 4.8],
}: {
  warmFocus?: [number, number, number];
  coolFill?: [number, number, number];
}) {
  return (
    <>
      <ambientLight intensity={0.055} color="#c9d1d2" />
      <hemisphereLight intensity={0.14} color="#738695" groundColor="#16130d" />
      <directionalLight
        castShadow
        position={[-5.5, 9.5, 5.5]}
        color="#aab9c3"
        intensity={0.78}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-far={30}
        shadow-bias={-0.0003}
      />
      <spotLight
        castShadow
        position={warmFocus}
        angle={0.6}
        penumbra={0.82}
        intensity={3.1}
        distance={15}
        decay={2}
        color="#ffd6a0"
      />
      <pointLight position={coolFill} color="#7892a5" intensity={1.05} distance={12} decay={2} />
      <pointLight position={[5.1, 2.9, 3.5]} color="#d8a96f" intensity={0.72} distance={9} decay={2} />
    </>
  );
}

export function ApproachCamera({
  from,
  to,
  lookAt,
  mobileFrom,
  mobileTo,
  mobileLookAt,
  duration = 2.2,
  instant = false,
  onArrive,
}: {
  from: [number, number, number];
  to: [number, number, number];
  lookAt: [number, number, number];
  mobileFrom?: [number, number, number];
  mobileTo?: [number, number, number];
  mobileLookAt?: [number, number, number];
  duration?: number;
  instant?: boolean;
  onArrive?: () => void;
}) {
  const { camera, size, pointer } = useThree();
  const elapsed = useRef(0);
  const finished = useRef(false);
  const desired = useRef(new THREE.Vector3());
  const currentLook = useRef(new THREE.Vector3());

  useEffect(() => {
    const mobile = size.width < 760;
    const start = mobile && mobileFrom ? mobileFrom : from;
    const targetLook = mobile && mobileLookAt ? mobileLookAt : lookAt;
    camera.position.set(...(instant ? (mobile && mobileTo ? mobileTo : to) : start));
    currentLook.current.set(...targetLook);
    camera.lookAt(currentLook.current);
    elapsed.current = instant ? duration : 0;
    finished.current = false;
  }, [camera, duration, from, instant, lookAt, mobileFrom, mobileLookAt, mobileTo, size.width, to]);

  useFrame((_, dt) => {
    const mobile = size.width < 760;
    elapsed.current += Math.min(dt, 0.05);
    const start = mobile && mobileFrom ? mobileFrom : from;
    const end = mobile && mobileTo ? mobileTo : to;
    const targetLook = mobile && mobileLookAt ? mobileLookAt : lookAt;
    const raw = instant ? 1 : THREE.MathUtils.clamp(elapsed.current / duration, 0, 1);
    const eased = raw * raw * (3 - 2 * raw);
    const subtleX = mobile ? 0 : pointer.x * 0.055 * raw;
    const subtleY = mobile ? 0 : pointer.y * 0.025 * raw;

    desired.current.set(
      THREE.MathUtils.lerp(start[0], end[0], eased) + subtleX,
      THREE.MathUtils.lerp(start[1], end[1], eased) + subtleY,
      THREE.MathUtils.lerp(start[2], end[2], eased),
    );
    camera.position.lerp(desired.current, 1 - Math.exp(-8 * dt));
    currentLook.current.lerp(
      new THREE.Vector3(targetLook[0] + subtleX * 0.18, targetLook[1] + subtleY * 0.14, targetLook[2]),
      1 - Math.exp(-9 * dt),
    );
    camera.lookAt(currentLook.current);

    if (raw >= 1 && !finished.current) {
      finished.current = true;
      onArrive?.();
    }
  });

  return null;
}
