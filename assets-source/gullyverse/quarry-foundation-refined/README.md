# Stage2C.5.1 — bounded geology refinement

Original Stage2C.5 source and maps remain unchanged at their original paths. This new
editable master has two adjoining refined regions in the same connected shell,
three actual wall LODs, graded outer land and45 sparse foot fragments.

```sh
python scripts/blender/refined_foundation_terrain_material.py
blender --background --python scripts/blender/author_refined_quarry_foundation.py
node reports/stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/validate-gltf.mjs
blender --background --python reports/stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/validate-foundation.py
```

Blender4.3.2; NumPy in Blender. The authoring script borrows the accepted map
files from assets-source/gullyverse/quarry-foundation/textures. Outer terrain maps use filtered residuals of the same accepted source.
The three cliff image payloads are byte-identical; no source download is needed. Textures are packed into the editable master.
Metres; Blender(x,-z,y) exports to glTF Y-up. Original foot/tunnel/navigation
unchanged, bounded local rim changes are intentional. Remaining wall positions
and indices are byte-equivalent; actual exported invariants are unit-tested.

Runtime geometry is material-free. One session-owned
foundation-materials.glb supplies six shared maps for all regions. No extra map
sets per wall or new licensed source family are introduced. Do not render
material-holder meshes. Clone meshes borrow cached resources and must not dispose
them. No collision registry changes: collision-reference export is diagnostic.

Review only: /?arrival=hub&quarryReview=foundation-refined, with the existing
NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1 build flag. Original candidate:
/?arrival=hub&quarryReview=foundation. No public-default promotion.
