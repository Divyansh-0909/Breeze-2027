"""Private Blender derivative only. All baseline scenes/objects remain untouched."""
import bpy,bmesh,json,math,hashlib,sys,ast
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];cfg=json.loads((O/'source/BASELINE.json').read_text());BASE=Path(cfg['path']);assert hashlib.sha256(BASE.read_bytes()).hexdigest()==cfg['sha256']
old=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD')
def scene_copy(src,name,variant):
 s=src.copy();s.name=name;s['variant']=variant;s.use_fake_user=True
 for c in list(s.collection.children):s.collection.children.unlink(c)
 for o in list(s.collection.objects):s.collection.objects.unlink(o)
 c=bpy.data.collections.new(variant+' / inherited');s.collection.children.link(c)
 for o in src.objects:c.objects.link(o)
 return s,c
before_scene,_=scene_copy(old,'REV08 0 / Before Wider World','TERRACE BEFORE')
s,hosts=scene_copy(old,'REV08 I / Continuous Rooftop / Old Crowd','TERRACE ARCH');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
details=bpy.data.collections.new('REV08 / terrace construction');s.collection.children.link(details)
# Reuse the reviewed physical-material hierarchy and metre UV convention.
text=(O/'source/geometry_helpers.py').read_text();tree=ast.parse(text)
for n in tree.body:
 if isinstance(n,ast.FunctionDef)and n.name in ['piece','box','rod','uvmetre']:exec(compile(ast.Module(body=[n],type_ignores=[]),str(BASE),'exec'))
parts=[];buckets={};cement=bpy.data.materials['WORLD / mineral concrete'];lime=bpy.data.materials['WORLD / warm grey limewash'];sage=bpy.data.materials['WORLD / faded blue-green plaster'];roof=bpy.data.materials['WORLD / continuous roof concrete'];seal=bpy.data.materials['PILOT / bituminous joint and gaskets'];steel=bpy.data.materials['PILOT / blackened zinc and aged fixings'];zinc=bpy.data.materials['PILOT / folded galvanised sheet'];glass=bpy.data.materials['WORLD / dusty non-emissive glazing'];frame=bpy.data.materials['WORLD / aged painted sash'];repair=bpy.data.materials['WORLD / localized render repair']
# Existing slab top stays Z7.2 exactly. Add actual supporting storeys BELOW it.
for side in [-1,1]:
 zone=f'loadbearing side {side}'
 box('support facade',(side*15.87,31,3.49),(.24,34,6.68),lime,zone)
 for zz in[3.25,6.67]:box('continuous RC edge beam',(side*15.90,31,zz),(.34,34,.28),cement,zone)
 for yy in[14.2,20.8,27.4,34,40.6,47.8]:box('RC facade pier',(side*15.94,yy,3.42),(.38,.28,6.60),cement,zone)
 # Outer-facing lower storey details make elevation readable as roof, not plaza.
 for yy in[17.4,24.1,30.8,37.5,44.1]:
  for zz in[1.8,5.0]:
   box('lower storey glazing',(side*16.006,yy,zz),(.02,1.52,1.22),glass,zone)
   for dy in[-.80,.80]:box('window jamb',(side*16.04,yy+dy,zz),(.08,.07,1.36),cement,zone)
   for dz in[-.65,.65]:box('window sill',(side*16.06,yy,zz+dz),(.14,1.66,.07),cement,zone)
 box('adjoining terrace deck',(side*18,31,7.00),(3.98,34,.36),roof,'perimeter roofs')
 box('outer terrace guarding',(side*19.85,31,7.75),(.27,34,1.10),lime,'perimeter roofs')
 box('outer coping',(side*19.85,31,8.34),(.38,34,.08),cement,'perimeter roofs')
 box('front return below original art',(side*12.2,14.07,3.42),(7.55,.22,6.82),lime,'building base')
 for zz in[3.25,6.67]:box('front floor band',(side*12.2,13.96,zz),(7.60,.28,.25),cement,'building base')
 for xx in[side*9.5,side*12.2,side*14.9]:box('front lower glazing',(xx,13.94,4.7),(1.55,.035,1.3),glass,'building base')
box('rear building face',(0,48.05,3.42),(32,.25,6.82),lime,'building base')
box('rear roof edge beam',(0,48.09,6.67),(32,.36,.28),cement,'building base')
# Adjoining rooftops share slab level but remain behind the ORIGINAL guarding.
# Four service rooms face inward, with modelled jambs/recesses and closed doors.
room_specs=[(-1,21.2,6.0,3.35,sage),(1,20.5,5.7,3.65,lime),(-1,40.9,5.0,2.85,lime),(1,39.7,6.1,3.05,sage)]
for k,(side,cy,length,height,mat)in enumerate(room_specs):
 zone='terrace service room '+str(k);x=side*18.10;xfront=side*16.40;xback=side*19.76;g=7.20;dy=.48 if k%2 else -.52;door_y=cy+dy
 box('room back',(xback,cy,g+height/2),(.18,length,height),mat,zone)
 for yy in[cy-length/2+.09,cy+length/2-.09]:box('room end wall',(x,yy,g+height/2),(3.50,.18,height),mat,zone)
 # Front cut is framed by three solids, not a fake opening painted on a cube.
 for lo,hi in[(cy-length/2,door_y-.54),(door_y+.54,cy+length/2)]:box('inward facade jamb',(xfront,(lo+hi)/2,g+height/2),(.18,hi-lo,height),mat,zone)
 box('door lintel',(xfront,door_y,g+(2.22+height)/2),(.18,1.08,height-2.22),mat,zone)
 box('recessed steel access door',(side*16.52,door_y,g+1.07),(.06,.99,2.12),frame,zone)
 for yy in[door_y-.515,door_y+.515]:box('galvanized door return',(side*16.42,yy,g+1.10),(.18,.035,2.20),zinc,zone)
 box('door head flashing',(side*16.37,door_y,g+2.25),(.27,1.17,.055),zinc,zone)
 rod('door pull',(side*16.477,door_y+.32,g+.98),(side*16.477,door_y+.32,g+1.18),.012,zinc,zone)
 box('room roof slab',(x,cy,g+height+.09),(3.78,length+.28,.18),roof,zone)
 for yy in[cy-length/2,cy+length/2]:box('low roof parapet',(x,yy,g+height+.45),(3.64,.16,.56),mat,zone)
 box('outer roof parapet',(side*19.82,cy,g+height+.45),(.16,length,.56),mat,zone)
 for zz in[g+.18,g+height-.3]:box('local repair patch',(side*16.295,cy+length/2-.39,zz),(.025,.42,.22),repair,zone)
 # Ventilated louvre has real blade depth, restrained size and no emission.
 vy=cy-length/2+.85;vz=g+height-.71
 box('vent recess',(side*16.295,vy,vz),(.025,.72,.51),seal,zone)
 for j in range(6):box('vent louvre',(side*16.27,vy,vz-.21+j*.084),(.075,.68,.035),zinc,zone)
 # Pipe stays outside public circulation; saddles locate it physically.
 yy=cy+length/2+.12
 rod('roof drain',(side*16.27,yy,g+.05),(side*16.27,yy,g+height+.1),.035,zinc,zone)
 for z in[g+.55,g+2.05]:box('pipe clamp',(side*16.26,yy,z),(.13,.105,.04),steel,zone)
# Two rear access headhouses and a lower connecting roof wrap AROUND the screen.
for k,(x,y,w,l,h)in enumerate([(-11.5,49.1,3.5,2.7,3.5),(10.5,49.0,3.5,2.55,4.0),(0,51.5,12.8,3.9,2.8)]):
 zone='rear access roof '+str(k);mat=lime if k%2 else sage
 box('access roof body',(x,y,7.2+h/2),(w,l,h),mat,zone)
 box('access roof slab',(x,y,7.2+h+.10),(w+.22,l+.22,.20),roof,zone)
 box('access door',(x,y-l/2-.02,8.28),(1.0,.04,2.15),frame,zone)
 for dx in[-.54,.54]:box('access door jamb',(x+dx,y-l/2-.04,8.3),(.06,.12,2.22),zinc,zone)
 box('door drip',(x,y-l/2-.12,9.45),(1.22,.30,.06),cement,zone)
 for xx in[x-w/2,x+w/2]:box('roof edge return',(xx,y,7.2+h+.49),(.16,l,.60),mat,zone)
 box('roof rear parapet',(x,y+l/2,7.2+h+.49),(w,.16,.60),mat,zone)
# Modest rooftop storage tanks, physical ribbing, base pads and short pipe loops.
for k,(x,y,z)in enumerate([(-18.1,40.9,10.23),(18.1,20.5,11.03)]):
 zone='roof water service '+str(k);box('tank plinth',(x,y,z+.09),(1.65,1.65,.18),cement,zone)
 rod('water tank body',(x,y,z+.18),(x,y,z+1.55),.66,steel,zone,20)
 for zz in[z+.32,z+.56,z+.80,z+1.04,z+1.28,z+1.52]:rod('tank rib',(x,y,zz-.018),(x,y,zz+.018),.685,frame,zone,20)
 rod('tank lid',(x,y,z+1.55),(x,y,z+1.62),.32,steel,zone,16)
 rod('water riser',(x+.83,y,z-.15),(x+.83,y,z+1.4),.025,zinc,zone)
 rod('water inlet',(x+.83,y,z+1.4),(x+.60,y,z+1.4),.025,zinc,zone)
for side in[-1,1]:
 for yy in[27.0,32.3,45.1]:
  box('drain grate',(side*16.16,yy,7.205),(.22,.32,.01),steel,'roof services')
  rod('service downpipe',(side*16.18,yy,7.19),(side*16.18,yy,.42),.035,zinc,'roof services')
  for zz in[1.5,3.8,6.2]:box('downpipe saddle',(side*16.16,yy,zz),(.14,.11,.045),steel,'roof services')
 # Wires follow parapet outside edges. None cross the arrival/screen sightlines.
 for j in range(8):
  a=14.4+j*4.1;b=a+4.1;rod('perimeter conduit',(side*16.12,a,7.46),(side*16.12,b,7.46),.012,seal,'roof services')
 # Short guarded roof stretches between access volumes preserve open skyline.
 for yy in[29.5,33.7]:
  rod('outer handrail',(side*18.9,yy-1.7,8.45),(side*18.9,yy+1.7,8.45),.024,zinc,'roof services')
  for dy in[-1.7,0,1.7]:rod('handrail standard',(side*18.9,yy+dy,7.2),(side*18.9,yy+dy,8.45),.026,zinc,'roof services')
new=[]
for(zone,mat),d in buckets.items():
 m=bpy.data.meshes.new('REV08 '+zone);m.from_pydata(d['v'],[],d['f']);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(m);bm.free();m.update();o=bpy.data.objects.new('REV08 / '+zone+' / '+mat.split(' / ')[-1],m);details.objects.link(o);m.materials.append(bpy.data.materials[mat]);uvmetre(o);new.append(o.name)
# Exact four source idle bakes, using Crowd.tsx implementation in Node/Three.
rows=json.loads((O/'source/website/exact-baked-poses.json').read_text());pose_meshes=[]
color=tuple(((v/255)/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4)for v in[5,6,10])
sil=bpy.data.materials.new('WEB EXACT / Crowd.tsx Lambert #05060a');sil.use_nodes=True;n=sil.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(*color,1);diff.inputs['Roughness'].default_value=0;sil.node_tree.links.new(diff.outputs[0],out.inputs[0]);sil.diffuse_color=(*color,1);sil['sourceMaterial']='THREE.MeshLambertMaterial color #05060a; diffuse-only Blender analogue, no PBR relighting'
for i,r in enumerate(rows):
 p=r['positions'];v=[(p[j],-p[j+2],p[j+1])for j in range(0,len(p),3)];idx=r['indices'];f=[idx[j:j+3]for j in range(0,len(idx),3)];m=bpy.data.meshes.new('WEB EXACT POSE '+str(i));m.from_pydata(v,[],f);m.update();nm=r['normals'];normals=[(nm[j],-nm[j+2],nm[j+1])for j in range(0,len(nm),3)];m.normals_split_custom_set_from_vertices(normals)
 for p in m.polygons:p.use_smooth=True
 m.materials.append(sil);pose_meshes.append(m)
crowd_scene,crowd_hosts=scene_copy(s,'REV08 II / Terrace + Actual Website Crowd','TERRACE WEB CROWD');actors=json.loads((O/'evidence/rev05b-authoring.json').read_text())['actors'];placed=[]
for r in actors:
 if not all(n in old.objects for n in r['objects']):continue
 originals=[bpy.data.objects[n]for n in r['objects']];height=max((o.matrix_world@v.co).z for o in originals for v in o.data.vertices)-7.2
 for o in originals:crowd_hosts.objects.unlink(o)
 # Deterministic family mix, exactly shared source poses; never width-fitting.
 i=len(placed);vi=0 if i%5<2 else 1 if i%5==2 else 2 if i%5==3 else 3
 o=bpy.data.objects.new('WEB CROWD / '+r['label'],pose_meshes[vi]);crowd_hosts.objects.link(o);o.location=r['foot'];o.rotation_euler.z=r['yawRadians']+math.pi;o.scale=(height,)*3;o['sourceActor']=r['label'];o['poseVariant']=vi;o['nativeUniformScaleOnly']=True
 placed.append({'actor':r['label'],'object':o.name,'poseVariant':vi,'family':rows[vi]['family'],'clip':rows[vi]['clip'],'time':rows[vi]['time'],'foot':r['foot'],'yaw':r['yawRadians'],'uniformHeight':height,'sourceFootprint':r['footprint']})
# Import exact website prop meshes into a private source-audit scene, no reconstructions.
audit=bpy.data.scenes.new('REV08 / Exact Website Source Audit');audit['variant']='SOURCE AUDIT';audit.world=old.world;source_col=bpy.data.collections.new('WEB EXACT / imported prop source');audit.collection.children.link(source_col)
bpy.context.window.scene=audit;imports=[]
for file in ['aftermovie-stage.glb','festival-stall.glb']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(O/'source/website'/file));objs=[o for o in bpy.data.objects if o not in before]
 for o in objs:
  for c in list(o.users_collection):c.objects.unlink(o)
  source_col.objects.link(o);o['websiteOriginalName']=o.name;o['websiteSourceGLB']=file;o.name='WEB SOURCE / '+file+' / '+o.name
 imports.extend(objs)
propmeta=[]
for o in imports:
 if o.type!='MESH':continue
 p=[o.matrix_world@v.co for v in o.data.vertices];propmeta.append({'object':o.name,'sourceName':o['websiteOriginalName'],'sourceGLB':o['websiteSourceGLB'],'matrix':[list(v)for v in o.matrix_world],'bounds':[[min(v[i]for v in p),max(v[i]for v in p)]for i in range(3)],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':[m.name for m in o.data.materials]})
def prop_scene(name,variant,plan):
 sc,co=scene_copy(crowd_scene,name,variant);matches=[]
 for group,delta in plan:
  selected=[o for o in imports if o.type=='MESH'and (o['websiteOriginalName'] in group)]
  assert len(selected)==len(group),(group,len(selected))
  for src in selected:
   o=src.copy();o.name=variant+' / '+src['websiteOriginalName'];co.objects.link(o);o.location=src.location+Vector(delta);o.rotation_euler=src.rotation_euler;o.scale=src.scale;o.update_tag(refresh={'OBJECT'});o['exactWebsiteSourceObject']=src.name;matches.append({'source':src.name,'copy':o.name,'translationOnly':delta,'matrix':[list(v)for v in o.matrix_basis]})
 return sc,matches
table=['TABLE_top','TABLE_cloth_front','TABLE_cloth_left','TABLE_cloth_right'];case=['PROP_roadcase_0','PROP_roadcase_trim_0']
# Native-size table centered near rear media/service perimeter, no protected counters replaced.
pA,a=prop_scene('REV08 III-A / ARCHIVED Table + Active Roadcase Proposal','TERRACE PROPS A',[(table,(9.2,48.3,7.24)),(case,(23.3,44.1,5.89))])
pB,b=prop_scene('REV08 III-B / ARCHIVED Table + Active Roadcase Proposal','TERRACE PROPS B',[(table,(-9.2,48.3,7.24)),(case,(-3.1,44.1,5.89))])
# Audit display includes unaltered source meshes at native placement plus two 1.8m silhouettes.
for i in[0,2]:
 o=bpy.data.objects.new('SOURCE POSE / '+str(i),pose_meshes[i]);source_col.objects.link(o);o.location=(-2+i*2,8,0);o.scale=(1.8,)*3
for sc in[s,crowd_scene,pA,pB]:
 sc['supportOffLocked']=True;sc['sourceArtLocked']=True;sc['websiteUnmodified']=True;sc['rooftopFloorMoved']=False;sc['noAudienceCeiling']=True
sys.path.insert(0,str(O/'source'));from terrace_cameras import add
for sc in[before_scene,s,crowd_scene,pA,pB]:add(sc)
bpy.context.window.scene=crowd_scene;crowd_scene.camera=bpy.data.objects['TERRACE CAMERA / 02-screen-wide'];crowd_scene.frame_set(1);bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all();target=O/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend';bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
proof={'status':'AUTHORED_PENDING_VALIDATION','baselineSHA256':cfg['sha256'],'masterSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'newConstruction':new,'parts':parts,'actors':placed,'originalPropMetadata':propmeta,'propPlanA':a,'propPlanB':b,'fourSourcePoses':[{k:v for k,v in r.items()if k not in['positions','normals','indices']}for r in rows],'noNamedRackAssetFound':True,'tableNotSteelTop':'Actual source is timber top and cloth, within aluminium-frame stall; do not relabel as bare steel table.','crowdLicence':'Existing project source reused on user instruction; upstream author/license not documented in GLB or checked project sources; no blanket CC0/redistribution assertion.'}
(O/'evidence/authoring.json').write_text(json.dumps(proof,indent=2));print('REV08_AUTHORED',len(new),len(parts),len(placed),target.stat().st_size,flush=True)
