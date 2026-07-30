"use client";
import React, { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Canvas, useFrame, useLoader, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

import { PALETTE } from "./palette";
import Barricades from "./Barricades";
import Crowd from "./Crowd";
import Fireworks from "./Fireworks";
import Stage from "./Stage";
import Trusses from "./Trusses";
import LEDScreens from "./LEDScreens";
import Speakers from "./Speakers";
import Lights from "./Lights";
import Particles from "./Particles";
import Effects from "./Effects";
import CameraRig from "./CameraRig";

/**
 * Hero entry point. Import with next/dynamic + ssr: false.
 * Fully procedural (no GLB downloads), one canvas, adaptive DPR [1, 1.75].
 */

/** Neutral PBR environment from three's built-in RoomEnvironment — no CDN/HDRI fetch. */
function Env(): null {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.1; // near-nothing: the LEDs/beams must read as the only light
    return () => {
      scene.environment = null;
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, scene]);
  return null;
}

/**
 * Frame-time governor: steps render resolution down when the GPU can't hold
 * ~50fps and cautiously back up once it's comfortably fast again. Each
 * downgrade doubles the streak of fast windows required before retrying, so
 * a machine that genuinely can't afford a level stops oscillating into it.
 */
const DPR_LEVELS = [1.5, 1.25, 1.0, 0.8];
function AdaptiveDpr({ startLevel = 0 }: { startLevel?: number }): null {
  const setDpr = useThree((s) => s.setDpr);
  const a = useRef({ t: 0, n: 0, level: startLevel, streak: 0, needStreak: 4 });

  useFrame((_, dt) => {
    const g = a.current;
    g.t += dt;
    g.n += 1;
    if (g.t < 1) return; // evaluate once per ~1s window
    const avg = g.t / g.n;
    g.t = 0;
    g.n = 0;

    const apply = () => setDpr(Math.min(DPR_LEVELS[g.level], window.devicePixelRatio));
    if (avg > 1 / 50 && g.level < DPR_LEVELS.length - 1) {
      g.level += 1;
      g.streak = 0;
      g.needStreak = Math.min(g.needStreak * 2, 60);
      apply();
    } else if (avg < 1 / 57 && g.level > 0) {
      if (++g.streak >= g.needStreak) {
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

type Phase = "idle" | "loading" | "playing";

/**
 * Fires `onReady` once the scene has PROVEN it renders smoothly: thirty
 * consecutive frames, not the first one. Mounted last inside the Suspense
 * boundary, so counting can't start until every sibling has resolved. A
 * loading screen that stands down on this signal reveals a scene that is
 * already fluid — never one still stuttering through warm-up.
 */
function ReadySignal({ onReady }: { onReady?: () => void }): null {
  const frames = useRef(0);
  useFrame(() => {
    if (frames.current > 30) return;
    frames.current += 1;
    if (frames.current === 30) onReady?.();
  });
  return null;
}


/**
 * While an opaque overlay covers the canvas, render at a fraction of the
 * resolution. The scene must keep rendering under the travel video — that is
 * what warms it — but nobody can see it, and at full DPR it competes with
 * the video for the GPU hard enough to stutter playback. At 0.45 DPR the
 * hidden warm-up costs roughly a fifth of the pixels; the jump back to full
 * resolution happens as the reveal fade begins, behind the overlay.
 */
function CoveredThrottle({ covered }: { covered: boolean }): null {
  const setDpr = useThree((s) => s.setDpr);
  useEffect(() => {
    setDpr(covered ? 0.45 : Math.min(1, window.devicePixelRatio));
  }, [covered, setDpr]);
  return null;
}

export default function ConcertStageHero({
  onReady,
  pov = false,
  covered = false,
}: {
  /** Called once, on the first frame the stage actually renders. */
  onReady?: () => void;
  /** Rest the camera in the crowd at eye height instead of the wide shot. */
  pov?: boolean;
  /** True while a loading overlay hides the canvas — renders cheap until then. */
  covered?: boolean;
} = {}): React.ReactElement {
  const reduced = usePrefersReducedMotion();
  const motion = !reduced;

  // ---- staged warm-up (pov only) ----
  // The scene arrives in WAVES rather than at once. Mounting everything
  // together stacks GLB parsing, crowd pose-baking and one monolithic shader
  // compile into a single frame — a stall long enough to visibly stutter the
  // travel video playing on top, wherever in the video it lands. Split into
  // waves, each mount is a small burst with breathing room between: the
  // set first, then rig and lights, then the crowd (whose models started
  // fetching at wave one), then post-processing. Outside pov there is no
  // video to protect and everything mounts at once, as it always did.
  const [wave, setWave] = useState(pov ? 1 : 4);
  useEffect(() => {
    if (!pov) return;
    const ts = [
      window.setTimeout(() => setWave(2), 1200),
      window.setTimeout(() => setWave(3), 2600),
      window.setTimeout(() => setWave(4), 4200),
    ];
    return () => ts.forEach((t) => window.clearTimeout(t));
  }, [pov]);
  useEffect(() => {
    // models fetch and parse from the first moment, well before the crowd
    // mounts and needs them — its wave then pays only for pose-baking
    useLoader.preload(GLTFLoader, ["/models/Man.glb", "/models/Animated-Woman.glb"]);
  }, []);

  // ---- aftermovie on the LED wall ----
  // Nothing downloads up-front: clicking play zooms the camera in, dims the
  // rig, and only THEN starts fetching /after-movie.mp4 — the center screen
  // shows a loading spinner while it buffers. The video wall and the pyro
  // both wait for the first real playback frame.
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textureRef = useRef<THREE.VideoTexture | null>(null);
  const [phase, setPhase] = useState<Phase>("idle");
  const [pyroKey, setPyroKey] = useState(0);

  const playTimer = useRef<number | null>(null);
  const clickedAt = useRef(0);

  const stopMovie = useCallback(() => {
    if (playTimer.current !== null) window.clearTimeout(playTimer.current);
    playTimer.current = null;
    const video = videoRef.current;
    if (video) {
      // aborts any in-flight download as well as playback
      video.pause();
      video.removeAttribute("src");
      video.load();
    }
    // dispose only after the wall's ~0.35s fade-out has finished sampling it
    const tex = textureRef.current;
    if (tex) window.setTimeout(() => tex.dispose(), 600);
    videoRef.current = null;
    textureRef.current = null;
    setPhase("idle");
  }, []);

  // unmount mid-load/mid-show: tear the video down so it stops downloading
  useEffect(() => stopMovie, [stopMovie]);

  const startMovie = useCallback(() => {
    if (videoRef.current) return; // already loading or playing

    const video = document.createElement("video");
    video.playsInline = true;
    video.preload = "auto";
    const tex = new THREE.VideoTexture(video);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.minFilter = THREE.LinearFilter;
    videoRef.current = video;
    textureRef.current = tex;

    // buffered enough to play through uninterrupted → roll it, but never
    // before the camera dolly has landed (~0.9s), so a cached instant load
    // still gets the show-opening beat
    video.addEventListener(
      "canplaythrough",
      () => {
        const wait = Math.max(0, 900 - (performance.now() - clickedAt.current));
        playTimer.current = window.setTimeout(() => {
          video.currentTime = 0;
          // long loads can outlive the click's user-activation window, in
          // which case unmuted play() is blocked — degrade to muted playback
          // rather than stalling the show
          video.play().catch(() => {
            video.muted = true;
            void video.play();
          });
        }, wait);
      },
      { once: true }
    );

    // pyro + video wall are keyed off ACTUAL playback, not the click
    video.addEventListener(
      "playing",
      () => {
        setPhase("playing");
        setPyroKey((k) => k + 1);
      },
      { once: true }
    );

    video.addEventListener("ended", stopMovie);
    video.addEventListener("error", stopMovie);

    clickedAt.current = performance.now();
    setPhase("loading");
    video.src = "/after-movie.mp4"; // download starts here, not at page load
    video.load();
  }, [stopMovie]);

  // Esc cancels the load / exits the aftermovie
  useEffect(() => {
    if (phase === "idle") return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") stopMovie();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, stopMovie]);

  return (
    <div className="absolute inset-0" aria-label="3D concert stage">
      <Canvas
        // pov opens at 1.0 dpr and earns its way up instead of opening at 1.5
        // and discovering it can't afford it — the discovery is a slow first
        // second exactly when the loading screen hands over.
        // NOTE: no frameloop gating. A shader-compile gate was tried here
        // (frameloop "never" until compileAsync resolved) and produced black
        // screens — the parked loop didn't reliably restart. The sync compile
        // cost lands on the first frame instead, early under the travel
        // video, which is a hitch nobody sees rather than a page nobody sees.
        dpr={pov ? 1 : [1, 1.5]}
        camera={{ fov: 42, near: 0.5, far: 150, position: [0, 7.2, 28.5] }}
        gl={{ antialias: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={[PALETTE.void]} />
        <fog attach="fog" args={[PALETTE.void, 24, 62]} />
        <Suspense fallback={null}>
          {/* wave 1: the set AND the full light rig. Lights must be in the
              first wave: three.js recompiles every material in the scene
              whenever the light count changes, so lights arriving in a later
              wave would stall the page on a full recompile of everything the
              earlier waves had already paid for. */}
          {/* the governor stays out of the way while covered — it would fight
              the throttle's pinned low resolution */}
          {pov && <CoveredThrottle covered={covered} />}
          {!covered && <AdaptiveDpr startLevel={pov ? 2 : 0} />}
          <Env />
          <Stage />
          <LEDScreens
            videoTexture={phase === "playing" ? textureRef.current : null}
            loading={phase === "loading"}
            onPlay={startMovie}
          />
          <Lights motion={motion} dimmed={phase !== "idle"} />
          <CameraRig motion={motion} focus={phase !== "idle"} pov={pov} />

          {/* wave 2: the rig's steel */}
          {wave >= 2 && (
            <>
              <Trusses />
              <Speakers />
            </>
          )}

          {/* wave 3: the crowd — its OWN Suspense boundary, so its loaders
              re-suspending can never blank the already-visible waves. The
              crowd itself then chunks its pose-baking (see Crowd) unless
              told otherwise. */}
          {wave >= 3 && (
            <Suspense fallback={null}>
              <Crowd immediate={!pov} />
              <Barricades />
            </Suspense>
          )}

          {/* wave 4: post-processing and set dressing; ready is only
              reportable once everything above is in */}
          {wave >= 4 && (
            <>
              {/* pods are permanent set-dressing; the fire itself only
                  ignites when the aftermovie actually starts playing */}
              <Fireworks key={pyroKey} active={motion && pyroKey > 0 && phase === "playing"} />
              <Particles />
              <Effects />
              <ReadySignal onReady={onReady} />
            </>
          )}
        </Suspense>
      </Canvas>
      {/* cancel/exit hint while loading or playing */}
      {phase !== "idle" && (
        <div className="pointer-events-none absolute bottom-8 left-1/2 z-10 -translate-x-1/2 rounded-full bg-black/60 backdrop-blur-md border border-white/15 px-4 py-1.5 text-sm text-white/75">
          Press <span className="font-semibold text-white">Esc</span> to{" "}
          {phase === "loading" ? "cancel" : "exit"}
        </div>
      )}
      {/* fade into the black content below */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black to-transparent" />
    </div>
  );
}
