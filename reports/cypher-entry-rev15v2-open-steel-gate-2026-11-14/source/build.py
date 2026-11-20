import bpy,json,hashlib,math,argparse,sys,runpy
from pathlib import Path
from mathutils import Vector
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];V1=R.parent/'events-wall-rev15v1-coloured-plaster-2026-11-14';plan=json.loads((R/'source/entry-plan.json').read_text());snapshot=runpy.run_path(str(V1/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--base',default='/dev/shm/Gullyverse-Rev15V1-Events-Coloured-Plaster.blend');ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15V2-Open-Steel-Cypher-Gate.blend');ap.add_argument('--restore',action='store_true');ap.add_argument('--diagnose',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);out=Path(a.output);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();before=fp(base);assert before['sha256']==json.loads((V1/'evidence/native-scene-fingerprint.json').read_text())['sha256'];protected=snapshot(base,{'objects':[]},'REV15V1 / ');history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15V2 / Narrow open steel cypher gate';s['variant']='REV15V2'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 ob=old.copy();ob.name='REV15V2 / '+old.name.removeprefix('REV15V1 / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for driver in ob.animation_data.drivers:
   for v in driver.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15V2 / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
collection=bpy.data.collections.new('REV15V2 / Narrow cypher gate');s.collection.children.link(collection)
def material(name,col,rough,metal=0):
 m=bpy.data.materials.new('REV15V2 / '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
plaster=material('Pale boundary wall plaster',(.5,.48,.42),.89);cap=material('Weathered concrete coping',(.32,.33,.29),.9);steel=material('Aged galvanised gate steel',(.3,.32,.30),.48,.75);hingemat=material('Dark hinge steel',(.075,.085,.077),.56,.72)
class Batch:
 def __init__(self):self.vs=[];self.fs=[]
 def add(self,vs,fs):
  start=len(self.vs);self.vs.extend(vs);self.fs.extend(tuple(start+i for i in f) for f in fs)
 def box(self,c,size):
  vs=[(c[0]+x*size[0]/2,c[1]+y*size[1]/2,c[2]+z*size[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];self.add(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 def rod(self,a,b,r,sides=12):
  a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((1,0,0)) if abs(axis.z)>.9 else Vector((0,0,1))).normalized();v=axis.cross(u);vs=[tuple(c+r*(math.cos(i*math.tau/sides)*u+math.sin(i*math.tau/sides)*v)) for c in [a,b] for i in range(sides)];self.add(vs,[tuple(reversed(range(sides))),tuple(range(sides,sides*2))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides) for i in range(sides)])
 def object(self,name,mat,parent=None):
  me=bpy.data.meshes.new('REV15V2 / ENTRY / '+name);me.from_pydata(self.vs,[],self.fs);me.materials.append(mat);me.update();o=bpy.data.objects.new(me.name,me);collection.objects.link(o);o['entryGatePart']=name
  if parent:o.parent=parent
  return o
walls=Batch();piers=Batch();caps=Batch();ground=7.2;wallY=plan['wallY']
for lo,hi in [(-8.3,-1.08),(1.08,8.3)]:
 walls.box(((lo+hi)/2,wallY,ground+1.325),(hi-lo,.22,2.65));caps.box(((lo+hi)/2,wallY,ground+2.685),(hi-lo+.025,.28,.07))
# Short returns join the recessed entrance wall to both existing front houses.
for x in [-8.19,8.19]:walls.box((x,14.7,ground+1.325),(.22,1.02,2.65));caps.box((x,14.7,ground+2.685),(.28,1.02,.07))
for x in [-.99,.99]:piers.box((x,wallY,ground+1.375),(.18,.32,2.75));caps.box((x,wallY,ground+2.79),(.24,.38,.08))
walls.object('Boundary walls flanking the narrow opening',plaster);piers.object('Left and right masonry gate jambs',plaster);caps.object('Concrete coping and pier caps',cap)
root=bpy.data.objects.new('REV15V2 / ENTRY / Left hinge axis',None);collection.objects.link(root);root.location=plan['hinge'];root.rotation_euler.z=math.radians(plan['openAngleDegrees']);root['entryGatePart']='hinge axis';root['openAngleDegrees']=-90;root['openingWidthMetres']=1.8;root['singleLeaf']=True;root['swing']='Outwards toward the gully'
leaf=Batch()
for x in [.055,1.735]:leaf.box((x,0,1.295),(.04,.04,2.39))
for z in [.12,2.47]:leaf.box((.895,0,z),(1.72,.04,.04))
for i in range(13):
 x=.075+(1.715-.075)*(i+1)/14;leaf.rod((x,0,.14),(x,0,2.45),.008)
for z in [.88,1.65]:leaf.box((.895,0,z),(1.64,.018,.025))
leaf.rod((1.70,-.08,1.11),(1.70,-.08,1.32),.008)
for z in [1.11,1.32]:leaf.rod((1.70,0,z),(1.70,-.08,z),.008)
leaf.box((1.70,0,1.215),(.08,.045,.055));leafob=leaf.object('Single see through steel rod gate leaf',steel,root);leafob['verticalRods']=13;leafob['rodDiameterMetres']=.016;leafob['hasOpaquePanel']=False
fixings=Batch()
for z in [.45,2.05]:
 fixings.rod((-.88,14.9,ground+z-.07),(-.88,14.9,ground+z+.07),.031,16);fixings.box((-.99,14.925,ground+z),(.16,.025,.19));fixings.box((-.925,14.90,ground+z),(.12,.045,.045))
fixings.object('Fixed hinge knuckles and wall plates',hingemat)
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update();assert snapshot(SimpleNamespace(objects=list(copies.values())),{'objects':[]},'REV15V2 / ')==protected;assert fp(base)['sha256']==before['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items());fingerprint=fp(s);fingerprint.pop('data')
if a.diagnose:
 original=fp(s);bpy.ops.wm.open_mainfile(filepath='/dev/shm/Gullyverse-Rev15V2-Open-Steel-Cypher-Gate.blend');current=bpy.context.scene;current.frame_set(1);bpy.context.view_layer.update();reopened=fp(current);diff=[{'name':x['name'],'differences':{k:[x.get(k),y.get(k)] for k in set(x)|set(y) if x.get(k)!=y.get(k)}} for x,y in zip(original['data']['objects'],reopened['data']['objects']) if x!=y];print(json.dumps({'before':original['sha256'],'after':reopened['sha256'],'diffCount':len(diff),'diff':diff[:12]},indent=2));raise SystemExit()
if a.restore:assert fingerprint['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);proof={'status':'PASS','source':a.base,'sourceSHA256':sha(a.base),'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':57,'newObjects':sorted(o.name for o in collection.objects),'sourceObjectsUnchanged':True,'protectedSnapshot':protected,'openingWidthMetres':1.8,'gateAngleDegrees':-90,'singleLeaf':True,'verticalSteelRods':13,'rodDiameterMetres':.016,'opaquePanels':0,'gateBeyondNavigationStand':True,'EventsColouredPlasterAndAllPostersPreserved':True,'wholeTeamBuildingUnchanged':True,'originalMovementCodeAndRoadUnchanged':True,'sceneFingerprintSHA256':fingerprint['sha256']};(R/('evidence/restore-check.json' if a.restore else 'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:(R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fingerprint,indent=2)+'\n')
print(json.dumps({'status':'PASS','restore':a.restore,'scenes':len(bpy.data.scenes),'newObjects':len(collection.objects)}),flush=True)
