import sys,json,hashlib,zipfile,subprocess,os
from pathlib import Path
index,downloads,root,proof=map(Path,sys.argv[1:]);spec=json.load(open(index));root.mkdir(parents=True,exist_ok=True);assert not any(root.iterdir()),'Use an empty restore directory';proof.mkdir(parents=True,exist_ok=True)
def digest(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
masters={}
for r in spec['requiredComponents']:
 p=downloads/r['name'];assert p.stat().st_size==r['bytes']and digest(p)==r['sha256'],r['name']
 if r.get('part'):masters.setdefault(r['restorePath'],[]).append(r)
 else:
  with zipfile.ZipFile(p)as z:
   assert all(not Path(n).is_absolute()and'..'not in Path(n).parts for n in z.namelist());z.extractall(root)
for target,rows in masters.items():
 p=root/target;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('wb')as out:
  for r in sorted(rows,key=lambda r:r['part']):
   with(downloads/r['name']).open('rb')as f:
    while b:=f.read(1048576):out.write(b)
files=json.load(open(root/'FILE-MANIFEST.json'))
def verify():
 for r in files:assert(root/r['path']).stat().st_size==r['bytes']and digest(root/r['path'])==r['sha256'],r['path']
verify();env=dict(os.environ,WIDE_VALIDATION_OUTPUT=str(proof/'validation'))
with(proof/'blender.log').open('w')as f:subprocess.run(['blender','-b','-t','2','--python',str(root/'source/validate.py')],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
results={p.stem:json.load(open(p))['status']for p in(proof/'validation').glob('*.json')if'status'in json.load(open(p))};assert len(results)==5 and all(s=='PASS'for s in results.values()),results
probe="import bpy;bpy.ops.wm.open_mainfile(filepath="+repr(str(root/'delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend'))+");assert len(bpy.data.scenes)==38;assert not bpy.data.libraries;assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE');assert 'oc_wider_name_controls.py' in bpy.data.texts;print('PACKED_MASTER_OK')"
with(proof/'probe.log').open('w')as f:subprocess.run(['blender','-b','-t','2','--python-expr',probe],stdout=f,stderr=subprocess.STDOUT,check=True)
with(proof/'gltf.log').open('w')as f:subprocess.run([sys.executable,str(root/'source/gltf_check.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
verify();q={'status':'PASS','requiredComponents':len(spec['requiredComponents']),'componentBytes':sum(r['bytes']for r in spec['requiredComponents']),'verifiedPayloadFilesBeforeAndAfter':len(files),'validation':results,'masterSHA256':digest(root/'delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend'),'historical37ScenesPlusNew':True,'packedImages':True,'linkedLibraries':0,'independentDownloadedOnlyRestore':True};(proof/'PROOF.json').write_text(json.dumps(q,indent=2));print(q)
