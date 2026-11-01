# Restore revision 04

1. Verify both archives against CHECKPOINT-INDEX.json and the verified Drive receipt.
2. Extract Gullyverse-Straight-Walk-Source-Review.zip into a fresh folder. It contains the complete editable master, source, reports, gallery, MP4 and full-resolution stills.
3. Extract Gullyverse-Walk-Original-Rendered-Frames.zip into the same folder to restore all 120 original motion PNGs under walk-frames/C.
4. Verify FILE-SHA256SUMS.txt. Open source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend in Blender 4.3.2 or compatible Blender. Three scenes and 24 referenced images are packed; no website or external Blend library is required.
5. The default action is 13-CONTINUOUS-STRAIGHT-WALK, frames 1-960 at 24fps. It walks at X=0 and eye height 1.72m. No separate reveal action exists in this candidate. Other named cameras provide inspection views.
6. Open review/index.html or the review PDF. Straight-Connection-Walk-20s.mp4 is an actual 6fps/384x240 excerpt, not a runtime performance benchmark.

Render stills: blender -b source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend -t 2 --python source/render_study.py -- stills
Render motion: use -- walk. The renderer skips existing PNGs; use a fresh output copy to repeat captures.

To replay authoring against the previous master, download the byte-identical revision-03 master (SHA-256 8d3d143a629f62aa49b70125c659090643a3046e17bff1e32910514b503943f8), open it and run source/author_straight_walk.py. It accepts the loaded original master from any local location. Compare/survey scripts retain historical paths for recorded verification; opening or rendering the supplied new master does not depend on them.
Previous master: https://drive.google.com/file/d/17H4m2kcRNoOjHy8t-P7ms2v7MEydH0uQ/view

No credentials, live .env contents, node_modules, build output or Git repository are included. This is an independently restorable Blender concept, not a replacement for protected website checkpoints or permission to deploy.
