# Restore Rev15V2

Use Blender 4.3.2. Verify and extract this checkpoint ZIP into a new repository directory. PAYLOAD-SHA256.json records every payload hash. The native component, runtime GLB, full source, captures, PDF, viewer and licenses are included; the complete world is recovered using the verified unchanged base chain below.

1. Download the verified V1 source ZIP listed in delivery/Base-V1-Source-Checkpoint-Index.json and verify its SHA-256, ZIP CRCs and payload hashes. Extract at the same repository root. It includes the Events plaster source/maps and all prior dependency indexes.
2. Download both V source parts listed in delivery/Base-V-Source-Checkpoint-Index.json. Reassemble with source/restore-checkpoint.py using that --index path, then extract at the same root. The helper verifies parts, complete ZIP and every payload. Extract V's embedded verified U3 source ZIP at that root as described in V RESTORE.md.
3. Obtain the thirteen complete T2 native parts plus the T3 and U1 packed native deltas from the included indexes. Follow V RESTORE.md to reconstruct T2 -> T3 -> U1 -> U2 -> U3 -> V. Follow V1 RESTORE.md to reconstruct V1, including its three packed plaster maps.
4. From the extracted repository root run:

```bash
blender -b --python reports/cypher-entry-rev15v2-open-steel-gate-2026-11-14/source/build.py -- --restore --base /output/V1.blend --output /output/V2.blend
```

The builder refuses to overwrite an existing output. It verifies the V1 scene fingerprint, adds the new gate/boundary geometry, checks every original object and earlier scene membership, and matches the V2 scene fingerprint before saving. Actual reconstruction from verified V1 and a separate fresh opening passed, including gate angle/direction, old materials/geometry/UVs/transforms, all eight mural states and the Events posters. V1 previously passed reconstruction from restored V. Whole-file serialization checksums may differ. The resulting complete native master contains all 58 scenes and packed resources.

Rev15V2-Open-Steel-Cypher-Gate.blend is an editable new-object native component, not the complete world. Unlike the earlier replacement wall-surface components, this gate component contains additions only. Append it once to the matching V1 scene if editing manually; source reconstruction is the tested method for reproducing the complete V2 scene and its history.

For the isolated browser viewer, copy delivery/Rev15V2-Open-Steel-Cypher-Gate.glb to viewer/gate.glb, serve viewer over local HTTP and open index.html. Required Three.js files and license are included. Viewer lights/floor are diagnostic and are absent from the native master. The PDF's night capture uses original saved world lights/exposure. Full-world website integration and its collision/navigation registry update remain pending; no live walking test is claimed.

## Preserve the latest documentation when extracting dependencies

Older dependency ZIPs also contain historical docs. After extracting all dependency archives, re-extract the verified V1 source ZIP and then the current V2 source ZIP, in that order, over the repository. This restores the latest source and V2 documentation last while retaining all dependency files. Use this separately supplied RESTORE.md and the current outer Checkpoint-Index.json for these extraction-order notes; the immutable ZIP snapshot contains the preceding instructions. This affects documentation extraction order only; native reconstruction checks are unchanged.
