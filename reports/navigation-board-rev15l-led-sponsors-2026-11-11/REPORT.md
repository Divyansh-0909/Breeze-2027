# Rev15L — Aftermovie and Past Sponsors LED

11 November 2026. Current editable navigation-board candidate; visual approval and the proposed Schedule destination remain pending.

## Board layout

Aftermovie is the top direction sign below the existing Gullyverse header, with a real upward arrow. Events and Team keep their left/right row. Schedule is proposed for the former upper Past Sponsors slot; Contact Us stays beside it. The lowest plaque reads PAST SPONSORS without a direction arrow. Directly beneath it is a rounded black LED casing with short mounting brackets and power cable.

The screen is 6 cm below the plaque. Its case is 4.08 × 0.76 × 0.18 m; the visible LED face is 3.86 × 0.643 m. Extending the original frame upward keeps a conservative 2.15 m clearance over the walkway. The existing Gullyverse header, sign family and current mural artwork are retained.

Schedule is recommended because visitors need quick access to event timings. It is shown as a proposal in the freed-up slot; this review does not claim a new live destination or route.

## Sponsor display

The ticker contains 62 unique available marks from `public/images/sponsors` and `public/spons-image` in the work-in-progress-2027 branch. `evidence/sponsors.json` records the branch, Git HEAD, source paths, original checksums, canonical variants, UV bounds and tile positions. The user identifies these branch logos as past sponsors; individual historical sponsorship years were not independently inferred.

Original repository files are unchanged. Several `.png` files actually contain SVG, JPEG, WebP or AVIF data. The input originals are preserved, and format-normalized PNG derivatives are supplied for consistent rendering. SVG marks are rendered faithfully using CairoSVG. No sponsor artwork was invented or redrawn.

`source/render-logo-strip.py` renders the original marks through alpha/background-contrast shaders into one monochrome strip. Both the native Blender LED material and the review shader sample that strip at cell centres, with a 384 × 64 circular-diode grid and amber-red emission like the supplied LED reference. The strip repeats at 30 cells per second. Repeating texture coordinates and the modulo offset avoid an empty seam between the last and first marks.

The packed master includes the strip and runs the animation when its timeline is played. The private Three.js preview also scrolls continuously, with pause, close-up and sponsor-selection controls. The MP4 is an actual continuous browser recording crossing the last-to-first logo boundary. It is a short demonstration rather than a recording of the full 62-mark period.

## Verification and preservation

The new master contains 42 scenes and preserves the exact object memberships of all 41 historical scenes. The original Rev15K master is unchanged. Unrelated scene objects, original light energies and all eight mural meshes/materials are retained. The new scene has an independent mural controller. The moved sign light and local LED spill belong to this new board version.

Fresh-open checks confirm all file images are packed, no linked libraries, all eight mural states exclusive, native loop offsets correct and the previous controller independent. Every source logo checksum matches the branch, and all 62 rendered strip tiles contain visible ink with fitted height.

The private GLB exports only the active board, with evaluated world transforms baked from the freshly opened master. Browser checks verify the actual sign order, one exported scene, continuous motion, 62 sponsor choices, a pixel-identical loop start/end, a zero-gap boundary and no browser errors or horizontal mobile overflow. Native screenshots and PDF use the full saved Blender environment. The web review shows an isolated board with review lighting; physical-device performance is not established.

This task does not integrate or deploy the website. No commit, push or merge was performed.

## Files and backup

- `delivery/Gullyverse-Rev15L-Navigation-LED.blend`: actual packed editable master.
- `viewer/`: self-contained animated board preview, vendor modules and logo derivatives.
- `inputs/logos/`: original branch logo bytes; `inputs/navigation-before.png`: prior board capture.
- `renders/`: current native screenshots and browser evidence.
- `review/`: PDF and MP4 demonstration.
- `source/`: preparation, Blender authoring, export, rendering, checks and restore scripts.
- `evidence/`: provenance, checksums and validation results.
- `repository-files/`: current project-pointer snapshots for deliberate restoration.

Drive subphase: https://drive.google.com/drive/folders/1tLpi-33dYrA1mLRDQynQcmBhMW_7fhdI

Complete checkpoint: https://drive.google.com/drive/folders/1DSw0WQx7_3OSYsarmyc_AJtSZoGg7lLS

The checkpoint includes the full edited master and all new required assets. The unchanged original Rev15K master is reused from its previously verified checkpoint, as recorded in `evidence/base-reference.json`. Consult completed receipts for actual remote verification status.
