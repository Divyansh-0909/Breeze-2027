import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='C+A WORLD')
assert len(bpy.data.scenes)==5 and s.use_fake_user
assert {'A','B','C','C+A PILOT','C+A WORLD'}=={s['variant']for s in bpy.data.scenes}
assert len([i for i in bpy.data.images if i.type=='IMAGE'])==33 and all(i.packed_file for i in bpy.data.images if i.type=='IMAGE')
assert all(not f.filepath or f.filepath=='<builtin>'or getattr(f,'packed_file',None)for f in bpy.data.fonts)
assert sum(o.type=='LIGHT'for o in s.objects)==17 and sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12
assert all(o.data.energy==0 for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical'))
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==a['masterSHA256']
(O/'restored-blender-proof.json').write_text(json.dumps({'status':'PASS','fiveScenesIncludingFourHistorical':True,'images33Packed':True,'noExternalFontDependency':True,'lightsAndSourceHashVerified':True,'noResave':True},indent=2)+'\n');print('RESTORED_MASTER_PASS',flush=True)
