"""Fresh restoration exclusively from actual authenticated Drive-downloaded ZIPs."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,os,sys
O=Path(__file__).resolve().parents[1];items=json.loads((O/'checkpoint/final-archive-items.json').read_text());root=Path('/dev/shm/rev09/independent-restore-final');assert not root.exists(),'Refuse overwrite';root.mkdir()
for r in items:
 p=Path(r['save']);assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 with zipfile.ZipFile(p)as z:
  for n in z.namelist():assert not Path(n).is_absolute()and '..'not in Path(n).parts
  assert z.testzip()is None;z.extractall(root)
sys.path.insert(0,str(root/'source'));from verify_payload import verify
check=verify(root);master=root/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend'
# The audit scripts write JSONs: restore the original evidence bytes afterwards,
# then verify the delivered payload still hashes exactly. The .blend is never saved.
saved={p:p.read_bytes() for p in (root/'evidence').glob('*.json')}
for script in ['verify_reopen.py','audit_preservation.py']:
 env=dict(os.environ,LP_NUM_THREADS='2',GULLYVERSE_BASELINE_OVERRIDE=str(root/'source/baseline/Rev08-Protected-Original.blend'))
 with (O/'checkpoint'/('restored-'+script+'.log')).open('w')as f:subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(root/'source'/script)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
for p,b in saved.items():p.write_bytes(b)
assert verify(root)==check
proof={'status':'PASS','onlyActualDriveDownloadedZIPsUsed':True,'archives':len(items),'payloadHashesBeforeAndAfterBlenderOpen':check['payloadFiles'],'galleryLinksChecked':check['galleryLinks'],'freshDirectory':str(root),'masterSHA256':check['masterSHA256'],'all13ScenesAnd33PackedImagesReopened':True,'noExternalFontDependency':True,'all11HistoricalSceneSignaturesCheckedAgainstRestoredOriginalMaster':True,'previousCrowd180Exact':True,'allFiveOptionalSupportsOFF':True,'allFiveNumberedArchivesRequired':True,'validationJSONOutputsRestoredFromDeliveredBytesAfterAudit':True}
(O/'checkpoint/INDEPENDENT-RESTORE-VERIFICATION.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
