"use client";
import { useEffect, useMemo } from "react";
import * as THREE from "three";
import { point3, world } from "./world";

/** Original cream Gullyverse placard; travel still belongs to the boundary menu. */
function ReturnSign() {
  const texture=useMemo(()=>{
    const canvas=document.createElement("canvas");canvas.width=1024;canvas.height=192;
    const ctx=canvas.getContext("2d")!;
    ctx.fillStyle="#d9d4b5";ctx.fillRect(0,0,1024,192);
    ctx.strokeStyle="#4b4d40";ctx.lineWidth=8;ctx.strokeRect(12,12,1000,168);
    ctx.fillStyle="#202822";ctx.font="bold 64px sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("GULLYVERSE  →",512,100,950);
    const result=new THREE.CanvasTexture(canvas);result.colorSpace=THREE.SRGBColorSpace;return result;
  },[]);
  useEffect(()=>()=>texture.dispose(),[texture]);
  return <group position={point3(world.aftermovie.returnSignLocal)} rotation-y={Math.PI}>
    <mesh><boxGeometry args={[4.5,.84,.12]} /><meshStandardMaterial color="#504f46" roughness={.95} /></mesh>
    <mesh position-z={.065}><planeGeometry args={[4.4,.8]} /><meshStandardMaterial map={texture} roughness={.95} /></mesh>
  </group>;
}

export default function AftermovieEnvironment() {
  return <group position={point3(world.stage.origin)} rotation-y={world.stage.yaw}>
    {/* Keep the original dark material within the stage area, leaving the quarry ground visible behind it. */}
    <mesh rotation-x={-Math.PI/2} position={[0,.012,7.5]}>
      <planeGeometry args={[49,39]} /><meshStandardMaterial color="#07080b" roughness={.9} metalness={.1} />
    </mesh>
    <ReturnSign />
  </group>;
}
