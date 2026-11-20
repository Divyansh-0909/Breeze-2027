from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path('/dev/shm/texture-alpha-fix-2026-11-15');W=Path('/dev/shm/Breeze-2027-runtime');O=W/'public/models/gullyverse/locked-rev15z-clean-v2';D=R/'delivery';sha=lambda b:hashlib.sha256(b).hexdigest();files={}
def add(p,name):
 p=Path(p);assert p.is_file();assert not p.name.startswith('.env')and not p.name.startswith('auth-');files[name]=p.read_bytes()
for directory in ['scripts/gullyverse','components/gullyverse-runtime','docs/runtime']:
 for p in sorted((W/directory).rglob('*')):
  if p.is_file()and'node_modules'not in p.parts and'__pycache__'not in p.parts:add(p,'workspace-overlay/'+str(p.relative_to(W)))
m=json.loads((O/'manifest.json').read_text())
for row in m['files']:add(O/row['file'],'standalone-pilot/'+row['file'])
for name in ['manifest.json','rgbm-verification.json','uv-roundtrip-verification.json','reexport-verification.json']:add(O/name,'standalone-pilot/'+name)
add(O/'contact-frontage-baked.blend','editable/contact-frontage-baked.blend');add(O/'irradiance.raw.pfm','lighting-source/irradiance.raw.pfm');add(O/'lightmap.raw.hdr','lighting-source/lightmap.raw.hdr')
for p in O.glob('lightmap*.png'):add(p,'lighting-source/'+p.name)
add(O/'source-inventory.json','evidence/source-inventory.json')
for p in (R/'evidence').glob('*.json'):add(p,'evidence/'+p.name)
for name in ['quality-bake-final.log','denoise-final.log','uv-verification.log','reexport.log','compression.log','typecheck.log','preservation.log','browser-quality.log','bias-diagnostic.log']:add(R/'evidence'/name,'evidence/logs/'+name)
for p in (R/'source').glob('*'):
 if p.is_file()and p.suffix in ['.py','.js','.sh']:add(p,'phase-tools/'+p.name)
for p in (R/'renders').glob('*.png'):add(p,'review/captures/'+p.name)
add(R/'review/Breeze-2027-Clean-Textures-and-Transparent-Graffiti.pdf','review/Breeze-2027-Clean-Textures-and-Transparent-Graffiti.pdf')
for name in ['package.json','package-lock.json','tsconfig.json']:add(W/name,'base-reference/'+name)
files['base-reference/BASE.json']=json.dumps({'repository':'https://github.com/Divyansh-0909/Breeze-2027.git','baseHEAD':'0e1e23dd2f5181df202d862d147067249bc55a41','branch':'codex/locked-world-runtime-20261114','immutableNativeSeal':'https://drive.google.com/drive/folders/1pNvqnkT_Ic2XwMIe5v-_A37Vw7shLwcS','nativeSHA256':'89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041','scope':'Self-contained private runtime and new implementation overlay. Whole original website/LFS baseline is separate.'},indent=2).encode()
rows=[{'file':name,'bytes':len(b),'sha256':sha(b)}for name,b in sorted(files.items())];files['Archive-File-Manifest.json']=json.dumps(rows,indent=2).encode();archive=D/'Breeze-2027-Texture-and-Alpha-Fix.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for name,b in sorted(files.items()):info=zipfile.ZipInfo(name,(2026,11,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None
 for row in rows:assert sha(z.read(row['file']))==row['sha256']
data=archive.read_bytes();parts=[]
for i,start in enumerate(range(0,len(data),16*1024*1024),1):
 b=data[start:start+16*1024*1024];name=f'Breeze-2027-Texture-and-Alpha-Fix.zip.part{i:02d}';(D/name).write_bytes(b);parts.append({'file':name,'bytes':len(b),'sha256':sha(b)})
assert b''.join((D/x['file']).read_bytes()for x in parts)==data
index={'schemaVersion':1,'phase':'Texture grain and transparent graffiti, 15 November 2026 IST','version':m['version'],'archive':archive.name,'archiveBytes':len(data),'archiveSHA256':sha(data),'fileCount':len(files),'parts':parts,'sourceMasterSHA256':m['source']['sha256'],'sourceNativeSealFolder':'https://drive.google.com/drive/folders/1pNvqnkT_Ic2XwMIe5v-_A37Vw7shLwcS','localZIPAndPartVerification':'PASS','remoteVerification':'Pending until receipts added'};(D/'Checkpoint-Index.draft.json').write_text(json.dumps(index,indent=2)+'\n');(R/'evidence/package-verification.json').write_text(json.dumps({'status':'PASS','archiveBytes':len(data),'archiveSHA256':sha(data),'partCount':len(parts),'allPayloadHashesAndZIPCRCVerified':True,'byteExactReassembly':True},indent=2)+'\n');print(json.dumps(index|{'parts':len(parts)}))
