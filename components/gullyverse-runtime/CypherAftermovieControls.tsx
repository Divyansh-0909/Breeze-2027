"use client";

import { useEffect, useRef } from "react";

/**
 * Theater mode for the Aftermovie (Phase 2): a dark backdrop over the plaza with the film itself centred at 16:9 and
 * the playback band below it. The film is the same <video> that feeds the LED wall: it joins the theater frame only
 * while it is open (Chrome may pause an invisible muted video left in the page) and play() is called after each
 * move (Safari pauses a re-parented video). Esc, the Exit button or a click on the backdrop return to walking.
 * The low tier drops the backdrop blur (an opaque surface instead).
 */
export function CypherAftermovieControls({ loading, muted, toggleSound, close, video, low }: {
  loading: boolean;
  muted: boolean;
  toggleSound(): void;
  close(): void;
  video: HTMLVideoElement | null;
  low: boolean;
}) {
  const exit = useRef<HTMLButtonElement>(null);
  const frame = useRef<HTMLDivElement>(null);
  useEffect(() => { exit.current?.focus({ preventScroll: true }); }, []);
  useEffect(() => {
    const host = frame.current;
    if (!video || !host) return;
    host.append(video);
    void video.play().catch(() => { /* resumes on the next gesture */ });
    return () => {
      video.remove();
      void video.play().catch(() => {});
    };
  }, [video]);

  return <div className="cypher-theater" data-low={low || undefined}
    onClick={event => { if (event.target === event.currentTarget) close(); }}>
    <div className="cypher-theater-frame" ref={frame} data-loading={loading || undefined} />
    <section className="cypher-aftermovie-controls hud-panel" aria-label="Aftermovie playback">
      <div className="cypher-aftermovie-title">
        <h2>Aftermovie</h2>
        <button ref={exit} type="button" className="hud-text-button hud-close" onClick={close}><kbd>Esc</kbd><span>Exit Aftermovie</span></button>
      </div>
      {loading
        ? <p role="status">Loading Aftermovie…</p>
        : <button type="button" aria-keyshortcuts="V" aria-pressed={!muted} onClick={toggleSound}>{muted ? "Sound off" : "Sound on"}</button>}
    </section>
  </div>;
}
