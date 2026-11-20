# Restore Rev15X1

Use Blender 4.3.2 and new output paths. Preserve older backups. The source ZIP includes X1 source, editable native/runtime components, replacement manifest, captures, PDF, fonts/license, report and document audit snapshots. The complete native world is recovered by reusing the verified X dependency chain, then applying the X1 builder. Components alone are not the full world.

1. Use source/Base-X-Checkpoint-Index.json to download all four X source parts by their Drive IDs. Verify each size/hash, reassemble with source/restore-checkpoint.py using that base index, and verify the complete X ZIP hash and all payload hashes. X source is 14,966,883 bytes, SHA-256 `4b43d4ab892f7775b26d73cffc6845c77012b2827198e4a285d44626d50990e8`.
2. Follow X RESTORE.md to obtain W source and its 19 unchanged complete native/source dependencies. Extract W source before X, and X before X1, so the newest documentation is extracted last. Rebuild T2 -> T3 -> U1 -> U2 -> U3 -> V -> V1 -> V2 -> W -> X with the fingerprint guards. X has 60 scenes and 144 packed images; expected X scene fingerprint is `8214924dd55d741cd2b5abd5cd66d2aff92b1a82aac5483c014ff1070477ada1`.
3. Reassemble this X1 checkpoint using its external Checkpoint-Index.json and source/restore-checkpoint.py; verify ZIP CRCs and every PAYLOAD-SHA256.json entry before extracting X1 last at the repository root.
4. Rebuild and reopen the new world:

```bash
blender -b --python-exit-code 1 --python reports/accommodation-rev15x1-clean-wall-2026-11-14/source/build.py -- --restore --base /output/Gullyverse-Rev15X.blend --output /output/Gullyverse-Rev15X1.blend
blender -b --python-exit-code 1 --python reports/accommodation-rev15x1-clean-wall-2026-11-14/source/fresh-open.py -- --restored --base /output/Gullyverse-Rev15X.blend
```

The builder refuses to overwrite, verifies its exact source scene fingerprint, preserves all 60 older scene memberships and all unchanged objects/materials, removes only the house-wall label, and locally restores the left parapet material without touching original mesh data. It verifies the new scene fingerprint in evidence/native-scene-fingerprint.json before saving. The fresh-open check uses the output recorded by the restore builder. The complete native has 61 scenes and 144 packed images. Whole-file Blender serialization hashes may differ; the exact scene fingerprint and preservation/packed-resource checks must match. Actual reconstruction from an independently restored X file and fresh opening passed.

For manual component reuse, read delivery/component-manifest.json first. The component includes the four retained Accommodation objects and cleaned parapet. Replace previous Accommodation bindings/objects and the old parapet host, remove the old house-wall label, and do not append duplicate coplanar geometry. Production integration should use the complete corrected native world and the later M1 export/bake pipeline. Procedural material detail is not a claim of a complete browser visual match.

Contact diagrams are proposals; there is no Contact geometry or live form code to restore from this phase. Native Google Doc before/after responses preserve content/formatting audit data; the original shared Doc and earlier native-document backups preserve embedded image bytes. External checkpoint index and final verification contain new Drive IDs, sizes, hashes, owner/parent and authenticated download-back receipts.
