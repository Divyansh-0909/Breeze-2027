"use client";
import React, { useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { NIGHT } from "./palette";
import { makeLeafClusterTexture, rng } from "./textures";

/**
 * The leafy canopy that frames the reference shot — big trees overhanging the
 * top corners, more behind the arch, and a treeline fading into the fog.
 *
 * Canopies are alpha-cut leaf clumps drawn as instanced quads, several hundred
 * per grove. At night these read as dense foliage silhouettes catching a
 * little moonlight, which is exactly what the photo shows; cones or spheres
 * would read as toys.
 */

type TreeDef = {
  pos: [number, number, number];
  h: number; // trunk height
  r: number; // canopy radius
  lean: number;
  seed: number;
};

// Placed to reproduce the reference framing: heavy overhang top-left and
// top-right, a canopy mass directly above the arch, and depth behind it.
// The first two stand immediately beside the boards — on the mud just behind
// the gate line, never on the paved ring. Their canopies are wide enough to
// reach forward across the structure, so leaves drape over the top bar exactly
// as in the reference photos. Everything else keeps to the edges of the
// ground: its middle stays open (the camp hub lands there later), and no
// trunk sits on the near band or the side strips.
// Every trunk stands on the mud just INSIDE the ring — a planted line along
// the walkways' inner edge, the way campus paths are treed. Positions are
// points on each band's inner-edge offset (≈4.3 m from the centreline, ~1 m
// past the paving) at staggered distances down the two edges; the first pair
// sits just inside the corner arc, flanking the entry corridor, and their
// boughs are what reach forward over the gate's top bar. Nothing stands
// outside the ring, and the middle of the ground stays open for the camp.
const TREES: TreeDef[] = [
  // stood off the arch far enough to clear the tunnel behind it: its walls are
  // at x = ±2.3 and these canopies carry 3.5 m of reach, so any closer in and
  // their leaves grow through the tunnel's ceiling and hang there, indoors
  { pos: [-6.6, 0, -3.8], h: 7.4, r: 3.5, lean: 0.12, seed: 11 },
  { pos: [6.8, 0, -5.2], h: 7.6, r: 3.5, lean: -0.1, seed: 23 },
  // outside the ring, flanking the corner left and right of the stand — the
  // gate should sit nested in growth, not alone on a plain
  { pos: [-10.5, 0, 2.0], h: 6.8, r: 3.4, lean: 0.07, seed: 103 },
  { pos: [11.0, 0, 2.3], h: 7.0, r: 3.4, lean: -0.06, seed: 107 },
  { pos: [-13.5, 0, -1.5], h: 5.6, r: 3.0, lean: 0.05, seed: 109 },
  { pos: [13.8, 0, -1.8], h: 5.8, r: 3.0, lean: -0.04, seed: 113 },
  { pos: [-7.6, 0, -8.1], h: 5.4, r: 3.2, lean: 0.08, seed: 53 },
  { pos: [9.0, 0, -9.5], h: 5.6, r: 3.3, lean: -0.05, seed: 47 },
  { pos: [-11.8, 0, -12.3], h: 5.8, r: 3.2, lean: 0.05, seed: 31 },
  { pos: [13.9, 0, -14.4], h: 5.2, r: 3.0, lean: -0.07, seed: 67 },
  { pos: [-16.0, 0, -16.5], h: 4.6, r: 2.8, lean: 0, seed: 71 },
  { pos: [18.2, 0, -18.7], h: 4.6, r: 3.1, lean: 0, seed: 83 },
  { pos: [-20.3, 0, -20.8], h: 4.4, r: 2.6, lean: 0, seed: 97 },
];

/**
 * Foliage with no trunk of its own: boughs from the off-frame trees reaching
 * in over the camera. The reference is framed through overhanging leaves, and
 * without these the top of the shot is just empty sky.
 */
/**
 * A dense hedge line along the walkways' inner edge, sharing the ground with
 * the trunks — trunkless domes of the same instanced leaf clumps, packed
 * close enough (~2 m spacing, jittered) to read as continuous planting rather
 * than dotted shrubs. Generated along the same inner-edge offset the trees
 * use (band centreline + ~5.5 m), starting past the entry corridor's mouth.
 */
const BUSHES: { pos: [number, number, number]; r: number; seed: number }[] = (() => {
  const out: { pos: [number, number, number]; r: number; seed: number }[] = [];
  const r = rng(707);
  const CZ = 7.03; // ring corner z (matches Grounds)
  for (const side of [-1, 1]) {
    for (let t = 11.5; t <= 36; t += 1.8 + r() * 1.2) {
      const s = 5.2 + r() * 1.1; // inner-edge offset, jittered off the kerb
      const x = side * 0.707 * (t - s);
      const z = CZ - 0.707 * (t + s);
      // NEVER in the walking line: the corridor through the gate runs down
      // the bisector (|x| ≲ 3.4 until past the tents) — small t−s lands
      // exactly there, which is why the line starts at t = 11.5 and anything
      // jittering back into the mouth is skipped outright
      if (Math.abs(x) < 3.4 && z > -11) continue;
      out.push({
        pos: [x, 0, z],
        r: 0.9 + r() * 0.7,
        seed: 401 + out.length * 7,
      });
    }
  }
  return out;
})();

/**
 * Boughs sitting in front of the beam (z ≈ 2–4.5, around beam height), so they
 * hang down onto the top bar rather than clearing it. The ends of the beam are
 * meant to be partly veiled — that is what the photos show.
 *
 * The one exception is the centre: that bough is held high and far forward so
 * `V70 · V70 Elite` stays legible under it. Leaves obscuring the ends reads as
 * a real tree; leaves across the middle of the headline just reads as broken.
 */
const OVERHANG: { pos: [number, number, number]; r: number; n: number; seed: number }[] = [
  // over the beam (top at y ≈ 6.45): low enough to lie ON its top edge, so
  // leaves visibly rest on and spill over the board — heavier toward the
  // ends, thinner toward the middle so the headline stays readable
  { pos: [-3.54, 6.51, 2.2], r: 1.5, n: 56, seed: 301 },
  { pos: [-2.0, 6.86, 2.9], r: 1.2, n: 38, seed: 307 },
  { pos: [3.66, 6.56, 2.4], r: 1.5, n: 54, seed: 311 },
  { pos: [2.24, 6.96, 3.0], r: 1.2, n: 38, seed: 313 },
  // the beam's corners (ends at x ≈ ±4.27), buried in foliage like the photos
  { pos: [-4.72, 6.16, 2.6], r: 1.6, n: 56, seed: 331 },
  { pos: [4.84, 6.26, 2.8], r: 1.6, n: 54, seed: 337 },
  // past the facade, free to hang much lower
  { pos: [-6.96, 5.86, 3.0], r: 1.9, n: 54, seed: 319 },
  { pos: [7.32, 6.16, 3.6], r: 1.8, n: 50, seed: 323 },
  { pos: [0.24, 7.76, 4.6], r: 1.5, n: 34, seed: 317 },
];

/** Tapered trunk with a couple of forks — dark, barely lit, pure silhouette. */
function Trunk({ def }: { def: TreeDef }): React.ReactElement {
  const mat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: NIGHT.bark, roughness: 0.95 }),
    []
  );
  const forks = useMemo(() => {
    const r = rng(def.seed + 500);
    return [0, 1, 2].map((i) => ({
      a: (i / 3) * Math.PI * 2 + r(),
      y: def.h * (0.55 + r() * 0.25),
      len: def.h * (0.3 + r() * 0.2),
      tilt: 0.5 + r() * 0.4,
    }));
  }, [def]);

  return (
    <group position={def.pos} rotation-z={def.lean}>
      <mesh position={[0, def.h / 2, 0]} material={mat} castShadow>
        <cylinderGeometry args={[def.h * 0.045, def.h * 0.1, def.h, 7]} />
      </mesh>
      {forks.map((f, i) => (
        <mesh
          key={i}
          position={[
            Math.cos(f.a) * f.len * 0.35,
            f.y + f.len * 0.3,
            Math.sin(f.a) * f.len * 0.35,
          ]}
          rotation={[Math.sin(f.a) * f.tilt, 0, -Math.cos(f.a) * f.tilt]}
          material={mat}
        >
          <cylinderGeometry args={[def.h * 0.018, def.h * 0.04, f.len, 6]} />
        </mesh>
      ))}
    </group>
  );
}

export default function Trees(): React.ReactElement {
  const leafTex = useMemo(() => makeLeafClusterTexture(), []);

  const leafMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        map: leafTex,
        color: NIGHT.leaf,
        alphaTest: 0.42,
        side: THREE.DoubleSide,
        roughness: 0.95,
        metalness: 0,
      }),
    [leafTex]
  );

  const leafGeo = useMemo(() => new THREE.PlaneGeometry(1, 1), []);

  // one instance list for every canopy in the scene
  const instances = useMemo(() => {
    const out: {
      p: THREE.Vector3;
      rot: THREE.Euler;
      s: number;
    }[] = [];
    for (const t of TREES) {
      const r = rng(t.seed);
      const cy = t.h + t.r * 0.42;
      const perTree = t.pos[2] > -12 ? 132 : 74; // cheaper for distant trees
      // a handful of sub-blobs give the canopy a lumpy, non-spherical mass
      const blobs = 5;
      const centres = Array.from({ length: blobs }, () => {
        const a = r() * Math.PI * 2;
        const rad = r() * t.r * 0.5;
        return new THREE.Vector3(
          t.pos[0] + Math.cos(a) * rad,
          cy + (r() - 0.4) * t.r * 0.55,
          t.pos[2] + Math.sin(a) * rad
        );
      });
      for (let i = 0; i < perTree; i++) {
        const c = centres[i % blobs];
        // pow() biases toward the shell so the interior isn't wastefully dense
        const rad = Math.pow(r(), 0.55) * t.r * 0.72;
        const a = r() * Math.PI * 2;
        const b = Math.acos(2 * r() - 1);
        out.push({
          p: new THREE.Vector3(
            c.x + Math.sin(b) * Math.cos(a) * rad,
            c.y + Math.cos(b) * rad * 0.72,
            c.z + Math.sin(b) * Math.sin(a) * rad
          ),
          rot: new THREE.Euler(r() * Math.PI, r() * Math.PI, r() * Math.PI),
          s: t.r * (0.34 + r() * 0.3),
        });
      }
    }

    // bushes: trunkless domes — clumps biased downward so they sit fat and
    // low against the ground instead of floating like tiny canopies
    for (const b of BUSHES) {
      const r = rng(b.seed);
      const n = Math.round(20 + b.r * 16); // bigger bushes get fuller
      for (let i = 0; i < n; i++) {
        const rad = Math.pow(r(), 0.55) * b.r;
        const a = r() * Math.PI * 2;
        out.push({
          p: new THREE.Vector3(
            b.pos[0] + Math.cos(a) * rad,
            // shoulder-height hedge: clumps reach ~2× the bush radius up,
            // squared bias keeping the mass low so it still reads planted
            0.25 + Math.pow(r(), 1.6) * b.r * 2.0,
            b.pos[2] + Math.sin(a) * rad
          ),
          rot: new THREE.Euler(r() * Math.PI, r() * Math.PI, r() * Math.PI),
          s: b.r * (0.5 + r() * 0.35),
        });
      }
    }

    // boughs hanging into frame from above
    for (const o of OVERHANG) {
      const r = rng(o.seed);
      for (let i = 0; i < o.n; i++) {
        const rad = Math.pow(r(), 0.5) * o.r;
        const a = r() * Math.PI * 2;
        const b = Math.acos(2 * r() - 1);
        out.push({
          p: new THREE.Vector3(
            o.pos[0] + Math.sin(b) * Math.cos(a) * rad,
            o.pos[1] + Math.cos(b) * rad * 0.62,
            o.pos[2] + Math.sin(b) * Math.sin(a) * rad
          ),
          rot: new THREE.Euler(r() * Math.PI, r() * Math.PI, r() * Math.PI),
          s: o.r * (0.4 + r() * 0.34),
        });
      }
    }
    return out;
  }, []);

  const ref = useRef<THREE.InstancedMesh>(null);

  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const o = new THREE.Object3D();
    instances.forEach((inst, i) => {
      o.position.copy(inst.p);
      o.rotation.copy(inst.rot);
      o.scale.setScalar(inst.s);
      o.updateMatrix();
      mesh.setMatrixAt(i, o.matrix);
    });
    mesh.instanceMatrix.needsUpdate = true;
    mesh.computeBoundingSphere();
  }, [instances]);

  return (
    <group>
      {TREES.map((t, i) => (
        <Trunk key={i} def={t} />
      ))}
      <instancedMesh
        ref={ref}
        args={[leafGeo, leafMat, instances.length]}
        frustumCulled={false}
        castShadow
      />
    </group>
  );
}
