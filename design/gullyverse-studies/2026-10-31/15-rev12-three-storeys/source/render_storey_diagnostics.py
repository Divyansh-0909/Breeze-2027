import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from rooftop_cameras import add
d=json.loads((O/'evidence/authoring.json').read_text());old=json.loads((O/'evidence/before-storey-survey.json').read_text());rows=[]
def point(h,u,dep,z):
 c=sum(h['alongM'])/2;f=h['frontM'];e=h['edge'];return Vector((-f-dep,c+u,z))if e=='left'else Vector((f+dep,c-u,z))if e=='right'else Vector((c-u,f-dep,z))if e=='front'else Vector((c+u,f+dep,z))
for edition,variant in [('before','REV11'),('new','REV12')]:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant).copy();s.name='UNSAVED DIAGNOSTIC / '+edition;bpy.context.window.scene=s;s.frame_set(1);add(s)
 s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world=bpy.data.worlds.new('UNSAVED diagnostic studio '+edition);s.world.color=(.35,.35,.35)
 for ob in s.objects:
  ob.color=(.55,.55,.55,1)
  if ob.name.startswith('Bounded lane haze'):ob.hide_render=True
 def rod(name,a,b,r,color):
  dd=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=dd.length,location=(Vector(a)+Vector(b))/2);ob=bpy.context.object;[(c.objects.unlink(ob))for c in list(ob.users_collection)];s.collection.objects.link(ob);ob.name='DIAGNOSTIC / '+name;ob.rotation_euler=dd.to_track_quat('Z','Y').to_euler();ob.color=(*color,1)
 def text(name,p,color,size=.8):
  cu=bpy.data.curves.new('DIAG label','FONT');cu.body=name;cu.align_x='CENTER';cu.size=size;ob=bpy.data.objects.new('DIAGNOSTIC / '+name,cu);s.collection.objects.link(ob);ob.location=p;ob.color=(*color,1);return ob
 labels=[]
 for h in d['houses']:
  o=next(r for r in old['rows']if r['id']==h['id']);count=d['targetLevels'][h['id']]if edition=='new'else o['actualCourtResidentialLevels'];color=(.02,.48,.14)if count>=3 else(.8,.025,.025);roof=h['mainRoofZ']if edition=='new'else o['mainRoofZ'];offsets=h['setbacksM']if edition=='new'else next(r for r in json.loads((O/'baseline/evidence/authoring.json').read_text())['houses']if r['id']==h['id'])['setbacksM']
  for level in range(count):
   z=7.2+3*level;off=offsets[level];rod(h['id']+' measured floor '+str(level+1),point(h,-h['widthM']/2,off-.035,z),point(h,h['widthM']/2,off-.035,z),.045,color)
  labels.append(text(h['id']+' / '+str(count),point(h,0,offsets[-1]-.15,roof+2.8),color,.9))
 # Physical 1.700m ruler above the unchanged courtyard, plus clear floor datum tick.
 p=Vector((-15,19,7.2));rod('1.700m ruler',p,p+Vector((0,0,1.7)),.045,(.8,.02,.02))
 for z in[0,.5,1,1.5,1.7]:rod('ruler tick',p+Vector((-.2,0,z)),p+Vector((.2,0,z)),.025,(.8,.02,.02))
 labels.append(text('1.700m',p+Vector((0,0,2.1)),(.8,.02,.02),.45))
 for pose in['03-aerial','12-elevation','04-front','01-plan']:
  s.camera=bpy.data.objects['REV10 CAMERA / '+pose]
  for ob in labels:ob.rotation_euler=(s.camera.location-ob.location).to_track_quat('Z','Y').to_euler()
  s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';f=O/'review'/('DIAGNOSTIC-count-'+edition+'-'+pose+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);rows.append({'edition':edition,'pose':pose,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'diagnosticOnly':True,'geometryPreserved':True,'masterNeverSaved':True,'floorBandsAreMeasuredAnnotationsNotGeometryUsedForCount':True,'redBelowThree':True,'neutralStudioNotSelectedLights':True,'viewport':[1600,1000]})
(O/'evidence/storey-diagnostic-renders.json').write_text(json.dumps(rows,indent=2));print('COUNT_DIAGNOSTICS_COMPLETE',flush=True)

for edition,variant in [('before','REV11'),('new','REV12')]:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);add(s);s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='FLAT';sh.color_type='SINGLE';sh.single_color=(0,0,0);sh.show_shadows=False;sh.show_cavity=False;sh.background_type='WORLD';s.world=bpy.data.worlds.new('UNSAVED silhouette white');s.world.color=(1,1,1)
 for ob in s.objects:
  if ob.name.startswith('Bounded lane haze'):ob.hide_render=True
 for pose in ['04-front','03-aerial']:
  s.camera=bpy.data.objects['REV10 CAMERA / '+pose];s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';f=O/'review'/('DIAGNOSTIC-silhouette-'+edition+'-'+pose+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);rows.append({'edition':edition,'pose':pose,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'diagnosticOnly':True,'geometryPreserved':True,'masterNeverSaved':True,'sameOriginalCamera':True})
(O/'evidence/storey-diagnostic-renders.json').write_text(json.dumps(rows,indent=2))
