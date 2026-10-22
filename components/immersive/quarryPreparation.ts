import * as THREE from "three";

/** Warm the private material's existing quarry LODs without redrawing the
 * original stage/crowd under the cover. One existing renderer/context; no FBO,
 * scene duplication, changed lights or persistent layer changes. */
export function renderQuarryPreparation(
  renderer: Pick<THREE.WebGLRenderer, "render">,
  scene: THREE.Scene,
  camera: THREE.Camera,
  quarry: THREE.Object3D,
) {
  let occupied = camera.layers.mask;
  scene.traverse(object => { occupied |= object.layers.mask; });
  let spare = 31;
  while (spare > 0 && (occupied & (1 << spare)) !== 0) spare--;
  if (spare === 0) { renderer.render(scene, camera); return; }

  const cameraMask = camera.layers.mask;
  const original = new Map<THREE.Object3D, number>();
  const include = (object: THREE.Object3D) => {
    if (!original.has(object)) original.set(object, object.layers.mask);
    object.layers.enable(spare);
  };
  try {
    quarry.traverse(include);
    scene.traverse(object => {
      if (object instanceof THREE.Light && object.layers.test(camera.layers)) include(object);
    });
    camera.layers.set(spare);
    renderer.render(scene, camera);
  } finally {
    camera.layers.mask = cameraMask;
    for (const [object, mask] of original) object.layers.mask = mask;
  }
}
