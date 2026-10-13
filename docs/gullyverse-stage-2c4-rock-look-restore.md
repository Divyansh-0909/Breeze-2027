# Gullyverse Stage 2C.4 — original rock-pilot look restored

The connected excavation now selects **the actual original Stage 2A darker rock material** instead of Grey limestone. Geometry, layout, lights, fog, exposure, cameras, navigation and stage assets were preserved. This is a reversible material-direction correction, **not a photorealism pass**. Stop for human visual review.

[Open the before/after gallery](../reports/stage-2c4-rock-look-restore-2026-10-13/gallery.html) · [Original Stage2A reference](../reports/stage-2c4-rock-look-restore-2026-10-13/reference/original-stage2a-rock-pilot.png) · [Matched-pose validation](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/capture-pair-validation.json).

## 1. Exact preserved baseline

- Checkout: `/workspace/Breeze-2027-navigation`.
- Branch: `codex/navigation-board`; HEAD: `e3dbbc233f1f12f5e4d96333db3b797e75da4760`. No staged changes, commit, push, deployment, reset, clean or broad restore.
- Four already-modified tracked files: `AftermovieScene.tsx`, `HubScene.tsx`, `ImmersiveShell.tsx`, `rendering.tsx`, all under `components/immersive/`.
- The initial credential-free inventory includes **1,542 pre-existing untracked files** and 1,183 tracked files. The raw Git snapshot additionally records cache/audit bookkeeping; no guessed authorship is assigned to individual user changes.
- Non-destructive backup: `reports/stage-2c4-rock-look-restore-2026-10-13/backup/current-source-assets.tar.gz`, **917 source/config/asset files, 1,033,161,990 bytes**, including relevant untracked work. Credentials, build caches and duplicate review ZIPs were excluded. It remains on disk and is deliberately not duplicated into the mobile review package.
- [Git status](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/baseline-git-status.txt), [baseline state](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/baseline-state.json), [inventory counts](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/baseline-inventory-counts.json), [file hashes](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/baseline-hashes.json).

Final preservation check: **2,723/2,725 existing inventoried files unchanged**, no missing files. Only two intended existing source files differ: `ImmersiveShell.tsx` and `LimestoneExcavationSession.ts`. In particular, all connected excavation GLBs/masters/UVs/manifests, original stage/crowd/video files, world registry, movement/travel bounds, map/camera code, lighting/fog, terrain, stalls and existing user-restored elements retain their original hashes. [Evidence](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/preservation-verification.json).

The preserved connected footprint remains approximately **97.8 × 123.5 m**, with its unchanged20-point registry polygon, 18 runtime geological partitions and existing28.61–38.67 m rim-height range. No support geometry tweak, remodelling, new rubble, collision registration or coordinate change was necessary.

## 2. Original look source and material changes

The supplied “STAGE 2A · ISOLATED DEVELOPMENT PREVIEW” corresponds to the retained original rock-pilot family:

- [Original runtime pilot](../public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb), SHA256 `82a48f71b714f48952e10e99aa2f1393fa3a6d2b6126d383318972c0478d2a6d`.
- [Original editable Blender source](../assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend).
- Authoring: `scripts/blender/rock_pilot_materials.py`, `rock_pilot_surface.py`, `author_rock_pilot_2a.py`. Their existing original project-generated maps are reused; no reference photograph pixels or new texture generation are used.
- Material: **`Quarry_Pilot_Original_Stone_PBR`**.
- Fresh actual-browser [reference capture](../reports/stage-2c4-rock-look-restore-2026-10-13/reference/original-stage2a-rock-pilot.png) and [reference metadata](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/reference-capture.json): original isolated bundle/asset, LOD0, medium view, FOV58°, 1280×843/DPR1.

The new [material-only GLB](../public/models/gullyverse/rock-look-restore/rock-pilot-material.glb) is **2,505,852 B**. Its material JSON, sampler settings and all three embedded image payloads are **byte-for-byte identical** to Stage2A. The tiny holder mesh is never rendered; no old panel geometry is copied into the quarry.

| Component | Restored source |
|---|---|
| Base colour | original `rock-basecolor-1024` JPEG, sRGB; darker neutral/brown mineral tone |
| Normal detail | original `rock-normal-1024` PNG, linear; normal strength0.7 |
| AO / roughness / metallic | original packed1024 PNG; roughness approximately0.76–0.99, metallic0 |
| Surface shader | original glTF/Three MeshStandard PBR, no added clearcoat, specular extension or postprocessing |
| Face policy | original double-sided setting retained |
| UVs / real-world scale | unchanged connected shell's safe painted-atlas UVs; nominal12×10 m pilot scale |

Grey limestone's paler map set and normal strength0.58 are replaced. **There is no global tint, exposure, fog, lighting or sky adjustment.** Original source maps/master files are not overwritten. The [extraction manifest](../public/models/gullyverse/rock-look-restore/manifest.json), [extraction evidence](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/material-extraction.json) and unit tests verify exact payload/PBR equality.

Both pilots use painted atlas bounds U0.02–0.88/V0.03–0.97. The existing connected UV reflection/safe-padding logic therefore transfers directly without stretching maps across the whole perimeter or sampling the old unpainted atlas strips. No new UV rewrite was needed. Existing medium/large-scale strata, fractures, grounded toe, tunnel opening and connected outer landmass remain geometrically identical.

## 3. Reversibility and active appearance

The connected setup keeps its existing opt-in/review activation: `/?arrival=hub&quarryReview=excavation`, development or a local build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`. That same URL now uses **original rock by default**. It applies consistently to every connected wall, all three LODs, rim, toe and surrounding terrain, under both approved Hub and Aftermovie lighting modes.

Historical comparison only: add `&quarryMaterial=limestone` to inspect the retained previous Grey family on the **same connected geometry**. The older Stage2C comparison/fallback and Stage2C.1 remain available; nothing is deleted. The existing ordinary `/` URL selection is unchanged and still uses the historical Stage2C rollout in this checkout. **This task restores the current connected review, without promoting a visual candidate to the production default or deploying it.** Thus “limestone no longer active” means the connected candidate's normal selection, not deletion of historical fallbacks. Removing the optional review returns to the unchanged previous default.

The legacy class/directory names containing `Limestone` are retained to avoid an unrelated architecture migration; they do not determine the active material. Runtime evidence confirms `Quarry_Pilot_Original_Stone_PBR` across all connected visual meshes, one shared material and three unique map resources. Normal connected requests load the rock holder and **do not request the Grey material holder or18.6 MB Stage2C comparison**. [Actual runtime/network verification](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/material-runtime-and-network.json).

## 4. Matched visual review

**24 before/after PNGs plus one fresh original pilot reference.** Desktop1366×900; portrait390×844. Eye-level, diagnostic close-up, public aerial map and stage-return views are labelled. All12 pairs match camera position/orientation/FOV, viewport, effective DPR, quality and selected LOD geometry exactly. Current scene exposure and lights remain unchanged.

| View | Grey limestone before | Original darker rock after |
|---|---|---|
| Desktop · 01 hub center | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-01-hub-center.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-01-hub-center.png) |
| Desktop · 02 stage facing | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-02-stage-facing.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-02-stage-facing.png) |
| Desktop · 03 left wall | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-03-left-wall.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-03-left-wall.png) |
| Desktop · 04 right wall | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-04-right-wall.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-04-right-wall.png) |
| Desktop · 05 close wall | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-05-close-wall.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-05-close-wall.png) |
| Desktop · 06 scaffold | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-06-scaffold.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-06-scaffold.png) |
| Desktop · 08 tunnel exit | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-08-tunnel-exit.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-08-tunnel-exit.png) |
| Desktop · 07 aerial map | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-07-aerial-map.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-07-aerial-map.png) |
| Desktop · 09 stage looking back | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/desktop-09-stage-looking-back.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/desktop-09-stage-looking-back.png) |
| Portrait · 01 hub center | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/mobile-01-hub-center.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/mobile-01-hub-center.png) |
| Portrait · 08 tunnel exit | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/mobile-08-tunnel-exit.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/mobile-08-tunnel-exit.png) |
| Portrait · 07 aerial map | [Before](../reports/stage-2c4-rock-look-restore-2026-10-13/before/mobile-07-aerial-map.png) | [After](../reports/stage-2c4-rock-look-restore-2026-10-13/after/mobile-07-aerial-map.png) |

[Before metadata](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/before-captures.json) · [after metadata](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/after-captures.json) · [pair validation](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/capture-pair-validation.json). PNGs retain original browser resolution. Portrait/touch views are emulation, not measurements on a physical iPhone.

The dark matte family visibly replaces the chalkier grey appearance. Its mineral grain, bedding and roughness follow the original pilot; the connected geological shell and rim remain intact. The identical material does not imply pixel-identical appearance to the isolated slab: larger surface normals, camera distance, fog and the unchanged current environment affect the rendered result. Some old authoring bands, reflected texture repetition and stylized fracture shapes remain. They are **not photorealistic**, and are intentionally left for the separately authorized realism phase. The unchanged stage-local floor and Hub/Aftermovie global-light differences are not redesigned to compensate for material darkness.

## 5. Exact source and asset changes

- `components/immersive/LimestoneExcavationSession.ts`: original rock is the default family; explicit Grey comparison uses the same owner/cache/loader, with material-family provenance added to existing traces. No new navigation state machine or geometry pipeline.
- `components/immersive/ImmersiveShell.tsx`: resolve the optional historical material comparison and label the existing review controls accurately. Public controls, routes and ordinary URL policy unchanged.
- New `scripts/blender/extract_original_rock_material.py`: deterministic lossless material extraction, **no Blender remodel or unrelated asset-generation script**.
- New `public/models/gullyverse/rock-look-restore/rock-pilot-material.glb` and `manifest.json`.
- New `tests/immersive/rock-look-restore.test.ts`: active/reversible family selection and original PBR/image-byte preservation.
- This report, gallery and evidence tooling. No package/lock/dependency changes; no admin/payment/form or original stage source changes.

[Patch against starting source](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/task-source-changes.patch). Reproduce extraction: `python scripts/blender/extract_original_rock_material.py`. Existing connected geometry masters and exports continue to be reused unchanged.

## 6. Build and browser verification

Typecheck `npx tsc --noEmit`: PASS. `npm run lint`: PASS with existing warnings, no warning-policy changes. `npm run build`: PASS. `npm run test:immersive`: **71 passed,0 failed**. Local production build used explicit review/inspection flags and an inert127.0.0.1 Supabase placeholder; no production data/credentials were used.

The actual Khronos glTF validator reports **zero errors and zero warnings** for the new material holder. Connected geometry was not edited; previous geometric coverage/collision/LOD validation remains applicable and its hashes are preserved, rather than falsely claiming a new geometry survey. [CLI commands/results](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/check-commands.json), [validator](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/glTF-validator.json).

| Browser workload | Result | Evidence |
|---|---|---|
| Original default-route browser checks | PASS | 8/8 actual-browser groups |
| Connected-quarry browser checks | PASS | 8/8 actual-browser groups |
| Context loss / load failures / fallback | PASS | 6/6 actual-browser groups |
| `default-regressions` | PASS | exit 0; 306.3 s |
| `connected-regressions` | PASS | exit 0; 318.0 s |
| `directional-travel` | PASS | exit 0; 59.4 s |
| `ten-toggle-cycles` | PASS | exit 0; 46.3 s |
| `context-and-fallback` | PASS | exit 0; 58.0 s |
| `ten-video-cycles` | PASS | exit 0; 169.8 s |
| `before-performance` | PASS | exit 0; 86.7 s |
| `after-performance` | PASS | exit 0; 88.6 s |
| `material-and-network` | PASS | exit 0; command duration not recorded |

[Browser command exits](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/browser-commands.json) · [default controls](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/default-regressions/results.json) · [connected controls](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/connected-regressions/results.json) · [directional travel](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/directional-travel.json) · [context/fallback](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/recovery.json).

The existing real-browser suites cover fresh intentional entry/tunnel pacing, editable focus/lost-keyup, map projection/resize, persistent Canvas, direct routes, NavbarHome, history, reduced motion, touch-emulated movement/map, physical directional Aftermovie travel, video/rapid-exit pose restoration, boundary Stay/Esc/hysteresis/return, actual WebGL loss/recovery, delayed/failing geometry/material, duplicate-map rejection and critical-stage native fallback. Synthetic blur/freeze is not native OS backgrounding proof. Test groups are reported from actual browser runs; unit tests are not substituted for unperformed browser interactions.

## 7. Performance, loading and resource ownership

Actual environment: Debian13/Linux6.18.44, Chromium151.0.7922.173, ANGLE/Vulkan SwiftShader **software rendering**; AMD EPYC9V74 host,2-vCPU quota,8 GiB limit. No physical GPU/iPhone/Android was accessible. Physical-device performance remains **pending**, not a blocker for this material correction. [Hardware profile](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/hardware.json); actual GL renderer/vendor are in the raw browser/performance snapshots.

The following are **identical connected geometry and same production build**, Grey family versus original rock. Matched1366×900, DPR0.5/Q3, unthrottled10-second windows, no competing authoring/recording/browser workload. Short software-renderer windows show run-to-run variance; they do not certify60 FPS or a physical-device performance change.

| Window | FPS before → after | p50 ms | p95 ms | p99 ms | Calls | Triangles |
|---|---:|---:|---:|---:|---:|---:|
| hub | 3.00 → 2.68 | 322.9 → 371.5 | 371.0 → 420.2 | 371.0 → 436.7 | 150 → 150 | 109,677 → 109,677 |
| left-wall | 2.36 → 2.55 | 419.0 → 392.2 | 464.5 → 454.0 | 470.4 → 460.8 | 30 → 30 | 100,549 → 100,549 |
| aerial-map | 2.78 → 2.87 | 372.8 → 372.4 | 404.7 → 390.9 | 407.6 → 393.6 | 171 → 171 | 113,899 → 113,899 |
| stage-looking-back | 1.99 → 2.34 | 491.1 → 418.6 | 570.0 → 486.2 | 570.0 → 487.5 | 65 → 65 | 1,037,043 → 1,037,043 |

[Before raw samples](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/before-performance.json) · [after samples](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/after-performance.json). Draw geometry remains the same; image content and original normal strength differ. Any measured frame-rate variation is reported, not hidden by altering lights/quality/world structure. GPU timer/driver-VRAM certainty is unavailable.

Cold local preparation/transfer: fresh CDP disk-cache-disabled contexts, DPR0.25/Q3, no network/CPU throttle; encoded bytes include response overhead, not an internet/device benchmark.

| Family | Total transfer recorded | Navigation to prepared local | Runtime material |
|---|---:|---:|---|
| rock | 8,396,373 B | 7,292 ms | Quarry_Pilot_Original_Stone_PBR |
| limestone | 8,005,251 B | 7,474 ms | Quarry_Pilot_Grey_Limestone_PBR |

Geometry detailed combined GLB remains **7,898,472 B**. Holder size changes **2,117,836 →2,505,852 B**, **+388,016 B**; connected geometry+material total is **10,404,324 B**. All three original maps remain1024²; estimated unique decoded RGBA8+mip payload remains **16 MiB**, not measured VRAM. No compression/loader upgrade or geometry optimization was attempted in a material rollback.

[Ten covered comparison-toggle cycles](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/lifecycle.json) check one visible LOD per partition, shared material uniqueness and settled Three/GL texture/geometry/program/buffer plateau after warm-up. All ten cycles settle at **31 Three textures /276 geometries /35 tracked GL textures /1,276 buffers /23 programs**: this includes the intentionally cached historical comparison family. Inactive geometry retirement decreases276→222 geometries and preserves maps still owned by the cache. [Ten actual playback/exit/restoration cycles](../reports/stage-2c4-rock-look-restore-2026-10-13/raw/video-with-wall.json) verify the original movie and settled **28 Three textures /32 tracked GL textures** on every exit; these are not ten full-length screenings. Fresh matched hub windows both contain28 textures and195 geometries. The shared material-holder mesh is never mounted, and no shared original-stage loader cache is cleared. Covered texture initialization, shader preparation and warm real draws continue through the existing machinery. No claim of driver-VRAM leak freedom follows solely from counters.

## 8. Remaining limitations and stop

1. Human visual review of the restored darker family is pending. This implementation intentionally makes no further colour/lighting/style invention.
2. The current connected macro shell plus three representative geology regions are retained; remainder detail, repeated material cues and final geology/contact work remain for later production.
3. Physical GPU/mobile performance, native tab-background timing and perceptual first-reveal smoothness on those devices remain pending.
4. Existing entrance/tunnel, hub people/stalls, stage environment and ordinary default selection are retained as inspected. No broader release/promotion or visual redesign is included.
5. **Photorealism is deliberately deferred.** No final quarry sculpting, new destinations, stage rebuild, new crowd/stall production, commit, push or deployment.

Recommendation: review these matched screenshots and approve/reject the material direction before authorizing the separately scoped realism work. Stop here.
