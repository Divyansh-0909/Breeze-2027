# Rev15P2 — browser night lighting and performance

12 November 2026, Asia/Kolkata. The user authorized continuing the isolated pilot and asked that the original website quarry movement flow be preserved. This update changes the private browser asset/viewer only. It restores static shadows, fixes the floor lightmap and damp roughness mapping, removes most runtime lighting work and leaves the live website, movement controller and entrance/exit transitions unchanged.

The updated asset is 16,701,980 bytes, down from 23,776,228 bytes (29.8%). All 447,269 source triangles, node transforms, positions, indices, UV0 artwork coordinates and retained base image bytes remain unchanged. The UV1 floor atlas is deliberately corrected. Original Rev15O and the packed 46-scene Rev15P source master are untouched.

## Lighting changes

Cycles baked diffuse direct/indirect illumination onto the compiled mesh, using the native lamp transforms, shapes, powers, colours and world. Four samples and up to three bounces were used. Metals were neutralized for a reusable diffuse illuminance field; original base artwork remains a separate unchanged map. The per-corner result is averaged to the existing export points and encoded as normalized 16-bit linear RGB. The material's explicit `nativeLightfieldScale=32` restores its range in Three.js; matching original emissive image contributions are preserved. No component clips at that scale.

The static scene uses lightweight unlit materials. Live normal/roughness maps and multiple lamps are removed from those surfaces. Four ground meshes retain a standard material with a single specular-only point light, preserving camera-dependent damp highlights while the main diffuse/shadow response remains baked. It is an approximation of the native area-light reflection and has no runtime shadow map. Native roughness noise is baked separately into the same atlas.

The previous test checked that a second UV existed, but two ground meshes contained metre-scale coordinates there. The new pass gives all four floors explicit non-overlapping, bounded tiles in a 1024 × 2048 atlas and explicitly requests that UV layer during baking. The viewer binds it on channel 1. This fixes actual sampling, beyond merely checking the attribute's presence.

Fog density remains 0.024. Its displayed target colour is calibrated to the fully fogged native reference sky (RGB8 19, 28, 37). Exposure follows the native 0.25-stop setting. The sponsor shader retains its two exact 5338 × 64 atlas tiles, 10,676-cell period, logo spacing, pause and reduced-motion behaviour. No thick particle layers, SSR or duplicate canvas is introduced.

## Preservation and movement

The original quarry runtime, navigation, input, rendering shell, hub, cave entrance and world files have recorded SHA-256 values and are unchanged. The production `app`, `components/immersive` and `lib` tracked diff is empty; HEAD remains `0e1e23dd2f5181df202d862d147067249bc55a41` on `work-in-progress-2027`. The existing README modification predates this task and is retained. No commit, push, PR, deployment or production integration occurred.

This is source preservation, not a claim that the new model has already been integrated or exercised through the production movement flow. Future integration must bind these materials/assets into the existing one-canvas runtime and keep its movement controller and transitions. The pilot's three fixed review cameras do not replace the website controls.

Packed native source SHA-256: `f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682`.

## Same-harness measurements

Chromium uses ANGLE SwiftShader in this cloud environment. Desktop is 1440 × 900 at render DPR 1. Emulated mobile is 390 × 844, device DPR 2 capped to render DPR 0.85, with 4× CPU throttling. Each view has two warm-up renders and five measured renders. A synchronous one-pixel readback forces completion; its overhead is included. CPU submission is measured separately. These are render-cost diagnostics, not display FPS, network delivery estimates or physical-device certification. Tail percentiles from five samples are descriptive only.

| Profile / view | Before mean ms | Updated mean ms | Reduction | Updated render p50 / p95 / p99 ms | CPU submission p50 / p95 / p99 ms | Valid GPU p50 / p95 / p99 ms |
| --- | ---: | ---: | ---: | --- | --- | --- |
| desktop / far | 4538.3 | 1303.5 | 71.3% | 1314.1 / 1362.1 / 1362.1 | 1.6 / 2.1 / 2.1 | 1301.3 / 1351.1 / 1351.1 |
| desktop / middle | 4605.0 | 1448.4 | 68.5% | 1425.0 / 1570.6 / 1570.6 | 0.9 / 1.4 / 1.4 | 1411.3 / 1561.0 / 1561.0 |
| desktop / near | 1957.8 | 772.0 | 60.6% | 771.7 / 870.7 / 870.7 | 1.3 / 2.6 / 2.6 | 759.7 / 854.5 / 854.5 |
| mobile-emulated / far | 537.2 | 285.9 | 46.8% | 297.9 / 308.2 / 308.2 | 9.1 / 11.6 / 11.6 | 287.1 / 301.3 / 301.3 |
| mobile-emulated / middle | 643.4 | 328.0 | 49.0% | 345.3 / 352.2 / 352.2 | 5.8 / 39.5 / 39.5 | 333.3 / 347.0 / 347.0 |
| mobile-emulated / near | 538.7 | 235.1 | 56.4% | 212.4 / 290.1 / 290.1 | 3.5 / 5.1 / 5.1 | 206.5 / 280.4 / 280.4 |

In these conditions, desktop render cost falls by roughly 61–71% and emulated-mobile cost by 47–56%. Draw calls stay at 95–128 depending on the view; this pass improves material/lighting cost, not mesh count. No geometry compression or LOD change is used to obtain the result.

The fair texture-source estimate rises slightly, from 145,513,472 to 149,707,776 bytes (about 2.9%), because the floor maps are higher resolution. Both versions use the same source/sRGB-variant/mip estimate. It does not measure driver VRAM or allocation padding. Geometry attribute bytes fall because unused normals/tangents are removed from static materials. Ground normals are derived at runtime for the four specular surfaces. Shader programs, load/compile times, bytes and raw samples are in `evidence/browser-comparison.json`.

Valid GPU query times are reported only when completed and non-disjoint; extension availability alone is not a result. Physical GPU performance, physical-phone FPS, input latency, battery/thermal behaviour and full-world production movement remain unmeasured. The desktop ~60 FPS and mobile >=30 FPS goals are not certified and remain unmet on this software renderer.

## Visual and functional checks

Matching far/middle/near captures compare the native reference, the previous browser and the updated browser. Whole-frame RGB error against the native reference falls in all three views; this is a descriptive check, not a perceptual-fidelity guarantee. Static shadows and shop interiors now follow the baked lighting. View-dependent metal response and very large sparsely sampled faces remain approximations.

Both versions/profile sets pass one-canvas, HTML directions, reduced-motion pause, LED count, second-UV presence and GL-error checks. The updated compile separately verifies valid ground atlas coordinates, original geometry/UV0/image hashes and movement-file preservation. There are no console or page errors in the comparison run. The review PDF is the user-facing visual deliverable.

## Recovery and delivery

All new files are under `reports/night-atmosphere-rev15p2-browser-2026-11-12`. `viewer/` is standalone with its bundled Three.js runtime. `source/` contains the bake, compile, server, comparison and review scripts. `evidence/` records hashes, raw lightfields, atlas metadata and test results. The packed native master and exact baseline GLB remain in the verified local Rev15P base checkpoint; they are not overwritten.

The user permitted PDF delivery to Breeze Drive. The source checkpoint remains local under the pilot source-upload restriction; PDF permission is not treated as permission to upload the entire editable source. The incremental local archive contains the new implementation, screenshots, PDF, restore instructions and checksums, with an explicit dependency on the already verified complete Rev15P base checkpoint. The Drive review PDF is separately verified by parent, size and authenticated download-back SHA-256. Earlier folders and sharing settings remain unchanged.

Existing local base: reports/night-atmosphere-rev15p-pilot-2026-11-11/checkpoint/Rev15P-Night-Pilot-Local-Checkpoint-20261111.zip; SHA256 df53edfb1d95dde30c3e3dfe140a730daec7a8b50d4dd79e575df7f8ba5340ac. Review phase: https://drive.google.com/drive/folders/1vn7QXmd8rfsCo0gb4eUjCJRG9x3H051e

PDF review folder: https://drive.google.com/drive/folders/1Oo7900mJqgq27s0rDOfgWElZ20kDH81N

The night look is retained as an isolated candidate. Full-environment rollout and production movement integration are not started by this handoff. Next work should validate representative physical hardware and address texture compression/streaming and culling/LODs before making a production performance claim.
