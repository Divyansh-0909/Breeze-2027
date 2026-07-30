"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import * as THREE from "three";
import Stage from "../stage3d/Stage";
import Trusses from "../stage3d/Trusses";
import Speakers from "../stage3d/Speakers";
import LEDScreens from "../stage3d/LEDScreens";
import StageLights from "../stage3d/Lights";
import { NIGHT } from "./palette";
import { finish, mk } from "./textures";

/**
 * What stands out on the ground once the tunnel opens up: the landmarks you
 * can see from the mouth but haven't reached yet.
 *
 * The menu drives this view. Hovering a destination features its landmark out
 * on the ground — the stage runs a ten-second cut of the aftermovie, Team
 * swaps the stage for the photobooth — so the list on the left and the world
 * on the right are the same set of places, seen two ways.
 *
 * To add a landmark, append to `LANDMARKS`. Give it a `href` once its page
 * exists, and a `when` if it should only stand in the view while its menu
 * entry is hovered.
 */

/** Which menu entry the visitor is hovering, or null for the resting view. */
export type MenuFocus = "aftermovie" | "team" | null;

const noop = () => {};

/** Local copy so this file doesn't have to import from `GateHero`, which
 *  imports this one. */
function useReducedMotion(): boolean {
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

export type Landmark = {
  id: string;
  /** Shown in the hub, and read out as the accessible name once linked. */
  label: string;
  /** `null` while the destination doesn't exist yet — scenery, not a link. */
  href: string | null;
  position: [number, number, number];
  /** Yaw, so a landmark off to one side still faces back toward the mouth. */
  rotationY?: number;
  scale?: number;
  /** When this landmark stands in the view. Omitted = always. */
  when?: (focus: MenuFocus) => boolean;
  Render: React.ComponentType<{ live: boolean; focus: MenuFocus }>;
};

/**
 * The main stage, exactly as the concert page builds it — deck, trusses,
 * speakers, LED wall and the full lighting rig, so it lights itself in its
 * own colours.
 *
 * Hovering the menu's Aftermovie entry runs a ten-second muted cut on the
 * wall. It's a dedicated preview file, not the real 87 MB movie: the clip is
 * warmed (`preload`) the moment the visitor commits to entering, so the wall
 * can light the instant the pointer lands rather than after a fetch.
 *
 * One knock-on to know about: the rig opens with `ambientLight 0.055`, and
 * ambient is global — it lifts the gate and the tunnel by the same 5.5%.
 * That's the price of the real rig rather than a copy; if the entry scene
 * ever looks washed out, that line in `stage3d/Lights.tsx` is the cause.
 */
function DistantStage({
  live,
  focus,
}: {
  live: boolean;
  focus: MenuFocus;
}): React.ReactElement {
  const motion = !useReducedMotion();
  const preview = focus === "aftermovie";

  const [videoTexture, setVideoTexture] = useState<THREE.VideoTexture | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // built and warmed at commit-to-enter; playback belongs to the hover
  useEffect(() => {
    if (!live) return;
    let alive = true;

    const video = document.createElement("video");
    // silent, and not negotiably: browsers refuse to autoplay with sound, and
    // a stage across the field has no business making noise on a landing page
    video.muted = true;
    video.defaultMuted = true;
    video.loop = true;
    video.playsInline = true;
    video.preload = "auto";
    video.src = "/aftermovie-preview.mp4";
    video.load();

    const tex = new THREE.VideoTexture(video);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearFilter;
    videoRef.current = video;

    // hand the wall its texture only once frames are genuinely arriving —
    // bound any earlier and it cross-fades its idle content to a black
    // rectangle while the buffer fills
    const onPlaying = () => {
      if (alive) setVideoTexture(tex);
    };
    video.addEventListener("playing", onPlaying);

    return () => {
      alive = false;
      video.removeEventListener("playing", onPlaying);
      setVideoTexture(null);
      videoRef.current = null;
      video.pause();
      video.removeAttribute("src");
      video.load(); // aborts an in-flight download as well as playback
      // dispose only once the wall's fade-out has finished sampling it
      window.setTimeout(() => tex.dispose(), 600);
    };
  }, [live]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (preview) {
      // from the top on every hover — a preview that resumes mid-scene reads
      // as broken, not as continuous
      video.currentTime = 0;
      void video.play().catch(() => {
        /* blocked or missing — the wall keeps its own idle content, which is
           a complete picture, so there is nothing to fall back to */
      });
    } else {
      video.pause();
      // wall cross-fades back to its idle shader
      setVideoTexture(null);
    }
  }, [preview]);

  return (
    <group>
      <Stage />
      <Trusses />
      <Speakers />
      {/* `loading` stays false: the spinner is owed to someone who clicked
          play, not to a stage that lights on hover */}
      <LEDScreens videoTexture={videoTexture} loading={false} onPlay={noop} />
      <StageLights motion={motion} dimmed={false} />
    </group>
  );
}

// ---- the photobooth ----
// Modelled on the classic Indian mall photo kiosk (the reference photo): a
// tall white cabin with red trim, a vertical lozenge banner down the left of
// the front, a gold curtain in the doorway, a dark flat roof overhanging the
// front, and a little red-framed hatch on the right. The copy is Breeze's:
// TEAM down the banner, BREEZE · 2027 across the lintel.

const BOOTH_WHITE = "#f2ece0";
const BOOTH_RED = "#b5432f";
const BOOTH_ROOF = "#17130f";
const CURTAIN_GOLD = "#c9a05a";

/**
 * The vertical banner: red rounded lozenge on the white pillar, TEAM reading
 * top-to-bottom in a serif — the reference kiosk's PHOTOS banner, re-lettered.
 */
function makeTeamBanner(): THREE.CanvasTexture {
  const W = 192;
  const H = 768;
  const { c, ctx } = mk(W, H);

  ctx.fillStyle = BOOTH_WHITE;
  ctx.fillRect(0, 0, W, H);

  const r = 78;
  const rounded = (inset: number, radius: number) => {
    ctx.beginPath();
    ctx.roundRect(inset, inset, W - inset * 2, H - inset * 2, radius);
  };
  ctx.fillStyle = BOOTH_RED;
  rounded(10, r);
  ctx.fill();
  // thin cream inset line, the detail that makes it read as a painted sign
  ctx.strokeStyle = BOOTH_WHITE;
  ctx.lineWidth = 5;
  rounded(24, r - 14);
  ctx.stroke();

  // letters rotated 90° so the word reads downward, as on the reference
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.rotate(Math.PI / 2);
  ctx.font = "700 132px Georgia, 'Times New Roman', serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = BOOTH_WHITE;
  ctx.fillText("TEAM", 0, 6);
  ctx.restore();

  return finish(c);
}

/** White lintel over the doorway with the fest's name in red serif caps. */
function makeLintel(): THREE.CanvasTexture {
  const W = 768;
  const H = 192;
  const { c, ctx } = mk(W, H);

  ctx.fillStyle = BOOTH_WHITE;
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = BOOTH_RED;
  ctx.fillRect(40, 26, W - 80, 6);
  ctx.fillRect(40, H - 32, W - 80, 6);

  ctx.font = "700 86px Georgia, 'Times New Roman', serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("BREEZE · 2027", W / 2, H / 2 + 4);

  return finish(c);
}

/** Hanging gold curtain: vertical folds, nothing else. */
function makeCurtain(): THREE.CanvasTexture {
  const W = 256;
  const H = 512;
  const { c, ctx } = mk(W, H);

  ctx.fillStyle = CURTAIN_GOLD;
  ctx.fillRect(0, 0, W, H);
  for (let i = 0; i < 15; i++) {
    const x = (i / 15) * W;
    const w = W / 15;
    const g = ctx.createLinearGradient(x, 0, x + w, 0);
    g.addColorStop(0, "rgba(58,40,16,0.4)");
    g.addColorStop(0.45, "rgba(240,205,140,0.32)");
    g.addColorStop(1, "rgba(58,40,16,0.4)");
    ctx.fillStyle = g;
    ctx.fillRect(x, 0, w, H);
  }
  return finish(c);
}

/**
 * Printed-surface material: lit by the scene like everything else, with just
 * enough self-light through its own art that the print survives the night —
 * the same treatment the arch's boards get.
 */
function printedMat(tex: THREE.Texture, emissive = 0.22): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    map: tex,
    emissiveMap: tex,
    emissive: new THREE.Color("#ffffff"),
    emissiveIntensity: emissive,
    roughness: 0.8,
  });
}

function Photobooth(): React.ReactElement {
  const banner = useMemo(() => printedMat(makeTeamBanner()), []);
  const lintel = useMemo(() => printedMat(makeLintel()), []);
  const curtain = useMemo(() => printedMat(makeCurtain(), 0.16), []);

  const white = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: BOOTH_WHITE,
        roughness: 0.85,
        // a trace of self-light, like the arch's printed boards: without it
        // the cabin falls to void-black wherever the two lamps don't reach
        emissive: new THREE.Color(BOOTH_WHITE),
        emissiveIntensity: 0.05,
      }),
    []
  );
  const red = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: BOOTH_RED,
        roughness: 0.8,
        emissive: new THREE.Color(BOOTH_RED),
        emissiveIntensity: 0.08,
      }),
    []
  );
  const roof = useMemo(
    () => new THREE.MeshStandardMaterial({ color: BOOTH_ROOF, roughness: 0.9 }),
    []
  );
  const dark = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#241f1a", roughness: 0.9 }),
    []
  );
  const bulbMat = useMemo(() => {
    const m = new THREE.MeshBasicMaterial({ color: NIGHT.bulb });
    m.toneMapped = false;
    return m;
  }, []);

  // the doorway spans x −0.60 … 0.95; the banner pillar carries the lozenge
  return (
    <group>
      {/* step */}
      <mesh material={dark} position={[0, 0.08, 0]}>
        <boxGeometry args={[3.9, 0.16, 3.3]} />
      </mesh>

      {/* shell: back, sides */}
      <mesh material={white} position={[0, 2.15, -1.42]}>
        <boxGeometry args={[3.4, 4.0, 0.15]} />
      </mesh>
      {[-1, 1].map((s) => (
        <mesh key={s} material={white} position={[s * 1.62, 2.15, 0]}>
          <boxGeometry args={[0.15, 4.0, 2.95]} />
        </mesh>
      ))}

      {/* front: banner pillar, narrow right pillar, lintel */}
      <mesh material={white} position={[-1.15, 2.15, 1.4]}>
        <boxGeometry args={[1.1, 4.0, 0.15]} />
      </mesh>
      <mesh material={banner} position={[-1.15, 2.05, 1.485]}>
        <planeGeometry args={[0.85, 3.4]} />
      </mesh>
      <mesh material={white} position={[1.32, 2.15, 1.4]}>
        <boxGeometry args={[0.75, 4.0, 0.15]} />
      </mesh>
      <mesh material={white} position={[0, 3.72, 1.4]}>
        <boxGeometry args={[3.4, 0.86, 0.15]} />
      </mesh>
      <mesh material={lintel} position={[0.17, 3.72, 1.485]}>
        <planeGeometry args={[1.65, 0.62]} />
      </mesh>

      {/* red trim: cabin corners and the doorway reveal */}
      {[-1, 1].map((s) => (
        <mesh key={s} material={red} position={[s * 1.68, 2.15, 1.42]}>
          <boxGeometry args={[0.07, 4.0, 0.07]} />
        </mesh>
      ))}
      <mesh material={red} position={[-0.62, 1.86, 1.44]}>
        <boxGeometry args={[0.06, 2.9, 0.06]} />
      </mesh>
      <mesh material={red} position={[0.96, 1.86, 1.44]}>
        <boxGeometry args={[0.06, 2.9, 0.06]} />
      </mesh>
      <mesh material={red} position={[0.17, 3.28, 1.44]}>
        <boxGeometry args={[1.64, 0.06, 0.06]} />
      </mesh>

      {/* the gold curtain, hung a little way into the doorway */}
      <mesh material={curtain} position={[0.17, 1.72, 0.85]}>
        <planeGeometry args={[1.62, 3.1]} />
      </mesh>

      {/* the hatch on the right pillar, and its red drop-box */}
      <mesh material={dark} position={[1.32, 2.42, 1.46]}>
        <boxGeometry args={[0.5, 0.6, 0.08]} />
      </mesh>
      <mesh material={red} position={[1.32, 2.08, 1.48]}>
        <boxGeometry args={[0.56, 0.07, 0.12]} />
      </mesh>
      <mesh material={red} position={[1.32, 1.45, 1.5]}>
        <boxGeometry args={[0.3, 0.34, 0.16]} />
      </mesh>

      {/* dark flat roof, overhanging the front as in the reference */}
      <mesh material={roof} position={[0, 4.28, 0.3]}>
        <boxGeometry args={[4.3, 0.2, 4.0]} />
      </mesh>
      <mesh material={roof} position={[0, 4.13, 2.1]}>
        <boxGeometry args={[4.3, 0.14, 0.4]} />
      </mesh>

      {/* practical under the overhang — the visible source of the front light */}
      <mesh material={bulbMat} position={[0.17, 3.95, 1.9]}>
        <sphereGeometry args={[0.07, 8, 8]} />
      </mesh>

      {/* the warm interior, mostly caught by the curtain */}
      <pointLight
        position={[0.17, 2.6, 0.2]}
        color={NIGHT.bulb}
        intensity={90}
        distance={12}
        decay={2}
      />
      {/* and the porch light the facade actually reads by — held down and
          pushed out so it grazes the front rather than torching the lintel */}
      <pointLight
        position={[0.3, 3.0, 4.6]}
        color={NIGHT.bulb}
        intensity={110}
        distance={16}
        decay={2}
      />
    </group>
  );
}

export const LANDMARKS: Landmark[] = [
  {
    id: "main-stage",
    label: "Main Stage",
    href: "/aftermovie", // the full ConcertStageHero, aftermovie and all
    // Out to the RIGHT rather than straight down the tunnel's axis. Dead
    // ahead it reads as the end of a corridor — something the run was aimed
    // at. Off to one side it reads as somewhere else on the ground that you
    // catch sight of the moment the walls fall away, which is the point.
    position: [28, 0, -120],
    // square-on to the arrival point. atan(28 / 64.4) — the exact yaw that
    // turns its front to the camera, so you get the stage's face rather than
    // a three-quarter view of its flank.
    rotationY: -0.41,
    // steps aside while the photobooth is featured
    when: (f) => f !== "team",
    Render: DistantStage,
  },
  {
    id: "photobooth",
    label: "Photobooth",
    href: "/team",
    // Nearer than the stage and scaled up a touch: a 5 m cabin at the stage's
    // 70 m would be a speck, and the swap would read as the stage vanishing
    // rather than a different place being featured. Sits about three-quarters
    // across the frame, where the stage stands, not jammed against its edge.
    // Yaw is the same solve — atan(12 / 28.4) toward the arrival point.
    position: [12, 0, -84],
    rotationY: -0.4,
    scale: 1.35,
    when: (f) => f === "team",
    Render: Photobooth as React.ComponentType<{ live: boolean; focus: MenuFocus }>,
  },
  // Next ones go here. Spread them around the ground rather than lining them
  // up: the point of the landmarks is that there is somewhere to go in every
  // direction, not a row of doors.
];

export default function Distant({
  live,
  focus,
}: {
  live: boolean;
  focus: MenuFocus;
}): React.ReactElement {
  return (
    <group>
      {/* `Grounds` only lays earth out to about 100 m, which was plenty when
          nothing stood past the arch. The landmarks are further out than that,
          and without this they float over a hole where the horizon should be */}
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.05, -170]}>
        <planeGeometry args={[420, 260]} />
        <meshStandardMaterial color={"#080a09"} roughness={1} />
      </mesh>
      {LANDMARKS.map(({ id, position, rotationY, scale, when, Render }) => (
        // `visible` rather than mount/unmount: the stage must not tear down
        // its warmed video element every time the pointer crosses Team
        <group
          key={id}
          position={position}
          rotation-y={rotationY ?? 0}
          scale={scale ?? 1}
          visible={!when || when(focus)}
        >
          <Render live={live} focus={focus} />
        </group>
      ))}
    </group>
  );
}
