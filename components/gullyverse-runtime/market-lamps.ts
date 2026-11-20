import { Mesh, MeshStandardMaterial, type Object3D } from "three";

// Rev15W authored these holds at 30 fps. The 8.4 s cycle starts
// 81 frames ahead for L06. Road illumination is baked separately.
const flickerHolds = [[53, 58, 0.18], [140, 145, 0.35], [206, 212, 0.06]] as const;
const lampStates = {
  L01: "steady", L02: "dead", L03: "flicker",
  L04: "steady", L05: "dead", L06: "flicker",
} as const;
type LampId = keyof typeof lampStates;

export function lampEmission(id: LampId, seconds: number, reduced: boolean) {
  const state = lampStates[id];
  if (state === "dead") return 0;
  if (state === "steady" || reduced) return 6;
  const frame = Math.floor(seconds * 30 + (id === "L06" ? 81 : 0)) % 252;
  return 6 * (flickerHolds.find(([start, end]) => frame >= start && frame < end)?.[2] ?? 1);
}

export function mountMarketLamps(roots: Object3D[]) {
  const lenses = new Map<LampId, { mesh: Mesh; original: MeshStandardMaterial; material: MeshStandardMaterial }>();
  try {
    for (const root of roots) root.traverse(object => {
      const id = object.userData.streetLampId as LampId;
      if (!Object.hasOwn(lampStates, id) || object.userData.streetLampPart !== "lens") return;
      if (!(object instanceof Mesh) || !(object.material instanceof MeshStandardMaterial)
          || lenses.has(id) || object.userData.lampState !== lampStates[id]) {
        throw new Error(`The frozen lamp ${id} is missing its expected lens.`);
      }
      const original = object.material;
      const material = original.clone();
      material.onBeforeCompile = original.onBeforeCompile;
      material.customProgramCacheKey = original.customProgramCacheKey;
      material.emissive.setRGB(1, 0.72, 0.43);
      material.emissiveIntensity = lampEmission(id, 0, true);
      object.material = material;
      lenses.set(id, { mesh: object, original, material });
    });
    if (lenses.size !== 6) throw new Error("The lane export does not contain all six streetlights.");
  } catch (error) {
    dispose();
    throw error;
  }
  function dispose() {
    for (const { mesh, original, material } of lenses.values()) {
      mesh.material = original;
      material.dispose();
    }
    lenses.clear();
  }
  let seconds = 0;
  return {
    advance(delta: number, reduced: boolean) {
      if (!reduced) seconds += delta;
      for (const [id, { material }] of lenses) material.emissiveIntensity = lampEmission(id, seconds, reduced);
    },
    dispose,
  };
}
