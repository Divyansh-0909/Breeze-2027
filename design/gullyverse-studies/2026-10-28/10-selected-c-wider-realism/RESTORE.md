# Wider C+A private Blender checkpoint

This restores the private artwork, not the website. Original A/B/C and approved pilot scenes remain intact. Do not promote, export into the app or alter the crowd/counters without separate approval.

Download all SEVEN complementary FINAL archives listed in ARCHIVE-INDEX.json. Compare byte counts and SHA-256, then extract them into the SAME NEW EMPTY directory. Never extract over an application repository or older checkpoint.

Verify FILE-SHA256SUMS.txt. Open source/Gullyverse-Selected-C-Wider-Realism.blend with Blender 4.3.2 or compatible later version. Choose SELECTED C+A / Wider Neighborhood Realism. There are five scenes: original A, B, C, approved pilot and new world. Keep five optional support lights at 0 W. All 33 image resources are packed. No live website dependency is needed.

World master SHA-256: 28020ff0d0a499571e615a28fc003ea9411692af4595da5a3b2764ffe0608225
Approved input SHA-256: 3ba2b0056a9cd12bc0fefaa9a503df0fe12539467d46a01c7fd0a91fa2124202

Crowd-and-Counter-Proposals-Only.blend is a SEPARATE proposal file, seven isolated scenes. No replacement has been applied to the world. Its neutral display-ground patch belongs only to isolated counter studies.

Open GALLERY.html after extracting ALL archives. PDFs, MP4, 44 full-resolution scene PNGs, 11 proposal PNGs and all 120 original walk frames are included. The walk is 40 seconds at 3 fps from original source frames 1-960, not interactive browser FPS.

## Reproduce in a separate working COPY

Run Blender with source/APPROVED-PILOT.blend and source/author_world.py. Then run source/repair_solidify_uv.py and source/finish_geometry.py against the resulting world master. These preserve exact evaluated floor geometry while correcting UVs and triangulating new fitting caps. Rerun run_validation.py, measure_visibility.py and validate_sightlines.py. No tolerance change is permitted.

Render matched before/after with render_world.py -- before / after. Run render_walk.py for source frames, then finalize_reviews.py. Run author_options.py against APPROVED-PILOT.blend and finish_option_ground.py against its separate output for proposal studies. Run validate_options.py on that proposal file.

Python review tooling requires Pillow, ReportLab and PyMuPDF; video tooling requires ffmpeg/ffprobe. No website dependencies or credentials are included or needed to open the delivered packed masters.

The source/prior-pilot directory includes the earlier source materials, artwork/provenance, authoring scripts and original corrugated-art master. Its duplicate prior pilot .blend is omitted because source/APPROVED-PILOT.blend is the identical original payload. Earlier independently verified full pilot checkpoint remains unchanged in Drive.

## Archive roles

1. Source-and-Tests: all new scripts, exact approved input, new world/proposal masters, technical evidence/report, restoration and per-file hashes.
2. Shared-Authoring-Inputs: prior editable corrugated master, raw/prepared art/material inputs and provenance.
3. Before-PNGs: 22 exact approved pilot views.
4. After-PNGs: 22 candidate views.
5. Proposal-PNGs-Final: 11 final proposal views.
6. Review-and-Gallery: review PDFs, technical PDF, walking clip and HTML gallery.
7. Original-Walk-Frames: all 120 genuine source frames.

Earlier Working-v1 and Validated-Source-v2 ZIPs are interim safety snapshots, not substitutes for the final seven archives. The earlier Proposal-PNGs ZIP predates neutral display-ground refinement; use Proposal-PNGs-Final for the final review. Earlier immutable backups are retained.

Final download-back receipts, independent fresh restore/reopen proof and shared Doc handoff are sidecars. They are not circularly included in their own precomputed archive hashes. A verified Drive backup does not assert that the user downloaded it to personal storage.
