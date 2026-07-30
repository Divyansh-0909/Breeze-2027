"use client";
import React, {
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  EffectComposer,
  Bloom,
  Vignette,
  Noise,
  SMAA,
} from "@react-three/postprocessing";
import * as THREE from "three";

import { GATE, NIGHT, TUNNEL } from "./palette";
import Gate from "./Gate";
import Grounds from "./Grounds";
import Trees from "./Trees";
import Sky from "./Sky";
import Lights from "./Lights";
import Tunnel from "./Tunnel";
import EntryNav from "./EntryNav";

/**
 * The night entry gate — the site's loading screen and way in.
 *
 * The arch loads as a moonlit silhouette, then powers on (floods and strung
 * bulbs ramp up) as the scene becomes ready; the invitation fades in; a click
 * flies the camera through the opening, down the graffiti tunnel behind it,
 * and out to the mouth where the ground opens up. `onEnter` fires on arrival,
 * which is where the rest of the site's chrome docks in.
 */

type Phase = "loading" | "ready" | "entering" | "arrived";

/** Seconds from the click to standing at the tunnel's mouth. */
const TRAVEL_S = 5.4;
const BASE_FOV = 45;
/**
 * How far to push the scene DOWN the frame, in metres of look-at height.
 *
 * The one knob for vertical composition: the camera aims this much higher than
 * whatever it's framing, and everything slides down the viewport by the same
 * amount. Done as a look-at offset rather than by dropping the world, because
 * the world and the camera would have to move together — and then the camera
 * is no longer at eye height over the tunnel's floor, which is the one place
 * in the whole shot where that matters.
 */
const FRAME_DROP = 2.15;
/** Where the flight stops: just short of the mouth, so it still frames the view. */
const ARRIVE_Z = TUNNEL.endZ + 2.4;

// ---- the arrival pose, named because two things solve off it ----
// The rig flies to it; the menu is planted on the axis it ends up looking down.
// Left as loose numbers they would drift apart on the first retune and the menu
// would land off-centre for reasons nobody could find.
const ARRIVE_EYE_Y = 1.72;
const AIM_Y = 2.1; // eye level down the tunnel, before FRAME_DROP
const AIM_AHEAD = 34; // how far in front of the camera the look-at rides

/**
 * How far past the camera's resting point the menu physically stands, in
 * metres — the one knob for the whole arrival.
 *
 * Small on purpose, and the ceiling is not a matter of taste. The menu is a
 * fixed-pixel block, so pushing it further out makes it proportionally WIDER in
 * world units to hold the same size on arrival — and once it is wider than the
 * tunnel's 4.6 m opening, its outer edges cross the tunnel walls for most of
 * the way in. A DOM overlay has no way to be occluded by them, so it would sit
 * over the brick instead of behind it.
 *
 * 4.4 keeps the block inside the mouth's cone at every aspect the layout
 * produces, worst case being a short landscape window (the block is capped in
 * pixels, the world is measured in vertical fov, so a short viewport is where
 * it eats the most of the frame).
 */
const MENU_DIST = 4.4;

/**
 * Where the menu stands in the world: on the arrival camera's own view axis,
 * MENU_DIST ahead of where it comes to rest — so at the end of the flight it is
 * dead centre of frame at exactly its authored size, and every metre before
 * that it is the same object seen from further away.
 */
const MENU_ANCHOR = (() => {
  const eye = new THREE.Vector3(0, ARRIVE_EYE_Y, ARRIVE_Z);
  const aim = new THREE.Vector3(0, AIM_Y + FRAME_DROP, ARRIVE_Z - AIM_AHEAD);
  return eye.clone().add(aim.sub(eye).normalize().multiplyScalar(MENU_DIST));
})();

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

/** Ramps the shared power-on level, then reports ready exactly once. */
function Warmup({
  powerRef,
  duration,
  onReady,
}: {
  powerRef: React.MutableRefObject<number>;
  duration: number;
  onReady: () => void;
}): null {
  const done = useRef(false);
  useFrame((_, dt) => {
    if (done.current) return;
    powerRef.current = Math.min(1, powerRef.current + dt / duration);
    if (powerRef.current >= 1) {
      done.current = true;
      onReady();
    }
  });
  return null;
}

/**
 * The single source of truth for how the shot is framed: the distance that
 * fits the facade at a given aspect, rather than a hard-coded position — so a
 * phone in portrait pulls back instead of cropping the arch.
 *
 * The HTML overlay solves with this too, which is how the call-to-action can
 * size itself to the arch's actual opening: share the math, and the text can
 * never drift out of the gap when the framing is retuned.
 */
function solveFraming(
  aspect: number,
  fovDeg: number
): { dist: number; halfW: number; halfH: number } {
  const halfH = Math.tan((fovDeg * Math.PI) / 180 / 2);
  const halfW = halfH * aspect;
  // the stand IS the shot: it spans most of the frame at every aspect —
  // near-full width on portrait, and on wide screens the height solve brings
  // it in until the arch towers rather than sits in a landscape
  const fillW = THREE.MathUtils.clamp(
    THREE.MathUtils.mapLinear(aspect, 0.7, 1.4, 1.0, 0.9),
    0.9,
    1.0
  );
  const distW = GATE.halfW / fillW / halfW;
  const distH = GATE.totalH / 2 / 0.8 / halfH;
  return { dist: Math.max(distW, distH, 6), halfW, halfH };
}

/**
 * Projected width of the arch's opening, as a fraction of the viewport — what
 * the overlay clamps the call-to-action to so it reads as sitting inside the
 * gap between the boards.
 */
function openingFraction(aspect: number, fovDeg = 45): number {
  const { dist, halfW } = solveFraming(aspect, fovDeg);
  return GATE.openingW / (2 * dist * halfW);
}

/**
 * Drives the camera: holds the framed composition, then flies the whole run
 * from outside the arch to the tunnel's mouth in one unbroken move.
 *
 * Time-driven rather than the exponential chase the idle pose uses, because a
 * chase never actually lands — over 58 metres it spends the last second
 * crawling the final half-metre, which reads as the flight stalling. An
 * explicit eased progress arrives, and arrives when the overlay expects it to.
 */
function CameraRig({
  phase,
  motion: allowMotion,
  travelS,
  skipTravel,
  progressRef,
  onArrive,
}: {
  phase: Phase;
  motion: boolean;
  travelS: number;
  skipTravel: boolean;
  progressRef: React.MutableRefObject<number>;
  onArrive: () => void;
}): null {
  const size = useThree((s) => s.size);
  const target = useRef(new THREE.Vector3(0, 2.05, 0));
  const desired = useRef(new THREE.Vector3());
  const desiredTarget = useRef(new THREE.Vector3());
  // seconds since the click — or already spent, when the run is being skipped
  const flown = useRef(skipTravel ? 1e6 : 0);
  const landed = useRef(false);

  useFrame((state, dt) => {
    const cam = state.camera as THREE.PerspectiveCamera;
    const aspect = size.width / Math.max(1, size.height);
    // solved at the BASE fov, never at the camera's current one: the flight
    // widens the lens for speed, and feeding that back into the framing would
    // have the arch drifting away from the composition it was solved for
    const { dist } = solveFraming(aspect, BASE_FOV);

    if (phase === "entering" || phase === "arrived") flown.current += dt;
    const p = THREE.MathUtils.clamp(flown.current / travelS, 0, 1);
    progressRef.current = p;
    const e = p * p * (3 - 2 * p); // smoothstep: pushes off, and lands soft
    const rush = 4 * p * (1 - p); // 0 at both ends, 1 through the middle

    if (!landed.current && p >= 1) {
      landed.current = true;
      onArrive();
    }

    const px = allowMotion ? state.pointer.x : 0;
    const py = allowMotion ? state.pointer.y : 0;
    const t = allowMotion ? state.clock.elapsedTime : 0;
    const idle = 1 - e; // parallax and breathing belong to the held shot only

    const z = THREE.MathUtils.lerp(dist, ARRIVE_Z, e);
    const y = THREE.MathUtils.lerp(
      1.6 + Math.sin(t * 0.35) * 0.03 * idle,
      ARRIVE_EYE_Y,
      e
    );

    desired.current.set(px * 0.55 * idle, y + py * 0.32 * idle, z);
    desiredTarget.current.set(
      px * 0.22 * idle,
      // starts on the stand's vertical centre, then drops to eye level for the
      // run down the tunnel — plus FRAME_DROP throughout, which is what sits
      // the whole composition lower in the viewport
      THREE.MathUtils.lerp(3.2, AIM_Y, Math.min(1, e * 2.2)) + FRAME_DROP,
      // always well ahead of the camera, so the last of the move is already
      // looking out at the ground rather than swinging onto it on arrival
      z - AIM_AHEAD
    );

    // The chase gives the held shot its weight — the camera trails the pointer
    // rather than being nailed to it. But a chase never arrives, and over this
    // run it leaves the camera nearly two metres short at the moment progress
    // reads 1: the flight "lands" and then goes on creeping forward for another
    // second and a half. So the smoothing is dissolved as the move ends and the
    // camera is handed straight to its eased pose. Steep power on purpose —
    // through the whole middle of the run this is worth nothing and the lag is
    // untouched; it only exists to close out the last of the approach.
    const k = THREE.MathUtils.lerp(1 - Math.exp(-2.4 * dt), 1, Math.pow(e, 6));
    cam.position.lerp(desired.current, k);
    target.current.lerp(desiredTarget.current, k);

    if (allowMotion) {
      // hand-held shake and a wider lens through the middle of the run: the
      // tunnel is a straight corridor, and without them the speed does not
      // register at all once the walls stop being individually readable
      cam.position.x += Math.sin(flown.current * 7.3) * 0.05 * rush;
      cam.position.y += Math.sin(flown.current * 5.1) * 0.038 * rush;
      const fov = BASE_FOV + 12 * rush;
      if (Math.abs(cam.fov - fov) > 0.02) {
        cam.fov = fov;
        cam.updateProjectionMatrix();
      }
    }

    cam.lookAt(target.current);

    // the gate is fogged down hard so the field falls away behind it; the
    // ground past the tunnel is 100 m out and would never surface through
    // that, so the fog thins as the flight goes
    const fog = state.scene.fog as THREE.FogExp2 | null;
    if (fog) fog.density = THREE.MathUtils.lerp(0.03, 0.0072, e);
  });
  return null;
}

/**
 * Pins the arrival menu to `MENU_ANCHOR`, so it is a thing standing at the far
 * end of the tunnel that you fly up to — not a panel that switches on once the
 * camera stops.
 *
 * The menu stays DOM rather than becoming geometry: it has to be crisp type,
 * real `<Link>`s, tab order and hover states. So each frame the anchor is
 * projected and the block is moved and scaled to sit exactly where that point
 * lands. Same result as putting it in the scene, none of the cost.
 *
 * Written straight to `style` from inside the frame loop rather than through
 * React state — this changes every frame, and re-rendering three `<Link>`s at
 * 60 fps during the one moment the scene is working hardest is not a trade
 * worth making.
 */
function MenuAnchor({
  blockRef,
  shadeRef,
  progressRef,
}: {
  blockRef: React.RefObject<HTMLDivElement>;
  shadeRef: React.RefObject<HTMLDivElement>;
  progressRef: React.MutableRefObject<number>;
}): null {
  const size = useThree((s) => s.size);
  const ndc = useRef(new THREE.Vector3());
  const view = useRef(new THREE.Vector3());

  useFrame((state) => {
    const el = blockRef.current;
    if (!el) return;
    const cam = state.camera as THREE.PerspectiveCamera;
    // the rig moved the camera earlier this frame but nothing has rendered
    // yet, so its world matrix is still last frame's — project against a stale
    // one and the menu lags the walls it is supposed to be standing behind
    cam.updateMatrixWorld();

    // where the anchor lands on screen, as an offset from centre: the block is
    // already flex-centred, so at rest these are both 0 and it sits exactly
    // where it was authored
    ndc.current.copy(MENU_ANCHOR).project(cam);
    const dx = (ndc.current.x * size.width) / 2;
    const dy = (-ndc.current.y * size.height) / 2;

    // perspective, done honestly: apparent size goes as 1 / (depth · tan(fov/2)),
    // and the fov term matters — the flight widens the lens through the middle
    // of the run, and without it the menu would swell as the walls rushed past
    view.current.copy(MENU_ANCHOR).applyMatrix4(cam.matrixWorldInverse);
    const depth = Math.max(0.01, -view.current.z);
    const k =
      (MENU_DIST * Math.tan(THREE.MathUtils.degToRad(BASE_FOV) / 2)) /
      (depth * Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2));

    const p = progressRef.current;
    el.style.transform = `translate3d(${dx}px, ${dy}px, 0) scale(${k})`;
    // up almost immediately and long before the end. The menu has to be
    // established while it is still a distant smudge at the mouth — the entire
    // point is that you watch it come to you, and anything held back until the
    // walls stop rushing is the old pop-in with a longer fuse. It spends the
    // first half of the run under a tenth of its size, which is a sign read
    // from 70 metres, not a panel competing with the graffiti.
    el.style.opacity = String(THREE.MathUtils.smoothstep(p, 0.05, 0.5));

    // the well of shade the type sits in belongs to the resting shot alone: run
    // it any earlier and it reads as the tunnel dimming rather than the ground
    // beyond it being dark
    const shade = shadeRef.current;
    if (shade) shade.style.opacity = String(THREE.MathUtils.smoothstep(p, 0.62, 1));
  });

  return null;
}

/** Steps resolution down when the GPU can't keep up, cautiously back up. */
const DPR_LEVELS = [1.5, 1.25, 1.0, 0.8];
function AdaptiveDpr(): null {
  const setDpr = useThree((s) => s.setDpr);
  const a = useRef({ t: 0, n: 0, level: 0, streak: 0, need: 4 });
  useFrame((_, dt) => {
    const g = a.current;
    g.t += dt;
    g.n += 1;
    if (g.t < 1) return;
    const avg = g.t / g.n;
    g.t = 0;
    g.n = 0;
    const apply = () =>
      setDpr(Math.min(DPR_LEVELS[g.level], window.devicePixelRatio));
    if (avg > 1 / 48 && g.level < DPR_LEVELS.length - 1) {
      g.level += 1;
      g.streak = 0;
      g.need = Math.min(g.need * 2, 60);
      apply();
    } else if (avg < 1 / 57 && g.level > 0) {
      if (++g.streak >= g.need) {
        g.level -= 1;
        g.streak = 0;
        apply();
      }
    } else {
      g.streak = 0;
    }
  });
  return null;
}

export default function GateHero({
  onEnter,
}: {
  onEnter?: () => void;
}): React.ReactElement {
  const reduced = usePrefersReducedMotion();
  const motionOn = !reduced;

  // `/?arrived` skips straight to the end state: the camera is already at the
  // mouth and the menu already at full size. Read before the first render
  // rather than in an effect — the menu is now a thing in the world that grows
  // as you close on it, so a frame spent flying is a frame of it being small,
  // and the point of the shortcut is to see it landed. Safe to touch `window`:
  // this whole component is loaded `ssr: false`.
  const skipTravel = useRef(
    typeof window !== "undefined" &&
      new URLSearchParams(window.location.search).has("arrived")
  ).current;

  const powerRef = useRef(0);
  const [phase, setPhase] = useState<Phase>(skipTravel ? "arrived" : "loading");

  // the flight's progress, and the two overlay nodes that ride the world with
  // it — shared by ref so the frame loop can drive them without a re-render
  const progressRef = useRef(0);
  const menuBlockRef = useRef<HTMLDivElement>(null);
  const menuShadeRef = useRef<HTMLDivElement>(null);

  // width of the arch's opening on screen, measured from the same framing
  // solve the camera uses, so the CTA tracks the gap through any resize
  const rootRef = useRef<HTMLDivElement>(null);
  const [gapPx, setGapPx] = useState(0);

  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const measure = () => {
      const w = el.clientWidth;
      const h = el.clientHeight;
      if (!w || !h) return;
      setGapPx(Math.round(openingFraction(w / h) * w));
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const enter = useCallback(() => {
    if (phase !== "ready") return;
    setPhase("entering");
  }, [phase]);

  // fired by the rig itself when the flight actually lands, rather than by a
  // timer racing it — a slow first frame or a dropped tab would otherwise put
  // the menu on screen while the camera was still somewhere in the tunnel
  const arrive = useCallback(() => {
    setPhase("arrived");
    onEnter?.();
  }, [onEnter]);

  useEffect(() => {
    if (phase !== "ready") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        enter();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, enter]);

  return (
    <div
      ref={rootRef}
      className="absolute inset-0 select-none"
      data-phase={phase}
      role={phase === "ready" ? "button" : undefined}
      aria-label={phase === "ready" ? "Enter Breeze" : undefined}
      tabIndex={phase === "ready" ? 0 : -1}
      onClick={phase === "ready" ? enter : undefined}
      style={{ cursor: phase === "ready" ? "pointer" : "default" }}
    >
      <Canvas
        shadows
        dpr={[1, 1.5]}
        camera={{ fov: 45, near: 0.1, far: 220, position: [0, 1.6, 12] }}
        gl={{ antialias: false, powerPreference: "high-performance" }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping;
          gl.toneMappingExposure = 0.98;
        }}
      >
        <color attach="background" args={[NIGHT.sky]} />
        {/* denser than before: with the light pooled at the gate, the fog is
            what carries the environment down into darkness with distance */}
        <fogExp2 attach="fog" args={[NIGHT.fog, 0.03]} />
        <Suspense fallback={null}>
          <AdaptiveDpr />
          <Warmup
            powerRef={powerRef}
            duration={reduced ? 1.0 : 2.1}
            onReady={() => setPhase((p) => (p === "loading" ? "ready" : p))}
          />
          <Sky />
          <Lights powerRef={powerRef} />
          <Grounds />
          <Gate powerRef={powerRef} />
          <Trees />
          <Tunnel />
          {/* the ground past the mouth is deliberately empty for now — the
              landmark layer (stage, photobooth: ./Distant.tsx) is parked
              until the arrival menu is settled. Mounting <Distant /> here is
              all it takes to bring it back. */}
          <CameraRig
            phase={phase}
            motion={motionOn}
            travelS={reduced ? 1.4 : TRAVEL_S}
            skipTravel={skipTravel}
            progressRef={progressRef}
            onArrive={arrive}
          />
          {/* after the rig, so it projects against the pose set this frame */}
          <MenuAnchor
            blockRef={menuBlockRef}
            shadeRef={menuShadeRef}
            progressRef={progressRef}
          />
          <EffectComposer multisampling={0}>
            <SMAA />
            {/* threshold high enough that the lit boards themselves don't
                bloom — only the bulbs and the letter lights do */}
            <Bloom
              mipmapBlur
              intensity={0.42}
              luminanceThreshold={0.8}
              luminanceSmoothing={0.28}
              radius={0.7}
            />
            <Vignette eskil={false} offset={0.22} darkness={0.72} />
            <Noise opacity={0.028} premultiply />
          </EffectComposer>
        </Suspense>
      </Canvas>

      {/* ---- overlay ----
          Deliberately plain CSS rather than a motion library: this is the only
          affordance telling anyone how to get in, so it must never depend on a
          JS animation resolving. Tailwind's own keyframes can't silently leave
          it stuck at opacity 0. */}
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        {phase === "loading" && (
          <div className="flex animate-in fade-in items-center gap-3 text-[12px] font-semibold uppercase tracking-[0.35em] text-white/60 duration-500">
            <span
              aria-hidden
              className="block h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/20 motion-reduce:animate-none"
              style={{ borderTopColor: NIGHT.gold }}
            />
            Loading
          </div>
        )}

        {phase === "ready" && (
          // two elements on purpose: `animate-in` and `animate-pulse` both set
          // the CSS `animation` property, so on one element they cancel out and
          // the label never appears
          <div
            className="animate-in fade-in slide-in-from-bottom-3 duration-700"
            // clamped to the arch's opening, so the line sits within the gap
            // between the boards rather than spilling across them
            style={gapPx ? { width: gapPx } : undefined}
          >
            <p
              className="animate-pulse text-center font-semibold uppercase tracking-[0.3em] text-white motion-reduce:animate-none"
              style={{
                // sized off the gap as well: ~26 characters at 0.3em tracking
                // land on one line inside the opening at any viewport, with a
                // little headroom so the line never crowds the boards
                fontSize: gapPx
                  ? `${Math.max(8, Math.min(20, gapPx / 29))}px`
                  : undefined,
                textShadow: "0 2px 18px rgba(0,0,0,0.9)",
              }}
            >
              click anywhere to continue
            </p>
          </div>
        )}

        {/* mounted the moment the flight starts, not on landing: it is out
            there the whole way in, and the approach IS its entrance */}
        {(phase === "entering" || phase === "arrived") && (
          <EntryNav
            arrived={phase === "arrived"}
            blockRef={menuBlockRef}
            shadeRef={menuShadeRef}
          />
        )}
      </div>
    </div>
  );
}
