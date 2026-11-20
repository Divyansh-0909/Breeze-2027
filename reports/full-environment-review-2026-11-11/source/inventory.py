import bpy, json, hashlib, re
from pathlib import Path
from mathutils import Vector

O=Path(__file__).resolve().parents[1]
P=O.parent/'team-wall-rev15j1-full-heading-2026-11-10/delivery/Gullyverse-Rev15J1-Full-Heading.blend'
bpy.ops.wm.open_mainfile(filepath=str(P))
s=next(s for s in bpy.data.scenes if s.get('variant')=='REV15J1')
bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
def value(v):
 if isinstance(v,(str,int,float,bool)) or v is None:return v
 try:return list(v)
 except:return str(v)
objects=[]
for o in s.objects:
 if o.type!='MESH':continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box]
 objects.append({'name':o.name,'min':[min(v[i] for v in bb) for i in range(3)],'max':[max(v[i] for v in bb) for i in range(3)],'hiddenRender':o.hide_render,'materials':[m.name for m in o.data.materials if m],'props':{k:value(v) for k,v in o.items()}})
cameras=[{'name':o.name,'position':list(o.location),'rotation':list(o.rotation_euler),'type':o.data.type,'lens':o.data.lens,'orthoScale':o.data.ortho_scale} for o in s.objects if o.type=='CAMERA']
lights=[{'name':o.name,'position':list(o.location),'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)}for o in s.objects if o.type=='LIGHT']
result={'master':str(P),'masterSHA256':hashlib.sha256(P.read_bytes()).hexdigest(),'scene':s.name,'objectCount':len(s.objects),'scenes':len(bpy.data.scenes),'sceneProps':{k:value(v) for k,v in s.items()},'objects':objects,'cameras':cameras,'lights':lights}
(O/'evidence/inventory.json').write_text(json.dumps(result,indent=2,default=str))
print(json.dumps({'scene':s.name,'objects':len(s.objects),'matched':len(objects),'cameras':len(cameras),'lights':len(lights),'shopObjectNames':[o['name'] for o in objects if re.search(r'shop|shutter',o['name'],re.I)][:140]},indent=2),flush=True)
