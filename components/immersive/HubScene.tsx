"use client";
import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { mapLabels } from "./navigation";
import { ReadinessGate } from "./rendering";
import type { ImmersiveRuntime } from "./runtime";

/** Temporary art only. Replace the shell and rock masses with approved authored GLBs. */
export function WorldSign({ label, position, rotation = [0, 0, 0], muted = false }: { label: string; position: [number, number, number]; rotation?: [number, number, number]; muted?: boolean }) {
  const texture = useMemo(() => {
    const canvas = document.createElement("canvas"); canvas.width = 1024; canvas.height = 192;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = muted ? "#827f71" : "#d9d4b5"; ctx.fillRect(0, 0, 1024, 192);
    ctx.strokeStyle = "#4b4d40"; ctx.lineWidth = 8; ctx.strokeRect(12, 12, 1000, 168);
    ctx.fillStyle = "#202822"; ctx.font = "bold 64px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(label, 512, 100, 950);
    const result = new THREE.CanvasTexture(canvas); result.colorSpace = THREE.SRGBColorSpace; return result;
  }, [label, muted]);
  useEffect(() => () => texture.dispose(), [texture]);
  return <group position={position} rotation={rotation}>
    <mesh><boxGeometry args={[4.5, 0.84, 0.12]} /><meshStandardMaterial color="#504f46" roughness={0.95} /></mesh>
    <mesh position-z={0.065}><planeGeometry args={[4.4, 0.8]} /><meshStandardMaterial map={texture} roughness={0.95} /></mesh>
  </group>;
}

export function CavernBoundary({ centerZ = -85, tunnelOpening = false }: { centerZ?: number; tunnelOpening?: boolean }) {
  return <group>
    {Array.from({ length: 28 }, (_, i) => {
      // These three masses intersect the authored tunnel corridor. Leave an
      // actual opening; the camera must never pass through a solid rock face.
      if (tunnelOpening && (i === 0 || i === 1 || i === 27)) return null;
      const angle = i / 28 * Math.PI * 2;
      // Open sky is deliberate: there is no enclosing roof geometry.
      const h = 21 + Math.sin(i * 4.1) * 6;
      return <mesh key={i} position={[Math.sin(angle) * 47, h * 0.47 - 2, centerZ + Math.cos(angle) * 63]} rotation={[0.08 * Math.sin(i), angle, 0.1 * Math.cos(i)]} scale={[14, h, 12]}>
        <dodecahedronGeometry args={[1, 0]} /><meshStandardMaterial color={i % 3 === 0 ? "#74776d" : "#838479"} roughness={0.98} flatShading />
      </mesh>;
    })}
  </group>;
}

function TunnelBlockout() {
  const paint = useMemo(() => {
    const canvas = document.createElement("canvas"); canvas.width = 2048; canvas.height = 512;
    const ctx = canvas.getContext("2d")!; ctx.fillStyle = "#888982"; ctx.fillRect(0, 0, 2048, 512);
    // Seeded scuffs/overpaint, explicitly a placeholder pending reference-based baked concrete.
    for (let i = 0; i < 1800; i++) { ctx.fillStyle = i % 2 ? "#6f716944" : "#b4b4a633"; ctx.fillRect((i * 173) % 2048, (i * 79) % 512, 2 + i % 15, 2 + i % 8); }
    ["BREEZE", "GULLY", "27", "MAKE SOME NOISE", "BREEZE", "GULLYVERSE"].forEach((word, i) => {
      ctx.save(); ctx.translate(110 + i * 320, 140 + i % 2 * 160); ctx.rotate(i % 2 ? -0.12 : 0.08);
      ctx.font = "italic bold 72px sans-serif"; ctx.lineWidth = 10; ctx.strokeStyle = "#293837"; ctx.strokeText(word, 0, 0, 295);
      ctx.fillStyle = ["#b1bdac", "#688b86", "#ae8176"][i % 3]; ctx.fillText(word, 0, 0, 295); ctx.restore();
    });
    const t = new THREE.CanvasTexture(canvas); t.colorSpace = THREE.SRGBColorSpace; return t;
  }, []);
  useEffect(() => () => paint.dispose(), [paint]);
  return <group>
    {[-1, 1].map((side) => <mesh key={side} position={[side * 3.35, 2.1, -19]}><boxGeometry args={[0.5, 4.2, 38]} /><meshStandardMaterial map={paint} roughness={0.98} /></mesh>)}
    <mesh position={[0, 4.35, -19]}><boxGeometry args={[7.2, 0.35, 38]} /><meshStandardMaterial color="#74756d" roughness={1} /></mesh>
    <mesh rotation-x={-Math.PI / 2} position={[0, -0.025, -19]}><planeGeometry args={[7.2, 42]} /><meshStandardMaterial color="#6a6b62" roughness={1} /></mesh>
    {[0, 1, 2, 3, 4].map((i) => <mesh key={i} position={[0, 4.1, -3 - i * 7]}><boxGeometry args={[1.1, 0.05, 0.15]} /><meshStandardMaterial color="#c6cbc2" emissive="#b9c1b9" emissiveIntensity={0.6} /></mesh>)}
    <pointLight position={[0, 2.8, -18]} intensity={28} distance={28} decay={1.5} color="#cdd4cd" />
  </group>;
}

function DistantCrowd({ count }: { count: number }) {
  const mesh = useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(() => {
    const matrix = new THREE.Matrix4();
    for (let i = 0; i < count; i++) { matrix.makeTranslation(((i * 37) % 100) / 100 * 26 - 13, 0.85, -112 + ((i * 19) % 100) / 100 * 15); mesh.current?.setMatrixAt(i, matrix); }
    if (mesh.current) mesh.current.instanceMatrix.needsUpdate = true;
  }, [count]);
  return <instancedMesh ref={mesh} args={[undefined, undefined, count]}><capsuleGeometry args={[0.23, 1.15, 2, 4]} /><meshStandardMaterial color="#373d3b" roughness={1} /></instancedMesh>;
}

export default function HubScene({ runtime, serial, quality }: { runtime: ImmersiveRuntime; serial: number; quality: number }) {
  return <>
    <color attach="background" args={["#b9c6c8"]} /><fog attach="fog" args={["#b9c6c8", 85, 195]} />
    <hemisphereLight args={["#dae5e6", "#686b59", 1.8]} />
    <directionalLight position={[-18, 42, -65]} intensity={2} color="#f4f4e8" />
    <CavernBoundary tunnelOpening />
    <mesh rotation-x={-Math.PI / 2} position={[0, -0.06, -85]}><planeGeometry args={[98, 136]} /><meshStandardMaterial color="#87897b" roughness={1} /></mesh>
    <TunnelBlockout />
    {/* Actual steel beam, uprights and hangers: labels are textured physical boards. */}
    <group position={[0, 0, -58]}>
      {[-6, 6].map((x) => <mesh key={x} position={[x, 3.6, 0]}><cylinderGeometry args={[0.1, 0.1, 7.2, 8]} /><meshStandardMaterial color="#616b68" roughness={0.65} metalness={0.5} /></mesh>)}
      <mesh position={[0, 7.15, 0]} rotation-z={Math.PI / 2}><cylinderGeometry args={[0.14, 0.14, 12.4, 8]} /><meshStandardMaterial color="#616b68" roughness={0.65} metalness={0.5} /></mesh>
      {[-2.5, 2.5].map((x) => <mesh key={x} position={[x, 5.5, 0]}><cylinderGeometry args={[0.025, 0.025, 3.2, 5]} /><meshStandardMaterial color="#4e5550" roughness={0.8} /></mesh>)}
    </group>
    {mapLabels.map((label, i) => <WorldSign key={label} label={label.toUpperCase() + (label === "Aftermovie" ? "  ↑" : "")} muted={label !== "Aftermovie"} position={[i % 2 === 0 ? -2.5 : 2.5, 6.25 - Math.floor(i / 2) * 1.05, -57.9]} />)}
    <WorldSign label="AFTERMOVIE  ↑" position={[0, 1, -60.5]} />
    {[-1, 1].flatMap((side) => [0, 1, 2].map((i) => <group key={`${side}-${i}`} position={[side * (23 + i % 2 * 4), 0, -62 - i * 15]}>
      <mesh position-y={1}><boxGeometry args={[6, 2, 3]} /><meshStandardMaterial color="#706957" roughness={1} /></mesh>
      <mesh position-y={3.1} rotation-z={side * 0.05}><boxGeometry args={[7, 0.2, 4]} /><meshStandardMaterial color={i % 2 ? "#6e827c" : "#a8a48f"} roughness={1} /></mesh>
      {[-2.7, 2.7].map((x) => <mesh key={x} position={[x, 1.7, 1.5]}><cylinderGeometry args={[0.06, 0.06, 3.4, 6]} /><meshStandardMaterial color="#65665b" roughness={0.8} /></mesh>)}
    </group>))}
    <group position={[0, 0, -130]}>
      <mesh position-y={1}><boxGeometry args={[26, 2, 12]} /><meshStandardMaterial color="#303b39" roughness={1} /></mesh>
      <mesh position={[0, 7, -3]}><boxGeometry args={[22, 9, 0.5]} /><meshStandardMaterial color="#27302e" roughness={0.95} /></mesh>
      <mesh position={[0, 12, 0]}><boxGeometry args={[28, 0.4, 12]} /><meshStandardMaterial color="#454c49" roughness={0.9} /></mesh>
    </group>
    <DistantCrowd count={quality >= 2 ? 60 : 140} />
    {["boot", "covered", "recovering"].includes(runtime.getSnapshot().phase) && <ReadinessGate key={serial} runtime={runtime} serial={serial} />}
  </>;
}
