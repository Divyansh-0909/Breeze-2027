# Original quarry rock — Stage 2A pilot

This is ONE independent original metre-scale rock segment. It does not replace approved production art. The production application does not import/request these pilot files.

Authoring: Blender 4.3.2, metres, Z-up, front -Y. glTF exports Y-up, front +Z. Origin is the bottom centre. The master has an editable ~101k-triangle source sculpt, explicit runtime LOD collections and a conservative convex collision hull. The topology is a closed stratified/faulted surface model, not a displaced stock primitive. The source maps are original, uniquely mapped 2048px images; reference photographs are not texture inputs. Runtime maps are 1024px: sRGB JPEG base color, linear OpenGL tangent normal, linear packed AO/roughness/metallic (metallic zero). The Blender exporter generates the ORM image from the separate source nodes. No Draco, Meshopt or KTX2 is assumed or added.

Reproduce from repository root:

```sh
python3 scripts/blender/rock_pilot_materials.py
blender --background --python scripts/blender/author_rock_pilot_2a.py
node reports/stage-2a-asset-pilot-2026-10-11/scripts/preview-server.mjs
```

Python requires numpy and Pillow; Blender ships its numpy. Use the pinned Blender version for equivalent exports. Scripts write only this new pilot's asset-source and public pilot-rock directories; they must not be repointed at the original stage assets.

`quarry-rock-pilot.glb` combines three explicitly named LOD nodes and `Rock_Collision` with a shared material/texture set. **glTF does not encode node visibility:** a consumer must select exactly one visual LOD and hide the proxy, as the isolated preview does. Do not drop the combined asset unfiltered into production. Separate `rock-lod0.glb`, `rock-lod1.glb`, `rock-lod2.glb` and `rock-collision.glb` are available. Loading all separate visual GLBs duplicates their texture caches; the preview intentionally uses the combined GLB to share resources. No automatic runtime LOD policy is claimed.

The proxy conservatively encloses all runtime LOD vertices. It is only an isolated raycast test, not a change to existing movement polygons. Pilot placement [47.4,0,-104], yaw -pi/2, is used in the separate preview; it is not registered in the production world. Context mode keeps the existing procedural wall intact behind the pilot. Default preview modes have current quarry-global lighting and an exact original rock fragment/common terrain. The procedural fragment and pilot are different-sized objects: matched cameras/light demonstrate material/topology differences, not identical silhouettes.

Originality: morphology, seed, textures and UVs are generated specifically for this project; no third-party texture or reference-photo extraction is used. Existing project's logos and approved scene geometry are referenced only by the development preview.

Human visual review is required before Stage 2B or any permanent substitution. Physical-device measurements remain pending and do not prevent this bounded authoring pilot.
