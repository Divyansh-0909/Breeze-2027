# Rev15P isolated night-atmosphere pilot — authorized scope

The user authorized implementing the latest next prompt on 11 November 2026. The shared document's final section is “NEXT CODEX PROMPT — REV15P NIGHT ATMOSPHERE PILOT (2026-11-11)”. Its restrictions apply: local isolated pilot only, no production route changes, no Drive writes, no commits, pushes, PRs or deployment. Rev15O remains authoritative pending review.

## Read-only gate completed

Blender 4.3.2 successfully opened the actual Rev15O packed master. SHA-256 matches `2c78b57e97a5a97683f946d60ad265b22a1eb88ae12abed6220ec268ce473657`; branch is `work-in-progress-2027`, HEAD `0e1e23dd2f5181df202d862d147067249bc55a41`. Full inventory: `evidence/inventory.json`, generated without saving the source.

The current scene has 1,601 objects, 1,412 mesh objects, 1,344 unique meshes and 690,617 raw triangles before modifiers/text conversion/visibility filtering. It has 189 native crowd mesh objects, no armature objects, 18 lights and 124 materials including object-level overrides. The packed file has 45 scenes, no linked libraries and 69 images across its history, with 95,446,183 packed image bytes. 1,404 mesh objects have at least one UV channel. Existing actions/drivers include the sponsor strip and carousel visibility. All objects, camera matrices, light/shadow parameters, materials/node graphs, UV names, image sizes and packed/missing state are recorded in the inventory.

Portability findings: the painted-brick node group, spatial Events shader mixing, world-coordinate texture sampling, plywood noise, volume haze and LED animation do not automatically reproduce in glTF. The crowd is static shared mesh data, not skeletal animation. Existing UVs do not establish a valid unique, non-overlapping second-UV lightmap atlas. Ordinary Principled PBR/image inputs are exportable; unsupported effects require explicit baking/conversion. The first mesh-data-only material pass counted 102; the completed audit includes the object-slot overrides and records 124. Full-lane raw draw count and image residency need reduction before production use.

The website is a separate older hub/blockout: React 19.0.8, R3F 9.6.1, Three.js 0.169.0. `components/immersive/ImmersiveShell.tsx` uses one Canvas. `rendering.tsx` implements quality/DPR adaptation, texture initialization, compileAsync and warm-up; `diagnostics.ts` records frame, CPU submission, GPU query and memory estimates. `scripts/perf-gullyverse.mjs` provides quantile summaries and desktop/mobile-emulated profiles. The pilot will reuse those measurement conventions without loading or modifying production routes.

## Exact proposed output locations

All implementation files are beneath `reports/night-atmosphere-rev15p-pilot-2026-11-11/`:

- `source/`: inventory, isolated build, export/material conversion, rendering, local server, browser measurement and review-generation scripts.
- `delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend`: all 45 source scenes retained, plus a separate pilot scene with independently editable look settings.
- `viewer/`: representative GLB, converted/baked textures, Three.js test viewer, local navigation alternative, pause/reduced-motion handling and camera settings. Three.js and loader/decoder modules are served from the existing installed dependency; no package or app files change.
- `renders/` and `review/`: fixed far/middle/near Blender/browser captures, before comparisons and combined PDF/gallery.
- `evidence/`: inventories, source hashes, preservation diff, material/export records, compression results, screenshot checks, performance data and logs.
- `REPORT.md`, `RESTORE.md` and local checksum/checkpoint files.

No existing source artwork, geometry, walking route, logo, portrait or navigation wording will change. The pilot duplicates scene objects/materials/world/camera/light data before look edits. All 45 historic scene memberships remain. The export is a representative approach/lane/nearby-cypher subset, derived from evaluated meshes; any LODs, material conversions or merging occur only in disposable export data. Original shop shutter geometry stays as authored: selective lighting will identify the few active storefronts rather than rebuilding shop fronts.

## Look and verification plan

Use a restrained blue-grey ambient fill and localized warm shop/street pools, reduce broad existing fill, keep artwork readable nearby and add occasional damp roughness. Fog should soften distant logo and board; use matching numerical distance-fog settings in Blender comparison and the browser. Avoid runtime volumetric fog and shadow-heavy lamp proliferation. Static light response will be baked/converted where feasible; any unbaked or visually approximate material must be reported honestly.

Use three fixed matching cameras and record their exact transforms/projection. The browser uses one canvas and one resident asset, exposes a persistent HTML navigation alternative, and pauses animation under reduced motion or explicit pause. Measure frame intervals and CPU render submission p50/p95/p99, GPU time only if the timer extension exists, draw calls, triangles, transferred bytes, compile time and estimated texture memory. Emulated mobile uses a documented viewport/DPR and CPU throttle; it is not physical phone or thermal certification. Report unmet targets and scaling limits rather than claiming production readiness.

Disk space was recovered only from prior authenticated, hash-verified duplicate download staging files; `evidence/staging-cleanup.json` records each removed path and its existing verified remote source. Original masters and reports remain.
