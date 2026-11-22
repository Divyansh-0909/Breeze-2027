"use client";

import { useEffect, useRef } from "react";

export function CypherAftermovieControls({ loading, muted, toggleSound, close }: {
  loading: boolean;
  muted: boolean;
  toggleSound(): void;
  close(): void;
}) {
  const exit = useRef<HTMLButtonElement>(null);
  useEffect(() => { exit.current?.focus({ preventScroll: true }); }, []);

  return <section className="cypher-aftermovie-controls" aria-label="Aftermovie playback">
    <div className="cypher-aftermovie-title">
      <h2>Aftermovie</h2>
      <button ref={exit} type="button" onClick={close}>Exit Aftermovie</button>
    </div>
    {loading
      ? <p role="status">Loading Aftermovie…</p>
      : <button type="button" onClick={toggleSound}>{muted ? "Enable sound" : "Mute sound"}</button>}
  </section>;
}
