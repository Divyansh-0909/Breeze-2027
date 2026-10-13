import type { VideoTexture } from 'three';
type Owner = { stopped: boolean; disposed: boolean; consumers: number };
const owners = new WeakMap<VideoTexture, Owner>();
function collect(texture: VideoTexture, owner: Owner) {
  if (owner.stopped && owner.consumers === 0 && !owner.disposed) { owner.disposed = true; texture.dispose(); }
}
export function ownVideoTexture(texture: VideoTexture) { owners.set(texture, { stopped: false, disposed: false, consumers: 0 }); }
/** LED samplers hold a lease until their rendered fade reaches zero and they detach. */
export function retainVideoTexture(texture: VideoTexture): () => void {
  const owner = owners.get(texture);
  if (!owner) return () => {}; // non-owned external textures retain their caller's policy
  if (owner.stopped || owner.disposed) throw new Error('Cannot bind a retired video texture');
  owner.consumers++; let released = false;
  return () => { if (released) return; released = true; owner.consumers--; collect(texture, owner); };
}
export function retireVideoTexture(texture: VideoTexture) {
  const owner = owners.get(texture);
  if (!owner) return;
  owner.stopped = true; collect(texture, owner);
}
