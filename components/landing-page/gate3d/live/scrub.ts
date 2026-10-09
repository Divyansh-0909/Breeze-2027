// Slot-space wall scrub: pure math for moving the poster row by gesture.
// The camera stays locked; `display` is a float slot coordinate — follow
// mode pins it to the time coordinate, scrub mode owns it absolutely.
// No React, no three — unit-testable via ts-node.

/** Pixels of horizontal drag per poster slot. */
export const SCRUB_PX_PER_SLOT = 140;
/** Snap-to-poster glide duration (ms). Instant jump under reduced motion. */
export const SCRUB_SNAP_MS = 300;
/** Extra slots of fling per (slot/sec) of release velocity. */
export const SCRUB_FLING_BOOST = 0.22;
/** Ms of no interaction before gliding back to follow mode. 0 disables. */
export const SCRUB_IDLE_RETURN_MS = 45000;
/** Overshoot resistance past the first/last slot (0 = hard wall). */
export const SCRUB_RUBBER = 0.35;
/** Hard overshoot limit in slots. */
export const SCRUB_MAX_OVERSHOOT = 0.75;

export function clampSlot(i: number, count: number): number {
  if (count <= 0) return 0;
  return Math.min(count - 1, Math.max(0, Math.round(i)));
}

/** Nearest slot to a display coordinate (the focused poster). */
export function focusIndexForCoord(coord: number, count: number): number {
  return clampSlot(coord, count);
}

/** Rubber-band: resist dragging past the ends, never beyond the limit. */
export function applyRubber(coord: number, count: number): number {
  if (count <= 0) return 0;
  const lo = 0 - SCRUB_MAX_OVERSHOOT;
  const hi = count - 1 + SCRUB_MAX_OVERSHOOT;
  if (coord < 0) return Math.max(lo, coord * SCRUB_RUBBER);
  if (coord > count - 1)
    return Math.min(hi, count - 1 + (coord - (count - 1)) * SCRUB_RUBBER);
  return coord;
}

/** Release target: nearest slot, nudged by fling velocity (slots/sec). */
export function snapTarget(
  coord: number,
  velocitySlotsPerSec: number,
  count: number
): number {
  if (count <= 0) return 0;
  return clampSlot(coord + velocitySlotsPerSec * SCRUB_FLING_BOOST, count);
}

export function easeOutCubic(t: number): number {
  const u = Math.min(1, Math.max(0, t));
  return 1 - Math.pow(1 - u, 3);
}

/** True when the focused slot is the live position (pill stays hidden). */
export function atLivePosition(
  focusIdx: number,
  followCoord: number,
  count: number
): boolean {
  if (count <= 0) return true;
  return focusIdx === clampSlot(followCoord, count);
}

/**
 * Which side the live position sits on: -1 left (past), +1 right
 * (upcoming), 0 already there. Higher coordinate = further right.
 */
export function liveDirection(
  focusIdx: number,
  followCoord: number,
  count: number
): -1 | 0 | 1 {
  if (count <= 0) return 0;
  const liveIdx = clampSlot(followCoord, count);
  if (liveIdx === focusIdx) return 0;
  return liveIdx > focusIdx ? 1 : -1;
}
