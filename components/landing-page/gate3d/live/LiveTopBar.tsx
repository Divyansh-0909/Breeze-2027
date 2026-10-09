// Top bar for Live mode: Back (left), current time (center), List/3D
// toggle (right). One row, no wrapping at 360px: tight grid with safe-area
// insets. The spray "Live" mark sits next to the clock, clear of the
// toggle. Absolute top; the gallery posters are framed below it.
"use client";
import React from "react";
import { formatClockShort } from "./timelineMath";
import RollDigits from "./RollDigits";

const CREAM = "#f4efe2";
const GOLD = "#ffc24b";
const SPRAY = "'Aerosoldier', 'Impact', 'Arial Black', sans-serif";

export default function LiveTopBar({
  nowMs,
  simple,
  onToggleSimple,
  onBack,
}: {
  nowMs: number;
  simple: boolean;
  onToggleSimple: () => void;
  onBack: () => void;
}): React.ReactElement {
  const clock = formatClockShort(nowMs);
  return (
    <div
      className="pointer-events-none absolute inset-x-0 top-0 z-[60] grid grid-cols-[auto_1fr_auto] items-center gap-1.5 px-3 pb-2"
      style={{
        paddingTop: "max(0.75rem, env(safe-area-inset-top))",
        paddingLeft: "max(0.75rem, env(safe-area-inset-left))",
        paddingRight: "max(0.75rem, env(safe-area-inset-right))",
      }}
    >
      <button
        onClick={onBack}
        aria-label="Back to menu"
        data-testid="live-back"
        className="pointer-events-auto shrink-0 whitespace-nowrap rounded-md px-2.5 py-1.5 text-[14px] font-bold"
        style={{
          color: GOLD,
          background: "rgba(11,12,16,0.92)",
          border: "1px solid rgba(255,194,75,0.45)",
        }}
      >
        ← Back
      </button>
      <div className="flex min-w-0 items-baseline justify-center gap-2 whitespace-nowrap">
        <RollDigits
          value={clock}
          className="text-[16px] font-bold tabular-nums"
          style={{ color: CREAM }}
          label={`Current time ${clock} IST`}
        />
        <span
          aria-hidden
          className="shrink-0 text-[24px] leading-none"
          style={{ fontFamily: SPRAY, color: "#ff6b61" }}
        >
          Live
        </span>
      </div>
      <button
        onClick={onToggleSimple}
        aria-pressed={simple}
        aria-label={simple ? "Show 3D view" : "Show simple list view"}
        data-testid="live-view-toggle"
        title={simple ? "3D view" : "Simple view"}
        className="pointer-events-auto shrink-0 whitespace-nowrap rounded-md px-2 py-1 text-[14px] font-bold"
        style={{
          color: CREAM,
          background: "rgba(11,12,16,0.92)",
          border: "1px solid rgba(244,239,226,0.35)",
        }}
      >
        {simple ? "◈ 3D" : "☰ List"}
      </button>
    </div>
  );
}
