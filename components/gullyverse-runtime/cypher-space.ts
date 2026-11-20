import type { Pose } from "../immersive/navigation";
import type { RuntimeSpace } from "../immersive/runtime";
import { lookAtPose, world } from "../immersive/world";
import walkSpace from "./cypher-walk-space.json";

type Point = { x: number; z: number };
type Segment = readonly [number, number, number, number];
type Limits = { start: number; end: number; halfWidth: number; spawnY: number; spawnPitch?: number };
const { eyeHeight } = world;
const radius = world.playerRadius;

export function createCypherSpace(limits?: Limits) {
  const strips = walkSpace.strips.flatMap(strip => {
    const start = Math.max(strip.start, limits?.start ?? strip.start);
    const end = Math.min(strip.end, limits?.end ?? strip.end);
    return start < end ? [{ ...strip, from: start, to: end, width: Math.min(strip.halfWidth, limits?.halfWidth ?? Infinity) }] : [];
  });
  if (!strips.length) {
    throw new Error("The cypher walk space needs a continuous road section.");
  }

  // Trace the outside of the union of the road strips. Internal seams are
  // traversable, including the ramp/apron join where the width changes.
  const edges: Segment[] = [];
  const first = strips[0], last = strips[strips.length - 1];
  edges.push([-first.width, first.from, first.width, first.from], [-last.width, last.to, last.width, last.to]);
  strips.forEach((strip, index) => {
    for (const side of [-1, 1]) {
      const x = side * strip.width;
      edges.push([x, strip.from, x, strip.to]);
      const next = strips[index + 1];
      if (next && strip.width !== next.width) edges.push([x, strip.to, side * next.width, strip.to]);
    }
  });

  const stripAt = (x: number, y: number) => strips.find(s => y >= s.from && y <= s.to && Math.abs(x) <= s.width);
  function grade(p: Point) {
    const y = -p.z;
    const strip = stripAt(p.x, y);
    if (!strip) return undefined;
    return strip.startHeight + (strip.endHeight - strip.startHeight) * (y - strip.start) / (strip.end - strip.start);
  }

  function clearance(p: Point) {
    const x = p.x, y = -p.z;
    if (!stripAt(x, y)) return -Infinity;
    let nearest = Infinity;
    for (const [ax, ay, bx, by] of edges) {
      const dx = Math.max(Math.min(ax, bx) - x, 0, x - Math.max(ax, bx));
      const dy = Math.max(Math.min(ay, by) - y, 0, y - Math.max(ay, by));
      nearest = Math.min(nearest, dx * dx + dy * dy);
    }
    for (const { bounds: [minX, minY, maxX, maxY] } of walkSpace.solids) {
      const dx = Math.max(minX - x, 0, x - maxX);
      const dy = Math.max(minY - y, 0, y - maxY);
      nearest = Math.min(nearest, dx * dx + dy * dy);
    }
    return Math.sqrt(nearest) - radius;
  }

  function resolve(before: Point, desired: Point): Point {
    let x = before.x, z = before.z;
    const distance = Math.hypot(desired.x - x, desired.z - z);
    const steps = Math.max(1, Math.ceil(distance / (radius / 4)));
    const dx = (desired.x - x) / steps, dz = (desired.z - z) / steps;
    for (let i = 0; i < steps; i++) {
      if (clearance({ x: x + dx, z: z + dz }) >= 0) { x += dx; z += dz; continue; }
      // Keep the component of motion along a wall so diagonal walking slides.
      if (clearance({ x: x + dx, z }) >= 0) x += dx;
      if (clearance({ x, z: z + dz }) >= 0) z += dz;
    }
    return { x, z };
  }

  const spawnY = limits?.spawnY ?? -27;
  const spawn = () => {
    const position = { x: 0, z: -spawnY };
    const floor = grade(position);
    if (floor === undefined || clearance(position) < 0) throw new Error("The cypher spawn is outside the walk space.");
    const eye = floor + eyeHeight;
    return {
      ...lookAtPose([0, eye, position.z], [0, eye, position.z - 1]),
      pitch: limits?.spawnPitch ?? 0,
    };
  };
  function constrain(pose: Pose) {
    const floor = grade(pose);
    if (floor === undefined || clearance(pose) < 0) Object.assign(pose, spawn());
    else pose.y = floor + eyeHeight;
  }

  const space: RuntimeSpace = {
    spawn,
    constrain: (_id, pose) => constrain(pose),
    constrainInterior: (_id, pose, before) => {
      Object.assign(pose, resolve(before, pose));
      constrain(pose);
    },
    boundaryClearance: (_id, pose) => clearance(pose),
    boundaryCrossings: () => [],
    composeCamera: (base, aspect) => ({
      ...base,
      fov: Math.min(85, Math.max(world.camera.fov, 2 * Math.atan(Math.tan(world.camera.fov * Math.PI / 360) / aspect) * 180 / Math.PI)),
    }),
    mapCamera: aspect => ({
      ...lookAtPose([0, 38, -(first.from + last.to) / 2], [0, 7.2, -(first.from + last.to) / 2 - 0.01]),
      pitch: -Math.PI / 2,
      fov: aspect < 1 ? 80 : 68,
    }),
  };
  return { space, grade, clearance, resolve };
}
