import type { Pose } from "../immersive/navigation";
import type { RuntimeSpace } from "../immersive/runtime";
import { lookAtPose, world } from "../immersive/world";
import walkSpace from "./cypher-walk-space.json";
import plazaSpace from "./plaza-walk-space.json";

type Point = { x: number; z: number };
type Segment = readonly [number, number, number, number];
type Limits = { start: number; end: number; halfWidth: number; spawnY: number; spawnPitch?: number; plaza?: boolean };
type Strip = typeof walkSpace.strips[number] & { endHalfWidth?: number };
const { eyeHeight } = world;
const radius = world.playerRadius;

export function createCypherSpace(limits?: Limits) {
  const rooftop = walkSpace.strips.at(-1)!;
  if (limits?.plaza && (plazaSpace.sourceSHA256 !== walkSpace.sourceSHA256 || plazaSpace.deck !== rooftop.source)) {
    throw new Error("The cypher deck and its walking footprint have different sources.");
  }
  const sourceStrips: Strip[] = limits?.plaza ? [
    ...walkSpace.strips.slice(0, -1),
    ...plazaSpace.strips.map(strip => ({ ...rooftop, ...strip })),
  ] : walkSpace.strips;
  const solids = limits?.plaza ? [...walkSpace.solids, ...plazaSpace.solids] : walkSpace.solids;
  const people = limits?.plaza ? plazaSpace.people : [];
  const strips = sourceStrips.flatMap(strip => {
    const from = Math.max(strip.start, limits?.start ?? strip.start);
    const to = Math.min(strip.end, limits?.end ?? strip.end);
    if (from >= to) return [];
    const widthAt = (y: number) => Math.min(
      strip.halfWidth + ((strip.endHalfWidth ?? strip.halfWidth) - strip.halfWidth) * (y - strip.start) / (strip.end - strip.start),
      limits?.halfWidth ?? Infinity,
    );
    return [{ ...strip, from, to, leftWidth: widthAt(from), rightWidth: widthAt(to), widthAt }];
  });
  if (!strips.length) {
    throw new Error("The cypher walk space needs a continuous road section.");
  }

  // Trace the outside of the union of the road strips. Internal seams are
  // traversable, including the ramp/apron join where the width changes.
  const edges: Segment[] = [];
  const first = strips[0], last = strips[strips.length - 1];
  edges.push([-first.leftWidth, first.from, first.leftWidth, first.from], [-last.rightWidth, last.to, last.rightWidth, last.to]);
  strips.forEach((strip, index) => {
    for (const side of [-1, 1]) {
      const xEnd = side * strip.rightWidth;
      edges.push([side * strip.leftWidth, strip.from, xEnd, strip.to]);
      const next = strips[index + 1];
      if (next && strip.rightWidth !== next.leftWidth) edges.push([xEnd, strip.to, side * next.leftWidth, strip.to]);
    }
  });

  const stripAt = (x: number, y: number) => strips.find(s => y >= s.from && y <= s.to && Math.abs(x) <= s.widthAt(y));
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
      const ex = bx - ax, ey = by - ay;
      const t = Math.max(0, Math.min(1, ((x - ax) * ex + (y - ay) * ey) / (ex * ex + ey * ey)));
      const dx = x - (ax + t * ex), dy = y - (ay + t * ey);
      nearest = Math.min(nearest, dx * dx + dy * dy);
    }
    for (const { bounds: [minX, minY, maxX, maxY] } of solids) {
      const dx = Math.max(minX - x, 0, x - maxX);
      const dy = Math.max(minY - y, 0, y - maxY);
      nearest = Math.min(nearest, dx * dx + dy * dy);
    }
    for (const [personX, personY, personRadius] of people) {
      const dx = personX - x, dy = personY - y;
      const reach = personRadius + radius;
      if (dx * dx + dy * dy < reach * reach) return Math.hypot(dx, dy) - reach;
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
