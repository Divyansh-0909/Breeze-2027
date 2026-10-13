# Full quarry limestone rollout

Approved source: the corrected Stage 2B pilot, approved by the user on 2026-10-12. Its original source/exports and all limestone maps remain unchanged. This directory contains the new full-perimeter candidate, not replacements for the stage or entrance assets.

## Source and reproduction

Open `quarry-limestone.blend` in Blender **4.3.2**. `EDITABLE_QUARRY_GEOLOGY` contains 25 closed quarry volumes and the two quarry-facing transition masters. `APPROVED_PILOT_REFERENCE` retains the prior pilot as a hidden reference. `RUNTIME_LOD0/1/2` are alternatives; the website selects one per part. `ORIGINAL_COLLISION_REFERENCE` is hidden and does not replace the existing player collision registry.

From the project root:

```sh
npx tsx reports/stage-2c-quarry-rollout-2026-10-12/scripts/extract-perimeter.mjs
blender -b --python-exit-code 1 --python scripts/blender/author_quarry_rollout.py
python scripts/blender/quantize_quarry_attributes.py
node reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-glb.mjs
python reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-exported-topology.py
python reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-shape.py
```

The glTF validator script uses Khronos `gltf-validator` **2.0.0-dev.3.10**; set `GLTF_VALIDATOR_MODULE` to its installed module path if necessary. Python validators require NumPy. Authoring imports the existing packed limestone material; it never generates or repaints textures. Do not run the unrelated stage-asset generation script.

All units are metres. Blender Z-up exports to glTF Y-up. Mesh positions are in the current world coordinates with identity runtime transforms. World/route/camera coordinates and lights are not regenerated. `source-topology.json` is extracted from the actual current TypeScript geometry before authoring. The accepted pilot body and its fitted neighboring contact surfaces are retained; remaining rock morphology is seeded per actual rock envelope. Large fractures cover each envelope's full dimensions. Small crest chips remain within the old solid and retain its extreme corner anchors.

The collar's front opening matches the original tunnel end. Its closed rear follows the existing bent passage and expands into the old wall mass, preserving the walking corridor. The rear exterior shell is stitched at its old section-local noise gaps; the entrance-facing shell, artist paint and enclosed passage remain in their original rendering system.

Fracture depth scales with each original envelope's area (approximately 1.58–2.11× the pilot-sized field), bounded to 32% of the radial distance. Uneven shallow scars add local chips. An irregular terrain-contact band preserves the original foot; only its crease samples are pinned for LODs, so planar contact surfaces can simplify. A BVH survey checks previously blocked horizontal sightlines from three visitor-height origins at every LOD. Upward skyline changes and LOD contour differences are published separately for visual review; macro corners and hull bounds remain independently locked.

## Runtime and reversal

Runtime exports: `public/models/gullyverse/quarry-rollout/`. The website loads the combined `quarry-limestone.glb`; standalone LOD files are validation/review exports, not additional downloads. A single approved material and three embedded maps are shared by all visible parts. All three detail levels are CPU-resident and warmed under cover; only one LOD per part is drawn, with screen-space thresholds, quality-tier scaling, hysteresis and frustum culling. Bounded cache ownership stays with the immersive shell.

Normal/tangent/UV0 attributes on new parts use native **KHR_mesh_quantization**, supported by the current Three.js GLTFLoader. Positions, accepted pilot attributes and image bytes remain unchanged. No Draco, Meshopt or KTX2 dependency is added. `uncompressed/` retains the original generated runtime files for comparison. A degenerate exporter tangent, when present, is derived from the fine-normal UV basis by the postprocessor.

The local branch uses the rollout by default. Restore the original placeholder world with `?quarry=original`, or build with `NEXT_PUBLIC_GULLYVERSE_QUARRY_ROLLOUT=0`. With the existing preview build flag enabled, `?wallPreview=limestone` restores the approved single-pilot comparison. These preserve the original code/assets. No deployment or commit is part of this task.

Physical GPU/mobile acceptance and further transfer-size/streaming refinements remain pending. The current combined asset retains all three LODs; its measured memory and loading costs must be included in device acceptance. Review `docs/gullyverse-stage-2c-full-quarry-rollout.md` and the matched browser gallery before approving this rollout.
