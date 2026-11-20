import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];p=Path('/dev/shm/Gullyverse-Rev15W-Streetlights-and-Overhead-Cables.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='cabf7566933a26bc9c1e7954343f3c007d8389919f4c49fcbacb75c5f5d76a3a';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for o in s.objects:
 if any(k in o.name.lower() for k in ['accom','contact','events','house','destination','coming','soon']):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'type':o.type,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'text':o.data.body if o.type=='FONT' else None,'properties':dict(o.items())})
images=[]
for im in bpy.data.images:
 if 'REV15K' in im.name and 'Organising' in im.name and im.packed_file:
  output=R/'assets/team-style-reference.png';output.write_bytes(im.packed_file.data);images.append({'name':im.name,'path':str(output)})
(R/'evidence/scene-inspection.json').write_text(json.dumps({'scene':s.name,'objects':rows,'images':images},indent=2,default=str)+'\n');print(json.dumps({'candidates':len(rows),'images':images}));print('\n'.join(o['name']+' '+str(o['bounds']) for o in rows))
