# Environment implementation acceptance — 8 October 2026

Historical preparation/performance baseline. The reference pack was subsequently supplied and inspected for [Stage 1 spatial acceptance](gullyverse-stage-1-spatial-acceptance.md). That report supersedes the missing-reference and temporary-layout status below; these measurements remain the before baseline.

The production environment is **not implemented or accepted**. The original graffiti-tunnel and daylight open-roof quarry reference images are unavailable in the supplied attachments and have not been located in the project assets. This revision advances loading diagnostics and recovery while keeping the existing temporary environment. It does not certify its geometry, materials, composition, sign framing, crowd density or artist graffiti against references.

## Reference and authoring gate

Both attachment directories (`45d795e1-3154-4722-9bfb-473964710b10` and `81a8a57e-fcc3-407b-9463-d3593a7d580f`) contain text briefs, not image references. Project assets were inventoried. Inspected images include the existing `public/image/hero-parallax.jpeg` night-stage photograph, the Ritviz and Chaar Diwaari poster artwork, representative concert-gallery photographs and the old illustrated landing artwork. They do not provide the required tunnel or daylight quarry authority.

Missing visual inputs:

- The original tunnel reference, including its proportions, surface treatment, exit alignment and artist graffiti.
- The original open-roof excavated-quarry reference, including rock morphology, daylight, stage distance, stalls and crowd layout.
- Any separate original entrance/exit/sign reference, if one was supplied outside those two images.

A question requesting the original local paths or image links was raised. No substitute reference has been invented. The existing Blender authoring script and environment pipeline document remain available; no working Blender executable or new editable `.blend` source was located/produced during this revision. Detailed asset production and runtime GLB/material replacement await the reference-matched blockout and visual comparison required by the brief. The original stage GLB and character assets are preserved.

## Implemented preparation and recovery

- Screenshot inspection found three temporary quarry masses intersecting the existing tunnel corridor. The hub now omits those masses to leave a physical opening; camera anchors and tunnel dimensions are unchanged. This corrects a clearance defect, not reference composition or realistic asset appearance. The Aftermovie boundary is unchanged.
- The immersive crowd retains all four original baked poses and their cache, geometry and distribution. Its covered preparation now yields between poses with a zero-delay task rather than four artificial 150 ms gaps. Standalone stage and recorder defaults are preserved. Departure/arrival pacing and the 7.2-second entrance are unchanged.
- Real destination draws wait until critical textures and shaders are prepared, avoiding synchronous shader creation from a partially mounted scene. The persistent R3F animation clock continues throughout. Hidden warm renders use the final viewing composition, followed by twelve measured frames after two upload frames; the previous four-frame window at the approach pose underestimated reveal cost and overreacted to transient initialization under CPU throttling. Recovery warms the saved pose. The existing density/DPR tiers are retained; this revision adds no lower tier or removed stage detail.
- Context loss keeps the existing Canvas and immediately covers it, clears input, invalidates old preparation, stops playback and retains the interrupted journey. Restoration repeats texture/shader/upload preparation before resuming the saved pose or choreography. URL changes during recovery queue through the same navigation model. Repeated loss during preparation keeps the original resume state. A 45-second preparation/restoration timeout offers the existing 2D fallback; the fallback reloads the current URL.
- Actual page freeze/resume listeners clear held keyboard and touch input, supplementing visibility, blur and focus handling.
- `?diagnostics` enables bounded frame/phase timelines, CPU render-submission and camera-update timings, asynchronous GPU render timers when supported, GLTF parse-to-ready intervals, individual crowd bakes, texture initialization, shader compilation, readiness-render windows and periodic JS/resource memory samples. Diagnostics do not publish frame updates to React or synchronously wait for GPU completion.

CPU render-submission time is not full main-thread work or GPU execution. The browser journey also records main-thread long tasks. GLTF parse-to-ready is elapsed time including asynchronous image decoding, not CPU-only decoding. Resource Timing records download/HTTP payload sizes; `decodedBodySize` means HTTP decompression, not decoded 3D geometry. GPU timers follow the [Khronos asynchronous timer-query specification](https://registry.khronos.org/webgl/extensions/EXT_disjoint_timer_query_webgl2/); unavailable capabilities and disjoint samples are reported explicitly.

WebGL does not expose driver VRAM allocation. Texture/geometry counts, deduplicated active geometry backing buffers and RGBA8/mipmap texture estimates are resource proxies, not measured GPU heap usage. They exclude driver overhead, hidden renderer allocations and inactive loader caches. JS heap measurements include raw CDP readings, readings after requested garbage collection, and a second collected reading after recording and clearing retained diagnostic samples across ten trips. This preserves natural GC fluctuations and makes intentionally retained observer data visible rather than calling it a scene leak. It does not disable instrumentation or erase the raw/first-collected evidence.

## Reproduce automated evidence

Build and start the production server in separate PowerShell terminals:

```powershell
npm.cmd run build
npx.cmd next start -p 3000
```

Then run:

```powershell
npm.cmd run test:immersive
npm.cmd run test:payments
npm.cmd run test:payments:browser
$env:GULLYVERSE_MODE = 'production'
$env:GULLYVERSE_ARTIFACT_DIR = '.gullyverse-artifacts/environment-preparation'
npm.cmd run perf:immersive
```

The profiler defaults to installed Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`; override `CHROME_PATH` if needed. Use `GULLYVERSE_BASE_URL` for another server. `GULLYVERSE_PROFILES=desktop,mobile-emulated` is the default. The second profile uses touch emulation and 4× CPU throttling on the desktop GPU; it is not physical mobile validation.

Artifacts remain local and ignored by Git. This revision uses `.gullyverse-artifacts/environment-preparation/`, preserving `.gullyverse-artifacts/results.json` and earlier screenshots. JSON contains phase p95/p99, long tasks, preparation events, HTTP timings, GPU capability, resource counts and memory trends. Tunnel/exit screenshots are explicitly current-blockout captures, not reference comparison evidence; their moving-camera photography journey runs separately from performance measurement to avoid screenshot readback stalls. Phase aggregates still include other test operations (playback, map, resize, simulated freeze); dedicated movement windows provide the steady-control comparison.

## Physical device acceptance procedure — still open

1. Serve the production build on the testing LAN. On each actual device, open `http://<test-machine-LAN-IP>:3000/?diagnostics`. Keep the laptop and device on the same network. Use remote debugging appropriate to that browser to extract `window.__gullyverse`, Performance recordings and network timings. Do not run desktop CPU throttling for a physical device profile.
2. Record exact device model, SoC/GPU, OS/browser versions, refresh rate, screen/DPR, battery/power state and ambient conditions. Test both cold browser/network cache and warm repeat navigation. Record the chosen quality tier and actual rendered resolution; resolution changes must be assessed alongside reference screenshots.
3. Run landing → entrance → hub walk/look → physical Aftermovie travel → playback/Escape → physical return → map travel → browser back/forward. Test direct `/aftermovie`, orientation changes, touch movement/look, reduced motion, fallback and failed asset loading.
4. Measure entrance, tunnel, hub, departure, covered loading, arrival, stage movement and return separately. Report average FPS, p95/p99 and frames over 16.67/34/50 ms; distinguish steady movement from preparation stalls. Measure for at least 10 minutes to expose thermal throttling and repeat ten round trips with resource/heap samples.
5. Switch to another app/tab while holding a movement control, then return. Verify no stale input or pose jump. Use `WEBGL_lose_context` when available to lose and restore the context during local movement, entrance, travel and playback; verify coverage, preparation and pose/history continuity. If unavailable, record that test as unverified, not passed. Confirm manual 2D access and timeout behavior when restoration cannot succeed.
6. After the actual reference images are available, compare entrance, tunnel, exit/sign, hub and stage screenshots against those originals at matched camera/FOV and aspect ratios. Correct composition before authoring final Blender geometry and PBR materials, then repeat performance and regression checks with the final production assets.

## Acceptance status

The final production-build browser run passed both profiles and all eleven edge-case checks. Chrome 155.0.8059.40 ran on Windows `10.0.26300`, Intel Core i5-8265U, with the actual renderer identifying Intel UHD Graphics 620 through ANGLE/D3D11. Installed drivers: Intel `26.20.100.7926`, NVIDIA MX130 `32.0.15.8183`. The MX130 was not the tested renderer. Desktop viewport was 1366×768 (then 1024×700); touch emulation used 390×844, device scale 2 and 4× CPU throttling (then 844×390), on the **same Intel GPU**.

| Dedicated movement window | Average FPS | p95 / p99 ms | Maximum ms | Draw calls / triangles | Textures / geometries | Tier / actual DPR |
| --- | ---: | --- | ---: | --- | --- | --- |
| Desktop hub | 59.64 | 17.0 / 17.6 | 24.2 | 60 / 11,348 | 8 / 82 | 0 / 1.0 |
| Desktop Aftermovie | 59.64 | 16.9 / 17.3 | 22.7 | 122 / 981,110 | 7 / 124 | 2 / 0.75 |
| Touch emulation hub | 59.64 | 17.6 / 18.2 | 19.5 | 26 / 10,618 | 8 / 60 | 1 / 1.0 |
| Touch emulation Aftermovie | 59.64 | 17.5 / 17.9 | 18.2 | 77 / 977,378 | 7 / 98 | 2 / 0.75 |

These short windows exclude preparation and test interaction overhead; they are not sustained physical-device certification. No movement window exceeded 50 ms in the final run. GPU timer support was available: 244 desktop and 245 emulated samples, 0 disjoint samples discarded. Full local-stage aggregates, including film focus/playback, resize and lifecycle probes, averaged only 57.28 / 56.08 FPS; roughly 872 / 805 ms gaps occurred around the CDP lifecycle probe, whose DOM visibility/freeze events were not observed. These gaps remain in the raw timeline. They are not removed to make the movement numbers attractive.

| Phase (complete journey aggregate) | Desktop FPS | Desktop p95 / p99 ms | Emulated FPS | Emulated p95 / p99 ms |
| --- | ---: | --- | ---: | --- |
| Entrance framing | 59.64 | 17.1 / 17.5 | 59.22 | 20.0 / 22.1 |
| Tunnel travel | 59.65 | 17.0 / 17.3 | 59.67 | 17.7 / 20.9 |
| Quarry exit | 58.84 | 17.1 / 17.3 | 59.57 | 18.0 / 20.4 |
| Hub departure | 59.63 | 17.2 / 17.9 | 58.56 | 20.5 / 52.6 |
| Aftermovie covered preparation | 51.65 | 41.1 / 78.6 | 30.76 | 113.1 / 310.9 |
| Aftermovie arrival | 59.63 | 17.0 / 17.2 | 59.19 | 21.9 / 38.4 |
| Aftermovie return departure | 59.63 | 17.6 / 30.5 | 56.72 | 21.6 / 69.9 |
| Hub covered preparation | 55.82 | 41.5 / 59.3 | 34.97 | 182.2 / 250.1 |
| Hub arrival | 59.65 | 17.0 / 17.1 | 59.66 | 17.9 / 22.4 |

Strict sustained 60 FPS / 16.67 ms acceptance **has not passed**. Several phase p95/p99 values exceed the budget, preparation has larger spikes, and only short movement windows have been measured. The production environment will need fresh profiles after its geometry/materials are integrated.

### Cold travel investigation

| Timing | Desktop ms | Touch emulation ms |
| --- | ---: | ---: |
| Initial landing preparation | 1,622 | 2,753 |
| Entrance observed by browser harness | 7,514 | 7,870 |
| Physical approach to threshold | 3,435 | 3,478 |
| Cold committed travel to local controls | 4,381 | 4,002 |
| Warm map travel | 1,497 | 1,798 |
| Warm direct `/aftermovie` | 1,986 | 3,508 |

These are one final run's wall-clock observations, not a statistical timing guarantee. The authored entrance remains 7.2 seconds and physical departure/arrival remain 1.05 / 1.15 seconds. The harness adds observation/interaction overhead.

The initial diagnostic revision (only removing crowd delays) measured cold travel at 4,437 / 4,395 ms. It exposed a 1,006.5 ms CPU render-submission stall during covered loading: the partially mounted stage drew before full shader preparation. Deferring that draw reduced an intermediate desktop cold trip to 3,418 ms, but the four-frame sample at the approach pose revealed a costly arrival (desktop p95 46.5 ms) and the throttled profile selected DPR 0.6 with a 5,023 ms trip. That intermediate configuration was not accepted.

The final configuration prepares the final viewing composition and samples twelve frames, retaining DPR 0.75 in both profiles. Desktop arrival p95 is now 17.0 ms. This adds necessary hidden preparation; **final desktop cold travel is still about 4.38 seconds**, close to the previous 4.50-second baseline. Emulated cold travel measured 4.00 seconds versus the previous report's 4.76 seconds, but that comparison is not a physical-mobile or multi-run claim. The removed 600 ms crowd pacing did not become a free overall latency reduction: the time was used for a more reliable reveal. Cold-latency acceptance remains open.

Final cold preparation evidence:

| Work | Desktop ms | Emulated ms |
| --- | --- | --- |
| Three GLTF parse-to-ready intervals | 7.6 / 8.4 / 10.6 | 50.6 / 59.6 / 61.9 |
| Four crowd pose bakes | 14.8 / 6.7 / 15.3 / 9.5 | 75.6 / 48.5 / 79.6 / 52.4 |
| Texture initialization | 45.7 | 149.4 |
| Shader preparation | 388.7 | 183.3 |
| Upload/warm/adaptive viewing window | 939.0 | 317.6 |

The three stage/character GLBs transfer about 554 KiB compressed in this local-server test and expand to about 2.29 MiB of HTTP body data. Download and decode-ready intervals are recorded individually in JSON; they overlap, so the table must not be summed as a total. Cold network cache here means fresh browser contexts, not a wiped OS/driver shader cache or a mobile network. Main-thread tasks during final covered-stage preparation peaked at 76 ms desktop / 309 ms emulated; scene submission no longer shows the earlier one-second first-draw stall. Steady movement CPU render submission averaged 1.23 / 2.03 ms (desktop hub/stage) and 5.19 / 7.36 ms (throttled hub/stage). Desktop stage arrival GPU rendering averaged 12.10 ms, p95 14.91 ms; the corresponding emulated values were 13.36 / 15.28 ms. Both CPU and GPU limits must be checked with the final art; low submission time alone is not proof of spare frame budget.

### Resource and JS memory evidence

Ten round trips retained **7 textures and 124 geometries** at the desktop stage. Active geometry backing buffers remained 1,727,328 bytes, and active texture estimates remained about 17.97 MiB. This passes the existing count-stability assertions and shows stable declared resource payloads, not measured driver VRAM.

Raw JS heap changed from 21.11 to 15.40 MiB as collection occurred. Post-GC heap rose from 12.35 to 13.19 MiB; after separately recording/clearing diagnostic samples and collecting again, it rose from 12.27 to 13.17 MiB. DOM node count was 311 / 311 in those collected snapshots. The roughly **0.90 MiB residual drift is unresolved**; this run does not prove a leak or prove long-term memory stability. A longer run and retained-object heap snapshots are still needed. Raw, collected, cleared-diagnostics heap, sample counts and resource values are preserved in `residency.json` / `edge-cases.json`.

### Regression and delivery decision

| Criterion | Result |
| --- | --- |
| Production build / TypeScript / targeted lint | Passed; existing unrelated lint/Browserslist warnings remain |
| Runtime tests | 12 passed, including four new recovery cases |
| Payment unit tests | 13 passed |
| Payment browser preview | Passed customer/admin/mobile flows; zero payment API mutations |
| Content smoke | Team, contact, existing Merch redirect and admin login returned 200; zero page errors or API mutations |
| Canvas/navigation/playback | Both browser profiles passed physical thresholds, map, history, direct entry, reduced motion, resize, touch controls and fallback |
| Shader readiness | First destination draw was verified to occur after shader preparation |
| WebGL recovery | Passed delayed initial preparation, hub local loss, stage playback loss, same Canvas/pose restoration and replay after recovery |
| Other recovery timing cases | Context loss during an in-flight `compileAsync` call and the no-restoration 45-second timeout have not been browser-verified |
| Failed critical asset | Passed covered failure with native video/information fallback |
| Ten-trip texture/geometry stability | Passed |
| Long-term JS/GPU memory acceptance | Open; JS drift observed; driver VRAM unavailable |
| Blur/focus and freeze/resume listener handling | Passed synthetic listener regressions and delta-clamp unit checks |
| Actual tab visibility / freeze events | Unverified; headless Chrome did not expose them, even with Playwright focus emulation disabled and a separate minimized-window probe |
| Reference-matched blockout and comparison | Blocked by missing original tunnel/quarry images |
| Realistic production assets and editable Blender sources | Not delivered; awaiting the visual gate |
| Physical mobile / sustained thermal performance | Unverified; no suitable physical-device session was available |
| Website/environment final acceptance | Not accepted |

The current hub screenshot still shows faceted primitive walls, uniform ground, proxy crowd/stalls and a large sign assembly. Those features are temporary and have not been visually approved. The existing stage remains recognizable and functional, but neither scene is evidence of a reference-matched production quarry.

Evidence files in `.gullyverse-artifacts/environment-preparation/`: `results.json`, both `*-diagnostics.json`, `edge-cases.json`, `residency.json`, `content-smoke.json`, and desktop/emulated landing, tunnel-blockout, exit-blockout, hub and stage screenshots. `before-render-gate-results.json`, `before-final-view-warm-results.json` and `before-tunnel-clearance-results.json` retain intermediate experiments; final results replace only this revision's `results.json`, not the original vertical-slice baseline. The successful run removed its stale `failure.txt` marker.

Current blockout captures (original-reference comparison remains pending):

| View | Desktop | Touch viewport |
| --- | --- | --- |
| Entrance | [capture](../.gullyverse-artifacts/environment-preparation/desktop-landing.png) | [capture](../.gullyverse-artifacts/environment-preparation/mobile-emulated-landing.png) |
| Tunnel | [capture](../.gullyverse-artifacts/environment-preparation/desktop-tunnel-blockout.png) | [capture](../.gullyverse-artifacts/environment-preparation/mobile-emulated-tunnel-blockout.png) |
| Exit / sign | [capture](../.gullyverse-artifacts/environment-preparation/desktop-exit-blockout.png) | [capture](../.gullyverse-artifacts/environment-preparation/mobile-emulated-exit-blockout.png) |
| Hub | [capture](../.gullyverse-artifacts/environment-preparation/desktop-hub.png) | [capture](../.gullyverse-artifacts/environment-preparation/mobile-emulated-hub.png) |
| Stage | [capture](../.gullyverse-artifacts/environment-preparation/desktop-aftermovie.png) | [capture](../.gullyverse-artifacts/environment-preparation/mobile-emulated-aftermovie.png) |
