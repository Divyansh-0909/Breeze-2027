"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { ownVideoTexture, retireVideoTexture } from "./videoTextureOwnership";

/** Extracted from ConcertStageHero: one video and texture for all LED panels. */
export function useStageVideo(onActiveChange?: (active: boolean) => void) {
  const activeCallback = useRef(onActiveChange);
  activeCallback.current = onActiveChange;
  const listeners = useRef<(() => void) | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const textureRef = useRef<THREE.VideoTexture | null>(null);
  const [phase, setPhase] = useState<"idle" | "loading" | "playing">("idle");
  const [pyroKey, setPyroKey] = useState(0);
  const playTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const stopMovie = useCallback(() => {
    if (playTimer.current !== null) clearTimeout(playTimer.current);
    playTimer.current = null;
    listeners.current?.(); listeners.current = null;
    const video = videoRef.current;
    if (video) { video.pause(); video.removeAttribute("src"); video.load(); }
    const tex = textureRef.current;
    if (tex) retireVideoTexture(tex);
    videoRef.current = null; textureRef.current = null; activeCallback.current?.(false); setPhase("idle");
  }, []);
  useEffect(() => () => {
    stopMovie();
  }, [stopMovie]);
  const startMovie = useCallback(() => {
    if (videoRef.current) return;
    const video = document.createElement("video");
    video.playsInline = true; video.preload = "none";
    const tex = new THREE.VideoTexture(video);
    ownVideoTexture(tex);
    tex.colorSpace = THREE.SRGBColorSpace; tex.minFilter = THREE.LinearFilter;
    videoRef.current = video; textureRef.current = tex;
    const playing = () => {
      if (videoRef.current !== video) return;
      setPhase("playing"); setPyroKey((key) => key + 1);
    };
    const ended = () => { if (videoRef.current === video) stopMovie(); };
    video.addEventListener("playing", playing, { once: true });
    video.addEventListener("ended", ended); video.addEventListener("error", ended);
    listeners.current = () => {
      video.removeEventListener("playing", playing); video.removeEventListener("ended", ended); video.removeEventListener("error", ended);
    };
    activeCallback.current?.(true);
    setPhase("loading");
    // Preserve the original 900ms focus move and HTTP-range/progressive loading.
    playTimer.current = setTimeout(() => {
      if (videoRef.current !== video) return;
      video.src = "/after-movie.mp4"; video.currentTime = 0;
      video.play().catch(() => {
        if (videoRef.current !== video) return;
        video.muted = true;
        void video.play().catch(() => { if (videoRef.current === video) stopMovie(); });
      });
    }, 900);
  }, [stopMovie]);
  const enableSound = useCallback(() => { if (videoRef.current) videoRef.current.muted = false; }, []);
  const getStatus = useCallback(() => ({ phase, currentTime: videoRef.current?.currentTime ?? 0, paused: videoRef.current?.paused ?? true, muted: videoRef.current?.muted ?? false }), [phase]);
  useEffect(() => {
    if (phase === "idle") return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && !(e.target instanceof Element && e.target.closest("form, input, textarea, select, [contenteditable]:not([contenteditable=false])"))) stopMovie(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, stopMovie]);
  return { phase, pyroKey, texture: textureRef.current, startMovie, stopMovie, enableSound, getStatus };
}
