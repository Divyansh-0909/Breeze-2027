# Tunnel exit integrated into the quarry rock

Starting branch: `codex/navigation-board`; revision `88b6c5989477a14a032121b934b25666a044f9de`; working tree clean before this task. [Starting metadata and public/Assets hashes](raw/starting-state.json) and the source/configuration snapshots in [baseline](baseline/captures.json) preserve the previous state without credentials.

The user reported a broken-looking tunnel end when looking back from Aftermovie and requested an opening within the rock surrounding the quarry.

## Cause and bounded correction

The previous `exitGeometry()` only generated a roughly 10 m wide, 5.8 m high collar. The broad exterior shell behind it was approximately 60 m wide and 49 m high at its rear rim. The quarry ring deliberately skips three rocks at the tunnel. This combination exposed the exterior shell and large gaps around the detached collar. Section-local noise also assigned different positions to adjacent exterior-rim corners, producing seams.

[blockoutGeometry.ts](../../components/immersive/blockoutGeometry.ts) now closes the entire quarry-facing exterior mass around the original passage profile. The face has broad irregular facets, matches the shell's edge vertices and uses the surrounding quarry's rock palette. Noise is continuous at the last two exterior rings, closing the rear-rim seams. Relief extends toward the exterior, away from the playable quarry. The human-height arch remains physically open; no black overlay hides the passage.

[HubScene.tsx](../../components/immersive/HubScene.tsx) uses the existing quarry rock material for this face. No new texture or rendering layer was added. The tunnel interior, bent centerline, landing portal, artist paint, quarry dimensions, scaffold, second-stall positions, walking boundaries, navigation, stage geometry/assets/crowd/video and lighting parameters are preserved. [Preservation checks](raw/preservation.json) confirm zero changed public/Assets files and byte-identical shared layout. This is a blockout correction, not final rock production or a claim of photorealism.

## Verification and actual captures

- [Matched before/after gallery](gallery.html): eight matched desktop/portrait views, including Aftermovie looking back, close tunnel mouth, tunnel exit looking forward and stage front. Actual browser captures, FOV58, desktop1366×900/portrait390×844, DPR.25, quality tier3. [Before metadata](baseline/captures.json), [after metadata](acceptance/captures.json).
- [Public visitor journey](acceptance/journey.json): fresh Enter → tunnel → hub → held W under scaffold → covered Aftermovie arrival on the same Canvas → actual drag to look back → map open/close. Four checks PASS, zero page exceptions. [Actual public-control rear view](acceptance/public-stage-looking-back.png), [map](acceptance/public-map.png), [raw journey output](raw/journey.log).
- `npm run test:immersive`: [57 PASS](raw/tests-after.log). The added geometry regression verifies solid rock at both shoulders and above the mouth, finite vertices and an unobstructed human-height passage. It failed against the old collar as expected: [before-fix output](raw/tests-before.log). Existing occlusion, reveal, movement, boundary, input and navigation coverage remains.
- `npm run build` and `npx tsc --noEmit`: PASS. [Build log](raw/build.log), [typecheck log](raw/typecheck.log), [commands/results](raw/checks.json). Existing lint warnings are included in the build output; no unrelated source fixes were made.

The first baseline attempt at direct `/aftermovie` with DPR.5 timed out after90s waiting for local readiness: [original capture log](raw/capture-baseline.log). A separate12s observation showed `boot`, not a reported runtime error. Its cause was not established or fixed in this visual task. The complete before/after captures instead use the existing hub→Aftermovie coordinator with DPR.25, and the separate public journey passes. This limits direct-entry acceptance for this run; the timeout is not hidden or declared resolved.

## Rendering cost and limits

[Raw renderer counters](raw/render-counters.json) compare matching views. Desktop rear-stage calls remain57, textures25 and geometries154; triangles increase from1,020,018 to1,020,158 (+140). Desktop close-mouth calls remain28, textures25 and geometries154; triangles increase88,942→89,082. Desktop stage-front calls115 and triangles1,020,152 are unchanged. Portrait counters are also recorded; live stage effects can change individual culled draws.

These are frame snapshots on Chromium151/SwiftShader in the cloud VM, not sustained frame-time or VRAM measurements. Portrait captures are browser aspect emulation, not physical iPhone profiling. Physical GPU/mobile performance is UNVERIFIED. Low DPR limits fine-detail review, and pixel-identical stage imagery is not claimed.

Only the two production geometry/rendering files above, [one regression test](../../tests/immersive/runtime.test.ts), the appended baseline note and this evidence directory changed. Stage2 art production was not started.
