# Two-section limestone continuity proof — Stage 2C.1

Scope: original quarry anchors **22 and 23** only. Stage 2C defaults, source masters, maps and all world/collision/camera configuration remain intact. This is a candidate for human review, not approval of the rest of the quarry.

Open `refined-limestone-pair.blend` in **Blender 4.3.2**. Metric units, one metre, Blender Z-up; glTF export converts to Y-up. Identity world anchors; mesh positions align to the current registry. The shared surface combines the two regions as one watertight volume. Separate editable region masters remain in `EDITABLE_CONTINUOUS_LIMESTONE`; the joined editable master and `REFINED_LOD0/1/2` demonstrate the seam-free result. Only one runtime LOD is rendered; internal duplicate closing faces are removed. Existing player collision/proxies remain authoritative and unchanged.

## Reproduce against the preserved current repository

```sh
python scripts/blender/prepare_refined_pair.py
blender -b --python-exit-code 1 --python scripts/blender/author_refined_quarry_pair.py
python scripts/blender/pack_refined_quarry.py
node reports/stage-2c1-geological-refinement-2026-10-13/scripts/validate-glb.mjs
python reports/stage-2c1-geological-refinement-2026-10-13/scripts/validate-exported-topology.py
blender -b --python-exit-code 1 --python reports/stage-2c1-geological-refinement-2026-10-13/scripts/validate-refined-shape.py
blender -b --python-exit-code 1 --python reports/stage-2c1-geological-refinement-2026-10-13/scripts/validate-coverage.py
```

Offline preparation uses Python NumPy/SciPy; authoring uses Blender's bundled NumPy/bmesh. It reads the existing Stage 2C source topology and packed material as dependencies. The review ZIP supplies the topology and preserved baseline GLB; if the large original Stage 2C Blender master is absent, authoring reads the exact same packed family from the supplied refined master. It never runs the stage-asset generator. No stage or original quarry file is overwritten. `prepared/` contains reproducible numerical meshes; `with-approved-material/` retains original Blender exports. `uncompressed-geometry/` retains pre-quantization geometry exports. Final exports are in `public/models/gullyverse/quarry-refinement/`.

A shared broad excavation curve replaces independent pointed envelopes ABOVE the exact terrain contact band. The broad unequal crest, finite bedding/joint paths, sparse chips, and metric UVs span both source regions. UV0 stays within the approved painted island rather than sampling its olive atlas padding; its UV derivative/physical grain scale stays unchanged. UV1 preserves 12×10 metre fine-normal scale. Texture bytes and material values are never repainted or adjusted. End/bottom closures are triangulated in their actual physical outline; collinear boundary samples are retained. LODs use common boundary sampling, reduced interior density and one coordinated selection across the welded volume.

## Review and ownership

Build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` and visit `/?arrival=hub&quarryReview=geology`. Development builds also permit this query. The opt-in review panel can switch between Stage 2C and the refined pair. Ordinary navigation has no review controls or new asset request. All normal routes still display Stage 2C by default; `?quarry=original` remains available as the older reversal.

The geometry-only GLB contains no images. `RefinedQuarrySession` borrows the exact live Stage 2C limestone material, normal map, ORM and base colour. The refinement cache owns its three geometries; it does not own the borrowed maps/material. Retirement requires covered restoration to Stage 2C; owner teardown disposes only owned geometry before the base owner retires its own cache. Standalone LODs are review exports, not additional runtime downloads.

Native `KHR_mesh_quantization` matches the existing validated loader. No Draco, Meshopt or KTX2 loader/dependency is added. No physical-GPU or full-perimeter performance certification follows from this proof. See the linked refinement report before expanding it.
