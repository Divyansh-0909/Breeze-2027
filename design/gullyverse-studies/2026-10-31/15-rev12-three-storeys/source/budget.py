import bpy,json,hashlib,statistics
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];out=[]
for variant in ['REV11','REV12']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();materials={slot.material for o in s.objects for slot in o.material_slots if slot.material};images={n.image for m in materials if m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image};tri=0
 for o in s.objects:
  if o.type in ['MESH','CURVE','FONT']:
   ev=o.evaluated_get(dep);mesh=ev.to_mesh();mesh.calc_loop_triangles();tri+=len(mesh.loop_triangles);ev.to_mesh_clear()
 out.append({'variant':variant,'triangles':tri,'meshCurveOwners':sum(o.type in ['MESH','CURVE']for o in s.objects),'geometryDatablocks':len({o.data for o in s.objects if o.type in ['MESH','CURVE','FONT']}),'materialOwners':len(materials),'shaderNodes':sum(len(m.node_tree.nodes)for m in materials if m.node_tree),'imageOwners':len(images),'RGBA8PlusMipsMiBEstimate':sum(i.size[0]*i.size[1]*4*4/3 for i in images)/1048576,'lightOwners':sum(o.type=='LIGHT'for o in s.objects),'activeLights':sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)})

result={'status':'MEASURED_OFFLINE_BLENDER_ONLY','rows':out,'masterBytes':Path(bpy.data.filepath).stat().st_size,'masterSHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'newImages':0,'newTextureBytes':0,'newLightOwners':0,'sharedC180NoExtraScaling':True,'noClaimOfBrowserDrawCallsFPSVRAMOrHardwareCertification':True,'futureRuntimeRecommendation':'Partition continuous shell at registered party walls; instance repeated windows/rails; near/mid/far LODs to be evaluated without altering floor/actor/art ownership.'};(O/'evidence/budget.json').write_text(json.dumps(result,indent=2));print('BUDGET',json.dumps(result))
