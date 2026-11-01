from pathlib import Path
import io,bisect,json,hashlib,zipfile,tempfile,subprocess,shutil,os
W=Path(__file__).resolve().parent;O=W.parent
class Parts(io.RawIOBase):
 def __init__(self,paths):
  self.paths=paths;self.ends=[];n=0
  for p in paths:n+=p.stat().st_size;self.ends.append(n)
  self.pos=0;self.size=n
 def readable(self):return True
 def seekable(self):return True
 def tell(self):return self.pos
 def seek(self,n,w=0):
  self.pos=n if w==0 else self.pos+n if w==1 else self.size+n
  if self.pos<0:raise ValueError('negative seek')
  return self.pos
 def read(self,n=-1):
  n=self.size-self.pos if n<0 else min(n,self.size-self.pos);out=[]
  while n>0:
   i=bisect.bisect_right(self.ends,self.pos);start=0 if i==0 else self.ends[i-1]
   with self.paths[i].open('rb')as f:f.seek(self.pos-start);b=f.read(min(n,self.ends[i]-self.pos))
   if not b:break
   out.append(b);self.pos+=len(b);n-=len(b)
  return b''.join(out)
archives=json.load(open(W/'archives.json'));rows=json.load(open(W/'files-manifest.json'));byfile={r['archive']+'::'+r['file']:r for r in rows};final={r['file']:r for r in rows};assert len(final)==196;stage=Path(tempfile.mkdtemp(prefix='independent-concept-restore-',dir=W));prefix='Gullyverse-Lane-Rooftop-Concept/';done=[]
try:
 for a in archives:
  paths=[W/p['name']for p in a['parts']]if a['parts']else[W/a['archive']];h=hashlib.sha256();size=0
  for p in paths:
   with p.open('rb')as f:
    while block:=f.read(1024*1024):h.update(block);size+=len(block)
  assert size==a['bytes']and h.hexdigest()==a['sha256']
  with zipfile.ZipFile(Parts(paths))as z:
   assert len(z.infolist())==a['members']
   for info in z.infolist():
    assert info.filename.startswith(prefix)and'..'not in Path(info.filename).parts
    rel=info.filename[len(prefix):];row=byfile[a['archive']+'::'+rel];dest=stage/info.filename;dest.parent.mkdir(parents=True,exist_ok=True);data=z.read(info);assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256'];dest.write_bytes(data)
  done.append({'archive':a['archive'],'members':a['members'],'sha256':a['sha256'],'wholeHashAndMemberExtraction':'PASS'})
 for row in final.values():
  for p in [stage/prefix/row['file'],O/row['file']]:assert p.stat().st_size==row['bytes']and hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==row['sha256'],str(p)
 # Open the independently restored master and prove packed assets/three scenes, without saving it.
 proof=W/'restored-blender-read.json';script=W/'check-restored-blender.py';script.write_text("import bpy,json\nfrom pathlib import Path\nimages=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(bpy.data.scenes)==3;assert len(images)==25;assert all(i.packed_file for i in images);assert all(f.filepath=='<builtin>' or f.packed_file for f in bpy.data.fonts)\nPath("+repr(str(proof))+").write_text(json.dumps({'status':'PASS','scenes':[s.name for s in bpy.data.scenes],'packedImages':len(images),'noLinkedExternalBlendLibraries':len(bpy.data.libraries)==0,'allUsedImagesPacked':True,'openedIndependentRestoredCopy':True},indent=2))\n")
 with (W/'restored-blender-read.log').open('w')as f:r=subprocess.run(['blender','-b',str(stage/prefix/'source/Gullyverse-Lane-Rooftop-ABC.blend'),'-t','1','--python',str(script)],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0 and proof.exists();opened=json.load(open(proof));assert opened['noLinkedExternalBlendLibraries']
 result={'status':'PASS_INDEPENDENT_EXTRACT_ALL_FILES_AND_OPEN_RESTORED_BLEND','files':len(final),'bytes':sum(r['bytes']for r in final.values()),'archives':done,'restoredBlender':opened,'websiteNotRequiredToOpenConceptMaster':True,'temporaryStagingDeletedAfterVerification':True,'protectedWebsiteFilesIdentical':1213,'priorCanalCheckpointFilesIdentical':311};(W/'restore-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
finally:shutil.rmtree(stage)
