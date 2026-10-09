// Supabase backing for the Live Timeline.
//
// Inactive unless NEXT_PUBLIC_TIMELINE_SOURCE=supabase. Every failure —
// missing tables, missing RPC, no network — resolves to null and the hook
// keeps serving the mock dataset, so this can never break the draft.
//
// Row shape (snake_case, TIMESTAMPTZ) maps to the camelCase TimelineEvent
// the scene renders. Server-time offset comes from the get_server_time()
// RPC in supabase_timeline_migration.sql.
"use client";
import type { Announcement, TimelineEvent } from "./types";

interface Row {
  id: string;
  title: string;
  artist: string;
  stage: string;
  description: string;
  start_time: string;
  end_time: string;
  status: TimelineEvent["status"];
  poster_url: string | null;
  featured: boolean | null;
  sort_order: number;
  updated_at: string;
}

interface AnnouncementRow {
  id: string;
  message: string;
  severity: string;
  active: boolean;
  created_at: string;
}

export function rowToEvent(r: Row): TimelineEvent {
  return {
    id: r.id,
    title: r.title ?? "",
    artist: r.artist ?? "",
    stage: r.stage ?? "Main Stage",
    description: r.description ?? "",
    startTime: r.start_time,
    endTime: r.end_time,
    status: r.status ?? null,
    posterUrl: r.poster_url ?? undefined,
    featured: r.featured ?? false,
    sortOrder: r.sort_order ?? 0,
    updatedAt: r.updated_at,
  };
}

export function rowToAnnouncement(r: AnnouncementRow): Announcement {
  const severity =
    r.severity === "warn" || r.severity === "urgent" ? r.severity : "info";
  return {
    id: r.id,
    message: r.message,
    severity,
    active: r.active,
    createdAt: r.created_at,
  };
}

export const TIMELINE_SOURCE =
  typeof process !== "undefined" &&
  process.env.NEXT_PUBLIC_TIMELINE_SOURCE === "supabase"
    ? "supabase"
    : "mock";

export interface Snapshot {
  events: TimelineEvent[];
  announcements: Announcement[];
  serverOffsetMs: number;
}

// eslint reports unknown-rule if disabled here (plugin not installed), and
// `any` is deliberate: the Supabase client type is heavy to import for a
// two-query module that is inactive unless the env flag selects it.
// eslint-disable-next-line
export async function fetchSnapshot(client: any): Promise<Snapshot | null> {
  try {
    const [evRes, anRes, timeRes] = await Promise.all([
      client
        .from("TimelineEvent")
        .select("*")
        .order("start_time", { ascending: true })
        .order("sort_order", { ascending: true }),
      client
        .from("TimelineAnnouncement")
        .select("*")
        .eq("active", true)
        .order("created_at", { ascending: false }),
      client.rpc("get_server_time"),
    ]);
    if (evRes.error || anRes.error) return null;
    let serverOffsetMs = 0;
    if (!timeRes.error && typeof timeRes.data === "string") {
      const serverMs = Date.parse(timeRes.data);
      if (Number.isFinite(serverMs)) serverOffsetMs = serverMs - Date.now();
    }
    return {
      events: (evRes.data as Row[]).map(rowToEvent),
      announcements: (anRes.data as AnnouncementRow[]).map(rowToAnnouncement),
      serverOffsetMs,
    };
  } catch {
    return null;
  }
}
