# Rev15P2 — browser lighting and performance

12 November 2026 (Asia/Kolkata). The user authorized continuing the isolated pilot, matching browser lighting to the native Blender renders and improving performance. All visual delivery will be a PDF. Breeze Drive PDF delivery is authorized; the editable checkpoint stays local under the pilot source-upload restriction; production integration, full-world rollout, commits, pushes and deployment are outside this task.

Keep Rev15O and the Rev15P master unchanged. Reuse the packed Rev15P master (SHA256 f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682) as the lighting reference and preserve the Rev15P plain GLB's positions, indices, artwork and UVs. No new native copy is needed because the intended changes are the compiled web asset and private viewer only.

The current browser has 447,269 triangles, 84 materials, 128 merged mesh objects and live PBR lighting. It lacks most baked occlusion/shadow response and spends substantial software-rendering time on per-pixel lighting and normal maps. Its prior three-frame, gl.finish benchmark is too small for stable percentile or physical-device claims.

Proposed files, confined to this directory:
- source/: bake the native lamp/world light response onto vertex colours, compile a compact unlit GLB, local server, browser checks and PDF/report/checkpoint scripts.
- viewer/: compiled model, camera settings, exact sponsor atlas tiles, runtime modules and browser viewer. Static diffuse illumination is baked; the original artwork remains in the base maps. Floor lighting retains an explicitly bound UV1 lightmap.
- evidence/: source hashes, geometry/UV/art preservation checks, bake findings, same-harness baseline/updated timing samples and functional checks.
- renders/ and review/: matching native/old-browser/updated-browser far/middle/near captures and a PDF.
- REPORT.md, RESTORE.md and checkpoint metadata.

First test Cycles vertex-colour baking on the actual compiled mesh with native lamp transforms, powers, colours, shapes and world. If supported, bake diffuse direct/indirect illumination offline and remove runtime lamp/normal-map work from static materials. Preserve emissive artwork and fog on the sponsor shader. Retain geometry/topology and evaluate spatial culling or LOD only if measurements justify another change.

Use the same local Chromium/SwiftShader conditions for baseline and updated comparisons, report sample counts and separate render completion from animation-frame cadence. GPU timings are reported only if valid non-disjoint queries complete. Desktop/mobile-emulated results do not certify hardware or physical phones. Verify one canvas, no duplicate asset residency, near text, distant fog, exact sponsor spacing, reduced motion, and standalone restoration. No performance claim precedes measurements.
