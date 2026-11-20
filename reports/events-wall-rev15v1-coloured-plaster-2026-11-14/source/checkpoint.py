from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[1];repo=R.parents[1];V=R.parent/'cypher-houses-rev15v-walls-windows-2026-11-14';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((R/'evidence/build-verification.json').read_text());receipts=json.loads((R/'evidence/upload-receipts.json').read_text());pdf=next(r for r in receipts if r['name'].endswith('.pdf'));phase='https://drive.google.com/drive/folders/1iQDs_aQPwDNAdINGp47EpDa_hDwS7jcf'
for key in ['fresh-open','restored-fresh-open','restore-check','export','captures','pdf']:assert json.loads((R/f'evidence/{key}.json').read_text())['status']=='PASS'
assert all(row['status']=='PASS' and sha(Path(row['path']))==row['sha256'] for row in receipts)
shutil.copy2(V/'delivery/Checkpoint-Index.json',R/'delivery/Base-V-Source-Checkpoint-Index.json');shutil.copy2(V/'delivery/Dependency-Index.json',R/'delivery/Base-V-Native-Dependency-Index.json');shutil.copy2(V/'delivery/Base-Rev15T2-Native-Parts.json',R/'delivery/Base-Rev15T2-Native-Parts.json')
(R/'delivery/Dependency-Index.json').write_text(json.dumps({'status':'PASS','basePhase':'Rev15V','baseSourceParts':'Base-V-Source-Checkpoint-Index.json','baseNativeChain':'Base-V-Native-Dependency-Index.json','completeBaseIndex':'Base-Rev15T2-Native-Parts.json','basePhaseURL':'https://drive.google.com/drive/folders/1tQAPv7-tZEQJaplmsw7VKOTIygzt95Zo','newArtifacts':receipts,'restoration':'Recover/extract V source and embedded U3 source; reconstruct T2 -> T3 -> U1 -> U2 -> U3 -> V using V RESTORE.md; then run this V1 build.py --restore from V.','actualV1RebuildAndIndependentFreshOpen':'PASS'},indent=2)+'\n')
(R/'REPORT.md').write_text(f'''# Rev15V1 — Events coloured house plaster

The Events L2 house wall now uses dusty terracotta painted plaster instead of a brick pattern. All brick colour courses, exposed-brick patches and mortar normal relief are removed from the new finish; subtle fine render grain, damp base and sill runoff remain. Exactly 3,151 selected wall faces in three objects receive the new material. Geometry, all UVs, colours and transforms remain unchanged.

The eight Events posters, artwork, frames, heading, size and placement are exact. Window details, the whole Team building and all eight mural states, other houses, navigation and sponsor LED, road, crowd, saved lighting and original movement code remain unchanged. Native fresh-open, actual reconstruction from restored V, independent restored-file opening and authored packed-image checks passed. The runtime GLB contains only the three changed wall-surface objects; it replaces their original primitives and is not a visible overlay.

The packed working master is `{b['editedMaster']}`, {b['editedBytes']:,} bytes, SHA-256 `{b['editedSHA256']}`. It has 57 scenes, preserving all 56 earlier memberships. The complete externally recoverable master uses the verified V source/native chain plus the V1 source and maps. See RESTORE.md and the dependency indexes.

[Two-page PDF review]({pdf['url']}) includes neutral-light colour inspection and same-camera original-night-light before/after. Inspection lighting was never saved. [Versioned Drive subphase]({phase}). No website code, commit, push or deployment. Full-world production integration remains pending. The subsequent requested entrance gate is a separate subphase.
''')
(R/'RESTORE.md').write_text('''# Restore Rev15V1

Use Blender 4.3.2. Verify/extract this checkpoint ZIP (every payload hash is in PAYLOAD-SHA256.json). Download the two verified V source checkpoint parts listed in delivery/Base-V-Source-Checkpoint-Index.json. Reassemble them with this source/restore-checkpoint.py helper using --index delivery/Base-V-Source-Checkpoint-Index.json. It verifies both part hashes, the combined ZIP, CRCs and every payload hash. Extract V at the same repository root, then extract its embedded verified U3 source ZIP at that root.

Follow the recovered V RESTORE.md to obtain the thirteen immutable T2 base parts and T3/U1 native deltas, and reconstruct T2 -> T3 -> U1 -> U2 -> U3 -> V. Those file IDs, sizes and checksums are also preserved here in Base-V-Native-Dependency-Index.json and Base-Rev15T2-Native-Parts.json. Earlier verified assets are reused, not overwritten.

From the extracted repository root:

```bash
blender -b --python reports/events-wall-rev15v1-coloured-plaster-2026-11-14/source/build.py -- --restore --base /output/V.blend --output /output/V1.blend
```

The builder checks the V scene fingerprint, validates and packs all three new maps, preserves every face material outside the L2 wall selection and all original shape/UV/colour/transform data, and matches the original V1 fingerprint before saving. Actual reconstruction from the previously restored V and an independent fresh opening passed. Blender file serialization can change whole-file hashes while scene content remains identical. The complete restored master has 57 scenes and all resources packed.

The small native component and GLB contain changed wall surfaces only, with no Team or poster geometry. Do not place them on top of the old surface faces. They are authoring/runtime replacement components; restore the complete native scene with the command above. Full-world production website integration remains pending.
''')
intro=f'''**Current Events finish: Rev15V1 / 14 November 2026.** Dusty terracotta painted plaster replaces the Events house brick pattern, including mortar relief and exposed-brick patches. All eight posters, frames, heading, size and position are unchanged. The whole Team building is untouched. [PDF review]({pdf['url']}) · [Native recovery and checkpoint]({phase}). The current full native scene is Rev15V1 with 57 scenes; production website integration remains pending. The entries below are historical.\n\n'''
for name,title in [('gullyverse-events-current.md','# Current Events place and full environment'),('gullyverse-cypher-houses-current.md','# Current cypher houses and windows')]:
 p=repo/'docs'/name;t=p.read_text()
 if intro not in t:p.write_text(t.replace(title+'\n\n',title+'\n\n'+intro,1))
p=repo/'docs/gullyverse-consolidated-handoff-current.md';t=p.read_text();line='The latest full native scene is **Rev15V1 / 14 November 2026**: Events now uses coloured plaster with no brick pattern, preserving all posters and the whole Team building. See [current Events](gullyverse-events-current.md). The newly requested cypher entrance gate is the following subphase. Full-world production integration remains pending.\n\n'
if line not in t:p.write_text(t.replace('# Current consolidated handoff\n\n','# Current consolidated handoff\n\n'+line,1).replace('The latest native scene is **14 November 2026 / Rev15V**','The preceding native scene was **14 November 2026 / Rev15V**'))
files=[]
for group in ['source','evidence','renders','review','textures']:
 files.extend(p for p in (R/group).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.log','.lock'])
files.extend(p for p in (R/'delivery').iterdir() if p.is_file() and p.suffix in ['.json','.glb','.blend'] and not p.is_symlink());files.extend(R/f for f in ['REPORT.md','RESTORE.md']);files.extend(repo/f for f in ['AGENTS.md','docs/gullyverse-events-current.md','docs/gullyverse-cypher-houses-current.md','docs/gullyverse-consolidated-handoff-current.md']);files=sorted(set(files));rows=[{'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files];out=R/'delivery/Breeze-Rev15V1-Events-Plaster-Checkpoint.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,str(p.relative_to(repo)))
 z.writestr('PAYLOAD-SHA256.json',json.dumps(rows,indent=2)+'\n')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for row in rows:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
assert out.stat().st_size<12*1024*1024
(R/'delivery/Checkpoint-Index.json').write_text(json.dumps({'status':'LOCAL_VERIFIED','file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'parts':[{'index':1,'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'status':'LOCAL_VERIFIED'}],'payloads':rows,'nativeRestoreTest':'PASS','baseDependency':'Verified V source/native recovery chain, indexed in included delivery files'},indent=2)+'\n');print(json.dumps({'status':'PASS','bytes':out.stat().st_size,'sha256':sha(out),'payloads':len(rows)}))
