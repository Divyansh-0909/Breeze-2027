# Restore Rev15V

Use Blender 4.3.2. Download the source checkpoint parts and Checkpoint-Index.json. Reassemble with the separately supplied source/restore-checkpoint.py helper, which checks every part, the whole ZIP, CRCs and every payload hash. Extract the verified ZIP to a new repository directory. Do not overwrite a different working copy.

The V checkpoint embeds the verified U3 source checkpoint in this report's dependencies directory. Extract that embedded ZIP at the same repository root to restore all prior T3/U1/U2/U3 recovery modules, fingerprints and required proofs under their original report paths. Verify its SHA-256 against delivery/Dependency-Index.json. It contains no credentials or dependencies.

Download all thirteen T2 native parts, the T3 packed ground delta and the U1 packed bilingual styling delta using IDs and checksums in delivery/Base-Rev15T2-Native-Parts.json and delivery/Dependency-Index.json. From the extracted repository root, run with your actual paths:

```bash
python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-master.py /downloads/base-parts /output/T2.blend --index reports/cypher-houses-rev15v-walls-windows-2026-11-14/delivery/Base-Rev15T2-Native-Parts.json
blender -b --python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-native.py -- --base /output/T2.blend --delta /downloads/Rev15T3-Rebuilt-Potholes-Additions.blend --output /output/T3.blend
blender -b --python reports/navigation-board-rev15u-highway-green-2026-11-13/source/restore-native.py -- --base /output/T3.blend --delta /downloads/Rev15U1-Bilingual-Highway-Sign-Styling.blend --output /output/U1.blend
blender -b --python reports/navigation-board-rev15u2-english-centred-2026-11-14/source/build.py -- --restore --base /output/U1.blend --output /output/U2.blend
blender -b --python reports/navigation-board-rev15u3-larger-english-text-2026-11-14/source/build.py -- --restore --base /output/U2.blend --output /output/U3.blend
blender -b --python reports/cypher-houses-rev15v-walls-windows-2026-11-14/source/build.py -- --restore --base /output/U3.blend --output /output/V.blend
```

Each builder refuses to overwrite an existing output. V checks the exact U3 scene fingerprint before editing, validates the authored map hashes before packing, preserves every unedited face material and original shape/UV/colour/transform, and matches the V scene fingerprint before saving. The complete V master has all 56 historical/current scenes and packed resources. Actual reconstruction from the prior phase's restored U3, followed by an independent fresh opening, passed; whole-file checksums can differ after Blender serialization. Check evidence/restore-check.json, evidence/restored-fresh-open.json and the original master hash in evidence/build-verification.json.

Rev15V-Cypher-Houses-Architecture-Update.blend is a compact native library containing changed surface faces and the new window-detail batches only. It is useful for editing these assets and is not the complete master. Never append it as a visible overlay over the old faces: reconstruct V with the commands above instead. The full working master is available locally through delivery/Gullyverse-Rev15V-Weathered-Cypher-Houses.blend; its complete externally recoverable equivalent is the verified base-and-source chain above.

For the isolated runtime review, download the verified architecture GLB to this report's viewer/houses.glb, serve viewer with a local HTTP server and open index.html. The Three.js files/license are included. This is a partial changed-surface material review with neutral diagnostic light; unchanged balconies, Events posters and Team surfaces are intentionally absent from that export. Use the PDF's native full-environment captures to assess those surrounding elements. Runtime integration must replace the original selected surface primitives, not layer this mesh on top of them. Full-world production integration remains pending.

The four-page PDF contains sourced reference images with links, full native neutral inspection views and an Events before/after pair under identical saved night lights. Inspection lights were never saved into the native master. All user-facing visual review remains in the PDF.
