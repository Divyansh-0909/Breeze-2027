// Full lineup drawer: the whole day chronologically in a bottom sheet.
// Past dimmed, live highlighted, upcoming normal; rows animate on schedule
// changes and the list auto-scrolls to now on open. Tapping a row closes
// the drawer and scrubs the wall to that act (the card shows its details).
// Built on the repo's existing Sheet + ScrollArea + Badge primitives.
"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import LiveEmpty from "./LiveEmpty";
import LineupRow from "./LineupRow";
import {
  deriveStatus,
  eventDayKey,
  eventDayLabel,
  formatShortIST,
} from "./timelineMath";
import type { TimelineApi } from "./useTimeline";

const CREAM = "#f4efe2";

export default function LineupDrawer({
  api,
  open,
  onOpenChange,
  onSelect,
}: {
  api: TimelineApi;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Tap a row → close the drawer, scrub the wall there, focus the act. */
  onSelect: (id: string) => void;
}): React.ReactElement {
  const { events, nowMs, days, hero, next } = api;
  // Day selector only when the schedule actually spans days. Defaults to
  // the day holding now (else the first day).
  const [day, setDay] = useState<string | null>(null);
  const activeDay = day ?? eventDayKey(events[0]?.startTime ?? "") ?? days[0] ?? null;
  const visible = useMemo(
    () =>
      activeDay
        ? events.filter((e) => eventDayKey(e.startTime) === activeDay)
        : events,
    [events, activeDay]
  );

  // auto-scroll to the live/next row once the sheet has slid in
  const anchorId = hero?.ev.id ?? next?.id ?? null;
  const rowRefs = useRef(new Map<string, HTMLDivElement>());
  useEffect(() => {
    if (!open) return;
    const t = window.setTimeout(() => {
      const el = anchorId ? rowRefs.current.get(anchorId) : undefined;
      el?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }, 380);
    return () => window.clearTimeout(t);
  }, [open, anchorId]);

  const emptyKind = events.every((e) => deriveStatus(e, nowMs) === "done")
    ? "after"
    : events.every(
        (e) =>
          deriveStatus(e, nowMs) === "upcoming" ||
          deriveStatus(e, nowMs) === "cancelled"
      )
      ? "before"
      : "empty";

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="bottom"
        className="mx-auto max-h-[82dvh] w-full max-w-xl rounded-t-2xl border-[rgba(244,239,226,0.18)] bg-[#0b0c10] p-0"
        aria-label="Full lineup"
      >
        <SheetHeader className="px-4 pb-2 pt-4 text-left">
          <SheetTitle
            className="text-[20px] font-extrabold"
            style={{ color: CREAM, fontFamily: "system-ui, sans-serif" }}
          >
            Full lineup
          </SheetTitle>
          <p
            className="px-4 text-[14px]"
            style={{ color: "rgba(244,239,226,0.6)" }}
          >
            All times IST
          </p>
          {days.length > 1 && (
            <div className="mt-2 flex gap-1.5" role="group" aria-label="Day">
              {days.map((d) => (
                <button
                  key={d}
                  onClick={() => setDay(d)}
                  aria-pressed={(activeDay ?? days[0]) === d}
                  className="rounded-md px-3 py-1.5 text-[14px] font-bold"
                  style={{
                    color: (activeDay ?? days[0]) === d ? "#0a0a0a" : CREAM,
                    background:
                      (activeDay ?? days[0]) === d
                        ? "#ffc24b"
                        : "rgba(244,239,226,0.1)",
                  }}
                >
                  {eventDayLabel(
                    events.find((e) => eventDayKey(e.startTime) === d)?.startTime ?? ""
                  )}
                </button>
              ))}
            </div>
          )}
        </SheetHeader>
        <ScrollArea className="max-h-[62dvh] px-2 pb-4">
          <div className="flex flex-col gap-1.5 px-2">
            {visible.length === 0 && <LiveEmpty kind="empty" />}
            {(visible.length === 0 ||
              visible.every((e) => {
                const s = deriveStatus(e, nowMs);
                return s !== "live" && s !== "delayed" && s !== "upcoming";
              })) &&
              visible.length > 0 && <LiveEmpty kind={emptyKind} />}
            <AnimatePresence initial={false}>
              {visible.map((e) => {
                const st = deriveStatus(e, nowMs);
                const dimmed = st === "done" || st === "cancelled";
                return (
                  <motion.div
                    key={e.id}
                    layout
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.22 }}
                    className="overflow-hidden rounded-lg"
                    ref={(el) => {
                      if (el) rowRefs.current.set(e.id, el);
                      else rowRefs.current.delete(e.id);
                    }}
                    style={{
                      background: "#0b0c10",
                      border: "1px solid rgba(244,239,226,0.14)",
                      opacity: dimmed ? 0.6 : 1,
                    }}
                  >
                    <LineupRow
                      ev={e}
                      status={st}
                      nowMs={nowMs}
                      onSelect={onSelect}
                    />
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
}
