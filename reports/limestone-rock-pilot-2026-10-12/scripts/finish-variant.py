from pathlib import Path
import json,hashlib,html,subprocess,zipfile,posixpath,re,datetime
ROOT=Path.cwd();R=ROOT/'reports/limestone-rock-pilot-2026-10-12';RAW=R/'raw'
def read(p):return json.loads(p.read_text())
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
s=read(RAW/'starting-state.json');groups={}
for label,items in [('existingPilot',s['existingPilotHashes']),('originalAuthoring',s['originalAuthoringHashes']),('productionBaseline',read(ROOT/'reports/stage-2a-asset-pilot-2026-10-11/raw/source-hashes-before.json'))]:
 bad=[p for p,h in items.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h];groups[label]={'checked':len(items),'changedOrMissing':bad,'status':'PASS' if not bad else 'FAIL'}
assert not any(g['changedOrMissing'] for g in groups.values()),groups
assert not subprocess.check_output(['git','diff','--name-only']) and not subprocess.check_output(['git','diff','--cached','--name-only'])
groups['git']={'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'trackedDiff':'empty','commitPushDeploy':'not performed'}
(RAW/'preservation.json').write_text(json.dumps(groups,indent=2))
d=read(RAW/'preview-verification.json');assert d['status']=='PASS';caps=read(RAW/'captures.json');validator=read(RAW/'glTF-validator.json');assert all(v['issues']['numErrors']==0 and v['issues']['numWarnings']==0 for v in validator['results'])
# Standalone authoring instructions beside the new asset, separate from the earlier pilot.
src=ROOT/'assets-source/gullyverse/limestone-pilot';src.joinpath('README.md').write_text('''# Original limestone rock pilot variant

Separate from the original approved rock pilot. Production website, stage, navigation, dimensions, camera and lighting are untouched. This is a limestone appearance/weathering variant, not a permanent environment replacement.

Blender4.3.2 master `quarry-limestone-pilot.blend`; metre units, Blender Z-up/front -Y to glTF Y-up/front +Z, bottom-centre pivot. Retains the first pilot's stratified macro form and adds 34 shallow dissolution pockets/interrupted solution channels. Original pale calcite/mineral maps, not reference-photo textures. Unique UV atlas; source2048/runtime1024. sRGB JPEG base colour; linear PNG tangent +Y normal, AO/roughness/metallic export packing. Metallic0, matte roughness0.82–0.99, normal strength0.58. Three explicit visual LODs and a conservative collision hull. No Draco/Meshopt/KTX2 assumptions.

From repository/package root:

```sh
python3 scripts/blender/limestone_pilot_materials.py
blender --background --python scripts/blender/author_limestone_pilot.py
blender --background --python scripts/blender/inspect_limestone_pilot.py
```

Python needs numpy/Pillow; Blender4.3.2 includes its own numpy. `limestone_pilot_surface.py` reuses the unchanged `rock_pilot_surface.py` morphological field; both source files are provided. Scripts only write dedicated limestone output paths.

Combined `quarry-limestone-pilot.glb` contains all LOD nodes and proxy. glTF does not encode visibility. Select exactly one `Rock_LOD0/1/2` and hide `Rock_Collision`, as the bundled preview does. Separate LOD GLBs are provided; loading all separate files duplicates texture cache entries. No automatic LOD distance policy or production collider integration is included.

After extracting the review ZIP, run `python reports/limestone-rock-pilot-2026-10-12/preview/serve-preview.py`, then open http://127.0.0.1:3002. Existing Hub lighting/exposure and fixed comparison cameras; Original pilot / Limestone pilot controls allow direct comparison. Original GLB is included for this isolated comparison only. Physical laptop/mobile GPU measurements remain unverified.
''')
# Results table uses fresh measurements from this variant, not the preceding task.
table='| Variant | FPS | p50 / p95 / p99 / max ms | Calls | Triangles |\n|---|---:|---|---:|---:|\n'
for w in d['windows']:
 stats=w['state']['current']['stats'];table+=f"| {w['name']} | {w['FPS']:.2f} | {w['p50']:.1f} / {w['p95']:.1f} / {w['p99']:.1f} / {w['max']:.1f} | {stats['calls']} | {stats['triangles']:,} |\n"
R.joinpath('README.md').write_text(f'''# Limestone rock pilot — October 12, 2026

The user approved the first rock pilot and requested a limestone variant. This is a **separate asset and isolated preview**. Neither the original pilot nor the approved production environment is changed. No commit, push or deployment. Starting branch `{s['branch']}`, HEAD `{s['HEAD']}`, empty tracked staged/unstaged diff; prior untracked assets/review evidence remain preserved. [Starting record](raw/starting-state.json), [hash preservation](raw/preservation.json).

## Visual comparison

[Open the browsable gallery](gallery.html). Ten actual Chromium PNGs at original resolution; desktop1366×900 and portrait390×844, effectiveDPR1, FOV58. [Camera/quaternion/lighting metadata](raw/captures.json). Portrait screens are aspect checks, not physical phone benchmarks.

The pale warm-gray/ivory calcite albedo, muted mineral staining, finer chalky normal response, matte roughness and shallow solution pockets distinguish this from the darker first pilot. It retains the first pilot's layered quarry form and anchor. Macro geometric bedding remains the same style; this is a variant, not a new overall quarry silhouette. No external reference-image texels or third-party material images were used. Some long bedding/slab regularity and cap mapping still need any future final-art refinement; this is not a claim of complete photographic realism.

Lighting is the unchanged Hub global configuration: background/fog#737d87 at205–520m; hemi#a9bfd4/#8a8274 intensity1.35; direction[-70,37,-145] #efd0a4 intensity1.35; practical[0,9.75,-67.4] #ffc681 intensity42, range21, decay2. ACES exposure1, sRGB output, shadows disabled. No special light or exposure was introduced for the limestone. The slightly darker/cooler cracks are the material and actual geometry under those lights. The stage-specific global mode was not substituted/tested on this segment.

Fixed medium inspection camera[31,5.6,-98] looking at[46,5,-104], close[41.1,5.4,-103.4] at[45.9,5.4,-104], long[3,7,-87] at[46,5,-104]. Development anchor[47.4,0,-104], yaw−π/2, scale1; the procedural wall stays intact behind the opt-in patch. Existing production cameras/coordinates/bounds/map are untouched.

## Asset files and export

[Editable Blender master](../../assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend), **9,760,728 bytes**; [combined runtime GLB](../../public/models/gullyverse/pilot-limestone/quarry-limestone-pilot.glb), **3,748,024 bytes**. [Asset instructions](../../assets-source/gullyverse/limestone-pilot/README.md), [LOD/anchor manifest](../../assets-source/gullyverse/limestone-pilot/asset-manifest.json), [asset inventory, hashes and texture specifications](raw/asset-inventory.json).

Blender4.3.2, original metre-scale closed surface, editable100,992-triangle master; runtimeLOD0 **32,616**, LOD1 **10,440**, LOD2 **2,820** triangles; proxy12. BlenderZ-up/front−Y→glTFY-up/front+Z. Approx12.075m wide×10.017m tall×4.106m deep. Unique frontUVs, lower-density caps, exported normals/tangents. Three explicit LODs share one visual PBR material/three maps in the combined GLB. Source maps2048px, runtime1024px baseJPEG/normalPNG/packedORMPNG. Estimated decoded RGBA8+mips **16MiB** per limestone material set, not driver VRAM measured. No compression decoder/runtime dependency was added. The old2MB experimental transfer target is still not met; file size is smaller than the first pilot4,127,092B, but this does not establish faster physical rendering.

The editable source and separateLOD/proxy GLBs are provided. Hide all but one LOD and the proxy explicitly; visibility is not encoded by glTF. Shared-cache ownership is preserved with the original unchanged `BlenderAsset` infrastructure; no production cache management changes.

## Verification

- Fresh Blender master reopened; all runtime vertices lie inside the proxy, signed volume positive, correct units/object scale, UVs and eight packed maps present. [Inspection](raw/master-inspection.json).
- All five GLBs pass Khronos validation with **zero errors/warnings**. [Validator results](raw/glTF-validator.json). A missing earlier temporary validator was reinstalled in `/tmp` only; project dependencies were not modified.
- Real isolated raycast succeeds. Shader preparation and six covered warm draws precede reveal. Browser captures showed no broken materials/UVs; this is settled-frame evidence, not a certified physical first-render hitch test.
- Ten alternating limestone mount/unmount cycles after warming both comparison assets plateau at **7 geometries / 7 textures / 3 programs**. Two URL parses total, one original and one limestone. Both caches deliberately retain their warmedLOD geometries/textures between mounts.
- Retirement occurs only after all preview consumers unmount: disposes8 owned geometries incl. proxies,4 materials incl. proxy defaults,6 textures and closes6ImageBitmaps, clears only these two isolated preview URLs. Counters return to ground-only **1geometry / 1texture / 1program**. Original production caches are not involved. [Resource and browser evidence](raw/preview-verification.json).
- Preserved hashes:664 original production source/config/assets; earlier pilot/report/master/exports/ZIP and original authoring tools. No original production source modification, no new navigation/state-machine work. Full production regression/build suites were not rerun for this isolated asset-only variant; preceding Stage2A results remain intact, and this variant received its own export/loader/geometry/lifecycle checks.

## Software-renderer diagnostics

Chromium{d['browser']}, Debian13 cloudVM with ANGLE Vulkan SwiftShader (renderer string in raw evidence). Desktop1366×900, fixedDPR0.5, no CPU/network throttle; two sequential8-second samples after readiness. Same medium camera/light/render settings; screenshot collection is in separate DPR1 pages. No physical laptop, iPhone or AndroidGPU is available. Physical benchmarks remain pending and do not block this variant.

{table}

These short software measurements vary with VM scheduling; the FPS difference does **not** certify a limestone performance improvement. Both renders include the same11,264-triangle common ground plus selected32,616-triangleLOD0. No sustained60FPS or driverVRAM leak-free claim. Resource plateau reflects bounded preview caches, not proof about driver memory. The asset remains opt-in and contributes zero default production transfer/geometry.

## Portable review package

`gullyverse-limestone-pilot-review.zip` contains this note, gallery/allPNG/metadata/raw checks, Blender master/maps, five limestoneGLBs, the original GLB for comparison, unchanged shared authoring field, new authoring scripts, bundled local viewer and font. Extract and run `python reports/limestone-rock-pilot-2026-10-12/preview/serve-preview.py`; open localhost:3002. The normal website and original pilot remain unchanged.

New files only: `scripts/blender/limestone_pilot_surface.py`, `limestone_pilot_materials.py`, `author_limestone_pilot.py`, `inspect_limestone_pilot.py`; dedicated `assets-source/gullyverse/limestone-pilot/`, `public/models/gullyverse/pilot-limestone/`, this report directory and review ZIP. No full quarry, tunnel, stage or other destination was replaced. This variant stops at review; no permanent production substitution is made.
''')
# Browsable full-res actual captures and comparison pairs.
lookup={c['file']:c for c in caps['captures']}
def figure(file):
 c=lookup[file];meta=c['before']['current'];v=meta['viewport'];camera=meta['camera'];caption=f"{Path(file).stem} · {v['width']}×{v['height']} · DPR{v['effectiveDpr']} · {meta['mode']} LOD{meta['lod']} · FOV{camera['fov']} · camera{camera['position']}"
 return f'<figure><a href="{file}"><img loading="lazy" src="{file}" alt="{html.escape(caption)}"></a><figcaption>{html.escape(caption)}<details><summary>Recorded camera/render state</summary><pre>{html.escape(json.dumps(c,indent=2))}</pre></details></figcaption></figure>'
parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Limestone variant review</title><style>body{background:#121914;color:#edf2eb;font:16px system-ui;max-width:1500px;margin:auto;padding:24px}a{color:#b6d8bb}img{max-width:100%;height:auto;display:block}figure{margin:12px 0 28px}figcaption{padding:12px;background:#213126}pre{white-space:pre-wrap}.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:20px}</style><h1>Limestone rock variant</h1><p>Actual browser captures under the unchanged approved Hub lighting. Original pilot and production environment are preserved. New limestone is an isolated appearance/weathering variant. No physical GPU/mobile benchmark is claimed.</p><p><a href="README.md">Variant notes and checks</a> · <a href="raw/captures.json">Capture metadata</a> · <a href="../../assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend">Blender source</a> · <a href="../../public/models/gullyverse/pilot-limestone/quarry-limestone-pilot.glb">Runtime GLB</a></p><h2>Same camera and lighting — original vs limestone</h2>''']
for a,b in [('screenshots/01-original-pilot-medium.png','screenshots/02-limestone-medium.png'),('screenshots/07-original-pilot-quarry-context.png','screenshots/08-limestone-quarry-context.png')]:parts+=['<div class="pair">',figure(a),figure(b),'</div>']
parts+=['<h2>All views — click for original PNG</h2>']
for c in caps['captures']:parts.append(figure(c['file']))
parts+=['<p>Portable viewer: run <code>python reports/limestone-rock-pilot-2026-10-12/preview/serve-preview.py</code> from extracted package root, then open http://127.0.0.1:3002. Original pilot/Limestone controls are isolated comparison modes.</p></html>'];R.joinpath('gallery.html').write_text('\n'.join(parts))
# Self-contained ZIP, include old GLB/source only for isolated comparison and shared authoring.
files=[p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ['PACKAGE-MANIFEST.json','package-build.log','package-verification.json','preview-server.log']]
for folder in ['assets-source/gullyverse/limestone-pilot','public/models/gullyverse/pilot-limestone']:
 files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix!='.blend1' and '__pycache__' not in p.parts]
files += [ROOT/'scripts/blender'/n for n in ['limestone_pilot_surface.py','limestone_pilot_materials.py','author_limestone_pilot.py','inspect_limestone_pilot.py','rock_pilot_surface.py']]
files += [ROOT/'public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb',ROOT/'public/fonts/Fatal Fighter.ttf'];files=sorted(set(files));index={str(p.relative_to(ROOT)):p for p in files}
links=[]
for p in files:
 if p.suffix not in ['.md','.html']:continue
 targets=re.findall(r'\]\(([^)]+)\)',p.read_text()) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',p.read_text())
 for target in targets:
  if target.startswith(('http:','https:','#','data:')):continue
  key=posixpath.normpath(posixpath.join(str(p.relative_to(ROOT).parent),target));assert key in index,(p,target);links.append(key)
manifest={'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineHEAD':s['HEAD'],'files':[{'path':k,'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in index.items()],'physicalDeviceTested':False,'productionSourceChanged':False,'manifestExcludesItself':True};R.joinpath('PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
zipfile_path=ROOT/'gullyverse-limestone-pilot-review.zip'
with zipfile.ZipFile(zipfile_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for k,p in index.items():z.write(p,k)
 z.write(R/'PACKAGE-MANIFEST.json','PACKAGE-MANIFEST.json')
with zipfile.ZipFile(zipfile_path) as z:
 assert z.testzip() is None
 for entry in manifest['files']:assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
result={'status':'PASS','ZIP':zipfile_path.name,'bytes':zipfile_path.stat().st_size,'sha256':sha(zipfile_path),'entries':len(files),'linksChecked':len(links),'hashes':'PASS','CRC':'PASS'};(RAW/'package-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
