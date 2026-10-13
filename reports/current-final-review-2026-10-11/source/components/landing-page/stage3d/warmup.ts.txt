"use client";
import { warmCrowd } from "./Crowd";

/**
 * Warms everything the aftermovie route needs, from anywhere — meant to run
 * on the LANDING page, while the visitor sits on "click anywhere to
 * continue". By the time they reach /aftermovie:
 *
 * - the stage's JS chunk is downloaded and parsed (module cache)
 * - the travel video is in the HTTP cache, so it opens on its first frames
 * - the crowd models are fetched and their four pose variants baked, held in
 *   Crowd's module-level cache
 *
 * What can NOT be warmed here is shader compilation — it belongs to a WebGL
 * context that doesn't exist until the stage's canvas mounts. That cost
 * stays on the aftermovie route, which is why its scene still mounts in
 * waves under the travel video.
 *
 * Everything here is failure-tolerant background work: any of it failing
 * just means the aftermovie route does that work itself, as it always could.
 */
let started = false;
export function warmStage(): void {
  if (started || typeof window === "undefined") return;
  started = true;

  void import("./ConcertStageHero");
  fetch("/travel-crowd.mp4").catch(() => {
    /* cache priming only */
  });
  void warmCrowd();
}
