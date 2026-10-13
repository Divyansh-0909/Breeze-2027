# Physical-device checks pending

No physical GPU/iPhone/Android was available in this cloud environment. This is
not a blocker for the user-authorized macro/three-area pilot. It remains a
requirement before performance certification or production-scale residency.

1. Use the same worktree and current asset hashes. Record OS, CPU, physical GPU,
   browser/version, viewport, device pixel ratio and power mode. Prioritize an
   integrated-GPU laptop, physical iPhone Safari and mainstream Android Chrome.
2. Run a local production build with `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1` and
   `NEXT_PUBLIC_GULLYVERSE_INSPECTION=1`. Keep your normal local configuration;
   do not copy credentials into results. Serve on the local LAN for phones.
3. Compare `/?arrival=hub&diagnostics` against
   `/?arrival=hub&diagnostics&quarryReview=excavation`. Reuse the same viewport,
   camera and recorded effective quality/DPR. Do not lower lighting or hide
   the original stage/crowd for the candidate. Capture a 30-second moving
   visitor window, then equivalent wall, stage and public aerial windows.
4. Export `window.__gullyverse.timeline`, `.memory`, `.stats`, `.preparations`
   and `window.__wallPreview.trace` through desktop DevTools, Safari remote
   Web Inspector on a Mac, or Android Chrome remote debugging. Record p50,
   p95/p99, mean FPS, >50/>100ms stalls, draw calls, triangles and long tasks.
5. Record cold-cache entry/readiness, first/return travel, playback focus and
   restoration, map ascent/descent, ten round trips and ten playback exits.
   Separate warm-up from settled textures/geometries/programs/buffers. Do not
   equate these proxies with measured driver VRAM.
6. Test native tab backgrounding, orientation/resize, sustained thermal behavior,
   sound, touch ownership, reduced motion, direct URLs and history. Browser
   viewport emulation is not physical-device GPU testing.
7. Target60 FPS where feasible and stable30 FPS on constrained supported
   hardware. Specifically investigate aerial rendering: the new PBR landmass
   slowed the matched SwiftShader overview despite fewer triangles/draws.
   Test and report a cause rather than extrapolating the software numbers.

Keep raw recordings/JSON and asset hashes; do not compare to an older laptop
benchmark unless hardware, view, effective DPR, tier and cache settings match.
