from pathlib import Path
import os,json,hashlib,shutil,zipfile,subprocess,datetime
ROOT=Path.cwd();W=Path('/workspace/stage3a1/2026-10-21/checkpoint');BASE=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint/final-restoration-test/project');TEST=W/'independent-restoration';overlay=TEST/'overlay';target=TEST/'project'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
index=json.loads((W/'checkpoint-index.json').read_text());assert not TEST.exists(),'Never overwrite an earlier restoration test';overlay.mkdir(parents=True)
for row in index['archives']:
 p=W/row['name'];assert p.stat().st_size==row['bytes']and sha(p)==row['sha256']
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  for item in z.infolist():
   rel=Path(item.filename);assert not rel.is_absolute()and'..'not in rel.parts
   out=overlay/rel;data=z.read(item)
   if out.exists():assert out.read_bytes()==data,'Conflicting duplicate archive metadata';continue
   out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
shutil.copytree(BASE,target,copy_function=os.link);sentinel=target/'UNRELATED-USER-FILE.txt';sentinel.write_text('Preserve this independent user file.\n')
command=['python',str(overlay/'apply-pilot-checkpoint.py'),'--base',str(target),'--overlay',str(overlay)]
first=subprocess.run(command,capture_output=True,text=True);assert first.returncode==0,first.stderr
manifest=json.loads((W/'complete-current-tree.json').read_text());fail=[]
for row in manifest['files']:
 p=target/row['path']
 if not p.is_file()or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:fail.append(row['path'])
assert not fail,fail;second=subprocess.run(command,capture_output=True,text=True);assert second.returncode==0 and json.loads(second.stdout)['applied']==0
assert sentinel.read_text()=='Preserve this independent user file.\n'
conflict=TEST/'conflicting-user-project';shutil.copytree(BASE,conflict,copy_function=os.link);rel='components/immersive/CaveEntranceSession.ts';changed=conflict/rel;tmp=changed.with_suffix('.conflicting-new');tmp.write_text('User edit to protect\n');os.replace(tmp,changed);parent_hash=sha(BASE/rel);other=conflict/'components/immersive/ImmersiveShell.tsx';other_hash=sha(other)
blocked=subprocess.run(['python',str(overlay/'apply-pilot-checkpoint.py'),'--base',str(conflict),'--overlay',str(overlay)],capture_output=True,text=True);assert blocked.returncode!=0 and'conflict'in(blocked.stderr+blocked.stdout).lower();assert changed.read_text()=='User edit to protect\n'and sha(other)==other_hash and sha(BASE/rel)==parent_hash;assert not(conflict/'assets-source/gullyverse/c9-cave-deep-relief').exists()
# Open the master from the new root without saving it.
readscript=TEST/'inspect-restored-master.py';readscript.write_text('''from pathlib import Path
import bpy,sys,json
p=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(p))
missing=[i.name for i in bpy.data.images if i.source in ['FILE','TILED']and not i.packed_file and not Path(bpy.path.abspath(i.filepath)).is_file()]
assert not missing,missing
print('RESTORED_MASTER_PASS',len(bpy.data.objects),flush=True)
''');master=target/'assets-source/gullyverse/c9-cave-deep-relief/cave-deep-pilot.blend';before=sha(master);read=subprocess.run(['blender','-b','-t','1','--python',str(readscript),'--',str(master)],capture_output=True,text=True);(W/'restored-master-read.log').write_text(read.stdout+read.stderr);assert read.returncode==0 and'RESTORED_MASTER_PASS'in read.stdout and sha(master)==before
# Dependencies are reused only for these source/asset smoke tests; restore itself
# contains no node_modules. A clean install uses the preserved package-lock.
(target/'node_modules').symlink_to(ROOT/'node_modules',target_is_directory=True)
unit=subprocess.run([str(ROOT/'node_modules/.bin/tsx'),'--test',*map(str,sorted((target/'tests/immersive').glob('*.test.ts')))],cwd=target,capture_output=True,text=True);(W/'restored-unit-tests.log').write_text(unit.stdout+unit.stderr);assert unit.returncode==0,unit.stderr[-2000:]
typecheck=subprocess.run([str(ROOT/'node_modules/.bin/tsc'),'--noEmit','--incremental','false'],cwd=target,capture_output=True,text=True);(W/'restored-typecheck.log').write_text(typecheck.stdout+typecheck.stderr);assert typecheck.returncode==0,typecheck.stdout[-3000:]
result={'status':'PASS','atUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'handoffID':index['handoffID'],'archiveCount':len(index['archives']),'allArchiveSHAsAndCRCs':'PASS','verifiedCompleteProjectFiles':len(manifest['files']),'overlayApply':json.loads(first.stdout),'idempotentReplay':json.loads(second.stdout),'conflictingUserEditRefusedBeforeWrites':True,'unrelatedFilePreserved':True,'protectedParentUnchanged':True,'restoredBlenderMasterOpensWithoutMutationOrMissingImages':True,'restoredImmersiveTests':'PASS_100','restoredTypecheck':'PASS','dependencySmokeTestMethod':'Temporary symlink to installed dependencies matching the preserved lockfile. No fresh npm ci or independent production build is claimed for this smoke test.','restorationRoot':str(target),'fullRequiredTreeSHAValidation':True,'physicalHardware':False}
(W/'restore-verification.json').write_text(json.dumps(result,indent=2)+'\n');index['independentRestore']='PASS_FULL_TREE_AND_SOURCE_SMOKE';(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2)+'\n')
lines=(W/'SHA256SUMS.txt').read_text().splitlines();lines=[sha(W/'checkpoint-index.json')+'  checkpoint-index.json'if line.endswith('  checkpoint-index.json')else line for line in lines];lines.append(sha(W/'restore-verification.json')+'  restore-verification.json');(W/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n');print(json.dumps(result,indent=2))
