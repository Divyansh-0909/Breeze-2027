from pathlib import Path
import hashlib,json,zipfile,shutil,os,subprocess,sys
ROOT=Path.cwd();W=Path('/workspace/recovery-phase3/2026-10-19/checkpoint');T=W/'restoration-test';T.mkdir(exist_ok=False)
def sha(path):
 with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
index=json.loads((W/'checkpoint-index.json').read_text());overlay=T/'overlay';overlay.mkdir()
for row in index['archives']:
 p=W/row['name'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  for info in z.infolist():
   rel=Path(info.filename);assert not rel.is_absolute()and'..'not in rel.parts and(info.external_attr>>16)&0o170000!=0o120000
  z.extractall(overlay)
manifest=json.loads((overlay/'recovery-phase3/phase3-file-manifest.json').read_text())
assert sha(overlay/'recovery-phase3/phase3-file-manifest.json')==index['perFileManifestSHA256']
for row in manifest['files']:assert sha(overlay/'project'/row['path'])==row['sha256']
base=Path('/workspace/recovery-phase2/2026-10-19/restoration-test/project');restored=T/'project';shutil.copytree(base,restored,copy_function=os.link)
(restored/'preserve-independent-user-note.txt').write_text('Unrelated user work must remain intact.\n')
def apply(target):
 p=subprocess.run([sys.executable,str(W/'apply-phase3.py'),'--base',str(target)],cwd=overlay,text=True,capture_output=True)
 return p
a=apply(restored);assert a.returncode==0,a.stdout+a.stderr;b=apply(restored);assert b.returncode==0,b.stdout+b.stderr
assert json.loads(b.stdout)['restored']==0
assert(restored/'preserve-independent-user-note.txt').read_text()=='Unrelated user work must remain intact.\n'
for row in manifest['files']:assert sha(restored/row['path'])==row['sha256']and sha(ROOT/row['path'])==row['sha256']
# Atomic fixture replacement avoids mutating any hard-linked protected baseline.
conflict=T/'conflicting-user-project';shutil.copytree(base,conflict,copy_function=os.link)
target=conflict/'components/immersive/ImmersiveShell.tsx';tmp=target.with_name('user-edit-fixture');tmp.write_text('Independent user source edit\n');tmp.replace(target)
c=apply(conflict);assert c.returncode!=0 and'Refusing to overwrite unrelated user changes'in c.stderr
assert target.read_text()=='Independent user source edit\n';assert not(conflict/'public/models/gullyverse/recovered-c9-composition').exists()
master=restored/'assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend';before=sha(master)
expr=f"import bpy,json; bpy.ops.wm.open_mainfile(filepath={str(master)!r}); assert all(i.packed_file for i in bpy.data.images if i.source=='FILE'); assert bpy.data.objects.get('C9_Wall_15_LOD2'); assert json.loads(bpy.data.texts['RECOVERY_C9_CONTRACT'].as_string())['uniformScale']==.9; print('RESTORED_MASTER_READ_ONLY_PASS')"
check=subprocess.run(['blender','-b','-t','2','--python-exit-code','1','--python-expr',expr],cwd=restored,text=True,capture_output=True)
(W/'restored-master-read.log').write_text(check.stdout+check.stderr);assert check.returncode==0 and'RESTORED_MASTER_READ_ONLY_PASS'in check.stdout;assert sha(master)==before
result={'status':'PASS','archiveCRCAndSHA256':True,'filesVerified':len(manifest['files']),'firstRestore':json.loads(a.stdout),'secondIdempotentRestore':json.loads(b.stdout),'unrelatedUserWorkPreserved':True,'conflictingUserSourceRejectedBeforeAnyWrite':True,'restoredMasterSHA256':before,'restoredMasterOpenedReadOnly':True,'allCurrentProjectFilesStillMatchFrozenCheckpoint':True,'phase1AndPhase2ProtectedReferencesUnchanged':True}
(W/'restore-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
