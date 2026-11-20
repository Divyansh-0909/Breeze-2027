# Restore Rev15V1

Use Blender 4.3.2. Verify/extract this checkpoint ZIP (every payload hash is in PAYLOAD-SHA256.json). Download the two verified V source checkpoint parts listed in delivery/Base-V-Source-Checkpoint-Index.json. Reassemble them with this source/restore-checkpoint.py helper using --index delivery/Base-V-Source-Checkpoint-Index.json. It verifies both part hashes, the combined ZIP, CRCs and every payload hash. Extract V at the same repository root, then extract its embedded verified U3 source ZIP at that root.

Follow the recovered V RESTORE.md to obtain the thirteen immutable T2 base parts and T3/U1 native deltas, and reconstruct T2 -> T3 -> U1 -> U2 -> U3 -> V. Those file IDs, sizes and checksums are also preserved here in Base-V-Native-Dependency-Index.json and Base-Rev15T2-Native-Parts.json. Earlier verified assets are reused, not overwritten.

From the extracted repository root:

```bash
blender -b --python reports/events-wall-rev15v1-coloured-plaster-2026-11-14/source/build.py -- --restore --base /output/V.blend --output /output/V1.blend
```

The builder checks the V scene fingerprint, validates and packs all three new maps, preserves every face material outside the L2 wall selection and all original shape/UV/colour/transform data, and matches the original V1 fingerprint before saving. Actual reconstruction from the previously restored V and an independent fresh opening passed. Blender file serialization can change whole-file hashes while scene content remains identical. The complete restored master has 57 scenes and all resources packed.

The small native component and GLB contain changed wall surfaces only, with no Team or poster geometry. Do not place them on top of the old surface faces. They are authoring/runtime replacement components; restore the complete native scene with the command above. Full-world production website integration remains pending.
