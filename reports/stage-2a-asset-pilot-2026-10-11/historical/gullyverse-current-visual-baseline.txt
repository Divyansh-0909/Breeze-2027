# Gullyverse — current visual and spatial baseline

Captured from the current production build on 11 October 2026. **This implementation takes precedence over historical art directions, coordinates and lighting recommendations.** This review does not authorize any redesign. No production source, assets or runtime configuration were edited.

Starting repository: `codex/navigation-board`, HEAD `e3dbbc233f1f12f5e4d96333db3b797e75da4760`; staged, unstaged and untracked status all empty. [Exact starting state](../reports/current-final-review-2026-10-11/raw/starting-state.json), [source hashes](../reports/current-final-review-2026-10-11/raw/source-hashes-before.json), [history](../reports/current-final-review-2026-10-11/raw/history.json). The previous baseline document describes an earlier uncommitted tree; it is not today's Git status.

## Visual evidence and capture conditions

[Browsable gallery](../reports/current-final-review-2026-10-11/gallery.html), [all core capture metadata](../reports/current-final-review-2026-10-11/raw/capture-metadata.json), [final review](gullyverse-current-final-review.md). Individual desktop/mobile PNGs are linked in the gallery; the evidence ZIP preserves them at original capture resolution. Desktop 1366×900 and portrait 390×844 use Chromium's actual production renderer, requested DPR 0.5 for environmental screenshots. Effective DPR, quality, camera XYZ/yaw/pitch/FOV and screenshot acquisition end pose are recorded individually. Screenshots use CSS scale for full viewport pixel dimensions; that does not make the underlying WebGL framebuffer DPR 1. Portrait is touch emulation on the same software GPU, not an iPhone benchmark.

Existing registry inspection cameras provide repeatable views; their screenshots are explicitly labeled as inspection. Fresh landing, cinematic entrance frames, map, playback and boundary shots use public controls. Live cameras can move while a screenshot is acquired: metadata records both endpoints. Fixed tunnel cameras do not prove cinematic occlusion; the separate live sequence and visitor trace are the evidence for that. No generated concept imagery is substituted for browser screenshots.

## World geometry and scale

Units are metres, Three.js Y up; front views face toward decreasing Z. Exact configuration: [current layout JSON](../reports/current-final-review-2026-10-11/raw/current-layout.json). [Computed geometry bounds](../reports/current-final-review-2026-10-11/raw/geometry-bounds.json) come from executing the current deterministic geometry functions without modifying them.

| Area | Actual current configuration | Ownership |
| --- | --- | --- |
| Quarry collision footprint | X −49.8…48, Z −165.5…−42; **97.8×123.5 m**, 20 vertices | `blockout.layout.json`, `world.ts`, `navigation.ts` |
| Rendered quarry rocks | 25 transformed faceted dodecahedra, merged into one vertex-colored mesh, 900 triangles; bounds X −72.474…70.147, Z −189.347…−29.990, Y −14.895…36.426 | `blockoutGeometry.quarryGeometry` |
| Nominal wall data | `wallHeights` 31.85…41.6, benches 0/14/28/43, setbacks 0/1.2/3.5/6 | Registry/aerial fitting; **not** a rendered terraced quarry. Restored mesh uses its own sinusoidal rock heights. |
| Front portal | Registry width58, height18 at [0,0,0]; generated mesh X−28…30, Y−.08…18, Z−3.02…1.241; 640 triangles | `portalGeometry` |
| Passage | Z0…−42; centerline [0,0], [−2.2,−8], [−6,−16], [−6,−24], [−2.6,−34], [0,−42]; 11-point cross-section up to5.6 m high, width about5.9; walking half-width2 | `tunnelGeometry`, `world.tunnelCenter` |
| Tunnel shell | Interior plus outer rock mass 3500 triangles; complete mesh bounds X−31.687…33.400, Y−.08…37.726, Z−42…0 | `tunnelGeometry`; bounds are exterior, not passage clearance |
| Quarry-facing exit | Annular closure160 triangles; X−31.565…33.400, Y−.08…35.681, Z−42…−36.769; crown blends across rear40% of exterior | `exitGeometry`, shared exterior rim |
| Ground | 600×600 generated uneven plane around [0,−.06,−104]; computed Y−.052…0, 11264triangles; no artificial circulation paths | `groundGeometry`, `worldPaint`, `GroundDetail` |
| Ground dressing | 340 instanced stones,180 three-blade grass tufts | `HubScene.GroundDetail`; sparse blockout dressing |

The collision footprint and rendered rock bounds are different measurements. Neither should be resized to match an older report. Rendered wall detail remains procedural and visibly coarse; it does not establish photorealism.

## Entrance and tunnel appearance

The current landing frames a broad gray-green textured rock face, irregular arched opening and cream GULLYVERSE graffiti above it. The entry copy remains left-bottom on desktop; mobile has its own fitted lens. Artist paint is visible in the enclosed passage. The bent corridor conceals the distant quarry initially. This is a functional blockout with a smooth, broadly planar outer face and low-frequency generated texture, rather than sculpted geological detail.

Artist names are NEHA KAKKAR, CHAAR DIWAARI, RITVIZ, KHULLAR G and TWIN STRINGS. They use generated alpha CanvasTexture paint on surfaces mapped to the current tunnel walls, not rectangular framed plaques. Roof/wall facets, generated marks and ground lack final normal/roughness/decal detail. The rear closure and lower geological crown are the latest accepted correction to the detached/broken tunnel rear; the front portal and interior path were retained.

[Portal/tunnel source](../reports/current-final-review-2026-10-11/source/components/immersive/blockoutGeometry.ts.txt), [paint source](../reports/current-final-review-2026-10-11/source/components/immersive/worldPaint.ts.txt). Historical reference photos are comparison/inspiration, not permission to replace the latest composition.

## Navigation installation — locked composition

Origin [0,0,−70], width24, height14.5, depth3.4. It stands 28 m beyond the tunnel exit and19 m ahead of the hub spawn. The front-only original stage truss system supplies both uprights, top beam and Breeze logo. Industrial lattice, foot blocks, straight hanging cables and three shaded practical lamps remain. No separate freestanding Aftermovie sign is present.

| Hanging sign | Local position / dimensions | Text / direction |
| --- | --- | --- |
| Header | [0,11.4,1.8],10×2.4, tilt.02rad | GULLYVERSE only, centered; Breeze2027 remains on top truss logo |
| Events | [−5.1,8.8,1.8],6.4×1.16 | EVENTS ↖ |
| Past Sponsors | [5.1,8.8,1.8],6.5×1.16 | PAST SPONSORS ↗ |
| Team | [−5.1,7.25,1.8],6.3×1.13 | TEAM ↙ |
| Contact | [5.1,7.25,1.8],6.5×1.13 | CONTACT US ↘ |
| Aftermovie | [0,5.65,1.8],9.2×1.18 | AFTERMOVIE ↓ |

Directional text uses a common0.58 m world-space size and aspect-correct board textures. Main Stage and Accommodation hanging signs were intentionally removed. The first registered gate supplies each canonical arrow. Aftermovie now also has a forward gate under/beyond the scaffold, preserving the user's request to walk through it without being stranded at the boundary. Do not reorder signs or move the installation to match the reference photograph.

[Scaffold/stalls/population source](../reports/current-final-review-2026-10-11/source/components/immersive/HubScene.tsx.txt).

## Lighting, materials and atmosphere — locked configuration

| Mode / component | Current values |
| --- | --- |
| Hub / aerial map | Background and fog#737d87, fog205–520; hemisphere sky#a9bfd4, ground#8a8274, intensity1.35; directional [−70,37,−145],#efd0a4,intensity1.35 |
| Aftermovie local mode | Background/fog#b2bbb9, fog55–130; hemisphere#d8e0dd/#686b59,intensity.65; hub directional omitted |
| Scaffold | Point lamp[0,9.75,2.6] relative to scaffold,#ffc681,intensity42,distance21,decay2; emissive bulb surfaces and hanging cones |
| Quarry / exit | Standard material, roughness.98, flat shading, vertex colors, DoubleSide; no authored rock PBR maps |
| Entrance / tunnel | Lambert generated512² rock map + vertex colors, DoubleSide |
| Common terrain | Lambert generated512² ground map,tint#c8c2b4; dry brown/gray rocky-grassy direction |
| Stage-local floor | 49×39 at stage-local[0,.012,7.5],#07080b,roughness.9,metalness.1 |
| Renderer | R3F/Three default tone mapping/exposure unless set by underlying renderer defaults; no explicit immersive exposure override, no immersive global postprocessing or shadow-map enablement |

The actual screenshots read muted gray/green with dark stage/crowd silhouettes and warm practical accents. They do not demonstrate detailed natural dusk illumination, baked contact shadows or realistic layered rock. The local dark floor edge and shorter stage fog differ visibly from hub/map mode. These are review concerns within the approved current configuration; no lighting/floor changes were made or authorized by this reporting task. Standalone Team/Contact pages have their own existing shadows/postprocessing and separate lighting; do not confuse that with the quarry's settings.

## Stall zones and population

Left generic stalls: [−21,0,−65.4], [−30.6,0,−91.4], [−29.4,0,−100]; right: [21.6,0,−65.4], [30.6,0,−91.4], [28.8,0,−109.6]. Size7×3.5×4, inward-facing yaws±π/2. Team occupies the **second left position** [−27.6,0,−77.1], anchor[−24,1.72,−77.1],8×3.8×1.2. Contact is **second right** [27,0,−77.1], anchor[23.4,1.72,−77.1],7×3.5×4. Shared central corridor stays open.

Current quarry stalls are instanced procedural counters/roofs/posts, sign textures and strings of small luminous bulbs. Team is a simple slab/sign, Contact a procedural stall. No immersive polaroid board zoom or in-quarry attached contact form is implemented. Their existing separate `/team` and `/get-in-touch` pages contain richer presentations and content. Capsule people are explicitly temporary in the quarry and distant stage; near Aftermovie uses original baked GLB crowd. Registry population parameters are retained exactly in the linked JSON.

## Aftermovie — preserved identity and current integration

Stage origin[−12,0,−134.3],yaw0. Original stage GLB, male/female GLBs and movie are byte-identical to older revisions: [hash evidence](../reports/current-final-review-2026-10-11/raw/stage-preservation.json). Stage GLB417140 bytes,53mesh primitives,6192source triangles. Man493196 bytes/1852triangles; Woman1491780bytes/6108triangles. Movie52291090bytes, progressive Range loading after user play. Principal stage, thrust runway, trusses, speakers, barricades, LED panels and light effects remain.

Current dark49×39 local floor and cream return placard at stage-local[6,2.8,27.8] are selectively retained original-style elements; the placard is visual, not the boundary menu interaction. The surrounding quarry remains visible behind the player. All this belongs to the present baseline, even where an earlier audit suggested changes.

Near crowd bakes two idle frames per gender (four variants), normalizes height and instances them with deterministic anchors. Counts900/600/300/300 for quality0/1/2/3. Near rows favor the cheaper male mesh; it is not a newly simulated or fully animated crowd. Three LED screens share one runtime-created HTMLVideoElement/VideoTexture, with cropped contiguous windows, cell/grout shader and entrance/exit blending. Film camera world target[−12,5.9,−117.3]. Reduced motion suppresses moving effects; pyro only quality0/non-reduced while playing.

[Scene composition](../reports/current-final-review-2026-10-11/source/components/immersive/AftermovieScene.tsx.txt), [retained local environment](../reports/current-final-review-2026-10-11/source/components/immersive/AftermovieEnvironment.tsx.txt). Byte preservation does not prove identical rendered lighting or adaptive crowd density.

The outer quarry registry footprint and its union-constraining helper are not the active visitor walking zone. The runtime navigation coordinator clamps the smaller Hub/Aftermovie polygons below. Rendered rock extents are wider than the nominal outer polygon. Nominal registry wall heights/bench levels used for fitting or layout are not proof of rendered terraced walls; the current restored rock generator has its own geometry.

## Movement, cameras, map and routes

| Parameter | Current value |
| --- | --- |
| Player | eye1.72,radius.38,speed4.2m/s,damping16; simulation dt≤.05s |
| Landing | [0,1.72,11.5],yaw0,pitch.15; requires intentional click/tap/Enter |
| Hub spawn / arrival | [0,1.72,−51] / [0,1.72,−46],yaw0,pitch.2 |
| Aftermovie spawn / arrival | [−10.5,1.72,−110.8] / [−10.5,1.72,−106.8],yaw0,pitch.16 |
| Hub movement | octagon X−20…20,Z−73…−42; six gates for five destinations, including second Aftermovie gateedge4 range.2–.8 |
| Aftermovie movement | octagon X−21…−3,Z−119.5…−105.3; all outer faces open text destination choices, not forced return |
| Camera | base vertical FOV58,near.1,far700; portrait composition fits horizontal42/34/58° by landing/tunnel/hub with verticalcap82→104 |
| Aerial | Same world; boundary/rim/portal samples +24m outward margin; landscape yaw0→−π/2,FOV80→64,padding1.065; computed heightfits aspect; saved pose restored on descent |
| Map markers | Shared destination world coordinates + left/right stalls/scaffold/tunnel exit; finite clip-W/depth/frustum guard and overlap-adjusted labels; no navigation-path graphics |
| Timings | Entrance7.2s active foreground; physical departure.65s/arrival.75s; map ascent1.4s/descent1.1s; readiness wait separate and covered |

[Coordinator](../reports/current-final-review-2026-10-11/source/components/immersive/navigation.ts.txt), [runtime/camera](../reports/current-final-review-2026-10-11/source/components/immersive/runtime.ts.txt), [aerial fitting](../reports/current-final-review-2026-10-11/source/components/immersive/aerial.ts.txt), [projection/overlays](../reports/current-final-review-2026-10-11/source/components/immersive/WorldOverlays.tsx.txt). Full polygons/gate ranges and every registered inspection camera are in current-layout.json; do not substitute historic coordinates.

Events is an existing webpage route with a physical reservation/sign. Sponsors is disabled in immersive controls and middleware redirects `/sponsors`; Accommodation has no destination href and is disabled. Neither is a completed 3D environment. Team/Contact leave the shared immersive Canvas for separate existing pages. Canvas persistence is scoped to `/`↔`/aftermovie`, not every website route.

## Current quality policy and asset status

Quality tiers0/1/2/3 cap DPR1.25/1/.75/.6. Coarse pointer starts tier1. Covered readiness initializes static textures, compiles shaders, draws two upload frames plus a twelve-frame measurement window, and lowers stage quality if it misses55FPS. Runtime quality checks two-second windows with upgrade cooldown. This is adaptive policy, not proof of actual60FPS on a device.

[Asset inventory](../reports/current-final-review-2026-10-11/raw/asset-inventory.json), [source material/resource policy](../reports/current-final-review-2026-10-11/source/components/immersive/rendering.tsx.txt). Quarry/entrance/tunnel/ground, graffiti, hub people/stalls remain procedural blockout. Scaffold construction and stage identity are reusable, but no final realistic rock masters exist. Existing richer standalone stall/team GLBs are not what HubScene renders. Current GLB inventory has no Draco/Meshopt/KTX2 compression; LODs are not automatically provided by the loader. Blender sources include the prior technical cube, not a production quarry master.

## History and precedence

The October audit captured8919589 plus uncommitted compact quarry/restored stage work. The later stabilization commitc5ffe11 includes that baseline and technical repairs; its entire diff is not synonymous with newly designed visuals. [Current versus audited worktree comparison](../reports/current-final-review-2026-10-11/raw/changes-against-audited-worktree.json) distinguishes changes from that manifest. Commit88b6c59 widened only walking bounds, added under-scaffold Aftermovie travel and moved Team/Contact to second stalls. Commits8998866/e3dbbc2 integrated the rear mouth and shaped its crown. Dependencies sharp/@next/env were declared directly for builds. No additional manual edits exist in today's clean starting tree; individual human authorship is not inferred from commit author labels.

This report freezes the actual present composition for review. Historical references and recommendations do not override it. Art refinement should preserve its dimensions, anchors, signs, current lighting and selectively restored stage elements unless the user approves a particular change.
