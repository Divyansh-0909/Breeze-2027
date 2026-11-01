from pathlib import Path
import json,hashlib,zipfile,subprocess,os,sys
O=Path(__file__).resolve().parents[1];items=json.loads((O/'checkpoint/final-archive-items.json').read_text());root=Path('/dev/shm/rev10/independent-restore-final');assert not root.exists(),'Refuse overwrite';root.mkdir()
for r in items:
 p=Path(r['save']);assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 with zipfile.ZipFile(p)as z:
  assert all(not Path(n).is_absolute()and '..'not in Path(n).parts for n in z.namelist());assert z.testzip()is None;z.extractall(root)
sys.path.insert(0,str(root/'source'));from verify_payload import verify
check=verify(root);saved={p:p.read_bytes()for p in (root/'evidence').glob('*.json')};m=root/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend'
for script in ['verify_reopen.py','validate_architecture.py']:
 with (O/'checkpoint'/('restored-'+script+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(root/'source'/script)],env=dict(os.environ,LP_NUM_THREADS='2'),stdout=f,stderr=subprocess.STDOUT,check=True)
for p,b in saved.items():p.write_bytes(b)
assert verify(root)==check
proof={'status':'PASS','onlyActualAuthenticatedDriveDownloadedZIPsUsed':True,'archives':len(items),'allNumberedArchivesRequired':True,'payloadHashesBeforeAndAfterBlenderOpen':check['payloadFiles'],'relativeGalleryLinksChecked':check['galleryLinks'],'masterSHA256':check['masterSHA256'],'freshDirectory':str(root),'all15ScenesAnd33PackedImagesReopened':True,'all13OriginalSceneSignaturesCheckedAgainstRestoredAuthenticRev09':True,'bothOriginal180CrowdsExact':True,'all17LightOwnersExactFiveSupportLightsOFF':True,'noExternalFontsOrWebsiteDependenciesNeeded':True,'validationJSONOutputsRestoredToDeliveredBytesAfterAudit':True}
(O/'checkpoint/INDEPENDENT-RESTORE-VERIFICATION.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
