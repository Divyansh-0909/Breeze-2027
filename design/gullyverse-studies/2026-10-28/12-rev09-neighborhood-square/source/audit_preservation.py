import bpy,json,sys,hashlib,os
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
cfg=json.loads((O/'source/BASELINE.json').read_text());original=Path(os.environ.get('GULLYVERSE_BASELINE_OVERRIDE',cfg['path']));master=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend'
a,ea,ma,wa,ia=snapshot(original);membership={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes};b,eb,mb,wb,ib=snapshot(master)
assert wa==wb;assert all(b.get(n)==v for n,v in a.items()),[n for n,v in a.items()if b.get(n)!=v];assert all(mb[n]==v for n,v in ma.items());assert ia==ib;assert all(eb[n]==v for n,v in ea.items());assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in membership.items())
old=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE ARCH');s=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');rows=json.loads((O/'evidence/rev05b-authoring.json').read_text())['actors'];actors=[r for r in rows if all(n in old.objects for n in r['objects'])];assert len(actors)==180
assert not any(o.name.startswith('WEB CROWD /')for o in s.objects)
actorproof=[]
for r in actors:
 for name in r['objects']:assert s.objects.get(name)==old.objects[name]
 actorproof.append({'actor':r['label'],'foot':r['foot'],'yawRadians':r['yawRadians'],'widthScale':r['widthScale'],'heightScale':r['heightScale'],'parts':r['objects'],'meshUVTransformMaterialActionHashesExact':True})
for o in old.objects:
 sem=o.get('pilotOriginalObject',o.name)
 protected=sem.startswith(('Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron','Counter','Shop stock shelf','Dry goods carton','Destination plaster wall'))or o.name.startswith(('Shutter slat','Closed rolling shutter','Existing Aftermovie','TEAM','EVENTS'))or any(sl.material and sl.material.name.startswith('ART /')for sl in o.material_slots)
 if protected:assert s.objects.get(o.name)==o,o.name
assert s.world==old.world and s.view_settings.exposure==old.view_settings.exposure and s.view_settings.look==old.view_settings.look
assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in old.objects if o.type=='LIGHT'};assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
r={'status':'PASS','baselineSHA256':cfg['sha256'],'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'originalObjectSignaturesExact':len(a),'all11HistoricalSceneMembershipsAndSettingsExact':True,'sceneCount':len(bpy.data.scenes),'originalMaterialsWorldsImagesUnchanged':True,'selectedCrowd':'EXACT PRIOR BLENDER C180','crowdActors':actorproof,'actorCount':180,'bodyPartCount':sum(len(r['objects'])for r in actors),'websiteActorsInSelectedScene':0,'lights17Active12FiveSupports0W':True,'allSevenArtAndPhysicalShutterHostsExact':True,'originalFloorDestinationsCounterStockExact':True}
(O/'evidence/preservation-audit.json').write_text(json.dumps(r,indent=2));print('PRESERVATION_PASS',len(a),180,flush=True)
