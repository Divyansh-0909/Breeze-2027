"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/**
 * Landing pyro: golden gerb fountains — a bright FLAME core at each nozzle
 * (large soft sprites + flickering firelight) with a dense golden SPARK
 * spray arcing above it. Two Points clouds = two draw calls total.
 * Goes fully idle once the show ends.
 */

const SPARK_MAX = 4500;
const SPARK_RATE = 650; // per active jet
const FLAME_MAX = 700;
const FLAME_RATE = 110; // per active jet

const JETS = [
  { x: -2.4, z: 13.4 },
  { x: 2.4, z: 13.4 },
  { x: -2.4, z: 9.0 },
  { x: 2.4, z: 9.0 },
];

// firing windows: [start, end, jet indices]
const SEQUENCE: { start: number; end: number; jets: number[] }[] = [
  { start: 0.8, end: 1.7, jets: [0, 1] },
  { start: 2.1, end: 3.0, jets: [2, 3] },
  { start: 3.4, end: 4.8, jets: [0, 1, 2, 3] }, // finale — all four
];
const SHOW_END = 6.5;

const NOZZLE_Y = 1.78;

/** Soft radial sprite so flame puffs render as round glows, not squares. */
function makeSoftCircle(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = c.height = 64;
  const g = c.getContext("2d")!;
  const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, "rgba(255,255,255,1)");
  grad.addColorStop(0.4, "rgba(255,255,255,0.55)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
}

type Pool = {
  cursor: number;
  debt: number[];
  pos: Float32Array;
  vel: Float32Array;
  col: Float32Array;
  life: Float32Array;
  lifeMax: Float32Array;
};

function makePool(max: number): Pool {
  return {
    cursor: 0,
    debt: JETS.map(() => 0),
    pos: new Float32Array(max * 3).fill(-1000),
    vel: new Float32Array(max * 3),
    col: new Float32Array(max * 3),
    life: new Float32Array(max),
    lifeMax: new Float32Array(max).fill(1),
  };
}

function makeGeometry(p: Pool): THREE.BufferGeometry {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(p.pos, 3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute("color", new THREE.BufferAttribute(p.col, 3).setUsage(THREE.DynamicDrawUsage));
  return g;
}

export default function Fireworks(): React.ReactElement {
  const s = useMemo(
    () => ({ t: 0, done: false, sparks: makePool(SPARK_MAX), flames: makePool(FLAME_MAX) }),
    []
  );
  const sparkGeo = useMemo(() => makeGeometry(s.sparks), [s]);
  const flameGeo = useMemo(() => makeGeometry(s.flames), [s]);
  const lightRefs = useRef<(THREE.PointLight | null)[]>([]);

  const sparkMat = useMemo(() => {
    const m = new THREE.PointsMaterial({
      size: 0.085,
      vertexColors: true,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    m.toneMapped = false;
    return m;
  }, []);

  const flameMat = useMemo(() => {
    const m = new THREE.PointsMaterial({
      size: 0.65,
      map: makeSoftCircle(),
      vertexColors: true,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      sizeAttenuation: true,
    });
    m.toneMapped = false;
    return m;
  }, []);

  useFrame((_, rawDt) => {
    if (s.done) return;
    const dt = Math.min(rawDt, 0.05);
    s.t += dt;

    const activeJets = new Set<number>();
    for (const w of SEQUENCE) {
      if (s.t >= w.start && s.t <= w.end) w.jets.forEach((j) => activeJets.add(j));
    }

    // emit
    for (const ji of activeJets) {
      const jet = JETS[ji];
      // sparks — dense golden fountain spray
      s.sparks.debt[ji] += SPARK_RATE * dt;
      while (s.sparks.debt[ji] >= 1) {
        s.sparks.debt[ji] -= 1;
        const p = s.sparks;
        const i3 = p.cursor * 3;
        p.cursor = (p.cursor + 1) % SPARK_MAX;
        p.pos[i3] = jet.x + (Math.random() - 0.5) * 0.12;
        p.pos[i3 + 1] = NOZZLE_Y;
        p.pos[i3 + 2] = jet.z + (Math.random() - 0.5) * 0.12;
        const theta = Math.random() * Math.random() * 0.38; // dense core, thin fan
        const phi = Math.random() * Math.PI * 2;
        const speed = 7 + Math.random() * 4.5;
        p.vel[i3] = Math.sin(theta) * Math.cos(phi) * speed;
        p.vel[i3 + 1] = Math.cos(theta) * speed;
        p.vel[i3 + 2] = Math.sin(theta) * Math.sin(phi) * speed;
        const life = 0.8 + Math.random() * 0.6;
        p.life[p.cursor === 0 ? SPARK_MAX - 1 : p.cursor - 1] = life;
        p.lifeMax[p.cursor === 0 ? SPARK_MAX - 1 : p.cursor - 1] = life;
      }
      // flames — big soft puffs hugging the nozzle
      s.flames.debt[ji] += FLAME_RATE * dt;
      while (s.flames.debt[ji] >= 1) {
        s.flames.debt[ji] -= 1;
        const p = s.flames;
        const i = p.cursor;
        p.cursor = (p.cursor + 1) % FLAME_MAX;
        const i3 = i * 3;
        p.pos[i3] = jet.x + (Math.random() - 0.5) * 0.3;
        p.pos[i3 + 1] = NOZZLE_Y + Math.random() * 0.15;
        p.pos[i3 + 2] = jet.z + (Math.random() - 0.5) * 0.3;
        p.vel[i3] = (Math.random() - 0.5) * 0.9;
        p.vel[i3 + 1] = 2.6 + Math.random() * 2.2; // slow column of fire
        p.vel[i3 + 2] = (Math.random() - 0.5) * 0.9;
        const life = 0.35 + Math.random() * 0.3;
        p.life[i] = life;
        p.lifeMax[i] = life;
      }
    }

    // integrate sparks: real gravity → fountain arcs, white-gold → amber
    let anyAlive = false;
    const sparkDrag = Math.exp(-0.55 * dt);
    const sp = s.sparks;
    for (let i = 0; i < SPARK_MAX; i++) {
      if (sp.life[i] <= 0) {
        sp.col.set([0, 0, 0], i * 3);
        continue;
      }
      anyAlive = true;
      sp.life[i] -= dt;
      const i3 = i * 3;
      sp.vel[i3] *= sparkDrag;
      sp.vel[i3 + 1] = sp.vel[i3 + 1] * sparkDrag - 6.5 * dt;
      sp.vel[i3 + 2] *= sparkDrag;
      sp.pos[i3] += sp.vel[i3] * dt;
      sp.pos[i3 + 1] += sp.vel[i3 + 1] * dt;
      sp.pos[i3 + 2] += sp.vel[i3 + 2] * dt;
      const u = Math.max(sp.life[i] / sp.lifeMax[i], 0);
      sp.col[i3] = 2.6 * u;
      sp.col[i3 + 1] = 2.1 * Math.pow(u, 1.4);
      sp.col[i3 + 2] = 1.0 * Math.pow(u, 2.4);
    }

    // integrate flames: buoyant, quick fade, white-gold core → orange
    const flameDrag = Math.exp(-1.8 * dt);
    const fp = s.flames;
    for (let i = 0; i < FLAME_MAX; i++) {
      if (fp.life[i] <= 0) {
        fp.col.set([0, 0, 0], i * 3);
        continue;
      }
      anyAlive = true;
      fp.life[i] -= dt;
      const i3 = i * 3;
      fp.vel[i3] *= flameDrag;
      fp.vel[i3 + 1] *= flameDrag;
      fp.vel[i3 + 2] *= flameDrag;
      fp.pos[i3] += fp.vel[i3] * dt;
      fp.pos[i3 + 1] += fp.vel[i3 + 1] * dt;
      fp.pos[i3 + 2] += fp.vel[i3 + 2] * dt;
      const u = Math.max(fp.life[i] / fp.lifeMax[i], 0);
      fp.col[i3] = 1.9 * u;
      fp.col[i3 + 1] = 1.5 * Math.pow(u, 1.6);
      fp.col[i3 + 2] = 0.6 * Math.pow(u, 3);
    }

    sparkGeo.attributes.position.needsUpdate = true;
    sparkGeo.attributes.color.needsUpdate = true;
    flameGeo.attributes.position.needsUpdate = true;
    flameGeo.attributes.color.needsUpdate = true;

    // flickering firelight at active nozzles
    JETS.forEach((_, ji) => {
      const light = lightRefs.current[ji];
      if (!light) return;
      const target = activeJets.has(ji) ? 26 + Math.random() * 14 : 0;
      light.intensity += (target - light.intensity) * Math.min(1, dt * 14);
    });

    if (!anyAlive && s.t > SHOW_END) s.done = true; // show over — go idle
  });

  return (
    <group>
      {/* pyro pods — visible fixtures on the runway edges the fire erupts from */}
      {JETS.map((jet, i) => (
        <group key={i} position={[jet.x, 1.3, jet.z]}>
          <mesh position-y={0.16}>
            <boxGeometry args={[0.55, 0.32, 0.55]} />
            <meshStandardMaterial color="#101318" roughness={0.55} metalness={0.5} />
          </mesh>
          {/* nozzle */}
          <mesh position-y={0.4}>
            <cylinderGeometry args={[0.1, 0.14, 0.16, 10]} />
            <meshStandardMaterial color="#1c2027" roughness={0.4} metalness={0.7} />
          </mesh>
          {/* firelight kissing the deck + pod while the jet burns */}
          <pointLight
            ref={(el) => {
              lightRefs.current[i] = el;
            }}
            position-y={1}
            color="#ffb347"
            intensity={0}
            decay={2}
            distance={7}
          />
        </group>
      ))}
      <points geometry={sparkGeo} material={sparkMat} frustumCulled={false} />
      <points geometry={flameGeo} material={flameMat} frustumCulled={false} />
    </group>
  );
}
