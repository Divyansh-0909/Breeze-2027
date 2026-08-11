"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import { NIGHT, SIGN } from "./palette";

/**
 * What you fly toward, and what you get when the flight lands: the way on, then
 * a hand-off to the site's ordinary chrome.
 *
 * With the ground past the mouth kept empty for now, the menu IS the arrival
 * — a centred block of big Aerosoldier over an editorial grid of indexes and
 * hairlines. The graffiti lives in the letterforms and nowhere else: no fake
 * strokes, no lean, no drips. One face doing the talking over a disciplined
 * grid reads as designed; effects fighting on every word read as a costume.
 *
 * It has no entrance of its own. `blockRef` is handed to `MenuAnchor` in
 * GateHero, which parks this block on a point in the world just past the
 * tunnel's mouth and drives its position and scale off the camera every frame
 * — so it is standing down there from the moment you set off, small and far,
 * and the whole flight is you closing on it. Anything animating in on top of
 * that would be the pop-in this replaced, wearing a longer coat.
 *
 * What it does own: standing down. The first time you try to move the page the
 * menu bows out and the real `Navbar` docks at the top, so every route after
 * this behaves like the rest of the site.
 *
 * Plain CSS transitions on purpose, for the same reason the "click to continue"
 * line is: this is the only route out of the entry scene, and it must never
 * depend on a JS animation resolving to become visible or clickable.
 */

const CREAM = "#f4efe2"; // the posters' paper, the resting colour of the type
const RULE = "rgba(244,239,226,0.22)"; // hairlines, cream knocked back

// Aerosoldier carries the whole graffiti register by itself; Satoshi does the
// quiet work (indexes, eyebrow) so the display face has something to be loud
// against. Impact stays behind Aerosoldier so a failed OTF still gives a
// heavy word, not a serif.
const DISPLAY = "'Aerosoldier', 'Impact', 'Arial Black', system-ui, sans-serif";
const UTILITY = "'Satoshi', system-ui, sans-serif";

const LINKS = [
  // first because it's the payoff: the aftermovie is the thing worth arriving
  // for, and clicking it takes you to the stage page
  { name: "Aftermovie", href: "/aftermovie" },
  { name: "Team", href: "/team" },
  { name: "Contact", href: "/get-in-touch" },
] as const;

/** Drawn arrow, so the hover affordance can't fall back to an emoji glyph. */
function Arrow(): React.ReactElement {
  return (
    <svg
      aria-hidden
      viewBox="0 0 20 20"
      className="h-[20px] w-[20px] shrink-0 -translate-x-1 opacity-0 transition-[transform,opacity] duration-300 ease-out group-hover:translate-x-0 group-hover:opacity-100 group-focus-visible:translate-x-0 group-focus-visible:opacity-100 motion-reduce:transition-none md:h-[26px] md:w-[26px]"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 17 17 3M7 3h10v10" />
    </svg>
  );
}

export default function EntryNav({
  arrived,
  departing = false,
  onDepart,
  blockRef,
  shadeRef,
}: {
  /** False while the camera is still on its way to it. */
  arrived: boolean;
  /** True once a link has been picked and the camera is walking out. */
  departing?: boolean;
  /**
   * Hands the destination to GateHero, which walks the camera through this
   * block and out of the tunnel before changing route. Optional: without it
   * the links are ordinary links and still work, which is the point — the
   * only way out of the entry scene must not depend on a camera move.
   */
  onDepart?: (href: string) => void;
  blockRef: React.RefObject<HTMLDivElement>;
  shadeRef: React.RefObject<HTMLDivElement>;
}): React.ReactElement {
  const [docked, setDocked] = useState(false);

  // any attempt to move the page stands the menu down. `scroll` alone isn't
  // enough — the entry scene is exactly one viewport tall, so a wheel gesture
  // over it never actually scrolls anything and never fires.
  //
  // Not armed until the flight lands: mid-flight the menu is a distant object
  // and there is nothing to stand down from, so a stray wheel tick on the way
  // in would throw away the arrival before it happened.
  // Once the walk out has started there is nothing left to stand down from,
  // and a stray wheel tick would blank the menu out from under a camera move
  // that is still passing through it.
  useEffect(() => {
    if (docked || !arrived || departing) return;
    const dock = () => setDocked(true);
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" || e.key === "PageDown" || e.key === "ArrowDown") dock();
    };
    const opts = { passive: true } as const;
    window.addEventListener("wheel", dock, opts);
    window.addEventListener("touchmove", dock, opts);
    window.addEventListener("scroll", dock, opts);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("wheel", dock);
      window.removeEventListener("touchmove", dock);
      window.removeEventListener("scroll", dock);
      window.removeEventListener("keydown", onKey);
    };
  }, [docked, arrived, departing]);

  /**
   * Holds the navigation back so the camera can walk out first.
   *
   * Everything that isn't a plain left click is left to the browser — a middle
   * click or ctrl-click means "open this somewhere else", and swallowing it to
   * play a camera move in a tab the visitor is leaving anyway is the kind of
   * thing that makes a nice transition into an annoying one. The `href` stays
   * real for the same reason it always was: right-click-copy, prefetch, and
   * the no-JS case all keep working.
   */
  const walkOut = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    if (!onDepart) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault();
    onDepart(href);
  };

  return (
    <>
      {docked && (
        <div className="pointer-events-auto animate-in fade-in duration-500">
          <Navbar />
        </div>
      )}

      {/* a centred well of shade for the type to sit in — broad and soft, so
          the tunnel mouth and the night still read around it. Two nested nodes
          because two things fade it independently: the approach ramps it in
          (inner, driven per-frame by MenuAnchor) and docking takes it away
          (outer) — on one node the later writer would stamp on the other. */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 transition-opacity duration-700 motion-reduce:transition-none"
        style={{ opacity: docked ? 0 : 1 }}
      >
        <div
          ref={shadeRef}
          className="absolute inset-0"
          // Tight and light. It exists to seat the type against the night past
          // the mouth, not to black the shot out — the graffiti down both sides
          // is what the flight was for, and a broad 0.8 scrim erases it and
          // leaves an arrival that could have happened anywhere.
          style={{
            opacity: 0,
            background:
              "radial-gradient(34% 40% at 50% 50%, rgba(3,4,8,0.55) 0%, rgba(3,4,8,0.3) 60%, rgba(3,4,8,0) 100%)",
          }}
        />
      </div>

      <nav
        aria-label="Enter the fest"
        className="absolute inset-0 flex items-center justify-center px-6 transition-opacity duration-500 motion-reduce:transition-none"
        style={{
          opacity: docked ? 0 : 1,
          // dead to the pointer until the flight lands: while it is a distant
          // sign at the end of the tunnel, a click on it is a mis-click. Dead
          // again the moment one is picked, so a second click during the walk
          // out can't queue a second destination behind the first.
          pointerEvents: docked || !arrived || departing ? "none" : "auto",
        }}
        // out of the tab order both before the menu has arrived and after it
        // has stood down — either way these are links nobody can see
        inert={docked || !arrived || departing}
      >
        <div
          ref={blockRef}
          className="w-[min(92vw,560px)] md:w-[720px]"
          // seeded so the block can never flash at full size in the frame
          // before MenuAnchor's first write; both are overwritten every frame
          style={{ opacity: 0, transform: "scale(0.05)", willChange: "transform" }}
        >
          <p
            className="mb-4 text-[12px] font-bold uppercase md:text-[13px]"
            style={{
              fontFamily: UTILITY,
              color: NIGHT.gold,
              letterSpacing: "0.42em",
            }}
          >
            {SIGN.theme}
            <span className="ml-3" style={{ color: "rgba(244,239,226,0.4)" }}>
              Breeze 2027
            </span>
          </p>

          <ul style={{ borderTop: `1px solid ${RULE}` }}>
            {LINKS.map((link, i) => (
              <li key={link.href} style={{ borderBottom: `1px solid ${RULE}` }}>
                <Link
                  href={link.href}
                  onClick={(e) => walkOut(e, link.href)}
                  // the wide index channel is load-bearing: Aerosoldier's
                  // opening swashes reach well left of the glyph box, and on a
                  // tighter gutter the T of "Team" lands on its own number
                  className="group flex items-center gap-8 py-5 outline-none md:gap-12 md:py-7"
                >
                  <span
                    className="w-8 text-[12px] font-bold tabular-nums transition-colors duration-300 md:text-[14px]"
                    style={{
                      fontFamily: UTILITY,
                      color: "rgba(244,239,226,0.38)",
                      letterSpacing: "0.1em",
                    }}
                  >
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <span
                    className="text-[44px] leading-none transition-[color,transform] duration-300 ease-out group-hover:translate-x-2 group-hover:text-[color:var(--hot)] group-focus-visible:translate-x-2 group-focus-visible:text-[color:var(--hot)] motion-reduce:transition-none sm:text-[62px] md:text-[84px]"
                    style={
                      {
                        fontFamily: DISPLAY,
                        color: CREAM,
                        "--hot": NIGHT.gold,
                        textShadow: "0 3px 30px rgba(0,0,0,0.9)",
                      } as React.CSSProperties
                    }
                  >
                    {link.name}
                  </span>
                  <span
                    className="ml-auto transition-colors duration-300 group-hover:text-[color:var(--hot)] group-focus-visible:text-[color:var(--hot)]"
                    style={{ color: CREAM, "--hot": NIGHT.gold } as React.CSSProperties}
                  >
                    <Arrow />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>
    </>
  );
}
