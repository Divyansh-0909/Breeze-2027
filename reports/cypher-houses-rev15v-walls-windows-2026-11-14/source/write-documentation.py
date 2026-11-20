from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[1];repo=R.parents[1];U3=R.parent/'navigation-board-rev15u3-larger-english-text-2026-11-14';b=json.loads((R/'evidence/build-verification.json').read_text());ex=json.loads((R/'evidence/export.json').read_text());folders=json.loads((R/'evidence/drive-folders.json').read_text());read=lambda f:json.loads((R/f'evidence/{f}.json').read_text());lib=read('library-upload');runtime=read('runtime-upload');pdf=read('pdf-upload');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in [lib,runtime,pdf]:assert row['status']=='PASS' and sha(Path(row['path']))==row['sha256']
dep=json.loads((U3/'delivery/Dependency-Index.json').read_text());dep['recoverySequence'].append('Reconstruct V from restored U3 with V build.py --restore, authored maps and the architecture plan');dep['currentArchitectureComponent']=lib;dep['currentArchitectureRuntime']=runtime;dep['previousU3SourceCheckpoint']={'file':'dependencies/Breeze-Rev15U3-Larger-English-Navigation-Checkpoint.zip','bytes':4348284,'sha256':'3a5185aa86a4bb786f621082cc0cee42f2f9db7c2c30b7f9f21e7f05a8e8fc23','id':'1KkMBweqXs7Kq9YPvHOnpQ-BP3JBt523N','status':'PASS'}
(R/'delivery/Dependency-Index.json').write_text(json.dumps(dep,indent=2)+'\n');shutil.copy2(U3/'delivery/Base-Rev15T2-Native-Parts.json',R/'delivery/Base-Rev15T2-Native-Parts.json');(R/'dependencies').mkdir(exist_ok=True);prior=U3/'delivery/Breeze-Rev15U3-Larger-English-Navigation-Checkpoint.zip';assert prior.stat().st_size==4348284 and sha(prior)==dep['previousU3SourceCheckpoint']['sha256'];shutil.copy2(prior,R/'dependencies'/prior.name)
report=f'''# Rev15V — Cypher house walls and windows

The cypher houses now use restrained weathered pale plaster, local render loss with small brick exposures, damp bases and runoff aligned to their actual window sills. Frames and shutters use worn muted paint; glazing has dirt at its edges. Fifty-nine eligible windows are updated, with 45 grilles, 59 projecting sills and 18 small rain hoods, batched into nine new objects. The existing house openings, topology and transforms are retained.

The Events house keeps warm masonry below its posters and pale plaster above. All eight existing poster artworks, frames, sizes, positions and the heading are unchanged; they remain the earlier clearly labelled event-art placeholders. The entire R2 Team building, upper windows, black wall, lights and all eight mural states are protected. A per-face spatial exclusion also protects Team surfaces in the shared structural mesh. New runtime and native component geometry contains no Team-region faces.

The references are real Delhi façades from [Outlook Traveller](https://www.outlooktraveller.com/celebrating-people/archeologist-anica-mann-founder-of-delhi-houses) and [LBB's Chunnamal Haveli article](https://lbb.in/delhi/lala-chunnamal-ki-haveli-chandni-chowk-forgotten-bit-history/). Source URLs, original image bytes, dimensions and hashes are retained in references/source-images.json. Photographs are research references only; all 31 material maps are authored procedural assets. No Firecrawl was used.

Native master: `{b['editedMaster']}`, {b['editedBytes']:,} bytes, SHA-256 `{b['editedSHA256']}`. Active scene: `{b['scene']}`. There are 56 scenes, retaining all 55 prior scene memberships, and 140 packed images with no linked libraries.

Verification passed: fresh native open; original geometry, old UVs, colours, transforms and unedited face materials; all eight exclusive Team mural states; all eight Events posters; new geometry outside the Team region; actual source reconstruction from the verified restored U3 base; a separate fresh opening of that reconstruction; all authored packed texture hashes. Native night captures use the original lights/world/exposure. The two neutral captures use temporary inspection lighting that is never saved to the master.

The runtime architecture asset is {ex['runtimeBytes']:,} bytes and comprises 61 changed-surface/detail objects (99 glTF material primitives). Its isolated Chromium review loads all 31 textures and has no JavaScript, request or GL errors. This partial replacement asset excludes unchanged surfaces, poster art and Team geometry; it is not a complete standalone world and is not an overlay to place on top of the old shell. Production integration must replace corresponding original surface primitives. No full-world frame-rate claim is made.

Navigation retains the English-only 12% larger, vertically centred lettering from U3, its arrows and Accommodation. The digital sponsor display, crowd, road and potholes, ground-level railing removals, original movement/input/rendering code and saved lighting are unchanged. Full-world production website integration remains pending. No commit, push or deployment was made.

[Four-page PDF review]({pdf['url']}) · [Versioned Drive phase]({folders['phase']['url']}) · [Native architecture component]({lib['url']}) · [Runtime architecture]({runtime['url']}). See RESTORE.md and delivery/Dependency-Index.json for complete native reconstruction. The source checkpoint embeds the verified U3 source checkpoint and all new V source/maps; immutable T2 parts and T3/U1 packed native dependencies are reused with IDs and checksums. Earlier backups and sharing are preserved.
'''
(R/'REPORT.md').write_text(report)
restore='''# Restore Rev15V

Use Blender 4.3.2. Download the source checkpoint parts and Checkpoint-Index.json. Reassemble with the separately supplied source/restore-checkpoint.py helper, which checks every part, the whole ZIP, CRCs and every payload hash. Extract the verified ZIP to a new repository directory. Do not overwrite a different working copy.

The V checkpoint embeds the verified U3 source checkpoint in this report's dependencies directory. Extract that embedded ZIP at the same repository root to restore all prior T3/U1/U2/U3 recovery modules, fingerprints and required proofs under their original report paths. Verify its SHA-256 against delivery/Dependency-Index.json. It contains no credentials or dependencies.

Download all thirteen T2 native parts, the T3 packed ground delta and the U1 packed bilingual styling delta using IDs and checksums in delivery/Base-Rev15T2-Native-Parts.json and delivery/Dependency-Index.json. From the extracted repository root, run with your actual paths:

```bash
python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-master.py /downloads/base-parts /output/T2.blend --index reports/cypher-houses-rev15v-walls-windows-2026-11-14/delivery/Base-Rev15T2-Native-Parts.json
blender -b --python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-native.py -- --base /output/T2.blend --delta /downloads/Rev15T3-Rebuilt-Potholes-Additions.blend --output /output/T3.blend
blender -b --python reports/navigation-board-rev15u-highway-green-2026-11-13/source/restore-native.py -- --base /output/T3.blend --delta /downloads/Rev15U1-Bilingual-Highway-Sign-Styling.blend --output /output/U1.blend
blender -b --python reports/navigation-board-rev15u2-english-centred-2026-11-14/source/build.py -- --restore --base /output/U1.blend --output /output/U2.blend
blender -b --python reports/navigation-board-rev15u3-larger-english-text-2026-11-14/source/build.py -- --restore --base /output/U2.blend --output /output/U3.blend
blender -b --python reports/cypher-houses-rev15v-walls-windows-2026-11-14/source/build.py -- --restore --base /output/U3.blend --output /output/V.blend
```

Each builder refuses to overwrite an existing output. V checks the exact U3 scene fingerprint before editing, validates the authored map hashes before packing, preserves every unedited face material and original shape/UV/colour/transform, and matches the V scene fingerprint before saving. The complete V master has all 56 historical/current scenes and packed resources. Actual reconstruction from the prior phase's restored U3, followed by an independent fresh opening, passed; whole-file checksums can differ after Blender serialization. Check evidence/restore-check.json, evidence/restored-fresh-open.json and the original master hash in evidence/build-verification.json.

Rev15V-Cypher-Houses-Architecture-Update.blend is a compact native library containing changed surface faces and the new window-detail batches only. It is useful for editing these assets and is not the complete master. Never append it as a visible overlay over the old faces: reconstruct V with the commands above instead. The full working master is available locally through delivery/Gullyverse-Rev15V-Weathered-Cypher-Houses.blend; its complete externally recoverable equivalent is the verified base-and-source chain above.

For the isolated runtime review, download the verified architecture GLB to this report's viewer/houses.glb, serve viewer with a local HTTP server and open index.html. The Three.js files/license are included. This is a partial changed-surface material review with neutral diagnostic light; unchanged balconies, Events posters and Team surfaces are intentionally absent from that export. Use the PDF's native full-environment captures to assess those surrounding elements. Runtime integration must replace the original selected surface primitives, not layer this mesh on top of them. Full-world production integration remains pending.

The four-page PDF contains sourced reference images with links, full native neutral inspection views and an Events before/after pair under identical saved night lights. Inspection lights were never saved into the native master. All user-facing visual review remains in the PDF.
'''
(R/'RESTORE.md').write_text(restore)
pointer=f'''# Current cypher houses and windows

**Rev15V / 14 November 2026** updates cypher house walls and 59 eligible windows with weathered pale plaster, sill runoff, worn frames, dirt-fringed glazing, grilles, projecting sills and small rain hoods. The Events wall keeps warm masonry and all eight posters with their artwork, frames, sizes and positions unchanged. The entire Team building, including upper windows and all eight mural states, is unchanged.

The latest full native scene is `REV15V / Weathered cypher houses and windows` in [the packed working master](../reports/{R.name}/delivery/Gullyverse-Rev15V-Weathered-Cypher-Houses.blend). It preserves 55 earlier scenes (56 total), the larger English-only U3 navigation, sponsor LED, rebuilt road/potholes, crowd, lighting and movement flow. Start further whole-world art work from V. Full-world production website integration remains pending.

[PDF review]({pdf['url']}) · [Drive phase]({folders['phase']['url']}) · [Implementation report](../reports/{R.name}/REPORT.md) · [Native restoration](../reports/{R.name}/RESTORE.md). New source/maps and the verified U3 source recovery package are retained in the versioned checkpoint; reused complete native base dependencies are indexed. Native fresh-open, actual reconstruction and browser material-load checks pass. User visual review is pending.
'''
(repo/'docs/gullyverse-cypher-houses-current.md').write_text(pointer)
handoff=repo/'docs/gullyverse-consolidated-handoff-current.md';old=handoff.read_text();intro=f'''The latest native scene is **14 November 2026 / Rev15V**. Cypher house walls and windows have reference-informed weathering and physical window details. The whole Team building and all eight Events posters are unchanged. Navigation retains the larger English-only centred U3 lettering. Road, crowd, movement and saved lighting remain unchanged. See the [current house review and recovery checkpoint](gullyverse-cypher-houses-current.md). Full-world production integration remains pending. User visual review of V is pending.\n\n'''
if intro not in old:handoff.write_text(old.replace('# Current consolidated handoff\n\n','# Current consolidated handoff\n\n'+intro,1).replace('The latest native scene is **14 November 2026 / Rev15U3**','The preceding native scene was **14 November 2026 / Rev15U3**'))
events=repo/'docs/gullyverse-events-current.md';old=events.read_text();intro='''The current full environment is **Rev15V / 14 November 2026**. The Events house now has updated warm masonry and upper plaster/window detail while all eight existing posters, their frames, heading, size and placement are preserved. The Team building is unchanged. See the [current cypher houses review](gullyverse-cypher-houses-current.md) for the PDF, verification and complete recovery chain. Start further whole-world work from V; the Rev15N record below is historical.\n\n'''
if intro not in old:events.write_text(old.replace('# Current Events place and full environment\n\n','# Current Events place and full environment\n\n'+intro,1).replace('The current full environment is now [Rev15O]','The following historical full-environment revision was [Rev15O]'))
print('DOCUMENTATION_READY')
