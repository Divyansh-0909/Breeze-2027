"""Clearly separate NEUTRAL OFFLINE source diagnostics. Never saves/relights master."""
import bpy,json,sys,math,time,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];master=Path(bpy.data.filepath);a=json.loads((O/'evidence/authoring.json').read_text());source_scene=next(s for s in bpy.data.scenes if s.get('variant')=='SOURCE AUDIT');bpy.context.window.scene=source_scene;bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
sc=bpy.data.scenes.new('UNSAVED / neutral source inspection');bpy.context.window.scene=sc;sc.render.engine='BLENDER_EEVEE_NEXT';sc.eevee.taa_render_samples=16;sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX'
w=bpy.data.worlds.new('UNSAVED neutral diagnostic');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.20,.20,.20,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;sc.world=w
def diffuse(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=.7;return m
clay=diffuse('UNSAVED clay - texture disabled',(.35,.38,.4));floor=diffuse('UNSAVED diagnostic floor',(.15,.16,.17))
me=bpy.data.meshes.new('UNSAVED floor');me.from_pydata([(-35,-20,-.01),(35,-20,-.01),(35,30,-.01),(-35,30,-.01)],[],[(0,1,2,3)]);o=bpy.data.objects.new('UNSAVED diagnostic ground',me);sc.collection.objects.link(o);me.materials.append(floor)
for loc,power,size in[((-5,-4,8),1800,7),((5,4,6),900,5)]:
 d=bpy.data.lights.new('UNSAVED diagnostic area','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
camd=bpy.data.cameras.new('UNSAVED source camera');cam=bpy.data.objects.new(camd.name,camd);sc.collection.objects.link(cam);sc.camera=cam;camd.lens=45;created=[];records=[]
def capture(name,loc,target):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();p=O/'renders/source-diagnostics'/f'{name}.png';p.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(p);bpy.ops.render.render(write_still=True);records.append({'file':str(p.relative_to(O)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lighting':'UNSAVED NEUTRAL DIAGNOSTIC ONLY','actualWebsiteScreenshot':False,'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest()})
def clear():
 for o in created:sc.collection.objects.unlink(o)
 created.clear()
def put(name,mesh,loc,scale=1,clay_override=False):
 o=bpy.data.objects.new(name,mesh);sc.collection.objects.link(o);o.location=loc;o.scale=(scale,)*3
 if clay_override:
  for slot in o.material_slots:slot.link='OBJECT';slot.material=clay
 created.append(o);return o
# Left pair built directly from Node-serialized web output; right pair references exact master data.
data=json.loads((O/'source/website/exact-baked-poses.json').read_text())
for i,vi in enumerate([0,2]):
 d=data[vi];v=d['positions'];ix=d['indices'];m=bpy.data.meshes.new('UNSAVED direct Node '+str(vi));m.from_pydata([(v[j],-v[j+2],v[j+1])for j in range(0,len(v),3)],[],[ix[j:j+3]for j in range(0,len(ix),3)]);m.update();nm=d['normals'];m.normals_split_custom_set_from_vertices([(nm[j],-nm[j+2],nm[j+1])for j in range(0,len(nm),3)])
 for p in m.polygons:p.use_smooth=True
 m.materials.append(clay)
 put('DIRECT NODE / '+str(vi),m,(-2.9+i*1.35,0,0),1.8);put('BLENDER MASTER / '+str(vi),bpy.data.meshes['WEB EXACT POSE '+str(vi)],(1.4+i*1.35,0,0),1.8,True)
capture('01-web-output-vs-blender-clay',(0,-9,3.25),(0,0,.95));clear()
# Four exact silhouette poses; the actual runtime overrides all source colors with near-black Lambert.
for i in range(4):put('EXACT WEB SILHOUETTE '+str(i),bpy.data.meshes['WEB EXACT POSE '+str(i)],(-2.4+i*1.6,0,0),1.8)
capture('02-four-web-silhouettes',(0,-9,3.25),(0,0,.95));clear()
# Active stage roadcase, native dimensions and steel material retained. Right is the translated copy.
for side in[-1,1]:
 for suffix in['PROP_roadcase_0','PROP_roadcase_trim_0']:
  src=next(o for o in source_scene.objects if o.get('websiteOriginalName')==suffix);r=next(r for r in a['originalPropMetadata']if r['object']==src.name);q=put('SOURCE CASE MATCH '+str(side)+suffix,src.data,(0,0,0));q.matrix_world=Matrix.Translation(Vector((side*1.8+10.1,-2.5,-1.31)))@Matrix(r['matrix'])
capture('03-active-website-roadcase-parity',(0,-7,3.3),(0,0,.5));clear()
# Dormant table source: faithful mesh extraction, explicitly not an active website steel-table claim.
for suffix in['TABLE_top','TABLE_cloth_front','TABLE_cloth_left','TABLE_cloth_right']:
 src=next(o for o in source_scene.objects if o.get('websiteOriginalName')==suffix);r=next(r for r in a['originalPropMetadata']if r['object']==src.name);q=put('ARCHIVED TABLE '+suffix,src.data,(0,0,0));q.matrix_world=Matrix.Translation(Vector((0,2.09,.04)))@Matrix(r['matrix'])
capture('04-archived-table-not-active-steel-table',(5,-7,3.7),(0,0,.75));clear()
(O/'evidence/source-diagnostic-renders.json').write_text(json.dumps(records,indent=2));print('SOURCE_DIAGNOSTICS_COMPLETE',len(records),flush=True)
