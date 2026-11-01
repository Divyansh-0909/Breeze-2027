import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1]
scene=next(s for s in bpy.data.scenes if s['variant']=='C');bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
v=[];f=[];names=[]
for ob in scene.objects:
 if ob.type!='MESH'or ob.name.startswith('Bounded lane haze'):continue
 ev=ob.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();base=len(v);v.extend(ev.matrix_world@p.co for p in m.vertices);f.extend(tuple(base+i for i in t.vertices)for t in m.loop_triangles);names.extend([ob.name]*len(m.loop_triangles));ev.to_mesh_clear()
tree=BVHTree.FromPolygons(v,f,all_triangles=True)
results=[]
for side,cy,index in [(-1,-25,0),(-1,-16,1),(-1,2,3),(1,-25,0),(1,-16,1),(1,-7,2),(1,2,3)]:
 host=bpy.data.objects[f'Building / {side} / {index}'];top=max((host.matrix_world@p.co).z for p in host.data.vertices)
 for z in [10.0,10.6,11.2,12.0,12.8,13.6]:
  if z+.55>top:continue
  for dy in [-2,0,2]:
   clear=True;hits=[]
   for y in [cy+dy-1.6,cy+dy-.8,cy+dy,cy+dy+.8,cy+dy+1.6]:
    for zz in [z-.52,z,z+.52]:
     h=tree.ray_cast(Vector((0,y,zz)),Vector((side,0,0)),5)
     hit=names[h[2]]if h[0]is not None else'none';hits.append(hit)
     clear&=hit==host.name
   if clear:results.append({'host':host.name,'side':side,'centerY':cy+dy,'centerZ':z,'widthM':3.2,'heightM':1.04,'clearWallProbeRays':len(hits),'faceX':side*4})
(O/'evidence/wall-candidate-survey.json').write_text(json.dumps({'status':'SURVEY_COMPLETE_NOT_PLACEMENT_LOCK','clearBlankRectangles':results},indent=2)+'\n')
print('CLEAR_BLANK_WALLS',results,flush=True)
rig=bpy.data.collections['04_SHARED_CAMERA_RIG']
specs=[('candidate-lane-left',(0,-27,8.8),(-4,-18,10.6),23),('candidate-lane-right',(0,-22,8.8),(4,-13,10.6),23),('candidate-transition',(0,21,10),(11.5,14.3,7.75),26)]
for name,loc,target,lens in specs:
 d=bpy.data.cameras.new(name);d.lens=lens;ob=bpy.data.objects.new(name,d);rig.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();scene.camera=ob
 scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16;scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
 target=O/'renders/candidates'/f'{name}.png';target.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
print('CANDIDATE_RENDERS_COMPLETE')
