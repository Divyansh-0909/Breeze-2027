# Grey limestone — colour revision

The limestone is now cooler grey with less yellow/beige. Previous pale limestone and the original rock pilot are preserved in their existing directories. No production source/assets/lighting/camera/navigation changes, no commit/push/deployment.

[Actual before/after gallery](gallery.html), [capture metadata](raw/captures.json), [colour-only verification](raw/colour-only-verification.json), [GLB validation](raw/glTF-validator.json).

[Blender master](../../assets-source/gullyverse/limestone-grey-pilot/quarry-grey-limestone-pilot.blend), [runtime GLB](../../public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb), [author/export instructions](../../assets-source/gullyverse/limestone-grey-pilot/README.md).

Source baseRGB184/188/193 replaces224/221/208; mineral rust warmth reduced. Same limestone weathering/shape/roughness/normal strength/UVs/collision/LODs. Exact exported positions/normals/UVs/indices and six non-colour source/runtime image hashes match. Blender re-export regenerated one LOD0 tangent component differing by about0.0001; this is quantified in verification, not claimed byte-identical. Geometry and normal maps are unchanged. Five GLBs validate with zero errors/warnings.

Four actual Chromium captures,1366×900,DPR1,FOV58; medium[31,5.6,-98] and close[41.1,5.4,-103.4], current Hub lights/ACES exposure1 unchanged. Context retains approved procedural wall behind the isolated pilot. No screenshot recolouring or synthetic renders used. Renderer is SwiftShader; no new physical benchmark or memory certification is claimed for this colour-only revision. All664 original production baseline files and prior limestone source/exports/review package hashes remain unchanged.

Extract `gullyverse-grey-limestone-pilot-review.zip` and run `python reports/grey-limestone-pilot-2026-10-12/preview/serve-preview.py`, then open localhost:3003. Package includes prior pale GLB for comparison, new grey source/maps/exports, shared authoring field and bundled viewer/font. Default production website remains unchanged.
