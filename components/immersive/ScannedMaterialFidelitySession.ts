import * as THREE from "three";
import {ScannedRockMaterialSession} from "./ScannedRockMaterialSession";
import type {ImmersiveRuntime} from "./runtime";

export const FIDELITY_PART_IDS = ["Wall_14", "Wall_15", "Wall_16"] as const;
export const FIDELITY_NODES = FIDELITY_PART_IDS.flatMap(id =>
  [0, 1, 2].map(level => `Foundation_${id}_LOD${level}`));

/** Restore the documented 35.557m material scope. The lost lower/upper C6.2
 * visual IDs were not the surviving C5.1 sector IDs. This separate preview
 * borrows the unchanged C8 owner and every unchanged C5.1 geometry buffer. */
export class ScannedMaterialFidelitySession extends ScannedRockMaterialSession {
  constructor(runtime: ImmersiveRuntime) { super(runtime, 3); }

  override load() {
    this.textureScale = 3;
    return super.load();
  }

  override cloneForRendering() {
    const clone = super.cloneForRendering(), material = this.borrowScannedMaterial();
    if (clone && material && this.foundationEnabled && this.scannedEnabled) {
      for (const name of FIDELITY_NODES) {
        const object = clone.getObjectByName(name);
        if (!(object instanceof THREE.Mesh)) throw new Error("Fidelity material host missing: " + name);
        object.material = material;
      }
    }
    return clone;
  }

  override materialDiagnostics() {
    return {...super.materialDiagnostics(), host: "unchanged C5.1 sectors14/15/16",
      selectedNodes: FIDELITY_NODES, fidelityMaterial: true,
      regionArcMetres: [311.02719558677654, 346.5843803697403],
      regionLengthMetres: 35.55718478296376, newTextureImages: 0};
  }
}
