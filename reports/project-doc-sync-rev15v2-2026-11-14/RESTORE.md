# Restore the project-document checkpoint

This phase updates documentation only. The current shared document is https://docs.google.com/document/d/1mUE4J2QCNMHk0ryoiSSOADbkjdwi3FN5IG5GZhoIBTU. The versioned phase is https://drive.google.com/drive/folders/1i_2DX0hvwc9e0YlqFUaeklKL3uGsrAbF.

Download every ordered checkpoint ZIP part and Checkpoint-Index.json. Run source/restore-checkpoint.py with the download folder, a new output ZIP filename and --index pointing at that index. It verifies each part's size/SHA-256, the complete ZIP, ZIP CRCs and every payload hash. Extract into a new empty directory. Source paths are relative to the repository root. Do not apply the fixed-index edit requests to an already updated or concurrently changed document.

Complete native BEFORE snapshot: https://docs.google.com/document/d/1reWAp_TODdHg4UjscE5FKIBf8RBuhJlanE2NEPaXvkk/edit?usp=drivesdk
Complete native final AFTER snapshot: https://docs.google.com/document/d/1Jd_2in3Gop4yyXFkErWkjsdH8Xv0raFYHsgXOWcriyU/edit?usp=drivesdk

For an editable native restoration, copy the appropriate verified native snapshot with Google Drive's native copy action into a new recovery folder, then read back its body, styles and image count. Preserve the live document and original snapshots. These native copies retain all five embedded images and their editable native layout. The JSON records and full PDF exports supply an independent content/structure and offline-readable record; rebuilding a Doc from PDF alone would lose native editing structure.

The archive includes snapshots/before-document.json (read from the verified BEFORE native copy after a runtime restart), snapshots/final-after-document.json (final live readback), full before/final PDF exports, the exact initially guarded requests, the two scoped layout repairs and complete readback evidence. The BEFORE native copy had been verified byte-for-byte in native body/style structure against the live original before editing. The final native copy likewise matches the final live body/structure/styles/image count, with destination parent/owner verification recorded.

NativeDoc indexes are UTF-16 units. compose-edit.js and planned-edit.json describe the original scoped update; layout-repair.json records the final filename/directory line-wrap adjustment. Replaying edits is optional and must start from the matching BEFORE state with a fresh requiredRevisionId. The tested and simplest restoration is a new native copy of the preserved complete document.

This archive is not a full 3D world backup. Current V2 art/native/runtime dependencies remain in their separately verified phase indexes and the source links in CONSOLIDATED-HANDOFF.md. The environment restart cleared temporary local 3D caches; recover the master through that existing chain before any further world editing. Website/walkable integration remains pending.
