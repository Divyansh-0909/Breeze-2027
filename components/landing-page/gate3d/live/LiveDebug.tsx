// Debug panel: time simulator + chaos buttons. Mounted only when
// `?debug=1` is present (or NODE_ENV is development). Never ships to
// production visitors — the parent gates on the flag, not this component.
"use client";
import React, { useState } from "react";
import type { TimelineApi } from "./useTimeline";
import { MOCK_RANGE } from "./mockEvents";

const SANS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";

export default function LiveDebug({
  api,
}: {
  api: TimelineApi;
}): React.ReactElement {
  const [msg, setMsg] = useState("Doors are open, Gullyverse!");
  const sliderVal = api.sim.scrubTo ?? api.nowMs;
  return (
    <div
      className="absolute bottom-0 left-0 z-40 m-3 w-[280px] rounded-lg p-3 text-[12px]"
      data-live-ui
      style={{
        fontFamily: SANS,
        background: "rgba(10,10,14,0.92)",
        border: "1px dashed rgba(255,194,75,0.6)",
        color: "#f4efe2",
      }}
      role="complementary"
      aria-label="Timeline debug panel"
    >
      <p className="mb-2 font-bold uppercase tracking-[0.2em] text-[#ffc24b]">
        Debug · time sim
      </p>
      <div className="mb-2 flex gap-1.5">
        <button
          onClick={() => api.setPaused(!api.sim.paused)}
          className="rounded bg-white/10 px-2 py-1 font-bold"
          aria-pressed={api.sim.paused}
        >
          {api.sim.paused ? "▶ Play" : "⏸ Pause"}
        </button>
        {([1, 60, 600] as const).map((s) => (
          <button
            key={s}
            onClick={() => api.setSpeed(s)}
            className="rounded px-2 py-1 font-bold"
            style={{
              background: api.sim.speed === s ? "#ffc24b" : "rgba(255,255,255,0.1)",
              color: api.sim.speed === s ? "#000" : "#f4efe2",
            }}
          >
            {s}x
          </button>
        ))}
      </div>
      <label className="mb-1 block opacity-80">
        Jump to time ({new Date(sliderVal).toLocaleTimeString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
        })}{" "}
        IST)
        <input
          type="range"
          min={MOCK_RANGE.min}
          max={MOCK_RANGE.max}
          step={60000}
          value={Math.min(Math.max(sliderVal, MOCK_RANGE.min), MOCK_RANGE.max)}
          onChange={(e) => api.scrubToTime(Number(e.target.value))}
          className="w-full"
        />
      </label>
      <div className="mb-2 flex gap-1.5">
        <button
          onClick={() => api.scrubToTime(null)}
          className="rounded bg-white/10 px-2 py-1"
        >
          Release hold
        </button>
        <button
          onClick={() => api.resumeLive()}
          className="rounded bg-white/10 px-2 py-1"
        >
          Resume live
        </button>
      </div>
      <div className="mb-2 flex flex-col gap-1.5">
        <button
          onClick={() => api.next && api.delayEvent(api.next.id, 15)}
          className="rounded bg-white/10 px-2 py-1 text-left"
        >
          Delay next act by 15 min
        </button>
        <button
          onClick={() => api.live[0] && api.cancelEvent(api.live[0].ev.id)}
          className="rounded bg-white/10 px-2 py-1 text-left"
        >
          Cancel current act
        </button>
        <div className="flex gap-1.5">
          <input
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
            className="min-w-0 flex-1 rounded bg-white/10 px-2 py-1 text-white"
            aria-label="Announcement message"
          />
          <button
            onClick={() => msg.trim() && api.pushAnnouncement(msg.trim())}
            className="shrink-0 rounded bg-white/10 px-2 py-1"
          >
            Announce
          </button>
        </div>
      </div>
      <p className="opacity-60">
        now={new Date(api.nowMs).toISOString()}
        {api.sim.scrubTo !== null ? " (held)" : ""}
      </p>
    </div>
  );
}
