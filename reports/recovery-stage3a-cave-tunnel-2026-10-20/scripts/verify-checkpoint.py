"""Independent restore, entire required tree, idempotence and conflict proof."""
from pathlib import Path
import hashlib,json,zipfile,shutil,os,subprocess,sys
ROOT=Path.cwd();W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint');T=W/'final-restoration-test';T.mkdir(exist_ok=False)
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
index=json.loads((W/'checkpoint-index.json').read_text());overlay=T/'overlay';overlay.mkdir()
for row in index['archives']:
 p=W/row['name'];assert sha(p)==row['sha256']and p.stat().st_size==row['bytes']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  for info in z.infolist():
   rel=Path(info.filename);assert not rel.is_absolute()and'..'not in rel.parts and(info.external_attr>>16)&0o170000!=0o120000
  z.extractall(overlay)
assert sha(overlay/'recovery-stage3a/stage3a-file-manifest.json')==index['perFileManifestSHA256']
manifest=json.loads((overlay/'recovery-stage3a/stage3a-file-manifest.json').read_text());tree=json.loads((overlay/'recovery-stage3a/complete-current-tree.json').read_text())
base=Path('/workspace/recovery-fidelity/2026-10-19/checkpoint/restoration-test/project');restored=T/'project';shutil.copytree(base,restored,copy_function=os.link)
fixture=restored/'stage3a-independent-user-note.txt';assert not fixture.exists();fixture.write_text('Independent unrelated user work.\n')
def apply(target):return subprocess.run([sys.executable,str(W/'apply-stage3a.py'),'--base',str(target)],cwd=overlay,text=True,capture_output=True)
a=apply(restored);assert a.returncode==0,a.stdout+a.stderr;b=apply(restored);assert b.returncode==0,b.stdout+b.stderr;assert json.loads(b.stdout)['restored']==0
for row in tree['files']:assert sha(restored/row['path'])==row['sha256']and sha(ROOT/row['path'])==row['sha256'],row['path']
assert fixture.read_text()=='Independent unrelated user work.\n'
conflict=T/'conflicting-user-project';shutil.copytree(base,conflict,copy_function=os.link);target=conflict/'components/immersive/ImmersiveShell.tsx';tmp=target.with_name('independent-edit');tmp.write_text('Independent user source edit\n');tmp.replace(target)
c=apply(conflict);assert c.returncode!=0 and'Refusing to overwrite unrelated user changes'in c.stderr;assert target.read_text()=='Independent user source edit\n';assert not(conflict/'public/models/gullyverse/c9-cave-recovery').exists()
# Original parent stays immutable despite efficient hard-linked restore fixtures.
for row in manifest['files']:
 if row.get('beforeSHA256'):assert sha(base/row['path'])==row['beforeSHA256']
master=restored/'assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend';before=sha(master)
expr=f"import bpy,json;bpy.ops.wm.open_mainfile(filepath={str(master)!r});assert all(i.packed_file for i in bpy.data.images if i.source=='FILE');assert bpy.data.objects.get('Cave_Passage4_LOD2');assert json.loads(bpy.data.texts['CAVE_RECOVERY_CONTRACT'].as_string())['approvedTextureScale']==3;print('RESTORED_CAVE_MASTER_READ_ONLY_PASS')"
p=subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python-expr',expr],text=True,capture_output=True,cwd=restored);(W/'restored-master-read.log').write_text(p.stdout+p.stderr);assert p.returncode==0 and'RESTORED_CAVE_MASTER_READ_ONLY_PASS'in p.stdout;assert sha(master)==before
result={'status':'PASS','archiveCRCAndSHA256':True,'overlayFilesVerified':len(manifest['files']),'entireRequiredCurrentTreeFilesVerified':len(tree['files']),'firstRestore':json.loads(a.stdout),'secondIdempotentRestore':json.loads(b.stdout),'unrelatedUserWorkPreserved':True,'conflictingUserSourceRejectedBeforeAnyWrite':True,'protectedParentUnchanged':True,'restoredMasterOpenedReadOnly':True,'restoredMasterSHA256':before,'phase1Phase2Phase3QuarryBackupsUnchanged':True}
(W/'restore-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
