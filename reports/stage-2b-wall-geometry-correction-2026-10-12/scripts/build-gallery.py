from pathlib import Path
import json,html
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');h=html.escape
before=json.loads((r/'raw/before-captures.json').read_text());after=json.loads((r/'raw/after-captures.json').read_text());extra=json.loads((r/'raw/extra-captures.json').read_text())
def metadata(c):
 d=c['data'];p=d['camera'];s=d['stats'];return h(f"Camera {p['x']:.3f}, {p['y']:.3f}, {p['z']:.3f}; yaw {p['yaw']:.4f}, pitch {p['pitch']:.4f}; FOV {p['fov']:.2f}°; DPR {s['dpr']}; quality {d['snapshot']['quality']}; LOD {d['wall']['activeLOD']}")
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Gullyverse — corrected wall comparisons</title><style>body{font:16px system-ui;background:#131817;color:#eceeea;margin:0 auto;padding:24px;max-width:1500px}h1{font-size:28px}a{color:#add5ee}section{margin:36px 0}figure{margin:0}img{width:100%;height:auto}figcaption,p{line-height:1.5}.pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}summary{cursor:pointer}video{width:100%;max-height:700px}pre{white-space:pre-wrap}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style><h1>One corrected limestone wall section</h1><p>Actual production-localhost Chromium screenshots. Left: preserved Stage 2B panel candidate. Right: corrected closed volume and localized fitted contact faces. Approved limestone material and global lighting are unchanged. Geometry is pending human approval. Surrounding procedural green blockout remains visibly different.</p><p><a href="../../docs/gullyverse-stage-2b-wall-geometry-correction.md">Geometry/integration report</a> · <a href="raw/before-captures.json">Before metadata</a> · <a href="raw/after-captures.json">After metadata</a> · <a href="raw/extra-captures.json">LOD/mobile metadata</a></p><p>Desktop comparisons use 1366×900 browser viewports; near-wall inspection cameras are diagnostic poses and do not change visitor movement bounds or saved camera settings. Map is captured through the public Map control. The profile, framing and timing of an open map can vary with its saved pose; metadata records the actual camera. PNG links preserve original resolution.</p>']
for b in before['captures']:
 name=Path(b['file']).name;a=next((c for c in after['captures']if Path(c['file']).name==name),None)
 if not a:continue
 parts.append(f'<section><h2>{h(name)}</h2><div class="pair">')
 for label,c in [('Previous candidate',b),('Corrected candidate',a)]:parts.append(f'<figure><a href="{h(c["file"])}"><img loading="lazy" src="{h(c["file"])}" alt="{h(label+" "+name)}"></a><figcaption><strong>{label}</strong><br>{metadata(c)}</figcaption></figure>')
 parts.append('</div></section>')
parts.append('<h2>LOD and portrait inspections</h2>')
for c in extra['captures']:
 parts.append(f'<section><figure><a href="{h(c["file"])}"><img loading="lazy" src="{h(c["file"])}" alt="{h(c["file"])}"></a><figcaption>{metadata(c)}<br>{h(c["file"])}</figcaption></figure></section>')
for filename,title in [('walkthrough.json','Actual W/A/S approach and retreat inside existing Hub bounds'),('inspection-walkthrough.json','Eye-height side inspection: diagnostic camera dolly outside player bounds')]:
 p=r/'raw'/filename
 if not p.exists():continue
 d=json.loads(p.read_text());v=Path(d['recording']);rel='recordings/'+v.name
 parts.append(f'<section><h2>{title}</h2><p>{h(d["method"])}</p><video controls preload="metadata" src="{h(rel)}"></video><p><a href="{h(rel)}">Original browser recording</a> · <a href="raw/{filename}">Camera/LOD trace</a></p></section>')
parts.append('<p>SwiftShader software renderer in a cloud VM. These images establish appearance, not physical GPU speed. Recordings are excluded from performance windows. LODs are automatically selected using screen-space size, quality and hysteresis; only one root is visible at a time. Close-up chips remain somewhat triangular; untouched neighboring blockout and material boundaries remain visible. No claim of photorealism or complete visual acceptance.</p></html>')
(r/'gallery.html').write_text('\n'.join(parts))
print('Gallery created; comparisons',len(before['captures']))
