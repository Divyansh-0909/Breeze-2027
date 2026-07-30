"use client";
import React, { useCallback, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";

import TravelOverlay from "../../../components/landing-page/stage3d/TravelOverlay";
import "../../globals.css";

// The 3D concert stage with the aftermovie on its LED wall — client-only
// WebGL. The travel overlay covers its whole start-up; no separate loading
// fallback, or the two would fight over the same moment.
const ConcertStageHero = dynamic(
  () => import("../../../components/landing-page/stage3d/ConcertStageHero"),
  { ssr: false, loading: () => null }
);

/**
 * The overlay never hides before this, loaded or not: the walk through the
 * crowd plays END TO END for everyone — 7.54 s of video plus a breath on its
 * final frame, which is the live scene's first frame. The wait costs nothing
 * visually; the reveal is a fade between two identical images whenever the
 * stage is ready.
 */
const MIN_SHOW_MS = 7900;

/**
 * When the stage mounts: essentially at once — one beat after the video's
 * first frames are up, so autoplay start (the one fragile moment) is never
 * competed with. Everything heavy then overlaps the walk itself: GLB fetch
 * and parse, crowd pose-baking, PMREM, and the async shader compile behind
 * `CompileGate`, with ~7 seconds of opaque video to hide under. By the end
 * of the walk the scene has been rendering for seconds — ready fired, DPR
 * settled, warm — and the reveal is nothing but the crossfade itself.
 * (Mounting later was tried; it pushed this work toward the walk's end,
 * which is exactly where it was felt.)
 */
const MOUNT_AT_MS = 600;

export default function AftermoviePage(): React.ReactElement {
  // `/aftermovie?bare` mounts the stage alone — no overlay, no timers — to
  // separate "the 3D scene is broken" from "the page choreography is broken".
  // `&wide` drops pov as well, which is the scene in its oldest configuration.
  const [bare, setBare] = useState<null | { pov: boolean }>(null);
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    if (q.has("bare")) setBare({ pov: !q.has("wide") });
  }, []);

  const [ready, setReady] = useState(false);
  const [gone, setGone] = useState(false);
  // The stage mounts mid-walk (see MOUNT_AT_MS); its chunk preloads from the
  // first moment so the timer spends nothing on the network.
  const [mountStage, setMountStage] = useState(false);
  const shownAt = useRef(0);
  // `/aftermovie?travel` pins the overlay open — for styling it without
  // racing the load
  const pinned = useRef(false);

  useEffect(() => {
    shownAt.current = performance.now();
    pinned.current = new URLSearchParams(window.location.search).has("travel");
    // warm the stage's code immediately; the mount timer then spends nothing
    // on the network
    void import("../../../components/landing-page/stage3d/ConcertStageHero");
    const t = window.setTimeout(() => setMountStage(true), MOUNT_AT_MS);
    return () => window.clearTimeout(t);
  }, []);

  // The walk's end is a free window: the video holds a FROZEN frame from
  // here until the reveal, and a still image cannot stutter. So this is
  // where the render throttle comes off — the jump back to full resolution
  // (buffer reallocation + first full-res frame, the one remaining hitch)
  // happens behind that frozen frame instead of during playback.
  const [walkEnded, setWalkEnded] = useState(false);
  const onWalkEnded = useCallback(() => {
    setMountStage(true); // backstop, if the mount timer was throttled
    setWalkEnded(true);
  }, []);

  const onReady = useCallback(() => {
    if (pinned.current) return;
    const wait = Math.max(0, MIN_SHOW_MS - (performance.now() - shownAt.current));
    window.setTimeout(() => setReady(true), wait);
  }, []);

  // never a trap: if WebGL fails and the first frame never comes, stand the
  // overlay down anyway rather than holding a travel screen forever
  useEffect(() => {
    const t = window.setTimeout(() => {
      if (!pinned.current) setReady(true);
    }, 18000);
    return () => window.clearTimeout(t);
  }, []);

  // unmount after the fade so the video stops costing anything
  useEffect(() => {
    if (!ready) return;
    const t = window.setTimeout(() => setGone(true), 800);
    return () => window.clearTimeout(t);
  }, [ready]);

  if (bare) {
    return (
      <main className="min-h-screen bg-black text-white relative w-full overflow-x-hidden">
        <div className="relative z-0 w-full min-h-screen h-dvh">
          <ConcertStageHero pov={bare.pov} />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-black text-white relative w-full overflow-x-hidden">
      <div className="relative z-0 w-full min-h-screen h-dvh">
        {/* pov: the camera rests in the crowd at eye height, so the scene
            picks up exactly where the overlay's walk ends. `covered` keeps
            the hidden warm-up render cheap so it can't stutter the video. */}
        {mountStage && (
          <ConcertStageHero
            onReady={onReady}
            pov
            // covered until the walk ENDS, not until the reveal: the stretch
            // between those two is the frozen last frame, where the costly
            // return to full resolution is invisible. `ready` is the fallback
            // for the day `ended` doesn't fire.
            covered={!walkEnded && !ready}
          />
        )}
        {!gone && <TravelOverlay done={ready} onEnded={onWalkEnded} />}
      </div>
    </main>
  );
}
