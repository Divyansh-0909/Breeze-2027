from pathlib import Path
import json,hashlib,zipfile,shutil
W=Path(__file__).resolve().parent;O=W.parent;folders=json.load(open(O/'evidence/drive-folders.json'));a=json.load(open(W/'archives.json'));payloads=[]
for family in a:
 for f in family['parts']if family['parts']else[{'name':family['archive'],'bytes':family['bytes'],'sha256':family['sha256']}]:
  v=json.load(open(W/('verified-'+f['name']+'.json')));assert v['verified']and v['bytes']==f['bytes']and v['sha256']==f['sha256'];payloads.append(v)
proof=json.load(open(W/'restore-verification.json'));assert proof['files']==196 and proof['restoredBlender']['allUsedImagesPacked']
root=O/'RESTORE.md';shutil.copyfile(root,W/'RESTORE.md')
raw=json.load(open(W/'files-manifest.json'));final=json.load(open(W/'final-files-manifest.json'));overrides=[];seen={}
for r in raw:
 if r['file']in seen and r['sha256']!=seen[r['file']]['sha256']:overrides.append({'file':r['file'],'from':seen[r['file']]['sha256'],'to':r['sha256']})
 seen[r['file']]=r
index={'handoff':'WORLD-LANE-ROOFTOP-ABC-20261023-01','scope':'Private Blender concept only; no website files/defaults/commits/push/deployment changed. User A/B/C approval pending.','selfContainedBlenderMaster':True,'websiteRequiredToOpenMaster':False,'phase':folders['phase'],'subphase':folders['subphase'],'review':folders['review'],'checkpoint':folders['checkpoint'],'fullResolutionRenders':folders['renders'],'websiteBaseline':{'branch':'work-in-progress-2027','HEAD':'e638140b37045a805b23b4d406d387a8870f8486','filesIdentical':1213,'priorCanalFilesIdentical':311},'restoreOrder':[x['archive']for x in a],'archives':a,'requiredPayloadFiles':payloads,'requiredPayloadCount':len(payloads),'finalRestoredFiles':len(final),'finalRestoredBytes':proof['bytes'],'metadataOverrides':overrides,'fontCorrection':'Required final overlay uses actual font filepath <builtin>, not a guessed display name. Scene/render pixels unchanged.','standaloneMasterCopy':json.load(open(W/'verified-Gullyverse-Lane-Rooftop-ABC.blend.json')),'canonicalRenders':36,'animaticRenderedKeyframes':12,'phoneReviewPDFPages':19,'technicalReportPDFPages':6,'decision':'READY FOR USER CONCEPT REVIEW; C recommended, no selection/adoption. Static proxies, route pinch points and all runtime/device integration remain documented.','verification':'All required payloads fully downloaded back and SHA256-verified; final metadata/receipt verification follows as separate files.'}
assert len(payloads)==4 and len(overrides)==3
(W/'checkpoint-index.json').write_text(json.dumps(index,indent=2));(W/'SHA256SUMS.txt').write_text(''.join(v['sha256']+'  '+v['name']+'\n'for v in payloads)+''.join(v['sha256']+'  '+v['archive']+'\n'for v in a if v['parts']))
meta=['checkpoint-index.json','RESTORE.md','SHA256SUMS.txt','FILE-SHA256SUMS.txt','archives.json','files-manifest.json','final-files-manifest.json','restore-verification.json','restored-blender-read.json','restored-blender-read.log','verify_restore.py','check-restored-blender.py','font-probe.log','make_metadata.py','package.py']
p=W/'Gullyverse-Concept-Restoration-Metadata.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,6)as z:
 for name in meta:z.write(W/name,name)
with zipfile.ZipFile(p)as z:
 for name in meta:assert hashlib.sha256(z.read(name)).hexdigest()==hashlib.file_digest((W/name).open('rb'),'sha256').hexdigest()
print(json.dumps({'metadataZip':p.name,'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'payloadsVerified':len(payloads),'restoredFiles':196,'overrides':len(overrides)}))
