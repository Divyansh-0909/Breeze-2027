"use client";
import React, { useEffect, useState } from "react";

import { warmStage } from "../../components/landing-page/stage3d/warmup";
import GateHero from "../../components/landing-page/gate3d/GateHero";

import "../globals.css";

// Night entry gate — the loading page / entry portal (client-only WebGL,
// mounted after hydration). The concert stage remains on its own route,
// reached later through the Aftermovie quicklink.
export default function Home(): React.ReactElement {
  // GateHero stays out of the server-rendered tree, but is statically bundled
  // with this client route. This avoids a separately requested Webpack chunk
  // becoming stale after HMR or a `.next` cache rebuild.
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Scroll to top on page load/refresh
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  // Warm the aftermovie route while the visitor sits at the gate: stage
  // chunk, travel video, crowd models and pose-baking all happen here in the
  // background, so clicking Aftermovie later plays its walk over a scene
  // with almost nothing left to load. Delayed past the gate's own power-on
  // (~2.1 s) so the warm-up never competes with this page's entrance.
  useEffect(() => {
    const t = window.setTimeout(() => warmStage(), 3500);
    return () => window.clearTimeout(t);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white relative w-full overflow-x-hidden">
      <link
        rel="preload"
        as="image"
        href="/gate/beam.webp"
        type="image/webp"
        fetchPriority="high"
      />
      <link
        rel="preload"
        as="image"
        href="/gate/board-left.webp"
        type="image/webp"
        fetchPriority="high"
      />
      <link
        rel="preload"
        as="image"
        href="/gate/board-right.webp"
        type="image/webp"
        fetchPriority="high"
      />
      {/* Entry Section — 3D night gate (loading page / entry portal) */}
      <div className="relative z-0 w-full min-h-screen h-dvh">
        {mounted ? <GateHero /> : <div className="absolute inset-0 bg-black" />}
      </div>

      {/* Main Content - positioned to overlap hero */}
      {/* <div className="relative z-10">
        <div className="bg-black relative overflow-hidden"> */}
          {/* White gradient from left edge - stats section only */}
          {/* <div className="absolute left-0 top-0 bottom-0 w-32 md:w-48 bg-gradient-to-r from-white/20 to-transparent pointer-events-none z-10" /> */}
          {/* White gradient from right edge - stats section only */}
          {/* <div className="absolute right-0 top-0 bottom-0 w-32 md:w-48 bg-gradient-to-l from-white/20 to-transparent pointer-events-none z-10" />
          <StatsSection />
        </div> */}

        {/* Wrapper with white gradient behind rounded sponsorship corners */}
        {/* <div className="relative bg-black"> */}
          {/* White gradient from left edge - behind rounded corners */}
          {/* <div className="absolute left-0 top-0 h-24 w-32 md:w-48 bg-gradient-to-r from-white/20 to-transparent pointer-events-none z-0" /> */}
          {/* White gradient from right edge - behind rounded corners */}
          {/* <div className="absolute right-0 top-0 h-24 w-32 md:w-48 bg-gradient-to-l from-white/20 to-transparent pointer-events-none z-0" />
          <div className="relative z-10">
            <Sponsorship />
          </div>
        </div> */}

        {/* <Gallery />
        <AfterMovie /> */}
      {/* </div> */}
    </main>
  );
}
