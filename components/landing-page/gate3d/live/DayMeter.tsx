// Fluid day meter: a rail spanning first-act start → last-act end. Fill,
// NOW pin, ticks and focus handle all derive from ONE fraction `p` computed
// with meterFraction — fill is a full-width element with transform
// scaleX(p) (origin left), marker/ticks/handle sit at left: calc(p*100%),
// so fill and pin cannot disagree. The liquid feel is a subtle sheen
// strip gliding inside the clipped fill (transform-only, parked while the
// tab is hidden, absent under prefers-reduced-motion). Ticks mark act
// starts (tap focuses the act); close ones merge into a cluster.
"use client";
import React, { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "motion/react";
import type { TimelineEvent } from "./types";
import { deriveStatus, formatShortIST, meterFraction } from "./timelineMath";

const GOLD = "#ffc24b";
/** Ticks closer than this (px) merge into one cluster. */
const CLUSTER_PX = 12;

function useHidden(): boolean {
  const [hidden, setHidden] = useState(false);
  useEffect(() => {
    const onVis = () => setHidden(document.hidden);
    setHidden(document.hidden);
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);
  return hidden;
}

function useRailWidth(): {
  ref: React.RefObject<HTMLDivElement>;
  width: number;
} {
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const measure = () => setWidth(el.clientWidth);
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return { ref, width };
}

/** Subtle travelling sheen inside the fill — a gradient strip looping
 *  across on transform only. Clipped by the fill's own rounded box. */
function Sheen({ paused }: { paused: boolean }): React.ReactElement {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-y-0 overflow-hidden rounded-full"
      style={{ left: 0, right: 0 }}
    >
      <div
        className="h-full w-1/3"
        style={{
          background:
            "linear-gradient(100deg, transparent 0%, rgba(255,244,220,0.35) 50%, transparent 100%)",
          animation: paused ? "none" : "meter-sheen 3.2s ease-in-out infinite",
        }}
      />
    </div>
  );
}

interface Tick {
  key: string;
  /** First act id in the cluster (tap target). */
  id: string;
  /** Fraction along the rail. */
  frac: number;
  kind: "past" | "upcoming" | "live";
  label: string;
}

export default function DayMeter({
  events,
  nowMs,
  focusStartMs,
  onTick,
}: {
  /** Full start-sorted schedule (the whole day, not the wall window). */
  events: TimelineEvent[];
  nowMs: number;
  /** Start time of the focused act (outlined handle), or null. */
  focusStartMs: number | null;
  /** Tap a tick → focus that act on the wall. */
  onTick: (id: string) => void;
}): React.ReactElement {
  const reduce = useReducedMotion();
  const hidden = useHidden();
  const { ref: railRef, width } = useRailWidth();
  if (events.length === 0) return <></>;
  const starts = events.map((e) => Date.parse(e.startTime));
  const ends = events.map((e) => Date.parse(e.endTime));
  const dayStart = Math.min(...starts);
  const dayEnd = Math.max(...ends, ...starts);
  const frac = (ms: number) => meterFraction(ms, dayStart, dayEnd);
  const fill = frac(nowMs);

  // cluster ticks closer than CLUSTER_PX (measured rail width)
  const ticks: Tick[] = [];
  const items = events
    .map((e) => {
      const st = deriveStatus(e, nowMs);
      if (st === "cancelled") return null; // hidden, per spec
      return {
        e,
        frac: frac(Date.parse(e.startTime)),
        kind:
          st === "live" || st === "delayed"
            ? ("live" as const)
            : st === "done"
              ? ("past" as const)
              : ("upcoming" as const),
      };
    })
    .filter((x): x is NonNullable<typeof x> => x !== null)
    .sort((a, b) => a.frac - b.frac);
  let cluster: typeof items = [];
  const flush = () => {
    if (cluster.length === 0) return;
    const first = cluster[0];
    const kind = cluster.some((c) => c.kind === "live")
      ? "live"
      : cluster.some((c) => c.kind === "upcoming")
        ? "upcoming"
        : "past";
    ticks.push({
      key: cluster.map((c) => c.e.id).join("+"),
      id: first.e.id,
      frac: first.frac,
      kind,
      label:
        cluster.length > 1
          ? `${cluster.length} acts from ${first.e.artist}`
          : first.e.artist,
    });
    cluster = [];
  };
  for (const item of items) {
    const last = cluster[cluster.length - 1];
    if (
      last &&
      width > 0 &&
      Math.abs(item.frac - last.frac) * width < CLUSTER_PX
    ) {
      cluster.push(item);
    } else {
      flush();
      cluster = [item];
    }
  }
  flush();

  // NOW pill label stays inside the rail (clamped); the dot sits exact
  const pinFrac = Math.min(0.88, Math.max(0.12, fill));

  return (
    <div className="mt-3">
      <div className="relative">
        {/* NOW pill with stem — above ticks, never overlapped */}
        <div
          className="pointer-events-none absolute -top-1 z-10 flex -translate-x-1/2 flex-col items-center"
          style={{ left: `calc(${pinFrac * 100}%)` }}
          aria-hidden
        >
          <span
            className="rounded px-1.5 py-0.5 text-[14px] font-bold tabular-nums"
            style={{ background: GOLD, color: "#0a0a0a" }}
          >
            {formatShortIST(new Date(nowMs).toISOString())}
          </span>
          <span
            className="block h-[7px] w-[2px]"
            style={{ background: GOLD }}
          />
        </div>
        <div
          ref={railRef}
          className="relative mt-7 h-[32px]"
          role="progressbar"
          aria-label="Day progress"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(fill * 100)}
        >
          {/* rail, clipped — nothing escapes it */}
          <div
            className="absolute inset-x-0 top-1/2 h-[8px] -translate-y-1/2 overflow-hidden rounded-full"
            style={{ background: "rgba(244,239,226,0.14)" }}
          >
            {/* liquid fill — full-width element scaled from the left, so
                its leading edge lands EXACTLY on the NOW position */}
            <div
              className="absolute inset-y-0 left-0 w-full origin-left rounded-full"
              style={{
                transform: `scaleX(${fill})`,
                background: `linear-gradient(90deg, #b97a1e, ${GOLD})`,
                transition: "transform 1000ms linear",
              }}
            >
              {!reduce && <Sheen paused={hidden} />}
            </div>
          </div>
          {/* NOW marker dot, exact same fraction */}
          <span
            className="pointer-events-none absolute top-1/2 h-[14px] w-[14px] -translate-x-1/2 -translate-y-1/2 rounded-full"
            style={{
              left: `calc(${fill * 100}%)`,
              background: GOLD,
              boxShadow: "0 0 10px rgba(255,194,75,0.9)",
            }}
            aria-hidden
          />
          {/* focused-act handle (outlined), rides the scrub */}
          {focusStartMs !== null && Number.isFinite(focusStartMs) && (
            <span
              className="pointer-events-none absolute top-1/2 h-[16px] w-[16px] -translate-x-1/2 -translate-y-1/2 rounded-full"
              style={{
                left: `calc(${frac(focusStartMs) * 100}%)`,
                background: "transparent",
                border: "2px solid #f4efe2",
                boxShadow: "0 0 8px rgba(244,239,226,0.5)",
              }}
              aria-hidden
            />
          )}
          {/* act-start ticks: 7px dots, high-contrast rings, 32px targets */}
          {ticks.map((t) => (
            <button
              key={t.key}
              onClick={() => onTick(t.id)}
              aria-label={`Focus ${t.label} on the wall`}
              title={t.label}
              className="absolute top-1/2 flex h-8 w-8 -translate-x-1/2 -translate-y-1/2 items-center justify-center"
              style={{ left: `calc(${t.frac * 100}%)` }}
            >
              <span
                aria-hidden
                className="block h-[7px] w-[7px] rounded-full"
                style={
                  t.kind === "live"
                    ? {
                        background: GOLD,
                        boxShadow:
                          "0 0 0 2px #0b0c10, 0 0 0 3.5px rgba(255,194,75,0.9), 0 0 8px rgba(255,194,75,0.9)",
                      }
                    : t.kind === "upcoming"
                      ? {
                          background: "transparent",
                          boxShadow:
                            "0 0 0 2px #0b0c10, 0 0 0 3.5px rgba(244,239,226,0.85)",
                        }
                      : {
                          background: "rgba(244,239,226,0.4)",
                          boxShadow:
                            "0 0 0 2px #0b0c10, 0 0 0 3.5px rgba(244,239,226,0.35)",
                        }
                }
              />
            </button>
          ))}
        </div>
        {/* rail end labels sit directly under the ends */}
        <div className="mt-0.5 flex items-baseline justify-between gap-2">
          <span
            className="text-[12px] font-semibold tabular-nums"
            style={{ color: "rgba(244,239,226,0.55)" }}
          >
            {formatShortIST(new Date(dayStart).toISOString())}
          </span>
          <span
            className="text-[12px] font-semibold tabular-nums"
            style={{ color: "rgba(244,239,226,0.55)" }}
          >
            {formatShortIST(new Date(dayEnd).toISOString())}
          </span>
        </div>
      </div>
    </div>
  );
}
