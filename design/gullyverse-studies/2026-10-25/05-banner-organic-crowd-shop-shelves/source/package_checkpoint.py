"""Create complementary archives and exact member hashes, excluding caches/receipts."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,shutil
O=Path(__file__).resolve().parents[1]; C=O/'checkpoint';C.mkdir(exist_ok=True)
def sha(p):
    with p.open('rb')as h:return hashlib.file_digest(h,'sha256').hexdigest()
web=Path('/workspace/Breeze-2027-wip-push')
b=json.loads((O/'evidence/website-baseline.json').read_text())
assert all(sha(web/r['file'])==r['sha256']for r in b['files'])
for field,args in [('gitStatus',['status','--porcelain']),('branch',['branch','--show-current']),('HEAD',['rev-parse','HEAD'])]:
    current=subprocess.check_output(['git',*args],cwd=web,text=True)
    assert current.rstrip()==b[field].rstrip(),field
(O/'evidence/website-final-preservation.json').write_text(json.dumps({'status':'PASS','protectedFilesChecked':len(b['files']),'branch':b['branch'],'HEAD':b['HEAD'],'gitStatusIdentical':True,'noWebsiteWrites':True},indent=2)+'\n')
shutil.copy2(C/'test_proposed_cavity.py',O/'source/test_proposed_cavity.py')
f=O/'source/test_proposed_cavity.py';s=f.read_text().replace("Path('/workspace/gullyverse-world-concept/2026-10-25/05-banner-organic-crowd-shop-shelves')","Path(__file__).resolve().parents[1]");f.write_text(s)
provenance={'phase':'Rev05A','status':'PARTIAL_SHOP_EXCEPTION_PENDING','newExternalMeshSources':[],'crowdSource':'Inherited neutral procedural low-poly eight-part proxies from protected Rev04. Linked source mesh data; no real-person identity claim.','newArt':'Only diagnostic charts and comparison layouts; no new final artist artwork.','inheritedSourceAndRights':'source/provenance/asset-provenance.json and material-provenance.json retain original attributions/rights. Project portrait, branding and film assets are not CC0.','baselineMaster':{'file':'source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend','sha256':'6041c26ac21fd990f14e2dae0fbe2cad15c21739f045d8cf56b7b8439a9e239a'},'reviewMaster':{'file':'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend','sha256':sha(O/'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend')},'userBannerReference':{'file':'evidence/user-banner-reference.png','sha256':sha(O/'evidence/user-banner-reference.png'),'license':'User-supplied correction reference, not redistributed as public stock art.'},'conditionalShopScript':'Prepared proposal only, requires pending explicit small interior-recess exception.'}
(O/'source/provenance/REV05A-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
members=[]
for root in ['source','evidence','review','renders']:
    for p in sorted((O/root).rglob('*')):
        if p.is_file()and'__pycache__'not in p.parts and p.suffix not in {'.pyc','.blend1'}:members.append(p)
members += [O/n for n in ['REPORT.md','RESTORE.md','GALLERY.html']]
members=sorted(set(members))
(O/'FILE-SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(O).as_posix()}\n'for p in members))
manifest={'phase':'Rev05A','status':'PARTIAL_SHOP_EXCEPTION_PENDING','memberCount':len(members),'note':'Manifest itself and archive/checkpoint receipts are sidecars, excluded from self-referential hashes. All four archives are needed for the complete gallery; packed master opens on its own.','files':[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in members]}
(O/'FILE-MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
base=[p for p in members if'renders'!=p.relative_to(O).parts[0]]+[O/'FILE-SHA256SUMS.txt',O/'FILE-MANIFEST.json']
groups={'Rev05A-Source-and-Reports.zip':base}
for v in ['A','B','C']:groups[f'Rev05A-Images-{v}.zip']=[p for p in members if p.relative_to(O).parts[0]=='renders'and p.relative_to(O).parts[2]==v]
archives=[]
for name,files in groups.items():
    target=C/name
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in files:z.write(p,p.relative_to(O).as_posix())
    assert target.stat().st_size<49*1024*1024
    archives.append({'file':name,'bytes':target.stat().st_size,'sha256':sha(target),'members':len(files),'required':True})
index={'phase':'Rev05A','handoff':'WORLD-BANNER-ORGANIC-CROWD-SHELVES-PENDING-20261025-05A','status':'PARTIAL_SHOP_EXCEPTION_PENDING','extractAllIntoSameEmptyDirectory':True,'baselineIncludedAndUnchanged':True,'archives':archives,'memberManifestSHA256':sha(O/'FILE-MANIFEST.json'),'memberSHA256SUMS':sha(O/'FILE-SHA256SUMS.txt'),'independentRestore':'Recorded after extraction in a separate verification receipt.','noWebsiteBackupClaim':'This checkpoint is the Blender-only correction; website history remains in prior protected checkpoints.'}
(C/'ARCHIVE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
upload=[O/'review/Gullyverse-Rev05A-Banner-Crowd-Pending-Shops.pdf',O/'REPORT.md',O/'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend',O/'review/B-Banner-Removed.jpg',O/'review/C-Organic-Audience.jpg',O/'review/C-Audience-Plan.jpg',O/'review/shop-interior-exception-proposal.png']+[C/a['file']for a in archives]+[C/'ARCHIVE-INDEX.json']
(C/'upload-inventory.json').write_text(json.dumps([{'path':str(p),'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'folder':'checkpoint'if p.parent==C or p.suffix=='.blend'else'review'}for p in upload],indent=2)+'\n')
print('CHECKPOINT_BUILT',len(members),'files',[(a['file'],a['bytes'])for a in archives],flush=True)
