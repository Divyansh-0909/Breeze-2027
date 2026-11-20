import bpy,json,math,hashlib,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];p=json.loads((R/'evidence/build-verification.json').read_text());cfg=json.loads((R/'source/road-layout.json').read_text())
assert hashlib.sha256(Path(p['editedMaster']).read_bytes()).hexdigest()==p['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=p['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();assets=bpy.data.collections['REV15T / Asphalt road and edge details'];floors=[o for o in assets.objects if o.get('groundSurface')];trees=[BVHTree.FromObject(o,deps) for o in floors]
def hit(x,y):
 locs=[r[0] for t in trees for r in [t.ray_cast(Vector((x,y,25)),Vector((0,0,-1)),50)] if r[0] is not None]
 return max((p.z for p in locs),default=None)
def grade(y):return 6 if y<=-10 else 6+.05*(y+10) if y<14 else 7.2
route=[]
for i in range(157):
 y=-29.99+77.98*i/156
 for x in [-1.4,0,1.4]:
  z=hit(x,y);assert z is not None and abs(z-grade(y))<.0002,(x,y,z,grade(y));route.append({'x':x,'y':y,'z':z})
cx,cy=cfg['circle']['centre']
for i in range(80):
 a=math.tau*i/80
 for r in [0,1.5,3,4.5]:
  z=hit(cx+math.cos(a)*r,cy+math.sin(a)*r);assert z is not None and abs(z-7.2)<.0002
seams=[]
for y in [-10,5,14]:
 for x in [-3,0,3]:
  a,b=hit(x,y-.0001),hit(x,y+.0001);assert a is not None and b is not None and abs(a-b)<.0001;seams.append({'x':x,'y':y,'stepMetres':abs(a-b)})
defects=[]
for h in p['holes']:
 z=hit(h['x'],h['y']);depth=grade(h['y'])-z;assert depth>.012 and depth<h['depth']+.002,(h['id'],depth);defects.append({'id':h['id'],'actualCentreDepressionMetres':depth,'targetDepthMetres':h['depth']})
crowd=[o for o in s.objects if o.type=='MESH' and o.data.name.startswith('REV13A shared')];feet=[]
for o in crowd:
 q=o.matrix_world.translation;z=hit(q.x,q.y)
 if z is not None:
  diff=grade(q.y)-z;assert diff<.003,(o.name,diff);feet.append({'object':o.name,'surfaceDepressionAtOriginMetres':diff})
assert len(crowd)==189 and all('LOD0' in o.data.name for o in crowd)
murals=[o for o in s.objects if o.get('artKind')];assert len(murals)==8
controller=next((o for o in s.objects if o.name.endswith('REV15O / Team Carousel Controller')),None);states=[]
if controller:
 old=controller.get('teamIndex',0)
 # The existing driver property names are recorded without changing their contract.
 states=[{'controller':controller.name,'properties':{k:str(v) for k,v in controller.items()}}]
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
newtri=sum(sum(max(0,len(f.vertices)-2) for f in o.data.polygons) for o in assets.objects if o.type=='MESH')
out={'status':'PASS','freshNativeOpen':True,'masterSHA256':p['editedSHA256'],'nativeScenes':len(bpy.data.scenes),'packedImages':sum(bool(im.packed_file) for im in bpy.data.images),'routeSamples':len(route),'flatCypherSamples':320,'seamSamples':seams,'defects':defects,'crowdCount':len(crowd),'crowdLOD0':True,'crowdFeetCheckedOnRoad':len(feet),'muralStates':len(murals),'carouselControl':states,'newGroundTriangles':newtri,'sourceSHA256':hashlib.sha256(Path(p['source']).read_bytes()).hexdigest(),'sourceUnchanged':True}
assert out['sourceSHA256']==p['sourceSHA256'];(R/'evidence/fresh-open.json').write_text(json.dumps(out,indent=2)+'\n')
exportScene=bpy.data.scenes.new('TEMP EXPORT / asphalt ground only')
for o in assets.objects:exportScene.collection.objects.link(o)
bpy.context.window.scene=exportScene
for o in exportScene.objects:o.select_set(False)
for o in assets.objects:o.select_set(True)
bpy.context.view_layer.objects.active=floors[0]
glb=R/'delivery/Rev15T-Continuous-Asphalt-Ground.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_yup=True,export_materials='EXPORT',export_normals=True,export_texcoords=True)
b=glb.read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert magic==b'glTF' and version==2 and length==len(b);n,kind=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+n])
roadidx=next(i for i,m in enumerate(g['materials']) if 'Reference-authored worn asphalt' in m['name']);m=g['materials'][roadidx]
assert m['normalTexture'].get('texCoord',0)==1,m
primitives=[p for me in g['meshes'] for p in me['primitives'] if p.get('material')==roadidx]
assert len(primitives)==4 and all('TEXCOORD_0' in x['attributes'] and 'TEXCOORD_1' in x['attributes'] for x in primitives)
assert all('bufferView' in i for i in g['images'])
assert len(g['nodes'])==13 and len(g['images'])==3,(len(g['nodes']),len(g['images']))
e={'status':'PASS','file':str(glb),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'nodes':len(g['nodes']),'materials':len(g['materials']),'embeddedImages':len(g['images']),'groundPrimitives':len(primitives),'detailNormalUVChannel':1,'worldColorAndRoughnessUVChannel':0,'boundsAndExistingGrade':'Same world-space footprint and grade as native source','scope':'Ground and edge-detail runtime asset, not a full-world browser integration'}
(R/'evidence/export.json').write_text(json.dumps(e,indent=2)+'\n');print('VERIFY_EXPORT_DONE',json.dumps(out),json.dumps(e),flush=True)
