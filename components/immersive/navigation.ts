import layout from "@/public/models/gullyverse/blockout.layout.json";

export type LocationId = "hub" | "aftermovie";
export type RequestSource = "physical" | "map" | "url";
export type Pose = { x: number; y: number; z: number; yaw: number; pitch: number };
export const locations = {
  hub: { label: "Gullyverse", href: "/", spatial: layout.hub },
  aftermovie: { label: "Aftermovie", href: "/aftermovie", spatial: layout.aftermovie },
} as const;
// An edge owns the route commitment and cinematic pacing. There is no Main Stage ID.
export const connections = {
  hub: { to: "aftermovie" as LocationId, threshold: layout.hub.route, departure: 1.05, arrival: 1.15 },
  aftermovie: { to: "hub" as LocationId, threshold: layout.aftermovie.route, departure: 1.05, arrival: 1.15 },
};
export const mapLabels = ["Events", "Aftermovie", "Team", "Contact Us", "Past Sponsors", "Accommodation"];
export function locationFromPath(path: string): LocationId | null {
  return path === "/" ? "hub" : path === "/aftermovie" ? "aftermovie" : null;
}
export function spawnPose(id: LocationId, approaching = false): Pose {
  const s = locations[id].spatial;
  const p = approaching ? s.arrivalStart : s.spawn;
  return { x: p[0], y: p[1], z: p[2], yaw: s.yaw, pitch: s.pitch };
}
export function insideThreshold(id: LocationId, p: Pose): boolean {
  const t = connections[id].threshold;
  return p.x >= t.xMin && p.x <= t.xMax && p.z >= t.zMin && p.z <= t.zMax;
}
export function constrain(id: LocationId, p: Pose): void {
  const b = locations[id].spatial.bounds;
  p.x = Math.max(b[0], Math.min(b[1], p.x));
  p.z = Math.max(b[2], Math.min(b[3], p.z));
}
