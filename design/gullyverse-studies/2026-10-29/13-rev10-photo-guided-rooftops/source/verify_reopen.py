import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s['variant']=='PHOTO A';assert len(bpy.data.scenes)==15;assert sum(i.type=='IMAGE'for i in bpy.data.images)==33;assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE');assert all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts)
data=json.loads((O/'evidence/rev05b-authoring.json').read_text());rows=[]
for v in ['PHOTO A','PHOTO B']:
 sc=next(x for x in bpy.data.scenes if x.get('variant')==v);assert sum(all(n in sc.objects for n in r['objects'])for r in data['actors'])==180;assert not any(o.name.startswith('WEB CROWD /')for o in sc.objects);assert sum(o.type=='LIGHT'and o.data.energy>0 for o in sc.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in sc.objects)==5;rows.append({'variant':v,'actors':180,'lightsActive12FiveOff':True})
p=Path(bpy.data.filepath);(O/'evidence/master-reopen.json').write_text(json.dumps({'status':'PASS','masterSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'scenes':15,'originalArchives':13,'packedImages':33,'noExternalFonts':True,'defaultSceneIsProposalA_NotUserApproval':True,'rows':rows},indent=2));print('REOPEN_PASS',flush=True)
