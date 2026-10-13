# Grey limestone revision

Requested by user: make the limestone more grey. Separate from the pale limestone so the previous version remains recoverable. Production environment, stage, lighting and navigation are unchanged.

Reproduce from repository/package root:

```sh
python3 scripts/blender/grey_limestone_pilot_materials.py
blender --background --python scripts/blender/author_grey_limestone_pilot.py
```

Ordinary Python needs numpy/Pillow. Blender4.3.2. Shared `limestone_pilot_surface.py` and `rock_pilot_surface.py` are included. Only base-colour palette/mineral warmth and Blender fallback colour differ; normal/roughness/AO maps retained. Editable source `quarry-grey-limestone-pilot.blend`; runtime `quarry-grey-limestone-pilot.glb`. Metres, BlenderZ-up/front−Y→glTFY-up/front+Z, bottom-centre pivot. LOD0/1/2=32616/10440/2820 triangles; proxy12. UVs/normal/indices/positions preserved. Select one LOD and hide `Rock_Collision`; glTF does not encode hidden nodes. Source2048/runtime1024 PBR maps; OpenGL tangent+Y normal, packed AO/roughness/metallic. No Draco/Meshopt/KTX2 loader added.

Preview after extraction: `python reports/grey-limestone-pilot-2026-10-12/preview/serve-preview.py`, then localhost:3003. Pale and grey limestone comparison under unchanged approved Hub lights. No physical GPU benchmarks claimed.
