import bpy,json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];p=Path(bpy.data.filepath);assert p.name=='Gullyverse-Rev08-Terrace-Website-Assets.blend';variants={s.get('variant')for s in bpy.data.scenes};assert len(bpy.data.scenes)==11
assert {'A','B','C','C+A PILOT','C+A WORLD','TERRACE BEFORE','TERRACE ARCH','TERRACE WEB CROWD','TERRACE PROPS A','TERRACE PROPS B','SOURCE AUDIT'}==variants
assert sum(i.type=='IMAGE'for i in bpy.data.images)==33;assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE');assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
s=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE WEB CROWD');assert sum(o.name.startswith('WEB CROWD /')for o in s.objects)==180;assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
assert not any(o.name.startswith('TERRACE PROPS ')for o in s.objects)
r={'status':'PASS','masterSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'masterBytes':p.stat().st_size,'scenes':sorted(variants),'all33ImagesPacked':True,'noExternalFontDependency':True,'actualWebsiteCrowd180':True,'fiveSupportsOFF':True,'ambiguousFurnitureNotInDefaultCandidate':True}
(O/'evidence/master-reopen.json').write_text(json.dumps(r,indent=2));print('MASTER_REOPEN_PASS',flush=True)
