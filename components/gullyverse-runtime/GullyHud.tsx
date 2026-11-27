"use client";

import { useEffect, useState } from "react";
import { mapStops, type CypherStart } from "./cypher-map";

/**
 * In-world HUD pieces for the walkable gully, after open-world game HUDs: a place title that announces each
 * new place once, a loading screen with real progress and a tip, and key glyphs that follow the visitor's input.
 */
export type InputMode = "keys" | "touch";

/** Keys or touch, from the last input used; starts from the primary pointer. */
export function useInputMode(): InputMode {
  const [mode, setMode] = useState<InputMode>(() =>
    typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches ? "touch" : "keys");
  useEffect(() => {
    const keys = () => setMode("keys");
    const pointer = (event: PointerEvent) => setMode(event.pointerType === "touch" ? "touch" : "keys");
    window.addEventListener("keydown", keys);
    window.addEventListener("pointerdown", pointer);
    return () => { window.removeEventListener("keydown", keys); window.removeEventListener("pointerdown", pointer); };
  }, []);
  return mode;
}

export type Zone = "Market lane" | "Navigation approach" | "Cypher gate" | "Cypher forecourt" | "Cypher plaza";
export const zoneAt = (z: number): Zone => {
  if (z < -22) return "Cypher plaza";
  if (z < -15.65) return "Cypher forecourt";
  if (z < -11.4) return "Cypher gate";
  if (z < -1.5) return "Navigation approach";
  return "Market lane";
};
const zoneHint: Record<Zone, string> = {
  "Market lane": "Cypher ahead",
  "Navigation approach": "Every stop is on the board",
  "Cypher gate": "Plaza ahead",
  "Cypher forecourt": "Plaza ahead",
  "Cypher plaza": "Join the crowd",
};
/** What a visitor can open in each place, read from the map so it never drifts from it. */
function zoneLine(zone: Zone) {
  const here = mapStops.filter(stop => stop.kind === "destination" && zoneAt(stop.marker[2]) === zone).map(stop => stop.label);
  return here.length ? here.join(", ") : zoneHint[zone];
}

const seenKey = "gully-places-seen";
function firstVisit(zone: Zone) {
  try {
    const seen: string[] = JSON.parse(sessionStorage.getItem(seenKey) ?? "[]");
    if (seen.includes(zone)) return false;
    sessionStorage.setItem(seenKey, JSON.stringify([...seen, zone]));
  } catch { /* storage blocked: announce every time */ }
  return true;
}

/** Top-left place name; a large title announces a place the first time the visitor walks into it. */
export function HudLocation({ zone }: { zone: Zone }) {
  const [banner, setBanner] = useState<Zone | null>(null);
  useEffect(() => {
    if (!firstVisit(zone)) return;
    setBanner(zone);
    const timer = window.setTimeout(() => setBanner(current => current === zone ? null : current), 3600);
    return () => window.clearTimeout(timer);
  }, [zone]);
  return <>
    <p className="gully-location" aria-live="polite">
      <span className="hud-place">{zone}</span>
    </p>
    {banner && <div className="hud-discovery" key={banner} aria-hidden="true">
      <div className="hud-discovery-sign">
        <strong>{banner}</strong>
        <span>{zoneLine(banner)}</span>
      </div>
    </div>}
  </>;
}

export type ArrivalProgress = { done: number; total: number };

/** Full-screen loading: a plain progress bar from real chunk progress. */
export function HudLoading({ start, progress, message, children }: {
  start: CypherStart | "quarry";
  progress: ArrivalProgress;
  /** Replaces the bar (restoring 3D, errors). */
  message?: string | null;
  children?: React.ReactNode;
}) {
  const destination = start === "quarry" ? "Quarry" : mapStops.find(stop => stop.id === start)?.label ?? "Market lane";
  // Each arrival chunk is one step; preparing the scene for the first frame is the last.
  const percent = progress.total ? Math.round(progress.done / (progress.total + 1) * 100) : 0;
  return <div className="native-loading hud-loading" role="status" data-failed={message ? true : undefined}>
    {message ? <p className="hud-loading-message">{message}</p> : <div className="hud-loading-bar">
      <p><span>Loading {destination}</span><span>{percent}%</span></p>
      <div className="hud-meter" role="progressbar" aria-label={`Loading ${destination}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent}>
        <span style={{ transform: `scaleX(${percent / 100})` }} />
      </div>
    </div>}
    {children}
  </div>;
}

/** Small line icons for the touch legend. */
export const PadIcon = () => <svg className="hud-glyph" viewBox="0 0 24 24" aria-hidden="true">
  <path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6z" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
</svg>;
export const DragIcon = () => <svg className="hud-glyph" viewBox="0 0 24 24" aria-hidden="true">
  <path d="M3 12h18M7 8l-4 4 4 4M17 8l4 4-4 4" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
</svg>;
