from pathlib import Path
import json,html
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13'
captures=[]
for name in ['before-captures','after-captures','before-detail-captures','after-detail-captures','stage-material-captures']:
    path=OUT/'raw'/(name+'.json')
    if path.exists():captures.extend(json.loads(path.read_text()).get('captures',[]))
video=OUT/'raw/video-with-wall.json'
if video.exists():
    cycle=json.loads(video.read_text()).get('cycles',[{}])[0]
    for file,key in [('after/desktop-18-stage-playing.png','playing'),('after/desktop-19-stage-restored.png','settled')]:
        if key in cycle:captures.append({'file':file,'note':'Actual public video cycle1; telemetry sampled at the beginning of screenshot acquisition. Live video/time can progress while capturing. Physical assets/lighting unchanged.','data':cycle[key]})
walk=OUT/'raw/walkthrough.json'
if walk.exists():
    for e in json.loads(walk.read_text()).get('events',[]):
        if e['event']in['public map ascent','public map descent']:
            captures.append({'file':'recordings/'+('map-ascent.png'if e['event'].endswith('ascent')else'map-descent.png'),
              'note':'Public map animation; telemetry sampled just after screenshot acquisition, camera continues moving.','data':e['data']})
(OUT/'screenshot-metadata.json').write_text(json.dumps({'method':'Actual browser captures. Camera pose/FOV, viewport, renderer DPR and graphics quality are in each data record. Close-up and normal/wireframe/forcedLOD captures are explicitly diagnostic. Portrait is emulation, not physical mobile.',
    'captures':captures},indent=2))
style='''body{background:#17201e;color:#ecece5;font:16px system-ui;margin:0;padding:20px;max-width:1500px}a{color:#d9d2a2}img{display:block;width:100%;height:auto;background:#333}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0 0 20px}figcaption{padding:8px;background:#28342f}h2{margin-top:36px}.portrait img{max-width:390px;margin:auto}pre{white-space:pre-wrap;font-size:12px}@media(max-width:760px){.pair{grid-template-columns:1fr}body{padding:10px}}'''
parts=['<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Gullyverse dark rock foundation</title><style>'+style+'</style></head><body><h1>Stage2C.5 · Dark rock foundation</h1><p>Actual website screenshots. Connected baseline on the left; foundation review on the right. Mobile layouts stack vertically. All global lighting, stage assets and navigation are retained.</p><p><a href="screenshot-metadata.json">Capture metadata</a> · <a href="../../docs/gullyverse-stage-2c5-photorealism-foundation.md">Report</a></p>']
def image(file,label,cls=''):
    return '<figure class="'+cls+'"><a href="'+html.escape(file)+'"><img loading="lazy" src="'+html.escape(file)+'"></a><figcaption>'+html.escape(label)+'</figcaption></figure>'
for p in sorted((OUT/'after').glob('*.png')):
    if p.name.startswith('diagnostic')or p.name.startswith('inspection'):continue
    before=OUT/'before'/p.name
    parts.append('<h2>'+html.escape(p.stem.replace('-',' '))+'</h2><div class="pair">')
    if before.exists():parts.append(image('before/'+p.name,'Approved connected Stage2C4 baseline','portrait'if p.name.startswith('mobile')else''))
    parts.append(image('after/'+p.name,'Foundation review · unchanged approved lights','portrait'if p.name.startswith('mobile')else''));parts.append('</div>')
parts.append('<h2>Material, geometric-normal and wireframe diagnostics</h2>')
for p in sorted((OUT/'after').glob('diagnostic*.png')):
    parts.append('<div class="pair">'+image('before/'+p.name,'Baseline · '+p.stem)+image('after/'+p.name,'Foundation · '+p.stem)+'</div>')
parts.append('<h2>LOD0 / LOD1 / LOD2 · inspection comparisons</h2>')
for p in sorted((OUT/'after').glob('inspection*.png')):parts.append(image('after/'+p.name,p.stem+' · one explicitly selected level'))
parts.append('<h2>Actual browser recordings</h2>')
for p in sorted((OUT/'recordings').glob('map-*.png')):parts.append(image('recordings/'+p.name,p.stem+' · public camera transition'))
for p in sorted((OUT/'recordings').glob('*.mp4')):parts.append('<p>'+html.escape(p.stem)+'</p><video controls playsinline preload="metadata" style="width:100%" src="recordings/'+p.name+'"></video>')
parts.append('<h2>References</h2>')
for p in sorted((OUT/'reference').glob('*')):
    if p.suffix.lower()in['.png','.jpg','.jpeg']:parts.append(image('reference/'+p.name,p.stem+' · reference/source, not acceptance screenshot'))
parts.append('</body></html>');(OUT/'gallery.html').write_text('\n'.join(parts))
print('Gallery',len(captures),'metadata records',len(list((OUT/'after').glob('*.png'))),'after PNGs')
