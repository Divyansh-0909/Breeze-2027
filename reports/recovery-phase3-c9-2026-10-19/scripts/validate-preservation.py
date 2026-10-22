from pathlib import Path
import hashlib,json,subprocess
ROOT=Path.cwd();RAW=ROOT/'reports/recovery-phase3-c9-2026-10-19/raw'
rows=json.loads((RAW/'starting-hashes.json').read_text());allowed={'components/immersive/ImmersiveShell.tsx','components/immersive/QuarryPerimeter.tsx','components/immersive/scannedRockSampling.ts'}
identical=0;changed=[];unexpected=[]
for row in rows:
 path=ROOT/row['path']
 if not path.is_file():unexpected.append({'path':row['path'],'reason':'missing'});continue
 with path.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 if digest==row['sha256']:identical+=1
 else:(changed if row['path']in allowed else unexpected).append({'path':row['path'],'beforeSHA256':row['sha256'],'afterSHA256':digest})
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert branch=='codex/navigation-board'and head=='14f36da1a9b79a3b4926f7445bf0cde6c6c8f767'
result={'status':'PASS'if not unexpected else'FAIL','startingFiles':len(rows),'byteIdentical':identical,'authorizedChanges':changed,'unexpectedChanges':unexpected,'branch':branch,'HEAD':head,'publicGeometryAndPBRAssetsUnchanged':not unexpected,'protectedPhase1OrPhase2BackupsOverwritten':False}
(RAW/'preservation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert not unexpected
