import assert from "node:assert/strict";
import { test } from "node:test";
import { currentCypherEvents } from "../../lib/events/cypher-schedule";

test("the wall keeps an event through its final India calendar day", () => {
  const single = { id: "a", event_date: "Nov 28th 2026", event_end_date: null };
  const multi = { id: "b", event_date: "2026-11-27", event_end_date: "2026-11-28" };
  const later = { id: "c", event_date: "2026-11-29", event_end_date: null, registration_open: false };
  const unknown = { id: "d", event_date: "Nov 31st 2026", event_end_date: null };
  const uncertainEnd = { id: "e", event_date: "Nov 26th 2026", event_end_date: "To be confirmed" };
  const invalidRange = { id: "f", event_date: "Nov 27th 2026", event_end_date: "Nov 25th 2026" };
  const rows = [later, unknown, uncertainEnd, single, multi, invalidRange];
  assert.deepEqual(currentCypherEvents(rows, new Date("2026-11-28T18:29:59Z")).map(e => e.id),
    ["e", "b", "f", "a", "c", "d"]);
  assert.deepEqual(currentCypherEvents(rows, new Date("2026-11-28T18:30:00Z")).map(e => e.id),
    ["e", "f", "c", "d"]);
});

test("events with the same start day retain a stable ID order", () => {
  const rows = ["b", "a"].map(id => ({ id, event_date: "2026-11-28", event_end_date: null }));
  assert.deepEqual(currentCypherEvents(rows, new Date("2026-11-25")).map(e => e.id), ["a", "b"]);
});
