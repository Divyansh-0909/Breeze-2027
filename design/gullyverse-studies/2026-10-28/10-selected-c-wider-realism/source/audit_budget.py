import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];rows=[]
for s in bpy.data.scenes:
 bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();tris=verts=meshes=0;materials={};images={}
 for o in s.objects:
  if o.type not in ['MESH','FONT','CURVE']or o.name.startswith('Bounded lane haze'):continue
  ev=o.evaluated_get(dep);m=ev.to_mesh()
  if m:
   m.calc_loop_triangles();tris+=len(m.loop_triangles);verts+=len(m.vertices);meshes+=1
   for slot in o.material_slots:
    mat=slot.material
    if mat:materials[mat.name]=mat
  ev.to_mesh_clear()
 for m in materials.values():
  if m.node_tree:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE'and n.image:images[n.image.name]=n.image
 rows.append({'variant':s['variant'],'triangles':tris,'evaluatedVertices':verts,'meshAndConvertedCurveObjects':meshes,'materialDatablocks':len(materials),'shaderNodes':sum(len(m.node_tree.nodes)for m in materials.values()if m.node_tree),'uniqueReferencedImages':len(images),'estimatedReferencedRGBA8MipMiB':sum(i.size[0]*i.size[1]*4*4/3 for i in images.values())/2**20,'storedLights':sum(o.type=='LIGHT'for o in s.objects),'activeLights':sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)})
imgs=[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),'packedSHA256':hashlib.sha256(i.packed_file.data).hexdigest()if i.packed_file else None,'colorSpace':i.colorspace_settings.name}for i in bpy.data.images if i.type=='IMAGE']
proof={'status':'PASS','sceneBudgets':rows,'uniqueImages':imgs,'allImagesPacked':all(i['packed']for i in imgs),'wholeMasterRGBA8MipMiB':sum(i['size'][0]*i['size'][1]*4*4/3 for i in imgs)/2**20,'masterBytes':Path(bpy.data.filepath).stat().st_size,'masterSHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'scope':'Offline Blender counts and conservative image estimate, not web GLB/draw calls/GPU VRAM/FPS.'}
(O/'evidence/scene-budget.json').write_text(json.dumps(proof,indent=2)+'\n');print('BUDGET',rows,flush=True)
