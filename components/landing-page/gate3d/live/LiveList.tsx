// Low-power fallback: a solid, uncluttered full-screen panel — header
// clock + IST note, sticky NOW / LATER / Earlier sections, one shared row
// design. Tapping a row returns to 3D and focuses that act on the wall.
"use client";
import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Separator } from "@/components/ui/separator";
import type { TimelineApi } from "./useTimeline";
import {
  deriveStatus,
  formatClockShort,
  formatShortIST,
} from "./timelineMath";
import LineupRow from "./LineupRow";
import LiveEmpty from "./LiveEmpty";
import RollDigits from "./RollDigits";

const SANS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";
const CREAM = "#f4efe2";

export default function LiveList({
  api,
  onSwitchToAct,
}: {
  api: TimelineApi;
  /** Tap a row → back to 3D, wall scrubbed to that act and focused. */
  onSwitchToAct: (id: string) => void;
}): React.ReactElement {
  const { events, hero, nowMs } = api;
  const [earlierOpen, setEarlierOpen] = useState(false);

  const nowActs = events.filter((e) => {
    const s = deriveStatus(e, nowMs);
    return s === "live" || s === "delayed";
  });
  const laterActs = events.filter(
    (e) => deriveStatus(e, nowMs) === "upcoming"
  );
  const earlierActs = events.filter((e) => {
    const s = deriveStatus(e, nowMs);
    return s === "done" || s === "cancelled";
  });

  // land on NOW when the panel opens
  const anchorId = hero?.ev.id ?? api.next?.id ?? null;
  const rowRefs = useRef(new Map<string, HTMLDivElement>());
  useEffect(() => {
    const el = anchorId ? rowRefs.current.get(anchorId) : undefined;
    el?.scrollIntoView({ block: "center" });
  }, [anchorId]);

  const emptyKind = events.every((e) => deriveStatus(e, nowMs) === "done")
    ? "after"
    : "before";

  const setRef = (id: string) => (el: HTMLDivElement | null) => {
    if (el) rowRefs.current.set(id, el);
    else rowRefs.current.delete(id);
  };

  return (
    <div
      className="pointer-events-auto min-h-0 w-full flex-1 overflow-y-auto px-3 pb-4 pt-20"
      data-live-ui
      style={{ fontFamily: SANS, background: "#0b0c10" }}
    >
      <div className="mx-auto flex w-full max-w-md flex-col pb-2">
        {/* header: clock + the single IST note */}
        <div
          className="rounded-lg p-3"
          style={{
            background: "#0b0c10",
            border: "1px solid rgba(244,239,226,0.18)",
          }}
        >
          <RollDigits
            value={formatClockShort(nowMs)}
            className="text-[20px] font-extrabold tabular-nums"
            style={{ color: CREAM }}
            label={`Current time ${formatClockShort(nowMs)} IST`}
          />
          <p
            className="mt-0.5 text-[14px]"
            style={{ color: "rgba(244,239,226,0.6)" }}
          >
            All times IST
          </p>
        </div>

        {events.length === 0 && <LiveEmpty kind="empty" />}
        {events.length > 0 && nowActs.length === 0 && laterActs.length === 0 && (
          <LiveEmpty kind={emptyKind} />
        )}

        {nowActs.length > 0 && (
          <section aria-label="Now">
            <h3
              className="sticky top-0 z-10 -mx-3 bg-[#0b0c10] px-3 py-2 text-[14px] font-bold uppercase"
              style={{ color: "#ff6b61", letterSpacing: "0.18em" }}
            >
              Now · {formatShortIST(new Date(nowMs).toISOString())}
            </h3>
            <div
              className="overflow-hidden rounded-lg"
              style={{ border: "1px solid rgba(244,239,226,0.18)" }}
            >
              {nowActs.map((e, i) => (
                <React.Fragment key={e.id}>
                  {i > 0 && (
                    <Separator style={{ background: "rgba(244,239,226,0.12)" }} />
                  )}
                  <div ref={setRef(e.id)}>
                    <LineupRow
                      ev={e}
                      status={deriveStatus(e, nowMs)}
                      nowMs={nowMs}
                      onSelect={onSwitchToAct}
                    />
                  </div>
                </React.Fragment>
              ))}
            </div>
          </section>
        )}

        {laterActs.length > 0 && (
          <section aria-label="Later" className="mt-3">
            <h3
              className="sticky top-0 z-10 -mx-3 bg-[#0b0c10] px-3 py-2 text-[14px] font-bold uppercase"
              style={{ color: "rgba(244,239,226,0.65)", letterSpacing: "0.18em" }}
            >
              Later
            </h3>
            <div
              className="overflow-hidden rounded-lg"
              style={{ border: "1px solid rgba(244,239,226,0.18)" }}
            >
              {laterActs.map((e, i) => (
                <React.Fragment key={e.id}>
                  {i > 0 && (
                    <Separator style={{ background: "rgba(244,239,226,0.12)" }} />
                  )}
                  <div ref={setRef(e.id)}>
                    <LineupRow
                      ev={e}
                      status={deriveStatus(e, nowMs)}
                      nowMs={nowMs}
                      onSelect={onSwitchToAct}
                    />
                  </div>
                </React.Fragment>
              ))}
            </div>
          </section>
        )}

        {earlierActs.length > 0 && (
          <section aria-label="Earlier" className="mt-3">
            <button
              onClick={() => setEarlierOpen((o) => !o)}
              aria-expanded={earlierOpen}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left"
              style={{
                background: "rgba(244,239,226,0.05)",
                border: "1px solid rgba(244,239,226,0.14)",
              }}
            >
              <span
                className="text-[14px] font-bold uppercase"
                style={{ color: "rgba(244,239,226,0.65)", letterSpacing: "0.18em" }}
              >
                Earlier ({earlierActs.length})
              </span>
              <span
                aria-hidden
                className="text-[14px] font-bold"
                style={{ color: "rgba(244,239,226,0.65)" }}
              >
                {earlierOpen ? "▾" : "▸"}
              </span>
            </button>
            <AnimatePresence initial={false}>
              {earlierOpen && (
                <motion.div
                  key="earlier"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.22 }}
                  className="overflow-hidden"
                >
                  <div
                    className="mt-1.5 overflow-hidden rounded-lg"
                    style={{ border: "1px solid rgba(244,239,226,0.14)" }}
                  >
                    {earlierActs.map((e, i) => (
                      <React.Fragment key={e.id}>
                        {i > 0 && (
                          <Separator
                            style={{ background: "rgba(244,239,226,0.1)" }}
                          />
                        )}
                        <LineupRow
                          ev={e}
                          status={deriveStatus(e, nowMs)}
                          nowMs={nowMs}
                          onSelect={onSwitchToAct}
                        />
                      </React.Fragment>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </section>
        )}
      </div>
    </div>
  );
}
