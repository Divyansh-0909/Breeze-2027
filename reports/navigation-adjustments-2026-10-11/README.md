# Hub travel, walking boundaries and second-stall placement

Starting revision: `4c58cd1126d3baa97e5e3d7adcc8eb68084d6745`, branch `codex/navigation-board`, clean working tree. The [starting state and asset hashes](raw/starting-state.json), [original shared layout](baseline/blockout.layout.json) and relevant source snapshots preserve the starting configuration without copying environment credentials.

## Changes

- Forward walking originally stopped at z −63.62, before the scaffold at z −70. Only the rear boundary had an Aftermovie gate. The added forward gate shares the existing coordinator and fade/readiness/arrival sequence; the original rear Aftermovie approach and approved downward arrow remain available.
- Hub walking limits change from X [−18,18], Z [−64,−44] to X [−20,20], Z [−73,−42]. Side/rear clearance increases about 2 m. The forward edge extends past the scaffold specifically to permit the requested under-board approach. The forward gate covers the central section, away from the scaffold support collisions. Events/Sponsors corner ranges adjust to retain their diagonal approaches.
- Aftermovie walking limits expand 1 m on every side: X [−21,−3], Z [−119.5,−105.3]. Boundary clamping, destination options and reactivation behavior remain.
- Team swaps slots with the first generic left stall: Team [−27.6,0,−77.1], first generic stall [−21,0,−65.4]. Contact Us swaps with the first generic right stall: Contact [27,0,−77.1], first generic stall [21.6,0,−65.4]. Both are second when approached from the tunnel. Destination anchors/map markers, collisions, generic-stall fixtures and nearby stall groups follow the shared positions. No new crowd models or density were introduced.

Production configuration changes are in [the shared layout](../../public/models/gullyverse/blockout.layout.json). [navigation.ts](../../components/immersive/navigation.ts) only gains an explanatory comment about multiple approach gates. Regression coverage is in [runtime.test.ts](../../tests/immersive/runtime.test.ts). The current baseline document gains a note recording these newly requested adjustments; `.gitignore` excludes this report's transient server log/PID.

The quarry shape/size, tunnel, scaffold placement/composition, stage origin/geometry/video/crowd assets and lighting configuration are preserved. [Preservation checks](raw/preservation.json) verify the shared layout is the only changed public/Assets file and the rendering/runtime source remains unchanged. This is not a claim that relocated stalls produce pixel-identical views.

## Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Reproduce reported forward blockage | REPRODUCED | [Baseline browser results](baseline/results.json): local hub remains blocked at z −63.62. |
| Actual keyboard walk beneath scaffold → fade → Aftermovie | PASS | [Acceptance browser results](acceptance/results.json): departure at z −72.62, covered opacity 1, arrival, local Aftermovie; same Canvas. |
| Existing Aftermovie boundary menu → Return to Hub | PASS | Public keyboard/button path in acceptance results. |
| Map reflects second-stall anchors; finite SVG coordinates | PASS | Acceptance results and [actual map capture](acceptance/map.png). |
| Portrait touch hold beneath scaffold → Aftermovie | PASS | Chromium touch-emulated 390 × 844 viewport; acceptance results and captures. |
| Unit/runtime tests | PASS | `npm run test:immersive`: [56 passed](raw/tests-final.log), including three added regressions, all six approach gates, diagonal directions, clamps and every Aftermovie segment. |
| Production build | PASS | `npm run build`: [build log](raw/build.log), [commands/results](raw/build-checks.json). |
| Type checking | PASS | `npx tsc --noEmit`: [typecheck log](raw/typecheck.log), commands/results. |
| Matched visual captures | PASS within capture scope | [Gallery](gallery.html): four matched poses, FOV58, desktop 1366 × 900, DPR .25, tier3; reviewed actual left/right stall views. |
| Physical laptop/mobile performance | UNVERIFIED | Cloud Chromium/SwiftShader only. Touch emulation is not mobile GPU profiling. |

Before-fix regression failures remain in [tests-before-fix.log](raw/tests-before-fix.log). The first post-config run passed54/56; its failures were outdated "forward must never travel" expectations and comparing guided speed to an arbitrarily short boundary-clipped walking step. [That run](raw/tests-after-fix.log) is retained. The test now requires forward Aftermovie travel and compares guided speed to the last full locomotion step while checking the clipped step remains bounded. Assertions were aligned with actual behavioral invariants, not disabled.

An initial browser run was incomplete after an execution transport interruption and a harness sequencing defect (desktop context closed before matched screenshots). [Initial summary](raw/browser-initial-summary.json) and initial captures are retained. The corrected complete run has four public checks, four matched captures and zero page exceptions: [browser-final.log](raw/browser-final.log). No application change was needed for that harness correction.

Screenshots are actual website captures. Matched views use a diagnostic review camera and are labelled as inspection evidence; journey and touch checks use public controls. No recording, physical-device benchmark or photorealistic art claim is made for this bounded change.
