from pathlib import Path
import json,hashlib,statistics,datetime
O=Path(__file__).resolve().parents[1]
read=lambda s:json.loads((O/s).read_text())
p=read('evidence/preservation-audit.json');a=read('evidence/body-overlap-validation.json');s=read('evidence/shop-geometry-stock-validation.json');l=read('evidence/layout-validation.json');b=read('evidence/scene-budget-final.json');w=read('evidence/website-preservation.json');r=read('evidence/render-manifest.json');v=read('evidence/review-build.json');f=read('checkpoint/drive-folders.json')
assert all(x['status']=='PASS'for x in [p,a,s,l,w,v]);assert len(r)==60
times=sorted(x['seconds']for x in r if x['edition']=='off')
cost={'freshSoftwareStillCount':len(times),'medianSeconds':statistics.median(times),'p95Seconds':times[int(.95*(len(times)-1))],'scope':'Offline EEVEE software wall time; not browser frame time, draw calls, physical GPU FPS or mobile certification.'}
(O/'evidence/offline-render-costs.json').write_text(json.dumps(cost,indent=2)+'\n')
report=f'''# Gullyverse Rev05C — optional shop supports OFF; original-graffiti asset gate

Built {datetime.datetime.now(datetime.timezone.utc).isoformat()}.

Handoff: **WORLD-REV05C-LIGHTS-OFF-GRAFFITI-ASSET-BLOCKED-20261026**.

## Status: PARTIAL — do not mark the combined prompt complete

The user authorized the combined Rev05C prompt on26October2026. Its lighting correction is implemented and validated in a new private Blender derivative. Exact artist-name shutters and style-matched generated supporting graffiti are **blocked on unavailable original artwork**. Authenticated searches found the historical reports, not the actual Chaar Diwari, Ritviz or Neha Kakkar image files. Historical Stage3A.1 reports already document those originals as missing. Local filename searches and specific/generic Drive image-name searches did not recover them. `original-artwork-search-summary.json` preserves the actual results. One malformed early Drive query returned400; corrected supported queries completed and found no originals. This is not a claim that the files do not exist outside currently accessible storage.

The user has been asked for the exact Drive folder or three file links. No artist-name substitute, generic-font replacement, invented license or nonexistent Drive ID was supplied. The authorized image-generation tool `image_gen.imagegen` IS available. It has not been called: the requested style matching requires actual original reference images first. The generated-art inventory is empty. Its technical placement/generation plan is retained separately. No blank source contact sheet is presented as completed artwork.

## Exact baseline and preservation

Input: packed Rev05B `source/baseline/Rev05B.blend`,4,035,714bytes, SHA256 `{p['beforeSHA256']}`. Historical Rev05B/05A/04 assets and checkpoints remain intact. New master `source/Gullyverse-Rev05C-Interior-Support-Off.blend`,{b['masterBytes']:,}bytes, SHA256 `{p['afterSHA256']}`.

Website: branch `{w['branch']}`, HEAD `{w['HEAD']}`. All{w['protectedFiles']} protected hashes and exact Git status match the prior baseline, including existing dirty source/traces and untracked canal-study files. Neither website checkout was edited. No commit, push, merge, reset, branch switch, deployment or public/WIP change.

## Implemented light change

Only `Rev05B shop interior practical -1 -25`, `-1 -7`, `-1 2`, `1 -16`, `1 -7` change energy45W→0W. These are five optional shadowed rectangular AREA supports. Their transforms, sizes, colors, shadow settings and all writable light settings except energy remain identical. They remain clearly tagged as disabled reversible authoring options. No emitter/visible fixture is deleted. The original twelve lights, fluorescent bars, world, ambient, fog, exposure, original materials/emission and image payloads remain unchanged. No compensating helper lighting was introduced.

The derivative contains the exact original geometry/topology/UVs, meshes, object transforms, actions and39cameras. Five new editor-only labels on those optional emitters explain OFF. All five real shop cavities,45shelf boards,180cartons, five counters and unrelated DJ furniture remain unchanged. Crowd counts A176/B184/C180 and all placement/body data are preserved. The full center beyond the original route end, irregular wings, sparse board-side spectators, original board, TeamRIGHT/EventsLEFT, screen,40second X=0walk and absence of the red banner are retained.

## Exact shutter inventory and pending art

There are exactly three eligible CLOSED shutters. No open shop needs to be closed. Planned shared A/B/C mapping:

| Original artist art required | Actual closed shutter | Site location | Status |
|---|---|---|---|
| CHAAR DIWARI | Closed rolling shutter.001 | right Y-25 | source/paint pending |
| RITVIZ | Closed rolling shutter | left Y-16 | source/paint pending |
| NEHA KAKKAR | Closed rolling shutter.002 | right Y+2 | source/paint pending |

Each backing is6.9m wide×2.8m tall and has18physical front slats. The maximum proposed artwork box is6.3m×2.1m, with final size fitted uniformly to the actual source proportions. This is a measured plan, not final artwork acceptance. Exact bounds, centers and null unresolved source IDs/hashes are in `source/artwork/artist-to-shutter-plan.json`. No optional other artist was selected because no further closed shutter exists.

The proposed implementation uses identical worldY/Z artwork projection on object-local material clones for BOTH shutter backing and slats; it preserves original corrugation, grain, roughness and latch, with nonmetallic paint and alpha. It must still be implemented and checked once the originals arrive. No floating decal plane or speculative geometry was added. Supporting art likewise has a source-dependent plan; no claim of model output or original-style match is made. Artist/paint close-ups, source contact sheet, generated image provenance, new wall-art context and readability assessments remain genuinely pending.

## Actual rendered evidence

Phone review: {v['phonePages']}pages. Full A/B/C lighting comparison: {v['fullPages']}pages. Full-resolution gallery:30matched pairs/60PNGs. All five shops, one inside diagnostic, lane-wide landing, mobile portrait, hub and crowd-eye context in each A/B/C. Exact ON PNGs are reused from the verified final Rev05B master and their original hashes checked; OFF is freshly rendered. This avoids relabeling Rev05A solid-shop imagery or pretending new artwork exists.

Every pair matches actual position/orientation, lens, sensor, camera type, ortho scale, clips, dimensions, samples, engine, view transform/look and exposure. Desktop1200×750,portrait540×960,EEVEE16samples. Blender DPR is not applicable. The only scene lighting difference is five optional45W→0W sources. Raw PNGs remain unchanged; PDF embeds JPEG previews for size. These are actual Blender renders, not a browser or image-generated mockup.

The darker interior preserves the user's chosen0W look. Stock remains dimmer, especially at the rear; no exposure boost was used to hide that consequence. The original fixture, threshold and counter make the opening readable in the inspected shop view. Art direction A/B/C and overall final-art acceptance are not selected by Codex.

## Validation and inherited limitations

Fresh preservation, scene-budget, body-overlap, shop-geometry and layout checks pass. Original strict0.35m route clearance and0.002m floor tolerance retained. All960straight-walk frames in each variant pass; Team/Events and entry/screen routes pass. Actual body validation checks188actors/1,504parts and17,578pairs with zero crowd-body/prop triangle overlaps. Cavity manifold/positive-volume, finite UV, tangent and facing checks pass; all45stock objects per shop remain inside and visible from the union of tested lane angles. No shop geometry or collision registry changed.

Inherited negative-Y approaches to LEFTY+2 (`Scooter steering.002`) and RIGHTY-7 (`Scooter steering.001`) remain blocked. Positive-Y approaches pass. Full failed samples retained; no scooter was moved or failure hidden. These are Blender concept surveys, not regulatory shop accessibility or live-site collision certification.

Since no website code/runtime changed, TypeScript/build/browser/map/playback tests are not represented as newly executed work. Existing website assets/navigation/media remain protected through hashes and Git state. Physical laptop/mobile rendering remains unverified. No source-art UI/scene selector is promoted to the website.

## Cost

Runtime geometry/image/material deltas: zero. Offline geometry A83,564/B86,698/C84,768triangles, unchanged. All24images packed; estimated unique RGBA8+mips{b['estimatedUniqueImageRGBA8MipMiB']:.2f}MiB, unchanged.17stored authoring lights/scene; five are0W, leaving12original sources. New master grows{b['masterBytes']-4035714:,}bytes due source metadata/container serialization. Not a measured runtimeGLB payload or draw-call claim.

Fresh software still median{cost['medianSeconds']:.2f}s andp95{cost['p95Seconds']:.2f}s. Cache/load differences prevent interpreting these offline still times as an isolated light-speed benefit. No hardware FPS extrapolation. Paint costs remain unmeasured because no paint images/shaders were added.

## Checkpoint / next step

New phase folder: {f['phase']['url']}

Review: {f['review']['url']}

Checkpoint: {f['checkpoint']['url']}

The checkpoint contains the packed editable0W derivative, exact packed Rev05B baseline, prior source provenance, executable correction/validation scripts, source-art plans, reports,60PNGs, PDFs, checksums and restoration instructions. Full authenticated download-back and fresh extraction/reopen are recorded in separate final receipts. It is a PRIVATE PARTIAL LIGHTING CHECKPOINT, not a complete graffiti delivery or new whole-website backup. Prior website/C9/C8 backups remain independent and unchanged.

Workspace had only128MiB free. Before rendering, a stale temporary fidelity-restore overlay was freshly matched against all545members and11authentic local archives, then only that duplicate extraction was removed.659,493,599verified temporary bytes were released; original project, archives and Drive backups remain intact. The exact audit is retained in evidence.

**Next action: provide access to the three original artist graffiti images.** Continue the same combined Rev05C only after inspecting them; use the available image-generation tool for supporting non-name art, then integrate and produce the outstanding matched art evidence. Do not restart lighting, choose A/B/C, or begin another phase. Combined Rev05C remains PARTIAL/ASSET BLOCKED.
'''
(O/'REPORT.md').write_text(report)
print('REPORT_BUILT',len(report))
