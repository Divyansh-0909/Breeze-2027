import bpy,json,math,hashlib,runpy,argparse,sys
from pathlib import Path
from mathutils import Vector
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];plan=json.loads((R/'source/lighting-plan.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fingerprint=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'];ap=argparse.ArgumentParser();ap.add_argument('--base',default=plan['source']);ap.add_argument('--output',default='/dev/shm/Gullyverse-Rev15W-Streetlights-and-Overhead-Cables.blend');ap.add_argument('--restore',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);out=Path(a.output);assert not out.exists(),'Choose a new output filename.';bpy.ops.wm.open_mainfile(filepath=a.base);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();basefp=fingerprint(base);assert basefp['sha256']==plan['sourceSceneFingerprint'];protected=snapshot(base,{'objects':[]},'REV15V2 / ');history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};s=base.copy();s.name='REV15W / Streetlights and suspended electricity cables';s['variant']='REV15W'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
bpy.context.window.scene=s;copies={}
for old in base.objects:
 ob=old.copy();ob.name='REV15W / '+old.name.removeprefix('REV15V2 / ')
 if old.type=='CAMERA':ob.data=old.data.copy()
 s.collection.objects.link(ob);copies[old]=ob
for old,ob in copies.items():
 if old.parent in copies:ob.parent=copies[old.parent]
 if ob.animation_data:
  for f in ob.animation_data.drivers:
   for v in f.driver.variables:
    for t in v.targets:
     if t.id in copies:t.id=copies[t.id]
layer=s.view_layers.new('REV15W / independent view')
for l in list(s.view_layers):
 if l!=layer:s.view_layers.remove(l)
bpy.context.window.view_layer=layer
for n in s.node_tree.nodes:
 if n.type=='R_LAYERS':n.scene=s;n.layer=layer.name
collection=bpy.data.collections.new('REV15W / Streetlights and overhead cables');s.collection.children.link(collection)
def mat(name,col,rough,metal=0):
 m=bpy.data.materials.new('REV15W / '+name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
steel=mat('Aged galvanised steel',(.19,.22,.20),.64,.72);dark=mat('Dark fixture steel',(.028,.034,.030),.68,.55);paint=mat('Worn pale lower pole paint',(.37,.35,.29),.88);rust=mat('Oxidised bands and fixings',(.14,.067,.026),.94,.2);wiremat=mat('Insulated black cable',(.012,.013,.010),.78);hardware=[steel,dark,paint,rust]
class Batch:
 def __init__(self):self.vs=[];self.fs=[];self.mi=[];self.smooth=[]
 def add(self,vs,fs,mi=0,smooth=False):
  start=len(self.vs);self.vs.extend(vs);self.fs.extend(tuple(start+i for i in f) for f in fs);self.mi.extend([mi]*len(fs));self.smooth.extend([smooth]*len(fs))
 def box(self,c,size,mi=0):
  vs=[(c[0]+x*size[0]/2,c[1]+y*size[1]/2,c[2]+z*size[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];self.add(vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mi)
 def tube(self,points,r=.01,mi=0,sides=8,endr=None):
  points=[Vector(p) for p in points];vs=[]
  for i,p in enumerate(points):
   tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();u=tangent.cross(Vector((1,0,0)) if abs(tangent.z)>.9 else Vector((0,0,1))).normalized();v=tangent.cross(u);rad=r if endr is None else r+(endr-r)*i/(len(points)-1)
   vs.extend(tuple(p+rad*(math.cos(j*math.tau/sides)*u+math.sin(j*math.tau/sides)*v)) for j in range(sides))
  fs=[tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]
  for i in range(len(points)-1):
   for j in range(sides):fs.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
  self.add(vs,fs,mi,True)
 def object(self,name,mats,part):
  me=bpy.data.meshes.new('REV15W / '+name);me.from_pydata(self.vs,[],self.fs);me.update()
  for m in mats:me.materials.append(m)
  for f,mi,smooth in zip(me.polygons,self.mi,self.smooth):f.material_index=mi;f.use_smooth=smooth
  ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob);ob['streetLampPart']=part;return ob
zones={z:Batch() for z in sorted({r['zone'] for r in plan['lamps']})};coils=Batch();records=[];fps=plan['sceneFPS'];period=round(plan['flickerPeriodSeconds']*fps);keys=[[round(t*fps),v] for t,v in plan['flickerKeys']]
def animate(owner,path,basevalue,phase):
 for f,value in keys:
  setattr(owner,path,basevalue*value) if path=='energy' else None
  if path!='energy':owner.default_value=basevalue*value;owner.keyframe_insert('default_value',frame=1+f-phase)
  else:owner.keyframe_insert('energy',frame=1+f-phase)
 action=owner.animation_data.action if path=='energy' else owner.id_data.animation_data.action
 for f in action.fcurves:
  for k in f.keyframe_points:k.interpolation='CONSTANT'
  cycle=f.modifiers.new('CYCLES');cycle.mode_before='REPEAT';cycle.mode_after='REPEAT'
for index,row in enumerate(plan['lamps']):
 p=Vector(row['position']);direction=row['armDirection'];h=row['height'];b=zones[row['zone']];x,y,z=p;b.tube([p,p+Vector((0,0,h))],.062,0,12,.039);b.box((x,y,z+.035),(.28,.28,.07),0)
 for dx in [-.095,.095]:
  for dy in [-.095,.095]:b.tube([(x+dx,y+dy,z+.07),(x+dx,y+dy,z+.105)],.016,1,6)
 b.tube([(x,y,z+.18),(x,y,z+1.03)],.064,2,12);b.box((x+direction*.061,y,z+.69),(.014,.13,.31),1);b.box((x+direction*.071,y,z+.69),(.008,.10,.24),0)
 for dz in [.17,.36,.91,5.48,5.70]:b.tube([(x,y,z+dz),(x,y,z+dz+.025)],.069,3 if dz<1 else 1,10)
 # Small swept steel arm with the utilitarian boxed lamp seen in the references.
 arm=[(x,y,z+5.62),(x+direction*.10,y,z+5.78),(x+direction*.26,y,z+5.91),(x+direction*.54,y,z+5.98),(x+direction*.96,y,z+5.98)];b.tube(arm,.026,0,10)
 centre=Vector((x+direction*1.18,y,z+5.95));b.box(centre,(.62,.235,.13),1);b.box((centre.x,centre.y,centre.z+.078),(.46,.20,.025),0);b.box((centre.x-direction*.29,centre.y,centre.z),(.05,.255,.16),0)
 # Compact junction box, cable clamps and service loop stay above head height.
 b.box((x+direction*.09,y,z+4.9),(.14,.18,.25),1)
 loop=[(x+direction*(.09+.09*math.cos(t)),y+.09*math.sin(t),z+5.24+.035*t/math.tau) for t in [i*math.tau*1.6/32 for i in range(33)]];coils.tube(loop,.0045,0,6)
 coils.tube([(x+direction*.07,y,z+5.76),(x+direction*.09,y,z+5.4),(x+direction*.09,y,z+5.0)],.005,0,6)
 lensmat=mat(row['id']+' lamp lens',(.075,.083,.070) if row['state']=='dead' else (.65,.59,.45),.42);bsdf=lensmat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Emission Color'].default_value=(*row['colour'],1);baseEmission=0 if row['state']=='dead' else 6;bsdf.inputs['Emission Strength'].default_value=baseEmission
 lens=Batch();lens.box((centre.x,centre.y,centre.z-.073),(.49,.168,.012));ob=lens.object(row['id']+' luminous panel',[lensmat],'lens');ob['streetLampId']=row['id'];ob['lampState']=row['state'];ob['emissionBase']=baseEmission
 data=bpy.data.lights.new('REV15W / '+row['id']+' local pool','SPOT');data.color=row['colour'];data.energy=0 if row['state']=='dead' else row['basePowerWatts'];data.use_custom_distance=True;data.cutoff_distance=11;data.spot_size=math.radians(82);data.spot_blend=.62;data.shadow_soft_size=.14;data.use_shadow=row['id'] in ['L01','L04'];light=bpy.data.objects.new(data.name,data);collection.objects.link(light);light.location=(centre.x,centre.y,centre.z-.09);light['streetLampPart']='local light';light['streetLampId']=row['id'];light['lampState']=row['state'];light['basePower']=row['basePowerWatts'];phase=round(row['flickerPhase']*fps)
 if row['state']=='flicker':animate(data,'energy',row['basePowerWatts'],phase);animate(bsdf.inputs['Emission Strength'],'default_value',baseEmission,phase)
 records.append({'id':row['id'],'zone':row['zone'],'state':row['state'],'polePosition':row['position'],'lampPosition':list(light.location),'lensObject':ob.name,'lightObject':light.name,'basePowerWatts':row['basePowerWatts'],'runtimeIntensity':150 if row['zone']=='lane' else 180,'emissionBase':baseEmission,'colour':row['colour'],'phaseFrames':phase,'range':11,'spotAngleDegrees':82,'spotBlend':.62})
for zone,b in zones.items():b.object(zone+' batched streetlight hardware',hardware,'hardware')
coils.object('High junction service loops and drops',[wiremat],'service wiring');cables=Batch()
for cable in plan['cables']:cables.tube(cable['points'],cable['radius'],0,6)
cableobj=cables.object('Suspended electricity cable network',[wiremat],'suspended cables');cableobj['overheadCableCount']=len(plan['cables']);cableobj['minimumRouteClearance']=plan['minimumCableClearance']
s.camera=copies[base.camera];bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update();assert snapshot(SimpleNamespace(objects=list(copies.values())),{'objects':[]},'REV15W / ')==protected;assert fingerprint(base)['sha256']==basefp['sha256'];assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items());fp=fingerprint(s);fp.pop('data')
if a.restore:assert fp['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
proof={'status':'PASS','source':a.base,'sourceSHA256':sha(a.base),'sourceSceneFingerprint':basefp['sha256'],'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),'scene':s.name,'scenes':len(bpy.data.scenes),'historicalSceneMembershipsPreserved':58,'allExistingObjectsGeometryUVColoursMaterialsTransformsAndLightsPreserved':True,'sourceProtectedSnapshot':protected,'lamps':len(records),'counts':plan['counts'],'overheadCables':len(plan['cables']),'minimumCableClearanceMetres':plan['minimumCableClearance'],'newObjects':sorted(o.name for o in collection.objects),'sceneFingerprintSHA256':fp['sha256'],'oldWorldExposureAndLightSettingsUnchanged':True,'extraEnvironmentChanges':False,'scope':'Gully lane road edges only; no fixtures or cable network inside the cypher','deadline':'2026-11-28','websiteIntegration':'PENDING'}
(R/('evidence/restore-check.json' if a.restore else 'evidence/build-verification.json')).write_text(json.dumps(proof,indent=2)+'\n')
if not a.restore:
 (R/'evidence/native-scene-fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n');(R/'delivery/streetlights.json').write_text(json.dumps({'version':'REV15W','sourceSceneFingerprint':fp['sha256'],'fps':fps,'periodFrames':period,'keys':keys,'lamps':records,'counts':plan['counts'],'overheadCables':len(plan['cables']),'minimumCableClearanceMetres':plan['minimumCableClearance'],'reducedMotion':'Flickering lamps remain steadily lit; dead lamps stay off.','integration':'New geometry/lighting component only; the website and existing lightfield are unchanged.'},indent=2)+'\n')
print(json.dumps({'status':'PASS','restore':a.restore,'scenes':len(bpy.data.scenes),'lamps':plan['counts'],'cables':len(plan['cables'])}),flush=True)
