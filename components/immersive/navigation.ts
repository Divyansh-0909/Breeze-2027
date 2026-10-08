import layout from "@/public/models/gullyverse/blockout.layout.json";
import { obstacles } from "./world";

export type LocationId = "hub" | "aftermovie";
export type TravelId = LocationId | "entrance" | "events" | "team" | "contact" | "accommodation" | "sponsors";
export type RequestSource = "physical" | "map" | "url";
export type Pose = { x: number; y: number; z: number; yaw: number; pitch: number };
export const locations = {
  hub: { label: "Gullyverse", href: "/", spatial: layout.hub },
  aftermovie: { label: "Aftermovie", href: "/aftermovie", spatial: layout.aftermovie },
} as const;
// The distant stage position and nearby travel boundary are separate concepts.
export const connections = {
  hub: { to: "aftermovie" as LocationId, departure: 0.65, arrival: 0.75 },
  aftermovie: { to: "hub" as LocationId, departure: 0.65, arrival: 0.75 },
};
export type NavigationDestination = { id: TravelId; label: string; href: string | null; available: boolean; worldPosition: readonly number[] };
const spatialDestination = (id: string) => layout.destinations.find((d) => d.id === id)!;
export const destinationOptions: NavigationDestination[] = [
  { id: "hub", label: "Return to Hub", href: "/", available: true, worldPosition: layout.hub.spawn },
  { id: "aftermovie", label: "Main Stage / Aftermovie", href: "/aftermovie", available: true, worldPosition: layout.stage.origin },
  ...(["events", "team", "contact", "accommodation", "sponsors"] as const).map((id) => {
    const destination = spatialDestination(id);
    return { id, label: destination.label, href: destination.href, worldPosition: destination.position,
      // Existing middleware redirects /sponsors, so it is unavailable here.
      available: id === "events" || id === "team" || id === "contact" };
  }),
  { id: "entrance", label: "Entrance", href: "/", available: true, worldPosition: layout.portal.position },
];
export const navigationDestination = (id: TravelId) => destinationOptions.find((destination) => destination.id === id)!;
export const mapLabels = destinationOptions.filter((d) => !["hub", "entrance"].includes(d.id)).map((d) => d.label);
export const travelZones = layout.hub.travelZones.map((zone) => {
  const destination = navigationDestination(zone.id as TravelId);
  const a = layout.hub.movementBoundary[zone.edge], b = layout.hub.movementBoundary[(zone.edge + 1) % layout.hub.movementBoundary.length];
  const t = (zone.range[0] + zone.range[1]) / 2;
  return { ...destination, edge: zone.edge, range: zone.range, sign: zone.sign ?? null,
    center: [a[0] + (b[0] - a[0]) * t, layout.eyeHeight, a[1] + (b[1] - a[1]) * t] as const };
});
export function locationFromPath(path: string): LocationId | null {
  return path === "/" ? "hub" : path === "/aftermovie" ? "aftermovie" : null;
}
export function spawnPose(id: LocationId, approaching = false): Pose {
  const s = locations[id].spatial;
  const p = approaching ? s.arrivalStart : s.spawn;
  return { x: p[0], y: p[1], z: p[2], yaw: s.yaw, pitch: s.pitch };
}
export function movementBoundary(id: LocationId): readonly (readonly number[])[] { return locations[id].spatial.movementBoundary; }
export function localObstacles(id: LocationId) {
  const b=locations[id].spatial.bounds;
  return obstacles.filter((o)=>
    // The broad stage reservation protects the hub's distant exterior, while
    // the Aftermovie viewing gate intentionally sits inside that reservation.
    !(id==="aftermovie" && o.id==="stage-enclosure") &&
    o.x+o.halfX>b[0] && o.x-o.halfX<b[1] && o.z+o.halfZ>b[2] && o.z-o.halfZ<b[3]);
}
const localFootprints={hub:localObstacles("hub"),aftermovie:localObstacles("aftermovie")};
export function constrainInterior(id: LocationId,p:Pose):void {
  for(const o of localFootprints[id]) {
    const hx=o.halfX+layout.playerRadius,hz=o.halfZ+layout.playerRadius,dx=p.x-o.x,dz=p.z-o.z;
    if(Math.abs(dx)>=hx || Math.abs(dz)>=hz) continue;
    if(hx-Math.abs(dx)<hz-Math.abs(dz)) p.x=o.x+(dx<0?-hx:hx);
    else p.z=o.z+(dz<0?-hz:hz);
  }
}
export function boundaryClearance(id: LocationId, p: Pick<Pose, "x" | "z">): number {
  const polygon = movementBoundary(id);
  let clearance = Infinity;
  for (let i = 0; i < polygon.length; i++) {
    const a = polygon[i], b = polygon[(i + 1) % polygon.length];
    const dx = b[0] - a[0], dz = b[1] - a[1], length = Math.hypot(dx, dz);
    clearance = Math.min(clearance, ((p.x - a[0]) * dz - (p.z - a[1]) * dx) / length - layout.playerRadius);
  }
  return clearance;
}
/** Swept crossing of OUTER faces only; obstacles never call this detector. */
export function boundaryCrossings(id: LocationId, before: Pick<Pose, "x" | "z">, attempted: Pick<Pose, "x" | "z">) {
  const polygon = movementBoundary(id), radius = layout.playerRadius;
  const moveX = attempted.x - before.x, moveZ = attempted.z - before.z, moveLength = Math.hypot(moveX, moveZ);
  const crossings: { edge: number; t: number; outward: number }[] = [];
  if (moveLength < 0.000001) return crossings;
  for (let i = 0; i < polygon.length; i++) {
    const a = polygon[i], b = polygon[(i + 1) % polygon.length];
    const dx = b[0] - a[0], dz = b[1] - a[1], length = Math.hypot(dx, dz), nx = dz / length, nz = -dx / length;
    const start = (before.x - a[0]) * nx + (before.z - a[1]) * nz;
    const end = (attempted.x - a[0]) * nx + (attempted.z - a[1]) * nz;
    if (start < radius - 0.00001 || end >= radius - 0.000001) continue;
    const outward = -(moveX * nx + moveZ * nz) / moveLength;
    if (outward <= 0.001) continue;
    const fraction = Math.max(0, Math.min(1, (start - radius) / (start - end)));
    const x = before.x + moveX * fraction, z = before.z + moveZ * fraction;
    const t = ((x - a[0]) * dx + (z - a[1]) * dz) / (length * length);
    crossings.push({ edge: i, t, outward });
  }
  return crossings;
}
export function crossedHubDestination(crossings: ReturnType<typeof boundaryCrossings>): TravelId | null {
  for (const crossing of [...crossings].sort((a, b) => b.outward - a.outward)) {
    // Gaps and outward intent reject tangent sliding into adjacent zones.
    if (crossing.outward < 0.55) continue;
    const zone = travelZones.find((z) => z.edge === crossing.edge && crossing.t >= z.range[0] && crossing.t <= z.range[1]);
    if (zone) return zone.id;
  }
  return null;
}
export function constrain(id: LocationId, p: Pose): void {
  constrainInterior(id,p);
  const polygon = movementBoundary(id), radius = layout.playerRadius;
  for (let pass = 0; pass < 12; pass++) {
    let correction=0;
    for (let i = 0; i < polygon.length; i++) {
      const a = polygon[i], b = polygon[(i + 1) % polygon.length];
      const dx = b[0] - a[0], dz = b[1] - a[1], length = Math.hypot(dx, dz), nx = dz / length, nz = -dx / length;
      const distance = (p.x - a[0]) * nx + (p.z - a[1]) * nz;
      if (distance < radius) { const shift=radius-distance;p.x += nx*shift;p.z += nz*shift;correction=Math.max(correction,shift); }
    }
    if(correction<0.000001) break;
  }
}
