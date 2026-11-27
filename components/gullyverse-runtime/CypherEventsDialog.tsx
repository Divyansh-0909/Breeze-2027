"use client";

import Link from "next/link";
import { useEffect, useRef, type KeyboardEvent } from "react";
import type { CypherCatalog, CypherEvent } from "../../lib/events/cypher-catalog";

export function CypherEventsDialog({ catalog, visibleEvents, page, pages, event, changePage, choose, close }: {
  catalog: CypherCatalog;
  visibleEvents: CypherEvent[];
  page: number;
  pages: number;
  event: CypherEvent | undefined;
  changePage(page: number): void;
  choose(id: string | null): void;
  close(): void;
}) {
  const dismiss = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    dismiss.current?.focus({ preventScroll: true });
  }, [event]);
  function onKeyDown(input: KeyboardEvent<HTMLElement>) {
    if (input.key === "Escape") {
      input.preventDefault();
      input.stopPropagation();
      close();
    }
    if (input.key !== "Tab") return;
    const buttons = input.currentTarget.querySelectorAll<HTMLElement>("button:not(:disabled), a[href]");
    const first = buttons[0], last = buttons[buttons.length - 1];
    if (input.shiftKey && document.activeElement === first) { input.preventDefault(); last?.focus(); }
    if (!input.shiftKey && document.activeElement === last) { input.preventDefault(); first?.focus(); }
  }

  return <section className="cypher-events-dialog hud-panel" role="dialog" aria-modal="true" aria-label="Events wall" onKeyDown={onKeyDown}>
    <div className="cypher-events-toolbar">
      <h2>{event?.event_name ?? "Events"}</h2>
      <button ref={dismiss} type="button" className="hud-text-button hud-close" onClick={close} aria-label="Close Events"><kbd>Esc</kbd><span>Close</span></button>
    </div>
    {event ? <>
      <p>{[event.event_org, event.event_date, event.event_end_date, event.event_venue].filter(Boolean).join(" · ")}</p>
      {event.event_description && <p className="cypher-event-description">{event.event_description}</p>}
      {!event.registration_open && <p>Registration closed</p>}
      <div className="cypher-events-toolbar">
        <button type="button" onClick={() => choose(null)}>Back to posters</button>
        <a href={`/events/${encodeURIComponent(event.id)}`}>Event details</a>
      </div>
    </> : <>
      {!catalog.available ? <p>Event listings are temporarily unavailable.</p> :
        !visibleEvents.length ? <p>No upcoming events are listed yet.</p> :
        <ul className="cypher-event-links">
          {visibleEvents.map(item => <li key={item.id}>
            <button type="button" onClick={() => choose(item.id)}>{item.event_name}</button>
          </li>)}
        </ul>}
      {pages > 1 && <nav className="cypher-events-toolbar" aria-label="Poster pages">
        <button type="button" onClick={() => changePage(page - 1)} disabled={page === 0}>Previous</button>
        <span aria-live="polite">{page + 1} / {pages}</span>
        <button type="button" onClick={() => changePage(page + 1)} disabled={page + 1 === pages}>Next</button>
      </nav>}
      {!catalog.available && <Link href="/events">Browse events</Link>}
    </>}
  </section>;
}
