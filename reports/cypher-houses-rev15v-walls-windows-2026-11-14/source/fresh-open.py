import bpy,json,hashlib,argparse,sys,runpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());plan=json.loads((R/'source/architecture-plan.json').read_text());snapshot=runpy.run_path(str(R/'source/preservation.py'))['snapshot'];fp=runpy.run_path(str(R.parent/'navigation-board-rev15u3-larger-english-text-2026-11-14/source/scene-fingerprint.py'))['fingerprint'];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--restored',action='store_true');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
base_path=b['source'];base_hash=b['sourceSHA256']
if a.restored:
 prior=json.loads((R.parent/'navigation-board-rev15u3-larger-english-text-2026-11-14/evidence/restore-check.json').read_text());base_path=prior['restoredMaster'];base_hash=prior['restoredSHA256']
assert sha(base_path)==base_hash;bpy.ops.wm.open_mainfile(filepath=base_path);base=bpy.context.scene;base.frame_set(1);bpy.context.view_layer.update();protected=snapshot(base,plan,'REV15U3 / ');history={s.name:sorted(o.name for o in s.objects) for s in bpy.data.scenes};original_channels={o.name:[list(o.location),list(o.rotation_euler),list(o.scale),o.parent.name if o.parent else None] for o in base.objects}
proof=json.loads((R/'evidence/restore-check.json').read_text()) if a.restored else b;path=proof['restoredMaster'] if a.restored else b['editedMaster'];expected=proof['restoredSHA256'] if a.restored else b['editedSHA256'];assert sha(path)==expected;bpy.ops.wm.open_mainfile(filepath=path);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
assert s.name=='REV15V / Weathered cypher houses and windows' and len(bpy.data.scenes)==56
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
historical=bpy.data.scenes['REV15U3 / Slightly larger English navigation'];assert all([list(historical.objects[n].location),list(historical.objects[n].rotation_euler),list(historical.objects[n].scale),historical.objects[n].parent.name if historical.objects[n].parent else None]==v for n,v in original_channels.items())
assert fp(s)['sha256']==json.loads((R/'evidence/native-scene-fingerprint.json').read_text())['sha256']
assert snapshot(s,plan,'REV15V / ')==protected
if not a.restored:assert protected==b['protectedSnapshot']
posters=[o for o in s.objects if 'EVENTS clearly labelled placeholder' in o.name];assert len(posters)==8
details=[o for o in s.objects if o.get('architectureHouse')];assert len(details)==9
for o in details:
 for face in o.data.polygons:
  pts=[o.matrix_world@o.data.vertices[i].co for i in face.vertices]
  assert not(max(p.x for p in pts)>13 and max(p.y for p in pts)>26.7 and min(p.y for p in pts)<38.3)
controller=next(o for o in s.objects if 'team_index' in o);checks=[]
for i in range(8):
 controller['team_index']=i;controller.update_tag();bpy.context.view_layer.update();visible=[o for o in s.objects if o.get('artKind') and not o.hide_render];assert len(visible)==1 and visible[0]['carouselSlide']==i;checks.append(i)
controller['team_index']=0;controller.update_tag();bpy.context.view_layer.update();assert all(im.source!='FILE' or im.packed_file for im in bpy.data.images);assert len(bpy.data.libraries)==0
texture_rows=json.loads((R/'evidence/material-authoring.json').read_text())['files']
for row in texture_rows:
 im=bpy.data.images[row['file']];assert hashlib.sha256(im.packed_file.data).hexdigest()==row['sha256']==sha(R/'textures'/row['file'])
result={'status':'PASS','freshNativeOpen':True,'scenes':56,'original55SceneMembershipsExact':True,'originalU3TransformChannelsExact':True,'activeSceneFingerprintExact':True,'protectedOriginalGeometryUVColoursMaterialsTransformsExact':True,'wholeTeamBuildingUnchanged':True,'exclusiveTeamMuralStates':checks,'EventsPostersUnchanged':8,'newWindowDetailBatches':9,'newGeometryOutsideTeamRegion':True,'allFileImagesPacked':True,'packedImages':sum(bool(im.packed_file) for im in bpy.data.images),'noLinkedLibraries':True,'sourceSHA256':expected}
(R/('evidence/restored-fresh-open.json' if a.restored else 'evidence/fresh-open.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
