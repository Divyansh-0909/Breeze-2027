# Gullyverse — Indian lane to rooftop cypher / Blender concept study

Handoff: `WORLD-LANE-ROOFTOP-ABC-20261023-01`.

Decision: **READY FOR USER CONCEPT REVIEW**, not approval for website implementation or production art. No A/B/C variant is selected automatically. Recommend C for discussion; A is the restrained alternative and B demonstrates a stronger festival takeover.

## Exact preserved website baseline

`work-in-progress-2027` / `e638140b37045a805b23b4d406d387a8870f8486`, `/workspace/Breeze-2027-wip-push`. All new work is outside that repository, under `/workspace/gullyverse-world-concept/2026-10-23`. The original `/workspace/Breeze-2027-navigation` tree is untouched.

All **1213 existing application/source/public/asset/test/document files** retain their recorded bytes and SHA-256; Git status is identical to the starting dirty state. This includes the completed canal-material code, approved C9/current cave/C8 3× material, layout, original stage/crowds/Aftermovie, navigation and existing edits. No commit, push, merge, deployment, public-default change or runtime code was made. An additional 311-file comparison against the earlier canal checkpoint also passes, including its complete gallery/PDF/report assets. The earlier canal shootout remains complete but unreviewed; the new setting direction does not retrospectively approve its materials.

## Authorized brief and cultural direction

The shared document's user-approved new world prompt was read and the user explicitly authorized starting this Blender study. Its frozen text is in `evidence/authorized-prompt.txt`.

The new sequence is an Indian neighborhood lane at night → visible distant silhouettes through haze → an architectural corner opening onto a rooftop cypher → the existing signboard's recognizable hierarchy → Team on the right / Events on the left → a short crowd-camera move → the existing digital Aftermovie screen. The screening audience is not a band watching a new giant stage.

The lane uses generic, fictional Hindi/Hinglish kirana, chai/nashta, mobile-repair, tailoring and stationery shop identities; occupied warm shops alternate with closed rolling shutters. Balconies, service cables, drainpipes, AC units, parked scooters, crates, water tanks and neighboring mixed-use buildings establish context. No named real street is reproduced and no caricature/neon-city treatment is proposed.

## One site-scale plan, three art layers

Coordinates are Blender metres: X right, Y forward, Z up. The lane has 6.8m nominal clear width; props are confined to its edges. It begins on a supported market podium at Z+6.0m. A 24m run rises 1.2m at 1:20, followed by a flared apron and +7.2m rooftop. No stair/elevator requirement, loading cut or teleport is introduced into the proposed entry route.

A roof service room at the end of the lane creates a genuine sightline corner. The path passes its left shoulder before returning to the central hub at [0,22,7.2]. The screen cannot be seen from the landing camera even when haze is excluded from the visibility survey. Three lane-end crowd stand-ins remain architecturally visible. The visible group creates curiosity; a convincing animated crowd is future production work.

The roof is 32m × 34m. The landmark stands to the right of the central corridor, centered at [5.6,25,7.2]. Team is [15,29,7.2], Events [-15,29,7.2], and the screen is straight ahead at Y45.8. An open central audience aisle and side poster-wall approaches are reserved. Crowd marks in the flow diagram are schematic; the Blender scene and survey JSON define the exact positions. See `review/master-layout.svg/png`, `access-section.svg/png`, and exact routes in `evidence/concept-feasibility.json`.

The podium, supports and parapets make the level change spatially legible. They are a virtual architectural concept, not a real building's structural loading, egress or accessibility certification. A real venue would require engineering/site approval.

| Version | Character | Deliberate changes on the SAME layout |
|---|---|---|
| A — Grounded Indian Neighborhood | Quiet lived-in lane; restrained festival takeover | Lower roof/screen spill; warm ordinary shops; shared base audience; minimal temporary graphics |
| B — Festival Heavy Block | Stronger gathering energy | Festival lane banner, small warm practical strings, additional paste-ups and eight secondary crowd proxies; warmer lighting |
| C — Balanced Neighborhood Cypher | Neighborhood intimacy with a recognizable rooftop watch party | Small lane/roof wayfinding, four secondary crowd proxies and moderate light/graphic emphasis |

All three scenes link the SAME architecture, poster-wall, signboard, base-crowd and camera collections. They do not silently change routes, dimensions, screen position or named camera poses. Secondary crowd density, optional graphics and lighting are intentionally the comparison variables.

## Reuse, source artwork and honest proxies

The GULLYVERSE hero plaque is the actual current `worldPaint.ts` canvas generator raster with the inherited project font. The support frame is a newly authored concept reduction (6.4m wide, 6.1m tall) retaining the familiar header/destination hierarchy; it is **not the current 24m × 14.5m scaffold imported unchanged**. Team/Events arrows follow the new proposed directions. Current website scaffold coordinates remain untouched.

The existing LED-screen code defines 13.6×9.2m center, 4×7.2m side panels and 0.4m gaps. This concept uniformly scales that arrangement by 0.65, yielding a 14.56m total width. One still at 12 seconds from the existing Aftermovie is mapped continuously across the panels with width-fit/vertical center cropping. No per-panel stretching or new video is introduced. This is still-image concept presentation, not implemented video playback. Old concert structures visible inside the film belong to the original footage; no physical stage platform, truss, bars or lighting towers are modelled in this new scene.

Eight existing authorized team portraits and their names/roles are reused from `app/(user)/team/teamData.ts`. They become sepia photocopy/paste-up graphics headed THE CREW, a wanted-poster typographic treatment with no claim of criminal wrongdoing. Source portraits are included separately. No real person or face was invented.

Current event artwork is database-backed; a verified local, current event-poster set was not available for this isolated concept. The four original graphic placeholders visibly say EVENT ART PROXY / PLACEHOLDER / NOT FINAL ART. These are not official event/lineup announcements. Missing artist graffiti was not invented. Human bodies, shop stock and scooters are explicitly simplified editable proxies.

Weathered limewash/concrete albedos are existing verified CC0 Poly Haven Scuffed Cement and Worn Plaster derivatives. The concept uses box-projected color and matte response; unused source normal files are authoring references, not a claim of baked production PBR. Full asset origins, native source specifications and retained project/CC0/font-license distinctions are in `assets/asset-provenance.json`, `material-provenance.json` and license files. Project portrait, film and existing-board rights are inherited for this private authorized study, not relabelled CC0. Existing font binaries are not redistributed.

## Blender authoring and scene organization

The editable master is `source/Gullyverse-Lane-Rooftop-ABC.blend` with three scenes A/B/C. Collections separate shared architecture, Team/Events graphics, navigation, crowd stand-ins, camera rig, variant practical lights and variant festival props. All 25 used image sources are packed. Text uses Blender's internal Bfont; sign/portrait artwork is supplied as editable external raster assets as well. No linked external .blend library is required to open the master.

Architecture is deliberately composed at real scale from editable meshes. This is not the rejected C7 rock method, deformed scanned-wall fitting, C8 Boolean union or a quarry regeneration. No quarry geometry is used in the proposed new setting. Source scripts preserve the construction and calibrated surface/camera changes. The initial storefront face-orientation and framing issues are retained as labelled drafts; they are excluded from the final gallery.

Blender 4.3.2 is the authoring tool. A Cycles probe exposed that the installed build lacks integrated OpenImageDenoise. An optional standalone OIDN diagnostic was inspected, but **final renders use Blender EEVEE Next**, 16 samples, with no image-generation, AI concept substitution or post-render denoising. Raw final PNGs are direct Blender outputs. The offscreen software graphics path works after normal EGL configuration fallbacks; this is not a physical GPU benchmark. The same AgX Medium High Contrast / exposure +0.7 is used across A/B/C. Lighting is concept-only and does not alter approved website globals.

## Matched visual evidence and storyboard

The final pack has 36 direct Blender PNGs: 12 named cameras per version. Desktop views are 1200×750; mobile hero is 540×960. All position/orientation/lens/sensor/resolution/sample/engine/exposure fields are checked across A/B/C. Source renders, per-version equal contact sheets, twelve A/B/C side-by-side strips, the offline gallery and a phone-oriented review PDF are included.

Views cover landing, forward lane walk, opening, hub/signboard, Team, Events, crowd-move beginning/middle/reveal, screen-watch composition, orthographic site overview and mobile hero. Inspection of a whole site concept is not presented as an existing public walking camera.

The camera move is keyed at 24fps over frames 1–480: approximately 20 seconds. Twelve rendered poses form the separately labelled **keyframe animatic**; it is not a continuous real-time/browser recording. The source camera animation is editable and can be rendered at full frame rate later. The camera follows the central audience aisle and rises from 1.72m to about 2.42m eye height for its final cinematic reveal. This rise is camera choreography, not a new walking-floor level.

| Beat | Proposed sound/attention cue | Camera/action |
|---|---|---|
| Lane / before corner | Quiet shops, distant crowd and muffled music | Warm shop pockets; silhouettes remain visible; screen hidden |
| Corner / first hub | Crowd becomes clearer and less muffled | Left-side bypass opens onto the roof; discover the signboard |
| 0–5s crowd move | Audience attention draws forward | Enter the clear center aisle; Team/Events remain optional side destinations |
| 5–15s through audience | Nearby cheers / musical pulse | Move between neutral stand-ins; no loading cut |
| 15–20s screen reveal | Aftermovie sound becomes the focus after user activation | Gentle cinematic lift; show the existing three-panel display |

No audio was newly implemented or unlicensed music added; sound is a storyboard proposal. Actual browser media activation/autoplay/return behaviour must be tested in a separately authorized runtime phase.

## Concept feasibility and limits

The mesh/ray survey status is **PASS**. All three variants share the same camera rig and site geometry. Landing screen visibility is 0/15 sampled rays; corner visibility is 11/15 and final reveal is 15/15. The three distant silhouettes are unblocked by architecture. Entry, central screen, Team and Events routes are surveyed every approximately 0.3m with a 0.35m visitor capsule and eye/body horizontal probes. No capsule intrusion or floor discontinuity was found; maximum floor-height error is below 0.002m. The camera move is sampled along its entire duration for nearby intersections. These are checks on the new **concept mesh only**, not the old world's authoritative registry, movement system or runtime implementation.


Measured one-sided minimum horizontal probe clearances (not a two-sided corridor-width certification):

| Variant | Entry | Screen aisle | Team | Events |
|---|---:|---:|---:|---:|
| A | 1.024m | >1.6m | 1.525m | 0.904m |
| B | 1.024m | >1.6m | 1.525m | 0.904m |
| C | 1.024m | >1.6m | 1.525m | 0.904m |

The closest entry and Events probes are below the nominal 1.5m half-width target. The 0.35m visitor capsule passes; a uniform 3m empty corridor is not proven. Movable crowd/prop placement and full accessible/egress envelopes need a later production clearance pass. No test threshold was lowered.

The 3m intended main circulation corridor is a design allowance; the formal pass above certifies only the explicitly reported capsule/probe sample, not a building-code or crowd-capacity claim. Crowds are static proxies. More people, final props, animated limbs and detailed production meshes require renewed clearance and camera checks.

## Offline asset cost and future runtime budgets

| Version | Evaluated mesh/curve triangles | Mesh/converted-curve objects | Material datablocks | Area lights |
|---|---:|---:|---:|---:|
| A | 45,340 | 1,434 | 50 | 12 |
| B | 48,478 | 1,531 | 53 | 12 |
| C | 46,546 | 1,469 | 53 | 12 |

The packed master is 3,930,020 bytes. Its 25 unique authoring images have an approximate **98.91 MiB** RGBA8+mipmap equivalent. This is an authoring estimate, not measured GPU residency or the existing website total. Current packed JPEG bytes are much smaller than decoded allocation.

The object count is unsuitable for naive one-object/one-draw-call runtime export despite modest blockout triangles. Before any site implementation, batch static architectural parts, instance repeated shutters/windows/props and replace crowd bodies with an appropriately licensed, efficient pose/animation kit. Bake or author UVs for box-projected surfaces; do not assume Blender node projection exports directly to standard glTF. Atlas poster/wayfinding graphics where actual readability permits. The concept's area lights and volume are offline design tools; they must not be copied as twelve expensive real-time shadow lights or assumed to map directly to Three.js.

Provisional production targets, NOT verified results: approximately 60–120k near static-environment triangles before final crowd detail; additional crowd cost depends on kit/LOD/pose strategy; roughly 120–180 visible draw calls after batching, and about 64–96MiB selected-scene unique decoded texture residency after atlas/resolution work. Prefer a baked/ambient practical-light solution with a small measured set of real-time lights. Use the existing persistent Canvas, covered preparation and safe owner retirement for mode switching; preserve historical quarry assets on disk without loading both complete environments simultaneously. These targets require actual laptop/phone tests and can change after final asset selection. No hardware FPS or loading equivalence is claimed.

## Existing-system mapping and implementation risks

| Existing capability | Proposed future mapping | Not established by this concept |
|---|---|---|
| Landing/Enter camera choreography | Lane entry → corner → rooftop hub | Actual runtime timings/input/reduced-motion route |
| Destination navigation/fast travel | Same semantic IDs; new Team-right/Events-left coordinates | Reusing the old quarry collision/coordinate registry unchanged |
| GTA-style aerial map | Use the new scaled site/markers with existing map interaction concept | Current camera/projection limits fitting the new site |
| Signboard/hotspots | Familiar hero/header and destination hierarchy | Exact old scaffold component or click-volume compatibility |
| Aftermovie/playback/return | Preserve original video player/owner; crowd-move leads to new screen | Gesture policy, screen UV shader, return anchor and browser-history tests |
| Persistent Canvas/cache/fallback | Retain established ownership principles | A measured new scene/asset-loading implementation |

The new site will need its own local layout/walking manifest and explicit mode integration, not an unreviewed overwrite of the old world registry. Source component integration, collisions, media, context recovery, performance and fallback remain unimplemented here. The current quarry's inherited visibility/cold-stage limitations are preserved in their prior reports; this new concept does not pretend to repair them.

## Artistic recommendation and outstanding work

C best balances the recognizable neighborhood with a purposeful rooftop gathering, while keeping the lane from feeling like a generic festival corridor. A is useful if the user prefers more restraint. B demonstrates maximum takeover but its banner and temporary practicals are more dominant. This recommendation does not select a final version.

The first production needs would be more convincing human animation, less box-like shop stock/vehicles, richer inhabited building detail, deliberate street-art placement using authorized artwork, production poster art, believable roof-edge/service details, UV/bake work and measured lighting. The broad facades and static proxies remain clearly artificial; these are readable environment-design blockouts, not photorealistic finished art. The first audience glimpse is a small group and lacks movement. Fine asset dressing and final crowd composition are unresolved. The proposed podium is fictional and intentionally avoids claiming a real neighborhood location.

## Restoration and stop condition

The new private dated phase/subphase Drive folder contains the editable packed master, source/assets ZIP, review/evidence ZIP parts, per-file/archive SHA-256 manifests, restoration instructions and authenticated full download-back verification. All older backups and the previous canal package remain untouched. The new concept master is self-contained; restoring the WEBSITE itself still requires its separately identified previous verified checkpoints. No credentials, .env, dependencies, build caches or downloaded diagnostic-tool binaries are packaged.

Open the .blend in Blender 4.3.2 and select A/B/C scenes and named cameras. All used images are packed; the assets directory supplies editable source graphics and original team portraits. Source generation/review scripts and exact poses accompany it. Raw intermediate renders are labelled as drafts/diagnostics and excluded from the final gallery. Check the final Drive receipt before treating the remote checkpoint as verified.

Stop for user environment-concept approval. Do not implement the website, replace the WIP, choose A/B/C on the user's behalf, commit, push, merge, deploy or start the next phase automatically.

## Verified destination folders

Review: https://drive.google.com/drive/folders/1QBSr156-kiT6Oop818SBZb1sMXE-lW1u

Checkpoint: https://drive.google.com/drive/folders/1XXiVhZHF9aWe3iQ_a6gFWHmJaPUWvmZI

Full-resolution A/B/C renders: https://drive.google.com/drive/folders/13Sp1PrOJUSVjLnbBlCoKBedffCuqrJcH
