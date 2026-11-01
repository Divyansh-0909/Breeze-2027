# Rev08 — Destination rooftop terrace and exact website crowd reuse

Handoff: `WORLD-C-A-TERRACE-WEB-ASSETS-20261028-f130611a`

Status: READY FOR PRIVATE VISUAL REVIEW; FURNITURE IDENTITY PARTIAL. This is a Blender art candidate. No website integration, final art approval, deployment or hardware performance acceptance is asserted.

## Starting point and preservation

Started from the 28 October wider-realism master SHA-256 `28020ff0d0a499571e615a28fc003ea9411692af4595da5a3b2764ffe0608225`, 14,015,088 bytes. That prior pass remains a technically valid, visually partial historical candidate, not finally approved world art. The latest green correction in the shared Doc was read before work and copied to `source/APPROVED-PROMPT.txt`.

Website branch `work-in-progress-2027`, HEAD `e638140b37045a805b23b4d406d387a8870f8486`. All 1213 protected SHA-256 records and exact starting dirty/untracked Git state are unchanged. Other navigation checkout also unchanged. No website edit, package installation, build, dev server, git mutation, commit, push, merge or deploy occurred.

All 3442 prior object signatures and all five archival scene memberships/settings remain exact. Original A/B/C, selected architectural pilot and wider world remain independently accessible. The new master has 11 scenes: five archives, BEFORE comparison, architecture-only, actual-crowd candidate, two clearly labelled furniture proposals, and a source-audit scene. Its default is the actual-crowd candidate WITHOUT ambiguous table proposals.

## Rooftop gap and implemented architecture

The prior 32 × 34 m roof slab was suspended at Z7.2 m with thin perimeter parapets, screen and neighboring blocks. Added edge finishes alone did not make its destination setting read as a complete terrace. We added an actual two-storey supporting facade beneath the existing slab, continuous RC edge/floor bands, piers, lower-storey openings, front returns below the protected entry art, connected neighboring roof decks outside the original guarding, four inward-facing service rooms, two rear access headhouses and a lower rear roof volume. Doors have real jambs/lintels and recess thickness; roof slabs and guarding have physical coping. Water tanks, ribs/plinths, louvres, drainage, saddles and perimeter service runs give those roofs a purpose.

357 authored components are grouped into 66 static spatial/material meshes. They reuse the existing mineral concrete, muted plaster, roof, zinc, frame, glass and seal materials. No new texture owner or dynamic light was added. This is deliberately additive perimeter construction. Main slab, original parapets/paint, usable floor, route elevation and destination coordinates did not move. The extra adjacent roofs are backdrop/service context behind existing guarding, not a newly approved public walking route.

The architecture surrounds the screen/crowd and Team/Events from forward, diagonal, reverse and elevated viewpoints. The central audience remains open to night sky; no ceiling, new main stage, screen portal, reveal column, banner or detour was added. Top plan and side elevation show the roof/body relationship. The elevation is an exterior orthographic inspection, not a claimed structural-engineering section or regulatory safety certification.

## Exact website asset audit and crowd import

See `SOURCE-AUDIT.md`, source inventory and the preserved code excerpts. `AftermovieScene.tsx` actually mounts `Crowd.tsx`, `Trusses.tsx`, and `Stage.tsx`. Crowd loads the authentic existing `Man.glb` and `Animated-Woman.glb`, chooses Man_Idle / Idle_Neutral, bakes at .35 and 1.35 s, merges/skins positions and indices, recomputes vertex normals and uniformly normalizes height. Our offline Node script executes the original bake function, without running/building the app. Source native rest heights are approximately 4.827 m and 1.800 m; these different authoring scales are deliberately normalized by the actual website.

The four imported Blender meshes match Node output positions and triangle indices exactly after the rigid Y-up → Z-up conversion; maximum position error is zero. Original computed normals are copied. Each original C180 audience identity retains its exact foot position, target stature and screen-facing orientation. Original body geometry remains in archival and architecture-only scenes. No new positions, broader row scheme, prior prototype humans or invented animation are used. 108 men and 72 women use four shared pose datablocks. Their dark diffuse Blender material corresponds to the website's #05060a MeshLambert override, rather than the colored source GLB materials. This is a diffuse-only offline analogue, not a claim that Blender and Three lighting are pixel-identical.

Source idle poses are STATIC in both this candidate and the website's baked crowd. The original clips remain in the source GLBs. No per-frame skinning was added. Characters have unwelded split/primitives topology in the authentic source; boundary-edge counts are reported, not silently healed or passed off as closed solids. They are not used as new collision geometry. The source-mesh parity test preserves their geometry, including those seams.

## Steel racks/tables — unresolved identity, not invented completion

The active Aftermovie steel frame is `Trusses.tsx`, a procedural 26 m-wide / 12.15 m-high box-truss rig using 0.072 m chords, 0.042 m braces and source steel #b7bec9 / metallic .85 / roughness .35. It is not a service table. Re-erecting that full portal would violate the explicit lock against the old screen truss, so none was added here.

The active stage GLB has exact steel-trimmed road cases `PROP_roadcase_0` / `PROP_roadcase_trim_0`: nominal body 1.25 × .85 × .82 m, trim 1.28 × .89 × .05 m. Exact meshes/materials are retained in separately named proposals. The project also stores `festival-stall.glb`, whose TABLE_* assembly is timber and cloth with an aluminium-frame stall; it is not currently mounted by the checked scene and is not a bare steel table. Current HubScene builds simpler counters/posts procedurally. It would be misleading to declare that dormant GLB the requested active steel-table asset.

Two rear service placement proposals show that archived table and an active-source road case at native dimensions, translated only. Both leave all five protected shop counter bases untouched and avoid crowd/route/screen intersections. They are isolated from the selected candidate and explicitly labelled pending. The old Codex counter mockup is shown only as NOT SELECTED historical evidence. The stored cloth extends about 0.33 m above its worktop in the original source, another reason not to adopt it as a final steel table. A clarification identifying the intended rack/table has been requested. Final adoption of an exact steel-rack/table asset is PARTIAL / pending that identity; it is not fabricated to complete a checklist.

## Source rights and provenance

Authentic model SHA-256 and bytes are in `evidence/source-inventory.json`; copied original GLBs and source code are checkpointed. Man: `dad8fa3ca2bc7760892f9ff47f544941179e50acb2aa772cf9f035154a37fc58`, 493,196 bytes. Woman: `a6522fe53d15de21130a957d1bf2b8a9a58d4e4e9a12af646645b667a9bb2d17`, 1,491,780 bytes. Existing GLB/project files do not document the crowd's upstream author/licence. User-directed existing-project reuse is performed; no CC0/public-redistribution claim is made. Stage and stall assets are generated by the preserved project Blender script. Existing Poly Haven CC0 architectural texture resources stay packed/shared. No new external scan is introduced.

## Comparison evidence

I — BEFORE wider world vs terrace architecture ONLY, with original crowd/props unchanged. II — Same terrace and lighting with old placeholders vs exact actual-website crowd. III — Active source road-case and archived table proposals vs the explicitly rejected old invented counter mockup. These responsibilities remain separated in scenes, gallery and PDFs.

Still frames use exactly matched camera poses/lenses, 1280×720 desktop or 576×1024 portrait, EEVEE 16 samples, same world/exposure/look/fog and five support lights at 0 W. Metadata carries exact positions, rotations, lens, image hashes and master hash. All planned matched captures are present. The screenshots are authentic OFFLINE BLENDER renders. Historical actual-browser Aftermovie arrival/playback captures are provided separately; they verify the original visual source and are labelled historical, not fresh deployed-parity evidence. No new website/browser capture was made because the prompt prohibited running a server/build or integrating this art.

The original straight 40 s action is sampled into 80 actual EEVEE renders over source frames 1–960, 480×270 at 2 samples, encoded at 2 fps. It is a deliberately coarse offline walking inspection, not real-time gameplay or measured FPS. No motion-generating concept art or interpolation substitutes for rendered geometry. The frame-linked gallery also allows route inspection. Early six 8-sample walk frames and a probe are retained only as unfinished diagnostic history, not the final movie.

## Measured asset budget

Counts below use one consistent evaluated method, including font-derived geometry. That explains the 12-triangle/one-material counting difference from the prior report; preservation hashes confirm the old scene has not changed.

| Scene | Triangles | Mesh/curve owners | Materials | Images | RGBA8+mips estimate |
|---|---:|---:|---:|---:|---:|
| TERRACE BEFORE | 121,332 | 2,822 | 87 | 33 | 138.53 MiB |
| TERRACE ARCH | 127,008 | 2,888 | 87 | 33 | 138.53 MiB |
| TERRACE WEB CROWD | 712,800 | 1,628 | 88 | 33 | 138.53 MiB |
| TERRACE PROPS A | 713,448 | 1,634 | 93 | 33 | 138.53 MiB |

Architecture adds 5,676 triangles. The exact crowd has 639,792 visible triangles versus 54,000 placeholder triangles. Four shared position/normal/uint32-index pose buffers estimate 971,664 bytes, before runtime wrappers and without a claim of exact GPU residency. Source crowd GLBs total 1,984,976 bytes. The eventual website already has those source families, so shared owners are preferable to duplicate downloads. Four instanced crowd draws are a source-backed planning hypothesis; the Blender scene itself has 180 linked actor owners. No runtime draw count or transfer timing was measured here.

Final master: 14,829,066 bytes; SHA-256 `f130611ac54090baf6e25052c222b53a5a243414e1e49686bc1882dc3d6f7f50`. The increase over the historical wider master is 813,978 bytes. The visible triangle increase is material even though shared pose storage and texture costs are small. Wider deployment should be gated on actual runtime testing and screen-size-aware crowd LOD/quality distribution. Possible distant man/woman simplification, pose/material instancing, spatial batching of the 66 new architecture meshes, preserving hero-room silhouettes and baking background details are proposals ONLY; no unapproved LOD or website adaptation has been implemented.

## Validation and inherited limitations

- Archive preservation: PASS, all five prior scene memberships, 3,442 objects, all original material/world/image/mesh-UV/action/transform signatures exact.
- Five candidate/comparison variants retain 17 original lights / 12 active / five optional supports 0 W. No new selected-scene world or exposure setting.
- All 66 new construction meshes: closed manifold components, positive signed volume, face area >1e−9 m², normal/tangent dot <1e−4, tangent length >.999, unit handedness, finite UV/tangents. Original numerical tolerances unchanged.
- Source crowd: exact positions/indices, preserved computed normal frames, uniform scale, 180 exact foot positions/heights/facing; 16,110 actor pairs checked, zero actor/body-architecture overlaps and zero protected narrow-gap violations. Authentic source unwelded boundaries explicitly retained.
- Walking and camera: PASS across ten applicable archive/candidate variants, 960 source frames per variant, floor error <.002 m, protected capsule radius .35 m, straight X=0 and strictly forward Y. Source-audit display scene is correctly outside walking-route scope.
- Original three name artworks: exact three 18-slat shutters / 54 physical slats, roughly 3 cm groove depth, 1 mm seam gaps, one source paint image each; no moved/recolored artwork. Four supporting wall motifs retain their host-ray/projection checks and source material contracts.
- Five recessed shops and stock/counters: preserved. Positive-Y alternative shop approaches pass. Exactly the inherited two negative-Y scooter-side approaches remain blocked; scooters were not moved to manufacture a pass.
- Board, screen, Team RIGHT and Events LEFT sampled visibility: no new first-hit occlusion relative to the BEFORE scene, including both proposal variants.
- Prop proposals: same mesh/material/units as discovered sources, translation only and no crowd intersections. This is geometry parity, not confirmation that the archived table is the intended active steel asset.
- Independent master reopen: all 11 scenes, 33 packed images, no external font dependency, actual crowd and support-OFF assertions.
- Website: all 1,213 protected hashes and current dirty/untracked state unchanged. Typecheck/build/runtime/navigation/device checks were deliberately NOT RUN, because no website changes, installs/builds/servers or runtime integration were authorized.

Initial test runs exposed missing carried-forward art-fixture files and an inactive-scene original-matrix cache in the new prop assertion. Dependencies were restored; the prop assertion now inspects actual evaluated geometry in its own scene. No geometry tolerance was loosened. Initial failure logs and final passing rerun logs remain in evidence.

## Honest art assessment / stop

The elevated views now read as a continuous inhabited roof and surrounding roof/service structures, rather than a floor card with edge trim. Eye-level forward views gain flanking headhouses and peripheral construction without moving the screen. Actual website human silhouettes are substantially more recognisable than the block placeholders, but intentionally almost black, as in the website. Sparse foreground bystanders outside the protected C180 audience remain unchanged archival art. Broad background facade planes, flat-door/service-room simplification, limited top-view interior furnishing, repeated window rhythm and low-sample walk grain remain visible limitations. This is not a photorealism claim or structural design certification.

Recommendation: review the terrace and exact crowd together, with the architecture-only controls. Do not promote to the website yet. Resolve which existing steel rack/table the user means before final furniture adoption. Keep both placement proposals reversible and all previous candidates. Browser/mobile performance, final runtime scene conversion and production deployment remain separate authorized milestones.

## Backup / restoration

New phase folder: https://drive.google.com/drive/folders/1xBAYTo8TNNO8K5zxGggQcbHRNXT6hJDZ

Verified direct master: https://drive.google.com/file/d/1UHSVqqkuA_NM0B6t8eLWTllv0G3wW0lL/view

Source audit: https://drive.google.com/file/d/1P3qoI4msP-HxDn7wtrw_-tyionJpGT6c/view

Final index and receipts are recorded in `checkpoint/FINAL-DELIVERY-VERIFICATION.json` once all final payloads have been uploaded, downloaded back, SHA-256 verified and independently extracted/reopened. The earlier working checkpoint is an explicitly INTERIM safety snapshot, not a substitute for the final complete evidence package. Old backups are untouched. See RESTORE.md and FILE-MANIFEST.json. No off-cloud verification is claimed until the final receipt exists.
