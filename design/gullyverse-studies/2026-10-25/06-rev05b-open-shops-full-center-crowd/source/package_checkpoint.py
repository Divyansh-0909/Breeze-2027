from pathlib import Path
import json,hashlib,zipfile,subprocess
O=Path(__file__).resolve().parents[1];C=O/'checkpoint'
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert json.loads((O/'evidence/review-build.json').read_text())['matchedPairs']==75
web=Path('/workspace/Breeze-2027-wip-push');baseline=json.loads((O/'source/baseline/website-baseline.json').read_text())
assert all(sha(web/r['file'])==r['sha256']for r in baseline['files'])
for field,args in [('gitStatus',['status','--porcelain']),('branch',['branch','--show-current']),('HEAD',['rev-parse','HEAD'])]:assert subprocess.check_output(['git',*args],cwd=web,text=True).rstrip()==baseline[field].rstrip(),field
(O/'evidence/website-final-preservation.json').write_text(json.dumps({'status':'PASS','protectedFiles':len(baseline['files']),'branch':baseline['branch'],'HEAD':baseline['HEAD'],'gitStatusIdentical':True,'websiteWrites':False},indent=2)+'\n')
author=json.loads((O/'evidence/rev05b-authoring.json').read_text())
provenance={'task':'Rev05B','authorization':'source/baseline/REV05B-APPROVED-PROMPT.txt plus manual user approval','sourceMaster':{'file':'source/baseline/Rev05A.blend','sha256':sha(O/'source/baseline/Rev05A.blend')},'finalMaster':{'file':'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend','sha256':sha(O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend')},'newExternalMeshSources':[],'newTextures':[],'crowdSource':'Inherited neutral eight-part proxy meshes; 32 new linked instances, original mesh data reused. No new real-person or scan identity claim.','newGeometry':'Explicit authored cavity/trim topology in five open shop hosts; no Boolean union. Original external bounds preserved.','sourceRights':'Inherited asset-provenance.json/material-provenance.json/licenses are retained as ancestry. Current master packs every referenced image. Historical inventories may reference unused earlier authoring assets not required by this master.','projectImages':'Project portraits, branding and Aftermovie still retain original project rights. They are not CC0. Private authorized concept use.','polyHavenMaterials':'Existing scanned base materials retain recorded CC0 source provenance; no new source collection downloaded.','font':'Original raster/builtin font use remains; review PDF uses built-in Helvetica.'}
(O/'source/provenance/REV05B-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
members=[]
for root in ['source','evidence','review','renders']:
    members.extend(p for p in sorted((O/root).rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix not in {'.pyc','.blend1'})
members.extend(O/n for n in ['REPORT.md','RESTORE.md','GALLERY.html']);members.append(C/'drive-folders.json');members=sorted(set(members))
(O/'FILE-SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(O).as_posix()}\n'for p in members))
fm={'phase':'Rev05B','handoff':'WORLD-OPEN-SHOPS-FULL-CENTER-CROWD-20261025-05B','files':[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in members],'note':'This manifest, SHA256SUMS and post-upload receipts are excluded from self-referential member hashes.'};(O/'FILE-MANIFEST.json').write_text(json.dumps(fm,indent=2)+'\n')
groups={'Rev05B-Source-and-Tests.zip':[p for p in members if p.relative_to(O).parts[0]not in ['renders','review']]+[O/'FILE-SHA256SUMS.txt',O/'FILE-MANIFEST.json'],'Rev05B-Reviews.zip':[p for p in members if p.relative_to(O).parts[0]=='review']}
for v in ['A','B','C']:
    for ed in ['before','after']:groups[f'Rev05B-Images-{v}-{ed}.zip']=[p for p in members if p.relative_to(O).parts[:3]==('renders',ed,v)]
groups['Rev05B-Image-Diagnostics.zip']=[p for p in members if p.relative_to(O).parts[0]=='renders'and p.relative_to(O).parts[1]not in ['before','after']]
archives=[]
for name,files in groups.items():
    target=C/name
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in files:z.write(p,p.relative_to(O).as_posix())
    assert target.stat().st_size<49*1024*1024,name
    archives.append({'file':name,'bytes':target.stat().st_size,'sha256':sha(target),'memberCount':len(files),'required':True})
index={'handoff':fm['handoff'],'status':'IMPLEMENTED_READY_FOR_USER_VISUAL_REVIEW','allArchivesRequiredForCompleteGallery':True,'extractIntoSameFreshDirectory':True,'archives':archives,'memberCount':len(members),'fileManifestSHA256':sha(O/'FILE-MANIFEST.json'),'originalRev05ABaselineIncluded':True,'website':'No website patch or full website backup; protected WIP remains in separate historical checkpoints.','verification':'Full authenticated download-back and independent restored-master open results are post-upload sidecar receipts.'};(C/'ARCHIVE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
uploads=[O/'review/Gullyverse-Rev05B-Review.pdf',O/'review/Gullyverse-Rev05B-Full-Comparisons.pdf',O/'REPORT.md',O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend']+[O/'review'/n for n in ['Crowd-Center-Comparison.jpg','Crowd-Eye-Comparison.jpg','Open-Shop-Comparison.jpg']]+[C/x['file']for x in archives]+[C/'ARCHIVE-INDEX.json']
(C/'upload-inventory.json').write_text(json.dumps([{'path':str(p),'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'folder':'checkpoint'if p.parent==C or p.suffix=='.blend'else'review'}for p in uploads],indent=2)+'\n')
print('CHECKPOINT_BUILT',len(members),'members',len(archives),'archives',[(a['file'],a['bytes'])for a in archives],flush=True)
