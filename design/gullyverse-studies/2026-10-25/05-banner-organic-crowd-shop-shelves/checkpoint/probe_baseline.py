import bpy,json
from pathlib import Path
p=Path('/workspace/gullyverse-world-concept/2026-10-25/05-banner-organic-crowd-shop-shelves')
rows=[]
for o in bpy.data.objects:
 if o.name.startswith(('Building /','Shop warm interior','Shop recess','Counter','Festival takeover banner','Shop stock shelf','Dry goods carton')):
  rows.append({'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'basis':[[*r]for r in o.matrix_basis],'collections':[c.name for c in o.users_collection],'materials':[m.name for m in o.data.materials]})
(p/'evidence/baseline-object-inventory.json').write_text(json.dumps(rows,indent=2)+'\n');print('INVENTORY',len(rows))
