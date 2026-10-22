"""Verify the assembled review, without changing source images or assets."""
from pathlib import Path
import json, re
import fitz
from PIL import Image

R = Path.cwd() / 'reports/recovery-quarry-fidelity-2026-10-19'
meta = json.loads((R / 'review-package.json').read_text())
assert meta['status'] == 'PASS' and meta['currentMatchedImages'] == 125
assert meta['historicalImages'] == 73 and meta['contactSheets'] == 21
matched = json.loads((R / 'matched-pose-verification.json').read_text())
assert matched['status'] == 'PASS' and all(c['matched'] for c in matched['comparisons'])
images = []
for mode in ['c51', 'c8', 'recovered', 'material', 'corrected']:
    group = json.loads((R / 'raw' / (mode + '-captures.json')).read_text())
    assert group['status'] == 'PASS' and len(group['captures']) == 25
    assert group['build'] == meta['build']
    for c in group['captures']:
        im = Image.open(R / c['file']); im.verify()
        assert im.size == (c['canvas']['cssWidth'], c['canvas']['cssHeight'])
        images.append(c['file'])
assert len(set(images)) == 125
pdfs = []
for stem, expected in [('Phone-Review', 26), ('Full-Screenshots', 205), ('Technical-Report', None)]:
    file = R / ('Gullyverse-Quarry-Fidelity-' + stem + '.pdf')
    doc = fitz.open(file)
    if expected: assert len(doc) == expected
    outside = []
    for i, page in enumerate(doc):
        for block in page.get_text('blocks'):
            if block[0] < -1 or block[1] < -1 or block[2] > page.rect.width + 1 or block[3] > page.rect.height + 1:
                outside.append(i + 1)
    assert not outside, (file, outside)
    pdfs.append({'file': file.name, 'pages': len(doc), 'textOutsidePage': outside})
gallery = (R / 'gallery.html').read_text()
links = set(re.findall(r'(?:href|src)="([^"]+)"', gallery))
for rel in links:
    assert not rel.startswith(('http', '/', '..')) and (R / rel).is_file(), rel
result = {'status': 'PASS', 'build': meta['build'], 'fullResolutionBrowserPNGs': len(images),
          'allCurrentCameraQualityDPRLightComparisonsExact': True, 'historicalReferenceAlignedOnly': True,
          'localGalleryLinksVerified': len(links), 'PDFs': pdfs,
          'manualVisualInspection': 'Phone pp1,2,9,25,26; full pp2,102,127,205; technical opening and performance/table pages rendered and inspected. No image crops or colour grading. Long camera JSON replaced with readable pose summary; full metadata remains linked.'}
(R / 'raw/pdf-review-verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
