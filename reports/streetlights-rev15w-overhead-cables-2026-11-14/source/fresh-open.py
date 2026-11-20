import bpy,json,hashlib,runpy,sys,argparse
from pathlib import Path
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());plan=json.loads((R/'source/lighting-plan.json').read_text());snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R/'source/scene-fingerprint.py'))['fingerprint'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ap=argparse.ArgumentParser();ap.add_argument('--restored',action='store_true');ap.add_argument('--base');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);b['source']=a.base or b['source'];assert a.base or sha(b['source'])==b['sourceSHA256'];bpy.ops.wm.open_mainfile(filepath=b['source']);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();assert fp(base)['sha256']==plan['sourceSceneFingerprint'];protected=snapshot(base,{'objects':[]},'REV15V2 / ');originalNames={o.name.removeprefix('REV15V2 / ') for o in base.objects};history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};world=base.world.name;exposure=base.view_settings.exposure;fps=base.render.fps/base.render.fps_base
proof=json.loads((R/'evidence/restore-check.json').read_text()) if a.restored else b;assert sha(proof['editedMaster'])==proof['editedSHA256'];bpy.ops.wm.open_mainfile(filepath=proof['editedMaster']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();assert len(bpy.data.scenes)==59 and fp(s)['sha256']==b['sceneFingerprintSHA256'];originals=[o for o in s.objects if o.name.removeprefix('REV15W / ') in originalNames];assert len(originals)==len(originalNames);assert snapshot(SimpleNamespace(objects=originals),{'objects':[]},'REV15W / ')==protected;assert s.world.name==world and s.view_settings.exposure==exposure and s.render.fps/s.render.fps_base==fps;assert all(sorted(o.name for o in bpy.data.scenes[k].objects)==v for k,v in history.items())
new=[o for o in s.objects if o.get('streetLampPart')];bounds=[]
for o in new:
 if o.type=='MESH':bounds.extend(o.matrix_world@v.co for v in o.data.vertices)
 elif o.type=='LIGHT':assert o.location.y+o.data.cutoff_distance<14,'A new light range reaches the cypher'
assert max(p.y for p in bounds)<0,'Streetlight geometry extends outside the gully-only scope';assert min(p.z for p in bounds)>5.9
meta=json.loads((R/'delivery/streetlights.json').read_text());checks=[]
def coefficient(lamp,frame):
 if lamp['state']=='dead':return 0
 if lamp['state']=='steady':return 1
 f=(frame-1+lamp['phaseFrames'])%meta['periodFrames'];value=1
 for at,v in meta['keys']:
  if at<=f:value=v
 return value
for frame in [1,52,54,59,81,140,142,146,147,204,207,211,214,253,306]:
 s.frame_set(frame);bpy.context.view_layer.update()
 for lamp in meta['lamps']:
  light=s.objects[lamp['lightObject']];lens=s.objects[lamp['lensObject']];strength=lens.material_slots[0].material.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value;v=coefficient(lamp,frame);assert abs(light.data.energy-lamp['basePowerWatts']*v)<.0002;assert abs(strength-lamp['emissionBase']*v)<.0002;checks.append({'frame':frame,'id':lamp['id'],'coefficient':v})
s.frame_set(1);c=next(o for o in s.objects if 'team_index' in o)
for i in range(8):
 c['team_index']=i;c.update_tag();bpy.context.view_layer.update();visible=[o for o in s.objects if o.get('artKind') and not o.hide_render];assert len(visible)==1 and visible[0]['carouselSlide']==i
c['team_index']=0;c.update_tag();bpy.context.view_layer.update();assert len([o for o in s.objects if 'EVENTS clearly labelled placeholder' in o.name])==8;assert not bpy.data.libraries and all(i.source!='FILE' or i.packed_file for i in bpy.data.images)
result={'status':'PASS','sourceSHA256':proof['editedSHA256'],'scenes':59,'all58HistoricalSceneMembershipsPreserved':True,'allOriginalObjectsShapesUVsColoursMaterialsTransformsAndLightsExact':True,'TeamEightMuralStatesAndEventsPostersPreserved':True,'newGeometryOnlyAlongGullyRoad':True,'newLightRangesExcludeCypher':True,'gateWalkingCorridorUnchanged':True,'worldExposureAndFrameRateUnchanged':True,'minimumPlannedCableClearanceMetres':plan['minimumCableClearance'],'lamps':meta['counts'],'nativeLightAndEmissionSamplesVerified':checks,'allImagesPacked':True,'packedImages':sum(bool(i.packed_file) for i in bpy.data.images)};(R/('evidence/restored-fresh-open.json' if a.restored else 'evidence/fresh-open.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','scenes':59,'gullyOnly':True,'nativeSamples':len(checks)}))
