import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1]
names=[]
for o in bpy.data.objects:
    if any(x in o.name.lower()for x in ['board','counter','shop recess','shop warm interior','shelf','carton','lamp','light','camera','continuous']):
        names.append({'name':o.name,'type':o.type,'basis':[list(r)for r in o.matrix_basis],'dimensions':list(o.dimensions),'materials':[m.name for m in o.data.materials if m]if hasattr(o.data,'materials')else[]})
(O/'evidence/baseline-key-objects.json').write_text(json.dumps(names,indent=2)+'\n')
print('BASELINE_PROBE',[(o['name'],[r[3]for r in o['basis'][:3]],o['dimensions'])for o in names if any(k in o['name']for k in ['board','13-CONTINUOUS','Shop warm interior'])])
