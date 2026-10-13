from pathlib import Path
import json, html

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/stage-2c4-rock-look-restore-2026-10-13"
before = json.loads((OUT/"raw/before-captures.json").read_text())["captures"]
after = json.loads((OUT/"raw/after-captures.json").read_text())["captures"]
titles = {"01-hub-center": "Hub center", "02-stage-facing": "Stage-facing quarry",
          "03-left-wall": "Left wall", "04-right-wall": "Right wall", "05-close-wall": "Close-up rock surface",
          "06-scaffold": "Scaffold and surrounding walls", "07-aerial-map": "Full aerial map",
          "08-tunnel-exit": "Tunnel exit", "09-stage-looking-back": "Stage looking back"}
cards = []
for a, b in zip(before, after):
    stem = Path(b["file"]).stem
    title = titles[stem.replace("desktop-", "").replace("mobile-", "")]
    if stem.startswith("mobile-"):
        title += " · portrait browser emulation"
    details = b["data"]
    camera = details["camera"]
    position = camera.get("position", {k: camera.get(k) for k in ["x", "y", "z"]})
    meta = json.dumps({"camera": camera, "viewport": details["viewport"], "quality": details["snapshot"]["quality"],
                       "effectiveDPR": details["stats"]["dpr"], "material": b["material"]}, indent=2)
    figures = []
    for capture, label in [(a, "Before · Grey limestone"), (b, "After · Original Stage 2A rock")]:
        file = html.escape(capture["file"])
        figures.append(f'<figure><figcaption>{label}</figcaption><a href="{file}"><img src="{file}" loading="lazy" alt="{html.escape(title)} — {label}"></a><a class="download" href="{file}" download>Original PNG</a></figure>')
    cards.append(f'<section><h2>{html.escape(title)}</h2><div class="pair">{"".join(figures)}</div><details><summary>Camera / rendering metadata</summary><pre>{html.escape(meta)}</pre></details></section>')
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gullyverse Stage 2C.4 — rock-look restoration</title>
<style>body{margin:0;background:#121714;color:#e8eae5;font:16px/1.5 system-ui}main{max-width:1500px;margin:auto;padding:20px}h1{font-size:clamp(24px,4vw,38px);line-height:1.2}h2{font-size:22px}a{color:#c3d7e3}section{border-top:1px solid #475247;padding:24px 0}.pair{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0}figcaption{padding:8px 0;font-weight:600}img{display:block;width:100%;height:auto;border-radius:4px}pre{white-space:pre-wrap;font-size:12px;overflow-wrap:anywhere}details{margin-top:15px}summary{cursor:pointer}.download{display:inline-block;padding:10px 0}.reference{max-width:1000px}.note{padding:16px;background:#263229;border-left:4px solid #a7b7a0}@media(max-width:760px){.pair{grid-template-columns:1fr}main{padding:14px}h2{font-size:20px}}</style>
<main><h1>Connected quarry · original rock-pilot look</h1>
<p>The connected geometry, lighting and visitor layout are unchanged. The original darker Stage 2A material replaces the Grey limestone family in the connected review.</p>
<p class="note">12 matched pairs: identical camera poses, FOV, viewport, effective DPR, quality and selected LOD geometry. Tap any image for its full-resolution PNG. Portrait views are browser emulation; physical iPhone GPU performance was not measured.</p>
<p><a href="../../docs/gullyverse-stage-2c4-rock-look-restore.md">Review report</a> · <a href="raw/capture-pair-validation.json">Matched-pose validation</a> · <a href="raw/after-captures.json">All screenshot metadata</a></p>
<section class="reference"><h2>Original Stage 2A source reference</h2><p>Fresh actual-browser capture of the preserved original asset, LOD0 / medium / FOV 58°. Its original maps and PBR settings are reused unchanged.</p><a href="reference/original-stage2a-rock-pilot.png"><img src="reference/original-stage2a-rock-pilot.png" alt="Original Stage 2A darker rock pilot"></a></section>
'''+"\n".join(cards)+'''<p>Photorealistic refinement is deferred. No commit, push or deployment.</p></main></html>'''
(OUT/"gallery.html").write_text(page)
print("Gallery created:", len(cards), "matched views /", 2*len(cards)+1, "actual browser PNGs")
