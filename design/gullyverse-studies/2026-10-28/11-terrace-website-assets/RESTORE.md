# Restore Rev08 private terrace/crowd study

Download **all five numbered final ZIP archives** listed in the verified ARCHIVE-INDEX.json. The INTERIM Working-Source-Checkpoint ZIP is not the final package. Keep all older approved backups.

1. Verify each downloaded archive against the SHA-256 in ARCHIVE-INDEX.json before extraction.
2. Extract all five into ONE NEW EMPTY directory, preserving relative paths. Never extract over a website checkout or another candidate. The archives complement one another.
3. Verify every payload against FILE-MANIFEST.json (the manifest does not claim a circular self-hash).
4. Open `source/Gullyverse-Rev08-Terrace-Website-Assets.blend` in Blender 4.3.2 or a compatible later version. Expected SHA-256 `f130611ac54090baf6e25052c222b53a5a243414e1e49686bc1882dc3d6f7f50`, 14,829,066 bytes. All 33 image owners are packed; no external font or live website is required to open/render the model.
5. Open GALLERY.html locally for the full-resolution matched comparisons, historical actual-browser source evidence, source diagnostics, furniture proposal labels and 40-second offline walking inspection.

## Five complementary archives

- `Rev08-01-Source-and-Audit.zip`: final master, new authoring/render/validation scripts, frozen website source excerpts and package lock, authentic crowd/prop GLBs, exact baked-pose data, reports, all technical evidence and file manifest.
- `Rev08-02-Protected-Baseline-Masters.zip`: actual original wider-world Blender master and original corrugated-art master, plus protected website hash inventory. These are real payloads, not Git LFS pointers. They make source comparison and reconstruction independent of the old cloud path.
- `Rev08-03-Architecture-Matched-PNGs.zip`: all BEFORE / architecture-only matched images.
- `Rev08-04-Crowd-and-Source-PNGs.zip`: actual-crowd candidate, exact-source diagnostics and both furniture-proposal PNG sets.
- `Rev08-05-Reviews-and-Walk.zip`: phone/full/source/technical PDFs, 40-second MP4, all 80 final source walk frames and clearly segregated initial unfinished walk diagnostics.

## Scenes and rollback

- `REV08 II / Terrace + Actual Website Crowd` is the default new private candidate. Ambiguous table proposals are excluded.
- `REV08 I / Continuous Rooftop / Old Crowd` isolates architecture.
- `REV08 0 / Before Wider World` is the comparison copy.
- `REV08 III-A/B` are **unselected proposals** using the stored, currently unmounted timber/cloth stall table and an active website-source road case. They are not confirmation of a standalone active steel rack/table.
- `REV08 / Exact Website Source Audit` retains native imported source props.
- Original A, B, C, selected architectural pilot and wider-world scenes remain intact and independently available. Do not overwrite old masters.

## Re-authoring and reproducibility

The frozen `source/BASELINE.json` records the original cloud path as historical evidence. For rebuilding in a different directory, work in a COPY and set its `path` to the extracted `source/baseline/Wider-Realism.blend`. New `geometry_helpers.py` is self-contained. `author_terrace.py` runs against that actual baseline, creates separate scenes and packs the resulting master. It does not modify a website. Do not run it over the delivered final master; use a fresh output directory/version.

The four exact source pose meshes are included as JSON and in the packed master. Recomputing them uses the preserved Crowd.tsx bake function and the repository's exact Three dependency; `bake_website_poses.mjs` reads the frozen source copy. Set GULLYVERSE_SOURCE_REPO to a dependency checkout matching the saved package lock if the original checkout is unavailable. Dependencies are intentionally not included in the checkpoint. No dependency install or website build was performed in this phase.

For independent archive preservation testing, `audit_preservation.py` accepts GULLYVERSE_BASELINE_OVERRIDE pointing to the extracted original baseline master. Other private validators derive their paths from this new directory. The protected-website test applies only where the actual matching website checkout exists; the preserved source snippets are an audit record, not a complete replacement for its separately protected source checkpoint.

`render_terrace.py` records all actual camera metadata. The exterior elevation camera is deliberately staged from the left in the capture script to avoid the tall right neighbor; this capture-only framing does not change source geometry or overwrite any saved master. All before/after elevation pairs use that identical pose.

## Scope / rights / performance

Existing-project crowd meshes were reused on the user's instruction. Their upstream artist/licence was not documented in the checked files; no CC0 or standalone redistribution claim is made. Preserve the provenance report and source GLBs. Existing packed Poly Haven architectural maps retain their prior CC0 provenance. The road-case/table assets have the original project authoring script.

This is a Blender-only art study. Website source, current C9/C8 cave/quarry default, navigation and deployments remain unchanged. No runtime GLB integration, browser FPS, real GPU VRAM, mobile performance or structural/regulatory approval is asserted. Future website work requires separate authorization and actual hardware/runtime verification.

Do not remove old checkpoints or upload credentials/live environment files. Final external verification requires authenticated download-back hashes and a fresh extraction/reopen; see FINAL-DELIVERY-VERIFICATION.json and the accompanying verification sidecar.
