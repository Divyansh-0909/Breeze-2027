"use client";
import React, { useLayoutEffect, useMemo, useRef } from "react";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";
import { PALETTE, STAGE } from "./palette";
// static import — Next bundles the image, no public/ copy needed
import breezeLogo from "../../../Assets/Images/breeze-logo.webp";

/**
 * All truss steel in the scene — towers, roof posts and beams — is generated
 * procedurally as box-truss members (chords, rungs, diagonals) and rendered
 * as a SINGLE InstancedMesh of unit cylinders: one draw call for ~1k members.
 */

type Member = { pos: THREE.Vector3; quat: THREE.Quaternion; len: number; r: number };

const UP = new THREE.Vector3(0, 1, 0);
const CHORD_R = 0.072; // thicker members also resolve >1px at distance (less shimmer)
const BRACE_R = 0.042;

function addMember(out: Member[], a: THREE.Vector3, b: THREE.Vector3, r: number) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  if (len < 1e-4) return;
  const quat = new THREE.Quaternion().setFromUnitVectors(UP, dir.normalize());
  out.push({ pos: new THREE.Vector3().addVectors(a, b).multiplyScalar(0.5), quat, len, r });
}

/** Generate a square box-truss between two points: 4 chords + rungs + alternating diagonals. */
function boxTruss(out: Member[], a: THREE.Vector3, b: THREE.Vector3, w = 0.5) {
  const dir = new THREE.Vector3().subVectors(b, a).normalize();
  const helper = Math.abs(dir.y) > 0.9 ? new THREE.Vector3(1, 0, 0) : new THREE.Vector3(0, 1, 0);
  const s = new THREE.Vector3().crossVectors(dir, helper).normalize();
  const u = new THREE.Vector3().crossVectors(s, dir).normalize();
  const h = w / 2;
  const corners = [
    new THREE.Vector3().addScaledVector(s, h).addScaledVector(u, h),
    new THREE.Vector3().addScaledVector(s, -h).addScaledVector(u, h),
    new THREE.Vector3().addScaledVector(s, -h).addScaledVector(u, -h),
    new THREE.Vector3().addScaledVector(s, h).addScaledVector(u, -h),
  ];
  for (const c of corners) {
    addMember(out, a.clone().add(c), b.clone().add(c), CHORD_R);
  }
  const len = a.distanceTo(b);
  const bays = Math.max(1, Math.round(len / 1.15));
  for (let i = 0; i <= bays; i++) {
    const p0 = a.clone().lerp(b, i / bays);
    for (let k = 0; k < 4; k++) {
      addMember(out, p0.clone().add(corners[k]), p0.clone().add(corners[(k + 1) % 4]), BRACE_R);
    }
    if (i < bays) {
      const p1 = a.clone().lerp(b, (i + 1) / bays);
      const flip = i % 2 === 0;
      for (let k = 0; k < 4; k++) {
        const c0 = corners[flip ? k : (k + 1) % 4];
        const c1 = corners[flip ? (k + 1) % 4 : k];
        addMember(out, p0.clone().add(c0), p1.clone().add(c1), BRACE_R);
      }
    }
  }
}

const v = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);

export default function Trusses(): React.ReactElement {
  const members = useMemo<Member[]>(() => {
    const m: Member[] = [];
    const { frontZ, backZ } = STAGE;
    const rigFrontZ = frontZ + 2.5; // front plane of the rig pushed out past the deck edge
    // Roof support towers (4 corners of the canopy) — slightly wider than the
    // deck so the rig visually clears the LED wall
    for (const x of [-13, 13]) {
      boxTruss(m, v(x, 0, rigFrontZ), v(x, 12.15, rigFrontZ), 0.75);
      boxTruss(m, v(x, 0, backZ), v(x, 12.15, backZ), 0.75);
    }
    // Roof beams: front (carries moving heads, overhangs the towers) + back
    boxTruss(m, v(-17, 11.65, rigFrontZ), v(17, 11.65, rigFrontZ), 0.75);
    boxTruss(m, v(-13, 11.65, backZ), v(13, 11.65, backZ), 0.75);
    // Side beams — connect the front and back corners so the rig reads as one box
    boxTruss(m, v(-13, 11.65, rigFrontZ), v(-13, 11.65, backZ), 0.75);
    boxTruss(m, v(13, 11.65, rigFrontZ), v(13, 11.65, backZ), 0.75);
    // Mid cross beam — spans the middle of the roof, parallel to the front beam
    const midZ = (rigFrontZ + backZ) / 2;
    boxTruss(m, v(-13, 11.65, midZ), v(13, 11.65, midZ), 0.75);
    return m;
  }, []);

  const ref = useRef<THREE.InstancedMesh>(null!);
  useLayoutEffect(() => {
    const mat = new THREE.Matrix4();
    const scale = new THREE.Vector3();
    const lit = new THREE.Color(1, 1, 1);
    const shadowed = new THREE.Color(0.22, 0.22, 0.25);
    const deepShadow = new THREE.Color(0.09, 0.09, 0.11); // behind the LED wall
    const c = new THREE.Color();
    members.forEach((mem, i) => {
      scale.set(mem.r, mem.len, mem.r);
      mat.compose(mem.pos, mem.quat, scale);
      ref.current.setMatrixAt(i, mat);
      // shade per member by how much LED-wall light can actually reach it:
      // - depth: fully shadowed behind the wall, ramping up toward the front
      // - height: the wall tops out ~y 10.5, so high members dim with altitude
      // - lateral: towers at ±13 stand beyond the wall's edges (±11)
      const depth = THREE.MathUtils.clamp((mem.pos.z + 2) / 8, 0, 1);
      const height = 1 - 0.68 * THREE.MathUtils.clamp((mem.pos.y - 8) / 4.5, 0, 1);
      let lateral = 1 - 0.3 * THREE.MathUtils.clamp((Math.abs(mem.pos.x) - 11) / 2, 0, 1);
      // front top beam: its overhanging ends fall away from the screen light
      if (mem.pos.y > 11 && mem.pos.z > 5) {
        lateral *= 1 - 0.5 * THREE.MathUtils.clamp((Math.abs(mem.pos.x) - 8) / 9, 0, 1);
      }
      if (mem.pos.y > 11 && Math.abs(mem.pos.x) > 12) {
        // top side beams: continuous ramp out of the deep shadow at the back
        // truss, brightening along their full length toward the front
        const tSide = THREE.MathUtils.clamp((mem.pos.z + 4.5) / 11, 0, 1);
        c.copy(deepShadow).lerp(lit, tSide * height * lateral);
      } else if (mem.pos.z < -4.5) {
        // fully behind the LED wall — deepest shadow, no gradient
        c.copy(deepShadow);
      } else {
        c.copy(shadowed).lerp(lit, depth * height * lateral);
      }
      ref.current.setColorAt(i, c);
    });
    ref.current.instanceMatrix.needsUpdate = true;
    if (ref.current.instanceColor) ref.current.instanceColor.needsUpdate = true;
  }, [members]);

  return (
    <group>
      <instancedMesh ref={ref} args={[undefined, undefined, members.length]} frustumCulled={false}>
        <cylinderGeometry args={[1, 1, 1, 6, 1]} />
        <meshStandardMaterial color={PALETTE.steel} metalness={0.85} roughness={0.35} />
      </instancedMesh>
      {/* black signage board mounted on the front face of the front top beam */}
      <mesh position={[0, 11.65, 7.05]}>
        <boxGeometry args={[4.6, 2.2, 0.3]} />
        <meshStandardMaterial color="#050608" roughness={0.8} metalness={0.2} />
      </mesh>
      <LogoBoard />
    </group>
  );
}

/** Glowing Breeze logo on the signage board (image has generous transparent
    padding, so the plane oversizes the board while the glyphs fit inside). */
function LogoBoard(): React.ReactElement {
  const tex = useLoader(THREE.TextureLoader, breezeLogo.src);
  const material = useMemo(() => {
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    const m = new THREE.MeshBasicMaterial({
      map: tex,
      transparent: true,
      color: new THREE.Color(1.7, 1.7, 1.7), // past 1.0 → bloom gives it the signage glow
    });
    m.toneMapped = false;
    return m;
  }, [tex]);

  return (
    <mesh position={[0, 11.65, 7.22]} material={material}>
      <planeGeometry args={[4.4, 4.4 / 1.5]} />
    </mesh>
  );
}
