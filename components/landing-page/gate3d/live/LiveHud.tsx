// The Live Timeline's single information card: bottom-anchored, solid, and
// always describing the FOCUSED poster (screen centre) — follow mode keeps
// it on the live act, scrub mode moves it. State badge, stage badge, name,
// time range, context line, slim progress (live only), THEN/NEXT row, the
// fluid day meter, and the Full lineup button. Clean sans throughout —
// the spray face lives only on the top bar's "Live" mark and the menu item.
"use client";
import React, { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import type { TimelineApi } from "./useTimeline";
import type { DerivedStatus } from "./types";
import {
  deriveStatus,
  formatAgo,
  formatCountdownShort,
  formatShortIST,
  selectNextIndex,
} from "./timelineMath";
import LiveEmpty from "./LiveEmpty";
import DayMeter from "./DayMeter";
import RollDigits from "./RollDigits";
import { clampSlot } from "./scrub";

const SANS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";
const CREAM = "#f4efe2";
const GOLD = "#ffc24b";
const CARD = "#0b0c10";
const DISMISS_KEY = "breeze-live-dismissed";
const SWIPE_HINT_KEY = "breeze-live-swipe-hint";

function readDismissed(): string[] {
  try {
    const v = window.localStorage.getItem(DISMISS_KEY);
    const p = v ? (JSON.parse(v) as unknown) : [];
    return Array.isArray(p) ? p.filter((x) => typeof x === "string") : [];
  } catch {
    return [];
  }
}

/** "43 min left" → "4m 12s left" under 5 minutes. */
function leftText(ms: number): string {
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  if (m >= 5) return `${m} min left`;
  if (m >= 1) return `${m}m ${s}s left`;
  if (ms <= 0) return "ending now";
  return `${s}s left`;
}

function stateBadge(status: DerivedStatus, isNext: boolean): string {
  switch (status) {
    case "live":
      return "Now";
    case "delayed":
      return "Delayed";
    case "upcoming":
      return isNext ? "Next" : "Upcoming";
    case "done":
      return "Over";
    case "cancelled":
      return "Cancelled";
  }
}

export default function LiveHud({
  api,
  settled,
  focusIdx,
  atLive,
  liveDir,
  onBackToLive,
  onFocusEvent,
  onOpenLineup,
  onHeight,
}: {
  api: TimelineApi;
  /** True once the camera has settled — the card fades in only then. */
  settled: boolean;
  /** Slot index of the focused (centred) poster. */
  focusIdx: number;
  /** False while scrubbed away from the live position. */
  atLive: boolean;
  /** Side the live position sits on: -1 left, +1 right. */
  liveDir: -1 | 0 | 1;
  onBackToLive: () => void;
  /** Focus an act on the wall (meter ticks, rows, also-live). */
  onFocusEvent: (id: string) => void;
  onOpenLineup: () => void;
  /** Reports the card's viewport-height fraction (camera framing). */
  onHeight?: (frac: number) => void;
}): React.ReactElement {
  const { alsoLive, next, nowMs } = api;
  const events = api.events;
  const focused = events[clampSlot(focusIdx, events.length)] ?? null;
  const fst = focused ? deriveStatus(focused, nowMs) : null;
  const isNext = !!focused && !!next && focused.id === next.id;
  // the act after the focused one — shared selector skips cancelled acts,
  // so a scrubbed-to-live poster never offers a dead slot as NEXT/THEN
  const afterEv =
    focused != null
      ? (() => {
          const i = selectNextIndex(events, nowMs, events.indexOf(focused), false);
          return i >= 0 ? events[i] : null;
        })()
      : null;
  const progress =
    focused && (fst === "live" || fst === "delayed")
      ? (() => {
          const s = Date.parse(focused.startTime);
          const e = Date.parse(focused.endTime);
          return e > s ? Math.min(1, Math.max(0, (nowMs - s) / (e - s))) : 0;
        })()
      : 0;

  // slim dismissible banner: latest active announcement only, above the card
  const [dismissed, setDismissed] = useState<string[]>(() => readDismissed());
  const banner =
    api.announcements.find((a) => !dismissed.includes(a.id)) ?? null;
  const dismissBanner = (id: string) => {
    setDismissed((prev) => {
      const nextDismissed = [...prev, id];
      try {
        window.localStorage.setItem(
          DISMISS_KEY,
          JSON.stringify(nextDismissed)
        );
      } catch {
        /* dismissal is a nicety */
      }
      return nextDismissed;
    });
  };

  // first-visit scrub hint, fading out after a few seconds and never again
  const [hint, setHint] = useState(false);
  useEffect(() => {
    let seen = false;
    try {
      seen = window.localStorage.getItem(SWIPE_HINT_KEY) === "1";
    } catch {
      seen = true;
    }
    if (seen || !settled) return;
    setHint(true);
    const t = window.setTimeout(() => {
      setHint(false);
      try {
        window.localStorage.setItem(SWIPE_HINT_KEY, "1");
      } catch {
        /* hint is a nicety */
      }
    }, 4000);
    return () => window.clearTimeout(t);
  }, [settled]);

  // report the card's viewport fraction so the camera can lift the poster
  // row above it; capped — the card never takes more than ~38% of the view
  const cardRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = cardRef.current;
    if (!el || !onHeight) return;
    const measure = () =>
      onHeight(
        Math.min(0.6, el.clientHeight / Math.max(1, window.innerHeight))
      );
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [onHeight]);

  if (events.length === 0) {
    return (
      <div className="w-full" style={{ fontFamily: SANS }}>
        <div
          className="pointer-events-auto mx-auto w-full max-w-md rounded-xl p-4 shadow-2xl"
          data-live-ui
          style={{ background: CARD, border: "1px solid rgba(244,239,226,0.18)" }}
        >
          <LiveEmpty kind="empty" />
        </div>
      </div>
    );
  }

  const context =
    !focused || fst === null
      ? ""
      : fst === "live" || fst === "delayed"
        ? leftText(Date.parse(focused.endTime) - nowMs)
        : fst === "upcoming"
          ? `in ${formatCountdownShort(Date.parse(focused.startTime) - nowMs)}`
          : fst === "done"
            ? `ended ${formatAgo(nowMs - Date.parse(focused.endTime))}`
            : "cancelled";

  return (
    <div
      className="w-full"
      style={{
        fontFamily: SANS,
        opacity: settled ? 1 : 0,
        transform: settled ? "none" : "translateY(14px)",
        transition: "opacity 320ms ease-out, transform 320ms ease-out",
      }}
    >
      {banner && (
        <div
          className="pointer-events-auto mx-auto mb-2 flex w-full max-w-md items-center gap-2 rounded-md border-l-4 px-3 py-2"
          data-live-ui
          style={{
            background: "#0b0c10",
            borderColor: "rgba(244,239,226,0.18)",
            borderLeftColor:
              banner.severity === "info" ? "#4a7dd6" : "#d0342a",
            color: CREAM,
          }}
          role="alert"
        >
          <p className="flex-1 text-[14px] font-semibold">{banner.message}</p>
          <button
            onClick={() => dismissBanner(banner.id)}
            aria-label="Dismiss announcement"
            className="shrink-0 rounded px-2 py-1 text-[14px] font-bold"
            style={{ color: CREAM, border: "1px solid rgba(244,239,226,0.35)" }}
          >
            ✕
          </button>
        </div>
      )}

      {!atLive && (
        <div className="pointer-events-auto mx-auto mb-2 flex w-full max-w-md justify-center">
          <button
            onClick={onBackToLive}
            className="rounded-full px-4 py-2 text-[15px] font-extrabold"
            style={{ background: GOLD, color: "#0a0a0a" }}
            aria-label="Back to the live act"
          >
            {liveDir < 0 ? "◀ Live" : "Live ▶"}
          </button>
        </div>
      )}

      <div
        ref={cardRef}
        className={`pointer-events-auto mx-auto w-full max-w-md rounded-xl p-4 shadow-2xl ${
          settled ? "" : "pointer-events-none"
        } max-h-[38vh] overflow-y-auto min-[900px]:grid min-[900px]:grid-cols-[1.15fr_1fr] min-[900px]:items-start min-[900px]:gap-x-5 [@media(max-height:719px)]:grid [@media(max-height:719px)]:grid-cols-[1.15fr_1fr] [@media(max-height:719px)]:items-start [@media(max-height:719px)]:gap-x-5`}
        data-live-ui
        style={{ background: CARD, border: "1px solid rgba(244,239,226,0.18)" }}
      >
        {focused && fst && (
          <div>
            <div className="flex flex-wrap items-center gap-1.5">
              <Badge
                className="text-[14px] font-bold uppercase"
                style={{
                  background:
                    fst === "live"
                      ? "#d0342a"
                      : fst === "delayed"
                        ? GOLD
                        : "rgba(255,194,75,0.12)",
                  color:
                    fst === "live"
                      ? "#f4efe2"
                      : fst === "delayed"
                        ? "#0a0a0a"
                        : GOLD,
                  border: "1px solid transparent",
                }}
              >
                {fst === "live" ? "● " : ""}
                {stateBadge(fst, isNext)}
              </Badge>
              <Badge className="border-[rgba(244,239,226,0.3)] bg-[rgba(244,239,226,0.08)] text-[14px] font-semibold text-[#f4efe2]">
                {focused.stage}
              </Badge>
            </div>
            <h2
              className="mt-1.5 text-[30px] font-extrabold leading-tight"
              style={{ color: CREAM }}
            >
              {focused.artist}
            </h2>
            {/* one merged line: range + context, never two time lines */}
            <p
              className="mt-0.5 text-[15px] font-semibold tabular-nums"
              style={{ color: GOLD }}
            >
              {formatShortIST(focused.startTime)} –{" "}
              {formatShortIST(focused.endTime)} ·{" "}
              <RollDigits
                value={context}
                label={`${focused.artist}: ${context}`}
              />
            </p>
            {(fst === "live" || fst === "delayed") && (
              <div
                className="mt-2 h-1.5 w-full overflow-hidden rounded-full"
                style={{ background: "rgba(244,239,226,0.16)" }}
                role="progressbar"
                aria-valuenow={Math.round(progress * 100)}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`${focused.artist} progress`}
              >
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.round(progress * 100)}%`,
                    background: fst === "delayed" ? GOLD : "#ff4b4b",
                  }}
                />
              </div>
            )}
            {alsoLive.length > 0 &&
              !alsoLive.some((a) => focused && a.ev.id === focused.id) && (
                <div className="mt-2 flex flex-wrap gap-1.5" aria-label="Also on now">
                  {alsoLive.map((a) => (
                    <button
                      key={a.ev.id}
                      onClick={() => onFocusEvent(a.ev.id)}
                      className="truncate rounded-full px-2.5 py-1 text-[14px] font-semibold"
                      style={{
                        color: CREAM,
                        background: "rgba(255,194,75,0.1)",
                        border: "1px solid rgba(255,194,75,0.35)",
                      }}
                    >
                      <span
                        className="mr-1.5 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-red-500"
                        aria-hidden
                      />
                      {a.ev.artist}
                    </button>
                  ))}
                </div>
              )}
          </div>
        )}

        {/* secondary row: NEXT under a live focus, otherwise THEN */}
        {afterEv && focused && (
          <button
            onClick={() => onFocusEvent(afterEv.id)}
            className="mt-3 flex w-full items-baseline justify-between gap-2 border-t pt-3 text-left min-[900px]:mt-0 min-[900px]:border-t-0 min-[900px]:pt-0 [@media(max-height:719px)]:mt-0 [@media(max-height:719px)]:border-t-0 [@media(max-height:719px)]:pt-0"
            style={{ borderColor: "rgba(244,239,226,0.16)" }}
          >
            <span className="min-w-0">
              <span
                className="block text-[14px] font-bold uppercase"
                style={{
                  color: "rgba(244,239,226,0.65)",
                  letterSpacing: "0.18em",
                }}
              >
                {fst === "live" || fst === "delayed" ? "Next" : "Then"}
              </span>
              <span
                className="block truncate text-[17px] font-bold"
                style={{ color: CREAM }}
              >
                {afterEv.artist}
              </span>
            </span>
            <span
              className="shrink-0 text-right text-[14px] font-semibold tabular-nums"
              style={{ color: GOLD }}
            >
              {formatShortIST(afterEv.startTime)}
            </span>
          </button>
        )}

        {/* fluid day meter */}
        <div className="min-[900px]:col-span-2 [@media(max-height:719px)]:col-span-2">
          <DayMeter
            events={events}
            nowMs={nowMs}
            focusStartMs={
              !atLive && focused ? Date.parse(focused.startTime) : null
            }
            onTick={(id) => onFocusEvent(id)}
          />
        </div>

        {/* full lineup */}
        <div className="min-[900px]:col-span-2 [@media(max-height:719px)]:col-span-2">
          <button
            onClick={onOpenLineup}
            className="mt-3 w-full rounded-lg px-3 py-2.5 text-[15px] font-bold"
            style={{
              color: GOLD,
              background: "rgba(255,194,75,0.1)",
              border: "1px solid rgba(255,194,75,0.4)",
            }}
          >
            Full lineup →
          </button>

          {/* staleness only — the IST note lives in the list/drawer headers */}
          {api.stale && (
            <p
              className="mt-2 text-[12px]"
              style={{ color: "rgba(244,239,226,0.6)" }}
            >
              reconnecting… last update {formatShortIST(api.updatedAt)}
            </p>
          )}
        </div>
      </div>

      {hint && (
        <p
          className="pointer-events-none mx-auto mt-2 max-w-md text-center text-[14px] transition-opacity duration-700"
          style={{ color: "rgba(244,239,226,0.75)" }}
        >
          Swipe to browse · tap a tick to jump
        </p>
      )}
    </div>
  );
}
