"use client";

import { Canvas, useThree } from "@react-three/fiber";
import { Bloom, EffectComposer, Noise, Vignette } from "@react-three/postprocessing";
import { useEffect, useMemo } from "react";
import * as THREE from "three";
import { ApproachCamera, FestivalEnvironment, FestivalGround, FestivalNightLighting } from "../../../components/three/FestivalNight";
import { useTeamBoardTexture } from "./useTeamBoardTexture";

const WIDTH = 10.8;
const HEIGHT = 6.25;

function useBoardTextures() {
  const wood = useMemo(() => {
    const canvas = document.createElement("canvas"); canvas.width = canvas.height = 512;
    const ctx = canvas.getContext("2d")!; ctx.fillStyle = "#4d2916"; ctx.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 160; i += 1) {
      const y = i * 3.5; ctx.strokeStyle = i % 4 ? "rgba(20, 9, 4, .2)" : "rgba(229, 159, 82, .2)"; ctx.lineWidth = 1 + i % 3;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.bezierCurveTo(120, y - 9, 340, y + 11, 512, y - 3); ctx.stroke();
    }
    const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace; texture.wrapS = texture.wrapT = THREE.RepeatWrapping; texture.repeat.set(2.2, 1.2); texture.anisotropy = 8; return texture;
  }, []);
  useEffect(() => () => { wood.dispose(); }, [wood]);
  return wood;
}

function FestivalSet() {
  const lights = [[-8.8, 1.15, -3.8, "#edb86d"], [-6.6, 1.55, -8.9, "#8db5d3"], [8.4, 1.25, -4.2, "#f3c16e"], [6.4, 1.8, -9.2, "#738fac"]] as const;
  return <>{[[-7.2, -6.5, 2.75], [7.4, -7.7, 2.45]].map(([x, z, r]) => <group key={x} position={[x, 0, z]} rotation-y={x < 0 ? .25 : -.25}><mesh position={[0, 1.25, 0]} castShadow><coneGeometry args={[r, 2.5, 4]} /><meshStandardMaterial color="#383f36" roughness={.92} /></mesh><mesh position={[0, .03, 0]} rotation-x={-Math.PI / 2} receiveShadow><circleGeometry args={[r, 20]} /><meshStandardMaterial color="#22251e" roughness={1} /></mesh></group>)}{lights.map(([x, y, z, color]) => <group key={`${x}-${z}`} position={[x, 0, z]}><mesh position={[0, y / 2, 0]} castShadow><cylinderGeometry args={[.035, .05, y, 8]} /><meshStandardMaterial color="#252b2a" metalness={.62} roughness={.36} /></mesh><mesh position={[0, y, 0]}><sphereGeometry args={[.12, 12, 12]} /><meshBasicMaterial color={color} toneMapped={false} /></mesh><pointLight position={[0, y, 0]} color={color} intensity={5.5} distance={5.5} decay={2} /></group>)}</>;
}

function PhysicalBoard() {
  const wood = useBoardTextures();
  const board = useTeamBoardTexture();
  return <group>{[-4.35, 4.35].map(x => <mesh key={x} position={[x, 1.35, -.13]} rotation-z={x < 0 ? .045 : -.045} castShadow receiveShadow><cylinderGeometry args={[.18, .23, 3.25, 10]} /><meshStandardMaterial map={wood} color="#785033" roughness={.76} /></mesh>)}<mesh position={[0, 3.55, -.13]} castShadow receiveShadow><boxGeometry args={[WIDTH + .52, HEIGHT + .52, .26]} /><meshStandardMaterial map={wood} color="#704525" roughness={.72} /></mesh><mesh position={[0, 3.55, .035]} receiveShadow><planeGeometry args={[WIDTH, HEIGHT]} /><meshStandardMaterial map={board ?? undefined} color={board ? "#f5f1e8" : "#38513d"} roughness={.84} emissive="#ffffff" emissiveMap={board ?? undefined} emissiveIntensity={board ? .07 : 0} /></mesh><mesh position={[0, .12, .24]} receiveShadow><cylinderGeometry args={[3.1, 4.1, .15, 48]} /><meshStandardMaterial color="#33291b" roughness={.95} /></mesh>{[-4.45, -2.25, 0, 2.25, 4.45].map(x => <group key={x} position={[x, 6.8, .22]}><mesh><sphereGeometry args={[.095, 14, 14]} /><meshBasicMaterial color="#ffe0a1" toneMapped={false} /></mesh><pointLight color="#ffd38b" intensity={4.5} distance={4.2} decay={2} /></group>)}<spotLight position={[0, 7.8, 4.2]} target-position={[0, 3.4, 0]} color="#ffd8a6" intensity={11} angle={.52} penumbra={.75} distance={14} decay={2} castShadow /></group>;
}

function TeamCameraLens() {
  const { camera, size } = useThree();

  useEffect(() => {
    if (!(camera instanceof THREE.PerspectiveCamera)) return;
    const nextFov = size.width < 760 ? 75 : 43;
    if (camera.fov === nextFov) return;
    camera.fov = nextFov;
    camera.updateProjectionMatrix();
  }, [camera, size.width]);

  return null;
}

function Scene({ onFinish, instant }: { onFinish: () => void; instant: boolean }) {
  const { scene } = useThree();
  useEffect(() => { scene.fog = new THREE.Fog("#070b0b", 14, 36); return () => { scene.fog = null; }; }, [scene]);
  return <><color attach="background" args={["#05080b"]} /><FestivalEnvironment intensity={.16} /><TeamCameraLens /><ApproachCamera from={[12.5, 4.6, 17.5]} to={[0, 3.58, 10.9]} lookAt={[0, 3.45, 0]} mobileFrom={[9.5, 4.45, 26]} mobileTo={[0, 3.42, 20]} mobileLookAt={[0, 3.42, 0]} duration={3.35} instant={instant} onArrive={onFinish} /><FestivalNightLighting warmFocus={[0, 6.5, 5.8]} coolFill={[-6.5, 4.2, 5.8]} /><FestivalGround width={34} depth={34} mudZ={7.7} /><FestivalSet /><PhysicalBoard /></>;
}

export default function BackstageCorridor({ onFinish, instant = false }: { onFinish: () => void; instant?: boolean }) {
  return <Canvas shadows dpr={[1, 1.5]} camera={{ fov: 43, near: .1, far: 90, position: [12.5, 4.6, 17.5] }} gl={{ antialias: true, powerPreference: "high-performance" }} onCreated={({ gl }) => { gl.toneMapping = THREE.ACESFilmicToneMapping; gl.toneMappingExposure = 1.05; gl.shadowMap.type = THREE.PCFSoftShadowMap; }}><Scene onFinish={onFinish} instant={instant} /><EffectComposer multisampling={0}><Bloom intensity={.38} luminanceThreshold={1.05} mipmapBlur /><Vignette eskil={false} offset={.13} darkness={.62} /><Noise opacity={.012} /></EffectComposer></Canvas>;
}
