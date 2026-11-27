"use client";

import { useEffect, useRef, type KeyboardEvent, type RefObject } from "react";
import { teamSlides, type TeamDisplay } from "./team-carousel";
import type { InputMode } from "./GullyHud";

const Chevron = ({ flip = false }: { flip?: boolean }) => <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"
  style={flip ? { transform: "scaleX(-1)" } : undefined}>
  <path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
</svg>;

export function CypherTeamDialog({ canvas, display, advance, retry, close, input = "keys" }: {
  input?: InputMode;
  canvas: RefObject<HTMLDivElement | null>;
  display: TeamDisplay;
  advance(direction: -1 | 1): void;
  retry(): void;
  close(): void;
}) {
  const dismiss = useRef<HTMLButtonElement>(null);
  useEffect(() => { dismiss.current?.focus({ preventScroll: true }); }, []);
  useEffect(() => {
    const target = canvas.current;
    if (!target) return;
    let start: { id: number; x: number; y: number } | null = null;
    const down = (event: PointerEvent) => {
      if (event.pointerType === "touch" && event.isPrimary) {
        start = { id: event.pointerId, x: event.clientX, y: event.clientY };
      }
    };
    const up = (event: PointerEvent) => {
      if (start?.id !== event.pointerId) return;
      const dx = event.clientX - start.x, dy = event.clientY - start.y;
      start = null;
      if (Math.abs(dx) > 55 && Math.abs(dx) > 1.5 * Math.abs(dy)) advance(dx < 0 ? 1 : -1);
    };
    const cancel = () => { start = null; };
    target.addEventListener("pointerdown", down);
    target.addEventListener("pointerup", up);
    target.addEventListener("pointercancel", cancel);
    return () => {
      target.removeEventListener("pointerdown", down);
      target.removeEventListener("pointerup", up);
      target.removeEventListener("pointercancel", cancel);
    };
  }, [canvas, advance]);

  function onKeyDown(event: KeyboardEvent<HTMLElement>) {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      event.stopPropagation();
      advance(event.key === "ArrowLeft" ? -1 : 1);
    } else if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      close();
    } else if (event.key === "Tab") {
      const buttons = event.currentTarget.querySelectorAll("button");
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }
  }

  const slide = teamSlides[display.index];
  const touch = input === "touch";
  return <section className="cypher-team-dialog hud-panel" role="dialog" aria-modal="true" aria-label="Team murals"
    onKeyDown={onKeyDown}>
    <div className="cypher-team-navigation">
      <button type="button" className="hud-step" onClick={() => advance(-1)} aria-label="Previous mural" aria-keyshortcuts="ArrowLeft">
        {touch ? <Chevron flip /> : <kbd>←</kbd>}</button>
      <div className="cypher-team-title">
        <h2 aria-live="polite">{slide.team}</h2>
        <ol className="hud-pips" aria-label={`Mural ${display.index + 1} of ${teamSlides.length}`}>
          {teamSlides.map((item, index) => <li key={item.team} data-current={index === display.index || undefined} />)}
        </ol>
      </div>
      <button type="button" className="hud-step" onClick={() => advance(1)} aria-label="Next mural" aria-keyshortcuts="ArrowRight">
        {touch ? <Chevron /> : <kbd>→</kbd>}</button>
    </div>
    <ul className="sr-only">{slide.people.map(person => <li key={person.name}>{person.name}, {person.role}</li>)}</ul>
    <div className="hud-panel-foot">
      <p>{touch ? "Swipe for more" : `${display.index + 1} / ${teamSlides.length}`}</p>
      <button ref={dismiss} type="button" className="hud-text-button" onClick={close} aria-label="Close team murals">
        {!touch && <kbd>Esc</kbd>}<span>Close</span></button>
    </div>
    {display.status === "error" && <div className="cypher-team-retry">
      <p role="status">The mural could not load.</p>
      <button type="button" onClick={retry}>Retry</button>
    </div>}
  </section>;
}
