// Pure timeline logic: status derivation, window selection and the
// non-linear wall-spacing curve. No React, no three — unit-testable.
import type { DerivedStatus, TimelineEvent } from "./types";

export function deriveStatus(
  ev: TimelineEvent,
  nowMs: number
): DerivedStatus {
  if (ev.status === "cancelled") return "cancelled";
  if (ev.status === "done") return "done";
  // Forced-live beats the clock; delayed still shows its (shifted) times.
  const start = Date.parse(ev.startTime);
  const end = Date.parse(ev.endTime);
  if (ev.status === "live") {
    if (Number.isFinite(end) && nowMs >= end) return "done";
    return "live";
  }
  if (!Number.isFinite(start) || !Number.isFinite(end)) return "upcoming";
  if (nowMs >= end) return "done";
  if (nowMs >= start) return ev.status === "delayed" ? "delayed" : "live";
  return ev.status === "delayed" ? "delayed" : "upcoming";
}

/** Fractional progress of a live act, 0..1. */
export function liveProgress(
  ev: TimelineEvent,
  nowMs: number
): number {
  const start = Date.parse(ev.startTime);
  const end = Date.parse(ev.endTime);
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start)
    return 0;
  return Math.min(1, Math.max(0, (nowMs - start) / (end - start)));
}

export interface WindowedEvent {
  ev: TimelineEvent;
  status: DerivedStatus;
}

/**
 * Render window: the most recent finished act, the current act(s) and
 * roughly the next five. The tunnel recycles this window — it never grows
 * geometry for the whole day.
 */
export function selectWindow(
  events: TimelineEvent[],
  nowMs: number,
  nextCount = 5
): WindowedEvent[] {
  const sorted = [...events].sort(
    (a, b) =>
      Date.parse(a.startTime) - Date.parse(b.startTime) ||
      a.sortOrder - b.sortOrder
  );
  const withStatus = sorted.map((ev) => ({ ev, status: deriveStatus(ev, nowMs) }));
  const liveIdx = withStatus.findIndex(
    (w) => w.status === "live" || w.status === "delayed"
  );
  if (liveIdx === -1) {
    // No live act: show the last done one (if any) plus what's next.
    const nextIdx = withStatus.findIndex((w) => w.status === "upcoming");
    if (nextIdx === -1) return withStatus.slice(-2);
    const from = Math.max(0, nextIdx - 1);
    return withStatus.slice(from, nextIdx + nextCount);
  }
  const from = Math.max(0, liveIdx - 1);
  return withStatus.slice(from, liveIdx + 1 + nextCount);
}

/**
 * Hero pick for overlapping live acts: the featured live act wins, else
 * the earliest-started one. Everything else concurrent goes to `also`.
 */
export function selectHero(
  live: { ev: TimelineEvent; status: DerivedStatus; progress: number }[]
): {
  hero: { ev: TimelineEvent; status: DerivedStatus; progress: number } | null;
  also: { ev: TimelineEvent; status: DerivedStatus; progress: number }[];
} {
  if (live.length === 0) return { hero: null, also: [] };
  const sorted = [...live].sort(
    (a, b) =>
      Date.parse(a.ev.startTime) - Date.parse(b.ev.startTime) ||
      a.ev.sortOrder - b.ev.sortOrder
  );
  const feat = sorted.find((l) => l.ev.featured === true);
  const hero = feat ?? sorted[0];
  return { hero, also: sorted.filter((l) => l.ev.id !== hero.ev.id) };
}

/**
 * Shared "what's next" selector: first slot after fromIdx that is NOT
 * cancelled. Done acts are included (scrubbing history walks through
 * them; lists mute them) — only cancelled is ever skipped.
 *
 * - Card THEN row: fromIdx = focusIdx.
 * - Hook `next` / poster NEXT ribbon / drawer anchor: fromIdx = -1 plus
 *   an upcoming-only filter (a live act is "now", never "next").
 */
export function selectNextIndex(
  sorted: TimelineEvent[],
  nowMs: number,
  fromIdx: number,
  onlyUpcoming = false
): number {
  for (let i = fromIdx + 1; i < sorted.length; i++) {
    const st = deriveStatus(sorted[i], nowMs);
    if (st === "cancelled") continue;
    if (onlyUpcoming && st !== "upcoming" && st !== "delayed") continue;
    return i;
  }
  return -1;
}

/**
 * Precomputed start/end table for `timelineCoord`, rebuilt only when the
 * event list changes — so the per-frame coordinate costs zero allocation.
 */
export interface SlotTable {
  starts: number[];
  ends: number[];
}

export function buildSlotTable(sorted: TimelineEvent[]): SlotTable {
  return {
    starts: sorted.map((e) => Date.parse(e.startTime)),
    ends: sorted.map((e) => Date.parse(e.endTime)),
  };
}

/**
 * Continuous timeline coordinate for the gallery wall: the act's slot
 * index plus drift — 0.35 of a slot across its own set, 0.65 across the
 * gap to the next start. Slots are equal-width (not proportional to
 * duration); real times are printed on the posters. Allocation-free.
 */
export function timelineCoord(slots: SlotTable, nowMs: number): number {
  const { starts, ends } = slots;
  const n = starts.length;
  if (n === 0) return 0;
  if (nowMs < starts[0]) {
    const span = (n > 1 ? starts[1] : NaN) - starts[0] || 3600000;
    return 0 - (starts[0] - nowMs) / span;
  }
  for (let i = 0; i < n; i++) {
    const nextStart = i + 1 < n ? starts[i + 1] : Infinity;
    if (nowMs < nextStart) {
      if (nowMs < starts[i]) return i; // shouldn't happen, stay pinned
      if (Number.isFinite(ends[i]) && nowMs <= ends[i] && ends[i] > starts[i])
        return i + 0.35 * ((nowMs - starts[i]) / (ends[i] - starts[i]));
      // in the gap (or past the end): ease across to the next slot
      const gapEnd = Number.isFinite(nextStart) ? nextStart : nowMs + 1;
      const gapStart = Number.isFinite(ends[i]) ? Math.min(ends[i], gapEnd) : starts[i];
      if (gapEnd <= gapStart) return i + 0.35;
      return (
        i + 0.35 + 0.65 * Math.min(1, (nowMs - gapStart) / (gapEnd - gapStart))
      );
    }
  }
  // past the last end: keep drifting slowly so the wall never freezes
  const lastEnd = Number.isFinite(ends[n - 1]) ? ends[n - 1] : starts[n - 1];
  return n - 1 + 0.35 + Math.max(0, nowMs - lastEnd) / 3600000;
}

/**
 * Human-readable schedule-change messages for toasts: an act whose start
 * moved, was cancelled, or was delayed — but only while it's still
 * relevant (live or upcoming), never for finished history.
 */
export function diffEvents(
  prev: TimelineEvent[],
  next: TimelineEvent[],
  nowMs: number
): string[] {
  const out: string[] = [];
  const byId = new Map(prev.map((e) => [e.id, e]));
  for (const e of next) {
    const p = byId.get(e.id);
    if (!p) continue; // brand-new acts appear in the drawer on their own
    const st = deriveStatus(e, nowMs);
    if (st !== "live" && st !== "delayed" && st !== "upcoming") continue;
    if (p.startTime !== e.startTime && Number.isFinite(Date.parse(e.startTime)))
      out.push(`${e.artist} moved to ${formatShortIST(e.startTime)}`);
    else if (p.status !== "cancelled" && e.status === "cancelled")
      out.push(`${e.artist} was cancelled`);
    else if (p.status !== "delayed" && e.status === "delayed")
      out.push(`${e.artist} is delayed`);
  }
  return out;
}

const dayFmt = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  weekday: "short",
  day: "numeric",
  month: "short",
});

/** IST calendar day key (YYYY-MM-DD) for the drawer's day selector. */
export function eventDayKey(iso: string): string {
  const ms = Date.parse(iso);
  if (!Number.isFinite(ms)) return "";
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(ms));
  return parts; // YYYY-MM-DD
}

/** "Sat, 7 Mar" in IST. */
export function eventDayLabel(iso: string): string {
  const ms = Date.parse(iso);
  if (!Number.isFinite(ms)) return "";
  return dayFmt.format(new Date(ms));
}

const istFmt = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

/** "8:30 PM IST" — always explicit, stored UTC. */
export function formatIST(iso: string): string {
  const ms = Date.parse(iso);
  if (!Number.isFinite(ms)) return "";
  return `${istFmt.format(new Date(ms))} IST`;
}

const shortFmt = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

/**
 * "1:30 AM" — short wall/clock form with no zone suffix. Use for every
 * repeated time line; pair surfaces with ONE "All times IST" note instead.
 * Still IST-explicit under the hood (same timeZone as formatIST).
 */
export function formatShortIST(iso: string): string {
  const ms = Date.parse(iso);
  if (!Number.isFinite(ms)) return "";
  return shortFmt.format(new Date(ms)).toUpperCase();
}

export function formatCountdown(msLeft: number): string {
  if (msLeft <= 0) return "now";
  const m = Math.floor(msLeft / 60000);
  const h = Math.floor(m / 60);
  if (h > 0) return `${h}h ${m % 60}m`;
  const s = Math.floor((msLeft % 60000) / 1000);
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

/**
 * Compact countdown for card context lines: whole minutes ("23 min")
 * until under 5 remain, then minute:second precision ("4m 12s").
 */
export function formatCountdownShort(msLeft: number): string {
  if (msLeft <= 0) return "now";
  const m = Math.floor(msLeft / 60000);
  if (m >= 5) return `${m} min`;
  const s = Math.floor((msLeft % 60000) / 1000);
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

/** Shared time→fraction for meter fill, NOW marker and ticks. */
export function meterFraction(ms: number, start: number, end: number): number {
  const span = Math.max(1, end - start);
  return Math.min(1, Math.max(0, (ms - start) / span));
}

/** "1h 5m ago" — elapsed time for finished acts. */
export function formatAgo(msAgo: number): string {
  const m = Math.max(0, Math.floor(msAgo / 60000));
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  return `${Math.floor(m / 60)}h ${m % 60}m ago`;
}

const clockFmt = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: true,
});

/** "08:42:05 PM" — live wall-clock in IST for the top-bar clock. */
export function formatClockIST(ms: number): string {
  if (!Number.isFinite(ms)) return "";
  return clockFmt.format(new Date(ms)).toUpperCase();
}

const clockShortFmt = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});

/** "4:06 PM" — no leading zero, no seconds. Top-bar clock. */
export function formatClockShort(ms: number): string {
  if (!Number.isFinite(ms)) return "";
  return clockShortFmt.format(new Date(ms)).toUpperCase();
}
