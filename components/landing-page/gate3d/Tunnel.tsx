"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { NIGHT, SIGN, TUNNEL, VAULT } from "./palette";
import {
  ensureTagFont,
  makeNameTagTexture,
  makePieceTexture,
  makeShellBump,
  makeShellTexture,
} from "./graffiti";
import {
  finish,
  makeTurfPatchTexture,
  makeTurfTexture,
  mk,
  rng,
} from "./textures";

/**
 * The graffiti tunnel you fly down after clicking through the arch: a
 * flat-roofed run painted wall to wall and strip-lit from the ceiling, cut
 * straight through on patchy turf. It opens onto the fest ground at `endZ`.
 * Its head height is the arch's own opening (see `TUNNEL` in palette) so the
 * roof carries straight on from the beam's underside, while the walls stand
 * wider than the boards' reveals and are picked up only once you are inside —
 * and its floor is the same turf as the field outside, worn through down the
 * middle and washed back to the ground's own mud at both openings, so nothing
 * underfoot changes abruptly at the mouth.
 *
 * Lighting is deliberately not one lamp per fixture — a run this long would
 * need dozens and this scene already spends its light budget on the arch's two
 * floods. Instead a pair of lamps ride along with the camera, one ahead and
 * one trailing, over a fill that only exists inside the tunnel. The rods
 * themselves are emissive geometry that glows without lighting anything, the
 * same trick the lamps out on the ground use.
 */

/**
 * True once Aerosoldier is actually available to canvas. Every texture in
 * here is lettered, and drawing before the OTF lands bakes Impact's shapes
 * in permanently — so the generators wait on this and re-run when it flips.
 */
function useTagFont(): boolean {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let alive = true;
    void ensureTagFont().then(() => alive && setReady(true));
    return () => {
      alive = false;
    };
  }, []);
  return ready;
}

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
  // 1, not a tile count: the shell texture spans the whole tunnel exactly
  // once, so no word ever repeats down the corridor
  const repeatU = 1;

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

// scaled with the tunnel's length, so the run keeps its ~4 m spacing rather
// than bunching up now that the tunnel is shorter
const ROD_COUNT = 9;

function Shell({
  litRef,
}: {
  litRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const geo = useMemo(buildShell, []);
  const fontReady = useTagFont();
  // regenerated once Aerosoldier lands, so the wall is never left lettered
  // in the fallback face
  const tex = useMemo(() => makeShellTexture(), [fontReady]);
  // the masonry's relief. Nothing on it is lettered, so unlike the colour it
  // has no reason to wait on the font or to be rebuilt when it lands
  const bump = useMemo(() => makeShellBump(), []);

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
        // What stops the brick reading as a second wall printed behind the
        // paint: the courses are in the LIGHTING now, so the travelling lamps
        // rake across them as they pass instead of sliding over a flat sheet.
        // Kept low — this is a shallow arris, and a bump map pushed until you
        // can see it is a bump map turns the wall to corrugation.
        bumpMap: bump,
        bumpScale: 0.55,
        roughness: 0.96,
        metalness: 0,
      }),
    [tex, bump]
  );

  useFrame(() => {
    // The self-lit term is a fraction of the map, so it moves with whatever the
    // walls are made of: cream stock wanted 0.12, bare brick at half the albedo
    // wanted 0.17 to hold the same exposure. They are now neither — a coat of
    // white over brick, roughly half of each — so this sits between the two.
    // The point it is protecting either way is that you can read the walls as
    // you go past them.
    mat.emissiveIntensity = 0.14 + litRef.current * 0.16;
  });

  return <mesh geometry={geo} material={mat} />;
}

/**
 * The trodden strip down the middle: soft-edged, so it reads as ground worn
 * bare rather than a lane painted on.
 *
 * Its own quad rather than baked into the turf, because the turf TILES — a
 * worn track that starts again every 3 m is a pattern, not a path. This one
 * stretches the tunnel's whole length in a single pull.
 *
 * It earns its keep more now than it did over mud: bare ground down the middle
 * of grass is the shape feet actually leave, and it is what stops the floor
 * reading as a lawn that nobody has ever walked on.
 */
function makeWornTrack(): THREE.CanvasTexture {
  const W = 256;
  const H = 4;
  const { c, ctx } = mk(W, H);
  const g = ctx.createLinearGradient(0, 0, W, 0);
  g.addColorStop(0, "rgba(24,18,12,0)");
  g.addColorStop(0.3, "rgba(24,18,12,0.16)");
  g.addColorStop(0.5, "rgba(24,18,12,0.34)");
  g.addColorStop(0.7, "rgba(24,18,12,0.16)");
  g.addColorStop(1, "rgba(24,18,12,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  return finish(c);
}

/**
 * The last few metres at either mouth, where the tunnel's turf gives way to the
 * packed mud of the fest ground.
 *
 * `Grounds` lays one big mud square that passes clean UNDER this tunnel and out
 * the far side, so turfing the floor puts a straight line across the ground at
 * both openings — and the far one is dead centre of the composition the whole
 * flight lands on. This is a plain wash of the mud's own tone, ramped from
 * opaque at the opening to nothing a few metres in, so the two surfaces trade
 * off gradually the way ground cover actually gives out under cover.
 *
 * Tone only, no detail: at the mouth this is either under the travelling lamp's
 * falloff or beyond it, and mud grain resolved at 40 m is grain nobody sees.
 */
function makeMouthFade(towardArch: boolean): THREE.CanvasTexture {
  const W = 4;
  const H = 128;
  const { c, ctx } = mk(W, H);
  // canvas row 0 is v = 1 (three flips on upload), and after the floor quad's
  // −90° X rotation v = 1 is the far end — so the opaque stop leads for the far
  // mouth and trails for the one at the arch
  const g = ctx.createLinearGradient(0, towardArch ? H : 0, 0, towardArch ? 0 : H);
  g.addColorStop(0, "rgba(43,33,26,1)");
  g.addColorStop(0.4, "rgba(43,33,26,0.74)");
  g.addColorStop(1, "rgba(43,33,26,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  return finish(c);
}

/** Metres of blend at each opening. */
const MOUTH_FADE = 3.5;
/** ~3 m of turf per tile — the same tile `Grounds` lays the field with. */
const TURF_TILE = 3.0;

/**
 * The floor: turf, worn through down the middle.
 *
 * Laid with the SAME `makeTurfTexture` the field outside is, at the same tile
 * scale `Grounds` uses, so the ground you are walking on doesn't change species
 * halfway down a tunnel. Its dead patches are their own non-repeating sheet for
 * the same reason the worn track is one — see `makeTurfPatchTexture`. No
 * asphalt and no centre line: nothing drives down here.
 */
// clear of every surface `Grounds` lays down — its mud sits at y 0.006 and its
// kerbs at 0.014, and its mud square reaches well past the tunnel's far end, so
// a floor laid at the shell's own y = 0 z-fights the whole way. Shared, because
// anything standing on this floor (the weeds below) has to stand on the same
// number or it hovers.
const FLOOR_Y = 0.03;

function Path(): React.ReactElement {
  const { halfW, startZ, endZ, length } = TUNNEL;

  const turf = useMemo(() => {
    const t = makeTurfTexture();
    t.repeat.set((halfW * 2) / TURF_TILE, length / TURF_TILE);
    return t;
  }, [halfW, length]);

  // 256 × 2048 over 4.6 × 38 m works out to ~55 px/m across and ~54 along, so
  // the blotches come out round rather than smeared down the corridor. Fewer
  // and smaller than the field's: this is sheltered ground under a roof, where
  // what kills grass is feet rather than drought.
  const patches = useMemo(
    () =>
      makeTurfPatchTexture({
        w: 256,
        h: 2048,
        count: 84,
        minR: 9,
        maxR: 78,
        seed: 3311,
        feather: 30,
      }),
    []
  );

  const track = useMemo(makeWornTrack, []);
  const fadeFar = useMemo(() => makeMouthFade(false), []);
  const fadeNear = useMemo(() => makeMouthFade(true), []);

  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[0, FLOOR_Y, startZ - length / 2]}>
        <planeGeometry args={[halfW * 2, length]} />
        <meshStandardMaterial map={turf} roughness={0.97} metalness={0} />
      </mesh>
      <mesh
        rotation-x={-Math.PI / 2}
        position={[0, FLOOR_Y + 0.002, startZ - length / 2]}
      >
        <planeGeometry args={[halfW * 2, length]} />
        <meshStandardMaterial
          map={patches}
          transparent
          depthWrite={false}
          roughness={0.97}
          metalness={0}
        />
      </mesh>
      <mesh
        rotation-x={-Math.PI / 2}
        position={[0, FLOOR_Y + 0.004, startZ - length / 2]}
      >
        <planeGeometry args={[halfW * 2, length]} />
        <meshStandardMaterial
          map={track}
          transparent
          depthWrite={false}
          roughness={0.9}
          metalness={0}
        />
      </mesh>

      {/* last, so both openings sit over everything else on the floor */}
      {(
        [
          [fadeFar, endZ + MOUTH_FADE / 2],
          [fadeNear, startZ - MOUTH_FADE / 2],
        ] as const
      ).map(([tex, z], i) => (
        <mesh
          key={i}
          rotation-x={-Math.PI / 2}
          position={[0, FLOOR_Y + 0.006, z]}
        >
          <planeGeometry args={[halfW * 2, MOUTH_FADE]} />
          <meshStandardMaterial
            map={tex}
            transparent
            depthWrite={false}
            roughness={0.97}
            metalness={0}
          />
        </mesh>
      ))}
    </group>
  );
}

/**
 * One clump of blades, fanning from a single root at the bottom of the frame.
 *
 * Drawn rather than fetched for the same reason every other surface in here is:
 * one more image to download for something that is 15 cm tall and mostly seen
 * at 7 m/s. The tips run dry and the roots stay dark, which is the only detail
 * that survives at this size — grass lit from above is a bright fringe over a
 * black base, and a flat green card reads as plastic.
 */
function makeTuftTexture(): THREE.CanvasTexture {
  const S = 128;
  const { c, ctx } = mk(S, S);
  const r = rng(2207);

  for (let i = 0; i < 26; i++) {
    // rooted along a narrow band at the bottom, not across the whole width —
    // blades that start at the edges of the card fan from nothing and read as
    // separate weeds sharing a sprite
    const x0 = S / 2 + (r() - 0.5) * S * 0.38;
    const len = S * (0.4 + r() * 0.52);
    const lean = (r() - 0.5) * 1.5;
    const tipX = x0 + lean * len * 0.6;
    const tipY = S - len;
    // the mid control point leans less than the tip, so a blade bows over
    // under its own weight instead of shearing off in a straight line
    const midX = x0 + lean * len * 0.2;
    const midY = S - len * 0.55;
    const w = 1.1 + r() * 1.9;

    const g = ctx.createLinearGradient(0, S, 0, tipY);
    g.addColorStop(0, NIGHT.grass);
    g.addColorStop(0.55, `rgb(${44 + r() * 16 | 0}, ${68 + r() * 20 | 0}, 40)`);
    // straw at the very ends: nothing growing out of packed mud under a roof
    // is green all the way up
    g.addColorStop(1, `rgb(${104 + r() * 34 | 0}, ${104 + r() * 26 | 0}, 58)`);

    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(x0 - w, S);
    ctx.quadraticCurveTo(midX - w * 0.45, midY, tipX, tipY);
    ctx.quadraticCurveTo(midX + w * 0.45, midY, x0 + w, S);
    ctx.closePath();
    ctx.fill();
  }

  return finish(c);
}

/**
 * A tuft's geometry: two quads crossing at a right angle, rooted on y = 0.
 *
 * The cross is what makes a flat sprite survive this shot. The camera runs
 * dead straight down −z, so a single card either faces it the whole way (and
 * never turns, which is worse) or is edge-on and vanishes. With two, one is
 * always presenting. Built by hand rather than merged from primitives to stay
 * with the rest of this file, and because the normals need overriding anyway.
 *
 * Every normal points straight UP, which is not what the surfaces face. That
 * is the point: lit honestly, a vertical card takes almost nothing from a lamp
 * that is above and ahead of it, and the weeds go black the moment they aren't
 * side-on to it. Facing them up hands them the same light the mud they grow out
 * of is getting, which is what the eye expects from grass.
 */
function buildTuft(): THREE.BufferGeometry {
  const pos: number[] = [];
  const nor: number[] = [];
  const uv: number[] = [];
  const idx: number[] = [];

  for (const [ax, az] of [
    [1, 0],
    [0, 1],
  ]) {
    const base = pos.length / 3;
    for (const y of [0, 1]) {
      pos.push(-0.5 * ax, y, -0.5 * az, 0.5 * ax, y, 0.5 * az);
      nor.push(0, 1, 0, 0, 1, 0);
      uv.push(0, y, 1, y);
    }
    idx.push(base, base + 1, base + 3, base, base + 3, base + 2);
  }

  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("normal", new THREE.Float32BufferAttribute(nor, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  return g;
}

/** Clumps of weeds down the run — the tufts are scattered around these. */
const WEED_CLUMPS = 36;

/**
 * The tufts standing proud of the turf — the growth that has escaped the feet.
 *
 * The floor's own grass is painted on and therefore perfectly flat, which is
 * fine everywhere the camera is moving but gives the ground no silhouette at
 * all where it meets the wall. These are what put a real edge there.
 *
 * Placed in clumps hugging the walls rather than scattered evenly, which is
 * both what happens and what sells it: the middle of this floor is a worn track
 * (see `makeWornTrack`) and nothing gets tall where the feet fall, so tufts
 * living anywhere but the edges would quietly contradict the wear already
 * painted on the ground. A few strays reach in toward the track, because a
 * hard-edged margin of long grass down both sides is a border, not a floor.
 *
 * One `instancedMesh` for the lot — ~190 tufts of two quads each is a couple of
 * hundred triangles in a single draw call, which is what lets there be enough
 * of them to read as ground cover rather than as props.
 */
function Weeds(): React.ReactElement {
  const geo = useMemo(buildTuft, []);
  const tex = useMemo(makeTuftTexture, []);
  const mat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        map: tex,
        // cut out, not blended: transparency here would need sorting against
        // 190 instances in one mesh, which instancing cannot do. Low threshold
        // so the antialiased edges of the blades survive their mipmaps at the
        // far end of the tunnel instead of eroding to nothing.
        alphaTest: 0.24,
        side: THREE.DoubleSide,
        roughness: 1,
        metalness: 0,
      }),
    [tex]
  );

  const tufts = useMemo(() => {
    const r = rng(6142);
    const { halfW, startZ, endZ } = TUNNEL;
    const out: { x: number; z: number; rot: number; w: number; h: number }[] = [];

    for (let i = 0; i < WEED_CLUMPS; i++) {
      const side = r() < 0.5 ? -1 : 1;
      // one clump in six pushes in toward the middle — the odd survivor in the
      // track, which is what keeps the edges from reading as a planted border
      const stray = r() < 0.17;
      const cx = side * halfW * (stray ? 0.2 + r() * 0.3 : 0.6 + r() * 0.34);
      const cz = THREE.MathUtils.lerp(startZ - 0.8, endZ + 0.8, r());
      const n = 3 + Math.floor(r() * 5);

      for (let j = 0; j < n; j++) {
        // small, and smaller in the track: this is the stuff that gets stepped
        // on. The width follows the height rather than being drawn on its own,
        // so no tuft ends up a wide flat smear of the sprite.
        const h = (stray ? 0.06 : 0.09) + r() * 0.14;
        out.push({
          x: THREE.MathUtils.clamp(
            cx + (r() - 0.5) * 0.75,
            -halfW + 0.05,
            halfW - 0.05
          ),
          z: cz + (r() - 0.5) * 0.95,
          rot: r() * Math.PI, // a quarter turn covers a cross; this is spare
          w: h * (0.85 + r() * 0.85),
          h,
        });
      }
    }
    return out;
  }, []);

  const ref = useRef<THREE.InstancedMesh>(null);
  useEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const m = new THREE.Matrix4();
    const q = new THREE.Quaternion();
    const up = new THREE.Vector3(0, 1, 0);
    const p = new THREE.Vector3();
    const s = new THREE.Vector3();
    tufts.forEach((t, i) => {
      q.setFromAxisAngle(up, t.rot);
      // sat on the mud, not sunk into it: the geometry's root IS y = 0, so the
      // floor's own height is the whole offset
      p.set(t.x, FLOOR_Y, t.z);
      s.set(t.w, t.h, t.w);
      mesh.setMatrixAt(i, m.compose(p, q, s));
    });
    mesh.instanceMatrix.needsUpdate = true;
    mesh.computeBoundingSphere();
  }, [tufts]);

  return (
    <instancedMesh
      ref={ref}
      args={[geo, mat, tufts.length]}
      // the bounds are computed from the instances above; until that runs the
      // default unit sphere at the origin would cull the whole run away
      frustumCulled={false}
    />
  );
}

/**
 * The legible pieces, alternating walls down the run. Each is a quad standing
 * a couple of centimetres off the brick so the paint reads as being ON the
 * wall rather than being the wall.
 */
function Pieces(): React.ReactElement {
  const fontReady = useTagFont();
  const items = useMemo(() => {
    const r = rng(5150);
    const acts = SIGN.lineup;
    const usable = TUNNEL.length - 9; // nothing right at either mouth
    // A piece is a quad standing ON the wall, so every edge of it has to be on
    // the wall too. These were sized and positioned independently, and a wide
    // name at a low y put the bottom of its quad through the floor — the paint
    // then carried on below the mud and read as a board stuck through the
    // ground rather than as something painted on brick.
    const FLOOR = 0.14; // clear of the floor plane at y = 0.03
    const CEIL = 4.6; // and of the roof at 5
    const ENDS = 0.4; // and of both mouths, so nothing hangs out into the night
    // widest a piece may be before it would reach its same-side neighbour —
    // every OTHER act shares a wall, so that is twice the spacing
    const maxW = (2 * usable) / Math.max(1, acts.length - 1) - 0.8;

    return acts.map((entry, i) => {
      const tex = makePieceTexture(entry, 900 + i * 37);
      const img = tex.image as HTMLCanvasElement;
      // big: these are the one thing on the wall that has to be legible from
      // a moving camera, and 2 m of wall is what buys that
      let h = 2.0 + r() * 0.4;
      let w = (h * img.width) / img.height;
      // a long name is set smaller rather than allowed to run into the act
      // before it — the lineup grows by a line a year, and the spacing with it
      if (w > maxW) {
        h *= maxW / w;
        w = maxW;
      }
      const tilt = (r() - 0.5) * 0.07;
      // the tilted quad's real footprint, which is what has to fit
      const c = Math.abs(Math.cos(tilt));
      const s = Math.abs(Math.sin(tilt));
      const ew = w * c + h * s;
      const eh = w * s + h * c;

      const clamp = (v: number, lo: number, hi: number) =>
        lo > hi ? (lo + hi) / 2 : Math.min(Math.max(v, lo), hi);

      return {
        tex,
        w,
        h,
        side: i % 2 === 0 ? -1 : 1,
        // oldest nearest the arch, this year at the mouth: walking in is
        // walking forward through the fest's own history
        z: clamp(
          TUNNEL.startZ - 5 - (i / (acts.length - 1)) * usable,
          TUNNEL.endZ + ew / 2 + ENDS,
          TUNNEL.startZ - ew / 2 - ENDS
        ),
        // kept inside a can's reach off the ground: the walls are 5 m and a
        // piece halfway up one would have needed scaffolding to put there
        y: clamp(1.1 + r() * 0.8, FLOOR + eh / 2, CEIL - eh / 2),
        tilt,
      };
    });
  }, [fontReady]);

  /**
   * The same names again, small and scattered — the difference between a lineup
   * poster and a wall people keep coming back to.
   *
   * Placed against the pieces rather than independently of them. Thrown at a
   * random z on a random wall, these landed across the lineup often enough to
   * be the first thing you noticed: a piece is up to 7 m wide and there are
   * three of them on the left-hand wall alone, so most of that side is already
   * spoken for, and a tag that lands on one is not layering, it is a collision.
   *
   * So each one is offered up to 80 spots and takes the first that is clear of
   * everything already on that wall. WHAT FITS is the answer — the 26 here is
   * an ambition, not a count, and the ones that find nowhere to go are dropped.
   * That is deliberate: with the lineup fixed and the wall a fixed length, the
   * only way to guarantee 26 is to let them overlap, which is the bug. Add a
   * sixth act and a few tags will quietly give up their space to it.
   */
  const tags = useMemo(() => {
    const r = rng(8801);
    const acts = SIGN.lineup;
    const usable = TUNNEL.length - 6;
    const gap = 0.24; // clear brick between any two, so they read as separate

    // Footprint of a tilted quad. Every one of these is rotated a little, and
    // at a tag's proportions that is not a rounding error — 0.18 rad across a
    // 1.5 m name adds two thirds again to its height, so boxes taken from the
    // untilted size would let pairs overlap that the test had just cleared.
    type Box = { side: number; z0: number; z1: number; y0: number; y1: number };
    const box = (side: number, z: number, y: number, w: number, h: number, tilt: number): Box => {
      const c = Math.abs(Math.cos(tilt));
      const s = Math.abs(Math.sin(tilt));
      const ew = w * c + h * s;
      const eh = w * s + h * c;
      return { side, z0: z - ew / 2, z1: z + ew / 2, y0: y - eh / 2, y1: y + eh / 2 };
    };

    // the pieces are already up, and they get first claim on the wall
    const taken: Box[] = items.map((p) => box(p.side, p.z, p.y, p.w, p.h, p.tilt));

    const out = [];
    for (let i = 0; i < 26; i++) {
      const entry = acts[i % acts.length];
      const tex = makeNameTagTexture(entry, 4200 + i * 53);
      const img = tex.image as HTMLCanvasElement;
      // smaller than they were: these have to live in the gaps between pieces,
      // and at the old size half of them had nowhere to be
      const h = 0.26 + r() * 0.16;
      const w = (h * img.width) / img.height;

      const tilt = (r() - 0.5) * 0.36;
      // a tag is tilted much harder than a piece, so its footprint is a good
      // deal taller than its art — same clamp, and it matters more here
      const c = Math.abs(Math.cos(tilt));
      const s = Math.abs(Math.sin(tilt));
      const ew = w * c + h * s;
      const eh = w * s + h * c;
      const zLo = TUNNEL.endZ + ew / 2 + 0.4;
      const zHi = TUNNEL.startZ - ew / 2 - 0.4;
      const yLo = 0.14 + eh / 2;
      const yHi = 4.6 - eh / 2;

      for (let attempt = 0; attempt < 80; attempt++) {
        const side = r() < 0.5 ? -1 : 1;
        const z = Math.min(Math.max(TUNNEL.startZ - 3 - r() * usable, zLo), zHi);
        const y = Math.min(Math.max(0.5 + r() * 2.6, yLo), Math.max(yLo, yHi));
        const b = box(side, z, y, w, h, tilt);
        const clash = taken.some(
          (t) =>
            t.side === side &&
            b.z0 - gap < t.z1 &&
            t.z0 - gap < b.z1 &&
            b.y0 - gap < t.y1 &&
            t.y0 - gap < b.y1
        );
        if (clash) continue;
        taken.push(b);
        out.push({ tex, w, h, side, z, y, tilt });
        break;
      }
    }
    return out;
  }, [fontReady, items]);

  /**
   * These write depth, and that is not optional.
   *
   * They were briefly switched to `depthWrite={false}` to stop coplanar decals
   * flickering against each other, which worked and cost far more than it was
   * worth: a decal that writes no depth cannot occlude another one, so down a
   * 38 m tunnel viewed almost edge-on — where a tag 30 m away and a piece 3 m
   * away land on the same pixels constantly — whichever came later in
   * `renderOrder` won regardless of distance. Far paint drew over near paint,
   * detached from any surface, and read as graffiti floating in the air in
   * front of the wall.
   *
   * The flicker it was fixing is gone at the source instead: nothing on a given
   * wall overlaps anything else on it any more (see the placement above), so
   * there are no coplanar pairs left to fight. Against the wall itself 25 mm is
   * tens of times the depth buffer's resolution at these distances.
   *
   * `renderOrder` stays as the tiebreak, and it is the right order physically:
   * the lineup goes up first and the scrawled tags go over it, which is how a
   * wall like this actually accumulates.
   */
  const paint = (
    p: { tex: THREE.CanvasTexture; w: number; h: number; side: number; z: number; y: number; tilt: number },
    key: string,
    lit: number,
    order: number
  ) => (
    <mesh
      key={key}
      position={[p.side * (TUNNEL.halfW - 0.025), p.y, p.z]}
      rotation={[0, (p.side * -Math.PI) / 2, p.tilt]}
      renderOrder={order}
    >
      <planeGeometry args={[p.w, p.h]} />
      <meshStandardMaterial
        map={p.tex}
        emissiveMap={p.tex}
        emissive={new THREE.Color("#ffffff")}
        emissiveIntensity={lit}
        transparent
        alphaTest={0.06}
        roughness={0.95}
        metalness={0}
      />
    </mesh>
  );

  return (
    <group>
      {items.map((p, i) => paint(p, `act-${i}`, 0.16, 1 + i))}
      {tags.map((p, i) => paint(p, `tag-${i}`, 0.1, 1 + items.length + i))}
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

  // Both are the tunnel's width less an inset, so the run stays centred and
  // keeps its margin at either end however wide the section is set. The inset
  // is the knob for how long the battens read: bigger leaves more dark ceiling
  // between the tube and the wall, which is what stops them looking like they
  // are wedged in wall to wall. The housing keeps its 0.08 lead over the tube
  // so the endcaps still show.
  const ROD_INSET = 1.9;
  const rodGeo = useMemo(
    () => new THREE.BoxGeometry(halfW * 2 - ROD_INSET, 0.08, 0.15),
    [halfW]
  );
  const housingGeo = useMemo(
    () => new THREE.BoxGeometry(halfW * 2 - ROD_INSET + 0.08, 0.11, 0.23),
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
 * The tunnel's light: a lamp riding just ahead of the camera, a second one
 * trailing it so the wall you have just passed doesn't snap to black, and a
 * fill that lifts the whole interior.
 *
 * All three ramp with `lit`, which is 0 until you are a few metres inside —
 * so none of this touches the arch, which is lit by its own two floods and
 * would look wrong with anything else in front of it. That ramp is also what
 * lets the fill be an `ambientLight` at all: ambient is global and would
 * normally flatten the whole scene, but at the gate its intensity is zero.
 */
function TravellingLight({
  litRef,
}: {
  litRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const ahead = useRef<THREE.PointLight>(null);
  const behind = useRef<THREE.PointLight>(null);
  const fill = useRef<THREE.AmbientLight>(null);

  useFrame((state) => {
    const cam = state.camera;
    // 0 outside the tunnel → 1 once a few metres in
    const lit = THREE.MathUtils.clamp((TUNNEL.startZ - cam.position.z) / 6, 0, 1);
    litRef.current = lit;

    // Cream paper is a ~0.87 albedo, so this room reaches white on very little
    // light and every source here was fighting for the same headroom: at
    // ambient 0.95 the walls were already at the clip point before either lamp
    // or the emissive pass was added, and the paint went with them. The budget
    // is now split so the sum peaks just under 1 beside the camera — ambient
    // carries the base exposure, the points do shape and travel on top.
    if (ahead.current) {
      ahead.current.intensity = lit * 34;
      ahead.current.position.set(cam.position.x * 0.4, 2.6, cam.position.z - 3.4);
    }
    if (behind.current) {
      behind.current.intensity = lit * 18;
      behind.current.position.set(cam.position.x * 0.4, 2.4, cam.position.z + 4.5);
    }
    if (fill.current) fill.current.intensity = lit * 0.55;
  });

  return (
    <>
      <pointLight ref={ahead} color={VAULT.fixture} intensity={0} distance={30} decay={2} />
      <pointLight ref={behind} color={VAULT.fixture} intensity={0} distance={24} decay={2} />
      <ambientLight ref={fill} color={"#fff1d8"} intensity={0} />
    </>
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
      <Path />
      <Weeds />
      <Pieces />
      <Fixtures />
    </group>
  );
}
