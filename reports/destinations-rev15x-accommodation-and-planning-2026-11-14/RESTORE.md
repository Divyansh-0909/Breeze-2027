# Restore Rev15X

Use Blender 4.3.2. Preserve all existing work and choose new output paths. This is an incremental independently restorable checkpoint backed by the verified complete native T2 base and subsequent source/native chain to W. The small native and GLB files contain the five new Accommodation objects only, not the complete world. Events and Contact files are design proposals/reference snapshots; they are not production integration code.

1. Download the W source checkpoint using source/Base-W-Checkpoint-Index.json: Drive ID `1THXXCvN3T-uaFPHyibd13VhALSTvzEo1`, 5,508,531 bytes, SHA-256 `3010e106d800403fce42933113c5417c6b53176bece90da82943dc7aa7c40e43`. Verify owner/parent, byte hash, ZIP CRCs and every W PAYLOAD-SHA256.json entry. Extract W into a fresh repository directory **before** extracting X, so older documentation cannot replace X current pointers.
2. Reassemble this X checkpoint's parts using source/restore-checkpoint.py and the external Checkpoint-Index.json. It verifies each part, complete ZIP and every PAYLOAD-SHA256.json entry. Extract X into the same fresh root **last**. No dependencies, credentials or live .env values are included.
3. Download the 19 earlier dependency files listed in source/Base-W-Dependency-Manifest.json into W's restore/downloads directory, keeping the listed filenames. Verify the recorded sizes and SHA-256. Follow W RESTORE.md and run W source/restore-base.py to reconstruct the complete V2 master, preserving the original T2 byte hash and checking the incremental source fingerprints. Historical source files extract into W's isolated restore/repo directory, not over X workspace documents.
4. From the extracted repository root, rebuild W and X:

```bash
blender -b --python-exit-code 1 --python reports/streetlights-rev15w-overhead-cables-2026-11-14/source/build.py -- --restore --base reports/streetlights-rev15w-overhead-cables-2026-11-14/restore/masters/V2.blend --output /output/Gullyverse-Rev15W.blend
blender -b --python-exit-code 1 --python reports/destinations-rev15x-accommodation-and-planning-2026-11-14/source/build.py -- --restore --base /output/Gullyverse-Rev15W.blend --output /output/Gullyverse-Rev15X.blend
blender -b --python-exit-code 1 --python reports/destinations-rev15x-accommodation-and-planning-2026-11-14/source/fresh-open.py -- --restored --base /output/Gullyverse-Rev15W.blend
```

W's expected scene fingerprint is `0341ca372167972227e2ae55ebd585b18f52785222afccbca00b4b9f9c4aa913`. X's fingerprint is in evidence/native-scene-fingerprint.json. X refuses to overwrite outputs, checks its source fingerprint and all original objects/materials/scene memberships, packs the new RGBA artwork and checks the reconstructed final scene fingerprint. Fresh-open uses the output path/hash recorded by the restore builder. Whole-file serialization hashes may differ; exact scene-content/preservation fingerprints and packed-resource hashes must match. The full X native retains 60 scenes and 144 packed images. See the native rebuild and separate fresh-open evidence for the tests actually run.

The editable native component can be appended once to the matching W scene for manual edits. The runtime GLB carries only the Accommodation additions; the complete export/baked-light pipeline and production routing remain pending. No component append alone reproduces the historical full world.

Source-main snapshots are read-only reference files and should not be copied into production over current admin/backend code. The PDF labels proposed Events/Contact behavior separately from implemented Accommodation art. Google Doc before/after native responses are audit snapshots, not independent copies of their embedded image bytes; the current native shared Doc and earlier verified native-document backup retain those images. Keep all older verified Drive backups.
