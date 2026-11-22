"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { ownVideoTexture, retireVideoTexture } from "./videoTextureOwnership";

export const stageVideoSource = "/after-movie.mp4";

/** Extracted from ConcertStageHero: one video and texture for all LED panels. */
export function useStageVideo(onActiveChange?: (active: boolean) => void,
  { startMuted = false, onError }: { startMuted?: boolean; onError?: () => void } = {}) {
  const activeCallback = useRef(onActiveChange);
  activeCallback.current = onActiveChange;
  const errorCallback = useRef(onError);
  errorCallback.current = onError;
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
    video.playsInline = true; video.preload = "none"; video.muted = startMuted;
    const tex = new THREE.VideoTexture(video);
    ownVideoTexture(tex);
    tex.colorSpace = THREE.SRGBColorSpace; tex.minFilter = THREE.LinearFilter;
    videoRef.current = video; textureRef.current = tex;
    const playing = () => {
      if (videoRef.current !== video) return;
      setPhase("playing"); setPyroKey((key) => key + 1);
    };
    const ended = () => { if (videoRef.current === video) stopMovie(); };
    const failed = () => {
      if (videoRef.current !== video) return;
      stopMovie();
      errorCallback.current?.();
    };
    video.addEventListener("playing", playing, { once: true });
    video.addEventListener("ended", ended); video.addEventListener("error", failed);
    listeners.current = () => {
      video.removeEventListener("playing", playing); video.removeEventListener("ended", ended); video.removeEventListener("error", failed);
    };
    activeCallback.current?.(true);
    setPhase("loading");
    const play = () => {
      playTimer.current = null;
      if (videoRef.current !== video) return;
      video.src = stageVideoSource;
      video.play().catch(() => {
        if (videoRef.current !== video) return;
        if (video.muted) { failed(); return; }
        video.muted = true;
        void video.play().catch(failed);
      });
    };
    // The cypher starts muted inside the tap. The original stage keeps its focus delay.
    if (startMuted) play();
    else playTimer.current = setTimeout(play, 900);
  }, [startMuted, stopMovie]);
  const setMuted = useCallback((muted: boolean) => { if (videoRef.current) videoRef.current.muted = muted; }, []);
  const enableSound = useCallback(() => setMuted(false), [setMuted]);
  const getStatus = useCallback(() => ({ phase, currentTime: videoRef.current?.currentTime ?? 0, paused: videoRef.current?.paused ?? true, muted: videoRef.current?.muted ?? false }), [phase]);
  useEffect(() => {
    if (phase === "idle") return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && !(e.target instanceof Element && e.target.closest("form, input, textarea, select, [contenteditable]:not([contenteditable=false])"))) stopMovie(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [phase, stopMovie]);
  return { phase, pyroKey, texture: textureRef.current, startMovie, stopMovie, enableSound, setMuted, getStatus };
}
