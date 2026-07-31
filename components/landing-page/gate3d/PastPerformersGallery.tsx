"use client";
import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { PERFORMERS } from "./performers";
import SprayHeadline from "./SprayHeadline";

const DISPLAY = "'Impact', 'Haettenschweiler', 'Arial Black', sans-serif";

const SQUIGGLE_LR =
  "M 200 0 C 200 80, 100 120, 150 200 C 200 280, 500 200, 700 240 C 900 280, 950 350, 800 420 C 650 490, 600 550, 750 600";
const SQUIGGLE_RL =
  "M 800 0 C 800 80, 900 120, 850 200 C 800 280, 500 200, 300 240 C 100 280, 50 350, 200 420 C 350 490, 400 550, 250 600";

function getProgress(el: HTMLElement, startPct: number, endPct: number): number {
  const rect = el.getBoundingClientRect();
  const vh = window.innerHeight;
  const start = vh * startPct;
  const end = vh * endPct;
  const raw = (start - rect.top) / (start - end);
  return Math.min(1, Math.max(0, raw));
}

export default function PastPerformersGallery() {
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const pathRefs = useRef<(SVGPathElement | null)[]>([]);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [isMobile, setIsMobile] = useState(true);

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768);
    check();
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  useEffect(() => {
    const pathLengths: number[] = [];

    const rafId = requestAnimationFrame(() => {
      PERFORMERS.forEach((_, i) => {
        const pathEl = pathRefs.current[i];
        if (!pathEl) { pathLengths[i] = 0; return; }
        const len = pathEl.getTotalLength();
        if (len < 1) { pathLengths[i] = 0; return; }
        pathLengths[i] = len;
        pathEl.style.strokeDasharray = `${len}`;
        pathEl.style.strokeDashoffset = `${len}`;
      });
      update();
    });

    function update() {
      PERFORMERS.forEach((_, i) => {
        const sectionEl = sectionRefs.current[i];
        if (!sectionEl) return;

        const cardEl = cardRefs.current[i];
        if (cardEl) {
          const cardProg = getProgress(sectionEl, 0.9, 0.8);
          cardEl.style.opacity = `${cardProg}`;
          cardEl.style.transform = `translateY(${60 * (1 - cardProg)}px)`;
        }

        const pathEl = pathRefs.current[i];
        const len = pathLengths[i];
        if (pathEl && len) {
          const lineProg = getProgress(sectionEl, 0.8, 0.2);
          pathEl.style.strokeDashoffset = `${len * (1 - lineProg)}`;
        }
      });
    }

    let ticking = false;
    function onScroll() {
      if (!ticking) {
        requestAnimationFrame(() => { update(); ticking = false; });
        ticking = true;
      }
    }

    window.addEventListener("scroll", onScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", onScroll);
      cancelAnimationFrame(rafId);
      PERFORMERS.forEach((_, i) => {
        const pathEl = pathRefs.current[i];
        if (pathEl) { pathEl.style.strokeDasharray = ""; pathEl.style.strokeDashoffset = ""; }
        const cardEl = cardRefs.current[i];
        if (cardEl) { cardEl.style.opacity = ""; cardEl.style.transform = ""; }
      });
    };
  }, [isMobile]);

  const pathFor = (isLeft: boolean) => (isLeft ? SQUIGGLE_LR : SQUIGGLE_RL);

  return (
    <section className="relative min-h-screen overflow-x-hidden" style={{ background: "#04060e" }}>

      {/* Gullyverse graffiti backdrop */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <svg width="100%" height="100%" className="absolute inset-0">
          <defs>
            <pattern id="gully-past-perf" width="900" height="900" patternUnits="userSpaceOnUse">
              <g stroke="rgba(244,239,226,0.05)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
                <path d="M 80,50 C 250,20 400,180 350,350 C 300,520 50,480 80,300 Z" />
                <path d="M 500,100 L 650,30 L 780,200 L 850,80 L 820,350 L 900,500 L 680,420 L 600,700 L 480,380 Z" />
                <path d="M -50,650 C 150,600 300,850 500,780 C 700,710 780,950 600,1050" />
                <circle cx="220" cy="180" r="65" />
                <circle cx="220" cy="180" r="25" />
                <circle cx="620" cy="250" r="50" />
                <circle cx="620" cy="250" r="18" />
                <circle cx="400" cy="800" r="55" />
                <circle cx="400" cy="800" r="20" />
                <path d="M 530,320 L 530,400 M 760,580 L 760,660 M 870,420 L 870,530" strokeWidth="5" />
              </g>
              <text x="480" y="720" fill="rgba(244,239,226,0.03)" stroke="none" fontSize="75" fontFamily="'Impact', sans-serif" transform="rotate(-12 480 720)">बोल</text>
              <text x="60" y="680" fill="rgba(244,239,226,0.03)" stroke="none" fontSize="95" fontFamily="'Impact', sans-serif" transform="rotate(20 60 680)">GULLY</text>
              <text x="650" y="850" fill="rgba(244,239,226,0.025)" stroke="none" fontSize="60" fontFamily="'Impact', sans-serif" transform="rotate(-8 650 850)">VERSE</text>

              {/* Aerosol color wash blobs */}
              <circle cx="180" cy="200" r="160" fill="rgba(208,57,44,0.025)" />
              <circle cx="700" cy="150" r="120" fill="rgba(242,179,15,0.02)" />
              <circle cx="600" cy="650" r="200" fill="rgba(31,95,208,0.02)" />
              <circle cx="100" cy="750" r="220" fill="rgba(214,53,127,0.02)" />
              <circle cx="450" cy="450" r="140" fill="rgba(47,158,90,0.015)" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#gully-past-perf)" />
        </svg>

        {/* Radial vignette */}
        <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at center, rgba(4,6,14,0) 0%, rgba(4,6,14,0.4) 50%, #04060e 100%)" }} />

        {/* Top-to-bottom gradient fade for depth */}
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, #04060e 0%, transparent 8%, transparent 92%, #04060e 100%)" }} />
      </div>

      {/* Header */}
      <div className="relative z-10 w-full pt-28 pb-16 flex justify-center">
        <SprayHeadline text="PAST PERFORMERS" className="text-6xl md:text-8xl" />
      </div>

      {/* Gallery */}
      <div className="relative z-10 max-w-6xl mx-auto w-full flex flex-col pt-12 pb-64 px-4 md:px-8">
        {PERFORMERS.map((performer, i) => {
          const isLeft = i % 2 === 0;
          const isLast = i === PERFORMERS.length - 1;
          const initial = performer.name.charAt(0).toUpperCase();

          return (
            <div
              key={performer.name}
              ref={(el) => { sectionRefs.current[i] = el; }}
              className="relative w-full mb-[20vh] md:mb-[25vh]"
            >
              <div
                ref={(el) => { cardRefs.current[i] = el; }}
                className={`relative w-full md:w-[80%] flex flex-col md:flex-row items-center gap-8 md:gap-16 z-10 mx-auto ${isLeft ? "" : "md:flex-row-reverse"}`}
                style={{ opacity: 0, transform: "translateY(60px)" }}
              >
                <div className="relative w-full max-w-[340px] aspect-[3/4] shrink-0 overflow-hidden rounded-[2px] shadow-[0_20px_50px_rgba(0,0,0,0.6)]">
                  <div style={{ position: "absolute", inset: 0, backgroundColor: performer.accent }} />
                  {performer.image ? (
                    <img
                      src={performer.image}
                      alt={performer.name}
                      style={{
                        position: "absolute", inset: "4%", width: "92%", height: "92%",
                        objectFit: "cover", objectPosition: "center 15%",
                        borderRadius: "2px", boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
                      }}
                      loading="lazy"
                    />
                  ) : (
                    <div style={{
                      position: "absolute", inset: "4%", backgroundColor: "#0b0b0d",
                      borderRadius: "2px", display: "flex", alignItems: "center",
                      justifyContent: "center", boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
                    }}>
                      <span style={{ fontFamily: DISPLAY, fontSize: "clamp(4rem, 12vw, 8rem)", color: performer.accent, lineHeight: 1 }}>
                        {initial}
                      </span>
                    </div>
                  )}
                  <div
                    className="absolute inset-0 opacity-[0.08] mix-blend-overlay pointer-events-none"
                    style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")` }}
                  />
                </div>

                <div className={`flex flex-col flex-1 ${isLeft ? "md:items-start" : "md:items-end"} items-center text-center ${isLeft ? "md:text-left" : "md:text-right"}`}>
                  <h3
                    className="text-5xl md:text-7xl tracking-wide text-[#f4efe2]"
                    style={{ fontFamily: DISPLAY, lineHeight: 1.0, textShadow: "0 10px 30px rgba(0,0,0,0.8)" }}
                  >
                    {performer.name.toUpperCase()}
                  </h3>
                  <p
                    className="text-[#f4efe2] opacity-80 text-xl md:text-2xl font-bold tracking-[0.25em] mt-3 uppercase"
                    style={{ fontFamily: "system-ui, sans-serif" }}
                  >
                    {performer.year}
                  </p>
                </div>
              </div>

              {!isLast && !isMobile && (
                <svg
                  viewBox="0 0 1000 600"
                  preserveAspectRatio="none"
                  className="absolute top-[75%] left-0 w-full overflow-visible pointer-events-none"
                  style={{ height: "30vh", zIndex: 0 }}
                >
                  <path
                    ref={(el) => { pathRefs.current[i] = el; }}
                    d={pathFor(isLeft)}
                    fill="none"
                    stroke="#b9ae86"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </div>
          );
        })}
      </div>

      <div className="fixed top-8 left-8 z-50">
        <Link
          href="/"
          className="text-[#f4efe2] opacity-50 hover:opacity-100 transition-opacity uppercase tracking-widest text-sm font-bold drop-shadow-md"
          style={{ fontFamily: "system-ui, sans-serif" }}
        >
          ← BACK TO STAGE
        </Link>
      </div>
    </section>
  );
}
