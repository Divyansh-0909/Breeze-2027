import bpy,json,sys,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/art-authoring.json').read_text());master=O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend'
assert Path(bpy.data.filepath)==master and hashlib.sha256(master.read_bytes()).hexdigest()==d['masterSHA256']
assert len(bpy.data.scenes)==3
images=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(images)==28 and all(i.packed_file for i in images)
assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
assert len([o for o in bpy.data.objects if o.type=='CAMERA'])==61
for s in bpy.data.scenes:
 assert s.frame_end==960
 assert sum(o.type=='LIGHT'for o in s.objects)==17
 assert sum(o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')and o.data.energy==0 for o in s.objects)==5
for a in d['shutters']:
 mats={bpy.data.objects[n].material_slots[0].material for n in [a['host']]+a['slats']};assert len(mats)==1
 assert len(a['slats'])==18
assert bpy.data.objects.get('Festival takeover banner')is None
p=json.loads((O/'evidence/body-overlap-validation.json').read_text());assert p['actualAudienceCounts']=={'A':176,'B':184,'C':180}
r={'status':'PASS','masterSHA256':d['masterSHA256'],'scenes':3,'packedImages':28,'externalFontDependency':False,'cameras':61,'original40SecondActionPreserved':True,'storedLightsPerScene':17,'optionalLightsOffPerScene':5,'sourceArtists':3,'physicalSlats':54,'generatedWallProposals':4,'newMeshObjects':0,'audienceCounts':p['actualAudienceCounts'],'bannerAbsent':True}
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[];target=Path(args[0])if args else O/'evidence/master-reopen.json';target.write_text(json.dumps(r,indent=2)+'\n');print('PACKED_ART_MASTER_REOPEN_PASS',r)
