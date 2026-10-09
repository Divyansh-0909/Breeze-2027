// Poster-only wall scrub: the camera stays locked, the row translates in
// slot space. Follow mode pins the display coordinate to the time
// coordinate; scrub mode owns it absolutely until snap / Back-to-Live /
// idle timeout glides home. The 3D layer reads displayRef per frame;
// React state mirrors only the focused index (card) and mode (pill).
"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type { TimelineEvent } from "./types";
import {
  SCRUB_IDLE_RETURN_MS,
  SCRUB_PX_PER_SLOT,
  SCRUB_SNAP_MS,
  applyRubber,
  atLivePosition,
  clampSlot,
  easeOutCubic,
  focusIndexForCoord,
  liveDirection,
  snapTarget,
} from "./scrub";

export type ScrubMode = "follow" | "scrub";

interface VelSample {
  t: number;
  display: number;
}

export function useScrub(opts: {
  /** Number of slots (acts) on the wall. */
  count: number;
  /** Time coordinate, refreshed ~1 Hz. */
  followCoord: number;
  /** Gestures/keys allowed (live view mounted, phase arrived). */
  enabled: boolean;
  /** Wall gestures pause while the drawer is open. */
  drawerOpen: boolean;
  reduced: boolean;
  events: TimelineEvent[];
}): {
  displayRef: React.MutableRefObject<number>;
  modeRef: React.MutableRefObject<ScrubMode>;
  mode: ScrubMode;
  focusIdx: number;
  atLive: boolean;
  liveDir: -1 | 0 | 1;
  goToIndex: (i: number) => void;
  goLive: () => void;
  focusEvent: (id: string) => void;
  rootHandlers: {
    onPointerDown: (e: React.PointerEvent) => void;
    onPointerMove: (e: React.PointerEvent) => void;
    onPointerUp: (e: React.PointerEvent) => void;
    onPointerCancel: (e: React.PointerEvent) => void;
    onWheel: (e: React.WheelEvent) => void;
  };
} {
  const { count, followCoord, enabled, drawerOpen, reduced, events } = opts;
  const displayRef = useRef(followCoord);
  const modeRef = useRef<ScrubMode>("follow");
  const [mode, setMode] = useState<ScrubMode>("follow");
  const [focusIdx, setFocusIdx] = useState(() =>
    focusIndexForCoord(followCoord, count)
  );
  const focusIdRef = useRef<string | null>(null);
  const glideRef = useRef(0);
  const idleRef = useRef(0);
  const wheelSnapRef = useRef(0);
  const dragRef = useRef<{
    lastX: number;
    startDisplay: number;
    samples: VelSample[];
  } | null>(null);

  const setModeBoth = useCallback((m: ScrubMode) => {
    modeRef.current = m;
    setMode(m);
  }, []);

  const syncFocus = useCallback(
    (display: number) => {
      const fi = focusIndexForCoord(display, count);
      setFocusIdx((prev) => {
        if (prev !== fi) {
          focusIdRef.current = events[fi]?.id ?? null;
        }
        return prev === fi ? prev : fi;
      });
    },
    [count, events]
  );

  const killGlide = useCallback(() => {
    window.cancelAnimationFrame(glideRef.current);
    glideRef.current = 0;
  }, []);

  const resetIdle = useCallback(() => {
    window.clearTimeout(idleRef.current);
    idleRef.current = 0;
    if (SCRUB_IDLE_RETURN_MS <= 0) return;
    idleRef.current = window.setTimeout(() => {
      if (modeRef.current === "scrub") goLiveRef.current();
    }, SCRUB_IDLE_RETURN_MS);
  }, []);

  // glide the wall to an absolute slot coordinate, then optionally follow
  const glideTo = useCallback(
    (to: number, thenFollow: boolean) => {
      killGlide();
      if (reduced) {
        displayRef.current = to;
        syncFocus(to);
        if (thenFollow) {
          setModeBoth("follow");
        } else if (atLivePosition(focusIndexForCoord(to, count), followCoordRef.current, count)) {
          setModeBoth("follow");
        }
        return;
      }
      const from = displayRef.current;
      if (Math.abs(to - from) < 0.001) {
        if (thenFollow) setModeBoth("follow");
        return;
      }
      const start = performance.now();
      const step = (t: number) => {
        const k = easeOutCubic((t - start) / SCRUB_SNAP_MS);
        displayRef.current = from + (to - from) * k;
        syncFocus(displayRef.current);
        if (k < 1) {
          glideRef.current = requestAnimationFrame(step);
        } else {
          glideRef.current = 0;
          displayRef.current = to;
          syncFocus(to);
          if (thenFollow) setModeBoth("follow");
          else if (
            atLivePosition(to, followCoordRef.current, count)
          )
            setModeBoth("follow");
        }
      };
      glideRef.current = requestAnimationFrame(step);
    },
    [count, killGlide, reduced, setModeBoth, syncFocus]
  );
  const followCoordRef = useRef(followCoord);
  followCoordRef.current = followCoord;
  const goLiveRef = useRef(() => {});
  goLiveRef.current = () => {};

  const goLive = useCallback(() => {
    window.clearTimeout(idleRef.current);
    idleRef.current = 0;
    glideTo(followCoordRef.current, true);
  }, [glideTo]);
  goLiveRef.current = goLive;

  const goToIndex = useCallback(
    (i: number) => {
      if (count <= 0) return;
      killGlide();
      window.clearTimeout(wheelSnapRef.current);
      setModeBoth("scrub");
      glideTo(clampSlot(i, count), false);
      resetIdle();
    },
    [count, glideTo, killGlide, resetIdle, setModeBoth]
  );

  const focusEvent = useCallback(
    (id: string) => {
      const i = events.findIndex((e) => e.id === id);
      if (i >= 0) goToIndex(i);
    },
    [events, goToIndex]
  );

  // follow mode: track time; also repair clamps when the list changes
  useEffect(() => {
    if (mode === "follow") {
      displayRef.current = followCoord;
      const fi = focusIndexForCoord(followCoord, count);
      setFocusIdx((prev) => (prev === fi ? prev : fi));
      focusIdRef.current = events[fi]?.id ?? null;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [followCoord, mode, count]);

  // live data updates mid-scrub: keep the focused act focused (by id);
  // if it disappeared, fall back to the nearest surviving slot
  const eventsRef = useRef(events);
  useEffect(() => {
    const prev = eventsRef.current;
    eventsRef.current = events;
    if (prev === events || modeRef.current !== "scrub") return;
    const id = focusIdRef.current;
    const idx = id ? events.findIndex((e) => e.id === id) : -1;
    if (idx >= 0) {
      displayRef.current = idx;
      setFocusIdx(idx);
    } else {
      const fi = focusIndexForCoord(displayRef.current, events.length);
      displayRef.current = fi;
      setFocusIdx(fi);
      focusIdRef.current = events[fi]?.id ?? null;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events]);

  useEffect(
    () => () => {
      window.cancelAnimationFrame(glideRef.current);
      window.clearTimeout(idleRef.current);
      window.clearTimeout(wheelSnapRef.current);
    },
    []
  );

  const velocityOf = (samples: VelSample[]): number => {
    if (samples.length < 2) return 0;
    const first = samples[0];
    const last = samples[samples.length - 1];
    const dt = (last.t - first.t) / 1000;
    if (dt <= 0.01) return 0;
    const v = (last.display - first.display) / dt;
    return Math.min(8, Math.max(-8, v));
  };

  const onPointerDown = useCallback(
    (e: React.PointerEvent) => {
      if (!enabled || drawerOpen || count <= 0) return;
      if (e.pointerType === "mouse" && e.button !== 0) return;
      if (
        (e.target as HTMLElement).closest(
          "button, a, input, textarea, select, [role='dialog'], [data-live-ui]"
        )
      )
        return;
      killGlide();
      window.clearTimeout(wheelSnapRef.current);
      window.clearTimeout(idleRef.current);
      setModeBoth("scrub");
      dragRef.current = {
        lastX: e.clientX,
        startDisplay: displayRef.current,
        samples: [{ t: performance.now(), display: displayRef.current }],
      };
    },
    [count, drawerOpen, enabled, killGlide, setModeBoth]
  );

  const onPointerMove = useCallback(
    (e: React.PointerEvent) => {
      const drag = dragRef.current;
      if (!drag || !enabled) return;
      const dx = e.clientX - drag.lastX;
      drag.lastX = e.clientX;
      // drag left reveals upcoming (right side); vertical handled by pan-y
      const next = applyRubber(
        displayRef.current - dx / SCRUB_PX_PER_SLOT,
        count
      );
      displayRef.current = next;
      const now = performance.now();
      drag.samples.push({ t: now, display: next });
      while (drag.samples.length > 2 && now - drag.samples[0].t > 120)
        drag.samples.shift();
      syncFocus(next);
    },
    [count, enabled, syncFocus]
  );

  const endDrag = useCallback(
    (velocity: number) => {
      const drag = dragRef.current;
      dragRef.current = null;
      if (!drag || !enabled) return;
      const target = snapTarget(displayRef.current, velocity, count);
      setModeBoth("scrub");
      glideToRef.current(target);
      resetIdle();
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [count, enabled, resetIdle, setModeBoth]
  );

  const glideToRef = useRef((to: number) => {
    glideTo(to, false);
  });
  glideToRef.current = (to: number) => glideTo(to, false);

  const onPointerUp = useCallback(() => {
    const drag = dragRef.current;
    if (!drag) return;
    endDrag(velocityOf(drag.samples));
  }, [endDrag]);

  const onPointerCancel = useCallback(() => {
    if (dragRef.current) endDrag(0);
  }, [endDrag]);

  const onWheel = useCallback(
    (e: React.WheelEvent) => {
      if (!enabled || drawerOpen || count <= 0) return;
      const dx = e.deltaX + (e.shiftKey ? e.deltaY : 0);
      // predominantly vertical → page/drawer scroll owns it
      if (!e.shiftKey && Math.abs(e.deltaY) > Math.abs(dx)) return;
      if (dx === 0) return;
      killGlide();
      window.clearTimeout(wheelSnapRef.current);
      window.clearTimeout(idleRef.current);
      setModeBoth("scrub");
      displayRef.current = applyRubber(
        displayRef.current - dx / SCRUB_PX_PER_SLOT,
        count
      );
      syncFocus(displayRef.current);
      window.clearTimeout(wheelSnapRef.current);
      wheelSnapRef.current = window.setTimeout(() => {
        glideToRef.current(
          snapTarget(displayRef.current, 0, count)
        );
        resetIdle();
      }, 140);
    },
    [count, drawerOpen, enabled, killGlide, resetIdle, setModeBoth, syncFocus]
  );

  // arrow keys step the focus; only when live owns the keyboard
  useEffect(() => {
    if (!enabled || drawerOpen) return;
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      goToIndex(focusIdxRef.current + (e.key === "ArrowRight" ? 1 : -1));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled, drawerOpen, goToIndex]);
  const focusIdxRef = useRef(focusIdx);
  focusIdxRef.current = focusIdx;

  const atLive = atLivePosition(focusIdx, followCoord, count);
  const liveDir = liveDirection(focusIdx, followCoord, count);

  return {
    displayRef,
    modeRef,
    mode,
    focusIdx,
    atLive,
    liveDir,
    goToIndex,
    goLive,
    focusEvent,
    rootHandlers: {
      onPointerDown,
      onPointerMove,
      onPointerUp,
      onPointerCancel,
      onWheel,
    },
  };
}
