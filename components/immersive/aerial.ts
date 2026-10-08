import { world } from "./world";
import type { LocationId, Pose } from "./navigation";

export type CameraView = Pose & { fov: number };
const radians = Math.PI / 180;
const ease = (value: number) => { const t = Math.max(0, Math.min(1, value)); return t * t * (3 - 2 * t); };

/** Fit the actual rim, tunnel and portal, rather than the oversized ground plane. */
export function mapCamera(aspect: number): CameraView {
  const rim = world.quarry.boundary;
  const middleX = (Math.min(...rim.map(p => p[0])) + Math.max(...rim.map(p => p[0]))) / 2;
  const middleZ = (Math.min(...rim.map(p => p[1])) + world.landing.position[2]) / 2;
  const samples: [number, number, number][] = [];
  rim.forEach(([x, z], i) => {
    const distance = Math.hypot(x - middleX, z - middleZ);
    const outerX = x + (x - middleX) / distance * 6;
    const outerZ = z + (z - middleZ) / distance * 6;
    samples.push([x, 0, z], [outerX, world.quarry.wallHeights[i % world.quarry.wallHeights.length], outerZ]);
  });
  samples.push([-world.portal.width / 2, world.portal.height, 0], [world.portal.width / 2, world.portal.height, 0], [0, 0, world.landing.position[2]]);
  // In landscape the long quarry axis uses the screen's long axis. Rotation is
  // continuous across resize, and the descent reverses it to the saved heading.
  const landscape = ease((aspect - 0.72) / 0.8);
  const yaw = -Math.PI / 2 * landscape;
  const fov = 80 - 16 * landscape;
  const halfVertical = Math.tan(fov * radians / 2);
  const halfHorizontal = halfVertical * Math.max(0.25, aspect);
  const c = Math.cos(yaw), s = Math.sin(yaw);
  let altitude = 1;
  for (const [x, y, z] of samples) {
    const dx = x - middleX, dz = z - middleZ;
    const screenX = c * dx - s * dz;
    const screenY = -s * dx - c * dz;
    altitude = Math.max(altitude, y + Math.max(Math.abs(screenX) / halfHorizontal, Math.abs(screenY) / halfVertical) * 1.065);
  }
  return { x: middleX, y: altitude, z: middleZ, yaw, pitch: -Math.PI / 2, fov };
}

/** Portrait fitting is specific to the composition, not a blanket 93° lens. */
export function composeCamera(base: CameraView, aspect: number, scene: LocationId, inspection: string | null, phase: string): CameraView {
  if (inspection === "overview") return mapCamera(aspect);
  if (scene === "aftermovie" && !inspection) return base;
  const landing = inspection === "landing" || (!inspection && ["boot", "landing"].includes(phase));
  const tunnel = inspection?.startsWith("tunnel") || (!inspection && base.z > world.tunnel.endZ && !landing);
  const minimumHorizontal = tunnel ? 34 : 42;
  const fitted = 2 * Math.atan(Math.tan(minimumHorizontal * radians / 2) / Math.max(aspect, 0.25)) / radians;
  return { ...base, fov: Math.max(base.fov, Math.min(82, fitted)) };
}
