import type { Material, MeshStandardMaterial, Object3D } from "three";

/**
 * Which market lights are on (user request, 26 November 2026): the gooseneck sign-wash lamps above the shop
 * signboards stay off. The tube lights under the awnings, the shelf tubes inside the shops and the street
 * lights (market-lamps.ts) stay as they are.
 *
 * The locked master bakes the sign washes into the chunk lightmaps, so switching them off at runtime means:
 * the lamp heads stop glowing, they no longer drive lamp highlights (fidelity.ts), and the signboards, which
 * took almost all of their light, keep only a fraction of their baked light.
 */
export const switchedOff = /sign wash/i;
const lampHead = /warm lamp face/i;
const signboard = /Hand-painted/i;
/** Share of a signboard's baked light that is left once its wash lamps are off (street and shop light). */
const signboardLight = 0.3;

/** Call on a chunk before its lighting is bound (the signboard scale is read by the lightmap shader). */
export function switchOffSignLamps(root: Object3D) {
  const done = new Set<Material>();
  root.traverse(object => {
    const materials = (object as { material?: Material | Material[] }).material;
    if (!materials) return;
    for (const m of (Array.isArray(materials) ? materials : [materials]) as MeshStandardMaterial[]) {
      if (done.has(m)) continue;
      done.add(m);
      if (lampHead.test(m.name)) {
        m.emissive?.setRGB(0, 0, 0);
        m.emissiveIntensity = 0;
        // The diffuser also baked its own glow.
        m.userData.breezeLightScale = 0.3;
        m.needsUpdate = true;
      } else if (signboard.test(m.name)) {
        m.userData.breezeLightScale = signboardLight;
        // The paint's faint self-glow kept the lettering readable under the lamps; keep a little of it.
        m.emissiveIntensity *= 0.5;
        m.needsUpdate = true;
      }
    }
  });
}
