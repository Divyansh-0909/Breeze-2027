from pathlib import Path
import html,json
r=Path('reports/stage-2c1-geological-refinement-2026-10-13');pairs=[]
for p in sorted((r/'before').glob('*.png')):
 q=r/'after'/p.name
 if q.exists():pairs.append((p.relative_to(r).as_posix(),q.relative_to(r).as_posix()))
body=[]
for a,b in pairs:
 label=Path(a).stem.replace('-', ' ');body.append(f'<article><h2>{html.escape(label)}</h2><div class="pair"><figure><figcaption>Stage 2C baseline</figcaption><a href="{a}"><img loading="lazy" src="{a}"></a></figure><figure><figcaption>Opt-in refined pair</figcaption><a href="{b}"><img loading="lazy" src="{b}"></a></figure></div></article>')
for folder in ['diagnostics','lod']:
 files=sorted((r/folder).glob('*.png'));body.append('<h2>'+folder+'</h2><div class="pair">'+''.join(f'<figure><figcaption>{p.stem}</figcaption><a href="{p.relative_to(r).as_posix()}"><img loading="lazy" src="{p.relative_to(r).as_posix()}"></a></figure>'for p in files)+'</div>')
record=r/'recordings/geology-inspection-walkthrough.webm'
if record.exists():body.append('<h2>Actual browser inspection walkthrough</h2><p>Inspection camera path, then public aerial map; real runtime LOD. It does not alter or prove expanded public walking bounds.</p><video controls preload="metadata"><source src="recordings/geology-inspection-walkthrough.mp4" type="video/mp4"><source src="recordings/geology-inspection-walkthrough.webm" type="video/webm"></video>')
style='body{background:#101815;color:#ecefe9;font:16px system-ui;margin:24px}a{color:#b5d6cc}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;height:auto;display:block}figcaption{padding:8px 0}article{margin:32px 0}video{max-width:100%;width:1100px}@media(max-width:700px){.pair{grid-template-columns:1fr}}'
(r/'gallery.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Gullyverse 2C.1 geological refinement</title><style>'+style+'</style></head><body><h1>Two-section geological refinement</h1><p>Actual production-mode Chromium captures. Current limestone images/material and environment lighting are unchanged. Only sections 22/23 are opt-in candidates; surrounding walls stay Stage 2C. Mobile views are browser emulation. Click any PNG for its original resolution.</p><p><a href="../../docs/gullyverse-stage-2c1-geological-refinement.md">Report</a> · <a href="raw/capture-pair-validation.json">Matched-camera metadata</a></p>'+''.join(body)+'</body></html>')
print(len(pairs),'matched pairs')
