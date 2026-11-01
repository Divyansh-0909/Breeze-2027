from pathlib import Path
import hashlib,json,zipfile,datetime
p=Path(__file__).resolve().parents[1]
c=p/'checkpoint'
queue=json.loads((c/'UPLOAD-QUEUE.json').read_text())
uploaded=[json.loads(x.read_text()) for x in c.glob('uploaded-*.json')]
records=[]
for q in queue:
 matches=[x for x in uploaded if x['name']==q['name']]
 assert len(matches)==1,q['name']
 r=matches[0]
 assert r['bytes']==q['bytes'] and r['sha256']==q['sha256'] and r['fullDownloadBackSHA256Verified']
 raw=Path(q['path']).read_bytes()
 assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256']
 receipt=json.loads((c/('verified-'+r['id']+'.json')).read_text())
 assert receipt['verified'] and receipt['bytes']==r['bytes'] and receipt['sha256']==r['sha256']
 records.append({k:r[k] for k in ['name','id','url','parent','bytes','sha256','fullDownloadBackSHA256Verified']})
restore=json.loads((c/'independent-restore-verification.json').read_text())
master=json.loads((c/'independent-master-open.json').read_text())
assert restore['status']=='PASS' and master['status']=='PASS'
qa={'status':'PASS','reviewedActualScenePNGs':['after/A/ART-neha-kakkar-grazing.png','after/B/01-landing.png'],
 'phonePDFPagesVisuallyInspected':[2,4,11,15,23],'fullPDFPagesVisuallyInspected':[26,46],
 'observations':['Original lettering, saturated colour and silver/white highlights remain visible on dark shutter metal.',
 'Grazing views show true profiled slats deforming the paint shading; no floating image plane or white background rectangle.',
 'Four generated non-name wall compositions are labelled proposals, with their raw atlas distinguished from scene renders.',
 'PDF captions distinguish neutral-metal diagnostics from painted scene comparisons; matched-pose metadata is explicit.',
 'The broader environment remains a blockout, and this inspection does not award final visual approval.']}
(c/'FINAL-VISUAL-QA.json').write_text(json.dumps(qa,indent=2)+'\n')
proof={'status':'EXTERNALLY_VERIFIED','timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'handoffId':'WORLD-REV05C-CORRUGATED-ART-20261027-8b178dd8',
 'method':'Authenticated Google Drive upload; parent/size check; full streamed download-back SHA-256. No signed download URL retained.',
 'finalFilesVerified':len(records),'complementaryArchives':6,'finalFiles':records,
 'independentRestore':restore,'independentPackedMaster':master,'finalVisualQA':qa,
 'reviewFolder':json.loads((c/'drive-folders.json').read_text())['review']['url'],
 'checkpointFolder':json.loads((c/'drive-folders.json').read_text())['checkpoint']['url'],
 'preservedEarlierCheckpoints':True,'websiteUnchanged':True,'supportOffLocked':True,
 'limitations':['Private Blender art only; no live/WIP promotion or browser/device performance certification.',
 'Four supporting wall placements and A/B/C choice require user visual review.',
 'Two inherited scooter-side approach failures remain documented.'],
 'selfReferencePolicy':'This receipt describes the 17 frozen final payload/index files. Its own upload verification and the Doc handoff proof are separate sidecars.'}
(c/'FINAL-DELIVERY-VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n')
by={r['name']:r for r in records}
lines=['# Rev05C shutter art — verified delivery','',proof['handoffId'],'',
 'Private Blender implementation. SUPPORT OFF remains locked; website unchanged. Stop for user visual review.','',
 '## Review','']
for name in ['Gullyverse-Rev05C-Shutter-Graffiti-Review.pdf','Gullyverse-Rev05C-Full-Art-Comparisons.pdf','REPORT.md','Shutter-Chaar-Diwari.png','Shutter-Ritviz.png','Shutter-Neha-Kakkar.png']:
 lines.append(f'- [{name}]({by[name]["url"]})')
lines+=['','## Complete independent restoration','',
 'Download ALL six complementary ZIPs below and extract them into the SAME fresh directory. Read RESTORE.md and verify FILE-SHA256SUMS.txt. These contain the packed input and new master, source images, derived paint maps/masks, raw generated assets, scripts, provenance, PDFs and full-resolution render evidence. No older workspace is needed for this private Blender study.','']
for r in records:
 if r['name'].endswith('.zip'):
  lines.append(f'- [{r["name"]}]({r["url"]}) — {r["bytes"]:,} bytes; SHA-256 `{r["sha256"]}`')
lines+=['','## Restore metadata / direct master','']
for name in ['Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend','ARCHIVE-INDEX.json','FILE-MANIFEST.json','FILE-SHA256SUMS.txt','RESTORE.md']:
 lines.append(f'- [{name}]({by[name]["url"]})')
lines+=['',f'Fresh restore: {restore["memberHashesVerified"]} member hashes, {restore["galleryRelativeReferencesVerified"]} gallery references and packed master reopened successfully. All 17 final payload/index files passed complete authenticated download-back SHA-256.',
 '',f'Checkpoint folder: {proof["checkpointFolder"]}',
 '', 'The earlier working-source snapshot is retained as historical interim evidence; the six final ZIPs above are the complete delivery. No public asset, Git history or earlier checkpoint was modified.']
(c/'DELIVERY-LINKS.md').write_text('\n'.join(lines)+'\n')
zpath=c/'Rev05C-Art-Verification-Receipts.zip'
assert not zpath.exists()
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,6) as z:
 for f in [c/'FINAL-DELIVERY-VERIFICATION.json',c/'DELIVERY-LINKS.md',c/'FINAL-VISUAL-QA.json',
  c/'independent-restore-verification.json',c/'independent-master-open.json',c/'independent-master-open.log',
  c/'ARCHIVE-INDEX.json',p/'FILE-MANIFEST.json',p/'FILE-SHA256SUMS.txt',p/'RESTORE.md',Path(__file__)]:
  if f.exists():z.write(f, 'verification/'+f.name)
 for r in records:
  for prefix in ['verified-','uploaded-']:
   f=c/(prefix+r['id']+'.json');z.write(f,'verification/drive-receipts/'+f.name)
out=[]
for name in ['Rev05C-Art-Verification-Receipts.zip','FINAL-DELIVERY-VERIFICATION.json','DELIVERY-LINKS.md']:
 f=c/name;b=f.read_bytes();out.append({'name':name,'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'folder':'checkpoint'})
(c/'VERIFICATION-UPLOAD-QUEUE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':proof['status'],'finalFilesVerified':len(records),'memberHashes':restore['memberHashesVerified'],'sidecars':out},indent=2))
