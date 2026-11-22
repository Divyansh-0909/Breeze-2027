import type { Pose } from "../immersive/navigation";
import { createCypherSpace } from "./cypher-space";
import { cypherContact } from "./cypher-contact";
import { teamFocus, teamSlides } from "./team-carousel";
import { accommodationApproach } from "./cypher-accommodation";

/** The walkable route shared by every cypher preview start and map stop. */
export const routeBounds = { start: -29.5, end: 47.6, halfWidth: 16, plaza: true };

const startSpaces = {
  market: createCypherSpace({ ...routeBounds, spawnY: -27.6 }),
  approach: createCypherSpace({ ...routeBounds, spawnY: 2.2, spawnPitch: 0.27 }),
  plaza: createCypherSpace({ ...routeBounds, spawnY: 19.3, spawnPitch: 0.08 }),
  contact: createCypherSpace({ ...routeBounds, spawnY: -cypherContact.spawn.z, spawnX: cypherContact.spawn.x,
    spawnYaw: cypherContact.spawn.yaw, spawnPitch: cypherContact.spawn.pitch }),
  events: createCypherSpace({ ...routeBounds, spawnY: 31.05, spawnX: -10.7, spawnYaw: Math.PI / 2 }),
  team: createCypherSpace({ ...routeBounds, spawnY: -teamFocus.z, spawnX: teamFocus.x, spawnYaw: teamFocus.yaw }),
  aftermovie: createCypherSpace({ ...routeBounds, spawnY: 33.5, spawnPitch: 0.17 }),
  accommodation: createCypherSpace({
    ...routeBounds, spawnY: -accommodationApproach.z, spawnX: accommodationApproach.x,
    spawnYaw: accommodationApproach.yaw, spawnPitch: accommodationApproach.pitch,
  }),
};
export type CypherStart = keyof typeof startSpaces;
export const cypherStarts: Record<CypherStart, ReturnType<typeof createCypherSpace>> = startSpaces;
export const isCypherStart = (value: unknown): value is CypherStart =>
  typeof value === "string" && Object.prototype.hasOwnProperty.call(startSpaces, value);
/** The walking pose a start or map stop lands on. */
export const arrivalPose = (start: CypherStart): Pose => cypherStarts[start].space.spawn("hub", false);

export type MapStop = {
  id: CypherStart;
  label: string;
  /** World point the map marker points at: the artwork or place itself. */
  marker: readonly [number, number, number];
  /** Destinations open a focused view on arrival; places only move the visitor. */
  kind: "destination" | "place";
};
const teamCentre = teamSlides[0].centre as [number, number, number];

/** Ordered from the entrance to the screen, as the route is walked. */
export const mapStops: readonly MapStop[] = [
  { id: "market", label: "Market lane", marker: [0, 7.2, 24], kind: "place" },
  { id: "approach", label: "Navigation board", marker: [0, 7.2, -9.5], kind: "place" },
  { id: "accommodation", label: "Accommodation", marker: [-12.015, 9.12, -14.009], kind: "destination" },
  { id: "contact", label: "Contact", marker: cypherContact.headingCentre as [number, number, number], kind: "destination" },
  { id: "plaza", label: "Cypher plaza", marker: [0, 7.2, -21], kind: "place" },
  { id: "events", label: "Events", marker: [-15.85, 8.15, -31.05], kind: "destination" },
  { id: "team", label: "Team", marker: teamCentre, kind: "destination" },
  { id: "aftermovie", label: "Aftermovie", marker: [0, 11.59, -45.72], kind: "destination" },
];

/** Keep the preview URL on the latest stop so refresh and sharing land there. */
export function startHref(href: string, start: CypherStart) {
  const url = new URL(href);
  if (start === "market") url.searchParams.delete("start");
  else url.searchParams.set("start", start);
  if (start !== "team") url.searchParams.delete("team");
  return url.href;
}
