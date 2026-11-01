"""Proposal-only crowds and counters, isolated from the world."""
import bpy,json,math,hashlib,time
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];src=next(s for s in bpy.data.scenes if s.get('variant')=='C+A PILOT');d=json.loads((O/'evidence/rev05b-authoring.json').read_text());actor=next(r for r in d['actors']if r['label']=='Audience 00_00');foot=Vector(actor['foot']);old=[bpy.data.objects[n]for n in actor['objects']];H=max((o.matrix_world@v.co).z for o in old for v in o.data.vertices)-foot.z
scenes=[];measures=[];jobs=[]
def scene(name,counter=False):
 s=src.copy();s.name='PROPOSAL ONLY / '+name;s['variant']='OPTION '+name;s.use_fake_user=True
 for c in list(s.collection.children):s.collection.children.unlink(c)
 for o in list(s.collection.objects):s.collection.objects.unlink(o)
 for o in src.objects:
  if o.type=='LIGHT'or o.get('pilotOriginalObject',o.name).startswith('Lane flat'if counter else'Rooftop slab'):s.collection.objects.link(o)
 bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();scenes.append(s);return s
def mat(name,col,rough=.88,metal=0):
 m=bpy.data.materials.new('OPTION / '+name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;return m
shirt=mat('matte petrol cotton',(.065,.12,.14));skin=mat('skin',(.23,.13,.085),.72);pants=mat('dark cotton',(.055,.065,.067));hair=mat('hair',(.025,.021,.018));shoe=mat('canvas shoes',(.035,.04,.038))
def rings(name,rr,n,material,s):
 v=[]
 for z,rx,ry,x,y in rr:
  for j in range(n):
   a=2*math.pi*j/n;p=Vector(((x+rx*math.cos(a))*actor['widthScale'],(y+ry*math.sin(a))*actor['widthScale'],z*H/1.818));p=Matrix.Rotation(actor['yawRadians'],3,'Z')@p+foot;v.append(list(p))
 f=[tuple(range(n-1,-1,-1)),tuple((len(rr)-1)*n+j for j in range(n))]
 for k in range(len(rr)-1):
  for j in range(n):a=k*n+j;b=k*n+(j+1)%n;f.append((a,b,b+n,a+n))
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new('OPTION / '+name,m);s.collection.objects.link(o);m.materials.append(material)
 for p in m.polygons:p.use_smooth=len(p.vertices)==4
 return o
def cam(s,name,pos,target,lens):
 m=bpy.data.cameras.new('OPTION camera / '+name);m.lens=lens;m.sensor_width=36;o=bpy.data.objects.new(m.name,m);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();jobs.append({'name':name,'scene':s.name,'camera':o.name})
for mode in range(4):
 s=scene('crowd '+str(mode));objs=[]
 if mode<2:
  for o in old:
   cp=o.copy();cp.data=o.data.copy();cp.name='OPTION / '+o.name;s.collection.objects.link(cp);objs.append(cp)
   if mode==1:
    for p in cp.data.polygons:p.use_smooth=True
    cp.data.materials.clear();cp.data.materials.append(skin if'head'in o.name or'forearm'in o.name else pants if'trouser'in o.name else shirt)
 else:
  n=8 if mode==2 else 12
  objs.append(rings('tapered torso',[(.84,.16,.115,0,0),(1,.165,.12,0,0),(1.30,.205,.115,0,0),(1.40,.185,.105,0,0),(1.47,.085,.07,0,0)],n,shirt,s))
  for sign in[-1,1]:
   objs.append(rings('trousers',[(.10,.075,.077,sign*.09,0),(.46,.071,.074,sign*.095,.015),(.82,.085,.086,sign*.088,0),(.92,.088,.09,sign*.087,0)],n,pants,s))
   objs.append(rings('sleeve',[(1.16,.065,.070,sign*.238,.005),(1.35,.08,.082,sign*.211,0),(1.42,.065,.065,sign*.182,0)],n,shirt,s))
   objs.append(rings('arm',[(.88,.043,.046,sign*.255,.05),(1,.052,.052,sign*.25,.035),(1.17,.055,.055,sign*.238,.005)],n,skin,s))
   objs.append(rings('shoes',[(0,.079,.13,sign*.09,.04),(.075,.079,.13,sign*.09,.04),(.12,.065,.07,sign*.09,0)],n,shoe,s))
  objs.append(rings('neck',[(1.43,.061,.061,0,0),(1.52,.061,.061,0,0)],n,skin,s))
  objs.append(rings('head',[(1.49,.067,.065,0,0),(1.56,.105,.09,0,.005),(1.68,.112,.10,0,0),(1.77,.082,.077,0,-.005),(1.81,.03,.03,0,-.01)],n,skin,s))
  objs.append(rings('hair cap',[(1.70,.113,.101,0,0),(1.78,.083,.078,0,-.005),(1.818,.025,.026,0,-.01)],n,hair,s))
 tris=sum(len(p.vertices)-2 for o in objs for p in o.data.polygons)
 measures.append({'kind':'crowd','option':mode,'description':['locked control','same topology, smooth shading and matte cloth','8-sided tapered spectator silhouette','12-sided tapered spectator silhouette'][mode],'sourceActor':actor['label'],'foot':actor['foot'],'yaw':actor['yawRadians'],'sourceHeightM':H,'sameFootYawHeight':True,'trianglesPerActor':tris,'trianglesFor180':tris*180,'partOwners':len(objs),'newTextureBytes':0,'status':'PROPOSAL_ONLY_NOT_APPLIED'})
 for front in[False,True]:
  cam(s,('crowd-face-'if front else'crowd-')+str(mode),foot+Vector((-1.5,2.6,1.4)if front else(2.2,-3.1,1.4)),foot+Vector((0,0,1.05)),40)
wood=bpy.data.materials['PILOT / worn plywood edge'];metal=bpy.data.materials['PILOT / folded galvanised sheet'];dark=bpy.data.materials['PILOT / blackened zinc and aged fixings']
def box(s,name,loc,dim,material):
 x,y,z=loc;a,b,c=[q/2 for q in dim];v=[(x+sx*a,y+sy*b,z+sz*c)for sx,sy,sz in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 m=bpy.data.meshes.new(name);m.from_pydata(v,[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);m.update();o=bpy.data.objects.new('OPTION / '+name,m);s.collection.objects.link(o);m.materials.append(material);return o
for mode in range(3):
 s=scene('counter '+str(mode),True);objs=[];cy=-25;g=6
 if mode==0:
  o=bpy.data.objects['PILOT / Counter'];cp=o.copy();cp.data=o.data.copy();s.collection.objects.link(cp);objs=[cp]
 else:
  objs.append(box(s,'replaceable top',(-3.28,cy,g+1.255),(1,3.3,.05),metal if mode==1 else wood))
  if mode==1:
   for x in[-3.72,-2.84]:
    for y in[cy-1.57,cy+1.57]:objs.append(box(s,'tube leg',(x,y,g+.625),(.055,.055,1.25),dark))
   objs.append(box(s,'under shelf',(-3.28,cy,g+.28),(.86,3.13,.035),wood))
   for y in[cy-1.56,cy+1.56]:objs.append(box(s,'apron',(-3.28,y,g+1.16),(.86,.04,.14),metal))
  else:
   objs.append(box(s,'ply case',(-3.28,cy,g+.66),(.94,3.18,1.15),wood));objs.append(box(s,'recessed toe',(-3.32,cy,g+.06),(.80,3.06,.12),dark))
   for dy in[-1.04,0,1.04]:objs.append(box(s,'inset panel',(-2.796,cy+dy,g+.67),(.02,1.01,1.07),wood));objs.append(box(s,'pull',(-2.784,cy+dy+.36,g+.96),(.016,.04,.14),metal))
 measures.append({'kind':'counter','option':mode,'description':['protected cuboid / control','open steel service counter','repairable plywood case / recessed toe'][mode],'triangles':sum(len(p.vertices)-2 for o in objs for p in o.data.polygons),'owners':len(objs),'footprint':[1,3.3,1.28],'newTextureBytes':0,'status':'PROPOSAL_ONLY_NOT_APPLIED'})
 cam(s,'counter-'+str(mode),(-.5,cy-3.5,g+1.8),(-3.28,cy,g+.65),36)
for oldscene in list(bpy.data.scenes):
 if oldscene not in scenes:bpy.data.scenes.remove(oldscene)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();master=O/'source/Crowd-and-Counter-Proposals-Only.blend';bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
proof={'status':'PROPOSALS_ONLY','masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'measurements':measures,'jobs':jobs,'renders':[]};path=O/'evidence/options.json';path.write_text(json.dumps(proof,indent=2)+'\n')
for job in jobs:
 s=bpy.data.scenes[job['scene']];bpy.context.window.scene=s;s.camera=bpy.data.objects[job['camera']];s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';f=O/'renders/options'/f"{job['name']}.png";f.parent.mkdir(exist_ok=True,parents=True);s.render.filepath=str(f);start=time.monotonic();bpy.ops.render.render(write_still=True)
 proof['renders'].append({**job,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'seconds':time.monotonic()-start,'lens':s.camera.data.lens,'position':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'samples':16,'supportW':0});path.write_text(json.dumps(proof,indent=2)+'\n')
print('OPTIONS_DONE',flush=True)
