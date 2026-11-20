import bpy,json,hashlib,runpy
from array import array
from pathlib import Path
R=Path(__file__).resolve().parents[1];material_signature=runpy.run_path(str(R.parent/'cypher-houses-rev15v-walls-windows-2026-11-14/source/preservation.py'))['material_signature']
def snapshot(scene,plan,prefix):
 targets={r['object'].removeprefix('REV15V / '):set(r['faces']) for r in plan['objects']};rows=[];mc={};gc={}
 for o in sorted(scene.objects,key=lambda o:o.name):
  row={'name':o.name.removeprefix(prefix),'type':o.type,'matrix':[list(x) for x in o.matrix_world],'hidden':o.hide_render,'viewportHidden':o.hide_viewport,'parent':o.parent.name.removeprefix(prefix) if o.parent else None}
  if o.type=='MESH':
   me=o.data
   if me.as_pointer() not in gc:
    h=hashlib.sha256()
    for coll,prop,typ,n in [(me.vertices,'co','f',len(me.vertices)*3),(me.loops,'vertex_index','i',len(me.loops)),(me.polygons,'loop_total','i',len(me.polygons)),(me.polygons,'use_smooth','b',len(me.polygons))]:
     a=array(typ,[0])*n;coll.foreach_get(prop,a);h.update(a.tobytes())
    for uv in me.uv_layers:
     a=array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(uv.name.encode());h.update(a.tobytes())
    for ca in me.color_attributes:
     a=array('f',[0])*(len(ca.data)*4);ca.data.foreach_get('color',a);h.update(ca.name.encode());h.update(a.tobytes())
    gc[me.as_pointer()]=h.hexdigest()
   row['shapeUVColour']=gc[me.as_pointer()];mats={i:material_signature(slot.material,mc) for i,slot in enumerate(o.material_slots)};skip=targets.get(row['name'],set());row['protectedMaterials']=hashlib.sha256(json.dumps([(f.index,mats[f.material_index]) for f in me.polygons if f.index not in skip]).encode()).hexdigest()
  elif o.type=='FONT':row['font']=[o.data.body,o.data.size,o.data.font.name]
  elif o.type=='LIGHT':row['light']=[o.data.type,o.data.energy,list(o.data.color)]
  elif o.type=='CURVE':row['curve']=[(s.type,[list(p.co) for p in s.points]) for s in o.data.splines]
  rows.append(row)
 return {'objects':len(rows),'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}
