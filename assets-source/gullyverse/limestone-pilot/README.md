# Original limestone rock pilot variant

Separate from the original approved rock pilot. Production website, stage, navigation, dimensions, camera and lighting are untouched. This is a limestone appearance/weathering variant, not a permanent environment replacement.

Blender4.3.2 master `quarry-limestone-pilot.blend`; metre units, Blender Z-up/front -Y to glTF Y-up/front +Z, bottom-centre pivot. Retains the first pilot's stratified macro form and adds 34 shallow dissolution pockets/interrupted solution channels. Original pale calcite/mineral maps, not reference-photo textures. Unique UV atlas; source2048/runtime1024. sRGB JPEG base colour; linear PNG tangent +Y normal, AO/roughness/metallic export packing. Metallic0, matte roughness0.82–0.99, normal strength0.58. Three explicit visual LODs and a conservative collision hull. No Draco/Meshopt/KTX2 assumptions.

From repository/package root:

```sh
python3 scripts/blender/limestone_pilot_materials.py
blender --background --python scripts/blender/author_limestone_pilot.py
blender --background --python scripts/blender/inspect_limestone_pilot.py
```

Python needs numpy/Pillow; Blender4.3.2 includes its own numpy. `limestone_pilot_surface.py` reuses the unchanged `rock_pilot_surface.py` morphological field; both source files are provided. Scripts only write dedicated limestone output paths.

Combined `quarry-limestone-pilot.glb` contains all LOD nodes and proxy. glTF does not encode visibility. Select exactly one `Rock_LOD0/1/2` and hide `Rock_Collision`, as the bundled preview does. Separate LOD GLBs are provided; loading all separate files duplicates texture cache entries. No automatic LOD distance policy or production collider integration is included.

After extracting the review ZIP, run `python reports/limestone-rock-pilot-2026-10-12/preview/serve-preview.py`, then open http://127.0.0.1:3002. Existing Hub lighting/exposure and fixed comparison cameras; Original pilot / Limestone pilot controls allow direct comparison. Original GLB is included for this isolated comparison only. Physical laptop/mobile GPU measurements remain unverified.
