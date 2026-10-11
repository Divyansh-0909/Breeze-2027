from pathlib import Path
import json,re
r=Path('reports/verification-2026-10-10')
def read(name,default=None):
 p=r/name
 return json.loads(p.read_text()) if p.exists() else default

def table(headers,rows):
 def clean(v):return str(v).replace('|','/').replace('\n',' ')
 return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(clean(v)for v in row)+' |'for row in rows])
def fmt(v,n=1):return '—'if v is None else f'{v:,.{n}f}'

# Replace labelled blocks so reruns preserve prose and recompute measured tables.
p=r/'REPORT.md';s=p.read_text()
def block(name,body):
 global s
 begin=f'<!-- {name} -->';end=f'<!-- END_{name} -->'
 if end in s:s=re.sub(re.escape(begin)+r'.*?'+re.escape(end),lambda _:begin+'\n\n'+body+'\n\n'+end,s,flags=re.S)
 else:s=s.replace(begin,begin+'\n\n'+body+'\n\n'+end)

browser=read('raw/browser-audit.json',{});nav=read('raw/navigation-details.json',{});edges=read('raw/edges-and-media.json',{});media=read('raw/media-cycles.json',{})
rows=[
['Landing → automatic intro','Automatic tunnel without further activation','FAIL','Landing remains until Enter/click/tap; automatic cinematic follows activation','[browser checks](raw/browser-audit.json), [entrance](screenshots/01-desktop-entrance.png)','ImmersiveShell landing / runtime.enter','Literal automatic-entry criterion not met'],
['Tunnel interior → reveal','Continuous first-person trip into open quarry','PASS','Observed bent traversal, last tunnel section and sky reveal','[02](screenshots/02-desktop-tunnel-interior.png), [03](screenshots/03-desktop-tunnel-before-reveal.png), [04](screenshots/04-desktop-quarry-reveal.png), [video](recordings/full-journey.webm)','runtime.tick; tunnelGeometry','Pacing slows with low FPS'],
['Hub arrival / direction board','High hanging signs and open hub','PASS','Current Gullyverse-only board, diagonal directions and lower Aftermovie↓ observed','[05](screenshots/05-desktop-hub-arrival-board.png)','HubScene.Scaffold','Temporary environment assets'],
['Local hub keyboard movement','WASD/arrows walk; drag looks','PASS','Actual pose displacement in uninterrupted journey and clean movement run','[07](screenshots/07-desktop-hub-movement.png), [browser](raw/browser-audit.json)','useImmersiveInput; runtime.tick','Not physical-device acceptance'],
['Aftermovie direction → travel','Cross route threshold; covered travel; correct arrival','PASS','Public physical route completed; same Canvas and /aftermovie','[journey](raw/browser-audit.json), [clean window](raw/performance.json)','boundaryCrossings / requestDestination','Aftermovie sector is behind spawn, consistent with downward sign; first crowd prep is slow'],
['Aftermovie arrival / viewing','Original stage and playback accessible','PASS','Stage/screens/crowd present; movie time advances and LEDs show movie','[08](screenshots/08-desktop-aftermovie-arrival.png), [09](screenshots/09-desktop-aftermovie-viewing-area.png), [11](screenshots/11-desktop-aftermovie-playback.png)','AftermovieScene; useStageVideo','Density adapts; sound hardware/quality-0 pyro not tested'],
['Bounded Aftermovie movement','Outer edges clamp and show menu; Stay/Escape keeps pose','PARTIAL','Recorded journey edge passed; additional full-perimeter results below are authoritative','[12](screenshots/12-desktop-boundary-menu.png), [edge tests](raw/navigation-details.json)','constrain / dismissDestinationMenu','Assess all eight separately'],
['Aftermovie → hub','Boundary menu returns to local hub','PASS','Return to Hub completed in recording and clean benchmark','[video](recordings/full-journey.webm), [performance](raw/performance.json)','runtime.requestDestination','Same logical coordinator, no entire scene unload'],
['2D map → Aftermovie','Map provides correct destination','PARTIAL','Full-screen 3D aerial map navigates correctly; literal 2D map absent','[10](screenshots/10-desktop-aerial-map.png), [journey](raw/browser-audit.json)','AerialMap; MapMarkerProjection','Later reference pack requests aerial view; projection console errors during a transition'],
['Direct /aftermovie','Bypass landing/tunnel','PASS','Observed phases omit landing/entrance','[direct URL check](raw/browser-audit.json)','locationFromPath / constructor','Only two immersive URL IDs'],
['Standard navbar navigation','Home bypasses intro','FAIL','From Contact, Home returns landing/Enter','[navbar check](raw/browser-audit.json)','Navbar.handleHomeClick; ClientLayout','Previously observed gap persists'],
['Immersive header return','Breeze header returns hub without intro','PARTIAL','Media-cycle check uses the real header; final repeated-media result below qualifies it','[media cycles](raw/media-cycles.json)','ImmersiveShell header runtime.request','Separate from ordinary navbar'],
['Browser Back/Forward','Correct location; renderer retained','PASS','Observed local destination and same Canvas both ways','[history check](raw/browser-audit.json)','native history / popstate / request','No full-tab reload persistence claim'],
['Already focused editable input','New movement key has no effect','PASS','Injected focused input; before/after pose unchanged','[focus fixture](raw/browser-audit.json)','input.ts down target guard','Fixture in DOM, not a production form'],
['Held movement → editable focus','Immediately release prior held movement','FAIL','x moved about 1.47 m while injected textarea had focus','[held-focus failure](raw/browser-audit.json)','input.ts lacks focusin clearing','Input keydown filtering does not clear stored key state'],
['Control handoffs / repeat travel','Release during modal/travel/movie; usable on arrival','PARTIAL','Full journey, repeated maps/history and resize work; focus exception remains','[browser](raw/browser-audit.json), [navigation detail](raw/navigation-details.json)','ownership subscription; runtime.clearInput','Use separate movie restore/cycle assertions below'],
['Reduced motion','Skip long tunnel; reduced motion flag respected','PASS','Observed hub in 968 ms after entry under reduce preference','[reduced-motion check](raw/browser-audit.json)','input media query / runtime.tick','No physical vestibular/user study'],
['Mobile entry / available touch','Tap entry, touch movement/look, map and movie','PASS','390×844 browser emulation completed; actual touch event pose changes; movie advances','[mobile captures](screenshots/mobile-03-hub.png), [touch check](raw/browser-audit.json)','touch pad / pointer drag','Browser emulation only; no real mobile GPU/FPS certification'],
['Resize / orientation','Runtime and controls survive size change','PASS','Same Canvas, movement after 1024×700; 844×390 touch-emulated stage capture','[resize check](raw/browser-audit.json), [landscape](screenshots/mobile-07-landscape.png)','FrameController / composeCamera','One Chromium viewport sample'],
['Synthetic blur/focus','Release held axes and resume','PASS','Dispatched blur/focus; pose held stable','[synthetic evidence](raw/browser-audit.json)','input blur/focus','Not an actual backgrounded OS tab'],
]
for source,data in [('raw/edges-and-media.json',edges),('raw/navigation-details.json',nav),('raw/media-cycles.json',media),('raw/playback-restoration.json',read('raw/playback-restoration.json',{}))]:
 for c in data.get('checks',[]):
  if source=='raw/edges-and-media.json' and 'Four repeated playback' in c['name']:continue  # Dedicated refined raw sample appears separately.
  ev=c.get('evidence',{});detail=c.get('error','').split('\n')[0]if c.get('error')else ('document.hidden remained false; true visibility change unavailable'if c['status']=='NOT TESTED'else 'Observed assertion completed; raw state/pose/resource evidence linked')
  name=c['name'];expected='Scenario named in row';code='ImmersiveRuntime / FrameController'
  if 'outer edge' in name:expected='Clamp inside polygon, open menu, Escape preserves pose';code='navigation.constrain; runtime.dismissDestinationMenu'
  elif 'Delayed crowd' in name:expected='Opaque curtain until Crowd and render preparation ready';code='AftermovieScene / ReadinessGate'
  elif 'Failed stage' in name or 'Use without' in name:expected='No Canvas; native controlled video and content links';code='ImmersiveShell.SceneBoundary / Fallback'
  elif 'Context loss' in name:expected='Recover same Canvas and saved walking pose under cover';code='runtime.loseContext / restoreContext; FrameController'
  elif 'background' in name:expected='Real hidden tab clears held input; foreground recovers';code='input.visibility / blur / focus'
  elif 'cycles' in name:expected='Playback and return function; textures/geometries/programs bounded';code='useStageVideo.stopMovie; LEDScreens sampler reset'
  elif 'Map close' in name:expected='Saved pose restored; unavailable options disabled';code='runtime.setMap; AerialMap'
  elif 'restores' in name:expected='Saved activation pose restored, then fresh walking works';code='runtime.setMovie / tick; useStageVideo'
  elif 'Higher-resolution' in name:expected='Actual desktop stills at native DPR1, including stage';code='ReadinessGate / quality policy / Shell45s timeout'
  if c['status']=='PASS':
   if 'Delayed crowd' in name:detail='A 3 s delayed GLB kept boot covered (opacity 1); then reached local Aftermovie'
   elif 'Failed stage' in name or 'Use without' in name:detail='Observed Canvas count 0, native controlled video and festival links'
   elif 'Context loss' in name:detail='WEBGL_lose_context restored the same Canvas and exact saved walking pose; recovery curtain observed'
   elif 'outer edge' in name:detail='Outward walking clamped at this face and opened menu; Escape preserved the boundary pose'
   elif 'Map close' in name:detail='Map close restored exact saved pose; Sponsors and Accommodation buttons remained disabled'
   elif name.startswith('Movie restores'):detail='Actual activation-event pose restored; held movement rejected during playback and fresh walking worked afterward'
  if 'cycles' in name and c['status']=='FAIL':detail='Four functional play/return visits completed; settled Three textures increased 25→28 (GL allocation counter 29→32)'
  if 'outer edge 3' in name and c['status']=='FAIL':detail+='; strict x equality differs by approximately 1e-15 m; clamp/menu assertions already passed'
  if name.startswith('Playback eventually')and c['status']=='FAIL':detail+='; target was read before clicking while inertia remained. Fresh activation-event probes pass and reproduce a 7 cm read→activation shift'
  rows.append([name,expected,c['status'],detail,f'[raw check]({source})',code,('Retained failure; see qualification below; no production fix' if c['status']=='FAIL' else 'Only the named Chromium/profile scenario was tested')])
block('ACCEPTANCE_MATRIX',table(['Step / requirement','Expected','Status','Actual observation','Evidence','Relevant code','Outstanding problem / scope'],rows))

perf=read('raw/performance.json',{});native=read('raw/native-dpr1-profile.json',{})
perfrows=[]
for w in perf.get('windows',[]):
 stat=w.get('stats',{});mem=w.get('memory')or{}
 perfrows.append([w['name'],fmt(w['elapsedMs']/1000,2),fmt(w.get('renderedFPS'),2),fmt(w.get('medianMs')),fmt(w.get('p95Ms')),fmt(w.get('p99Ms')),fmt(w.get('maxMs')),f"{w.get('stallsOver50ms',0)} / {w.get('stallsOver100ms',0)}",f"{stat.get('calls','—')} / {stat.get('triangles','—')}",f"{stat.get('textures','—')} / {stat.get('geometries','—')}",f"{w.get('snapshot',{}).get('quality','—')} / {stat.get('dpr','—')}",fmt(mem.get('jsHeapBytes',0)/1048576)if mem else '—'])
body='''Environment: **Chromium 151.0.7922.173, Debian 13.6/Linux x86-64**, AMD EPYC 9V74 VM (3 exposed vCPUs, cgroup quota **2 CPU cores**, 8 GiB memory cap), ANGLE Vulkan **SwiftShader** software renderer. No `/dev/dri` hardware GPU. This is a cloud VM/software-renderer device class, not representative desktop/iGPU or physical mobile. [Host facts](raw/host-capabilities.json).

Clean journey profile: **1366×900 CSS, requested/actual DPR 0.25** (about 342×225 rendering pixels). Default adaptive graphics policy unchanged: quality 0/1/2/3 caps DPR 1.25/1/.75/.6 and crowd 900/600/300; the browser DPR 0.25 remains below all caps. Antialias off, existing high-performance preference, no CPU throttling. Raw snapshots record exact tier/DPR per window. A separate native-DPR1 profile is below. Touch captures use emulation, not mobile performance measurements.

Method: [performance.mjs](scripts/performance.mjs), [raw frames/network/preparation/memory](raw/performance.json), [log](raw/performance.log). One graphics benchmark at a time, production server, no recording/screenshots during timed windows; DOM/diagnostics read after each sample. Diagnostics instrument `gl.render` and record actual R3F deltas; **finite cpuRenderMs** distinguishes drawn frames from loading-only animation ticks. Average FPS below is actual draw count / total measured wall time, including covered work; render-cadence FPS is also retained in raw data. Median/p95/p99 refer to sorted drawn-frame deltas, not CPU submission time or necessarily unique displayed frames. Transition windows include control/navigation/covered preparation (and map ascent where used); physical route window also includes walking to the nearby threshold. Tunnel/reveal rows are subsets of the same entry sample. Short-window p99 may equal the maximum; raw sample counts permit independent interpretation. Screenshot/video contexts are separate.

'''+table(['Scenario','Wall s','Avg draws/s','Median ms','p95 ms','p99 ms','Max ms','Stalls >50 / >100 ms','Last calls / triangles','Textures / geometries','Quality / DPR','Sampled JS heap MiB'],perfrows)
loadrows=[]
for w in perf.get('windows',[])[:2]:
 resources=w.get('resources',[]);loadrows.append([w['name'],fmt(w['elapsedMs']),sum(v['transferSize']for v in resources),sum(v['encodedBodySize']for v in resources),sum(v['transferSize']==0 for v in resources),'; '.join(f"{v['name']} {v['ms']:.1f} ms" for v in w.get('preparation',[]))])
body+='\n\n'+table(['Load','Landing ready ms','Resource transfer bytes','Encoded body bytes (cache included)','Zero-transfer entries','Preparation wall times'],loadrows)
body+='''

These transfer sums are browser Resource Timing entries available at landing readiness, excluding the HTML navigation entry and any opaque/unrecorded external transfer. Cold means a fresh browser context/local client cache, **not a cold OS filesystem/CDN/server process**. Warm means same-browser HTTP cache enabled (CDP guards only API writes); cache flags and zero-transfer entries verify reuse. The earlier general browser-audit script uses Playwright routing, which disables HTTP cache; its “cold/warm” labels are **not** used as valid cache benchmarks here. Cached bytes remain encodedBodySize even with zero transfer. The largest cold landing transfer is a **4,586,644-byte `/404-image.png` preload** (about 84% of the measured resource transfer total), despite a successful landing route. `components/notFound.tsx` uses a priority image; whether Next fallback/preload hoisting is the exact trigger needs confirmation. It is not a visible immersive-scene asset. This pre-existing asset/preload path merits review, without changing it during this audit. Asset durations, navigation timing, GLTF parse-to-ready, init/compile/warm windows, movie Range and full network entries are in the raw files. Parse-to-ready includes asynchronous decode and is not CPU-only parsing time.

Selected actual compressed local GLB fetches: stage 30,904 transfer bytes / 31.4 ms; Man 174,553 / 51.6 ms; Woman 362,402 / 40.9 ms. These differ from uncompressed file lengths and are measured on localhost, not representative WAN. [Movie metadata](raw/movie-metadata.json) records 52,291,090 file bytes, 197.376 s, H.264 1920×1080 at 24 fps plus AAC. [Trace network evidence](raw/movie-range-from-trace.json) confirms `Range: bytes=0-` and HTTP206; streamed body size is unavailable (`-1`), so full movie transferred bytes are not claimed.\n\nGPU timer extension is unavailable on this renderer: GPU frame duration and reliable VRAM are **not measurable**. CPU render submission and main-thread long tasks are recorded; they are not GPU time. The source-derived geometry and texture payload estimates are discussed below. Stalls remain recurring through repeat transitions; they are not hidden by a high average. Current shader compilation is performed covered, but no “no visible compilation hitch” target is certified on real hardware.
'''
if native:
 nr=[]
 for w in native.get('windows',[]):
  nr.append([w['name'],fmt(w.get('renderedFPS'),2),fmt(w.get('medianMs')),fmt(w.get('p95Ms')),fmt(w.get('p99Ms')),fmt(w.get('maxMs')),w.get('stats',{}).get('dpr','—'),w.get('snapshot',{}).get('quality','—'),w.get('stats',{}).get('calls','—'),w.get('stats',{}).get('triangles','—')])
 body+='\n\nNative **1366×900 / requested DPR1**: [raw](raw/native-dpr1-profile.json), [script](scripts/native-profile.mjs), [log](raw/native-profile.log). Entry deliberately sampled for 20 s; it is a partial window, not a completed native journey. Adaptive tier/DPR remain visible.\n\n'+table(['Window','Avg draws/s','Median ms','p95 ms','p99 ms','Max ms','Actual DPR','Quality','Calls','Triangles'],nr)
 if native.get('error'):body+='\n\nNative profile error: `'+native['error'].split('\n')[0]+'`. Later unreached windows are NOT TESTED; retained samples are valid partial measurements.'
comparison=read('raw/reference-comparison.json',[])
if comparison:
 cr=[]
 for version in comparison:
  for w in version.get('windows',[]):cr.append([version['label'],w['name'],fmt(w['renderedFPS'],2),fmt(w['medianMs']),fmt(w['p95Ms']),fmt(w['p99Ms']),w['stats'].get('calls'),w['stats'].get('triangles'),w['snapshot'].get('quality'),w['stats'].get('dpr')])
 body+='\n\nSame-VM before/after: WIP `fe51c10` built in an isolated archive, versus audited working tree; sequential fresh contexts, **1366×900 / DPR.25**, same relative stage spawn and FOV58, idle and same public strafe input. [Raw comparison](raw/reference-comparison.json), [script](scripts/reference-compare.mjs), [baseline build](raw/reference-build.log). This compares stage-local rendering only; worlds and visual workloads differ. The WIP reference already contains the persistent slice; the pre-slice `b1ed3a8` has source/binary comparisons but no comparable full-journey performance run. One short run per scenario is not causal attribution, a confidence interval, or a complete pre/post implementation benchmark.\n\n'+table(['Revision','Scenario','Avg draws/s','Median ms','p95 ms','p99 ms','Calls','Triangles','Quality','DPR'],cr)
 for v in comparison:
  if v.get('error'):body+='\n\n'+v['label']+' comparison error: `'+v['error'].split('\n')[0]+'`; missing measurements not estimated.'
body+='''

| Intended target | Verdict |
| --- | --- |
| Smooth 60 FPS representative desktop / integrated GPU | **UNVERIFIED** — required physical hardware unavailable; VM measurements are poor |
| 60 FPS capable mobile | **UNVERIFIED** — no physical mobile GPU; emulation is not certification |
| Stable 30 FPS lower-end supported hardware | **UNVERIFIED** — no representative supported-device hardware tested |
| No recurring transition/compilation hitches | **Not achieved on available software profile; physical targets unverified.** Repeated tail stalls and covered waits are measured |

Existing native `npm run perf:immersive` failed waiting 60 s for hub arrival: [log](raw/existing-perf.log), [failure](raw/existing-perf/failure.txt). An earlier concurrent attempt was aborted and excluded ([log](raw/existing-perf-concurrent-aborted.log)); no contaminated result is treated as a benchmark. Historical 9 October performance was on a different run/configuration and is not mixed into today's table. No fabricated mobile benchmark or VRAM figure is supplied.
'''
block('PERFORMANCE_RESULTS',body)

cycles=read('raw/resource-lifecycle.json',[]);rr=[]
for c in cycles:
 st=c['stats'];gl=c['contexts'][0]['stats'];m=c.get('memory',{})
 rr.append([c['visit'],st['textures'],st['geometries'],gl['Texture']['active'],gl['Buffer']['active'],gl['Program']['active'],gl['Shader']['active'],gl['Buffer']['deleted'],gl['Program']['deleted'],fmt(m.get('jsHeapBytes',0)/1048576)])
resource='Six settled Hub↔Aftermovie rounds, same page/context, each sampled at Aftermovie after 1.2 s and explicit GC: [raw allocations](raw/resource-lifecycle.json). Counts come from `gl.info.memory` and wrapped WebGL create/delete APIs, not inferred React unmounts.\n\n'+table(['Visit','Three textures','Three geometries','GL textures','GL buffers','GL programs','GL shaders','Cumulative buffer deletes','Cumulative program deletes','Sampled JS MiB'],rr)
resource+='\n\nNormal arrival plateaus at **25 Three textures, 154 geometries, 29 GL textures, 572 GL buffers, 45 programs**. Program/buffer deletions increase through repeat visits. GL objects include renderer internals not counted as mapped Three textures; these counters are not VRAM sizes. Wrapped creation-minus-explicit-deletion counts are not direct enumeration of live driver objects: garbage collection or context loss can reclaim objects without an observed delete call. Three renderer texture growth independently supports the suspected cleanup problem. Crowd has four cached baked geometries and current material/instance resources; no stage GLB proliferation was observed. `Performance.getMetrics` was not enabled in this first six-cycle harness, so its `metrics: []` entries are **not heap measurements**; the labelled heap values above come from diagnostic performance.memory samples. Playback cycles separately enable CDP metrics.\n\nResident geometry source payload at Aftermovie is roughly **2.59 MiB**; source texture payload estimate about **42.94 MiB**, before playing video. These count buffer/image payloads, not driver allocation, compression, GPU padding or reliable GPU memory. A fresh direct-stage comparison records 115 uploaded geometries, versus 154 after the full journey. The difference is consistent with view-dependent lazy GPU uploads; those two samples are not a repeated-visit leak test. CPU scene residency and GPU upload counters are distinct. Driver/decoder/process RSS and retained material object counts were not measured with a full heap graph. Active programs plus explicit source ownership are the available material/shader evidence.'
mc=media.get('cycles',[])
if mc:
 mr=[]
 for c in mc:
  returned=c.get('returned',{});arrival=c.get('arrival',{});st=arrival.get('stats',{});gl=arrival.get('contexts',[{'stats':{}}])[0]['stats'];metrics={m['name']:m['value']for m in c.get('metrics',[])}
  mr.append([c['visit'],c.get('playing',{}).get('videos',[]),returned.get('videos',[]),st.get('textures','—'),st.get('geometries','—'),gl.get('Texture',{}).get('active','—'),gl.get('Program',{}).get('active','—'),fmt(metrics.get('JSHeapUsedSize',0)/1048576)if metrics else '—'])
 resource+='\n\nRepeated actual movie playback→header return→map arrival: [raw media/GL/CDP evidence](raw/media-cycles.json), [log](raw/media-cycles.log). Diagnostics arrays are explicitly cleared before post-GC heap sampling to avoid mistaking retained audit frame history for an application leak.\n\n'+table(['Cycle','Videos during play','Videos after return (src/paused/connected)','Arrival textures','Geometries','GL textures','GL programs','Post-GC heap MiB'],mr)
for c in media.get('checks',[]):resource+='\n\nFinal playback-cycle check (renderer allocation bounds, not VRAM bytes): **'+c['status']+'** — '+c.get('error','Raw state and resource assertions linked above.').split('\n')[0]
resource+='\n\n**Playback resource-bound assertion FAIL:** settled textures grew 25→26→27→28, and explicitly counted GL textures 29→30→31→32. Geometries stayed 154, programs stayed 45; post-GC JS heap rose from 13.61 to 14.20 MiB over four cycles, with 325 DOM nodes/two documents stable. Detached movie elements were released; the remaining connected preload-none video is Canvas native fallback. This is a suspected texture lifecycle leak, not a proven byte-size VRAM leak. The first cycle may not exercise identical upload timing; do not infer a leak slope beyond this sample. A plausible source-level race is late LED sampler reset (400 ms after an effect) versus VideoTexture disposal (600 ms after stop) under slow main-thread frames, allowing a disposed texture to be rebound/recreated. Allocation stacks were not traced, so that cause remains a hypothesis.\n\nInitial media assertion failure retained: [initial raw](raw/edges-and-media-initial.json), [initial script](scripts/edges-and-media-initial.mjs). That assertion included every video, including Canvas\'s connected native fallback with `preload=none`. The refined check inspects detached runtime-owned movie elements and preserves fallback evidence rather than requiring an unused native alternative to erase its configured src. Any remaining failure is reported without a production fix.'
block('RESOURCE_RESULTS',resource)

shots=[]
for f in sorted((r/'screenshots').glob('*.png')):
 name=f.name
 if name.startswith('mobile'):settings='390×844 CSS / DPR.5 (844×390 landscape); Chromium emulation'
 elif name.startswith(('13-','14-','15-','16-','17-')):settings='1366×900 / requested DPR1, adaptive actual DPR; reduced motion static capture; see navigation-details'
 elif name.startswith('critical'):settings='1366×900 / DPR.25; actual fallback'
 else:settings='1366×900 / DPR.25; actual public-control capture'
 shots.append([f'[ {name} ](screenshots/{name})',settings])
block('SCREENSHOT_INDEX','All files below exist and are actual screenshots of the running website. Required desktop journey frames 01–10 share 1366×900 CSS aspect; 10 is the implemented aerial map. Mobile captures are emulated viewports, not a physical phone. Higher-resolution stills and fallback captures are additional evidence. Exact absolute directory: `/workspace/Breeze-2027-navigation/reports/verification-2026-10-10/screenshots/`. Capture pose/state/DPR metadata is in [browser audit](raw/browser-audit.json) and [additional stills](raw/navigation-details.json).\n\n'+table(['Exact relative artifact','Capture profile'],shots))

pc='Archived pre-slice website captures are available as [original stage near](../../design/references/baselines/original-website/05-original-stage-near.png) and [original movie playing](../../design/references/baselines/original-website/06-original-aftermovie-playing.png). These were supplied in the repo, not captured by this audit; original hardware, pose/exposure and date are unknown. Current actual equivalents: [stage viewing](screenshots/09-desktop-aftermovie-viewing-area.png), [movie](screenshots/11-desktop-aftermovie-playback.png).'
for c in comparison:
 if c.get('screenshot'):pc+='\n\nFresh '+c['label']+' comparison: ['+c['screenshot']+']('+c['screenshot']+'); actual WIP/current application capture after the matched idle sample and before strafing, at the same relative stage pose, viewport, DPR and FOV58; world/lighting contents differ.'
block('PRESERVATION_COMPARISON',pc)

checks=read('raw/command-results.json',[])
tr=[]
for c in checks:tr.append([c['command'],c['result'],c.get('note',''),f"[log]({c['log']})"if c.get('log')else '—'])
block('TEST_RESULTS',table(['Executed command / check','Result','Scope/error/attribution','Raw evidence'],tr)+'\n\nThe first build failed because an audit source snapshot was saved with a `.tsx` suffix and included by TypeScript. Only that evidence filename was changed to `.tsx.txt`; the corrected production build and explicit type check pass. [Audit-induced failure retained](raw/build-audit-copy-failure.log). This was not silently fixed in production. Twenty lint warnings match the prior audit line-for-line: [comparison](comparison/lint-comparison.json). Tesseract worker bootstrap fetch/hang is also previously observed; it is not established as a new immersive regression. Initial overbroad media assertion and script portability failures are preserved separately from actual website failures. Suite process exit0 does not erase FAIL rows inside browser check JSON.')

integrity=read('raw/source-integrity.json',{})
body='[Before hashes](raw/source-hashes-before.json), [after hashes](raw/source-hashes-after.json), [integrity result](raw/source-integrity.json), [final Git status](raw/git-status-after.txt), [artifact manifest](raw/artifact-manifest.json), [report-link validation](raw/report-link-verification.json), [command results](raw/command-results.json).'
if integrity:body+='\n\n'+json.dumps(integrity,indent=2).join(['```json\n','\n```'])
body+='\n\nMarkdown is ignored by the repository\'s existing `*.md` rule; the report is present on disk and has not been committed. Existing uncommitted production changes remain exactly as at audit start. Generated `.next`, Prisma client, test caches/temp DB and this output directory are verification side effects. Reproduction scripts live only under this report directory; no production implementation was changed.'
block('INTEGRITY_RESULTS',body)
p.write_text(s)
print('Wrote',p,len(s.splitlines()),'lines')
