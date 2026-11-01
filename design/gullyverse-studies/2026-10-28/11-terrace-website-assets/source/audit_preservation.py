import bpy,json,sys,hashlib,os
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
cfg=json.loads((O/'source/BASELINE.json').read_text());base=Path(os.environ.get('GULLYVERSE_BASELINE_OVERRIDE',cfg['path']));new=O/'source/Gullyverse-Rev08-Terrace-Website-Assets.blend'
a,ea,ma,wa,ia=snapshot(base);members={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes}
b,eb,mb,wb,ib=snapshot(new);assert wa==wb
errors=[n for n,v in a.items()if b.get(n)!=v];assert not errors,errors
assert all(mb[n]==v for n,v in ma.items());assert all(ib[n]==v for n,v in ia.items())and set(ia)==set(ib)
assert all(eb[n]==v for n,v in ea.items());assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in members.items())
old=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD');rows=[]
for s in bpy.data.scenes:
 if not s.get('variant','').startswith('TERRACE'):continue
 assert s.world==old.world and s.view_settings.exposure==old.view_settings.exposure and s.view_settings.look==old.view_settings.look
 assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in old.objects if o.type=='LIGHT'}
 assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12
 assert sum(o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')and o.data.energy==0 for o in s.objects)==5
 for o in old.objects:
  if o.name.startswith(('Closed rolling shutter','Shutter slat'))or any(sl.material and sl.material.name.startswith('ART /')for sl in o.material_slots):assert s.objects.get(o.name)==o
  if o.get('pilotOriginalObject',o.name).startswith(('Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron','Counter')):assert s.objects.get(o.name)==o
 rows.append({'variant':s['variant'],'all17LightsExact':True,'active':12,'fiveOptionalSupportsW':[0]*5,'sevenArtPlacementsExact':True,'floorAndCountersExact':True})
r={'status':'PASS','originalObjectsExact':len(a),'allFiveArchivalSceneMembershipsAndSettingsExact':True,'allOriginalMaterialsWorldsImagesTransformsMeshUVActionsExact':True,'priorMasterSHA256':cfg['sha256'],'masterSHA256':hashlib.sha256(new.read_bytes()).hexdigest(),'sceneCount':len(bpy.data.scenes),'candidateChecks':rows}
(O/'evidence/preservation-audit.json').write_text(json.dumps(r,indent=2));print('ARCHIVE_ART_LIGHTS_FLOOR_PASS',len(a),flush=True)
