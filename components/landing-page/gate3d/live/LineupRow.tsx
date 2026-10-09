// One row design shared by the List fallback and the Full lineup drawer:
// fixed-width time column, 17–18px name, status text on the right only for
// NOW / CANCELLED / DELAYED, and a small muted second line (stage +
// countdown, no repeated times, no "Over · time"). Solid colors throughout.
"use client";
import React from "react";
import type { TimelineEvent } from "./types";
import type { DerivedStatus } from "./types";
import { formatCountdownShort, formatShortIST } from "./timelineMath";

const CREAM = "#f4efe2";

function leftText(ms: number): string {
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  if (m >= 5) return `${m} min left`;
  if (m >= 1) return `${m}m ${s}s left`;
  if (ms <= 0) return "ending now";
  return `${s}s left`;
}

export default function LineupRow({
  ev,
  status,
  nowMs,
  onSelect,
}: {
  ev: TimelineEvent;
  status: DerivedStatus;
  nowMs: number;
  onSelect: (id: string) => void;
}): React.ReactElement {
  const isLive = status === "live" || status === "delayed";
  const muted = status === "done" || status === "cancelled";
  const sub =
    isLive
      ? `${ev.stage} · ${leftText(Date.parse(ev.endTime) - nowMs)}`
      : status === "upcoming"
        ? `${ev.stage} · in ${formatCountdownShort(Date.parse(ev.startTime) - nowMs)}`
        : ev.stage;
  return (
    <button
      onClick={() => onSelect(ev.id)}
      className="grid w-full grid-cols-[86px_1fr_auto] items-baseline gap-x-3 px-3 py-2.5 text-left"
      style={
        isLive
          ? {
              background: "#1a1408",
              borderLeft: "3px solid #ffc24b",
            }
          : undefined
      }
    >
      <span
        className="text-[14px] font-semibold tabular-nums"
        style={{ color: "#ffc24b" }}
      >
        {formatShortIST(ev.startTime)}
      </span>
      <span className="min-w-0">
        <span
          className="block truncate text-[17px] font-semibold"
          style={{
            color: muted ? "rgba(244,239,226,0.55)" : CREAM,
            textDecoration: status === "cancelled" ? "line-through" : "none",
          }}
        >
          {isLive && (
            <span
              className="mr-1.5 inline-block h-2 w-2 animate-pulse rounded-full bg-red-500"
              aria-label="live"
            />
          )}
          {ev.artist}
        </span>
        <span
          className="block truncate text-[14px]"
          style={{ color: "rgba(244,239,226,0.6)" }}
        >
          {sub}
        </span>
      </span>
      <span
        className="shrink-0 text-[14px] font-bold uppercase"
        style={{
          color:
            status === "live"
              ? "#ff6b61"
              : status === "delayed"
                ? "#ffc24b"
                : "rgba(244,239,226,0.5)",
          letterSpacing: "0.08em",
        }}
      >
        {status === "live"
          ? "Now"
          : status === "delayed"
            ? "Delayed"
            : status === "cancelled"
              ? "Cancelled"
              : ""}
      </span>
    </button>
  );
}
