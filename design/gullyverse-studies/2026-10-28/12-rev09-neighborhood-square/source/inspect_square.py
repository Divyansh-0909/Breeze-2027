import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];s=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE ARCH');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 sem=o.get('pilotOriginalObject',o.name)
 if any(x in sem.lower()for x in['neighbor mid-rise','destination','team','events','notice','media','dj','roof water','headhouse'])or(o.name.startswith('REV08 /')and'room'in o.name):
  p=[o.matrix_world@v.co for v in o.data.vertices]if o.type=='MESH'else[];rows.append({'name':o.name,'semantic':sem,'bounds':[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)]if p else None})
(O/'evidence/existing-square.json').write_text(json.dumps(rows,indent=2));print(json.dumps([r for r in rows if 'wall'in r['name'].lower()or'board'in r['name'].lower()or'DJ'in r['name']],indent=2))
