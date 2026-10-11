from pathlib import Path
import json,subprocess
root=Path.cwd();out=root/'reports/stage-1-final-2026-10-11';raw=out/'raw'
def read(name):return json.loads((raw/name).read_text())
def link(name,label=None):return f'[{label or name}](../reports/stage-1-final-2026-10-11/{name})'
camera=read('camera-final/results.json');gap=read('gap-browser.json');maps=read('map-timing.json');comparison=read('visual-comparison.json')
metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-of','json',str(out/'acceptance/journey/recordings/full-journey.webm')],text=True));(raw/'recording-metadata.json').write_text(json.dumps(metadata,indent=2))
rows=[]
for name,state,evidence in [
 ('Entrance composition','PARTIAL','Current approved entrance preserved; facade/rock/graffiti remain blockout art.'),
 ('Tunnel reveal','PASS','Bent occlusion and actual public journey retained; seven-second authored entrance verified.'),
 ('Navigation scaffold','PASS','Current geometry/sign arrangement/placement unchanged, approved directional zones verified; final art remains temporary.'),
 ('Quarry layout','PASS','Actual registry/geometry/stalls/ground anchors hash-identical; no resizing or stage repositioning.'),
 ('Quarry lighting direction','PASS','Current user-approved atmosphere preserved; historical dusk redesign deliberately not applied.'),
 ('Stage integration','PARTIAL','Original/restored stage environment preserved, including visible dark floor edge and mode-specific fog; visual blending requires review.'),
 ('Hub movement','PASS','Public WASD/arrows/drag/touch and five approved directional zones, including truthful unavailable Sponsors.'),
 ('Boundary menu','PASS','Eight public approaches, four chamfer segments, clamp, Stay/Esc, rearm, chosen return and history.'),
 ('Aerial map','PASS','Approved same-world aerial view, shared markers, finite projection, resize/portrait and saved-pose return.'),
 ('Input ownership','PASS','Real held-key/focus fixtures stop immediately; stale repeats/lost keyup/blur/freeze/map/movie/menu covered.'),
 ('Video-resource lifecycle','PASS','Ten completed playback/return cycles plateau at Three25 / tracked GL29; seven media/lifecycle groups pass. Driver VRAM not certified.'),
 ('Cinematic timing','PASS','Final event-to-hub timing and exceptional-gap cover verified; poor software FPS remains visibly coarse.'),
 ('Loading/resource preparation','PARTIAL','Delay/failure/interruption/context recovery safe in functional profile; native SwiftShader stage readiness fails45s budget.'),
 ('Desktop hardware performance','UNVERIFIED','No physical GPU/laptop available; cloud software results are not representative.'),
 ('Physical mobile performance','UNVERIFIED','Touch emulation only; no iPhone/Android hardware.'),
 ('Blender pipeline readiness','PARTIAL','4.3.2 editable source→validated GLB→existing loader/cache/raycast smoke passes; final collision/anchor extraction, LOD/decoders/budgets remain to validate.')]:
 rows.append(f'| {name} | **{state}** | {evidence} |')
maprows=[]
for w in maps.get('windows',[]):
 maprows.append(f"| {w['location']} | {w['name']} | {w['eventDurationMs']:.1f} | {w['averageFPS']:.2f} | {w['p50Ms']:.1f} | {w['p95Ms']:.1f} | {w['p99Ms']:.1f} | {w['maxMs']:.1f} | {w['stats']['calls']} | {w['stats']['triangles']} | {w['snapshot']['quality']} | {w['stats']['dpr']} |")
text=f'''
## Final verification results and required classifications

Full public navigation suite: **32 checks**, browser errors `[]`, attempted API mutations `[]`: {link('raw/navigation/browser-checks.json')}. It covers eight boundary approaches, four chamfer segments, all five hub directions (Aftermovie/Events/Team/Contact/Sponsors), direct URLs, history, original playback/unmute/Escape, read-only ordinary pages, portrait marker projection and touch menu navigation. Accommodation remains unavailable on the map; no hanging Accommodation sign was restored. The interrupted earlier run is retained separately in {link('raw/navigation-interrupted.log')} / {link('raw/verification-interruption.json')}; its incomplete log was not counted as a passing run.

After the foreground-gap guard was added, the final production bundle passed four relevant browser groups: fresh click/timing, map/resize/coordinates, playback/rapid restoration, touch entry/movement/map plus fresh reduced-motion Enter. Final activation→hub **{camera['checks'][0]['evidence']['timing']['activationToLocalMs']:.1f} ms**: {link('raw/camera-final/results.json')}. A controlled real 750 ms main-thread stall remains hidden under the actual DOM curtain and completes entrance in **{gap['activationMs']:.1f} ms**: {link('raw/gap-browser.json')}. The first gap test forgot to install its own diagnostic context and failed in the test helper; this fixture error remains in {link('raw/gap-browser-initial.json')}, and was corrected without an application change.

Separate public M/Esc timing runs: **{maps['status']}**, same Canvas and restored walking poses: {link('raw/map-timing.json')}. These windows are additional measurements, not a before/after hardware benchmark. A long first shader/frame interval can still make the software animation appear coarse or covered; endpoint accuracy does not imply perceptual smoothness.

| Location | Map mode | Event duration ms | Drawn FPS | p50 ms | p95 ms | p99 ms | Max ms | Calls | Triangles | Tier | DPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(maprows)}

Controlled delayed asset, aborted stage asset and actual context-loss recovery pass: {link('raw/edges-and-media.json')}. Actual hidden-tab behavior is **NOT TESTED**: Chromium headless kept `document.hidden=false` after another tab was activated; synthetic lifecycle and runtime-clock suspension are tested separately. Public return while crowd asset preparation is delayed and actual WebGL loss during playback both pass: {link('raw/interruption.json')}. Mid-synchronous-pose-bake cancellation was not separately browser-injected; ownership cleanup is unit-tested and inspected, not claimed as exhaustive hardware failure certification.

| Category | Classification | Evidence / scope |
| --- | --- | --- |
{chr(10).join(rows)}

## Actual recording and final gallery evidence

{link('acceptance/journey/recordings/full-journey.webm','Uninterrupted actual visitor recording')} — {float(metadata['format']['duration']):.2f} s, {int(metadata['format']['size']):,} bytes. It shows user-activated landing, tunnel, hub, local walk, physical directional Aftermovie travel, real video, Escape, boundary return and actual-world map selection. This is a browser screen recording, not a generated cinematic. Recording/screenshots are separate from timed profiling. Extra Stay/rearm/ordinary-route/history combinations are exercised in the browser suites. {link('acceptance/journey/traces/full-journey.zip','Playwright trace')} and {link('acceptance/journey/raw/browser-audit.json','journey results/poses')} retain the raw evidence. Its two console errors are the existing local Vercel telemetry script404s; no page runtime exception or API write occurred.

{link('gallery.html','Matched visual gallery')} contains 23 before/after pairs, all matching camera pose, viewport, quality and DPR. Actual image inspection reviewed entrance/scaffold/stage front/rear and portrait exit/aerial pairs; all23 were compared numerically. Larger stage-front/menu differences track existing animated light beams and capture time. No unexpected mesh, sign, terrain or exposure replacement was found within the captured views; low DPR limits fine material review. This is assistant verification, not final user visual approval.

Additional actual acceptance-only captures: {link('acceptance/stage-ground-detail.png','Preserved dark floor edge')} and {link('acceptance/shared-led-playback.png','Original segmented LED video playback')}, with {link('acceptance/additional-captures.json','camera/quality metadata')}. They have **no** matched before capture; the ground-detail pose deliberately looks down at the visible seam, rather than presenting the repeated stage-return view as proof that the seam is absent. All captures are actual browser images.

## Confirmed failures, open risks and production-art work

| Severity | Issue | Evidence / files | Recommended direction |
| --- | --- | --- | --- |
| High / available environment | Native DPR1 SwiftShader cannot finish stage preparation within45s; stage-local FPS window could not be obtained. The existing `npm run perf:immersive` desktop run also times out awaiting local Aftermovie after60s. | {link('raw/native-dpr1-profile.json')}; {link('raw/project-performance/failure.txt')}; {link('raw/project-perf.log')}; `rendering.tsx`, `ImmersiveShell.tsx`. | Retain graceful fallback; profile real integrated GPU/mobile before tuning budgets. No scene/lighting downgrade was used to hide this failure. |
| High / unverified acceptance | Physical laptop/mobile smoothness, thermal behavior, audible sound and actual mobile background recovery are not certified. | {link('raw/host.json')}; {link('PHYSICAL-DEVICE-PROCEDURE.md')}. | Execute the recorded hardware procedure before full environment production budgets are approved. |
| Medium | Post-GC JS heap increased14.43→15.28 MB despite stable GPU counters and DOM counts. | {link('raw/resource-results.json')}; opt-in diagnostics and shared caches. | Longer retained-heap profiling; distinguish bounded caches/JIT/diagnostics from true retained-resource growth. Do not infer no JS leak from stable textures. |
| Medium / locked visual decision | Dark stage-local floor has a visible boundary; hub/stage fog/lighting differ. These current restored elements are intentionally retained. | {link('acceptance/stage-ground-detail.png')}; `AftermovieEnvironment.tsx`, `HubScene.tsx`. | Explicit user review before any ground/lighting integration work. No silent historical-reference restoration. |
| Medium / asset pipeline | Compression/LOD/registry-export/collision extraction have not been validated with production assets or physical-device budgets. | [pipeline contract](gullyverse-environment-pipeline.md); smoke evidence above. | One separately approved small asset pilot; locally pinned decoders only after measurement. |
| Medium / temporary art | Procedural faceted rock, simple graffiti surfaces, placeholder hub capsules and stall blocks remain. | {link('gallery.html')}; `HubScene.tsx`, `blockoutGeometry.ts`, world registry. | Subsequent authorized Blender/material/population pass preserving current positions/atmosphere. |
| Low / pre-existing environment | Local Vercel telemetry JS404s and existing lint warnings remain. | {link('raw/after-loading-check.json')}; {link('raw/lint.log')}. | Verify deployment-specific telemetry routing separately; unrelated cleanup not included. |

Cold landing readiness did **not** improve in the single-run sample (5.594→5.861s), despite the measured83.69% transfer reduction. There is no claimed FPS gain: software frame tails remain poor. The benchmark log's word “draws” refers to rendered-frame count; actual WebGL draw calls are `stats.calls` in the tables/raw data. Native-resolution failure and successful low-DPR functional checks are both retained.

Blender smoke has12 successful mount/cache checks, one-metre bounds `[-.5,0,-.5]`→`[.5,1,.5]`, UVs, `Smoke_PBR`, visible raycast hit `[0,.5,.5]`, stable geometry UUID and one resident geometry. Khronos validation has0 errors/0 warnings/one unused-UV informational notice. The optional Draco-library warning did not prevent this **uncompressed** GLB export; no compressed-asset or automatic collision-registry readiness claim is made.

## Readiness answers and stop condition

1. **Persistent rendering stable?** Yes across tested immersive trips/map/video; ordinary pages intentionally unmount it. Physical-device stress acceptance remains open.
2. **Additional destinations without major redesign?** The registry/coordinator supports existing destination types; new destinations still need anchors, collision, readiness and budget validation. None were added.
3. **Camera transitions consistent?** Tested state/pose restoration and active-clock durations pass, including covered exceptional gaps. Smoothness on physical hardware is unverified.
4. **Scene loading reliable?** Controlled delay/failure/interruption/recovery paths pass at the functional profile; native software rendering hits fallback. No blanket readiness certification.
5. **Resource disposal correct?** Video and published/unpublished ownership paths are repaired and bounded in ten measured cycles. Driver VRAM and all long-session JS retention are unverified.
6. **Performance measured and acceptable?** Measured honestly on the available VM; software FPS is poor and native stage readiness fails. Representative physical hardware acceptance is open.
7. **Existing Aftermovie preserved?** All current source assets, layout/environment locks and LED shader/dimensions pass preservation hashes; actual stage and playback captures support this conclusion.
8. **Ready for photorealistic Blender pass?** A small isolated asset pilot is technically feasible. Full quarry production should wait for user composition approval, physical-device measurements and an approved aggregate budget/import contract.
9. **Fixes required before visual refinement?** Review this bounded runtime delivery, run the physical-device gate, validate anchor/collision export and compressed-material/LOD readiness with a small pilot; investigate retained heap/native fallback if real hardware reproduces them. No architectural rewrite is justified by the cloud FPS alone.
10. **Smallest next scope?** After explicit approval, one small authored rock/material segment in an isolated pilot, with metre/UV/PBR/LOD/export/loader/collision/ownership checks and real-device profiling. Preserve all approved world coordinates and stage assets.

**Stopped after Stage1 stabilization and verification.** No Stage2 production art, new destinations, quarry redesign, commit, push or deployment. Current approved configuration remains authoritative for future work. Full Stage2 authorization and final world-composition approval remain with the user.
'''
p=root/'docs/gullyverse-stage-1-final-acceptance.md';p.write_text(p.read_text()+text)
gallery=out/'gallery.html';h=gallery.read_text();h=h.replace('</html>','''<h2>Actual acceptance-only detail and playback</h2><p>No matched before capture exists for these two views.</p><div class="grid"><figure><img src="acceptance/stage-ground-detail.png"><figcaption>Preserved dark floor boundary; fixed review pose.</figcaption></figure><figure><img src="acceptance/shared-led-playback.png"><figcaption>Actual original shared three-panel movie playback.</figcaption></figure></div><p><a href="acceptance/journey/recordings/full-journey.webm">Actual uninterrupted journey recording</a> · <a href="acceptance/journey/traces/full-journey.zip">Browser trace</a> · <a href="acceptance/additional-captures.json">Extra camera metadata</a></p></html>''');gallery.write_text(h)
print('Final result supplement and recording/detail gallery links written.')
