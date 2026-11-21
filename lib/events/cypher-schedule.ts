import { format, isValid, parse } from "date-fns";

const datePatterns = ["yyyy-MM-dd", "MMM do yyyy"];
const indiaCalendar = new Intl.DateTimeFormat("sv-SE", {
  timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit",
});

function canonicalDay(value: string | null) {
  const text = value?.trim();
  if (!text) return null;
  for (const pattern of datePatterns) {
    const date = parse(text, pattern, new Date(2000, 0, 1));
    if (isValid(date) && format(date, pattern) === text) return format(date, "yyyy-MM-dd");
  }
  return null;
}

export function currentCypherEvents<T extends {
  id: string; event_date: string | null; event_end_date: string | null;
}>(rows: readonly T[], now = new Date()) {
  const today = indiaCalendar.format(now);
  return rows.map(event => {
    const start = canonicalDay(event.event_date);
    const end = event.event_end_date ? canonicalDay(event.event_end_date) : start;
    return { event, start, end: start && end && end < start ? null : end };
  }).filter(row => !row.end || row.end >= today)
    .sort((a, b) => (a.start ?? "9999").localeCompare(b.start ?? "9999") || a.event.id.localeCompare(b.event.id))
    .map(row => row.event);
}
