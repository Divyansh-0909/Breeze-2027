# Gullyverse lane → rooftop concept / restoration

Handoff: WORLD-LANE-ROOFTOP-ABC-20261023-01.
This is an authorized PRIVATE BLENDER CONCEPT STUDY. No website files, production defaults or deployments were changed. Do not install it over the website or infer approval of a runtime implementation.

## Quick review

- Open review/Gullyverse-Lane-Rooftop-ABC-Review.pdf (19 long portrait pages).
- Open review/index.html locally for full-resolution A/B/C views and direct side-by-side strips.
- Watch review/Crowd-Reveal-20s-Animatic.mp4. It is a 20-second rendered-keyframe animatic, not a browser walkthrough or continuous real-time animation.
- Read GULLYVERSE-LANE-ROOFTOP-CONCEPT-REPORT.md or the technical PDF.

## Restore this concept independently

1. Download every required file in checkpoint-index.json. Verify the listed SHA-256 for each binary part and complete ZIP. Do not mix archive families or versions.
2. If an archive is split, concatenate .part001, .part002, etc. in numeric order into its exact .zip name before extraction. Example:

    from pathlib import Path
    import hashlib
    family = 'Gullyverse-Concept-Review-and-Evidence.zip'
    with open(family, 'wb') as output:
        for part in sorted(Path('.').glob(family+'.part[0-9][0-9][0-9]')):
            with part.open('rb') as source:
                while block := source.read(1024*1024):
                    output.write(block)
    with open(family,'rb') as source:
        print(hashlib.file_digest(source,'sha256').hexdigest())

3. Extract Source-and-Assets, then Review-and-Evidence, then Final-Metadata-Overlay into a NEW folder. All share the root Gullyverse-Lane-Rooftop-Concept/. No archive needs to overwrite the website. Existing images in the Blender master are packed; the authoring scene has no linked external .blend library.
4. Compare every restored file with FILE-SHA256SUMS.txt / files-manifest.json. restore-verification.json records the independently extracted archive-member checks performed before delivery.
5. Open source/Gullyverse-Lane-Rooftop-ABC.blend in Blender 4.3.2 or a compatible newer version. Select scene A / Grounded, B / Festival Heavy, or C / Balanced. Each links the same site and camera rig. Named cameras 01–12 match the review images; camera 13 has the editable 1–480 / 24fps crowd move. The file opens on C for inspection; this is not a final user selection.

The direct .blend download is an additional convenience copy, not the complete source/evidence checkpoint. Use the ZIPs to recover editable artwork, scripts, original portraits, manifests and reviews. A .blend1 is a retained internal authoring draft; use .blend for the final scene. Diagnostics/pre-final images are deliberately separated from renders/A, B and C.

## Re-rendering and source editing

All final used images are packed in the master and supplied under assets/. Only Blender is required to open/edit/render it. Portrait and existing film/navigation artwork retain existing project rights; only the selected Poly Haven sources are CC0. No project font binary is shipped.

The optional authoring scripts reproduce the new site. Run them in a NEW COPY of source + assets with fresh renders/evidence output directories. build_scene.py creates the base; calibrate_scene.py applies the documented surface-facing, screen-UV, camera, crowd-spacing and parapet corrections. Then validate_concept.py / audit_scene.py / render_study.py produce the evidence. The helper render_all.sh documents this order. Resuming render_study.py keeps existing PNGs; move old renders into a separately labelled version directory before changing the model/camera, rather than silently mixing poses.

Python authoring/review helpers use Pillow 12.3, NumPy, Matplotlib 3.10 and ReportLab 4.4.9. The optional technical PDF helper uses Node/Playwright and Chromium. Set GULLYVERSE_TOOL_PACKAGE_JSON to an existing tool environment's package.json if the original /workspace/Breeze-2027-wip-push dependency path is unavailable. No dependency/cache folder is shipped.

prepare_assets.py / extract-navigation.mjs document first-time derivation from the protected existing website. They are NOT required to open the delivered master; generated rasters, selected maps and original team portraits are included. The navigation helper originally used current worldPaint.ts and the inherited font to produce the included exact board raster. The extracted Aftermovie still is included; the full unchanged movie remains in the protected website checkpoint.

Final renders use EEVEE Next / 16 samples. Earlier Cycles/OIDN/software-driver probes are diagnostics only. No separate downloaded denoiser binary is required or shipped. The animatic uses 12 EEVEE poses and a labelled 24fps video container; it does not claim to contain 480 independently rendered frames. Sound cues are only a storyboard proposal.

## Website preservation and dependencies

This concept master is SELF-CONTAINED and does not require the quarry assets to open. The WEBSITE itself remains at work-in-progress-2027 / e638140b37045a805b23b4d406d387a8870f8486 with its pre-existing dirty state. A 1,213-file preservation check and an additional 311-file prior canal-checkpoint comparison pass.

To restore the old running website separately, use its already verified WIP and canal checkpoints, not this concept archive:

- WIP parent: https://drive.google.com/drive/folders/1G-LsAHgaKyRZb7mgn8nG0atL2rNrxXR3
- Canal material study: https://drive.google.com/drive/folders/1iD2YTzDHLORsF_X-mS-fA3f6xcEJE9Jy

Follow their own explicit earlier recovery chains and real LFS payload instructions. They were not overwritten or deleted.

## Verification and limits

DRIVE-BACKUP-RECEIPT.json identifies remote parent/name/bytes and full authenticated download-back SHA-256 verification. A folder URL alone does not certify a backup. Per-file/source/archive checks and the independent restore proof accompany it. No credentials, private .env, dependencies, build caches or diagnostic-tool binaries are included.

This is a concept feasibility gate. All sampled visitor capsules/floors and the proposed camera move pass the reported checks, but minimum side-route clearances are below a uniform 3m corridor in places. Proxy crowds, production mounting, final UV/bakes, atlas/instancing, runtime navigation/media/history/context recovery and physical-device performance remain unimplemented/unverified for this new world. Do not claim the existing runtime can simply load this Blender file unchanged.

Stop for user approval of the environment concept. No automatic website replacement, final A/B/C selection, commit, push, merge, deployment or next phase.

## Required final metadata overlay

Gullyverse-Concept-Final-Metadata-Overlay.zip is applied AFTER the first two archives. It replaces exactly source/audit_scene.py, evidence/scene-budget-final.json and this README, and adds evidence/font-validation-correction.json. The original archive metadata tested the built-in font by display name Bfont; Blender 4.3.2 actually names it Bfont Regular with filepath <builtin>. The final check uses the built-in filepath or an actual packed payload. This corrects the check and metadata only: the .blend, cameras, geometry, packed images and every final render are unchanged. Original archive-member hashes remain valid; final per-file hashes account for these documented overrides.
