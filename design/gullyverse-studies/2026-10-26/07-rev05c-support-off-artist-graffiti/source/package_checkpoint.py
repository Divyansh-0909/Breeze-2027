from pathlib import Path
import json,hashlib,zipfile,datetime
O=Path(__file__).resolve().parents[1];C=O/'checkpoint'
def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=[]
for root in ['source','evidence','review','renders']:
 for p in sorted((O/root).rglob('*')):
  if p.is_file()and'__pycache__'not in p.parts and not p.name.endswith('.pyc'):files.append(p)
files += [O/'REPORT.md',O/'RESTORE.md',O/'GALLERY.html',C/'drive-folders.json',C/'delivery-helpers.js']
assert all(p.is_file()for p in files)
manifest={'status':'PARTIAL_LIGHTING_IMPLEMENTED_GRAFFITI_ASSET_BLOCKED','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':digest(p)}for p in files]}
(O/'FILE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
(O/'FILE-SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n"for r in manifest['files']))
groups={
 'Rev05C-Lighting-Source-Tests-PARTIAL.zip':[p for p in files if p.relative_to(O).parts[0]in ['source','evidence','checkpoint']]+[O/'REPORT.md',O/'RESTORE.md',O/'FILE-MANIFEST.json',O/'FILE-SHA256SUMS.txt'],
 'Rev05C-Lighting-Reviews.zip':[p for p in files if p.relative_to(O).parts[0]=='review']+[O/'GALLERY.html'],
 **{f'Rev05C-Lighting-Images-{v}.zip':[p for p in files if p.relative_to(O).parts[0]=='renders'and v in p.relative_to(O).parts]for v in ['A','B','C']}}
archives=[]
for name,parts in groups.items():
 dest=C/name
 assert not dest.exists(),'Do not overwrite already frozen archive bytes; use a new version.'
 with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in parts:z.write(p,str(p.relative_to(O)))
 with zipfile.ZipFile(dest)as z:assert z.testzip()is None
 archives.append({'name':name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':digest(dest),'members':len(parts),'folder':'checkpoint'})
index={'status':'PARTIAL_LIGHTING_CHECKPOINT_GRAFFITI_UNRESOLVED','archives':archives,'requiredArchives':len(archives),'memberManifest':'FILE-MANIFEST.json','independentBlenderRestore':True,'websiteBackup':False,'previousRev05BBackup':'https://drive.google.com/drive/folders/1RBUH2fDcXWhGUn32txMNqo6ejWKwFz7p'}
(C/'ARCHIVE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
queue=[*archives]
for p in [O/'review/Gullyverse-Rev05C-Lighting-PARTIAL-Review.pdf',O/'review/Gullyverse-Rev05C-Lighting-All-ABC.pdf',O/'REPORT.md',O/'source/Gullyverse-Rev05C-Interior-Support-Off.blend',C/'ARCHIVE-INDEX.json',O/'FILE-MANIFEST.json',O/'FILE-SHA256SUMS.txt',O/'RESTORE.md']:
 queue.append({'name':p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'folder':'review'if p.suffix=='.pdf'or p.name=='REPORT.md'else'checkpoint'})
(C/'UPLOAD-QUEUE.json').write_text(json.dumps(queue,indent=2)+'\n')
print('CHECKPOINT_PACKAGED',len(manifest['files']),'members',len(archives),'archives')
