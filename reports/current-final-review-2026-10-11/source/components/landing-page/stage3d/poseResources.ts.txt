import type { BufferGeometry } from 'three';
const released = new WeakSet<BufferGeometry>();
/** Only unpublished operation-owned poses may be freed; the shared cache is protected. */
export function disposeUnpublishedPoses(poses: readonly BufferGeometry[], cached: readonly BufferGeometry[] | null) {
  for (const pose of poses) {
    if (cached?.includes(pose) || released.has(pose)) continue;
    released.add(pose); pose.dispose();
  }
}
