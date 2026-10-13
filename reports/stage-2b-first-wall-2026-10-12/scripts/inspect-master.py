import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path.cwd();bpy.ops.wm.open_mainfile(filepath=str(root/'assets-source/gullyverse/first-wall-section/first-wall-section.blend'))
rows=[];errors=[];master=bpy.data.objects['Wall_Master'];bvhs={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();rows.append({'name':o.name,'nonManifoldEdges':non,'volume':vol,'UVLayers':[u.name for u in o.data.uv_layers],'scale':list(o.scale),'rotation':list(o.rotation_euler)});assert non==0 and vol>0
 if o.name.startswith('Wall_LOD') or o.name=='Wall_Master':bvhs[o.name]=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
# Stratified ray sample over front: morphology deviation only, not silhouette/Hausdorff/visual certification.
for name,bvh in bvhs.items():
 if name=='Wall_Master':continue
 diffs=[]
 for ix in range(50):
  for iz in range(65):
   x=-7.3+15.4*(ix+.5)/50;z=-9.6+19.8*(iz+.5)/65
   a=bvhs['Wall_Master'].ray_cast((x,-4,z),(0,1,0),10)[0];b=bvh.ray_cast((x,-4,z),(0,1,0),10)[0]
   if a is not None and b is not None:diffs.append(abs(a.y-b.y))
 diffs.sort();errors.append({'LOD':name,'samples':len(diffs),'rmsM':math.sqrt(sum(d*d for d in diffs)/len(diffs)),'p95M':diffs[int(len(diffs)*.95)],'maxM':max(diffs),'method':'50x65 front-plane ray samples versus editable master; not Hausdorff distance'})
result={'blender':bpy.app.version_string,'metreScale':bpy.context.scene.unit_settings.scale_length,'objects':rows,'LODerrors':errors,'images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'colorspace':i.colorspace_settings.name} for i in bpy.data.images if i.source=='FILE']}
(root/'reports/stage-2b-first-wall-2026-10-12/raw/master-inspection.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
