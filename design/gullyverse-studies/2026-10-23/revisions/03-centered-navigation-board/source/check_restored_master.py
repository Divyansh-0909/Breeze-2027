import bpy,json,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
assert len(bpy.data.scenes)==3
images=[i for i in bpy.data.images if i.type=='IMAGE']
assert len(images)==25 and all(i.packed_file for i in images)
assert not bpy.data.libraries
assert '14-board-arrival' in bpy.data.objects
for n in ['Navigation base','Navigation base.001']:assert abs(bpy.data.objects[n].location.y-21)<1e-5
assert abs((bpy.data.objects['Navigation base'].location.x+bpy.data.objects['Navigation base.001'].location.x)/2)<1e-5
assert not any(o.name.startswith(('Roof service room / reveal occluder','Service roof cap','Service black water tank','Tank reinforcing rib','Street wayfinding paste-up'))for o in bpy.data.objects)
Path(args[0]).write_text(json.dumps({'status':'PASS','scenes':3,'packedImages':25,'noLinkedBlendLibraries':True,'noRevealColumnOrFloatingDependents':True,'boardCenteredInApproach':True,'openedIndependentExtractedMaster':True},indent=2)+'\n')
print('RESTORED_MASTER_PASS',flush=True)
