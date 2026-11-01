# Gullyverse — straight walk and semicircular screen audience

Handoff: `WORLD-STRAIGHT-WALK-SEMICIRCLE-20261025-04`.

## User corrections implemented

The camera walks straight through the open connection with no separate reveal section. Entry and screen routes now remain at X=0. The old left-side L-turn, zigzag through the audience, staged camera lift and reveal-specific camera/action names are removed from the new candidate. One editable 40-second action covers the lane at Y=-27m through the board and hub to Y=36.5m, at about 1.59m/s. Forward heading and 30mm lens are constant. Eye height is always 1.72m above the existing surface; only Z follows the existing 1:20 ramp. No facade, reveal column, camera cut, teleport, fade or geometry popping is introduced.

The Aftermovie audience forms a front semicircular fan facing the screen center [0,45.8]m. The existing 48 shared figures occupy three tiers at radii 7.8, 10.2 and 12.6m, with ends five degrees short of the screen plane. The eight festival extras and four balanced extras sit on compatible additional arcs. The foot-center gap is 4m, keeping a clear central walking/camera aisle. No audience is placed behind the screen. All 60 repositioned figures reuse their original meshes, clothing and poses.

The centered navigation board remains at [0,21,7.2]m. Shops, architecture, floor, ramp, cypher circle, Team/right, Events/left, screen, graffiti/graphics and every light remain unchanged. No A/B/C variant is selected automatically.

## Evidence

23 actual Blender EEVEE stills include six matched current views across A/B/C (18), plus five C inspection/context views: lane, mobile landing, board, high audience angle and rooftop plan. Current cameras differ from historical cameras where required to remove the detour; before/after views are labelled accordingly. A 12-page phone-friendly PDF, contact sheets and full-resolution offline gallery are supplied.

A separate 20-second MP4 shows the actual straight opening walk: 120 independently rendered Blender frames, source frames 300 through 776 every four frames, encoded at 6fps and native 384x240 with two render samples. It is an uncut low-resolution motion proof, not interpolated footage, a held-keyframe animatic, browser video or physical-device FPS evidence. The complete 40-second action remains editable in the master. The conceptual digital screen still displays the existing Aftermovie still; this clip does not claim runtime movie playback.

## Verification and correction

All 960 animation frames were checked in each variant. X error is zero, Y advances monotonically and maximum eye-height error is approximately 0.00000065m. Original 0.35m capsule and <0.002m floor-height tolerances remain unchanged. Entry, straight screen, Team and Events tests pass, and no tested camera intersection occurs. Minimum measured one-sided horizontal rays: 1.512m entry, >1.6m screen, 0.981m Team, 0.625m Events. These are concept checks, not a certificate for continuous route width, regulations or the current website collision registry.

Actual actor object locations and screen-facing orientations were verified independently. An initial authoring issue in the inactive B collection returned cached world matrices. This was repaired by composing unparented local matrix_basis transforms and using evaluated geometry for validation. Incorrect B draft captures are excluded from the review; valid unaffected A/C captures are retained. No validation tolerance was loosened.

All existing mesh data, UVs and materials match the preceding master. The 480 audience body-part transforms and requested cameras change; other object transforms and all lighting remain unchanged. Two diagnostic cameras are added. The new master packs 24 referenced images, estimated 95.86 MiB RGBA8+mips; one unused wayfinding image with zero users retired naturally on resave and remains in earlier checkpoints. No active material sampling changed. Evaluated triangles remain A 44,824 / B 47,960 / C 46,028 with the same 12 offline authoring lights. These are authoring counts, not measured runtime draw calls or GPU performance.

## Preservation and checkpoint

The previous centered-board master and all earlier phases remain unchanged. The website remains work-in-progress-2027 at e638140b37045a805b23b4d406d387a8870f8486. All 1,213 protected files and Git status are preserved. No website implementation, default promotion, commit, push, merge or deployment.

The new dated Drive subphase contains a main source/review archive and a separate archive of every original walk PNG. Extract both for the complete evidence set; the main master opens independently with its packed images. Checkpoint manifests, archive/member SHA-256s, full download-back verification and an independent restored-master open test accompany the backup. All earlier external checkpoints are retained. Stop for user visual review.
