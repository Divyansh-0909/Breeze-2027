import { Camera, Vector4 } from 'three';
/** Clip-space validity must be checked before dividing by W. */
export function projectMapPoint(position: readonly number[], camera: Camera, width: number, height: number, clip = new Vector4()) {
  if (![...position, width, height].every(Number.isFinite) || width <= 0 || height <= 0) return null;
  clip.set(position[0], position[1], position[2], 1).applyMatrix4(camera.matrixWorldInverse).applyMatrix4(camera.projectionMatrix);
  const { x, y, z, w } = clip;
  if (![x, y, z, w].every(Number.isFinite) || w <= 1e-8 || Math.abs(x) > w || Math.abs(y) > w || Math.abs(z) > w) return null;
  return { x: (x / w + 1) * width / 2, y: (1 - y / w) * height / 2 };
}
