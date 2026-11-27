"use client";
import { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import type { ImmersiveRuntime } from "../immersive/runtime";
import { tier } from "./gully-diagnostics";
import { deviceBudget } from "./device-tier";

/**
 * Bounded, hysteretic render-resolution tiers. Only the drawing-buffer scale changes: geometry, content,
 * lighting, movement, input and destinations are identical in every tier.
 *
 *   high      DPR min(device, cap)  after sustained headroom; cap from the device budget (device-tier.ts):
 *                                   1.75 high, 1.5 medium, 1.25 low
 *   balanced  DPR 1                 the starting tier everywhere (the previous fixed setting)
 *   low       DPR 0.8               after sustained overload
 *   minimum   DPR 0.65              after further sustained overload (weak or thermally throttled devices)
 *
 * Decisions use 3-second windows of walking frames only (no loading, map, focused views or hidden tab).
 * Down a step: average frame over 1/45 s (desktop) or 1/26 s (touch). Up a step: 20 seconds averaging
 * under 1/58 s, at most twice per visit. Each change is followed by an 8-second hold. `?tier=<name>`
 * pins a tier (benchmarks use `?tier=balanced`). Changes are recorded in the diagnostics.
 */
const tiers = [
  { name: "minimum", dpr: () => 0.65 },
  { name: "low", dpr: () => 0.8 },
  { name: "balanced", dpr: () => 1 },
  { name: "high", dpr: () => Math.min(window.devicePixelRatio, deviceBudget().dprCap) },
] as const;

/** `setDpr` must drive the Canvas `dpr` prop: R3F re-applies that prop whenever it differs. */
export function QualityGovernor({ runtime, setDpr }: { runtime: ImmersiveRuntime; setDpr(dpr: number): void }) {
  const state = useRef({ index: 2, pinned: false, touch: false, elapsed: 0, frames: 0, fast: 0, hold: 0, upgrades: 0 });
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get("tier");
    const pinned = tiers.findIndex(t => t.name === requested);
    const s = state.current;
    s.touch = window.matchMedia("(pointer: coarse)").matches;
    if (pinned >= 0) { s.index = pinned; s.pinned = true; }
    apply(s.index, pinned >= 0 ? "pinned" : "start");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  function apply(index: number, reason: string) {
    const from = tier.name, next = tiers[index], dpr = next.dpr();
    setDpr(dpr);
    tier.name = next.name; tier.dpr = dpr;
    tier.changes.push({ at: performance.now(), from, to: next.name, dpr, reason });
  }
  useFrame((_, delta) => {
    const s = state.current, snapshot = runtime.getSnapshot();
    if (s.pinned) return;
    if (snapshot.phase !== "local" || snapshot.map || runtime.interacting || runtime.suspended || document.hidden || delta > 0.25) {
      s.elapsed = s.frames = 0; return;
    }
    s.elapsed += delta; s.frames++;
    if (s.elapsed < 3) return;
    const average = s.elapsed / s.frames;
    s.elapsed = s.frames = 0;
    if (s.hold > 0) { s.hold -= 3; return; }
    const slow = s.touch ? 1 / 26 : 1 / 45;
    if (average > slow && s.index > 0) { s.index--; s.fast = 0; s.hold = 8; apply(s.index, `average ${(average * 1000).toFixed(1)} ms`); return; }
    if (average < 1 / 58) s.fast += 3; else s.fast = 0;
    if (s.fast >= 20 && s.index < tiers.length - 1 && s.upgrades < 2) {
      s.index++; s.upgrades++; s.fast = 0; s.hold = 8; apply(s.index, `headroom ${(average * 1000).toFixed(1)} ms`);
    }
  });
  return null;
}
