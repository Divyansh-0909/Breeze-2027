from pathlib import Path
import zipfile,json,hashlib,re,posixpath,datetime,tarfile,subprocess
ROOT=Path.cwd(); R=ROOT/'reports/stage-2a-asset-pilot-2026-10-11'; OUT=ROOT/'gullyverse-stage-2a-asset-pilot-review.zip'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def eligible(p):return p.is_file() and 'backup' not in p.relative_to(R).parts and '__pycache__' not in p.parts and p.name not in ['PACKAGE-MANIFEST.json','package-verification.json','package-build.log']
files=[p for p in R.rglob('*') if eligible(p)]
for dirname in ['assets-source/gullyverse/rock-pilot-2a','public/models/gullyverse/pilot-rock']:
 files += [p for p in (ROOT/dirname).rglob('*') if p.is_file() and p.suffix!='.blend1' and '__pycache__' not in p.parts]
files += [ROOT/'scripts/blender'/n for n in ['rock_pilot_surface.py','rock_pilot_materials.py','author_rock_pilot_2a.py','inspect_rock_pilot_2a.py']]
files += [ROOT/'docs/gullyverse-stage-2a-asset-pilot.md',ROOT/'public/fonts/Fatal Fighter.ttf']
files=sorted(set(files))
# Final additions inventory is itself included.
added=sorted(str(p.relative_to(ROOT)) for p in files if p!=ROOT/'public/fonts/Fatal Fighter.ttf')
(R/'raw/files-added.json').write_text(json.dumps({'productionFilesModified':[],'newPilotFiles':added,'additionalLocalOnlyFiles':['reports/stage-2a-asset-pilot-2026-10-11/backup/approved-source-assets.tar.gz','reports/stage-2a-asset-pilot-2026-10-11/backup/staged.patch','reports/stage-2a-asset-pilot-2026-10-11/backup/unstaged.patch','assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend1','scripts/blender/__pycache__/ (generated authoring bytecode)','reports/stage-2a-asset-pilot-2026-10-11/PACKAGE-MANIFEST.json','reports/stage-2a-asset-pilot-2026-10-11/raw/package-verification.json','reports/stage-2a-asset-pilot-2026-10-11/raw/package-build.log','gullyverse-stage-2a-asset-pilot-review.zip'],'scope':'Original production files and existing untracked work unchanged. Original Fatal Fighter.ttf is copied into ZIP for portable viewer, never modified.'},indent=2)+'\n')
index={str(p.relative_to(ROOT)):p for p in files}
# Validate every Markdown/report-gallery link against proposed archive contents.
missing=[]; links=0
for p in files:
 if p.suffix not in ['.md','.html']:continue
 s=p.read_text();targets=re.findall(r'\]\(([^)]+)\)',s) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',s)
 for t in targets:
  if t.startswith(('http:','https:','data:','#')):continue
  key=posixpath.normpath(posixpath.join(str(p.relative_to(ROOT).parent),t.split('#')[0]))
  links+=1
  if key not in index:missing.append({'source':str(p.relative_to(ROOT)),'target':t,'normalized':key})
assert not missing,missing
for key in index:
 assert not any(x.startswith('.env') or x in ['.vercel','credentials','auth.json'] for x in Path(key).parts),key
manifest={'createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baselineHEAD':'e3dbbc233f1f12f5e4d96333db3b797e75da4760','measurementDate':'2026-10-11','physicalHardwareTested':False,'entries':[{'path':k,'bytes':p.stat().st_size,'sha256':sha(p)} for k,p in index.items()],'manifestExcludesItself':True,'excluded':'Large local recovery backup, automatic .blend1 draft, Python caches, credentials and prior entire ZIP. Original font is included for portable viewer.'}
(R/'PACKAGE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for k,p in index.items():z.write(p,k)
 z.write(R/'PACKAGE-MANIFEST.json','PACKAGE-MANIFEST.json')
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 for e in manifest['entries']:
  assert hashlib.sha256(z.read(e['path'])).hexdigest()==e['sha256'],e['path']
 verification={'status':'PASS','archive':OUT.name,'bytes':OUT.stat().st_size,'sha256':sha(OUT),'payloadEntries':len(index),'payloadBytes':sum(e['bytes'] for e in manifest['entries']),'relativeLinksChecked':links,'missingLinks':[],'CRC':'PASS','allPayloadHashes':'PASS','credentialsIncluded':False,'productionSourcesModified':False,'editableMasterIncluded':True,'portableViewerIncluded':True,'verifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(R/'raw/package-verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps(verification,indent=2))
