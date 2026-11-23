# M2P Performance recovery

The live site is the walkable gully (market lane, navigation board, cypher gate, plaza with Events, Team, Contact, Accommodation and the Aftermovie screen) on a persistent React Three Fiber canvas. The quarry, tunnel and entrance choreography were removed from the site earlier at the user's request (M2L), so they are not measured. Versions: Next.js 15.3.8, React 19.0.8, three.js 0.169.0, @react-three/fiber 9.6.1. The environment is the frozen Rev15Z export; the master `.blend` is untouched.

## Measuring

`npm run perf:breeze` (`scripts/perf-breeze.mjs`) drives a production build in Chromium and records:

- **Load:** cold (fresh browser context, empty HTTP cache) and warm (reload in the same context) visits to `/`, with:
  - transfer bytes by type (CDP `encodedDataLength`)
  - when walking unlocks and when the whole world has joined the scene
  - `breeze:*` load marks
  - failed requests and console errors
- **Poses:** each map stop (market, navigation board, plaza, Events, Team, Aftermovie), reached with the map's own travel. Each is sampled from its fixed arrival pose after the world is complete and a 5 s settle, with:
  - presentation intervals from `requestAnimationFrame`
  - CPU render-submit time
  - GPU timer samples where `EXT_disjoint_timer_query_webgl2` exists (disjoint results discarded)
  - renderer counters
  - scene memory estimates
- **Cycles:** repeated map round trips (market → Events → Team → Aftermovie → market), recording JS heap and renderer geometries, textures and programs after each cycle.
- **Journey:** walk (W), then sprint (Shift+W), from the market spawn.

The same instrumentation is opt-in on the site: `?diagnostics` exposes `window.__breezePerf`, and `?perf=overlay` shows a developer overlay with a JSON download. Ordinary visits install nothing. `?tier=<minimum|low|balanced|high>` pins a quality tier; benchmarks pin `balanced`, which is the previous fixed DPR of 1.

`node scripts/perf-asset-manifest.mjs` writes `perf/asset-manifest.json`. For every runtime asset it records:
- transfer size, decoded geometry, texture dimensions and an estimated GPU allocation
- which part of the walk uses it and when it loads
- whether it is shared or duplicated

**Limits of this environment.** The build machine has no GPU. Chromium renders WebGL with SwiftShader (software), at several seconds per frame. Its frame times, GPU timings and load times are therefore not device performance, and are reported only as SwiftShader numbers. Draw calls, triangles, programs, transfer bytes and load ordering do not depend on the renderer. Mobile figures use Chromium's Pixel 7 emulation (viewport, DPR, touch), not a phone GPU. No physical phones or GPUs were available, so the device acceptance gates below are **unverified**.

## What was found (baseline)

See the results section for the numbers. In order of impact:

1. **Everything loaded at once, before walking.** All six chunks were fetched in parallel and walking waited for all of them: about 100 MB of GLB on desktop and 50 MB on mobile.
2. **The film competed with the world.** The looping screen film (52 MB, 1080p) started streaming during the initial load. In the first baseline run, 172 MB had transferred before walking unlocked.
3. **Duplicated textures.** Two road textures (3.5 MB + 2.0 MB on desktop) and eight small shop packets were embedded separately in five chunks. That meant 22.4 MB of repeated download on desktop (5.8 MB on mobile), with up to five transcodes and GPU copies of each.
4. **Oversized reflection probes.** Seven 1024 × 512 HDR panoramas (9.4 MB) fed reflections that the matte roughness floor (0.75, metals 0.5) only samples blurred.
5. **Many small draws.** The market chunks had 595 primitives over 164 materials; the whole world drew about 912 calls.
6. **132 shader programs** were compiled before walking.
7. **The crowd is 572k of the world's 1.1 M triangles,** with no distance LOD in the export.
8. **One KTX2 transcoder per chunk:** six worker pools, and three.js warns about it.

## What changed

| Change | Files | Effect |
|---|---|---|
| Shared road textures move out of the chunk GLBs into content-named KTX2 files. A loader hook fetches, transcodes and uploads each once per visit, and every chunk gets a clone that shares the same GPU texture. | `scripts/gullyverse/share-textures.mjs`, `public/models/gullyverse/locked-rev15z-shared/`, `baked-assets.ts` | −22.4 MB desktop, −5.8 MB mobile; fewer transcodes and uploads. Pixels unchanged: the same source images in the same encoding, with identical samplers. |
| Progressive streaming. The arrival half loads first (lane: market south and north, navigation board, gate; plaza stops: gate, board, plaza, crowd). The rest streams after walking starts. Each late chunk's textures are uploaded and its shaders compiled against the scene's lighting before it joins, so there is no first-use compile hitch. With data saver or a 2G-class connection, it waits until the visitor heads that way. A failed late chunk no longer ends the visit. A chip shows "Loading the rest of the gully…". | `CypherGatePreview.tsx`, `chunk-order.ts` | Lane arrivals download about 39 MB before walking instead of about 128–172 MB. |
| The screen film starts only after the world has streamed. The loop plays a 720p copy (30 MB at 1.1 Mbit/s instead of 52 MB). **Watch Aftermovie** switches to the full 1080p film from the beginning. | `cypher-screen-film.ts`, `public/after-movie-720.mp4` | The film no longer competes with the world. The per-frame video upload is less than half the size. |
| Plain static market meshes that share a material are merged in the chunk's space. Lightmap UVs, materials and shaders are unchanged. Named, interactive, animated, transparent, decal, projected-art and lamp objects stay separate. | `static-batching.ts`, `baked-assets.ts` | Draw calls at the market arrival drop from 912 (whole world) to 435 (arrival half). |
| Reflection probes use the 512 × 256 panoramas everywhere. | `fidelity.ts` | −7 MB desktop; the PMREM cube drops from 256 to 128 px, beyond what roughness ≥ 0.5 samples. |
| One shared KTX2 transcoder (two workers) for all chunks. | `baked-assets.ts` | One worker pool instead of six. |
| Adaptive resolution tiers (minimum 0.65, low 0.8, balanced 1.0, high ≤ 1.5 DPR) with 3 s windows, a sustained-overload rule, an 8 s hold after each change and at most two upgrades. Walking frames only. Only resolution changes; content, lighting, movement and input do not. | `quality-governor.tsx` | Weak or thermally throttled devices step down instead of dropping frames; capable desktops can step up. |

## Not done, and why

- **Crowd LOD.** The master has LOD1 and LOD2 people, but the export carries only LOD0, and exporting the lower levels needs a crowd re-bake. Simplifying the exported crowd reaches only 572k → 210k triangles (UV seams), and quantising its lightmap UVs needs a visual review that software rendering cannot provide in time. This is the largest remaining GPU cost on phones.
- **Texture re-encoding.** UASTC roughness maps on the eight plaza houses could move to ETC1S, saving about 5 MB. Deferred until it can be reviewed on a GPU.
- **Long-lived caching.** Model files are served `max-age=0` with ETags, so repeat visits revalidate rather than re-download. Immutable caching would need versioned URLs, because chunk names are not content-hashed.

## Results

Filled in from `perf-results/` (baseline-*.json and candidate-*.json); see below.

## Status at hand-over (23 November 2026)

Work moves to a machine with a GPU. Everything is pushed; the last two changes are **untested in the browser**:

- `1a39ddb` market batches split into 10 m cells (unit-tested; not yet re-measured);
- `86421b7` the Rocketbox crowd (189 people, 15 avatars chosen by the user, `rocketbox-crowd.ts`). Unit-tested and built, but not yet viewed in the scene: check facing, scale, foot height and lighting first.

Raw results so far (SwiftShader, Chromium headless, 4 vCPU, no GPU; frame times are not device performance) are in `perf/results-2026-11-23-swiftshader/`: baseline = commit 66a7f69 (instrumentation only), candidate = 73cbe36 (before the 10 m cells and the Rocketbox crowd). Load numbers (desktop 1280 x 720, DPR 1, cold):

| | Baseline | Candidate |
|---|---|---|
| Transferred before walking | 127.9 MB | 38.6-38.9 MB |
| Walking unlocked (SwiftShader) | 198-205 s | 94-104 s |
| Draw calls, market arrival, whole world loaded | 912 | 711 |
| Shader programs | 132 | ~102 |
| Memory over 5 map round trips | flat (974 geometries, 131 textures) | flat (739 geometries, 113 textures) |

The navigation-board pose drew slightly more with whole-chunk batches (449 vs 433 calls); `1a39ddb` addresses it.

### Running the measurements on the GPU machine

```bash
npm run build
GULLYVERSE_RUNTIME_PREVIEW=1 npm start
BREEZE_BASE_URL=http://127.0.0.1:3000 CHROME_PATH="<path to Chrome>" npm run perf:breeze -- --label gpu-candidate
BREEZE_BASE_URL=http://127.0.0.1:3000 node scripts/perf-functional.mjs
```

For a baseline, check out 66a7f69 in a separate worktree, start it on another port, and run `perf:breeze` against it with the same settings. Use real Chrome (`CHROME_PATH`) so H.264 video and the GPU are used; record the GPU in the report. `?perf=overlay` shows live FPS, frame percentiles, draw calls and the quality tier on any device. `perf/results-2026-11-23-swiftshader/people-shots.mjs` captures fixed-camera before/after screenshots of the people (`SHOTS=crowd` for the crowd views).
