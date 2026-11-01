import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/before-survey.json').read_text());eligible=[]
for row in d['actors']:
 head=next(bpy.data.objects[n]for n in row['objects']if n.endswith(' head'));stature=max((head.matrix_basis@v.co).z for v in head.data.vertices)-7.2
 if abs(stature-row['heightM'])<.005:eligible.append(row)
actor=min(eligible,key=lambda a:abs(a['heightM']-1.7))
s=bpy.data.scenes.new('DIAGNOSTIC ONLY / actual human-scale rulers');bpy.context.window.scene=s;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world=bpy.data.worlds.new('Diagnostic neutral background');s.world.color=(.65,.65,.65)
def mat(name,color):
 m=bpy.data.materials.new('DIAGNOSTIC / '+name);m.diffuse_color=(*color,1);return m
red=mat('ruler',(.65,.03,.03));dark=mat('labels',(.02,.02,.02));grey=mat('reference',(.30,.42,.5));ground=mat('ground',(.4,.4,.4))
def box(name,p,dim,m):
 x,y,z=p;a,b,c=[q/2 for q in dim];v=[(x+sx*a,y+sy*b,z+sz*c)for sx,sy,sz in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];me=bpy.data.meshes.new(name);me.from_pydata(v,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.materials.append(m);o=bpy.data.objects.new(name,me);s.collection.objects.link(o)
def text(body,p,size=.16):
 c=bpy.data.curves.new('dimension','FONT');c.body=body;c.size=size;c.align_x='CENTER';c.materials.append(dark);o=bpy.data.objects.new('DIAGNOSTIC '+body,c);o.location=p;o.rotation_euler=(math.pi/2,0,0);s.collection.objects.link(o)
for x,f in[(0,1),(1.5,1.06),(3,1.07),(4.5,1.09),(6,1.7/actor['heightM'])]:
 for n in actor['objects']:
  src=bpy.data.objects[n];o=src.copy();o.data=src.data.copy();o.matrix_basis.identity()
  for va,vb in zip(src.data.vertices,o.data.vertices):
   p=src.matrix_basis@va.co;vb.co=(p.x-actor['foot'][0]+x,p.y-actor['foot'][1],(p.z-7.2)*f)
  s.collection.objects.link(o)
 title=('+0%'if f==1 else'+6%'if f==1.06 else'+7% proposed'if f==1.07 else'+9%'if f==1.09 else'1.700m reference')
 text(title,(x,-.60,-.23),.14);text(f'{actor["heightM"]*f:.3f}m',(x,-.60,actor['heightM']*f+.18),.14)
 box('1.7m vertical ruler',(x+.45,0,.85),(.018,.03,1.7),red)
 for zz in[0,.5,1,1.5,1.7]:box('tick',(x+.45,0,zz),(.16,.03,.015),red)
for x in[7.6,8.6]:box('2.1m door jamb',(x,0,1.05),(.08,.18,2.1),grey)
box('2.1m clear lintel',(8.1,0,2.14),(1.08,.18,.08),grey);text('2.1m clear door',(8.1,-.6,-.23),.14)
box('1.1m parapet',(9.9,0,.55),(1.0,.20,1.10),grey);text('1.1m parapet',(9.9,-.6,-.23),.14)
box('3m floor datum',(11.1,0,1.5),(.02,.03,3.0),red)
for z in[0,3]:box('3m storey tick',(11.1,0,z),(.5,.03,.02),red)
text('3.0m storey',(11.1,-.6,-.23),.14);box('floor',(5.5,0,-.065),(13,2,.1),ground)
cd=bpy.data.cameras.new('Diagnostic scale camera');cam=bpy.data.objects.new('Diagnostic scale camera',cd);s.collection.objects.link(cam);cam.location=(5.5,-16,1.65);cam.rotation_euler=(Vector((5.5,0,1.65))-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=13.7;s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.filepath=str(O/'review/actual-blender-scale-rulers.png');s.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)
(O/'evidence/scale-diagnostic.json').write_text(json.dumps({'evidence':'ACTUAL BLENDER WORKBENCH DIAGNOSTIC; studio inspection only, no selected scene or lighting change','sourceActor':actor['label'],'sourceActorHeightM':actor['heightM'],'referenceHeightM':1.7,'doorClearHeightM':2.1,'parapetM':1.1,'storeyM':3,'file':'review/actual-blender-scale-rulers.png','sha256':hashlib.sha256((O/'review/actual-blender-scale-rulers.png').read_bytes()).hexdigest()},indent=2))
