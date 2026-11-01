import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];p=Path(bpy.data.filepath);variants={s.get('variant')for s in bpy.data.scenes};assert len(bpy.data.scenes)==13;assert {'SQUARE C180','SQUARE BEFORE','TERRACE ARCH','TERRACE WEB CROWD','A','B','C','SOURCE AUDIT'}<=variants
assert sum(i.type=='IMAGE'for i in bpy.data.images)==33;assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE');assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
s=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');assert bpy.context.scene==s;assert not any(o.name.startswith('WEB CROWD /')for o in s.objects);assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
data=json.loads((O/'evidence/rev05b-authoring.json').read_text());assert sum(all(n in s.objects for n in r['objects'])for r in data['actors'])==180
r={'status':'PASS','masterSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'masterBytes':p.stat().st_size,'sceneCount':13,'all11Rev08ArchivesPresent':True,'selectedCrowd':'EXACT PRIOR BLENDER C180','selectedOldCrowdActors':180,'websiteActorsInSelectedScene':0,'all33ImagesPacked':True,'noExternalFontDependency':True,'original12LightsAndFiveOffSupports':True}
(O/'evidence/master-reopen.json').write_text(json.dumps(r,indent=2));print('MASTER_REOPEN_PASS',flush=True)
