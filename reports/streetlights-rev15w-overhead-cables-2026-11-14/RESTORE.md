# Restore Rev15W

Use Blender 4.3.2 and Python 3. Verify the checkpoint SHA-256, ZIP CRCs and every entry in PAYLOAD-SHA256.json before extracting at a fresh repository root. Preserve existing work. The new native component, GLB, manifest, controller, local viewer/vendor licenses, source, reference photos, PDF, documentation and evidence are included. The complete world is recovered from the unchanged verified native/source chain below.

1. Read source/restore-manifest.json. Download each file through authenticated Google Drive using its raw ID. Verify owner losersamurai09@gmail.com, parent (where recorded), exact byte size and SHA-256. Save files under this phase's restore/downloads directory using the manifest filenames. There are 13 T2 full-master parts, two V source ZIP parts, V1 and V2 source ZIPs, and T3/U1 native deltas. All were actually downloaded and verified in this phase. V's source ZIP includes the verified U3 source ZIP and earlier restoration code/indexes. No user credentials are included.
2. Run from the extracted repository root:

```bash
python reports/streetlights-rev15w-overhead-cables-2026-11-14/source/restore-base.py
```

This verifies all inputs, reconstructs/extracts the source ZIPs under this phase's isolated restore/repo directory, reassembles the exact complete T2 native master, and rebuilds T2 -> T3 -> U1 -> U2 -> U3 -> V -> V1 -> V2 under restore/masters. Every builder verifies its expected active-scene fingerprint. Native intermediates are recovery caches. The helper does not extract historical documents over current workspace files.

3. Build the final edited master; choose a new output filename:

```bash
blender -b --python-exit-code 1 --python reports/streetlights-rev15w-overhead-cables-2026-11-14/source/build.py -- --restore --base reports/streetlights-rev15w-overhead-cables-2026-11-14/restore/masters/V2.blend --output /output/Gullyverse-Rev15W.blend
blender -b --python-exit-code 1 --python reports/streetlights-rev15w-overhead-cables-2026-11-14/source/fresh-open.py -- --restored --base reports/streetlights-rev15w-overhead-cables-2026-11-14/restore/masters/V2.blend
```

The W builder refuses to overwrite outputs, validates V2 fingerprint 1b882cca849915c98c7df36fec1f38365b9166c325d541ee8fbaaaec749b4629, preserves original objects/58 historical scene memberships and reproduces W fingerprint 0341ca372167972227e2ae55ebd585b18f52785222afccbca00b4b9f9c4aa913. It writes the restored output path/hash to evidence/restore-check.json, which the separate fresh-open check uses. The native has 59 scenes and 143 packed images. Re-serialization can change the complete .blend byte hash; the content fingerprints, packed-image and object checks must match. An actual W rebuild and fresh opening passed in this phase.

The small delivery/Rev15W-Gully-Streetlights-and-Cables.blend contains only the new editable collection and six native animated lights, not the whole world. It can be appended once to the matching V2 scene for manual edits; source reconstruction is the tested recovery method. Keep all earlier backups.

To review the isolated runtime component, serve viewer over local HTTP. The ZIP includes actual copies of streetlights.glb, streetlights.json, the controller and Three.js/license. Run node source/browser-review.cjs from this phase if Playwright is installed at the documented repository path. The viewer's floor and illumination are diagnostic and absent from the native master. The PDF uses actual native night lighting. Full-world website integration remains pending.

The snapshot files under document-snapshots preserve before/after native Google Docs responses for audit and content recovery; embedded image IDs reference the preserved native shared document and its earlier independently verified native-document backup. They are not a credentials backup. Checkpoint-Index.json and upload verification receipts provide final Drive IDs, sizes and download-back hashes for this phase.
