# Wider sponsor-logo gaps / Rev15L1

The sponsor LED now leaves three times as much nominal space between logos: 72 cells instead of 24. All 62 source marks retain their artwork, fitted dimensions and scroll speed. The strip is 10,676 by 64 cells; one period lasts 355.87 seconds at 30 cells per second. Board geometry and mural art are unchanged.

Open `delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend` for the current packed full environment. The active scene is Rev15L1 and all 42 scene slots remain. The previous Rev15L master is preserved. `source/apply-spacing.py` updates only the active LED texture, period denominator, scroll driver and timeline. The same original branch assets supply the wider strip. Source hashes, logo sizes and raster extents match the base. Minor antialiasing differences from re-rendering are recorded in `evidence/spacing.json`.

The private browser preview uses the same strip and period as Blender. Its board GLB is reused unchanged from Rev15L. See the native screenshots, MP4 and PDF in this report. Schedule remains a proposal; no website route is added.

The checkpoint contains the complete packed edited master, runtime preview, source for this revision, visual evidence and repository pointers. Unchanged logo originals and the original authoring pipeline are reused from the complete verified Rev15L checkpoint, specified in `evidence/base-reference.json`. They are needed only to re-run authoring from the original base. The current master and preview are self-contained.

Drive subphase: https://drive.google.com/drive/folders/1OoIQZBvgqRoodjDC296R5BGxpkoJqkAH

Checkpoint: https://drive.google.com/drive/folders/1ej5qL-HyyI5xvVUGnqrAufGwCs1pWqbQ

The user requested increased spacing; this threefold gap is presented for visual review. No commit, push or deployment is included.
