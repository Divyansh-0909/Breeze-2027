import bpy,sys,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1]
master=O/'source/Gullyverse-Rev05C-Interior-Support-Off.blend'
assert Path(bpy.data.filepath)==master
p=json.loads((O/'evidence/preservation-audit.json').read_text())
a=json.loads((O/'evidence/rev05b-authoring.json').read_text())
assert hashlib.sha256(master.read_bytes()).hexdigest()==p['afterSHA256']
assert len(bpy.data.scenes)==3
assert len([i for i in bpy.data.images if i.type=='IMAGE'])==24
assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE')
assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
counts={s['variant']:sum(all(n in s.objects for n in r['objects'])for r in a['actors'])for s in bpy.data.scenes}
assert counts=={'A':176,'B':184,'C':180}
for s in bpy.data.scenes:
 assert s.frame_end==960
 assert len([o for o in s.objects if o.type=='LIGHT'])==17
 optional=[o for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')]
 assert len(optional)==5 and all(o.data.energy==0 for o in optional)
assert len([o for o in bpy.data.objects if o.type=='CAMERA'])==39
assert bpy.data.objects.get('Festival takeover banner')is None
r={'status':'PASS','masterSHA256':p['afterSHA256'],'scenes':3,'packedImages':24,'externalFontDependency':False,'cameraCount':39,'original40SecondActionPresent':True,'storedLightsPerScene':17,'optionalSupportsOffPerScene':5,'audienceCounts':counts,'bannerAbsent':True,'graffitiAssetsAdded':0,'scope':'Partial lighting-only derivative; graffiti is unresolved, not falsely completed'}
args=sys.argv[sys.argv.index('--')+1:]if'--'in sys.argv else[]
target=Path(args[0])if args else O/'evidence/master-reopen.json'
target.write_text(json.dumps(r,indent=2)+'\n');print('RESTORED_REV05C_PASS',counts)
