# Gullyverse — No reveal column (revision 02)

Handoff: `WORLD-LANE-ROOFTOP-NO-COLUMN-20261023-02`.

The user requested removal of the reveal column. The large central service-room/reveal block is removed in all three A/B/C scenes. Its roof, water tank, four reinforcing ribs and two attached paste-ups are removed as one dependent group (9 objects). No substitute occluder is added. Below-deck structural support columns are unrelated and remain.

The original master is preserved unchanged (SHA-256 `cc8c52a0a3a4106a2c94a36ec2364778ce5b2d8db6ef1ebabfbb553f38e66056`). The revised editable master is separate and self-contained with 25 packed images. All 1,617 surviving objects retain their meshes, topology, UVs, transforms, materials, camera rig and light parameters; both masters were reopened and compared.

Shops, signboard, Team/right, Events/left, screen, crowd, ramp and original route/camera paths remain where they were. No A/B/C art direction has been selected. No website code, default, deployment or Git history changed.

## Visibility and validation

The roof connection is now open. The screen can be seen earlier: landing 11/15 sampled rays; opening 14/15; final reveal 15/15 in every variant. The unchanged historical survey consequently reports `REVIEW_FAILURES` for its old zero-visible-screen landing condition. This condition is superseded by the explicit removal request; it is not falsely marked passing, and no numerical geometry tolerance is relaxed.

All original 0.35m capsule, floor-height (<0.002m), distant silhouette and sampled camera-path checks continue to pass. The original minimum-width/pinch-point caveats remain: these tests do not certify a 3m-wide route or regulatory accessibility. No runtime or hardware performance certification is claimed.

## Evidence

18 new actual Blender EEVEE Next renders: landing, forward lane walk, rooftop opening, hub, overhead and mobile landing, for A/B/C. Cameras, FOV, resolution, samples, per-variant light settings and exposure match the previous concept. A separate 9-page phone-oriented review PDF includes before/after C opening, updated plan/section and all 18 revised views. An offline full-resolution HTML gallery, three contact sheets and six matched A/B/C strips are included. Other historical views and the original animatic remain in the previous checkpoint and are not represented as newly rendered here.

## Scope and limitations

This is the same Blender concept with one obstructing structure removed, not a website implementation or a broader layout redesign. Crowd, vehicles, shop stock and skyline remain concept proxies; event art remains labelled placeholder. All 1,213 protected WIP source/runtime files remain byte-identical. The existing website stays on `work-in-progress-2027` at `e638140b37045a805b23b4d406d387a8870f8486`.

The new Drive subphase is `02-No-Reveal-Column` under the existing world-concept phase; older checkpoints are untouched. Restore from the new source/review ZIP to open the revised master directly. SHA-256 manifests and a download-back verification receipt accompany the checkpoint. No commit, push, merge, deployment or automatic next phase.
