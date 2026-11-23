"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { LinearFilter, SRGBColorSpace, VideoTexture } from "three";
import { stageVideoSource } from "../landing-page/stage3d/useStageVideo";

export type ScreenFilm = { video: HTMLVideoElement; texture: VideoTexture };

/**
 * The plaza screen's Aftermovie: one looping video for the whole visit. It starts muted (browsers allow
 * muted autoplay); its sound reaches the gully through GullyAudio once the visitor first interacts.
 * It pauses while the tab is hidden. `restart` plays it from the start (the Watch action).
 */
export function useScreenFilm(onError: () => void) {
  const [film, setFilm] = useState<ScreenFilm | null>(null);
  const [ready, setReady] = useState(false);
  const failed = useRef(onError);
  failed.current = onError;

  useEffect(() => {
    const video = document.createElement("video");
    video.src = stageVideoSource; video.loop = true; video.muted = true; video.playsInline = true;
    video.setAttribute("playsinline", ""); video.preload = "auto";
    const texture = new VideoTexture(video);
    texture.colorSpace = SRGBColorSpace; texture.minFilter = LinearFilter;
    const playing = () => setReady(true);
    const error = () => { setReady(false); failed.current(); };
    const play = () => { if (!document.hidden) void video.play().catch(() => { /* retried on the first gesture */ }); };
    const visibility = () => { if (document.hidden) video.pause(); else play(); };
    video.addEventListener("playing", playing);
    video.addEventListener("error", error);
    document.addEventListener("visibilitychange", visibility);
    play();
    setFilm({ video, texture });
    return () => {
      video.removeEventListener("playing", playing);
      video.removeEventListener("error", error);
      document.removeEventListener("visibilitychange", visibility);
      video.pause(); video.removeAttribute("src"); video.load();
      texture.dispose();
      setFilm(null); setReady(false);
    };
  }, []);

  const restart = useCallback(() => {
    if (!film) return;
    const { video } = film;
    if (video.error) { video.src = stageVideoSource; video.load(); }
    video.currentTime = 0;
    void video.play().catch(() => failed.current());
  }, [film]);

  return { film, ready, restart };
}
