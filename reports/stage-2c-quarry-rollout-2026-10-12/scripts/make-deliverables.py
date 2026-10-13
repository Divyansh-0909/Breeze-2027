"""Generate review artifacts from measured evidence, without changing the world."""
from pathlib import Path
import json, hashlib, html, struct, subprocess

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'reports/stage-2c-quarry-rollout-2026-10-12'
RAW = R / 'raw'
def read(name):
    return json.loads((RAW / (name + '.json')).read_text())

manifest = json.loads((ROOT / 'public/models/gullyverse/quarry-rollout/manifest.json').read_text())
asset_dir = ROOT / 'public/models/gullyverse/quarry-rollout'
inventory = {
    'blender': '4.3.2', 'units': 'metres', 'glTFUp': 'Y', 'blenderUp': 'Z',
    'parts': len(manifest['parts']),
    'trianglesPerWholeLOD': [sum(n['triangles'] for n in manifest['nodes'] if n['name'].endswith('LOD' + str(i))) for i in range(3)],
    'visualMaterials': 1, 'embeddedTextures': 3,
    'decodedRGBAWithMipmapsEstimateBytes': 12582912,
    'estimateCaution': 'Texture payload estimate, not measured driver VRAM.',
    'sourceQuarryVisualBounds': manifest['sourceQuarryBounds'],
    'runtimePolicy': 'Only combined GLB downloads. All LODs resident; one LOD per part drawn. Proxy remains hidden; existing walking collision is unchanged.',
    'files': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(asset_dir.glob('*.glb'))],
    'editableSource': {'path': 'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend', 'bytes': (ROOT / 'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend').stat().st_size},
}
(RAW / 'asset-inventory.json').write_text(json.dumps(inventory, indent=2))
hardware = {
    'OS': 'Debian GNU/Linux 13.6 (trixie), x86_64 KVM cloud VM',
    'CPU': '3 exposed vCPUs, AMD EPYC 9V74 80-Core Processor host',
    'browser': subprocess.check_output(['/usr/bin/chromium', '--version'], text=True).strip(),
    'renderer': read('after-performance')['windows'][0]['after']['renderer'],
    'physicalGPU': False, 'physicalMobile': False,
    'benchmarkViewport': [1366,900], 'benchmarkDPR': 0.5, 'benchmarkQuality': 3,
    'throttling': 'No artificial CPU/network throttle; software renderer.',
    'sampling': 'Three sequential fixed-camera 10-second frame windows; no concurrent Blender/capture/browser load. One before and one after run, not a statistical hardware certification.',
}
(RAW / 'hardware-profile.json').write_text(json.dumps(hardware, indent=2))

before, after = read('before-captures'), read('after-captures')
titles = ['Tunnel exit toward quarry','Quarry center','Stage-facing quarry','Left quarry wall','Right quarry wall','Public aerial map','Stage looking back toward tunnel']
rows = []
for index, (a,b) in enumerate(zip(before['captures'],after['captures'])):
    da,db=a['data'],b['data']
    assert da['camera']==db['camera']
    assert da['stats']['dpr']==db['stats']['dpr']
    assert da['snapshot']['quality']==db['snapshot']['quality']
    mobile=index>=7
    name=titles[index%7]+(' · mobile portrait' if mobile else ' · desktop')
    camera=db['camera'];viewport=db['viewport']
    caption=f"{viewport['width']} × {viewport['height']} · FOV {camera['fov']}° · effective DPR {db['stats']['dpr']} · quality {db['snapshot']['quality']} · camera [{camera['x']}, {camera['y']}, {camera['z']}]"
    metadata={'camera':camera,'pose':db['pose'],'viewport':viewport,'quality':db['snapshot']['quality'],'effectiveDPR':db['stats']['dpr'],'selectedPartLODs':db['wall']['lodSelections']}
    images=''.join(f'<figure><figcaption>{label}</figcaption><a href="{x["file"]}"><img loading="lazy" src="{x["file"]}" alt="{html.escape(name)} {label}"></a></figure>' for x,label in [(a,'Before: approved single-pilot baseline'),(b,'After: full quarry rollout')])
    rows.append(f'<section id="view-{index+1}" class="{"mobile" if mobile else "desktop"}"><h2>{html.escape(name)}</h2><p>{html.escape(caption)}</p><div class="pair">{images}</div><details><summary>Capture metadata and selected LODs</summary><pre>{html.escape(json.dumps(metadata,indent=2))}</pre></details></section>')

gallery='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse Stage 2C · Matched quarry comparison</title>
<style>body{margin:0;background:#101716;color:#edece5;font:16px/1.55 system-ui,sans-serif}main{max-width:1600px;margin:auto;padding:28px}h1{font-size:32px}h2{font-size:22px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{display:block;width:100%;height:auto}figcaption{padding:8px 0}section{margin:40px 0;border-top:1px solid #496059;padding-top:18px}a{color:#aedfd0}pre{overflow:auto;font-size:12px;background:#18221f;padding:12px}.mobile .pair{max-width:850px}nav{display:flex;gap:16px;flex-wrap:wrap}button{font:inherit;background:#263b34;color:inherit;border:1px solid #6d8e81;padding:8px 14px;cursor:pointer}@media(max-width:700px){.pair{grid-template-columns:1fr}main{padding:16px}}</style>
<main><h1>Gullyverse · Full quarry rollout</h1><p>Actual production-mode Chromium captures. All 14 camera poses, FOVs, effective DPRs and quality tiers match between before and after. Click an image for its original PNG. Mobile views are touch/viewport emulation, not physical-device GPU evidence.</p>
<p>The approved limestone maps and world configuration are retained. Large angular contours inherited from the quarry remain visible; visual production acceptance is for the user to decide.</p>
<nav><button onclick="filterViews('all')">All views</button><button onclick="filterViews('desktop')">Desktop</button><button onclick="filterViews('mobile')">Mobile portrait</button><a href="raw/before-captures.json">Before metadata</a><a href="raw/after-captures.json">After metadata</a><a href="../../docs/gullyverse-stage-2c-full-quarry-rollout.md">Implementation report</a></nav>'''+''.join(rows)+'''</main><script>function filterViews(type){document.querySelectorAll('section').forEach(s=>s.hidden=type!=='all'&&!s.classList.contains(type));}</script></html>'''
(R / 'gallery.html').write_text(gallery)
print('Created gallery with',len(rows),'matched pairs and asset/hardware inventories.')
