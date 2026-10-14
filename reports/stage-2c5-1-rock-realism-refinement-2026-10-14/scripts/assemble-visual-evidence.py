"""Metadata/pair checks and a self-contained, phone-friendly PNG gallery."""
from pathlib import Path
import json,html
from PIL import Image
ROOT=Path.cwd();OUT=ROOT/'reports/stage-2c5-1-rock-realism-refinement-2026-10-14';RAW=OUT/'raw'
captures=[]
for name in ['before-captures','after-captures','before-detail-captures','after-detail-captures',
             'before-supplement-captures','after-supplement-captures',
             'before-lighting-diagnostics','after-lighting-diagnostics','stage-lighting-captures']:
    p=RAW/(name+'.json')
    if p.exists():captures.extend(json.loads(p.read_text()).get('captures',[]))
walk=RAW/'walkthrough.json'
if walk.exists():
    for e in json.loads(walk.read_text()).get('events',[]):
        name={'public map ascent':'map-ascent','public map descent':'map-descent'}.get(e['event'])
        if name:captures.append({'file':'recordings/'+name+'.png','note':'Actual map animation frame; camera metadata sampled immediately after screenshot, approximate during motion.','data':e['data']})
for item in captures:
    p=OUT/item['file'];assert p.exists(),p
    with Image.open(p)as image:item['pngPixels']=list(image.size)
    item['label']='diagnostic'if'diagnostic'in item['file']else'candidate'if item['file'].startswith('after/')else'baseline'
    data=item['data'];item['qualityTier']=data['snapshot']['quality'];item['effectiveDPR']=data['stats']['dpr']
    item['lightingPreset']=data['snapshot']['scene'];item['originalResolutionPreserved']=True
(OUT/'screenshot-metadata.json').write_text(json.dumps(captures,indent=2))
lookup={q['file']:q for q in captures};pairs=[]
for name,q in lookup.items():
    if not name.startswith('before/')or'diagnostic'in name:continue
    after=lookup.get(name.replace('before/','after/',1))
    if not after:continue
    a,b=q['data'],after['data'];equal={}
    for key in['x','y','z','yaw','pitch','fov']:equal[key]=abs(a['camera'][key]-b['camera'][key])<1e-6
    equal['viewport']=a['viewport']==b['viewport'];equal['dpr']=q['effectiveDPR']==after['effectiveDPR']
    equal['quality']=q['qualityTier']==after['qualityTier'];equal['lightingPreset']=q['lightingPreset']==after['lightingPreset']
    pairs.append({'before':name,'after':after['file'],'matched':all(equal.values()),'checks':equal})
(RAW/'matched-capture-validation.json').write_text(json.dumps({'status':'PASS'if all(p['matched']for p in pairs)else'FAIL','pairs':pairs},indent=2))

names={'01-hub-center':'Hub centre','02-stage-facing':'Stage-facing composition','03-left-wall':'Left wall',
 '04-right-wall':'Right wall','05-close-wall':'Closer wall','06-scaffold':'Scaffold and cliffs','07-aerial-map':'Actual aerial map',
 '08-tunnel-exit':'Tunnel exit','09-stage-looking-back':'Stage looking back','10-broad-face':'Broad face',
 '11-corner':'Curved corner','12-joined-regions':'Connected regions','13-fracture-close':'Matched original fracture view',
 '14-upper-rim':'Low-angle rim','15-wall-foot':'Wall-foot contact','16-along-wall':'Eye-height along-wall inspection',
 '17-terrain-map-height':'Upper terrain','20-regions-under-stage-lighting':'Regions under original Aftermovie lighting',
 '21-broken-fracture':'Broken fracture edge','22-bed-fault-intersection':'Bedding/fault interaction','23-rim-contact':'Rim/terrain contact','24-ground-contact':'Ground contact'}
cards=[]
for p in pairs:
    before,after=p['before'],p['after'];suffix=Path(before).stem.split('-',1)[-1]
    title=('Portrait — 'if'mobile'in before else'')+names.get(suffix,suffix)
    cards.append(f'<section><h2>{html.escape(title)}</h2><div class="pair"><figure><figcaption>Stage2C.5 baseline</figcaption><a href="{before}"><img loading="lazy" src="{before}" alt="Before {html.escape(title)}"></a></figure><figure><figcaption>Stage2C.5.1 candidate</figcaption><a href="{after}"><img loading="lazy" src="{after}" alt="After {html.escape(title)}"></a></figure></div><small>Matched camera/FOV/viewport/DPR/quality: {p["matched"]}</small></section>')
extra=[]
for q in captures:
    if q['label']=='diagnostic'or'inspection-lod'in q['file']:
        f=q['file'];extra.append(f'<figure><figcaption>{html.escape(f)}</figcaption><a href="{f}"><img loading="lazy" src="{f}" alt="{html.escape(f)}"></a></figure>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gullyverse Stage2C.5.1 visual review</title><style>body{margin:0;background:#111815;color:#eee;font:16px/1.5 system-ui;padding:16px;max-width:1600px;margin:auto}a{color:#c7ddbf}h1{font-size:26px}h2{font-size:20px}section{border-top:1px solid #425147;padding:18px 0}img{display:block;max-width:100%;height:auto}figure{margin:0}figcaption{padding:7px 0;color:#ccd6cf}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.extra{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}small{color:#aac1b2}video{width:100%;max-width:1100px}@media(max-width:700px){.pair,.extra{grid-template-columns:1fr}}</style><h1>Stage2C.5.1 — fracture and continuity review</h1><p>Actual, unbrightened browser PNGs under the approved lighting. Click an image for its original file. Desktop1366×900; portrait390×844. Close/high poses are inspection cameras; visitor cameras and movement bounds are unchanged. Physical mobile/GPU performance remains unverified.</p><p><a href="../../docs/gullyverse-stage-2c5-1-rock-realism-refinement.md">Report</a> · <a href="screenshot-metadata.json">Camera and rendering metadata</a></p>'''+''.join(cards)+'''<h2>Recordings</h2><p>Actual silent browser captures; software-renderer pauses are retained.</p><video controls playsinline preload="none" src="recordings/visitor-walk-and-aerial.mp4"></video><p>Public mouse/WASD/map journey.</p><video controls playsinline preload="none" src="recordings/near-wall-inspection.mp4"></video><p>Eye-height inspection traverse; automatic LOD. Existing travel gates prevent this near-wall path through ordinary walking.</p><h2>Diagnostics and forced single LODs</h2><p>Neutral lights/normal isolation/wireframe are browser-only diagnostics, not proposed default lighting.</p><div class="extra">'''+''.join(extra)+'</div></html>'
(OUT/'gallery.html').write_text(page)
print('captured',len(captures),'paired',len(pairs),'mismatched',[p for p in pairs if not p['matched']])
