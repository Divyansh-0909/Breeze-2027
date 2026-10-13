"use client";
import React from "react";

/**
 * The cover for the gap between clicking Aftermovie and the stage's first
 * frame — the three.js chunk is the heaviest download on the site, and until
 * it lands the page is otherwise a black void.
 *
 * It IS the moment it stands in for: a first-person walk through the scene's
 * own crowd, recorded from the 3D stage itself (`/flythrough-rec` renders it
 * frame by frame; see that page). The path ends exactly on the pov
 * composition `CameraRig` opens at, so the video plays ONCE and holds its
 * last frame — which is the live scene's first frame. However long the
 * stage's start-up takes behind it, the handover is a fade between two
 * identical images.
 *
 * No loop and no CSS motion on top: the recording carries its own camera
 * work, and anything layered on it would break that end-match.
 *
 * The clip is muted at the file level (no audio track) — it streams its
 * first frames in well under a second, and until then the copy sits on plain
 * black, which is what any video does before it opens anyway.
 */

const CREAM = "#f4efe2";
const GOLD = "#ffc24b";
const DISPLAY = "'Aerosoldier', 'Impact', 'Arial Black', system-ui, sans-serif";
const UTILITY = "'Satoshi', system-ui, sans-serif";

export default function TravelOverlay({
  done,
  onEnded,
}: {
  /** True once the stage is rendering — fades the overlay out. */
  done: boolean;
  /** Fires when the walk finishes (the video holds its last frame after). */
  onEnded?: () => void;
}): React.ReactElement {
  return (
    <div
      aria-hidden={done}
      className="absolute inset-0 z-20 overflow-hidden transition-opacity duration-1000 motion-reduce:transition-none"
      style={{
        backgroundColor: "#04050a",
        opacity: done ? 0 : 1,
        pointerEvents: done ? "none" : "auto",
      }}
    >
      <video
        className="absolute inset-0 h-full w-full object-cover"
        src="/travel-crowd.mp4"
        autoPlay
        muted
        playsInline
        preload="auto"
        onEnded={onEnded}
        // React has historically dropped the `muted` attribute from server
        // markup; setting it imperatively as well is what guarantees mobile
        // browsers let the autoplay through
        ref={(el) => {
          if (el) {
            el.muted = true;
            el.defaultMuted = true;
          }
        }}
      />

      {/* just enough top shade for the copy — the scene is already night, and
          darkening it further would make the fade to the live render visible */}
      <div
        aria-hidden
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(to bottom, rgba(4,5,10,0.5) 0%, rgba(4,5,10,0) 30%)",
        }}
      />

      <div
        role="status"
        className="absolute inset-x-0 flex flex-col items-center"
        style={{ top: "11%" }}
      >
        <p
          className="mb-3 text-[11px] font-bold uppercase md:text-[12px]"
          style={{ fontFamily: UTILITY, color: GOLD, letterSpacing: "0.42em" }}
        >
          Breeze 2027
        </p>
        <p
          className="text-[42px] leading-none md:text-[58px]"
          style={{
            fontFamily: DISPLAY,
            color: CREAM,
            textShadow: "0 3px 30px rgba(0,0,0,0.95)",
          }}
        >
          Main Stage
        </p>
        <p
          className="mt-4 animate-pulse text-[11px] font-bold uppercase motion-reduce:animate-none md:text-[12px]"
          style={{
            fontFamily: UTILITY,
            color: "rgba(244,239,226,0.6)",
            letterSpacing: "0.3em",
            textShadow: "0 2px 12px rgba(0,0,0,0.9)",
          }}
        >
          Making your way to the front
        </p>
      </div>

      <style>{`
        /* the push-in that makes handheld footage read first-person — slow,
           and alternating so the loop never visibly snaps back */
        .travel-push {
          animation: travel-push 10s ease-in-out infinite alternate;
        }
        @keyframes travel-push {
          from { transform: scale(1); }
          to { transform: scale(1.12); }
        }
        @media (prefers-reduced-motion: reduce) {
          .travel-push { animation: none; }
        }
      `}</style>
    </div>
  );
}
