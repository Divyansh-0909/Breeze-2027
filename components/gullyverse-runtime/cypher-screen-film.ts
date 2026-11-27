"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { LinearFilter, SRGBColorSpace, VideoTexture } from "three";
import { stageVideoSource } from "../landing-page/stage3d/useStageVideo";

export type ScreenFilm = { video: HTMLVideoElement; texture: VideoTexture };

/** The background loop: the same film at 1280 x 720 and about 1.1 Mbit/s (30 MB instead of 52 MB). */
export const loopSource = "/after-movie-720.mp4";

/**
 * The plaza screen's Aftermovie: one looping video for the whole visit. It starts once `active` (the
 * world has finished streaming, so the film never competes with it for bandwidth), muted (browsers
 * allow muted autoplay); its sound reaches the gully through GullyAudio once the visitor first
 * interacts. It pauses while the tab is hidden. The loop plays the 720p copy; `restart` (the Watch
 * action) switches to the full 1080p film and plays it from the start.
 */
export function useScreenFilm(onError: () => void, active: boolean) {
  const [film, setFilm] = useState<ScreenFilm | null>(null);
  const [ready, setReady] = useState(false);
  const failed = useRef(onError);
  failed.current = onError;

  useEffect(() => {
    if (!active) return;
    const video = document.createElement("video");
    video.src = loopSource; video.loop = true; video.muted = true; video.playsInline = true;
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
  }, [active]);

  /** `full`: switch to the 1080p film (low-tier devices keep the 720p loop: bandwidth and decoder memory). */
  const restart = useCallback((full = true) => {
    if (!film) return;
    const { video } = film;
    if (full && (video.error || !video.src.endsWith(stageVideoSource))) { video.src = stageVideoSource; video.load(); }
    else if (video.error) { video.src = loopSource; video.load(); }
    video.currentTime = 0;
    void video.play().catch(() => failed.current());
  }, [film]);

  return { film, ready, restart };
}
