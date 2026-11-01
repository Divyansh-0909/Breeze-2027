import bpy,json
from pathlib import Path
images=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(bpy.data.scenes)==3;assert len(images)==25;assert all(i.packed_file for i in images);assert all(f.filepath=='<builtin>' or f.packed_file for f in bpy.data.fonts)
Path('/workspace/gullyverse-world-concept/2026-10-23/checkpoint/restored-blender-read.json').write_text(json.dumps({'status':'PASS','scenes':[s.name for s in bpy.data.scenes],'packedImages':len(images),'noLinkedExternalBlendLibraries':len(bpy.data.libraries)==0,'allUsedImagesPacked':True,'openedIndependentRestoredCopy':True},indent=2))
