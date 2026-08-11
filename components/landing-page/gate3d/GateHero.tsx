"use client";
import React, {
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
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
import { warmStage } from "../stage3d/warmup";

/**
 * The night entry gate — the site's loading screen and way in.
 *
 * The arch loads as a moonlit silhouette, then powers on (floods and strung
 * bulbs ramp up) as the scene becomes ready; the invitation fades in; a click
 * flies the camera through the opening, down the graffiti tunnel behind it,
 * and out to the mouth where the ground opens up. `onEnter` fires on arrival,
 * which is where the rest of the site's chrome docks in.
 *
 * Picking a menu item doesn't cut: the camera walks on THROUGH the sign and
 * out of the mouth onto the fest ground, and the route only changes once that
 * has carried the frame to black. So the aftermovie's own walk-through-the-
 * crowd video opens on the step after the one you took here.
 */

type Phase = "loading" | "ready" | "entering" | "arrived" | "departing";

/**
 * Seconds from the click to standing at the tunnel's mouth.
 *
 * Long, and deliberately: the walls carry the name of every act that has
 * played, and a walk nobody can read them on is a walk that wasted them.
 * Over ~48 m this averages a shade under 7 m/s — walking pace for a camera —
 * so each piece holds the frame for about a second.
 */
const TRAVEL_S = 7.4;
const BASE_FOV = 45;

/**
 * Seconds from picking a menu item to the black the next route opens on.
 *
 * Short — this is a step off the mark, not a second tour. Long enough that the
 * sign visibly passes the camera rather than dissolving where it stands, short
 * enough that nobody who has decided where they're going is made to wait for a
 * camera move to finish.
 */
const DEPART_S = 1.55;

/**
 * Metres past the tunnel's mouth the departure carries you.
 *
 * Past `TUNNEL.endZ`, so the walls, the roof and the mouth all leave the frame
 * behind you: the move has to end OUTSIDE, on open ground, or the cut to black
 * happens while the tunnel is still wrapped around the shot and the whole thing
 * reads as a fade rather than as having walked out of it.
 */
const DEPART_PAST = 11;

/**
 * How hard the menu pushes in as you walk at it, as a fraction of its own size
 * added over the full walk.
 *
 * Read against the fade rather than the walk: the block is invisible by ~58% of
 * the move, and on the squared curve that is where it lands at about 1.6× — the
 * last of the distance closed, and nothing past the point where anyone can see
 * it. Turning this up is the knob for a more aggressive arrival; it cannot run
 * away, because unlike a true projection it is not dividing by a depth heading
 * for zero.
 */
const DEPART_ZOOM = 1.8;
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

// ---- the arrival pose ----
const ARRIVE_EYE_Y = 1.72;
const AIM_Y = 2.1; // eye level down the tunnel, before FRAME_DROP
const AIM_AHEAD = 34; // how far in front of the camera the look-at rides

/**
 * How much of the frame the tunnel's mouth takes at rest — the composition the
 * flight lands on, and the reason it stops where it does.
 *
 * The run ends INSIDE the tunnel, back far enough that the opening reads as a
 * frame: painted wall down both sides, roof overhead, road running out, and the
 * night beyond the mouth as a lit rectangle in the middle of it. Stopping at
 * the mouth instead — which is what `endZ + 2.4` did — puts the camera past
 * everything it spent the whole flight travelling through, and the arrival is a
 * menu on black with no evidence the tunnel was ever there.
 *
 * Solved per aspect rather than fixed, the same way `solveFraming` sizes the
 * arch: a phone's horizontal field is a third of a desktop's, so one hard-coded
 * distance either buries the mouth off both edges of a portrait screen or
 * strands the camera 20 m back on a wide one.
 */
const MOUTH_FILL_W = 0.78; // of frame width — the rest is painted wall
const MOUTH_FILL_H = 0.95; // of frame height — the rest is roof and road

/** Metres back from the mouth that the flight comes to rest, at this aspect. */
function solveArrival(aspect: number, fovDeg: number): number {
  const halfH = Math.tan((fovDeg * Math.PI) / 180 / 2);
  const byW = TUNNEL.halfW / (MOUTH_FILL_W * halfH * aspect);
  const byH = TUNNEL.roofY / 2 / (MOUTH_FILL_H * halfH);
  // never so far back that the last of the graffiti is behind you unread, and
  // never so close that the mouth stops being a frame
  return THREE.MathUtils.clamp(Math.max(byW, byH), 4.5, 22);
}

// ---- where the menu stands ----
/**
 * In the plane of the tunnel's mouth, on its centre line.
 *
 * Being coplanar with the opening is what makes the containment exact: the menu
 * and the mouth are then the same distance from the camera at every point of
 * the run, so a block narrower than 4.6 m is inside the opening at 70 m out and
 * at 7 m out and everywhere between — one comparison of two numbers, no solve,
 * no aspect to get wrong. It matters because a DOM overlay cannot be occluded
 * by the walls: the moment it is wider than the mouth it is painted over the
 * brick instead of framed by it.
 */
const MENU_ANCHOR = new THREE.Vector3(0, 2.3, TUNNEL.endZ);

/**
 * How wide the menu is IN THE WORLD, in metres — it is an object out there, so
 * this is its size, and how many pixels that comes to is the framing's business
 * rather than the layout's.
 *
 * Under the opening's 4.6 m by enough to leave daylight down both sides, so the
 * mouth reads as containing it rather than being plugged by it. This is also
 * the knob for how big the menu lands: it is measured against the mouth, so it
 * cannot quietly grow into the full-screen panel this replaced.
 */
const MENU_W = 3.5;

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
  departS,
  skipTravel,
  progressRef,
  departRef,
  onArrive,
  onDeparted,
}: {
  phase: Phase;
  motion: boolean;
  travelS: number;
  departS: number;
  skipTravel: boolean;
  progressRef: React.MutableRefObject<number>;
  departRef: React.MutableRefObject<number>;
  onArrive: () => void;
  onDeparted: () => void;
}): null {
  const size = useThree((s) => s.size);
  const target = useRef(new THREE.Vector3(0, 2.05, 0));
  const desired = useRef(new THREE.Vector3());
  const desiredTarget = useRef(new THREE.Vector3());
  // seconds since the click — or already spent, when the run is being skipped
  const flown = useRef(skipTravel ? 1e6 : 0);
  const landed = useRef(false);
  // seconds since a menu item was picked, and whether the walk out has ended
  const walked = useRef(0);
  const left = useRef(false);

  useFrame((state, dt) => {
    const cam = state.camera as THREE.PerspectiveCamera;
    const aspect = size.width / Math.max(1, size.height);
    // solved at the BASE fov, never at the camera's current one: the flight
    // widens the lens for speed, and feeding that back into the framing would
    // have the arch drifting away from the composition it was solved for
    const { dist } = solveFraming(aspect, BASE_FOV);
    const arriveZ = TUNNEL.endZ + solveArrival(aspect, BASE_FOV);

    if (phase === "entering" || phase === "arrived") flown.current += dt;
    const p = THREE.MathUtils.clamp(flown.current / travelS, 0, 1);
    progressRef.current = p;
    // Mostly linear, with just enough smoothstep blended in to push off and
    // land soft. Pure smoothstep peaks at 1.5× its own average, and that
    // midpoint surge is exactly where the lineup is painted — the walls blur
    // through the one stretch they most need to be read in. This holds the
    // peak to about 1.15×, so the pace through the middle is near constant.
    const s = p * p * (3 - 2 * p);
    const e = 0.32 * s + 0.68 * p;
    const rush = 4 * p * (1 - p); // 0 at both ends, 1 through the middle

    if (!landed.current && p >= 1) {
      landed.current = true;
      onArrive();
    }

    // The walk out, which only ever runs from the arrival pose. Accelerating
    // rather than eased at both ends: you push off from a standstill and keep
    // gaining, and the frame is black before there is anywhere to slow down
    // for — an ease-out here would be the camera politely parking itself half a
    // second after the visitor has already committed to leaving.
    if (phase === "departing") walked.current += dt;
    const dp = THREE.MathUtils.clamp(walked.current / departS, 0, 1);
    departRef.current = dp;
    const d = dp * dp;

    if (!left.current && phase === "departing" && dp >= 1) {
      left.current = true;
      onDeparted();
    }

    const px = allowMotion ? state.pointer.x : 0;
    const py = allowMotion ? state.pointer.y : 0;
    const t = allowMotion ? state.clock.elapsedTime : 0;
    const idle = 1 - e; // parallax and breathing belong to the held shot only

    // one line of Z for the whole scene: the flight in, then the walk out
    // stacked on its end. `d` is 0 until a menu item is picked, so the inner
    // lerp is untouched for the entire approach.
    const z = THREE.MathUtils.lerp(
      THREE.MathUtils.lerp(dist, arriveZ, e),
      TUNNEL.endZ - DEPART_PAST,
      d
    );
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
      // the departure is a walk, not a dolly: footfall in the vertical, the
      // sway of shifting weight in the horizontal, at roughly half the step
      // rate. Ramped over the first quarter-second so it starts from the still
      // arrival pose instead of snapping into gait on frame one.
      const gait = Math.min(1, dp * 6);
      cam.position.y += Math.sin(walked.current * 9.4) * 0.055 * gait;
      cam.position.x += Math.sin(walked.current * 4.7) * 0.05 * gait;
      // and the same wider lens the flight used for speed, brought back in as
      // the walk gathers pace
      const fov = BASE_FOV + 12 * rush + 13 * d;
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
  veilRef,
  progressRef,
  departRef,
}: {
  blockRef: React.RefObject<HTMLDivElement>;
  shadeRef: React.RefObject<HTMLDivElement>;
  veilRef: React.RefObject<HTMLDivElement>;
  progressRef: React.MutableRefObject<number>;
  departRef: React.MutableRefObject<number>;
}): null {
  const size = useThree((s) => s.size);
  const ndc = useRef(new THREE.Vector3());
  const view = useRef(new THREE.Vector3());
  // the last pose the approach wrote — i.e. where the block is standing at the
  // moment a link is picked, which is what the walk out pushes in on
  const pose = useRef({ dx: 0, dy: 0, k: 1 });

  // the block's own laid-out width, which is what the world size has to be
  // converted into. Measured on resize rather than in the frame loop: reading
  // offsetWidth forces layout, and doing that every frame during the flight is
  // the one thing guaranteed to cost more than the whole rest of this file.
  // (offsetWidth reports the pre-transform box, which is exactly what's wanted.)
  const blockW = useRef(1);
  useEffect(() => {
    const el = blockRef.current;
    if (el) blockW.current = el.offsetWidth || 1;
  }, [blockRef, size.width, size.height]);

  useFrame((state) => {
    const el = blockRef.current;
    if (!el) return;
    const cam = state.camera as THREE.PerspectiveCamera;
    // the rig moved the camera earlier this frame but nothing has rendered
    // yet, so its world matrix is still last frame's — project against a stale
    // one and the menu lags the walls it is supposed to be standing behind
    cam.updateMatrixWorld();

    const p = progressRef.current;
    const dp = departRef.current;

    // The full world pin belongs to the APPROACH, and only to it. Its endgame
    // is unusable here: the departure crosses `MENU_ANCHOR`'s own plane around
    // 60% of the way through, so an honest projection spends the fade racing
    // the block off the bottom of the frame at a dozen times its size. That was
    // the lurch. But freezing it outright is the other error — a block nailed
    // to the screen while the walls slide past it is the menu travelling WITH
    // the camera, not the camera closing on the menu.
    //
    // So: the centre is frozen at the arrival pose, and only the scale moves.
    // Growth alone is what the eye reads as approach — the sweep across the
    // frame was never carrying that, it was just the near plane arriving.
    if (dp === 0) {
      // where the anchor lands on screen, as an offset from centre: the block
      // is already flex-centred, so at rest these are both 0 and it sits
      // exactly where it was authored
      ndc.current.copy(MENU_ANCHOR).project(cam);
      const dx = (ndc.current.x * size.width) / 2;
      const dy = (-ndc.current.y * size.height) / 2;

      // How many pixels MENU_W metres comes to from here. The fov term is
      // load-bearing — the flight widens the lens through the middle of the
      // run, and without it the menu would swell as the walls rushed past.
      //
      // Note what this does NOT reference: the block's authored pixel width.
      // The menu is 3.5 m of the world and is drawn at whatever size that works
      // out to, so it is measured against the tunnel it stands in rather than
      // against the viewport. That is the whole reason it can't take the screen
      // over on arrival — the mouth is 4.6 m and it is 3.5, at any distance, on
      // any display.
      view.current.copy(MENU_ANCHOR).applyMatrix4(cam.matrixWorldInverse);
      const depth = Math.max(0.01, -view.current.z);
      const mPerPx =
        (2 * depth * Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2)) /
        size.height;
      const k = MENU_W / mPerPx / blockW.current;

      // kept so the walk out has an arrival pose to grow from — on the frame a
      // link is picked this is already exactly where the block stands
      pose.current.dx = dx;
      pose.current.dy = dy;
      pose.current.k = k;

      el.style.transform = `translate3d(${dx}px, ${dy}px, 0) scale(${k})`;
    } else {
      // On the camera's own accelerating curve rather than a linear ramp, so
      // the push-in starts from nothing and gathers exactly as the walk does —
      // the sign barely stirs on the first few frames because the camera has
      // barely left the mark, then comes on as it picks up.
      const q = pose.current;
      el.style.transform = `translate3d(${q.dx}px, ${q.dy}px, 0) scale(${
        q.k * (1 + DEPART_ZOOM * dp * dp)
      })`;
    }
    // up almost immediately and long before the end. The menu has to be
    // established while it is still a distant smudge at the mouth — the entire
    // point is that you watch it come to you, and anything held back until the
    // walls stop rushing is the old pop-in with a longer fuse. It spends the
    // first half of the run under a tenth of its size, which is a sign read
    // from 70 metres, not a panel competing with the graffiti.
    //
    // Going the other way it is a plain fade, held off the click by about a
    // third of a second. The pause is the acknowledgement: leave on frame one
    // and the menu appears to vanish from under the cursor, which reads as a
    // mis-click rather than as a choice being taken. It stays lit long enough
    // for the walk to visibly start under it, then goes.
    const stand = 1 - THREE.MathUtils.smoothstep(dp, 0.2, 0.58);
    el.style.opacity = String(THREE.MathUtils.smoothstep(p, 0.05, 0.5) * stand);

    // the well of shade the type sits in belongs to the resting shot alone: run
    // it any earlier and it reads as the tunnel dimming rather than the ground
    // beyond it being dark. It leaves with the type, and a touch slower — it is
    // the ground out there, not part of the sign.
    const shade = shadeRef.current;
    if (shade) {
      shade.style.opacity = String(
        THREE.MathUtils.smoothstep(p, 0.62, 1) * (1 - THREE.MathUtils.smoothstep(dp, 0.1, 0.85))
      );
    }

    // Black, on the back half of the walk — the hand-off to whatever route was
    // picked. Late on purpose: the first half is spent watching the mouth come
    // at you, and darkening from the moment of the click would throw that away
    // to save no time at all.
    const veil = veilRef.current;
    if (veil) veil.style.opacity = String(THREE.MathUtils.smoothstep(dp, 0.52, 1));
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
  const router = useRouter();

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

  // the walk out, driven the same way: progress by ref, and the black it ends
  // on written straight to a node rather than transitioned by CSS, so it can
  // never finish early or late relative to the camera it is covering
  const departRef = useRef(0);
  const veilRef = useRef<HTMLDivElement>(null);
  const destination = useRef<string | null>(null);

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

  /**
   * A menu item was picked: walk out first, change route after.
   *
   * The fetching is started here rather than on arrival at the far end, so the
   * ~1.5 s of camera move is also the route's head start. For the aftermovie
   * that matters most — its walk-through-the-crowd video and the stage chunk
   * behind it are the heaviest things on the site, and this is the moment they
   * stop being speculative.
   */
  const depart = useCallback(
    (href: string) => {
      if (phase !== "arrived") return;
      destination.current = href;
      router.prefetch(href);
      if (href.startsWith("/aftermovie")) warmStage();
      setPhase("departing");
    },
    [phase, router]
  );

  // fired by the rig on the walk's last frame, by which point the veil is
  // opaque — so the route swap happens behind black rather than cutting
  const departed = useCallback(() => {
    if (destination.current) router.push(destination.current);
  }, [router]);

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
            departS={reduced ? 0.5 : DEPART_S}
            skipTravel={skipTravel}
            progressRef={progressRef}
            departRef={departRef}
            onArrive={arrive}
            onDeparted={departed}
          />
          {/* after the rig, so it projects against the pose set this frame */}
          <MenuAnchor
            blockRef={menuBlockRef}
            shadeRef={menuShadeRef}
            veilRef={veilRef}
            progressRef={progressRef}
            departRef={departRef}
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
        {(phase === "entering" ||
          phase === "arrived" ||
          phase === "departing") && (
          <EntryNav
            // still "arrived" through the walk out: the block keeps its place
            // in the world and MenuAnchor keeps fading it. Flipping this back
            // would hand it to EntryNav's own CSS mid-move and the two would
            // fight over the same opacity.
            arrived={phase === "arrived" || phase === "departing"}
            departing={phase === "departing"}
            onDepart={depart}
            blockRef={menuBlockRef}
            shadeRef={menuShadeRef}
          />
        )}
      </div>

      {/* The black the next route opens on — above the canvas AND above the
          overlay, since it has to cover the menu it just walked through.
          Opacity is written per frame by MenuAnchor; the seeded 0 is only so
          it can't flash before that first write. #04050a rather than #000 to
          match what /aftermovie's travel overlay paints, so the hand-off
          between two pages is one continuous colour. */}
      <div
        ref={veilRef}
        aria-hidden
        className="pointer-events-none absolute inset-0 z-30"
        style={{ opacity: 0, backgroundColor: "#04050a", willChange: "opacity" }}
      />
    </div>
  );
}
