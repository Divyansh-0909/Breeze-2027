import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
assert len(bpy.data.scenes)==3
images=[i for i in bpy.data.images if i.type=='IMAGE']
assert len(images)==25 and all(i.packed_file for i in images)
assert not bpy.data.libraries
assert not any(o.name.startswith(('Roof service room / reveal occluder','Service roof cap','Service black water tank','Tank reinforcing rib','Street wayfinding paste-up'))for o in bpy.data.objects)
Path(args[0]).write_text(json.dumps({'status':'PASS','scenes':3,'packedImages':25,'noLinkedBlendLibraries':True,'noRevealColumnOrFloatingDependents':True,'openedIndependentExtractedMaster':True},indent=2)+'\n')
print('RESTORED_MASTER_PASS',flush=True)
