# One fitted cool-grey limestone wall section

Original source geometry/maps; quarry photographs are morphology references, not texture pixels. Private opt-in integration only. No new stage/crowd assets.

Editable master: `first-wall-section.blend` (Blender 4.3.2, metres). Collections `EDITABLE_GEOLOGY_MASTER`, `WALL_RUNTIME_LODS`, `COLLISION_REFERENCE`. Runtime materials/maps are packed; 2048 author maps are also supplied separately in `textures/`. Named master and three LODs remain editable. Open hidden collections/objects to inspect them. Default source presentation shows LOD0, not overlapping visible levels.

From repository root with Python NumPy/Pillow and Blender 4.3.2:

```sh
python scripts/blender/wall_section_materials.py
blender -b --python scripts/blender/author_first_wall_section.py
python reports/stage-2b-first-wall-2026-10-12/scripts/check-asset-fit.py
python reports/stage-2b-first-wall-2026-10-12/scripts/inventory-assets.py
node reports/stage-2b-first-wall-2026-10-12/scripts/validate-glb.mjs
blender -b --python reports/stage-2b-first-wall-2026-10-12/scripts/inspect-master.py
```

The validator script uses the locally installed Khronos `gltf-validator`; set its module path to your installed copy if the cloud temporary path is unavailable. Runtime loading does not require this validator. Do not run whole-site or stage generation scripts.

Only dedicated `first-wall-section` paths are generated. Scripts depend on unchanged `rock_pilot_surface.value_noise`; seed 2401012 for cavities and explicit unequal fracture/bedding/plane definitions. Anchor is the existing rock4/face3 pentagon, not a free-standing boulder. Author front -Y/Z-up -> glTF front +Z/Y-up. Rigid metric runtime basis/pivot is recorded in `anchor.json` and `manifest.json`.

Near LOD: feature-weighted quadric collapse of 243,110-triangle closed source to 21,500. Mid 5,290 and far 1,720 triangles sample the same geological surface at lower density with identical original corners. Collision prism: 16 triangles, a conservative proxy inside the old rock; it is not installed into current walking polygons. All source meshes closed and positive-volume. Back/caps are intentionally simple and remain embedded in the original solid.

Two UV channels: unique complete-face albedo/roughness/AO; metre-based fine mineral normal tile on UV1 (12x10m, no additional texture download). Single material, single sided, metallic0, normal scale0.58, roughness0.82..0.99. Cool-grey body184/188/193 source palette; narrow0.62m perimeter only blends toward actual untouched neighbor colors. This is compatible re-authored mapping, not byte-identical reuse of the old pilot maps. No texture reference photographs, no global lighting change.

Combined GLB embeds one shared1024 JPEG base/1024 PNG normal/512 PNG ORM set across all three LOD nodes. Load the combined file once; filter nodes and select one visible LOD. Separate GLBs are alternatives and each embeds maps: don't load all of them together. No Draco/Meshopt/KTX2 dependency is introduced.

Production default stays procedural. Dev mode or a local production build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` accepts `/?arrival=hub&wallPreview=limestone&diagnostics`. Remove query/reload to return to default. No preview is enabled or deployed automatically. See the Stage2B report for shader preparation, cache retirement and real-device tests pending.
