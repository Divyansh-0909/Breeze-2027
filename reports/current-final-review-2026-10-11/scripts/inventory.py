import json,struct,hashlib,subprocess,platform,os
from pathlib import Path
from PIL import Image
root=Path('reports/current-final-review-2026-10-11'); assets=[]
for p in sorted(list(Path('public').rglob('*'))+list(Path('Assets').rglob('*'))):
 if not p.is_file() or p.suffix.lower() not in ['.glb','.png','.jpeg','.jpg','.webp','.ktx2','.mp4','.blend']:continue
 item={'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix=='.glb':
  b=p.read_bytes();n,t=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n]);acc=g.get('accessors',[])
  meshes=g.get('meshes',[]);pr=[q for m in meshes for q in m.get('primitives',[])];item.update(meshes=len(meshes),primitives=len(pr),vertices=sum(acc[q['attributes']['POSITION']]['count'] for q in pr if 'POSITION' in q['attributes']),triangles=sum(acc[q['indices']]['count']//3 if 'indices' in q else acc[q['attributes']['POSITION']]['count']//3 for q in pr if q.get('mode',4)==4),materials=g.get('materials',[]),images=g.get('images',[]),extensionsUsed=g.get('extensionsUsed',[]),positionBounds=[{'min':a.get('min'),'max':a.get('max')} for a in acc if a.get('type')=='VEC3' and 'min' in a])
  for im in item['images']:
   if 'bufferView' in im:
    bv=g['bufferViews'][im['bufferView']];off=20+n+8+bv.get('byteOffset',0)
    try:
     import io
     image=Image.open(io.BytesIO(b[off:off+bv['byteLength']]));im.update(width=image.width,height=image.height,format=image.format)
    except Exception as e:im['inspectionError']=str(e)
 else:
  try:
   im=Image.open(p);item.update(width=im.width,height=im.height,format=im.format)
  except:pass
 assets.append(item)
root.joinpath('raw/asset-inventory.json').write_text(json.dumps({'assets':assets,'blenderSources':[str(p) for p in Path('.').rglob('*.blend') if 'node_modules' not in p.parts],'note':'GLB triangle sums are authoring payload totals, not actual drawn instancing totals. Bound arrays are local accessor bounds, not assembled world extents.'},indent=2))
info={'os':platform.platform(),'cpu':subprocess.check_output(['lscpu'],text=True),'browser':subprocess.check_output(['/usr/bin/chromium','--version'],text=True),'node':subprocess.check_output(['node','--version'],text=True),'blender':subprocess.check_output(['/usr/bin/blender','--version'],text=True)}
root.joinpath('raw/hardware.json').write_text(json.dumps(info,indent=2))
