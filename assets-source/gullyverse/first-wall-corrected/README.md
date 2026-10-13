# Corrected limestone wall — reversible candidate

This is one existing Rock 4 volume and four localized contact faces on Rocks 3/5. It is not an approved replacement for the whole quarry. The original Stage 2B candidate and all its texture files remain intact.

## Editable source and deterministic export

Open `first-wall-corrected.blend` in Blender 4.3.2. `Wall_Master` is the editable closed compound surface; `Wall_LOD0/1/2` are separate visual alternatives. `Wall_Collision` is a hidden compound proxy of the original rock solids. The master and proxy are excluded from normal visual rendering.

From the repository root:

```sh
blender -b --python scripts/blender/author_corrected_wall_section.py
python reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/validate-geometry.py
python reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/validate-exported-topology.py
blender -b --python reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/inspect-master.py
blender -b --python reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/check-scene-seams.py
```

The author imports the locked material from `approved-limestone-material.blend` (packed maps), actual source topology from `host.json` and `joins.json`, and the original anchor from `../first-wall-section/anchor.json`. Geometry helpers are `scripts/blender/corrected_wall_geometry.py` and `corrected_wall_joins.py`; the unchanged deterministic noise helper is `rock_pilot_surface.py`. Export writes only this corrected source/export directory. It does not regenerate limestone textures or stage assets. The material library keeps this source reproducible without copying the previous large geometry master.

Khronos validation also runs with `node reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/validate-glb.mjs`. It uses `gltf-validator` 2.0.0-dev.3.10; set `GLTF_VALIDATOR_MODULE` to that module's absolute path if it is not installed in the author's temporary validation directory. The Python inspection scripts require NumPy/Pillow; Blender includes NumPy for the authoring workflow.

World coordinates are metres. Blender Z-up becomes glTF Y-up; runtime rotation/translation comes from `manifest.json`. No object scale compensation is required. Runtime files are under `public/models/gullyverse/first-wall-corrected/`. Only the combined GLB is loaded by the preview, sharing its three embedded maps across all LODs; standalone LOD exports are review assets.

## Browser preview

```text
/?diagnostics&wallPreview=limestone
/?diagnostics&wallPreview=limestone&wallCandidate=previous
```

The first selects this correction; the second selects the preserved prior candidate. Without `wallPreview`, the public/default quarry stays unchanged. The preview's **Original quarry** button restores the original mesh immediately. Its session owns the optional cache; scene clones borrow geometry/materials and do not dispose shared resources. Collision proxies are raycast-verifiable but do not replace current walking polygons.

## Limits

The master is closed and all visual LODs stay inside the original solids. Protected host corners and outer skyline edges are retained; decimated contact perimeters have measured millimetre/centimetre deviation, documented in the report. Neighbor blockout coloration and silhouettes remain visible. Review the actual browser gallery before accepting the integration; technical validation does not establish visual approval or physical-GPU performance.

See `docs/gullyverse-stage-2b-wall-geometry-correction.md` and `reports/stage-2b-wall-geometry-correction-2026-10-12/gallery.html`.
