import bpy,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from diagnostic_cameras import add_cameras
add_cameras()
for scene in bpy.data.scenes:scene['rev05_shelf_status']='PENDING_USER_ARCHITECTURE_EXCEPTION'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend'),compress=True)
print('REVIEW_MASTER_EXPORTED_WITH_PENDING_SHELF_STATUS',flush=True)
