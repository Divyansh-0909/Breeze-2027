import bpy,json,math,re
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];P=O.parent/'navigation-board-rev15l1-logo-spacing-2026-11-11/delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;bpy.context.view_layer.update();refs=[o for o in s.objects if o.type=='MESH' and o.data.name.startswith('REV13A shared')];bank={}
for o in refs:
 key=(o.get('archetype'),o.get('poseFamily'))
 if key not in bank:bank[key]=o
rows=[]
for (a,p),o in bank.items():
 if p not in ['relaxed','folded-arms','one-hand-pocket','hands-together','weight-shift','phone-record']:continue
 mesh=bpy.data.meshes[o['LOD0']];slots=[m.name for m in mesh.materials];ids=[i for i,m in enumerate(slots) if 'eye sclera' in m];vs=set(v for poly in mesh.polygons if poly.material_index in ids for v in poly.vertices);eye=sum((mesh.vertices[v].co for v in vs),Vector())/len(vs) if vs else Vector();rows.append({'object':o.name,'archetype':a,'pose':p,'LOD0':mesh.name,'vertices':len(mesh.vertices),'scale':list(o.scale),'rotation':list(o.rotation_euler),'localMinZ':min(v.co.z for v in mesh.vertices),'localMaxZ':max(v.co.z for v in mesh.vertices),'eyeCentreLocal':list(eye),'standingHeight':o.get('standingHeightM')})
cameras=[{'name':o.name,'loc':list(o.location),'rot':list(o.rotation_euler),'lens':o.data.lens} for o in s.objects if o.type=='CAMERA'];(O/'evidence/reference-bank.json').write_text(json.dumps({'bank':rows,'cameras':cameras},indent=2));print('reference bank',len(rows),'cameras',len(cameras),flush=True)
