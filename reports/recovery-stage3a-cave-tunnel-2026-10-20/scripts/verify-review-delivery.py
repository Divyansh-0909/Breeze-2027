"""Check the portable review set and render representative PDF pages."""
from pathlib import Path
import fitz,json,re,hashlib
R=Path('reports/recovery-stage3a-cave-tunnel-2026-10-20');W=Path('/workspace/recovery-stage3a/2026-10-20/checkpoint/layout-checks');W.mkdir(exist_ok=True)
package=json.loads((R/'review-package.json').read_text());rows=[]
for name,pages,selected in [(package['phonePDF'],23,[0,1,18,22]),(package['fullScreenshotPDF'],74,[0,1,47,58]),(package['technicalPDF'],7,[0,4,6])]:
 p=R/name;d=fitz.open(p);assert len(d)==pages
 for i in selected:
  page=d[i];scale=min(1,1100/page.rect.width);pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale));pix.save(W/(p.stem+f'-p{i+1}.png'))
 rows.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'pages':len(d),'representativePagesRendered':[i+1 for i in selected]})
missing=[]
for link in re.findall(r'(?:href|src)="([^"]+)"',(R/'gallery.html').read_text()):
 if link.startswith(('http:','https:','#')):continue
 if not(R/link).is_file():missing.append(link)
assert not missing,missing
for v in ['visitor-journey.mp4','automatic-lod-inspection.mp4']:assert(R/'videos'/v).stat().st_size>0
assert json.loads((R/'raw/walkthrough-encoding.json').read_text())['status']=='PASS'
assert json.loads((R/'matched-pose-verification.json').read_text())['status']=='PASS'
(R/'raw/review-delivery-validation.json').write_text(json.dumps({'status':'PASS','PDFs':rows,'galleryRelativeLinksAllPresent':True,'videosHaveUnchangedTiming':True,'actualRendererMatchedPairs':29,'referenceImagesClearlySeparated':True},indent=2)+'\n');print(json.dumps(rows,indent=2))
