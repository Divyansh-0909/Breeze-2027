import bpy,json,math,sys,statistics,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
P=O/'inputs/Rev10-original.blend';sig=snapshot(P);s=next(s for s in bpy.data.scenes if s.get('variant')=='PHOTO A');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update()
def bbox(o):
 p=[o.matrix_world@v.co for v in o.data.vertices] if o.type=='MESH' else [o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p),max(v[i] for v in p)] for i in range(3)]
data=json.loads((O/'baseline/evidence/rev05b-authoring.json').read_text());actors=[]
for r in data['actors']:
 if not all(n in s.objects for n in r['objects']):continue
 bb=[bbox(s.objects[n]) for n in r['objects']];lo=[min(b[i][0]for b in bb)for i in range(3)];hi=[max(b[i][1]for b in bb)for i in range(3)];actors.append({**r,'bounds':[lo,hi],'heightM':hi[2]-lo[2]})
h=[r['heightM']for r in actors]
interesting=[o for o in s.objects if any(k in o.name.lower() for k in ['aftermovie','hero raster','rooftop slab','navigation','board','team authorized','events clearly'])]
measures=[{'object':o.name,'type':o.type,'bbox':bbox(o),'dimensions':list(o.dimensions)}for o in interesting if o.type in ['MESH','FONT']]
for r in measures:
 b=r['bbox'];r['center']=[sum(x)/2 for x in b];r['distanceFromWalkEndpointM']=math.dist(r['center'],[0,36.5,8.92])
arch=json.loads((O/'baseline/evidence/authoring.json').read_text());houses=arch['studies'][0]['houses'];parts=arch['studies'][0]['parts']
measureparts=[p for p in parts if any(k in p['name']for k in ['door','parapet','gallery','supporting','roof access']) and 'dimensions'in p]
result={'status':'READ_ONLY_BEFORE_AUTHORING','units':'metres / Z up','masterSHA256':hashlib.sha256(P.read_bytes()).hexdigest(),'sceneCount':len(bpy.data.scenes),'actorCount':len(actors),'actorHeightM':{'min':min(h),'median':statistics.median(h),'max':max(h)},'actors':actors,'protectedObjects':measures,'houses':houses,'architecturalParts':measureparts,'guidanceNotMeasured':{'avatarM':1.7,'doorClearHeightM':2.1,'floorToFloorM':[2.8,3.3],'parapetHeightM':[1,1.2]},'sceneNames':[s.name for s in bpy.data.scenes]}
(O/'evidence/before-survey.json').write_text(json.dumps(result,indent=2));(O/'evidence/source-signatures.json').write_text(json.dumps({'objects':sig[0],'environment':sig[1],'materials':sig[2],'worlds':sig[3],'images':sig[4],'memberships':{s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes}},indent=2))
print('ACTORS',len(actors),result['actorHeightM']);print('PROTECTED',json.dumps(measures,indent=1));print('SCENES',result['sceneNames'])
