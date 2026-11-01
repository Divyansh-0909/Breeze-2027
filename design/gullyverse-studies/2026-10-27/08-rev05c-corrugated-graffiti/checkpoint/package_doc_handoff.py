from pathlib import Path
import json,hashlib,datetime,zipfile
c=Path(__file__).resolve().parent
proof=json.loads((c/'SHARED-DOC-HANDOFF-VERIFICATION.json').read_text())
assert proof['status']=='READY_FOR_REVIEW' and proof['allNontargetDocumentTextUnchanged']
assert proof['protectedGreenUTF16UnitsUnchanged']==142042 and proof['foregroundColor']=='#C62828'
records=[json.loads(p.read_text()) for p in c.glob('uploaded-*.json')]
names={r['name'] for r in records}
required=json.loads((c/'UPLOAD-QUEUE.json').read_text())+json.loads((c/'VERIFICATION-UPLOAD-QUEUE.json').read_text())
assert all(x['name'] in names for x in required)
for x in required:
 r=next(r for r in records if r['name']==x['name'])
 receipt=json.loads((c/('verified-'+r['id']+'.json')).read_text())
 assert r['fullDownloadBackSHA256Verified'] and receipt['verified'] and receipt['sha256']==x['sha256']
status={'status':'COMPLETE_AND_STOPPED_FOR_VISUAL_REVIEW',
 'handoffId':proof['id'],'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'finalDeliveryFilesAndVerificationSidecars':len(required),'allAuthenticatedDownloadBackSHA256Verified':True,
 'independentFreshRestore':'PASS: six ZIPs, 239 file hashes, 246 relative gallery links, packed Blender master reopened',
 'sharedDocUpdatedAndReadBack':True,'newCodexTextColor':'#C62828',
 'allNontargetDocTextAnd142042GreenUTF16UnitsPreserved':True,
 'supportOffLocked':True,'userVisualApprovalPending':True,'fourWallPlacements':'PROPOSED_NOT_LOCKED',
 'websiteAndOldCheckpointsUnchanged':True,'noCommitPushMergeDeploy':True,
 'nextAction':'User reviews PDFs and art. No next phase or document polling automatically.'}
(c/'FINAL-HANDOFF-STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
zp=c/'Rev05C-Art-Doc-Handoff-Proof.zip'
assert not zp.exists()
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,6) as z:
 for name in ['SHARED-DOC-HANDOFF-VERIFICATION.json','CODEX-HANDOFF.txt','FINAL-HANDOFF-STATUS.json',
 'FINAL-DELIVERY-VERIFICATION.json','DELIVERY-LINKS.md','independent-restore-verification.json','independent-master-open.json','package_doc_handoff.py']:
  z.write(c/name,'handoff/'+name)
 for r in records:
  for prefix in ['verified-','uploaded-']:
   f=c/(prefix+r['id']+'.json');z.write(f,'handoff/drive-receipts/'+f.name)
b=zp.read_bytes();item={'name':zp.name,'path':str(zp),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'folder':'checkpoint'}
(c/'HANDOFF-UPLOAD-QUEUE.json').write_text(json.dumps([item],indent=2)+'\n')
print(json.dumps({'status':status,'sidecar':item},indent=2))
