from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'reports/stage-2c-quarry-rollout-2026-10-12';P=R/'raw'
def read(name):return json.loads((P/(name+'.json')).read_text())
before,after=read('before-performance'),read('after-performance')
inventory=read('asset-inventory');sizes={Path(x['path']).name:x['bytes']for x in inventory['files']}
network=read('network');n0,n1=network['runs']
resource=next(x for x in n1['resources']if x['name'].endswith('/quarry-limestone.glb'))
assert resource['decodedBodySize']==sizes['quarry-limestone.glb']
assert read('test-summary')['status']=='PASS'
assert read('loading-access-after')['status']=='PASS'
rows=[]
for a,b,label in zip(before['windows'],after['windows'],['Quarry center','Left wall','Right wall']):
 s0,s1=a['after']['stats'],b['after']['stats']
 rows.append(f"| {label} | {a['FPS']:.2f} → {b['FPS']:.2f} | {a['p50']:.1f} → {b['p50']:.1f} | {a['p95']:.1f} → {b['p95']:.1f} | {a['p99']:.1f} → {b['p99']:.1f} | {s0['calls']} → {s1['calls']} | {s0['triangles']:,} → {s1['triangles']:,} |")
trace=after['windows'][0]['after']['wall']['trace']
def event(name):return next(x for x in trace if x['event']==name)
geometryBefore=before['windows'][0]['after']['memory']['activeGeometryBytes']/1e6
geometryAfter=after['windows'][0]['after']['memory']['activeGeometryBytes']/1e6
heaps=[x['after']['memory']['jsHeapBytes']/1e6 for x in after['windows']]
coverage=read('perimeter-coverage');q=next(x for x in read('attribute-quantization')if x['file'].endswith('/quarry-limestone.glb'))
prefix='../reports/stage-2c-quarry-rollout-2026-10-12/'
report=f'''# Gullyverse Stage 2C — Full quarry rollout

2026-10-12 · Implemented locally; stop for user visual review. **No commit, push or deployment.**

## Approved baseline preserved

Branch `codex/navigation-board`, HEAD `e3dbbc233f1f12f5e4d96333db3b797e75da4760`, unchanged. The four initially dirty tracked files and relevant untracked pilot work were preserved. The user's approval of the corrected cool grey limestone pilot governs this rollout. [Exact starting state]({prefix}raw/starting-state.json), [recoverable scoped backup]({prefix}backup/current-approved-wall-baseline.tar.gz), [final hashes/status]({prefix}raw/final-preservation.json).

Of 119 protected files, 115 remain byte-identical; four existing integration files changed. Original stage/crowd GLBs, video and stage code, lighting/fog, ground, scaffold/signs, stalls, coordinates, movement bounds, camera/map and navigation systems are preserved. `rendering.tsx` retains its pre-existing user edits untouched. Payment/admin/routes were not edited. Walking-area extent remains 97.8 × 123.5 m; visible surrounding solids retain their larger 142.62 × 159.36 m combined bounds. Stage origin remains `[-12, 0, -134.3]`.

## Implementation

The 25 perimeter solids now use closed authored limestone geometry, replacing their procedural render surfaces. Independently seeded uneven rock units, interrupted fractures, localized scars and edge chips provide variation. Fracture depth scales to each host's size and remains bounded inward. Original corner anchors and enclosing bounds are retained. The approved pilot body and neighboring fitted contact skins are preserved.

Two fitted parts connect the quarry-facing tunnel collar and rear exterior crown. The collar follows the existing bend; section-local crown seams were stitched. Only 168 rear exterior vertices are replaced. All 10,080 enclosed-passage vertices, remaining entrance-facing shell, portal, paint and choreography remain unchanged.

A deeper trial exposed one ground-level sightline gap: radial carving lifted a low sloping face. An irregular terrain-contact band now retains the original foot, with its crease samples protected during LOD simplification. No ground or boundary change was needed. The final survey preserves all **{coverage['visitorHeightSourceHitRays']} horizontal source-blocked rays at every LOD**, with zero new gaps. [Coverage]({prefix}raw/perimeter-coverage.json), [superseded failure]({prefix}trials/deep-before-ground-contact/perimeter-coverage.json).

The approved material JSON, three embedded image byte hashes and eight original map files are unchanged. Fine-normal UV scale remains 12 × 10 m and normal strength approximately 0.58; new side UVs use the same limestone family. No global light/exposure adjustment was made. [Material lock]({prefix}raw/material-lock-validation.json).

## Assets, LODs and ownership

There are 27 independently selected parts, with whole-asset LOD totals **338,048 / 135,814 / 34,960 triangles**. Only one LOD per part draws. Selection uses projected size, viewport/FOV, drawing-buffer resolution, adaptive tier and hysteresis; meshes retain frustum culling. Existing movement/collision stays authoritative; the separate hidden 900-triangle reference proxy is not a replacement collision system.

The combined runtime GLB is **{sizes['quarry-limestone.glb']:,} bytes**, reduced from {q['beforeBytes']:,} using native loader-supported `KHR_mesh_quantization` for new normal/tangent/UV0 attributes. Positions, accepted pilot attributes and image bytes are unchanged. No new compression loader or dependency was added. Standalone review LOD exports are {sizes['quarry-lod0.glb']:,} / {sizes['quarry-lod1.glb']:,} / {sizes['quarry-lod2.glb']:,} bytes; only the combined asset downloads.

One visible limestone material and three shared maps serve the quarry: approximately **12 MiB decoded RGBA with mipmaps**, an estimate rather than driver VRAM. All three LODs remain resident and receive covered shader/texture warm preparation. This avoids first-use uploads at the cost of residency and initial transfer. Scene clones borrow the cache; owner retirement waits for consumers. No shared stage assets are evicted.

[Editable Blender master](../assets-source/gullyverse/quarry-rollout/quarry-limestone.blend) · [Runtime GLB](../public/models/gullyverse/quarry-rollout/quarry-limestone.glb) · [Reproducible workflow](../assets-source/gullyverse/quarry-rollout/README.md) · [Inventory]({prefix}raw/asset-inventory.json).

## Visual comparison

[Open the gallery]({prefix}gallery.html): **14 matched pairs / 28 browser PNGs**, covering exit, center, stage-facing, left/right walls, aerial map and stage looking back, at desktop 1366 × 900 and portrait 390 × 844. Every pair has identical camera/orientation/FOV, effective DPR and quality. [Before metadata]({prefix}raw/before-captures.json) · [After metadata]({prefix}raw/after-captures.json). Fixed inspection poses and public map/travel captures are identified; mobile views are emulation.

The perimeter now shares limestone coloration and fractured surfaces. Large inherited angular contours and light/shadow bands remain apparent, particularly from above and at the crown. Macro anchors/bounds are preserved; **{len(coverage['changedUpwardSkylineSamples'])} upward sampled sightlines changed** with local contour treatment, including **{len(coverage['LODHitDisagreements'])} LOD hit disagreement**. Those are published for review, not represented as pixel-identical silhouettes or universal seam perfection. Photorealism and full-rollout visual approval are not claimed.

The preparation cover also hid the existing native-fallback footer. It now draws above that cover while loading; normal ready-state composition is unchanged. [Before]({prefix}raw/loading-access-before.png) · [After]({prefix}raw/loading-access-after.png) · [Browser check]({prefix}raw/loading-access-after.json).

## Matched performance

Debian 13.6 VM, three AMD EPYC 9V74 vCPUs, Chromium 151.0.7922.173, **SwiftShader software rendering**. Fixed matched cameras, 1366 × 900, DPR 0.5, quality 3; ten-second sequential windows without competing capture/authoring load or artificial throttling. One paired run is diagnostic, not hardware certification.

| View | FPS before → after | p50 ms | p95 ms | p99 ms | Draw calls | Triangles |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Settled textures remain 28; geometries increase 152 → 222. Diagnostic geometry payload grows {geometryBefore:.2f} → {geometryAfter:.2f} MB; total texture estimate remains 57.61 MB. After-run heap snapshots span {min(heaps):.1f}–{max(heaps):.1f} MB, not a retained-heap leak proof. Maximum after frames are {', '.join(f"{x['max']:.0f}" for x in after['windows'])} ms respectively. [Raw before]({prefix}raw/before-performance.json) · [Raw after]({prefix}raw/after-performance.json) · [Hardware/method]({prefix}raw/hardware-profile.json).

One after-run recorded {event('load-ready')['ms']:.1f} ms load readiness, {event('parse-ready')['ms']:.1f} ms parse, {event('texture-init')['ms']:.1f} ms texture initialization, {event('shader-compile')['ms']:.1f} ms compilation and {event('covered-ready')['ms']:.1f} ms covered preparation. Cache-disabled localhost landing responses increase **{n0['CDPLocalEncodedBytes']/1e6:.2f} → {n1['CDPLocalEncodedBytes']/1e6:.2f} MB**, comparing single-pilot baseline with full rollout; landing readiness {n0['at']:.0f} → {n1['at']:.0f} ms. GPU shader caches may persist between contexts. [Network evidence]({prefix}raw/network.json).

**Physical integrated-GPU laptop, iPhone and Android acceptance is PENDING.** No sustained 60 FPS or leak-free VRAM claim is made. For local verification, repeat paired URLs at identical camera/FOV/DPR/tier, then separately test native adaptive settings; collect three 30-second windows plus map/travel/playback, network and GPU identity under comparable cache/thermal conditions.

## Verification and handoff

Type checking, lint with existing warnings, production build and **64 unit tests PASS**. All eight existing browser groups pass for the final geometry/runtime. The final temporary footer-stacking adjustment was additionally checked through actual delayed-loading captures and recovery tests. **Ten toggle cycles, ten map-mediated Hub ↔ Aftermovie round trips and ten playback/exit cycles PASS**, including toggles during playback. The persistent Canvas and settled resource counters plateau; explicit quarry-cache retirement returns cold reference counts. Actual context loss/restore, optional-load failure/retry, delayed-load abandonment and critical-stage fallback pass. [Commands/results]({prefix}raw/test-summary.json) · [Toggle lifecycle]({prefix}raw/lifecycle.json) · [Travel]({prefix}raw/navigation-cycles.json) · [Playback]({prefix}raw/video-with-wall.json) · [Recovery]({prefix}raw/recovery.json).

Five final GLBs validate with zero errors/warnings; proxy-only unused attributes are informational. Exported meshes are closed, consistently wound and positive-volume. Every rock LOD remains inside its source hull and retains its corners within 3e−5 m; 84 eye-height corridor samples per collar LOD remain clear. [glTF]({prefix}raw/glTF-validator.json) · [Topology]({prefix}raw/exported-topology-validation.json) · [Shape/corridor]({prefix}raw/shape-validation.json). Earlier authoring failures and superseded trials are retained, not presented as final passes.

Existing files changed: `AftermovieScene.tsx` dispatches the quarry component; `HubScene.tsx` swaps perimeter/exit/rear-shell geometry; `ImmersiveShell.tsx` handles default/reversal and covered preparation/access; `wallSection.ts` adds manifest guards and loading. New `QuarryPerimeter.tsx`, `quarryRollout.ts`, Blender authoring/quantization scripts, two regression cases, assets and evidence support this integration. [Exact patch against starting worktree]({prefix}raw/stage-2c-source.patch).

Reversal: **`?quarry=original`**, or build with **`NEXT_PUBLIC_GULLYVERSE_QUARRY_ROLLOUT=0`**. The earlier single-pilot preview remains available with its existing preview build flag. No new ordinary navigation controls were added.

Intentionally deferred: entrance/enclosed-tunnel art, graffiti, detailed stalls and hub people; approved ground and original stage surroundings/floor remain unchanged. Additional contour/seam/LOD refinement is subject to visual review. Device budgets and initial transfer/residency remain risks before deployment. No new destination or subsequent production phase was started. **Stop for user review.**
'''
(ROOT/'docs/gullyverse-stage-2c-full-quarry-rollout.md').write_text(report)
print('Final report written from measured evidence:',len(report.split()),'words.')
