# Restore the private Rev11 study

Download every required complementary ZIP in `FINAL-REVIEW-AND-RESTORE-INDEX.md`, verify its SHA-256, and extract all into one NEW empty folder. Do not concatenate the ZIPs or overwrite an existing project. This restores a private Blender study, not a website deployment.

Open `source/Gullyverse-Rev11-Connected-Neighborhood.blend` in Blender 4.3.2 or compatible. Its SHA-256 is `b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd` (20,471,503 bytes). All 15 historical scenes remain, plus REV11 (+7%) and H00/H06/H09 crowd controls: 19 scenes total. All 33 original image owners are packed. No external website or photo backplate is needed to open it.

Authentic inputs: `inputs/Rev10-original.blend` and `source/prior-pilot/baseline/Rev05C-Approved-Corrugated-Art.blend`. Original reference photos/credits are under `references/` and `baseline/source/REFERENCE-PROVENANCE.json`. R2/R4 remain private references with unverified public redistribution rights. No photo pixels were used as scene textures.

Run `python source/run_checks.py` to invoke the Blender checks. Dependencies for model validation are Blender's bundled NumPy/mathutils. Pillow/ReportLab and FFmpeg are needed only to rebuild reviews/video. `source/author_connected.py` reproduces the derivative from the authentic Rev10 input; run it only in a NEW extracted working copy, because it writes the candidate output filename. Preserve the sealed original and old checkpoints.

The original `measure_floor.py` is retained as a diagnostic: exact unchanged-population occupancy fails after authorized height changes. The current `measure_floor_attribution.py` keeps the same 0.35m rays, proves zero new architecture obstructions with unchanged-height H00, and explicitly attributes 29 changed sampled centers at +7% to taller people. Protected-route clearance passes 960 frames / 18 applicable scenes, with 0.35m capsule and 0.002m floor thresholds unchanged. This is not a claim that all grid occupancy is identical.

Open `GALLERY.html` locally for full-resolution images, PDFs and the actual offline walking clip. The 40-second clip uses 80 Blender samples played at 2fps, encoded with repeated frames at 24fps; it is not interactive/device FPS. Matched stills are 1280×720 or 576×1024 at pixel ratio 1 / 16 EEVEE samples. Original A/B control PNGs are byte-exact prior evidence; Rev11 transient images were recaptured after the environment restart from the same sealed model. No claim of byte-identical restoration of lost temporary Rev11 renders is made.

Scale-ruler, hidden-media and floor-patina diagnostics are temporary process-only variants. They are not saved into the master and must not be adopted silently. The selected floor, screen, lights/world/exposure remain original; five optional supports remain 0W. Steel table/rack identity remains unresolved.

`FILE-MANIFEST.json` covers restored payload hashes; final index/receipt/handoff are external sidecars to avoid circular hashes. Independent restoration uses only actual authenticated Drive-downloaded ZIPs, opens the master and verifies its packed resources and source signatures. Keep the verified Drive checkpoint and a local downloaded copy outside Codex.

The website remains unchanged at WIP HEAD `e638140b37045a805b23b4d406d387a8870f8486`, with existing dirty/untracked state preserved. No website integration, build, server, commit, push, merge or deployment is authorized. Stop for user visual approval; neither A/B nor this hybrid is selected as final.
