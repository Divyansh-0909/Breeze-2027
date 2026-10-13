# Physical device acceptance — pending

No physical GPU, iPhone or Android was available in this VM. Do not use the SwiftShader FPS as hardware acceptance.

On the integrated-GPU laptop, build this branch with the existing project environment configured, `NEXT_PUBLIC_GULLYVERSE_WALL_PREVIEW=1`, and `npm run start -- --hostname 0.0.0.0`. Use a visible Chrome window, mains power, no CPU/network throttling and fixed browser zoom. Record OS, exact CPU/GPU, Chrome version and actual unmasked WebGL renderer. Confirm hardware rendering before comparing.

Compare `/?arrival=hub&diagnostics` with `/?arrival=hub&diagnostics&quarryReview=geology`, using the poses in `before-captures.json` / `after-captures.json`. For each collect three 30-second Hub/left-wall/Stage windows at the SAME viewport, effective DPR and quality. Separately test native adaptive quality, aerial ascent/descent, entrance, directional Aftermovie travel, first/repeat playback and restoration. Record p50/p95/p99/max frame time, draw calls, triangles, heap snapshots, textures/geometries and GL resource counters after ten round trips/toggles. Reset HTTP cache for cold loading, then repeat warm. Note browser/GPU shader-cache persistence and thermal state.

On Windows PowerShell, the evidence scripts can use the installed Chrome:

```powershell
$env:CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$env:GULLYVERSE_HEADED = '1'
$env:GULLYVERSE_ARTIFACT_ROOT = 'reports/stage-2c1-local-intel'
New-Item -ItemType Directory -Force reports/stage-2c1-local-intel/raw
node reports/stage-2c1-geological-refinement-2026-10-13/scripts/measure.mjs before
node reports/stage-2c1-geological-refinement-2026-10-13/scripts/measure.mjs after
```

These short ten-second script windows are a smoke check; extend collection for physical acceptance. Do not replace the archived cloud results when recording local runs: use a separate device report/output directory.

For physical iPhone/Android, open the laptop's LAN address on the phone and use Safari Web Inspector / Chrome remote debugging. Record device model, SoC, OS/browser, viewport, effective DPR/tier, actual renderer and battery/thermal state. Repeat the same routes and ten resource cycles. Collect frame timing via the existing `window.__gullyverse` diagnostics. Device emulation is not this test. A sustained 60 FPS claim requires those measured physical results; lower-end 30 FPS acceptance also remains open.
