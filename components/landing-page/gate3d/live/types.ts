// Live Timeline data shapes. The 3D scene and DOM overlays render against
// these types only — never against a concrete backend — so the mock dataset
// can be swapped for Supabase Realtime later without touching the scene.
export type EventStatusOverride =
  | "scheduled"
  | "live"
  | "delayed"
  | "cancelled"
  | "done"
  | null;

export interface TimelineEvent {
  id: string;
  title: string;
  artist: string;
  stage: string;
  description: string;
  /** ISO 8601, UTC. */
  startTime: string;
  /** ISO 8601, UTC. */
  endTime: string;
  /** Admin override only (cancelled / delayed / forced live). Null = derive. */
  status: EventStatusOverride;
  /** Hero pick when several acts overlap: the featured live act wins over
   *  the earliest-started one. Null/false = ordinary. Admin-managed. */
  featured: boolean | null;
  posterUrl?: string;
  sortOrder: number;
  updatedAt: string;
}

export interface Announcement {
  id: string;
  message: string;
  severity: "info" | "warn" | "urgent";
  active: boolean;
  createdAt: string;
}

/** Client-derived display status. `live`/`done`/`upcoming` come from
 *  timestamps; `cancelled`/`delayed` come from the admin override. */
export type DerivedStatus =
  | "upcoming"
  | "live"
  | "done"
  | "cancelled"
  | "delayed";
