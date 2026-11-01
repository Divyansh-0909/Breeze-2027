# Gullyverse — Rev05B real open shops and filled-center audience

Task date: 25 October 2026. Report built 2026-10-26T06:32:48.470069+00:00.

Handoff: **WORLD-OPEN-SHOPS-FULL-CENTER-CROWD-20261025-05B**.

**Implemented private Blender correction; ready for user visual review.** This completes the implementation that was blocked in Rev05A, while preserving that partial handoff as history. No A/B/C aesthetic selection, final production acceptance or website change is implied.

## Starting baseline and explicit authorization

Direct input is the exact protected Rev05A master, included as `source/baseline/Rev05A.blend`, SHA-256 `b143dc873b9566217301119f97cf349a73db58d7fdc1591c451e2daf7000ee8c`. This builds on Rev05A, not the obsolete Rev04 crowd. The full approved prompt is preserved in `source/baseline/REV05B-APPROVED-PROMPT.txt`. It explicitly authorizes genuine cavities in the five solid shop hosts, necessary local trim/backplane changes, side-wall stock, minimal interior light support, a filled crowd center, scattered wings and sparse people beyond the navigation board.

Final editable master: `source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend`, SHA-256 `8fbfbfb1c69bd0daefb5690c935c8317ed3516ab0e1af07e8a9bd371747ec5ff`. Its packed images and builtin/packed font dependencies permit independent opening without older cloud directories.

Protected WIP remains `work-in-progress-2027` at `e638140b37045a805b23b4d406d387a8870f8486`. All 1,213 protected file hashes and Git status match the starting state. Existing uncommitted canal-study work and original dirty navigation checkout are untouched. No reset, clean, commit, push, merge, deployment or public/WIP default change occurred. Rev05A, Rev04 and their verified checkpoints remain intact.

## Genuine open-shop interiors

The five stores (left Y-25,-7,+2; right Y-16,-7) originally were solid eight-vertex/six-face building blocks with decorative facade layers. The correction replaces only five host meshes and five trim meshes with explicitly constructed closed, manifold cavity topology. This is local retopology, not Boolean union, DoubleSide rendering, a painted black hole or hidden intersecting stock. All external building bounds are exact (maximum measured error 0.000000000m), and all closed stores, shutters, signs and positions remain protected.

Each final recess is **6.2m wide, 4.4m deep and 2.85m high**, from |X|4.0 to8.4, with an inner floor at the store's local ground +0.015m. The front trim has a slightly larger through-opening, avoiding duplicated coplanar interior skins. The existing wooden back lining moves to |X|8.32. Host depth behind that lining remains solid. Existing varying lane elevations and shop thresholds are preserved as concept-level steps, not certified accessible shop entrances.

The first 3.8m-deep proposal failed the 0.35m doorway survey because front stock was too close to the route. That failed log and draft images are retained. Increasing only the internal depth to4.4m places the first stock at least0.675m behind the opening and lets a visitor pass around the fixed counter. No collision tolerance was lowered. An initial too-tight diagnostic camera crop is also archived; final equal-camera sections were widened/rotated to show both side walls and the counter.

All **45 shelf boards and 180 cartons** are retained in 15 complete rigid rack assemblies. Two banks line one side wall and one lines the opposite side wall in each store. Rotation/translation preserves every carton-to-shelf offset and original mesh/UV. All stock is inside the actual cavities, clear of masonry and the fixed counters; minimum side-wall clearance is about0.07m. Carton bottoms remain on shelf tops within0.00002m. Individual stock visibility is measured over several actual lane angles and inside diagnostics; it does not mean every carton is simultaneously visible from one point.

All five counters and the DJ tabletop/legs have exact unchanged matrix and mesh/UV hashes. Their contents and every non-target prop are protected by the full preservation audit, not merely by a list of counter names.

| Shop | Stock visible from union of lane probes | Tested approaches | Inherited blocking prop |
|---|---:|---|---|
| Left Y-25 | 45/45 | negative-Y: PASS, positive-Y: PASS | none |
| Left Y-7 | 45/45 | negative-Y: PASS, positive-Y: PASS | none |
| Left Y+2 | 45/45 | negative-Y: BLOCKED, positive-Y: PASS | Scooter steering.002 |
| Right Y-16 | 45/45 | negative-Y: PASS, positive-Y: PASS | none |
| Right Y-7 | 45/45 | negative-Y: BLOCKED, positive-Y: PASS | Scooter steering.001 |

Every shop has at least one tested clear approach. The negative-Y approach to left Y+2 and right Y-7 remains blocked by the original scooter steering geometry. The positive-Y alternatives pass. Full blocked-ray samples/object IDs remain in `shop-geometry-stock-validation.json`; these failures are not omitted or described as universally clear access. No scooter/counter was moved to force a pass.

## Crowd center, irregular wings and density gradient

The revised deterministic composition uses seed **2026102506**. It keeps a coherent screen-facing viewing mass but removes the permanent3.3m division. Physical body bounds now stay at least0.45m from the straight X=0 camera route only until Y36.95. The exact original camera action ends at Y36.5. Beyond that endpoint, the center is occupied: **A16 / B18 / C16** spectators now stand within the old central3.3m gap above Y37. The same0.35m camera-capsule threshold remains in effect. This is a feasible static layout; no collision disabling, per-load randomness or unimplemented crowd-parting trick is used.

Shared population: six sparse spectators just beyond the board, fourteen transition viewers, thirty-six mid-zone viewers, ninety-two dense main viewers and fourteen in each outside wing. B retains eight scene-specific extras; C retains four. Nine fixed lane/cypher people are unchanged and excluded from the main-audience totals. Whole-body source meshes are reused with linked data, inherited garment/pose variation and object-local overrides. The added32 shared actors create256 linked body-part instances; existing1,248 audience body-part transforms change.

The wings are sampled from asymmetric cartesian clusters and loose rectangular spillover domains rather than fixed radii or concentric arc tails. Small heading variation preserves screen-facing intent. Crowd remains on the roof, in front of the screen and clear of props and destination routes. The low/medium/dense gradient is measured in `density-table.json`, `density-zones.csv`, occupancy maps and the density chart. Those maps are foot-center distributions, separate from actual body collision checks and not an art-quality score.

## Lighting exception, isolated from geometry

The initial unlit cavity preview left stock dark. The final candidate adds **one shadowed45W rectangular area source inside each store** (five total), placed below the ceiling with its whole emitter inside the cavity. No visible fixture is added. All original12 street/board/scene lights, their transforms and values, all world/sky/fog/exposure settings and materials remain exact. The optional sources light stock and the immediate opening; they are not a global brightness change. New cavity walls are closed and tested; shadowing is retained rather than accepting light leaking through solids.

The separate `lighting-inspection` images hold the final geometry, pose, exposure and samples fixed and toggle only those five energies0W/45W. The delivered master retains45W; no diagnostic state is saved back into it.

| Camera | Mean display luma, off | Mean display luma, on | Software still time off / on |
|---|---:|---:|---:|
| 21-shop-left-25 | 0.144 | 0.197 | 15.88s / 16.85s |
| 31-shop-inside-1 | 0.057 | 0.214 | 16.13s / 14.53s |

Luminance is measured from the same display-image crop, not physical lux or albedo. Still-render durations are diagnostic software wall times affected by caching/workspace load, not laptop/mobile FPS. Five extra authoring shadowed lights have a genuine future web cost; bake or budget equivalent interior lighting during any separately approved conversion. No production lighting architecture is changed here.

## Rendered review evidence

`review/Gullyverse-Rev05B-Review.pdf` is the **14-page phone-friendly review**. `review/Gullyverse-Rev05B-Full-Comparisons.pdf` contains **80 pages**, including all75 matched pairs /150 final original PNGs. `GALLERY.html` exposes all full-resolution files. A/B/C each receive five shop lane angles, five inside diagnostics, five camera-clipped sections, eye/plan/hub views, both outside wings, the sparse board-forward group, center approach and desktop/mobile context.

All pairs use identical actual camera position, rotation, focal length, sensor width, perspective/orthographic type, ortho scale, clipping, dimensions, exposure/view transform and EEVEE quality. Desktop1200x750; portrait540x960;16 samples. DPR is not applicable to offline Blender. The authorized interior lights are the intentional local before/after exception; original global/street lighting is identical. Every original24 camera and action is preserved;15 extra diagnostics are added.

Section views use the same near-plane camera cut above local Z+2.7m, not hidden or removed meshes. Inside-before viewpoints are explicitly diagnostic because the old host was solid. Rejected3.8m drafts and cropped early sections are excluded from final pairs and retained in the technical evidence. PDF JPEG embedding keeps the package phone-friendly; PNGs remain untouched. All evidence is from the actual Blender renderer, not generated concept art, a browser capture or runtime movie playback.

The existing40-second straight action is unchanged; this phase validates all frames and provides matched walking-context stills. No new animated crowd, full Aftermovie playback or fresh motion video is claimed.

## Validation and preservation

- Five hosts and five trims: closed manifold edges, positive volumes, nonzero face areas, finite UVs and tangent frames; orthogonal unit normals/tangents and valid bitangent signs. Actual front/side/floor/ceiling hits face the cavity correctly. Stock stays within cavities and behind openings; relative rack transforms and shelf support are checked.
- Actual audience: 188 actor instances /1504 parts across all variant collections together, 17,578 actor pairs, zero body triangle overlaps and zero person/prop overlaps. This stricter union check uses actual geometry, not foot centers alone. All feet stay within0.002m of the roof, all headings within12 degrees of screen-facing intent. Board rays from landing/arrival cameras have no new crowd occlusion.
- All960 frames in each A/B/C: X=0, monotonic forward Y, unchanged heading/lens/eye height and no hits within the existing0.35m camera test. The original straight entry/screen, Team-right and Events-left surveys pass with the original0.002m floor tolerance. Shop-side approach failures above remain disclosed separately.
- Exact preservation: all original cameras/actions, all non-target mesh/UV/material state/transforms, all original light values, world/node settings and packed image payload/color spaces. Only ten local shop meshes, five backplane positions,225 stock objects, audience placement/32 new actors, five interior lights and diagnostic cameras change. Banner stays absent; screen/nav/scaffold/destination geometry stays fixed.
-24 images remain packed; builtin/packed font dependencies are available. External source/license inventories and reproducible scripts are included. Independent restoration and full remote download-back verification are recorded in post-upload checkpoint receipts.

These are concept geometry/clearance checks, not regulatory accessibility, current live-site collision certification or physical-device acceptance. No website code changed, so builds/TypeScript/browser playback were not represented as newly implemented or retested website work.

## Asset costs and artistic limitations

| Variant | Audience | Evaluated triangles | Triangle delta | Mesh/converted-curve objects |
|---|---:|---:|---:|---:|
| A | 144 -> 176 | 73,624 -> 83,564 | +9,940 | 2,451 |
| B | 152 -> 184 | 76,758 -> 86,698 | +9,940 | 2,546 |
| C | 148 -> 180 | 74,828 -> 84,768 | +9,940 | 2,485 |

Compressed editable source is4,002,949 bytes before and4,035,714 bytes after (+32,765 bytes). That is the Blender container, not a measured runtime GLB transfer. No new texture images or PBR maps.24 packed images remain approximately95.86MiB estimated unique RGBA8+mips in the authoring study. Lights increase12 to17. These are offline scene/object counts, not runtime draw calls or web texture residency. A future implementation needs real instancing/batching/LODs and a deliberate local-light budget; no full-world duplicate, GLB rollout or hardware extrapolation is introduced here.

The audience remains static low-detail proxies with repeated inherited gesture templates. Shop plaster, box stock, typography and broad architectural masses remain concept-quality. The new work solves spatial organization and real interiors, not final realism. It preserves the intended centered board dominance and leaves all A/B/C artistic selection to the user. The two scooter-side access limitations remain, with passing alternatives.

## Checkpoint and decision

New task folder: https://drive.google.com/drive/folders/1g807WYu5ZSlfaoLUXnQK4OFvzpHlXW7F

Review folder: https://drive.google.com/drive/folders/1sRMTPGiTS8FYTVTg8wr3dj1Ya_4__PkM

Checkpoint folder: https://drive.google.com/drive/folders/1RBUH2fDcXWhGUn32txMNqo6ejWKwFz7p

Archives include packed editable Rev05B and exact Rev05A input, complete current scripts, source/license references, reports/PDFs, all final/diagnostic PNGs, metadata, hashes and restoration instructions. `ARCHIVE-INDEX.json` lists every complementary archive. Post-upload `EXTERNAL-VERIFICATION.json` records parent/size/full authenticated download-back SHA-256 and independent extraction/open results. Earlier checkpoints are not overwritten; this Blender checkpoint is not falsely called a new full website backup.

**Recommendation: review Rev05B's shop organization and crowd composition.** Do not choose A/B/C or begin high-fidelity look-dev, website integration, commits, pushes, merges or deployment automatically.
