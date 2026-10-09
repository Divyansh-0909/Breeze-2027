// The single data hook for the Live Timeline. Draft 1 serves the local
// mock dataset; the Supabase version keeps this exact return shape and
// swaps the internals to Realtime + polling fallback.
//
// Server-time offset: every timestamp comparison uses `nowMs`, which is
// Date.now() plus the server offset, so a wrong phone clock can't break
// live/next derivation. The mock reports offset 0.
//
// Clock model: `nowRef` is the mutable sim clock. It advances inside the
// Canvas frame loop (SimDriver in LiveLayer) so the treadmill is smooth at
// 60x without re-rendering React every frame; a 1 Hz interval refreshes
// the DOM countdowns.
"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import type {
  Announcement,
  DerivedStatus,
  TimelineEvent,
} from "./types";
import {
  deriveStatus,
  diffEvents,
  eventDayKey,
  liveProgress,
  selectHero,
  selectNextIndex,
} from "./timelineMath";
import { MOCK_ANNOUNCEMENTS, MOCK_EVENTS } from "./mockEvents";
import { TIMELINE_SOURCE, fetchSnapshot } from "./supabaseTimeline";

export interface SimState {
  paused: boolean;
  speed: 1 | 60 | 600;
  /** Manual jump target (ms). Non-null = hold the clock here. */
  scrubTo: number | null;
}

export interface LiveAct {
  ev: TimelineEvent;
  status: DerivedStatus;
  progress: number;
}

export interface TimelineApi {
  /** Mutable sim clock — read per-frame in 3D, never in render. */
  nowRef: React.MutableRefObject<number>;
  /** 1 Hz snapshot for DOM rendering. */
  nowMs: number;
  /** ALL events, start-sorted — one unified timeline, no stage split. */
  events: TimelineEvent[];
  /** Alias kept while the wall migrates; identical to `events`. */
  allEvents: TimelineEvent[];
  announcements: Announcement[];
  /** Every live act right now (any stage). */
  live: LiveAct[];
  /** Hero: featured live act, else earliest-started live act. */
  hero: LiveAct | null;
  /** Other concurrent live acts (the "Also on now" line). */
  alsoLive: LiveAct[];
  /** Next upcoming act across the whole timeline. */
  next: TimelineEvent | null;
  /** IST day keys present in the schedule (drawer day selector). */
  days: string[];
  updatedAt: string;
  /** True when data may be stale (offline, or Supabase sync failing). */
  stale: boolean;
  serverOffsetMs: number;
  sim: SimState;
  setPaused: (p: boolean) => void;
  setSpeed: (s: SimState["speed"]) => void;
  scrubToTime: (ms: number | null) => void;
  resumeLive: () => void;
  delayEvent: (id: string, minutes: number) => void;
  cancelEvent: (id: string) => void;
  pushAnnouncement: (message: string) => void;
}

export function useTimeline(): TimelineApi {
  const [events, setEvents] = useState<TimelineEvent[]>(MOCK_EVENTS);
  const [announcements, setAnnouncements] =
    useState<Announcement[]>(MOCK_ANNOUNCEMENTS);
  const [sim, setSim] = useState<SimState>({
    paused: false,
    speed: 1,
    scrubTo: null,
  });
  const [tick, setTick] = useState(0);
  const [serverOffsetMs, setServerOffsetMs] = useState(0);
  const [stale, setStale] = useState(false);
  const lastSyncRef = useRef(Date.now());

  const nowRef = useRef<number>(Date.now());
  const simRef = useRef(sim);
  simRef.current = sim;

  // 1 Hz DOM refresh + sim-clock advance. The Canvas SimDriver advances the
  // same ref per-frame; both writers agree because scrubTo (a hold) wins.
  useEffect(() => {
    const iv = window.setInterval(() => {
      const s = simRef.current;
      if (s.scrubTo !== null) nowRef.current = s.scrubTo;
      else if (!s.paused) nowRef.current += 1000 * s.speed;
      if (
        TIMELINE_SOURCE === "supabase" &&
        Date.now() - lastSyncRef.current > 45000
      )
        setStale(true);
      setTick((n) => (n + 1) % 1000000);
    }, 1000);
    const markOffline = () => setStale(true);
    const markOnline = () => {
      lastSyncRef.current = Date.now();
      setStale(false);
    };
    window.addEventListener("offline", markOffline);
    window.addEventListener("online", markOnline);
    return () => {
      window.clearInterval(iv);
      window.removeEventListener("offline", markOffline);
      window.removeEventListener("online", markOnline);
    };
  }, []);
  void tick;

  // Supabase backing (Realtime + 15 s polling fallback). Gated on
  // NEXT_PUBLIC_TIMELINE_SOURCE=supabase; any failure keeps mock data.
  useEffect(() => {
    if (TIMELINE_SOURCE !== "supabase") return;
    let alive = true;
    let channel: { unsubscribe: () => void } | null = null;
    let poll: number | undefined;
    const apply = async () => {
      try {
        const { createClient } = await import("@/utils/supabase/client");
        const client = createClient();
        const snap = await fetchSnapshot(client);
        if (!alive || !snap) {
          if (alive) setStale(true);
          return;
        }
        if (snap.events.length > 0) setEvents(snap.events);
        setAnnouncements(snap.announcements);
        setServerOffsetMs(snap.serverOffsetMs);
        lastSyncRef.current = Date.now();
        setStale(false);
      } catch {
        /* mock fallback stands */
      }
    };
    void apply();
    poll = window.setInterval(apply, 15000);
    (async () => {
      try {
        const { createClient } = await import("@/utils/supabase/client");
        const client = createClient();
        channel = client
          .channel("timeline-live")
          .on(
            "postgres_changes",
            { event: "*", schema: "public", table: "TimelineEvent" },
            () => void apply()
          )
          .on(
            "postgres_changes",
            { event: "*", schema: "public", table: "TimelineAnnouncement" },
            () => void apply()
          )
          .subscribe() as unknown as { unsubscribe: () => void };
      } catch {
        /* polling fallback stands */
      }
    })();
    return () => {
      alive = false;
      window.clearInterval(poll);
      channel?.unsubscribe();
    };
  }, []);

  const nowMs = (sim.scrubTo ?? nowRef.current) + serverOffsetMs;

  // One unified timeline: everything start-sorted, no stage split. Stage
  // survives only as a small badge on posters and rows.
  const sorted = useMemo(
    () =>
      [...events].sort(
        (a, b) =>
          Date.parse(a.startTime) - Date.parse(b.startTime) ||
          a.sortOrder - b.sortOrder
      ),
    [events]
  );

  const live = useMemo(() => {
    const out: LiveAct[] = [];
    for (const ev of sorted) {
      const st = deriveStatus(ev, nowMs);
      if (st === "live" || st === "delayed")
        out.push({ ev, status: st, progress: liveProgress(ev, nowMs) });
    }
    return out;
  }, [sorted, nowMs]);

  const { hero, also: alsoLive } = useMemo(() => selectHero(live), [live]);

  const next = useMemo(() => {
    // shared selector: first upcoming/delayed overall, cancelled never matches
    const idx = selectNextIndex(sorted, nowMs, -1, true);
    return idx >= 0 ? sorted[idx] : null;
  }, [sorted, nowMs]);

  const days = useMemo(() => {
    const keys = new Set<string>();
    for (const e of sorted) {
      const k = eventDayKey(e.startTime);
      if (k) keys.add(k);
    }
    return [...keys].sort();
  }, [sorted]);

  // Toast live schedule changes (moved / cancelled / delayed acts). Fires
  // only when the event LIST changes (debug tools, Supabase push) — never
  // on clock ticks, so natural live handoffs stay quiet. The ref comparison
  // makes it StrictMode-safe: the second pass finds no diff.
  const prevEventsRef = useRef<TimelineEvent[]>(events);
  useEffect(() => {
    const prev = prevEventsRef.current;
    prevEventsRef.current = events;
    if (prev === events) return;
    for (const msg of diffEvents(prev, events, nowMs)) toast(msg);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events]);

  const setPaused = useCallback(
    (p: boolean) => setSim((s) => ({ ...s, paused: p })),
    []
  );
  const setSpeed = useCallback(
    (s: SimState["speed"]) => setSim((prev) => ({ ...prev, speed: s })),
    []
  );
  const scrubToTime = useCallback(
    (ms: number | null) =>
      setSim((s) => {
        if (ms !== null) nowRef.current = ms;
        return { ...s, scrubTo: ms };
      }),
    []
  );
  const resumeLive = useCallback(() => {
    nowRef.current = Date.now();
    setSim((s) => ({ ...s, scrubTo: null, paused: false }));
  }, []);
  const delayEvent = useCallback((id: string, minutes: number) => {
    setEvents((prev) =>
      prev.map((e) =>
        e.id !== id
          ? e
          : {
              ...e,
              startTime: new Date(
                Date.parse(e.startTime) + minutes * 60000
              ).toISOString(),
              endTime: new Date(
                Date.parse(e.endTime) + minutes * 60000
              ).toISOString(),
              status:
                e.status === "cancelled" || e.status === "done"
                  ? e.status
                  : "delayed",
              updatedAt: new Date().toISOString(),
            }
      )
    );
  }, []);
  const cancelEvent = useCallback((id: string) => {
    setEvents((prev) =>
      prev.map((e) =>
        e.id === id
          ? {
              ...e,
              status: "cancelled" as const,
              updatedAt: new Date().toISOString(),
            }
          : e
      )
    );
  }, []);
  const pushAnnouncement = useCallback((message: string) => {
    setAnnouncements((prev) => [
      ...prev,
      {
        id: `an-${Date.now()}`,
        message,
        severity: "warn" as const,
        active: true,
        createdAt: new Date().toISOString(),
      },
    ]);
  }, []);

  return {
    nowRef,
    nowMs,
    events: sorted,
    allEvents: sorted,
    announcements: announcements.filter((a) => a.active),
    live,
    hero,
    alsoLive,
    next,
    days,
    stale,
    updatedAt: events.reduce(
      (m, e) => (e.updatedAt > m ? e.updatedAt : m),
      MOCK_EVENTS[0]?.updatedAt ?? new Date().toISOString()
    ),
    serverOffsetMs,
    sim,
    setPaused,
    setSpeed,
    scrubToTime,
    resumeLive,
    delayEvent,
    cancelEvent,
    pushAnnouncement,
  };
}
