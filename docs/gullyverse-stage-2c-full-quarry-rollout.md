# Gullyverse Stage 2C — Full quarry rollout

2026-10-12 · Implemented locally; stop for user visual review. **No commit, push or deployment.**

## Approved baseline preserved

Branch `codex/navigation-board`, HEAD `e3dbbc233f1f12f5e4d96333db3b797e75da4760`, unchanged. The four initially dirty tracked files and relevant untracked pilot work were preserved. The user's approval of the corrected cool grey limestone pilot governs this rollout. [Exact starting state](../reports/stage-2c-quarry-rollout-2026-10-12/raw/starting-state.json), [recoverable scoped backup](../reports/stage-2c-quarry-rollout-2026-10-12/backup/current-approved-wall-baseline.tar.gz), [final hashes/status](../reports/stage-2c-quarry-rollout-2026-10-12/raw/final-preservation.json).

Of 119 protected files, 115 remain byte-identical; four existing integration files changed. Original stage/crowd GLBs, video and stage code, lighting/fog, ground, scaffold/signs, stalls, coordinates, movement bounds, camera/map and navigation systems are preserved. `rendering.tsx` retains its pre-existing user edits untouched. Payment/admin/routes were not edited. Walking-area extent remains 97.8 × 123.5 m; visible surrounding solids retain their larger 142.62 × 159.36 m combined bounds. Stage origin remains `[-12, 0, -134.3]`.

## Implementation

The 25 perimeter solids now use closed authored limestone geometry, replacing their procedural render surfaces. Independently seeded uneven rock units, interrupted fractures, localized scars and edge chips provide variation. Fracture depth scales to each host's size and remains bounded inward. Original corner anchors and enclosing bounds are retained. The approved pilot body and neighboring fitted contact skins are preserved.

Two fitted parts connect the quarry-facing tunnel collar and rear exterior crown. The collar follows the existing bend; section-local crown seams were stitched. Only 168 rear exterior vertices are replaced. All 10,080 enclosed-passage vertices, remaining entrance-facing shell, portal, paint and choreography remain unchanged.

A deeper trial exposed one ground-level sightline gap: radial carving lifted a low sloping face. An irregular terrain-contact band now retains the original foot, with its crease samples protected during LOD simplification. No ground or boundary change was needed. The final survey preserves all **301 horizontal source-blocked rays at every LOD**, with zero new gaps. [Coverage](../reports/stage-2c-quarry-rollout-2026-10-12/raw/perimeter-coverage.json), [superseded failure](../reports/stage-2c-quarry-rollout-2026-10-12/trials/deep-before-ground-contact/perimeter-coverage.json).

The approved material JSON, three embedded image byte hashes and eight original map files are unchanged. Fine-normal UV scale remains 12 × 10 m and normal strength approximately 0.58; new side UVs use the same limestone family. No global light/exposure adjustment was made. [Material lock](../reports/stage-2c-quarry-rollout-2026-10-12/raw/material-lock-validation.json).

## Assets, LODs and ownership

There are 27 independently selected parts, with whole-asset LOD totals **338,048 / 135,814 / 34,960 triangles**. Only one LOD per part draws. Selection uses projected size, viewport/FOV, drawing-buffer resolution, adaptive tier and hysteresis; meshes retain frustum culling. Existing movement/collision stays authoritative; the separate hidden 900-triangle reference proxy is not a replacement collision system.

The combined runtime GLB is **18,594,988 bytes**, reduced from 23,344,400 using native loader-supported `KHR_mesh_quantization` for new normal/tangent/UV0 attributes. Positions, accepted pilot attributes and image bytes are unchanged. No new compression loader or dependency was added. Standalone review LOD exports are 12,226,984 / 6,447,240 / 3,271,672 bytes; only the combined asset downloads.

One visible limestone material and three shared maps serve the quarry: approximately **12 MiB decoded RGBA with mipmaps**, an estimate rather than driver VRAM. All three LODs remain resident and receive covered shader/texture warm preparation. This avoids first-use uploads at the cost of residency and initial transfer. Scene clones borrow the cache; owner retirement waits for consumers. No shared stage assets are evicted.

[Editable Blender master](../assets-source/gullyverse/quarry-rollout/quarry-limestone.blend) · [Runtime GLB](../public/models/gullyverse/quarry-rollout/quarry-limestone.glb) · [Reproducible workflow](../assets-source/gullyverse/quarry-rollout/README.md) · [Inventory](../reports/stage-2c-quarry-rollout-2026-10-12/raw/asset-inventory.json).

## Visual comparison

[Open the gallery](../reports/stage-2c-quarry-rollout-2026-10-12/gallery.html): **14 matched pairs / 28 browser PNGs**, covering exit, center, stage-facing, left/right walls, aerial map and stage looking back, at desktop 1366 × 900 and portrait 390 × 844. Every pair has identical camera/orientation/FOV, effective DPR and quality. [Before metadata](../reports/stage-2c-quarry-rollout-2026-10-12/raw/before-captures.json) · [After metadata](../reports/stage-2c-quarry-rollout-2026-10-12/raw/after-captures.json). Fixed inspection poses and public map/travel captures are identified; mobile views are emulation.

The perimeter now shares limestone coloration and fractured surfaces. Large inherited angular contours and light/shadow bands remain apparent, particularly from above and at the crown. Macro anchors/bounds are preserved; **13 upward sampled sightlines changed** with local contour treatment, including **1 LOD hit disagreement**. Those are published for review, not represented as pixel-identical silhouettes or universal seam perfection. Photorealism and full-rollout visual approval are not claimed.

The preparation cover also hid the existing native-fallback footer. It now draws above that cover while loading; normal ready-state composition is unchanged. [Before](../reports/stage-2c-quarry-rollout-2026-10-12/raw/loading-access-before.png) · [After](../reports/stage-2c-quarry-rollout-2026-10-12/raw/loading-access-after.png) · [Browser check](../reports/stage-2c-quarry-rollout-2026-10-12/raw/loading-access-after.json).

## Matched performance

Debian 13.6 VM, three AMD EPYC 9V74 vCPUs, Chromium 151.0.7922.173, **SwiftShader software rendering**. Fixed matched cameras, 1366 × 900, DPR 0.5, quality 3; ten-second sequential windows without competing capture/authoring load or artificial throttling. One paired run is diagnostic, not hardware certification.

| View | FPS before → after | p50 ms | p95 ms | p99 ms | Draw calls | Triangles |
|---|---:|---:|---:|---:|---:|---:|
| Quarry center | 4.04 → 3.94 | 250.7 → 257.9 | 291.7 → 303.6 | 292.9 → 311.3 | 142 → 160 | 94,674 → 154,026 |
| Left wall | 3.21 → 3.10 | 308.2 → 321.4 | 364.4 → 387.8 | 367.9 → 393.9 | 48 → 58 | 83,960 → 126,548 |
| Right wall | 3.47 → 3.18 | 289.1 → 304.9 | 359.7 → 363.7 | 361.7 → 385.2 | 22 → 31 | 89,852 → 143,212 |

Settled textures remain 28; geometries increase 152 → 222. Diagnostic geometry payload grows 3.55 → 18.43 MB; total texture estimate remains 57.61 MB. After-run heap snapshots span 53.7–86.9 MB, not a retained-heap leak proof. Maximum after frames are 316, 400, 386 ms respectively. [Raw before](../reports/stage-2c-quarry-rollout-2026-10-12/raw/before-performance.json) · [Raw after](../reports/stage-2c-quarry-rollout-2026-10-12/raw/after-performance.json) · [Hardware/method](../reports/stage-2c-quarry-rollout-2026-10-12/raw/hardware-profile.json).

One after-run recorded 1169.3 ms load readiness, 50.8 ms parse, 10.6 ms texture initialization, 48.3 ms compilation and 2730.8 ms covered preparation. Cache-disabled localhost landing responses increase **3.91 → 14.86 MB**, comparing single-pilot baseline with full rollout; landing readiness 7367 → 8402 ms. GPU shader caches may persist between contexts. [Network evidence](../reports/stage-2c-quarry-rollout-2026-10-12/raw/network.json).

**Physical integrated-GPU laptop, iPhone and Android acceptance is PENDING.** No sustained 60 FPS or leak-free VRAM claim is made. For local verification, repeat paired URLs at identical camera/FOV/DPR/tier, then separately test native adaptive settings; collect three 30-second windows plus map/travel/playback, network and GPU identity under comparable cache/thermal conditions.

## Verification and handoff

Type checking, lint with existing warnings, production build and **64 unit tests PASS**. All eight existing browser groups pass for the final geometry/runtime. The final temporary footer-stacking adjustment was additionally checked through actual delayed-loading captures and recovery tests. **Ten toggle cycles, ten map-mediated Hub ↔ Aftermovie round trips and ten playback/exit cycles PASS**, including toggles during playback. The persistent Canvas and settled resource counters plateau; explicit quarry-cache retirement returns cold reference counts. Actual context loss/restore, optional-load failure/retry, delayed-load abandonment and critical-stage fallback pass. [Commands/results](../reports/stage-2c-quarry-rollout-2026-10-12/raw/test-summary.json) · [Toggle lifecycle](../reports/stage-2c-quarry-rollout-2026-10-12/raw/lifecycle.json) · [Travel](../reports/stage-2c-quarry-rollout-2026-10-12/raw/navigation-cycles.json) · [Playback](../reports/stage-2c-quarry-rollout-2026-10-12/raw/video-with-wall.json) · [Recovery](../reports/stage-2c-quarry-rollout-2026-10-12/raw/recovery.json).

Five final GLBs validate with zero errors/warnings; proxy-only unused attributes are informational. Exported meshes are closed, consistently wound and positive-volume. Every rock LOD remains inside its source hull and retains its corners within 3e−5 m; 84 eye-height corridor samples per collar LOD remain clear. [glTF](../reports/stage-2c-quarry-rollout-2026-10-12/raw/glTF-validator.json) · [Topology](../reports/stage-2c-quarry-rollout-2026-10-12/raw/exported-topology-validation.json) · [Shape/corridor](../reports/stage-2c-quarry-rollout-2026-10-12/raw/shape-validation.json). Earlier authoring failures and superseded trials are retained, not presented as final passes.

Existing files changed: `AftermovieScene.tsx` dispatches the quarry component; `HubScene.tsx` swaps perimeter/exit/rear-shell geometry; `ImmersiveShell.tsx` handles default/reversal and covered preparation/access; `wallSection.ts` adds manifest guards and loading. New `QuarryPerimeter.tsx`, `quarryRollout.ts`, Blender authoring/quantization scripts, two regression cases, assets and evidence support this integration. [Exact patch against starting worktree](../reports/stage-2c-quarry-rollout-2026-10-12/raw/stage-2c-source.patch).

Reversal: **`?quarry=original`**, or build with **`NEXT_PUBLIC_GULLYVERSE_QUARRY_ROLLOUT=0`**. The earlier single-pilot preview remains available with its existing preview build flag. No new ordinary navigation controls were added.

Intentionally deferred: entrance/enclosed-tunnel art, graffiti, detailed stalls and hub people; approved ground and original stage surroundings/floor remain unchanged. Additional contour/seam/LOD refinement is subject to visual review. Device budgets and initial transfer/residency remain risks before deployment. No new destination or subsequent production phase was started. **Stop for user review.**
