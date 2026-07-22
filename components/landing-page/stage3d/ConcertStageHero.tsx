"use client";
import React, { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

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
function AdaptiveDpr(): null {
  const setDpr = useThree((s) => s.setDpr);
  const a = useRef({ t: 0, n: 0, level: 0, streak: 0, needStreak: 4 });

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

export default function ConcertStageHero(): React.ReactElement {
  const reduced = usePrefersReducedMotion();
  const motion = !reduced;

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
        dpr={[1, 1.5]}
        camera={{ fov: 42, near: 0.5, far: 150, position: [0, 7.2, 28.5] }}
        gl={{ antialias: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={[PALETTE.void]} />
        <fog attach="fog" args={[PALETTE.void, 24, 62]} />
        <Suspense fallback={null}>
          <AdaptiveDpr />
          <Env />
          <Stage />
          <Barricades />
          <Crowd />
          {/* pods are permanent set-dressing; the fire itself only ignites
              when the aftermovie actually starts playing — never on page
              load, never while it's still buffering */}
          <Fireworks key={pyroKey} active={motion && pyroKey > 0 && phase === "playing"} />
          <Trusses />
          <LEDScreens
            videoTexture={phase === "playing" ? textureRef.current : null}
            loading={phase === "loading"}
            onPlay={startMovie}
          />
          <Speakers />
          <Lights motion={motion} dimmed={phase !== "idle"} />
          <Particles />
          <CameraRig motion={motion} focus={phase !== "idle"} />
          <Effects />
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
