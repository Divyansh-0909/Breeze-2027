from pathlib import Path
import json,hashlib,subprocess,re,html
from PIL import Image
root=Path.cwd();r=root/'reports/current-final-review-2026-10-11';raw=r/'raw'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.load(open(raw/'source-hashes-before.json'));after={k:hashfile(root/k) if (root/k).is_file() else None for k in before};(raw/'source-hashes-after.json').write_text(json.dumps(after,indent=2))
changed=[k for k in before if before[k]!=after[k]]
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip();diff=subprocess.check_output(['git','diff','--name-only'],text=True);staged=subprocess.check_output(['git','diff','--cached','--name-only'],text=True);status=subprocess.check_output(['git','status','--short'],text=True)
(raw/'git-status-after.txt').write_text(status)
audit=root/'reports/verification-2026-10-10';manifest=json.load(open(audit/'raw/artifact-manifest.json'));bad=[]
for v in manifest['artifacts']:
 p=audit/v['path']
 if not p.is_file() or hashfile(p)!=v['sha256']:bad.append(v['path'])
# Tracked old reports are independently unchanged from starting HEAD; nonindexed files are not claimed hash-verified.
integrity={'startingHead':'e3dbbc233f1f12f5e4d96333db3b797e75da4760','finalHead':head,'branch':branch,'comparedSourceConfigAssetFiles':len(before),'changedSourceConfigAssetFiles':changed,'stagedChangedFiles':staged.splitlines(),'trackedChangedFiles':diff.splitlines(),'currentStatus':status.splitlines(),'OctoberArtifactManifestChecked':len(manifest['artifacts']),'OctoberManifestMismatches':bad,'scope':'664 pre-existing source/config/asset hashes plus git tracked diff. October historical manifest is checked independently; files not indexed there are not claimed exhaustively hash-proven. All writes in this task are new review artifacts or ignored build/test caches.'}
(raw/'integrity.json').write_text(json.dumps(integrity,indent=2));assert not changed and not staged and not diff;assert head==integrity['startingHead']
core={c['file']:c for c in json.load(open(raw/'capture-metadata.json'))['captures']};imgs=[]
for p in sorted(r.rglob('*.png')):
 rel=p.relative_to(r).as_posix();im=Image.open(p);is_hist=rel.startswith(('references/','historical/'));m=core.get(rel)
 imgs.append({'file':rel,'width':im.width,'height':im.height,'sha256':hashfile(p),'classification':'historical/reference copy' if is_hist else 'actual current browser capture' if not rel.endswith(('frame-intervals.png','resource-lifecycle.png')) else 'raw-data plot','metadata':m if m else {'camera':'unmeasured or not applicable; supplemental test/fallback/isolated viewer or historical evidence','note':'See associated raw result JSON; no camera or hardware pose inferred from pixels.'}})
(raw/'all-screenshot-metadata.json').write_text(json.dumps({'coreMeasuredCaptures':len(core),'allPNGCount':len(imgs),'captures':imgs},indent=2))
# Validate documentation and gallery relative file links. Historical reports are labeled .txt, not rendered as current relative-link reports.
missing=[];count=0
for p in [root/'docs/gullyverse-current-final-review.md',root/'docs/gullyverse-current-visual-baseline.md',r/'gallery.html',r/'START-HERE.html',r/'PHYSICAL-DEVICE-PROCEDURE.md']:
 text=p.read_text()
 links=re.findall(r'\]\((<[^>]+>|[^\s)]+)\)',text) if p.suffix=='.md' else re.findall(r'(?:href|src)="([^"]+)"',text)
 for link in links:
  link=html.unescape(link.strip('<>')).split('#')[0]
  if not link or re.match(r'^[a-z]+:',link):continue
  count+=1
  if not (p.parent/link).exists():missing.append({'document':str(p.relative_to(root)),'target':link})
files=[root/'docs/gullyverse-current-final-review.md',root/'docs/gullyverse-current-visual-baseline.md']+[p for p in r.rglob('*') if p.is_file()]
for p in files:
 assert p.name not in ['.env','.env.local'] and '.vercel' not in p.parts and '.git' not in p.parts
placeholders=[str(p.relative_to(root)) for p in files[:2] if '<!--' in p.read_text()]
result={'relativeLinksChecked':count,'missingLinks':missing,'unresolvedReportPlaceholders':placeholders,'coreMeasuredCaptures':len(core),'allPNGCount':len(imgs),'packagedFilesPlanned':len(files),'secretEnvironmentOrAuthPathsIncluded':False,'productionUnchanged':not changed,'historicalAuditManifestMismatches':bad,'status':'PASS' if not missing and not placeholders and not changed else 'FAIL'}
(raw/'package-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert not missing and not placeholders
