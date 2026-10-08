# Environment delivery contract

The React hub and tunnel are temporary movement blockouts. No realism approval
is implied. Supplied real photography is the art authority. Replace the major
shells with authored Blender assets; retain existing `aftermovie-stage.glb`.

## Authoring and exports

Use one Blender master scene in metres (Z-up in Blender; exporter converts to
glTF Y-up). Save a versioned master outside `public`, with packed/linked source
textures and reference photography. Separate export collections:

* `ENTRY_HUB_CRITICAL`: entrance exterior, the only main tunnel, hub rock bowl,
  ground, scaffold signs and basic festival infrastructure. This is one persistent
  world for both URL states, following the Stage 1 coordinate registry.
* `DESTINATION_ANCHORS`: Team/Contact/reserved zones, the original stage origin,
  permitted viewing area and continuous arrival/return anchors. Do not export a
  second quarry, a stage proxy or replacements for the original stage/LED rig.
* Optional dressing collections per zone: removable clutter and distant props.

Rock is irregular authored topology, not scaled primitive rocks. Keep a huge
opening overhead. Use concrete damage, stains, layered paint and natural light.
Do not bake orange theatrical washes or mirror-like floors into the environment.
Optimize hidden faces and LOD silhouettes without changing the visible shapes.
Bake static occlusion/lighting into textures where useful; keep dynamic shadows
off in this slice. Apply transforms; check normals, UV density, scale, pivots and
material slots. Share material atlases for repeated structures, with enough
variation to avoid obvious tiled graffiti or identical weathering.

Export GLB with Principled materials and named empties included. Bake UVs and
roughness variation; use sRGB for base color and linear normal/roughness/AO.
Author textures at source quality, then prepare appropriate web resolutions.
Use glTF Transform/Blender export simplification offline and Meshopt or Draco
only when the measured byte/CPU tradeoff helps. Run Khronos glTF Validator.
Prepare KTX2/Basis (ETC1S for color when appropriate; UASTC for normal/detail
maps); inspect artifacts on real devices. Commit decoders locally and configure
`KTX2Loader.detectSupport(renderer)` / `MeshoptDecoder` or `DRACOLoader` before
shipping compressed GLBs. Current blockout assets do not use those extensions;
no pretend decoder integration or compressed-art claim is made.

## Spatial authoring contract

Preserve glTF node names and export empties:

| Node | Purpose |
| --- | --- |
| `spawn_hub`, `arrival_start_hub` | Hub eye-height arrival poses |
| `spawn_aftermovie`, `arrival_start_aftermovie` | Bounded crowd viewing poses |
| `entrance_00` through `entrance_04` | Ordered cinematic camera anchors |
| `route_hub_aftermovie_min`, `route_hub_aftermovie_max` | Commit threshold corners |
| `route_aftermovie_hub_min`, `route_aftermovie_hub_max` | Return threshold corners |
| `quarry_boundary_00` onwards | Ordered ground-level collision polygon |
| `walk_hub_min`, `walk_hub_max` | Broad movement limits, refined by polygon/solid footprints |
| `walk_aftermovie_min`, `walk_aftermovie_max` | Viewing rectangle corners |
| `reentry_start_hub`, `reentry_end_hub` | Physical return beside the same stage |
| `stage_origin`, `destination_<id>`, `interaction_<id>` | Shared geometry and map/sign anchors |

Use empty orientation for camera direction and `extras` for destination ID,
scene residency class, and metre-based route metadata. Extract world transforms
in the offline build after Y-up conversion, validate bounds/spawns/thresholds,
and emit the same layout schema as
`public/models/gullyverse/blockout.layout.json`. The runtime graph references
that schema; spatial coordinates do not live scattered through controllers.
Replace the manifest as part of an art export, and rerun navigation tests.
Stage 1 geometry and all destination transforms now read this registry.

## Browser preparation and residency

Download/decode/parse under the covered transition. Instantiate critical
collections before readiness. Initialize all mapped and shader-uniform
textures, run `WebGLRenderer.compileAsync`, and render hidden full-resolution
frames to exercise geometry uploads and the real program variants. Only then
begin the arrival reveal. Network completion alone is not readiness. Failures
offer 2D content rather than exposing an empty scene.

Keep one renderer, input runtime, world shell and original stage. Swap only
near/far crowd detail behind the existing curtain; dispose its instance buffers.
Retain only the
small shared asset caches needed for repeat trips. Scope optional decoration
outside critical readiness; it must not change the critical scene's light count
or shader variants after reveal. Check allocation/resource counts across ten
round trips and measure rendered-frame tails while moving, not just idle FPS.

## Review gate

Before visual approval, compare matched-camera captures against the tunnel
and open-roof quarry photographs. Reject plastic rock, perfect edges, uniform
roughness, repeats, wet mirror floors, glossy concrete, excess bloom or warm
washes. Measure the authored assets again on an integrated GPU and physical
mobile devices. The blockout's performance cannot certify final art.

## Local toolchain status after Stage 1

No Blender executable is on PATH or in the inspected standard installation
folders. No editable `.blend` exists in this repository. Stage 1 uses deterministic
TypeScript blockout meshes, and does not claim Blender export validation.

After installing Blender through an approved setup, run the safe smoke test in
an empty scratch directory:

Use the official [Blender 5.2 release archive](https://download.blender.org/release/Blender5.2/)
to select a stable Windows x64 build; pin the downloaded filename, its verified
SHA256 and the reported `--version` in the authoring manifest. Check the official
[system requirements](https://www.blender.org/download/requirements/) on this
Intel/NVIDIA machine before installing. The glTF exporter performs the
[Y-up conversion](https://docs.blender.org/manual/en/5.1/addons/import_export/scene_gltf2.html).
No installation or hardware compatibility certification has been performed here.

```powershell
& 'C:\Program Files\Blender Foundation\Blender <installed-version>\blender.exe' --version
& 'C:\Program Files\Blender Foundation\Blender <installed-version>\blender.exe' --background --python scripts/blender/validate_toolchain.py -- .gullyverse-artifacts/blender-smoke
```

This writes a one-metre cube `.blend`, GLB and version manifest. Then load the
scratch GLB with the existing GLTFLoader in a temporary browser probe, verify
metre scale/Y-up/materials, and record renderer errors before production authoring.
The existing `generate_breeze_assets.py` writes over the original stage/team/help
desk exports and is not a safe toolchain smoke test. Do not run it against the
production asset directory for Stage 1.
