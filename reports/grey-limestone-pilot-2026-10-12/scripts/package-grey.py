from pathlib import Path
import json,html,zipfile,hashlib,re,posixpath,subprocess
root=Path.cwd();r=root/'reports/grey-limestone-pilot-2026-10-12';d=json.loads((r/'raw/captures.json').read_text());assert d['status']=='PASS';assert not subprocess.check_output(['git','diff','--name-only']);assert not subprocess.check_output(['git','diff','--cached','--name-only'])
source=root/'assets-source/gullyverse/limestone-grey-pilot';source.joinpath('README.md').write_text('''# Grey limestone revision

Requested by user: make the limestone more grey. Separate from the pale limestone so the previous version remains recoverable. Production environment, stage, lighting and navigation are unchanged.

Reproduce from repository/package root:

```sh
python3 scripts/blender/grey_limestone_pilot_materials.py
blender --background --python scripts/blender/author_grey_limestone_pilot.py
```

Ordinary Python needs numpy/Pillow. Blender4.3.2. Shared `limestone_pilot_surface.py` and `rock_pilot_surface.py` are included. Only base-colour palette/mineral warmth and Blender fallback colour differ; normal/roughness/AO maps retained. Editable source `quarry-grey-limestone-pilot.blend`; runtime `quarry-grey-limestone-pilot.glb`. Metres, BlenderZ-up/front−Y→glTFY-up/front+Z, bottom-centre pivot. LOD0/1/2=32616/10440/2820 triangles; proxy12. UVs/normal/indices/positions preserved. Select one LOD and hide `Rock_Collision`; glTF does not encode hidden nodes. Source2048/runtime1024 PBR maps; OpenGL tangent+Y normal, packed AO/roughness/metallic. No Draco/Meshopt/KTX2 loader added.

Preview after extraction: `python reports/grey-limestone-pilot-2026-10-12/preview/serve-preview.py`, then localhost:3003. Pale and grey limestone comparison under unchanged approved Hub lights. No physical GPU benchmarks claimed.
''')
r.joinpath('README.md').write_text('''# Grey limestone — colour revision

The limestone is now cooler grey with less yellow/beige. Previous pale limestone and the original rock pilot are preserved in their existing directories. No production source/assets/lighting/camera/navigation changes, no commit/push/deployment.

[Actual before/after gallery](gallery.html), [capture metadata](raw/captures.json), [colour-only verification](raw/colour-only-verification.json), [GLB validation](raw/glTF-validator.json).

[Blender master](../../assets-source/gullyverse/limestone-grey-pilot/quarry-grey-limestone-pilot.blend), [runtime GLB](../../public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb), [author/export instructions](../../assets-source/gullyverse/limestone-grey-pilot/README.md).

Source baseRGB184/188/193 replaces224/221/208; mineral rust warmth reduced. Same limestone weathering/shape/roughness/normal strength/UVs/collision/LODs. Exact exported positions/normals/UVs/indices and six non-colour source/runtime image hashes match. Blender re-export regenerated one LOD0 tangent component differing by about0.0001; this is quantified in verification, not claimed byte-identical. Geometry and normal maps are unchanged. Five GLBs validate with zero errors/warnings.

Four actual Chromium captures,1366×900,DPR1,FOV58; medium[31,5.6,-98] and close[41.1,5.4,-103.4], current Hub lights/ACES exposure1 unchanged. Context retains approved procedural wall behind the isolated pilot. No screenshot recolouring or synthetic renders used. Renderer is SwiftShader; no new physical benchmark or memory certification is claimed for this colour-only revision. All664 original production baseline files and prior limestone source/exports/review package hashes remain unchanged.

Extract `gullyverse-grey-limestone-pilot-review.zip` and run `python reports/grey-limestone-pilot-2026-10-12/preview/serve-preview.py`, then open localhost:3003. Package includes prior pale GLB for comparison, new grey source/maps/exports, shared authoring field and bundled viewer/font. Default production website remains unchanged.
''')
def figure(c):
 m=c['current'];cam=m['camera'];v=m['viewport'];label=f"{Path(c['file']).stem} · {v['width']}×{v['height']} DPR{v['effectiveDpr']} FOV{cam['fov']} · camera{cam['position']}"
 return '<figure><a href="'+c['file']+'"><img src="'+c['file']+'" alt="'+html.escape(label)+'"></a><figcaption>'+html.escape(label)+'<details><summary>Metadata</summary><pre>'+html.escape(json.dumps(c,indent=2))+'</pre></details></figcaption></figure>'
parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Grey limestone colour revision</title><style>body{background:#101814;color:#edf2ed;font:16px system-ui;max-width:1500px;margin:auto;padding:24px}a{color:#b8d8c0}img{max-width:100%;height:auto;display:block}figure{margin:10px 0 28px}figcaption{padding:10px;background:#213328}pre{white-space:pre-wrap}.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:20px}</style><h1>Cooler grey limestone</h1><p>Only the limestone colour treatment changed. Shape, surface detail and approved lighting retained. Previous version and production environment untouched.</p><p><a href="README.md">Notes/source links</a> · <a href="raw/captures.json">Metadata</a></p><div class="pair">''',figure(d['captures'][0]),figure(d['captures'][1]),'</div>']
parts+=[figure(c) for c in d['captures'][2:]];parts+=['</html>'];r.joinpath('gallery.html').write_text('\n'.join(parts))
files=[p for p in r.rglob('*') if p.is_file() and p.name not in ['preview-server.log','package-build.log','PACKAGE-MANIFEST.json','package-verification.json'] and '__pycache__' not in p.parts]
for directory in ['assets-source/gullyverse/limestone-grey-pilot','public/models/gullyverse/pilot-limestone-grey']:
 files += [p for p in (root/directory).rglob('*') if p.is_file() and p.suffix!='.blend1']
files += [root/'scripts/blender'/n for n in ['grey_limestone_pilot_materials.py','author_grey_limestone_pilot.py','limestone_pilot_surface.py','rock_pilot_surface.py']]
files += [root/'public/models/gullyverse/pilot-limestone/quarry-limestone-pilot.glb',root/'public/fonts/Fatal Fighter.ttf'];files=sorted(set(files));index={str(p.relative_to(root)):p for p in files}
for p in files:
 if p.suffix not in ['.md','.html']:continue
 targets=re.findall(r'\]\(([^)]+)\)',p.read_text()) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',p.read_text())
 for target in targets:
  if target.startswith(('http:','https:','#','data:')):continue
  assert posixpath.normpath(posixpath.join(str(p.relative_to(root).parent),target)) in index,(p,target)
def sha(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
manifest={'files':[{'path':k,'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in index.items()],'productionUnchanged':True,'geometryPreserved':True};r.joinpath('PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2));out=root/'gullyverse-grey-limestone-pilot-review.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for key,p in index.items():z.write(p,key)
 z.write(r/'PACKAGE-MANIFEST.json','PACKAGE-MANIFEST.json')
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for entry in manifest['files']:assert hashlib.sha256(z.read(entry['path'])).hexdigest()==entry['sha256']
result={'status':'PASS','ZIP':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'entries':len(files),'CRC':'PASS','payloadHashes':'PASS'};(r/'raw/package-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
