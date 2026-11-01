from pathlib import Path
import json,zipfile,hashlib,datetime
O=Path(__file__).resolve().parents[1];C=O/'checkpoint'
def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
files=[]
for dirname in ['source','evidence','renders','review']:
 for p in sorted((O/dirname).rglob('*')):
  if p.is_file()and'__pycache__'not in p.parts and not p.name.endswith('.pyc'):files.append(p)
files += [O/'REPORT.md',O/'RESTORE.md',O/'GALLERY.html',C/'drive-folders.json',C/'delivery-helpers.js']
manifest={'status':'PRIVATE_ART_COMPLETE_READY_FOR_USER_REVIEW','createdUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSHA256':json.loads((O/'evidence/art-authoring.json').read_text())['masterSHA256'],'files':[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':digest(p)}for p in files]}
(O/'FILE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n');(O/'FILE-SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n"for r in manifest['files']))
groups={
 'Rev05C-Art-Source-and-Tests.zip':[p for p in files if p.relative_to(O).parts[0]in ['source','evidence','checkpoint']]+[O/'REPORT.md',O/'RESTORE.md',O/'FILE-MANIFEST.json',O/'FILE-SHA256SUMS.txt'],
 'Rev05C-Art-Reviews-and-Gallery.zip':[p for p in files if p.relative_to(O).parts[0]=='review']+[O/'GALLERY.html'],
 **{f'Rev05C-Art-Images-{v}.zip':[p for p in files if p.relative_to(O).parts[0]=='renders'and p.relative_to(O).parts[1]in ['before','after']and p.relative_to(O).parts[2]==v]for v in ['A','B','C']},
 'Rev05C-Art-Diagnostics-and-Drafts.zip':[p for p in files if p.relative_to(O).parts[0]=='renders'and p.relative_to(O).parts[1]not in ['before','after']]}
archives=[]
for name,parts in groups.items():
 p=C/name;assert not p.exists(),'Frozen archive exists; create a versioned replacement, never overwrite verified bytes.'
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for q in parts:z.write(q,str(q.relative_to(O)))
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
 assert p.stat().st_size<80*1024*1024,'Split oversized archive into complementary parts before upload.'
 archives.append({'name':name,'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'members':len(parts),'folder':'checkpoint'})
index={'status':'READY_FOR_USER_VISUAL_REVIEW','scope':'Self-contained private Blender art checkpoint, not a website release','requiredArchives':len(archives),'archives':archives,'perFileManifest':'FILE-MANIFEST.json','allArchivesExtractIntoSameFreshDirectory':True,'supportLighting':'APPROVED_LOCKED_OFF','interimSourceSnapshotSuperseded':True}
(C/'ARCHIVE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
queue=[*archives]
extra=[(O/'review/Gullyverse-Rev05C-Shutter-Graffiti-Review.pdf',None,'review'),(O/'review/Gullyverse-Rev05C-Full-Art-Comparisons.pdf',None,'review'),(O/'REPORT.md',None,'review'),(O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend',None,'checkpoint'),(C/'ARCHIVE-INDEX.json',None,'checkpoint'),(O/'FILE-MANIFEST.json',None,'checkpoint'),(O/'FILE-SHA256SUMS.txt',None,'checkpoint'),(O/'RESTORE.md',None,'checkpoint')]
for key,name in [('chaar-diwari','Shutter-Chaar-Diwari.png'),('ritviz','Shutter-Ritviz.png'),('neha-kakkar','Shutter-Neha-Kakkar.png')]:extra.append((O/f'renders/after/C/ART-{key}-front.png',name,'review'))
for p,name,folder in extra:queue.append({'name':name or p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'folder':folder})
(C/'UPLOAD-QUEUE.json').write_text(json.dumps(queue,indent=2)+'\n');print('ART_CHECKPOINT_PACKAGED',len(manifest['files']),'member hashes',len(archives),'archives',len(queue),'delivery files')
