import os
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/'public/models/gullyverse/locked-rev15z-v1')));out.mkdir(parents=True,exist_ok=True);plan=json.loads(Path(os.environ.get('GULLYVERSE_PLAN',str(Path(__file__).with_name('export-plan.json')))).read_text());guard={'lockedSource':plan['source']['path'],'sourceSHA256':plan['source']['sha256']};source=Path(guard['lockedSource']);assert hashlib.sha256(source.read_bytes()).hexdigest()==guard['sourceSHA256'];bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert s.name==plan['source']['scene']
def val(v):
 if isinstance(v,(str,float,int,bool,type(None))):return v
 try:return list(v)
 except:return str(v)
rows=[];materials={}
for o in s.objects:
 row={'name':o.name,'type':o.type,'tags':{k:val(v)for k,v in o.items()},'hidden':o.hide_render,'matrix':[list(x)for x in o.matrix_world]}
 if o.type in ['MESH','FONT','CURVE']:
  bb=[o.matrix_world@Vector(p)for p in o.bound_box];row['bounds']=[[min(p[a]for p in bb),max(p[a]for p in bb)]for a in range(3)]
 if o.type=='MESH':
  me=o.data;me.calc_loop_triangles();row.update(mesh=me.name,vertices=len(me.vertices),triangles=len(me.loop_triangles),faces=len(me.polygons),uvLayers=[u.name for u in me.uv_layers],materials=[m.name if m else None for m in me.materials])
  for m in me.materials:
   if not m or m.name in materials:continue
   mats={'nodes':[n.type for n in m.node_tree.nodes]if m.use_nodes else[],'images':[{'name':n.image.name,'size':list(n.image.size),'packedSHA256':hashlib.sha256(n.image.packed_file.data).hexdigest()if n.image.packed_file else None}for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image]if m.use_nodes else[]};materials[m.name]=mats
 if o.type=='LIGHT':row['light']={'type':o.data.type,'energy':o.data.energy,'colour':list(o.data.color)}
 rows.append(row)
world={'name':s.world.name,'nodes':[n.type for n in s.world.node_tree.nodes]if s.world.use_nodes else[],'exposure':s.view_settings.exposure,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look}
result={'status':'PASS','source':str(source),'sourceSHA256':guard['sourceSHA256'],'scene':s.name,'scenes':len(bpy.data.scenes),'packedImages':sum(bool(i.packed_file)for i in bpy.data.images),'world':world,'objects':rows,'materials':materials};(out/'source-inventory.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','objects':len(rows),'triangles':sum(r.get('triangles',0)for r in rows),'materials':len(materials),'lights':sum(r['type']=='LIGHT'for r in rows),'world':world}))
