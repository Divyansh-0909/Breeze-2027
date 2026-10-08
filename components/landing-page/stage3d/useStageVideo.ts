"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";

/** Extracted from ConcertStageHero: one video and texture for all LED panels. */
export function useStageVideo() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textureRef = useRef<THREE.VideoTexture | null>(null);
  const [phase, setPhase] = useState<"idle" | "loading" | "playing">("idle");
  const [pyroKey, setPyroKey] = useState(0);
  const playTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const disposalTimers = useRef(new Map<THREE.VideoTexture, ReturnType<typeof setTimeout>>());
  const stopMovie = useCallback(() => {
    if (playTimer.current !== null) clearTimeout(playTimer.current);
    playTimer.current = null;
    const video = videoRef.current;
    if (video) { video.pause(); video.removeAttribute("src"); video.load(); }
    const tex = textureRef.current;
    if (tex) disposalTimers.current.set(tex, setTimeout(() => { tex.dispose(); disposalTimers.current.delete(tex); }, 600));
    videoRef.current = null; textureRef.current = null; setPhase("idle");
  }, []);
  useEffect(() => () => {
    stopMovie();
    // Unmount owns every outstanding texture; do not leave timers/resources behind.
    disposalTimers.current.forEach((timer, tex) => { clearTimeout(timer); tex.dispose(); });
    disposalTimers.current.clear();
  }, [stopMovie]);
  const startMovie = useCallback(() => {
    if (videoRef.current) return;
    const video = document.createElement("video");
    video.playsInline = true; video.preload = "none";
    const tex = new THREE.VideoTexture(video);
    tex.colorSpace = THREE.SRGBColorSpace; tex.minFilter = THREE.LinearFilter;
    videoRef.current = video; textureRef.current = tex;
    video.addEventListener("playing", () => {
      if (videoRef.current !== video) return;
      setPhase("playing"); setPyroKey((key) => key + 1);
    }, { once: true });
    video.addEventListener("ended", () => { if (videoRef.current === video) stopMovie(); });
    video.addEventListener("error", () => { if (videoRef.current === video) stopMovie(); });
    setPhase("loading");
    // Preserve the original 900ms focus move and HTTP-range/progressive loading.
    playTimer.current = setTimeout(() => {
      if (videoRef.current !== video) return;
      video.src = "/after-movie.mp4"; video.currentTime = 0;
      video.play().catch(() => {
        if (videoRef.current !== video) return;
        video.muted = true;
        void video.play().catch(stopMovie);
      });
    }, 900);
  }, [stopMovie]);
  const enableSound = useCallback(() => { if (videoRef.current) videoRef.current.muted = false; }, []);
  const getStatus = useCallback(() => ({ phase, currentTime: videoRef.current?.currentTime ?? 0, paused: videoRef.current?.paused ?? true, muted: videoRef.current?.muted ?? false }), [phase]);
  useEffect(() => {
    if (phase === "idle") return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") stopMovie(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, stopMovie]);
  return { phase, pyroKey, texture: textureRef.current, startMovie, stopMovie, enableSound, getStatus };
}
