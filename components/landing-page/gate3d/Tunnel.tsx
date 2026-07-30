"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { SIGN, TUNNEL, VAULT } from "./palette";
import { makePieceTexture, makeShellTexture } from "./graffiti";
import { makeAsphaltTexture, rng } from "./textures";

/**
 * The graffiti tunnel you fly down after clicking through the arch: a
 * flat-roofed brick run, painted end to end and strip-lit from the ceiling. It
 * opens onto the fest ground at `endZ`. Its section is the arch's own opening
 * (see `TUNNEL` in palette), so the walls carry straight on from the boards'
 * inner reveals.
 *
 * Lighting is deliberately not one lamp per fixture — a run this long would
 * need dozens and this scene already spends its light budget on the arch's two
 * floods. Instead ONE point light rides along with the camera, which is
 * indistinguishable from per-fixture lighting while you're moving and costs a
 * single light. The rods themselves are emissive geometry that glows without
 * lighting anything, the same trick the lamps out on the ground use.
 */

/** One tile of the shell texture spans this much of the tunnel's length. */
const TILE_M = 26;

/**
 * The shell: three flat runs — left wall, roof, right wall — each extruded the
 * length of the tunnel.
 *
 * Built by hand rather than from a box so v can follow TRUE arc length around
 * the section: the paint then keeps one constant scale as it turns the corner
 * onto the ceiling instead of being stretched to whatever a primitive's UVs
 * happen to allocate. The runs are also unwelded from each other, so the
 * wall/roof corners stay crisp — a shared vertex averages the two normals and
 * rounds the junction off, which on a built surface reads as moulded pipe.
 */
function buildShell(): THREE.BufferGeometry {
  const { halfW, roofY, startZ, endZ, length, profileS } = TUNNEL;
  const repeatU = length / TILE_M;

  const segs: {
    a: [number, number];
    b: [number, number];
    n: [number, number, number];
  }[] = [
    { a: [-halfW, 0], b: [-halfW, roofY], n: [1, 0, 0] },
    { a: [-halfW, roofY], b: [halfW, roofY], n: [0, -1, 0] },
    { a: [halfW, roofY], b: [halfW, 0], n: [-1, 0, 0] },
  ];

  const pos: number[] = [];
  const nor: number[] = [];
  const uv: number[] = [];
  const idx: number[] = [];
  let s = 0;

  for (const seg of segs) {
    const len = Math.hypot(seg.b[0] - seg.a[0], seg.b[1] - seg.a[1]);
    const base = pos.length / 3;
    for (const [p, v] of [
      [seg.a, s / profileS],
      [seg.b, (s + len) / profileS],
    ] as const) {
      pos.push(p[0], p[1], startZ, p[0], p[1], endZ);
      nor.push(...seg.n, ...seg.n);
      uv.push(0, v, repeatU, v);
    }
    // wound so the INNER surface is front-facing: no back-face pass needed,
    // and the normals above already point into the tunnel where the light is
    idx.push(base, base + 1, base + 3, base, base + 3, base + 2);
    s += len;
  }

  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

const ROD_COUNT = 13;

function Shell({
  litRef,
}: {
  litRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const geo = useMemo(buildShell, []);
  const tex = useMemo(makeShellTexture, []);

  const mat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        map: tex,
        // the paint carries a little of its own light. With one travelling
        // lamp the walls behind you would otherwise fall to pure black the
        // instant you pass them, and the tunnel would read as a short box
        emissiveMap: tex,
        emissive: new THREE.Color("#ffffff"),
        emissiveIntensity: 0,
        roughness: 0.96,
        metalness: 0,
      }),
    [tex]
  );

  useFrame(() => {
    mat.emissiveIntensity = 0.05 + litRef.current * 0.13;
  });

  return <mesh geometry={geo} material={mat} />;
}

function Road(): React.ReactElement {
  const { halfW, startZ, length } = TUNNEL;

  const tex = useMemo(() => {
    const t = makeAsphaltTexture();
    t.repeat.set((halfW * 2) / 6.4, length / 6.4);
    return t;
  }, [halfW, length]);

  // clear of every surface `Grounds` lays down — its mud sits at y 0.006 and
  // its kerbs at 0.014, and the mud square reaches almost 50 m in, so a road
  // laid at the shell's own y = 0 z-fights along most of the tunnel's length
  const Y = 0.03;

  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[0, Y, startZ - length / 2]}>
        <planeGeometry args={[halfW * 2, length]} />
        <meshStandardMaterial map={tex} color={VAULT.road} roughness={0.93} metalness={0.03} />
      </mesh>
      {/* the worn centre line — the strongest depth cue in the whole shot, and
          the thing that tells you which way the tunnel runs before you move */}
      <mesh rotation-x={-Math.PI / 2} position={[0, Y + 0.004, startZ - length / 2]}>
        <planeGeometry args={[0.13, length]} />
        <meshStandardMaterial color={"#b9ae86"} roughness={0.85} transparent opacity={0.5} />
      </mesh>
    </group>
  );
}

/**
 * The legible pieces, alternating walls down the run. Each is a quad standing
 * a couple of centimetres off the brick so the paint reads as being ON the
 * wall rather than being the wall.
 */
function Pieces(): React.ReactElement {
  const items = useMemo(() => {
    const r = rng(5150);
    const words = SIGN.tunnel;
    const usable = TUNNEL.length - 8; // nothing right at either mouth
    return words.map((word, i) => {
      const tex = makePieceTexture(word, 900 + i * 37);
      const img = tex.image as HTMLCanvasElement;
      const h = 1.0 + r() * 0.75;
      return {
        tex,
        w: (h * img.width) / img.height,
        h,
        side: i % 2 === 0 ? -1 : 1,
        z: TUNNEL.startZ - 5 - (i / (words.length - 1)) * usable,
        // kept inside a can's reach off the ground: the walls are 5 m and a
        // piece halfway up one would have needed scaffolding to put there
        y: 0.9 + r() * 1.5,
        tilt: (r() - 0.5) * 0.09,
      };
    });
  }, []);

  return (
    <group>
      {items.map((p, i) => (
        <mesh
          key={i}
          position={[p.side * (TUNNEL.halfW - 0.025), p.y, p.z]}
          rotation={[0, p.side * -Math.PI / 2, p.tilt]}
        >
          <planeGeometry args={[p.w, p.h]} />
          <meshStandardMaterial
            map={p.tex}
            emissiveMap={p.tex}
            emissive={new THREE.Color("#ffffff")}
            emissiveIntensity={0.16}
            transparent
            alphaTest={0.06}
            roughness={0.95}
            metalness={0}
          />
        </mesh>
      ))}
    </group>
  );
}

/**
 * The strip lights across the roof — the tunnel's only fixtures.
 *
 * The rods run ACROSS the tunnel rather than along it: a continuous line down
 * the middle gives you nothing to measure speed against, where a row of
 * battens flicking overhead is the whole reason a tunnel feels fast. Every
 * fourth one is dead and one flickers, because a run of thirteen identical
 * working tubes is the single most CG thing you could put on that ceiling.
 */
function Fixtures(): React.ReactElement {
  const { startZ, length, roofY, halfW } = TUNNEL;

  const litMat = useMemo(
    () => new THREE.MeshBasicMaterial({ color: VAULT.fixture, toneMapped: false }),
    []
  );
  const deadMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: VAULT.dead, roughness: 0.7 }),
    []
  );
  const flickerMat = useMemo(
    () => new THREE.MeshBasicMaterial({ color: VAULT.fixture, toneMapped: false }),
    []
  );
  const housingMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#131417", roughness: 0.85 }),
    []
  );

  const rodGeo = useMemo(
    () => new THREE.BoxGeometry(halfW * 2 - 0.5, 0.08, 0.15),
    [halfW]
  );
  const housingGeo = useMemo(
    () => new THREE.BoxGeometry(halfW * 2 - 0.42, 0.11, 0.23),
    [halfW]
  );

  const rods = useMemo(
    () =>
      Array.from({ length: ROD_COUNT }, (_, i) => ({
        z: startZ - 2.5 - (i / (ROD_COUNT - 1)) * (length - 6),
        state: i % 4 === 3 ? "dead" : i === 6 ? "flicker" : "lit",
      })),
    [startZ, length]
  );

  useFrame((state) => {
    // a failing tube doesn't blink on a timer, it stutters — two beats out of
    // phase multiplied together, then hard-clipped, gets close enough
    const t = state.clock.elapsedTime;
    const s = Math.sin(t * 21) * Math.sin(t * 6.3);
    flickerMat.color
      .set(VAULT.fixture)
      .multiplyScalar(s > 0.1 ? 1 : 0.06 + Math.max(0, s) * 2);
  });

  return (
    <group>
      {rods.map((rod, i) => (
        <group key={i} position={[0, roofY - 0.14, rod.z]}>
          <mesh
            geometry={rodGeo}
            material={
              rod.state === "dead"
                ? deadMat
                : rod.state === "flicker"
                  ? flickerMat
                  : litMat
            }
          />
          {/* the fitting the tube sits in — without it the bar floats, and a
              floating bar reads as a glowing prop rather than a light */}
          <mesh geometry={housingGeo} material={housingMat} position={[0, 0.1, 0]} />
        </group>
      ))}
    </group>
  );
}

/**
 * The single lamp that lights the whole tunnel, riding just ahead of and above
 * the camera. It fades up as you cross the threshold so it never spills onto
 * the arch, which is lit by its own two floods and would look wrong with a
 * third source in front of it.
 */
function TravellingLight({
  litRef,
}: {
  litRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const light = useRef<THREE.PointLight>(null);

  useFrame((state) => {
    const l = light.current;
    if (!l) return;
    const cam = state.camera;
    // 0 outside the tunnel → 1 once a few metres in
    const lit = THREE.MathUtils.clamp(
      (TUNNEL.startZ - cam.position.z) / 6,
      0,
      1
    );
    litRef.current = lit;
    l.intensity = lit * 34;
    l.position.set(cam.position.x * 0.4, 2.35, cam.position.z - 2.2);
  });

  return (
    <pointLight
      ref={light}
      color={VAULT.fixture}
      intensity={0}
      distance={22}
      decay={2}
    />
  );
}

export default function Tunnel(): React.ReactElement {
  // how lit the interior is, shared so the shell's self-illumination and the
  // travelling lamp come up together instead of drifting apart
  const litRef = useRef(0);

  return (
    <group>
      <TravellingLight litRef={litRef} />
      <Shell litRef={litRef} />
      <Road />
      <Pieces />
      <Fixtures />
    </group>
  );
}
