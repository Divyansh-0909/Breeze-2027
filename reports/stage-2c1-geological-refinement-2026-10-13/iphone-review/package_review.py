"""Package existing browser evidence for iPhone review; never alter production files."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
import re
import subprocess
import zipfile

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
PROJECT = EVIDENCE.parent.parent
PDF = HERE / 'Gullyverse-Stage-2C1-iPhone-Review.pdf'
ZIP = PROJECT / 'gullyverse-stage-2c1-iphone-review.zip'
W, H, M = 420, 840, 24
INK, MUTED, GREEN = map(HexColor, ['#202932', '#56636F', '#23654D'])
pdfmetrics.registerFont(TTFont('ReviewSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ReviewSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

DESKTOP = [
 ('desktop-01-matched-wall.png', '01  Wall at the same camera', 'Compare broad wall shape and the upper contour.'),
 ('desktop-02-two-section-join.png', '02  Two-section connection', 'Check that the adjoining sections read as one formation.'),
 ('desktop-03-close-fractures.png', '03  Close-up fractures', 'Check chipped edges and the locked limestone surface grain.'),
 ('desktop-04-medium-wall.png', '04  Medium-distance wall', 'Judge the geology at an ordinary viewing distance.'),
 ('desktop-05-low-angle-crest.png', '05  Low-angle upper edge', 'Look for remaining sharp peaks or artificial wall terminations.'),
 ('desktop-06-along-wall.png', '06  Looking along the wall', 'Inspect volume, recesses and the relationship to nearby rocks.'),
 ('desktop-07-quarry-context.png', '07  Quarry context', 'Only the selected pair is refined; the rest remains Stage 2C.'),
 ('desktop-08-aerial-map.png', '08  Aerial map', 'Check the perimeter segment within the unchanged quarry footprint.'),
 ('desktop-09-far-wall.png', '09  Long-distance wall', 'Check the silhouette and how the pair sits among the other walls.'),
 ('desktop-10-seam-close.png', '10  Join close-up', 'The near-vertical highlighted joint is a remaining review point.'),
 ('desktop-11-stage-lighting.png', '11  Aftermovie lighting', 'Same camera and stage lighting; check the limestone response.'),
]
MOBILE = [
 ('mobile-01-matched-wall.png', '12  Portrait wall view'),
 ('mobile-04-medium-wall.png', '13  Portrait medium view'),
 ('mobile-07-quarry-context.png', '14  Portrait quarry context'),
 ('mobile-08-aerial-map.png', '15  Portrait aerial map'),
]
LODS = [('near.png', '16  Near detail - LOD0'),
        ('middle.png', '17  Middle detail - LOD1'),
        ('distant-map.png', '18  Aerial detail - LOD2')]
DIAGNOSTICS = [('normal-disabled', '19  Normal-map isolation'),
               ('normals', '20  Geometry normals'),
               ('wireframe', '21  Mesh wireframe')]

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=PROJECT, text=True)

all_images = [p for folder in ['before', 'after', 'lod', 'diagnostics']
              for p in sorted((EVIDENCE / folder).glob('*.png'))]
protected = all_images + [EVIDENCE / 'recordings/geology-inspection-walkthrough.mp4',
                         PROJECT / 'docs/gullyverse-stage-2c1-geological-refinement.md']
initial_hashes = {str(p): digest(p) for p in protected}
initial_diff = git('diff', 'HEAD', '--', '.', ':!reports', ':!docs')
initial_head = git('rev-parse', 'HEAD').strip()
branch = git('branch', '--show-current').strip()

c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle('Gullyverse Stage 2C.1 - iPhone Visual Review')
c.setAuthor('Breeze 2027 / Gullyverse')
c.setSubject('Actual browser screenshots of the reversible two-section limestone refinement')
page = 0

def textline(text, x, y, size=12, bold=False, color=INK):
    c.setFillColor(color)
    c.setFont('ReviewSans-Bold' if bold else 'ReviewSans', size)
    c.drawString(x, y, text)

def paragraph(text, x, y, width=W-2*M, size=13, leading=19, color=INK):
    words, line = text.split(), ''
    c.setFont('ReviewSans', size)
    for word in words:
        candidate = (line + ' ' + word).strip()
        if c.stringWidth(candidate, 'ReviewSans', size) > width and line:
            textline(line, x, y, size, color=color)
            y -= leading
            line = word
        else:
            line = candidate
    if line:
        textline(line, x, y, size, color=color)
        y -= leading
    return y

def begin(title, subtitle='Actual website captures - original PNGs available in the ZIP'):
    global page
    page += 1
    c.setFillColor(HexColor('#FAFBFC'))
    c.rect(0, 0, W, H, fill=1, stroke=0)
    textline('GULLYVERSE  /  STAGE 2C.1', M, H-28, 10, True, GREEN)
    textline(title, M, H-58, 17, True)
    paragraph(subtitle, M, H-80, size=10, leading=14, color=MUTED)
    c.setStrokeColor(HexColor('#D6DDE3'))
    c.line(M, 35, W-M, 35)
    textline('Two-section proof only  |  13 October 2026', M, 20, 9, color=MUTED)
    textline(str(page), W-M-16, 20, 9, color=MUTED)

def image_fit(path, x, top, width, max_height):
    with Image.open(path) as im:
        iw, ih = im.size
        encoded = BytesIO()
        im.convert('RGB').save(encoded, format='JPEG', quality=94, subsampling=0, optimize=True)
    encoded.seek(0)
    scale = min(width/iw, max_height/ih)
    dw, dh = iw*scale, ih*scale
    c.drawImage(ImageReader(encoded), x+(width-dw)/2, top-dh,
                dw, dh, preserveAspectRatio=True, mask='auto')
    return top-dh

def pair_page(title, before, after, note, diagnostic=False):
    begin(title, 'Diagnostic view - not the final material' if diagnostic else
          'Matched camera, lighting, viewport, quality and effective DPR')
    y = 720
    textline('BEFORE - existing Stage 2C', M, y, 12, True)
    y = image_fit(before, M, y-12, W-2*M, 248) - 26
    textline('AFTER - refined sections 22 + 23', M, y, 12, True, GREEN)
    y = image_fit(after, M, y-12, W-2*M, 248) - 22
    paragraph(note, M, y, size=12, leading=17, color=MUTED)
    c.showPage()

begin('Your iPhone review guide', 'PDF + original screenshots + H.264 MP4 walkthrough')
y = 711
for heading, body in [
 ('What changed', 'Two adjoining limestone wall sections were reshaped into one continuous geological volume. The rest of the quarry is unchanged.'),
 ('What stayed locked', 'The approved limestone maps, colour, lighting, quarry footprint, stage, scaffold and navigation are preserved. The public default still uses Stage 2C.'),
 ('How to review', 'Swipe through the matched pairs and pinch to zoom. This PDF uses high-quality image compression for a smaller download. All original PNGs are in the ZIP.'),
 ('On your iPhone', 'Save this PDF to Files or Books. Open the MP4 in Files. Tap the review ZIP in Files to extract all original PNGs, metadata and the report.'),
 ('About the video', 'Actual browser inspection-camera travel alongside the wall, followed by the public aerial map. It is an inspection path, not a demonstration of ordinary walking bounds.'),
 ('Device testing', 'Phone-sized captures use browser emulation. Physical iPhone, Android and hardware-GPU performance remain pending. The recording used software rendering.'),
]:
    textline(heading, M, y, 14, True)
    y = paragraph(body, M, y-23, size=13, leading=19) - 19
c.showPage()

for filename, title, note in DESKTOP:
    pair_page(title, EVIDENCE/'before'/filename, EVIDENCE/'after'/filename, note)

for filename, title in MOBILE:
    for folder, label in [('before', 'BEFORE - existing Stage 2C'),
                          ('after', 'AFTER - refined pair')]:
        begin(title, label + ' | 390 x 844 browser viewport, not physical iPhone profiling')
        image_fit(EVIDENCE/folder/filename, M, 720, W-2*M, 665)
        c.showPage()

for filename, title in LODS:
    begin(title, 'Actual runtime-selected level; only one visual LOD drawn at a time')
    y = image_fit(EVIDENCE/'lod'/filename, M, 714, W-2*M, 600) - 28
    paragraph('These images are taken at different distances. They document real LOD selection; they are not matched-camera before/after pairs.', M, y, size=13)
    c.showPage()

for suffix, title in DIAGNOSTICS:
    pair_page(title, EVIDENCE/'diagnostics'/f'before-{suffix}.png',
              EVIDENCE/'diagnostics'/f'after-{suffix}.png',
              'Optional diagnostic capture for the dark-recess investigation. The normal review screenshots use the unchanged approved material.', True)

begin('What to look for', 'Visual review remains open; no rollout beyond this pair')
y = 706
for t in [
 'Does the upper wall read as an excavated quarry rather than repeated pointed mountains?',
 'Do the adjoining sections feel connected from the front and from an oblique angle?',
 'Does the highlighted near-vertical joint look like a believable fracture, or still like a seam?',
 'Does the limestone retain the colour, grain and roughness you approved?',
 'Are the top and ground transitions convincing at close, medium and far distances?',
]:
    y = paragraph(t, M, y, size=15, leading=22) - 22
textline('Included technical evidence', M, y, 15, True)
y = paragraph('The ZIP contains the original report, camera metadata, test summary and resource measurements. Editable Blender sources and runtime GLBs remain in the separate full technical ZIP.', M, y-26, size=13)
y -= 20
paragraph(f'Starting branch: {branch}. Revision: {initial_head[:12]}. No commit, push or deployment was performed for this review package.', M, y, size=11, leading=17, color=MUTED)
c.showPage()
c.save()

notes = '''GULLYVERSE STAGE 2C.1 - IPHONE REVIEW

Start with 01-Visual-Review.pdf.
Open it in Files or Books. Pinch to zoom into fractures and joins.
Then open 02-Wall-Walkthrough.mp4 in Files for the actual browser recording.
The MP4 is H.264, 1366 x 900, 73.4 seconds.

Screenshots/before and Screenshots/after contain 15 matched pairs:
11 desktop views and 4 portrait views. Every PNG retains its original
resolution and exact file bytes. The PDF uses high-quality JPEG encoding
without reducing image dimensions; use the PNGs for exact pixel inspection.
Screenshots/lod has 3 selected runtime detail levels.
Screenshots/diagnostics has 6 shading/mesh diagnostic images; those do
not represent the approved normal material appearance.

Only sections 22 and 23 are refined. The rest stays at Stage 2C.
Limestone maps, lighting, stage, layout, navigation and production-default
appearance remain unchanged. This is a reversible opt-in proof.
The near-vertical highlighted joint remains a visual-review point.

The walkthrough uses a labelled inspection camera alongside the wall,
then the actual public aerial map. It is not a claim that normal walking
controls can cross the existing movement boundaries.

Portrait images use phone-sized browser emulation. Physical iPhone,
Android and laptop-GPU testing remain pending. Rendering here used
SwiftShader software graphics, not an iPhone GPU.

Report.md includes full findings. Evidence/ contains capture metadata,
tests, lifecycle counters and performance measurements.
Blender .blend source and GLBs are in the separate full technical ZIP;
they are not needed for visual review on iPhone.

No website implementation was changed while creating this package.
No commit, push or deployment was performed.
'''
(HERE/'START-HERE.txt').write_text(notes)

metadata = {
 'createdAt': datetime.now(timezone.utc).isoformat(),
 'branch': branch, 'head': initial_head,
 'scope': 'Repackage existing Stage 2C.1 evidence only; no implementation changes',
 'mobileStatus': 'Browser-emulated portrait views, not physical iPhone benchmarks',
 'screenshots': [{
     'file': str(p.relative_to(EVIDENCE)),
     'archivePath': 'Screenshots/'+str(p.relative_to(EVIDENCE)),
     'sizeBytes': p.stat().st_size,
     'sha256': digest(p), 'dimensions': list(Image.open(p).size),
 } for p in all_images],
 'pdfPages': len(PdfReader(str(PDF)).pages),
 'pdfImageEncoding': 'JPEG quality 94, 4:4:4, original pixel dimensions; original PNG bytes unchanged in ZIP',
 'video': {'durationSeconds': 73.4, 'codec': 'h264', 'viewport': [1366, 900],
           'method': 'Actual browser inspection-camera walkthrough and public map',
           'sha256': digest(EVIDENCE/'recordings/geology-inspection-walkthrough.mp4')},
}
(HERE/'review-metadata.json').write_text(json.dumps(metadata, indent=2)+'\n')

files = [(PDF, '01-Visual-Review.pdf'),
         (EVIDENCE/'recordings/geology-inspection-walkthrough.mp4', '02-Wall-Walkthrough.mp4'),
         (HERE/'START-HERE.txt', 'START-HERE.txt'),
         (HERE/'review-metadata.json', 'review-metadata.json'),
        ]
files.extend((p, 'Screenshots/'+str(p.relative_to(EVIDENCE))) for p in all_images)
for filename in ['before-captures.json', 'after-captures.json', 'capture-pair-validation.json',
                 'stage-lighting-comparison.json', 'lod-walkthrough.json', 'test-summary.json',
                 'hardware-profile.json', 'before-performance.json', 'after-performance.json',
                 'lifecycle.json', 'navigation-cycles.json', 'video-with-wall.json',
                 'asset-inventory.json', 'local-hardware-procedure.md']:
    p = EVIDENCE/'raw'/filename
    if p.exists(): files.append((p, 'Evidence/'+filename))

# Resolve links in the distributed copy without touching the original report.
# Authoring binaries stay in the separate full technical archive.
report_source = PROJECT/'docs/gullyverse-stage-2c1-geological-refinement.md'
report_text = report_source.read_text()
def rewrite_link(match):
    label, target = match.group(1), match.group(2)
    path = (report_source.parent/target).resolve()
    if path.parent == EVIDENCE/'raw' and path.exists():
        arc = 'Evidence/'+path.name
        if not any(a == arc for _, a in files): files.append((path, arc))
        return f'[{label}]({arc})'
    if path == EVIDENCE/'gallery.html':
        return '[**Open the PDF comparison gallery**](01-Visual-Review.pdf)'
    if path.name == 'geology-inspection-walkthrough.mp4':
        return f'[{label}](02-Wall-Walkthrough.mp4)'
    return f'{label} (available in the separate full technical ZIP)'
report_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', rewrite_link, report_text)
(HERE/'Review-Report.md').write_text(report_text)
files.append((HERE/'Review-Report.md', 'Report.md'))
archive_names = {arc for _, arc in files}
for target in re.findall(r'\]\(([^)]+)\)', report_text):
    assert target in archive_names, 'Unresolved distributed report link: '+target

with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path, arc in files: z.write(path, arc)

with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None, 'ZIP CRC validation failed'
    for p, arc in files:
        assert sha256(z.read(arc)).hexdigest() == digest(p), arc

assert all(digest(Path(p)) == h for p, h in initial_hashes.items()), 'Original evidence changed'
assert git('rev-parse', 'HEAD').strip() == initial_head, 'HEAD changed'
assert git('diff', 'HEAD', '--', '.', ':!reports', ':!docs') == initial_diff, 'Production diff changed'
result = {'status': 'PASS', 'pdfPages': metadata['pdfPages'], 'pngCount': len(all_images),
          'zipEntries': len(files), 'originalEvidencePreserved': True,
          'productionDiffUnchanged': True, 'headUnchanged': True,
          'pdf': {'path': str(PDF), 'sizeBytes': PDF.stat().st_size, 'sha256': digest(PDF)},
          'zip': {'path': str(ZIP), 'sizeBytes': ZIP.stat().st_size, 'sha256': digest(ZIP)}}
(HERE/'package-validation.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
