import type { Pose } from "../immersive/navigation";
import type { RuntimeSpace } from "../immersive/runtime";
import { lookAtPose } from "../immersive/world";

export type ContactSpaceConfig = {
  sourceSHA256: string;
  normal: number[]; tangent: number[]; centreU: number; wallDepth: number;
  floor: number; eyeHeight: number; playerRadius: number;
  walkU: number[]; walkDepth: number[]; triggerU: number; triggerDepth: number; triggerRadius: number;
};

/** Source-local u/depth -> Blender XYZ -> Three X/Y/Z, with no geometry rescale. */
export function contactSpace(config: ContactSpaceConfig) {
  const normal = config.normal.map(x => x / Math.hypot(...config.normal));
  const tangent = config.tangent.map(x => x / Math.hypot(...config.tangent));
  if (Math.abs(normal[0] * tangent[0] + normal[1] * tangent[1]) > 1e-5) throw Error("Native frame is not orthogonal");
  const point = (u: number, depth: number, height = config.floor + config.eyeHeight): [number, number, number] =>
    [tangent[0] * u + normal[0] * depth, height, -(tangent[1] * u + normal[1] * depth)];
  const local = (p: Pick<Pose, "x" | "z">) => ({ u: p.x * tangent[0] - p.z * tangent[1], depth: p.x * normal[0] - p.z * normal[1] });
  const radius = config.playerRadius;
  const clamp = (pose: Pose) => {
    const { u, depth } = local(pose);
    const safeU = Math.max(config.walkU[0] + radius, Math.min(config.walkU[1] - radius, u));
    const safeDepth = Math.max(config.walkDepth[0] + radius, Math.min(config.walkDepth[1] - radius, depth));
    if (safeU !== u || safeDepth !== depth) {
      const p = point(safeU, safeDepth); pose.x = p[0]; pose.z = p[2];
    }
    pose.y = config.floor + config.eyeHeight;
  };
  const target = point(config.centreU, config.wallDepth, 8.95);
  const spawn = () => lookAtPose(point(config.centreU, -16.15), point(config.centreU, config.wallDepth));
  const focus = () => lookAtPose(point(config.centreU, config.wallDepth + 6.7, 8.95), target);
  const near = (pose: Pose) => {
    const p = local(pose);
    return Math.hypot(p.u - config.triggerU, p.depth - config.triggerDepth) <= config.triggerRadius;
  };
  const clearance = (pose: Pose) => {
    const p = local(pose);
    return Math.min(p.u - config.walkU[0], config.walkU[1] - p.u, p.depth - config.walkDepth[0], config.walkDepth[1] - p.depth) - radius;
  };
  const space: RuntimeSpace = {
    spawn, constrain: (_id, p) => clamp(p), constrainInterior: (_id, p) => clamp(p),
    boundaryClearance: (_id, p) => clearance(p), boundaryCrossings: () => [],
    composeCamera: (base, aspect) => ({ ...base, fov: Math.max(35.6, Math.min(85, 2 * Math.atan(Math.tan(35.6 * Math.PI / 360) / Math.max(aspect, 0.3)) * 180 / Math.PI)) }),
    mapCamera: aspect => ({ ...lookAtPose(point(config.centreU, -18.2, 20), point(config.centreU, -18.2, config.floor)), pitch: -Math.PI / 2, fov: aspect < 1 ? 68 : 45 }),
  };
  return { space, point, local, spawn, focus, near, clearance, clamp };
}
