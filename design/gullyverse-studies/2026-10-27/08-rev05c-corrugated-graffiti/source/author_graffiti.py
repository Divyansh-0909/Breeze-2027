"""Authorized private Rev05C art derivative. Only3closed-shutter assemblies and local paint.
No website, route, crowd, counter, original-light or world modifications.
"""
import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from art_cameras import ARTISTS,add_cameras
BASE=O/'source/baseline/Rev05C-Support-Off.blend'
assert Path(bpy.data.filepath)==BASE
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='e68a1874b7c5412c5389937b37f8ea3a0aab32390ef583b5547e11cc3982690a'
original_objects=set(bpy.data.objects);modified_mesh=[];painted=[];profiles=[]
def node(t,kind,name):
 n=t.nodes.new(kind);n.label=name;n.name=name;return n
def mathnode(t,operation,a,b=None):
 n=node(t,'ShaderNodeMath',operation);n.operation=operation
 for index,value in enumerate([a,b]):
  if value is None:continue
  if hasattr(value,'node'):t.links.new(value,n.inputs[index])
  else:n.inputs[index].default_value=value
 return n.outputs[0]
def source_socket(t,n,name):
 s=n.inputs[name]
 if s.is_linked:return s.links[0].from_socket
 return list(s.default_value)if hasattr(s.default_value,'__len__')else s.default_value
def mix(t,a,b,factor):
 n=node(t,'ShaderNodeMixRGB','World aligned paint mixture');n.blend_type='MIX'
 for index,value in [(0,factor),(1,a),(2,b)]:
  if hasattr(value,'node'):t.links.new(value,n.inputs[index])
  else:n.inputs[index].default_value=value
 return n.outputs[0]
def xyz(t,vec):
 n=node(t,'ShaderNodeSeparateXYZ','World metres');t.links.new(vec,n.inputs[0]);return n.outputs
def projection(t,axes,centers,dimensions,signs=(1,1),uvrect=(0,0,1,1)):
 g=node(t,'ShaderNodeNewGeometry','World-space metre projection');p=xyz(t,g.outputs['Position']);com=node(t,'ShaderNodeCombineXYZ','Continuous paint coordinates')
 for i,(axis,center,dim,sign)in enumerate(zip(axes,centers,dimensions,signs)):
  q=mathnode(t,'ADD',mathnode(t,'MULTIPLY',mathnode(t,'SUBTRACT',p[axis],center),sign/dim),.5)
  q=mathnode(t,'ADD',mathnode(t,'MULTIPLY',q,uvrect[i+2]-uvrect[i]),uvrect[i]);t.links.new(q,com.inputs[i])
 return com.outputs[0],g
def apply_image_paint(mat,image,axes,centers,dimensions,signs,normal_axis,normal_sign,uvrect=(0,0,1,1),atlas=False,wear=False):
 t=mat.node_tree;bs=next(n for n in t.nodes if n.type=='BSDF_PRINCIPLED');uv,g=projection(t,axes,centers,dimensions,signs,uvrect)
 tex=node(t,'ShaderNodeTexImage','Exact source paint / shared image');tex.image=image;tex.extension='CLIP';tex.interpolation='Linear';t.links.new(uv,tex.inputs['Vector'])
 n=xyz(t,g.outputs['Normal']);front=mathnode(t,'GREATER_THAN',mathnode(t,'MULTIPLY',n[normal_axis],normal_sign),.001)
 alpha=mathnode(t,'MULTIPLY',tex.outputs['Alpha'],front)
 # Atlas subregions need an independent0..1 placement rectangle; suppress all other quadrants.
 if atlas:
  loc,_=projection(t,axes,centers,dimensions,signs);c=xyz(t,loc)
  for axis in [0,1]:
   alpha=mathnode(t,'MULTIPLY',alpha,mathnode(t,'GREATER_THAN',c[axis],0))
   alpha=mathnode(t,'MULTIPLY',alpha,mathnode(t,'LESS_THAN',c[axis],1))
 if wear:
  noise=node(t,'ShaderNodeTexNoise','Fine paint wear only');noise.inputs['Scale'].default_value=95;noise.inputs['Detail'].default_value=2;t.links.new(g.outputs['Position'],noise.inputs['Vector'])
  alpha=mathnode(t,'MULTIPLY',alpha,mathnode(t,'ADD',.90,mathnode(t,'MULTIPLY',noise.outputs['Fac'],.10)))
 base=source_socket(t,bs,'Base Color');t.links.new(mix(t,base,tex.outputs['Color'],alpha),bs.inputs['Base Color'])
 rough=source_socket(t,bs,'Roughness');t.links.new(mix(t,(rough,rough,rough,1)if isinstance(rough,(int,float))else rough,(.82,.82,.82,1),alpha),bs.inputs['Roughness'])
 metallic=source_socket(t,bs,'Metallic')
 if isinstance(metallic,(int,float)):t.links.new(mathnode(t,'MULTIPLY',metallic,mathnode(t,'SUBTRACT',1,alpha)),bs.inputs['Metallic'])
 else:t.links.new(mathnode(t,'MULTIPLY',metallic,mathnode(t,'SUBTRACT',1,alpha)),bs.inputs['Metallic'])
 return tex
def metal_material(name):
 m=bpy.data.materials.new(name);m.use_nodes=True;t=m.node_tree;bs=t.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.20,.235,.22,1);bs.inputs['Metallic'].default_value=.32;bs.inputs['Roughness'].default_value=.70;bs.inputs['Coat Weight'].default_value=0;bs.inputs['Emission Strength'].default_value=0
 g=node(t,'ShaderNodeNewGeometry','Actual metal surface');noise=node(t,'ShaderNodeTexNoise','Submillimetre enamel grain');noise.inputs['Scale'].default_value=140;noise.inputs['Detail'].default_value=2;t.links.new(g.outputs['Position'],noise.inputs['Vector'])
 bump=node(t,'ShaderNodeBump','Fine enamel pitting');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0006;t.links.new(noise.outputs['Fac'],bump.inputs['Height']);t.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 rough=mathnode(t,'ADD',.60,mathnode(t,'MULTIPLY',noise.outputs['Fac'],.20));t.links.new(rough,bs.inputs['Roughness'])
 t.links.new(mix(t,(.13,.155,.14,1),(.24,.27,.245,1),noise.outputs['Fac']),bs.inputs['Base Color'])
 return m
def replace_mesh(obj,world,faces):
 oldmat=[s.material for s in obj.material_slots];inv=obj.matrix_world.inverted();mesh=bpy.data.meshes.new(obj.name+' / true rolled steel profile');mesh.from_pydata([inv@Vector(p)for p in world],[],faces);mesh.update()
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4]);bm.to_mesh(mesh);bm.free();mesh.update()
 for m in oldmat:mesh.materials.append(m)
 obj.data=mesh
 uv=mesh.uv_layers.new(name='Local_metal_tangent_UV')
 for poly in mesh.polygons:
  pp=[obj.matrix_world@mesh.vertices[v].co for v in poly.vertices];extent=[max(p[i]for p in pp)-min(p[i]for p in pp)for i in range(3)];ax=sorted(range(3),key=lambda i:extent[i],reverse=True)[:2]
  for li in poly.loop_indices:
   p=obj.matrix_world@mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p[ax[0]],p[ax[1]])
  poly.use_smooth=len(poly.vertices)==4
 mesh.calc_loop_triangles();mesh.calc_tangents(uvmap=uv.name);modified_mesh.append(obj.name)
 return mesh
def material_override(obj,m):
 assert len(obj.material_slots)==1,obj.name
 obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=m;painted.append(obj.name)
def slat_mesh(obj,side,cy):
 z=obj.matrix_world.translation.z
 offsets=[-.0745,-.071,-.066,-.059,-.052,-.033,-.012,.012,.033,.052,.059,.066,.071,.0745]
 xs=[3.7075,3.705,3.699,3.691,3.685,3.680,3.6775,3.6775,3.680,3.685,3.691,3.699,3.705,3.7075]
 cross=[(side*x,z+dz)for x,dz in zip(xs,offsets)]+[(side*(x+.003),z+dz)for x,dz in reversed(list(zip(xs,offsets)))];n=len(cross)
 world=[(x,y,zz)for y in [cy-3.425,cy+3.425]for x,zz in cross];faces=[]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 faces.extend([tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]);mesh=replace_mesh(obj,world,faces)
 profiles.append({'object':obj.name,'profileSamples':len(offsets),'pitchM':.15,'frontToValleyDepthM':.03,'metalThicknessM':.003,'interSlatGapM':.001,'triangles':len(mesh.loop_triangles),'centerZ':z})
images={}
for a in ARTISTS:
 image=bpy.data.images.load(str(O/'source/derived'/f"{a['key']}-paint-rgba.png"));image.name='ART / original '+a['label']+' / RGBA';image.colorspace_settings.name='sRGB';image.alpha_mode='STRAIGHT';image.pack();images[a['key']]=image
atlas=bpy.data.images.load(str(O/'source/generated/supporting-wall-atlas.png'));atlas.name='ART / generated supporting pieces / shared atlas';atlas.colorspace_settings.name='sRGB';atlas.alpha_mode='STRAIGHT';atlas.pack()
shutters=[]
for a in ARTISTS:
 side,cy=a['side'],a['cy'];host=bpy.data.objects[a['host']];m=metal_material('ART / '+a['label']+' / painted rolled steel')
 apply_image_paint(m,images[a['key']],(1,2),(cy,a['z']),(6.3,2.1),(-side,1),0,-side)
 # Recess the original backing locally so real slat valleys are no longer occluded by its flat front.
 world=[]
 for v in host.data.vertices:
  p=host.matrix_world@v.co
  if side*p.x<3.8:p.x=side*3.8
  world.append(tuple(p))
 replace_mesh(host,world,[tuple(p.vertices)for p in host.data.polygons]);material_override(host,m)
 slats=sorted([o for o in bpy.data.objects if o.name.startswith('Shutter slat')and o.location.x*side>0 and abs(o.location.y-cy)<.01],key=lambda o:o.location.z)
 assert len(slats)==18
 for slat in slats:slat_mesh(slat,side,cy);material_override(slat,m)
 shutters.append({**a,'host':host.name,'slats':[o.name for o in slats],'source':'source/originals/'+a['key']+'.jpeg','rgba':'source/derived/'+a['key']+'-paint-rgba.png','artworkWidthM':6.3,'artworkHeightM':2.1,'material':m.name,'normalMapsUsedForGrooves':False,'addedHoveringPlanes':0})
# Candidate review rejected upper-storey blank bands as too high for pedestrian impact.
# Four PROPOSED placements:2 existing narrow wall/piers +2 transition returns, no new panels.
walls=[
 {'key':'lane-pier-left','hosts':['Building / -1 / 0','Shop pier.001'],'axes':(2,1),'centers':(7.5,-21.15),'dimensions':(1.56,.52),'signs':(1,1),'normalAxis':0,'normalSign':1,'uvrect':(0,.5,.5,1),'rotation':'90deg vertical composition; original motif aspect preserved'},
 {'key':'lane-pier-right','hosts':['Building / 1 / 1','Shop pier.011'],'axes':(2,1),'centers':(7.5,-12.15),'dimensions':(1.56,.52),'signs':(1,-1),'normalAxis':0,'normalSign':-1,'uvrect':(.5,.5,1,1),'rotation':'90deg vertical composition; original motif aspect preserved'},
 {'key':'return-left','hosts':['Entry parapet return'],'axes':(0,2),'centers':(-11.5,7.75),'dimensions':(2.6,2.6/3),'signs':(1,1),'normalAxis':1,'normalSign':1,'uvrect':(0,0,.5,.5),'rotation':'landscape'},
 {'key':'return-right','hosts':['Entry parapet return.001'],'axes':(0,2),'centers':(11.5,7.75),'dimensions':(2.6,2.6/3),'signs':(1,1),'normalAxis':1,'normalSign':1,'uvrect':(.5,0,1,.5),'rotation':'landscape'}]
for w in walls:
 for name in w['hosts']:
  ob=bpy.data.objects[name];old=ob.material_slots[0].material;m=old.copy();m.name='ART / '+w['key']+' / '+name
  apply_image_paint(m,atlas,w['axes'],w['centers'],w['dimensions'],w['signs'],w['normalAxis'],w['normalSign'],w['uvrect'],atlas=True,wear=True);material_override(ob,m)
addedcams=add_cameras()
for scene in bpy.data.scenes:
 assert len([o for o in scene.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')and o.data.energy==0])==5
 scene['rev05c_art_status']='THREE_EXACT_SOURCE_SHUTTERS_AND_FOUR_PROPOSED_GENERATED_WALLS_USER_REVIEW_PENDING'
 bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version=0
master=O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend';bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
result={'status':'AUTHORED_FOR_REVIEW_NOT_VISUALLY_APPROVED','baselineSHA256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'masterBytes':master.stat().st_size,'shutters':shutters,'profiles':profiles,'modifiedMeshObjects':sorted(modified_mesh),'paintMaterialOverrideObjects':sorted(painted),'newCameras':addedcams,'walls':walls,'wallPlacementStatus':'PROPOSED_NOT_LOCKED','newImages':[i.name for i in images.values()]+[atlas.name],'newLights':0,'optionalSupportsRemainOff':True,'originalImageRGBSourcePreserved':True,'websiteWrites':False}
(O/'evidence/art-authoring.json').write_text(json.dumps(result,indent=2)+'\n');print('ART_AUTHORED',len(modified_mesh),'controlled shutter meshes',len(painted),'painted existing objects',len(addedcams),'review cameras',flush=True)
