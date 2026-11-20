from pathlib import Path
import json,hashlib,zipfile
R=Path('/dev/shm/m2a-contact-journey-2026-11-15');W=Path('/dev/shm/Breeze-2027-runtime');O=W/'public/models/gullyverse/locked-rev15z-m2a';G=W/'public/models/gullyverse/locked-rev15z-m2a-contact-ground';D=R/'delivery';sha=lambda b:hashlib.sha256(b).hexdigest();files={}
def add(p,name):
 p=Path(p);assert p.is_file();assert not p.name.startswith('.env')and not p.name.startswith('auth-');files[name]=p.read_bytes()
for directory in ['scripts/gullyverse','components/gullyverse-runtime','docs/runtime']:
 for p in sorted((W/directory).rglob('*')):
  if p.is_file()and'node_modules'not in p.parts and'__pycache__'not in p.parts:add(p,'workspace-overlay/'+str(p.relative_to(W)))
for rel in ['components/immersive/runtime.ts','components/immersive/input.ts','app/runtime-preview/page.tsx','app/api/preview-health/route.ts','tests/immersive/contact-journey.test.ts','README.md']:add(W/rel,'workspace-overlay/'+rel)
for p in sorted(O.rglob('*')):
 if p.is_file():add(p,'standalone-journey/'+str(p.relative_to(O)))
for name in ['contact-frontage-baked.blend','irradiance.raw.pfm','lightmap.raw.hdr','source-inventory.json','rgbm-verification.json','uv-roundtrip-verification.json','reexport-verification.json']:add(G/name,'editable-ground/'+name)
for p in G.glob('lightmap*.png'):add(p,'editable-ground/'+p.name)
for directory in ['evidence','source','review','renders']:
 for p in sorted((R/directory).glob('*')):
  if p.is_file()and p.suffix in ['.json','.log','.py','.js','.cjs','.sh','.ts','.png','.pdf']:add(p,directory+'/'+p.name)
for name in ['package.json','package-lock.json','tsconfig.json']:add(W/name,'base-reference/'+name)
files['base-reference/BASE.json']=json.dumps({'repository':'https://github.com/Divyansh-0909/Breeze-2027.git','baseHEAD':'0e1e23dd2f5181df202d862d147067249bc55a41','branch':'codex/locked-world-runtime-20261114','cleanTextureCheckpoint':'https://drive.google.com/file/d/1IRa7nuHQpmVEW0mZ82rys2Ll2f1mJuRT/view','immutableNativeSeal':'https://drive.google.com/drive/folders/1pNvqnkT_Ic2XwMIe5v-_A37Vw7shLwcS','nativeSHA256':'89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041','scope':'Self-contained native Contact journey and implementation overlay. Original repository/LFS baseline and immutable source seal are separate.'},indent=2).encode()
rows=[{'file':name,'bytes':len(b),'sha256':sha(b)}for name,b in sorted(files.items())];files['Archive-File-Manifest.json']=json.dumps(rows,indent=2).encode();out=D/'Breeze-2027-M2A-Contact-Journey.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for name,b in sorted(files.items()):info=zipfile.ZipInfo(name,(2026,11,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
with zipfile.ZipFile(out)as z:
 assert z.testzip()is None
 for row in rows:assert sha(z.read(row['file']))==row['sha256']
b=out.read_bytes();parts=[]
for i,start in enumerate(range(0,len(b),16*1024*1024),1):
 data=b[start:start+16*1024*1024];name=f'{out.name}.part{i:02d}';(D/name).write_bytes(data);parts.append({'file':name,'bytes':len(data),'sha256':sha(data)})
idx={'schemaVersion':1,'phase':'M2A native Contact journey, 15 November 2026 IST','archive':out.name,'archiveBytes':len(b),'archiveSHA256':sha(b),'fileCount':len(files),'parts':parts,'localZIPAndPartVerification':'PASS','sourceMasterSHA256':'89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041'};(D/'Checkpoint-Index.draft.json').write_text(json.dumps(idx,indent=2)+'\n');(R/'evidence/package-verification.json').write_text(json.dumps({'status':'PASS','allPayloadHashesAndZIPCRCVerified':True,'archiveBytes':len(b),'archiveSHA256':sha(b),'parts':len(parts)},indent=2)+'\n');print(json.dumps(idx|{'parts':len(parts)}))
