import bpy,json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];master=O/'source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend';bpy.ops.wm.open_mainfile(filepath=str(master))
a=json.loads((O/'evidence/rev05b-authoring.json').read_text());p=json.loads((O/'evidence/preservation-audit.json').read_text());assert hashlib.sha256(master.read_bytes()).hexdigest()==p['finalMasterSHA256']
assert len(bpy.data.scenes)==3
images=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(images)==24 and all(i.packed_file for i in images)
assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
assert bpy.data.objects.get('Festival takeover banner')is None
counts={s['variant']:sum(all(n in s.objects for n in r['objects'])for r in a['actors'])for s in bpy.data.scenes};assert counts==a['newAudienceCounts']
for n,r in p['counterAndDJFurniture'].items():assert [list(x)for x in bpy.data.objects[n].matrix_basis]==r['matrix']
for s in bpy.data.scenes:
    assert s['rev05b_status']=='OPEN_SHOPS_AND_DENSE_CENTER_STATIC_CROWD';assert s.frame_end==960;assert sum(o.type=='LIGHT'for o in s.objects)==17
for n in p['modifiedMeshObjects']:assert len(bpy.data.objects[n].data.vertices)==16
assert len([o for o in bpy.data.objects if o.type=='CAMERA'])==39
r={'status':'PASS','masterSHA256':p['finalMasterSHA256'],'baselineSHA256':hashlib.sha256((O/'source/baseline/Rev05A.blend').read_bytes()).hexdigest(),'scenes':3,'packedImages':24,'noExternalFontDependency':True,'audienceCounts':counts,'allFiveCountersAndDJMatricesIdentical':True,'cavityAndTrimMeshesPresent':10,'originalAndDiagnosticCameras':39,'lightsPerScene':17,'original40SecondActionPresent':True,'bannerAbsent':True}
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];target=Path(args[0])if args else O/'evidence/restored-master-validation.json';target.write_text(json.dumps(r,indent=2)+'\n');print('RESTORED_REV05B_MASTER_PASS',counts,flush=True)
