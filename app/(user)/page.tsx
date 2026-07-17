"use client";
import React, { useEffect } from "react";
import dynamic from "next/dynamic";

import ParallaxHero from "../../components/landing-page/ParallaxHero";
import Sponsorship from "../../components/landing-page/sponsorship";
import AfterMovie from "../../components/landing-page/aftermovie";
import Gallery from "../../components/landing-page/gallery";
import "../globals.css";
import StatsSection from "../../components/landing-page/StatsSection";

// 3D stage is client-only (WebGL) and lazy-loaded to keep the initial bundle lean
const ConcertStageHero = dynamic(
  () => import("../../components/landing-page/stage3d/ConcertStageHero"),
  { ssr: false, loading: () => <div className="absolute inset-0 bg-black" /> }
);

export default function Home(): React.ReactElement {
  // Scroll to top on page load/refresh
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <main className="min-h-screen bg-black text-white relative w-full overflow-x-hidden">
      {/* Hero Section — 3D concert stage */}
      <div className="relative z-0 w-full min-h-screen h-dvh">
        <ConcertStageHero />
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
