import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
def row(o):
 p=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else []
 return {'name':o.name,'semantic':o.get('pilotOriginalObject',o.name),'bounds':[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)]if p else None,'location':list(o.location),'dims':list(o.dimensions)}
names=['Rooftop','parapet','Neighbor','TEAM','EVENTS','DJ','Counter','Aftermovie']
r=[row(o)for o in s.objects if any(n.lower()in o.name.lower() for n in names)]
(O/'evidence/existing-destination-geometry.json').write_text(json.dumps(r,indent=2));print(json.dumps([x for x in r if 'Neighbor'in x['name']or'DJ'in x['name']or'TEAM'in x['name']or'EVENTS'in x['name']],indent=2))
