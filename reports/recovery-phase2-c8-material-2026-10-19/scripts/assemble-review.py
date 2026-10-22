"""Package genuine browser PNGs into an offline gallery and phone review PDF."""
from pathlib import Path
from io import BytesIO
import hashlib
import html
import json
import shutil

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path.cwd()
OUT = ROOT / "reports/recovery-phase2-c8-material-2026-10-19"
before = json.loads((OUT / "raw/c51-captures.json").read_text())
after = json.loads((OUT / "raw/c8-3x-captures.json").read_text())
assert before["status"] == after["status"] == "PASS"
byname = {Path(frame["file"]).name: frame for frame in before["captures"]}
pairs = []
for frame in after["captures"]:
    prior = byname[Path(frame["file"]).name]
    assert frame["data"]["camera"] == prior["data"]["camera"]
    assert frame["data"]["snapshot"]["quality"] == prior["data"]["snapshot"]["quality"] == 0
    assert abs(frame["canvas"]["effectiveDpr"] - prior["canvas"]["effectiveDpr"]) < 1e-10
    assert abs(frame["canvas"]["effectiveDpr"] - 1) < 1e-10
    assert frame["scanned"]["enabled"] and frame["scanned"]["scale"] == 3
    pairs.append({"title": frame["title"], "lighting": frame["lighting"], "note": frame["note"],
                  "before": prior["file"], "after": frame["file"],
                  "camera": frame["data"]["camera"], "viewport": frame["data"]["viewport"],
                  "effectiveDpr": frame["canvas"]["effectiveDpr"], "quality": 0})
(OUT / "raw/matched-pose-verification.json").write_text(json.dumps({"status": "PASS", "pairs": pairs,
    "sameGeometry": True, "sameApprovedGlobalLighting": True,
    "historicalC8ScreenshotComparison": "PENDING: companion Evidence ZIP unavailable; original report available"}, indent=2) + "\n")

reference_dir = OUT / "references"
reference_dir.mkdir(exist_ok=True)
for name in ["quarry-open-sky-geometry.jpeg", "quarry-warm-dappled-light.jpeg"]:
    shutil.copyfile(ROOT / "design/references/03-open-roof-quarry" / name, reference_dir / name)
parts = ["<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Gullyverse Recovery Phase 2 — C8 3×</title>",
         "<style>body{margin:0;background:#111714;color:#eee;font:16px/1.55 system-ui}main{max-width:1400px;margin:auto;padding:24px}a{color:#d4c28d}h1{font-size:clamp(24px,4vw,42px)}section{margin:30px 0;padding:18px;border:1px solid #465048;border-radius:10px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}figure{margin:0}img{width:100%;height:auto;display:block}figcaption{padding:8px 0}summary{cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}p{max-width:90ch}.notice{background:#3a3020}small{color:#ccc}@media(max-width:700px){main{padding:12px}.pair{grid-template-columns:1fr}}</style><main>",
         "<h1>BREEZE 2027 / GULLYVERSE<br>Recovery Phase 2 — C8 material at 3×</h1>",
         "<p>Actual-browser images. The continuous C5.1 geometry, collision, lighting, floor and venue remain unchanged. C8 is a private material preview on existing Wall_15, not recovered C6.2 geometry or new physical relief.</p>",
         "<p><a href='Gullyverse-Recovery-Phase2-C8-Review.pdf'>Phone review PDF</a> · <a href='https://drive.google.com/drive/folders/12pJVNnfimi4e-rbN_pNvhc2FmKsUoUj-'>Separate Phase 2 Drive folder</a> · <a href='raw/matched-pose-verification.json'>Exact comparison poses</a></p>",
         "<section class=notice><b>Historical comparison limitation</b><p>The original approved C8 report is available. Its companion 162-page screenshot/Evidence ZIP was not accessible in this task. These images compare preserved C5.1 with the reconstruction. They are not labelled as historical C8 screenshots, and pixel matching remains unverified. The original mask formula and C6.2 host are also missing.</p></section>",
         "<p>Default private selector: <code>?arrival=hub&amp;diagnostics&amp;quarryReview=scanned-material-multi</code>. Requires the existing development/preview gate. Default 3× = one-third UV0 repeat; explicit 1/2/3/4 controls remain. Normal/AO/roughness/colour stay aligned. No UV1 bake is fabricated.</p>"]
for index, pair in enumerate(pairs, 1):
    parts.extend([f"<section><h2>{index}. {html.escape(pair['title'])}</h2><p>{html.escape(pair['note'])} Lighting: {html.escape(pair['lighting'])}.</p><div class=pair>",
                  f"<figure><img loading=lazy src='{pair['before']}' alt='Preserved C5.1'><figcaption>Preserved C5.1</figcaption></figure>",
                  f"<figure><img loading=lazy src='{pair['after']}' alt='C8 3x material on C5.1'><figcaption>C8 scanned multi-material · 3× · same C5.1 mesh</figcaption></figure></div>",
                  "<details><summary>Camera and rendering metadata</summary><pre>" + html.escape(json.dumps({k:v for k,v in pair.items() if k not in ["before", "after"]}, indent=2)) + "</pre></details></section>"])
extras = []
controls = OUT / "raw/final-visual-controls.json"
if controls.exists():
    control = json.loads(controls.read_text())
    for frame in control["frames"]:
        extras.append((frame["file"], "Final build control: " + frame["mode"] + " · scale " + str(frame["scale"])))
for path in sorted((OUT / "screenshots").glob("automatic-lod-*.png")):
    extras.append((str(path.relative_to(OUT)), "Automatic LOD — non-public inspection: " + path.stem))
if (OUT / "screenshots/c8-stage-playing.png").exists():
    extras.append(("screenshots/c8-stage-playing.png", "Original Aftermovie playback with C8 owner preserved"))
if extras:
    parts.append("<h2>Final-build controls and separate diagnostics</h2>")
    for file, title in extras:
        parts.append(f"<section><h3>{html.escape(title)}</h3><img loading=lazy src='{file}' alt='{html.escape(title)}'></section>")
featured = {pair[key] for pair in pairs for key in ['before', 'after']} | {file for file, _ in extras}
retained = [path for path in sorted((OUT / 'screenshots').rglob('*.png'))
            if str(path.relative_to(OUT)) not in featured]
if retained:
    parts.append('<section><details><summary>Retained earlier-build controls — historical technical evidence</summary><p>These are earlier recovery-cohort controls, not original historical C8 screenshots or the final build. Filenames retain their recorded build/control identity.</p><ul>')
    for path in retained:
        file = str(path.relative_to(OUT))
        parts.append(f"<li><a href='{file}'>{html.escape(file)}</a></li>")
    parts.append('</ul></details></section>')
parts.append("<section><h2>Original quarry references</h2><p>Broad charcoal/grey-brown bodies, selective weathered faces and light-driven warmth guide the palette. They do not establish calibrated albedo or physical material percentages. Reference pixels are not runtime textures.</p><div class=pair>")
for path in sorted(reference_dir.iterdir()):
    parts.append(f"<img loading=lazy src='references/{path.name}' alt='Project quarry reference'>")
parts.append("</div></section><p>SwiftShader results are software diagnostics. Physical laptop/mobile acceptance is pending. No C9, cave, stage or public-default reconstruction was performed.</p></main></html>")
(OUT / "gallery.html").write_text("\n".join(parts))

pdfmetrics.registerFont(TTFont("Review", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("ReviewBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdf_path = OUT / "Gullyverse-Recovery-Phase2-C8-Review.pdf"
W, H = 432, 720
pdf = canvas.Canvas(str(pdf_path), pagesize=(W, H), pageCompression=1)
pdf.setTitle('BREEZE 2027 — Recovery Phase 2 — C8 material at 3×')
pdf.setAuthor('BREEZE 2027 / GULLYVERSE')
pdf.setSubject('Matched actual-browser material recovery review; unchanged C5.1 geometry')
page_count = 0


def wrap(text, width=390, font="Review", size=10):
    lines, line = [], ""
    for word in text.split():
        probe = (line + " " + word).strip()
        if pdfmetrics.stringWidth(probe, font, size) > width and line:
            lines.append(line); line = word
        else:
            line = probe
    return lines + ([line] if line else [])


def start(title, note):
    global page_count
    page_count += 1
    pdf.setFillColorRGB(0.06, 0.085, 0.07); pdf.rect(0, 0, W, H, fill=1, stroke=0)
    pdf.setFillColorRGB(0.94, 0.93, 0.88); pdf.setFont("ReviewBold", 14)
    y = H - 30
    for line in wrap(title, size=14, font="ReviewBold"):
        pdf.drawString(20, y, line); y -= 19
    pdf.setFont("Review", 9)
    for line in wrap(note, size=9):
        pdf.drawString(20, y - 6, line); y -= 13
    pdf.setFont("Review", 8); pdf.drawString(20, 12, f"BREEZE 2027 · Recovery Phase 2 · {page_count} · actual browser evidence")
    return y - 20


def place(path, x, y_top, width, height):
    # Only encoding for the PDF; full-resolution original PNGs remain intact.
    image = Image.open(path).convert("RGB")
    stream = BytesIO(); image.save(stream, format="JPEG", quality=90, subsampling=0); stream.seek(0)
    ratio = min(width / image.width, height / image.height)
    w, h = image.width * ratio, image.height * ratio
    pdf.drawImage(ImageReader(stream), x + (width - w) / 2, y_top - h, w, h)
    return y_top - h


y = start("C8 scanned material · approved 3× sampling", "Private recovery on preserved C5.1. Same geometry and approved dusk lighting. Not a new physical-rock benchmark.")
y = place(OUT / "screenshots/c8-3x/desktop-visitor-1.png", 20, y, W - 40, 270)
for paragraph in ["C8's documented Poly Haven Marble Rock 03 + Rock Face 03 family is reconstructed. Features are enlarged threefold by reducing repeats, not by adding repetitions.",
                  "Historical approved C8 screenshot matching is PENDING: the companion Evidence ZIP was not available. The C6.2 host and original mask source are missing. Reconstructed masks and unchanged C5.1 are explicitly documented.",
                  "The next pages are matched C5.1 / reconstructed C8 pairs. Neutral lights are separate browser-only diagnostics. Original PNGs and camera metadata are in the offline gallery."]:
    y -= 17
    for line in wrap(paragraph):
        pdf.setFont("Review", 10); pdf.drawString(20, y, line); y -= 15
pdf.showPage()
for pair in pairs:
    y = start(pair["title"], pair["note"] + " · " + pair["lighting"])
    mobile = pair["viewport"]["width"] < 700
    pdf.setFont("ReviewBold", 10)
    if mobile:
        pdf.drawString(20, y, "C5.1"); pdf.drawString(W / 2 + 8, y, "C8 3×")
        place(OUT / pair["before"], 20, y - 12, W / 2 - 28, y - 40)
        place(OUT / pair["after"], W / 2 + 8, y - 12, W / 2 - 28, y - 40)
    else:
        pdf.drawString(20, y, "Preserved C5.1")
        bottom = place(OUT / pair["before"], 20, y - 10, W - 40, 262)
        pdf.drawString(20, bottom - 21, "Reconstructed C8 3× · same C5.1 geometry")
        place(OUT / pair["after"], 20, bottom - 31, W - 40, 262)
    pdf.showPage()
for file, title in extras:
    y = start(title, "Final-build control or diagnostic. The full PNG and original metadata are retained in the gallery.")
    place(OUT / file, 20, y, W - 40, y - 30); pdf.showPage()
y = start("Reference and remaining limitations", "Project quarry reference; review use only, not a runtime texture.")
y = place(reference_dir / "quarry-open-sky-geometry.jpeg", 20, y, W - 40, 230)
for paragraph in ["The scan provides strong mineral grain and fractured-looking normal detail. It does not replace the smooth C5.1 geological forms, thin bright legacy fractures or the visible material boundary.",
                  "One original sector, 21.950 m in perimeter arc, is the smallest whole-mesh host used here. Its full-height shape differs from the missing historical 35.557 m C6.2 study. No geometry or UV1 bake was invented.",
                  "3 unique new images, approximately 32 MiB decoded RGBA8+mips; 5.41 MB material GLB. Detailed measured loading, frame times and regressions are in the technical report/JSON. SwiftShader is not physical GPU certification.",
                  "C9 reconstruction and cave work remain unstarted. Stop for visual review; historical matching and physical-device acceptance remain pending."]:
    y -= 15
    for line in wrap(paragraph):
        pdf.setFont("Review", 9); pdf.drawString(20, y, line); y -= 13
pdf.showPage(); pdf.save()
summary = {"matchedPairs": len(pairs), "originalBrowserPNGs": len(list((OUT / "screenshots").rglob("*.png"))),
           "pdfPages": page_count, "pdfBytes": pdf_path.stat().st_size,
           "pdfSHA256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
           "screenshotColourEditing": False, "PDFEncoding": "JPEG encoding for practical PDF size; original PNGs unchanged",
           "historicalC8ScreenshotComparison": "PENDING — evidence ZIP unavailable"}
(OUT / "raw/review-package.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
