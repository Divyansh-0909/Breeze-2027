import layout from "@/public/models/gullyverse/blockout.layout.json";
import type { Pose } from "./navigation";

/** Geometry, routes, collisions, signs and inspection cameras all read this registry. */
export const world = layout;
export type Destination = typeof world.destinations[number];
export const point3 = (p: readonly number[]): [number, number, number] => [p[0], p[1], p[2]];
export function lookAtPose(position: readonly number[], target: readonly number[]): Pose {
  const dx = target[0] - position[0], dy = target[1] - position[1], dz = target[2] - position[2];
  const horizontal = Math.hypot(dx,dz);
  return { x: position[0], y: position[1], z: position[2], yaw: horizontal < 0.00001 ? 0 : Math.atan2(-dx, -dz), pitch: Math.atan2(dy, horizontal) };
}
export function inspectionCamera(id: string) {
  const camera = world.cameras.find((entry) => entry.id === id);
  return camera ? { ...lookAtPose(camera.position, camera.target), fov: camera.fov } : null;
}
export function landingPose(): Pose {
  const p = world.landing.position;
  return { x: p[0], y: p[1], z: p[2], yaw: world.landing.yaw, pitch: world.landing.pitch };
}
export function filmPose(): Pose {
  const a = world.stage.origin, b = world.stage.filmFocusLocal;
  return { x: a[0] + b[0], y: a[1] + b[1], z: a[2] + b[2], yaw: world.stage.yaw, pitch: 0 };
}
/** Tube rings, entrance choreography and collision share this bent centreline. */
export function tunnelCenter(z: number): number {
  const points = world.tunnel.centerline;
  for (let i=0;i<points.length-1;i++) {
    const a=points[i],b=points[i+1];
    if (z<=a[1] && z>=b[1]) return a[0]+(b[0]-a[0])*(z-a[1])/(b[1]-a[1]);
  }
  return z>points[0][1] ? points[0][0] : points[points.length-1][0];
}
export type Obstacle = { id: string; x: number; z: number; halfX: number; halfZ: number };
function footprint(id: string, position: readonly number[], size: readonly number[], yaw = 0): Obstacle {
  const c = Math.abs(Math.cos(yaw)), s = Math.abs(Math.sin(yaw));
  return { id, x: position[0], z: position[2], halfX: (size[0] * c + size[2] * s) / 2, halfZ: (size[0] * s + size[2] * c) / 2 };
}
export const obstacles: Obstacle[] = [
  ...world.stalls.map((stall) => footprint(stall.id, stall.position, stall.size, stall.yaw)),
  ...world.destinations.filter((d) => d.id === "team" || d.id === "contact").map((d) => footprint(d.id, d.position, d.size, d.yaw)),
  ...world.destinations.filter((d) => d.status === "reserved").map((d) => footprint(d.id+"-sign", d.position, [7,1,0.14])),
  ...[-1, 1].map((side) => footprint(`scaffold-${side}`, [world.scaffold.position[0] + side * world.scaffold.width / 2, 0, world.scaffold.position[2]], [1.2, 0.5, world.scaffold.depth + 0.8])),
  // Enter the existing stage enclosure through the central gate, not its side walls.
  footprint("stage-enclosure", [world.stage.origin[0], 0, world.stage.origin[2] + 7.5], [49, 1, 39]),
];
// Convex excavation footprint in clockwise x/z order. Slide the capsule inside every face.
export function constrainQuarry(p: Pose) {
  const boundary = world.quarry.boundary, radius = world.playerRadius;
  const tunnel = world.tunnel, entry = world.portal.position[2], half = tunnel.walkHalfWidth;
  // Union of excavation, carved passage and front landing: walk back through
  // the same tunnel after returning from the stage, without a new scene/teleport.
  if (p.z > entry + radius) {
    p.x = Math.max(world.landing.walkBounds[0],Math.min(world.landing.walkBounds[1],p.x)); return;
  }
  if (p.z >= tunnel.endZ-radius*2 && p.z <= entry+radius && Math.abs(p.x-tunnelCenter(p.z)) <= half) return;
  const originalX=p.x, originalZ=p.z;
  for (let pass = 0; pass < 3; pass++) {
    for (let i = 0; i < boundary.length; i++) {
      const a = boundary[i], b = boundary[(i + 1) % boundary.length];
      const dx = b[0] - a[0], dz = b[1] - a[1], length = Math.hypot(dx, dz);
      const nx = dz / length, nz = -dx / length;
      const distance = (p.x - a[0]) * nx + (p.z - a[1]) * nz;
      if (distance < radius) { p.x += nx * (radius - distance); p.z += nz * (radius - distance); }
    }
    for (const o of obstacles) {
      const hx = o.halfX + radius, hz = o.halfZ + radius, dx = p.x - o.x, dz = p.z - o.z;
      if (Math.abs(dx) >= hx || Math.abs(dz) >= hz) continue;
      if (hx - Math.abs(dx) < hz - Math.abs(dz)) p.x = o.x + (dx < 0 ? -hx : hx);
      else p.z = o.z + (dz < 0 ? -hz : hz);
    }
  }
  if (originalZ >= tunnel.endZ-radius*2) {
    // Select the nearest legal point in the UNION. A side step inside the
    // tunnel must meet its wall, never project 10+ metres back into the quarry.
    let distance=(p.x-originalX)**2+(p.z-originalZ)**2;
    const tubeZ=Math.max(tunnel.endZ-radius*2,Math.min(entry+radius,originalZ));
    const center=tunnelCenter(tubeZ);
    const tubeX=Math.max(center-half,Math.min(center+half,originalX));
    const tubeDistance=(tubeX-originalX)**2+(tubeZ-originalZ)**2;
    if (tubeDistance<distance) {p.x=tubeX;p.z=tubeZ;distance=tubeDistance;}
    const frontX=Math.max(world.landing.walkBounds[0],Math.min(world.landing.walkBounds[1],originalX));
    const frontZ=Math.max(entry+radius,originalZ);
    if ((frontX-originalX)**2+(frontZ-originalZ)**2<distance) {p.x=frontX;p.z=frontZ;}
  }
}
