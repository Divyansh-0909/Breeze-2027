import bpy,json,re,collections
from pathlib import Path
O=Path(__file__).resolve().parents[1];P=O.parent/'events-wall-rev15n-warm-brick-2026-11-11/delivery/Gullyverse-Rev15N-Events-House-Wall.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if ob.type!='MESH' or not (ob.name.startswith('REV15 / REV12 /') or 'connector house /' in ob.name) or not any(m and 'blackened zinc' in m.name for m in ob.data.materials):continue
 me=ob.data;parents=list(range(len(me.vertices)))
 def find(i):
  while i!=parents[i]:parents[i]=parents[parents[i]];i=parents[i]
  return i
 for e in me.edges:
  a,b=map(find,e.vertices);parents[b]=a
 groups={}
 for v in me.vertices:groups.setdefault(find(v.index),[]).append(v.index)
 components=[]
 for ids in groups.values():
  points=[ob.matrix_world@me.vertices[i].co for i in ids];bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)];components.append({'vertices':ids,'bounds':bounds})
 rows.append({'object':ob.name,'mesh':me.name,'components':components})
(O/'evidence/rail-components.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{'object':r['object'],'components':len(r['components']),'heightBands':dict(collections.Counter((round(c['bounds'][2][0],2),round(c['bounds'][2][1],2)) for c in r['components']))} for r in rows],default=str),flush=True)
