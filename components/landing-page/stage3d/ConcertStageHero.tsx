"use client";
import React, { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

import { PALETTE } from "./palette";
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

export default function ConcertStageHero(): React.ReactElement {
  const reduced = usePrefersReducedMotion();
  const motion = !reduced;

  // ---- aftermovie on the LED wall: click-to-play (user gesture → plays
  // WITH sound), camera zooms in while it runs, ✕ or video end returns ----
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textureRef = useRef<THREE.VideoTexture | null>(null);
  const [playing, setPlaying] = useState(false);
  const [pyroKey, setPyroKey] = useState(0);

  const stopMovie = useCallback(() => {
    videoRef.current?.pause();
    setPlaying(false);
  }, []);

  const startMovie = useCallback(() => {
    let video = videoRef.current;
    if (!video) {
      // created lazily — the 600MB file only downloads for viewers who ask
      video = document.createElement("video");
      video.src = "/after-movie.mp4";
      video.playsInline = true;
      video.preload = "metadata";
      video.addEventListener("ended", stopMovie);
      videoRef.current = video;
      const tex = new THREE.VideoTexture(video);
      tex.colorSpace = THREE.SRGBColorSpace;
      tex.minFilter = THREE.LinearFilter;
      textureRef.current = tex;
    }
    video.currentTime = 0;
    void video.play();
    setPlaying(true);
    setPyroKey((k) => k + 1); // re-fire the stage pyro as the show opens
  }, [stopMovie]);

  useEffect(
    () => () => {
      // unmount: tear the video down so it stops downloading/decoding
      videoRef.current?.pause();
      videoRef.current?.removeAttribute("src");
      videoRef.current?.load();
      textureRef.current?.dispose();
    },
    []
  );

  // Esc exits the aftermovie
  useEffect(() => {
    if (!playing) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") stopMovie();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [playing, stopMovie]);

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
          <Env />
          <Stage />
          <Crowd />
          {/* pyro only fires as the aftermovie show opens — never on page load */}
          {motion && pyroKey > 0 && <Fireworks key={pyroKey} />}
          <Trusses />
          <LEDScreens videoTexture={playing ? textureRef.current : null} onPlay={startMovie} />
          <Speakers />
          <Lights motion={motion} dimmed={playing} />
          <Particles />
          <CameraRig motion={motion} focus={playing} />
          <Effects />
        </Suspense>
      </Canvas>
      {/* close the aftermovie */}
      {playing && (
        <button
          onClick={stopMovie}
          aria-label="Close aftermovie"
          className="absolute right-5 top-[11vh] z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black/60 backdrop-blur-md border border-white/20 text-white/80 transition-colors hover:text-white hover:border-white/40"
        >
          ✕
        </button>
      )}
      {/* exit hint while the movie runs */}
      {playing && (
        <div className="pointer-events-none absolute bottom-8 left-1/2 z-10 -translate-x-1/2 rounded-full bg-black/60 backdrop-blur-md border border-white/15 px-4 py-1.5 text-sm text-white/75">
          Press <span className="font-semibold text-white">Esc</span> to exit
        </div>
      )}
      {/* fade into the black content below */}
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-black to-transparent" />
    </div>
  );
}
