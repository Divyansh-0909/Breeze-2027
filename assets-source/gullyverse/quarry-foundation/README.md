# Stage 2C.5 dark-rock foundation

This editable study changes two adjoining wall regions and surrounding land in
an opt-in review mode. It does not replace the public quarry or any stage asset.

Reproduce from the repository root with Blender4.3.2, Python3, NumPy and Pillow:

```sh
python scripts/blender/foundation_source_materials.py
python scripts/blender/foundation_materials.py
blender --background --python scripts/blender/author_quarry_foundation.py
node reports/stage-2c5-photorealism-foundation-2026-10-13/scripts/validate-gltf.mjs
blender --background --python reports/stage-2c5-photorealism-foundation-2026-10-13/scripts/validate-foundation.py
```

The glTF validation command uses the separately installed Khronos validator;
install `gltf-validator` and update the script's local module path if necessary.
No new runtime loader/compression dependencies are required. Source download
needs the recorded provider API files in the evidence directory; all original
downloaded maps are also supplied in `licensed-source/` for offline authoring.

- `quarry-foundation.blend`: editable runtime surface partitions, three wall
  LODs, shared packed PBR maps and authoring contract text. Objects remain
  editable polygon surfaces; the deterministic height/stratigraphy field is
  in `scripts/blender/foundation_geometry.py`.
- `licensed-source/`: original CC0 provider maps, metadata and license.
- `textures/`: derived dark-mineral maps and selected-height residuals.
- `source-provenance.json`: URLs, license, attribution, SHA256 and provider MD5.
- `material-manifest.json`: resolution, colour reference and artistic amplitude.
- `manifest.json`: anchors, LOD nodes, regions and hashes.

Metres throughout. Blender `(worldX,-worldZ,worldY)` exports to glTF Y-up.
Wall UVs use perimeter arc/2 and elevation/2: a2m mineral tile, without atlas
reflection. Terrain UVs are Cartesian XZ/90 using the provider's nominal90m
surface extent. Vertex colour modulates regional weathering and is explicitly
bounded below1 before normalized glTF export. These are authored surfaces,
not a scan of a physical quarry. Provider API metadata does not establish
capture method or physical displacement amplitude.

The shell is intentionally open at its buried foot, far-land boundary and
original tunnel attachment. It is not a watertight underground solid. Interior
edges and cross-LOD borders must remain continuous. Collision exports are
diagnostic raycast surfaces; authoritative walking polygons are unchanged.

Geometry-only exports use one material-holder GLB. Holder meshes are never
rendered. All wall nodes share one rock material; terrain shares another.
Terrain macro geometry and small scree geometry are shared between levels;
wall detail has real three-level topology reduction. Only one node per part
is visible. Cache owners dispose geometry/materials/textures and image bitmaps;
render clones must never dispose borrowed resources.

Build review mode with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` and open
`/?arrival=hub&quarryReview=foundation`. Use the review buttons to restore the
connected original-rock baseline. Removing the query restores the ordinary
website. Original assets remain in their original paths.
