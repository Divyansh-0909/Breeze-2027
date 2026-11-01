import bpy,json,collections,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];rows=[]
for s in bpy.data.scenes:
 if s.get('variant')=='SOURCE AUDIT':continue
 bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();tris=0;meshes=set();mats=set();images=set()
 for o in s.objects:
  if o.type not in ['MESH','CURVE','FONT']:continue
  ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);meshes.add(o.data.name);ev.to_mesh_clear()
  for sl in o.material_slots:
   if not sl.material:continue
   mat=sl.material;mats.add(mat.name)
   if mat.node_tree:
    for n in mat.node_tree.nodes:
     if n.type=='TEX_IMAGE'and n.image:images.add(n.image.name)
 mem=sum(bpy.data.images[n].size[0]*bpy.data.images[n].size[1]*4*4/3 for n in images)
 rows.append({'variant':s['variant'],'triangles':tris,'meshCurveOwners':sum(o.type in ['MESH','CURVE']for o in s.objects),'sharedGeometryDatablocks':len(meshes),'materials':len(mats),'shaderNodes':sum(len(bpy.data.materials[n].node_tree.nodes)if bpy.data.materials[n].node_tree else 0 for n in mats),'uniqueImageOwners':len(images),'RGBA8PlusMipsMiBEstimate':mem/1024**2,'lights':sum(o.type=='LIGHT'for o in s.objects),'activeLights':sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)})
poses=[bpy.data.meshes['WEB EXACT POSE '+str(i)]for i in range(4)];byteestimate=sum(len(m.vertices)*3*4*2+len(m.polygons)*3*4 for m in poses)
a=json.loads((O/'evidence/authoring.json').read_text());r={'status':'MEASURED_BLENDER_COUNTS_ONLY','masterBytes':(O/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend').stat().st_size,'rows':rows,'crowdSourceGLBBytes':sum((O/'source/website'/n).stat().st_size for n in['Man.glb','Animated-Woman.glb']),'fourSharedPosePositionNormalUint32IndexByteEstimate':byteestimate,'selectedCrowdTriangles':sum(len(bpy.data.objects[r['object']].data.polygons)for r in a['actors']),'selectedCrowdCount':180,'possibleCrowdInstanceDraws':4,'newCrowdImageBytes':0,'newArchitectureImageOwners':0,'newDynamicLights':0,'runtimeDrawsFPSVRAMOrMobileNotMeasured':True,'reuseCaveQuarryOrWebsiteNotImplemented':True}
(O/'evidence/budget.json').write_text(json.dumps(r,indent=2));print('BUDGET',json.dumps(r),flush=True)
