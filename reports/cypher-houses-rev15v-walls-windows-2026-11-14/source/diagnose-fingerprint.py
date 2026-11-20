import bpy,runpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=json.loads((R/'evidence/build-verification.json').read_text());fp=runpy.run_path(str(R.parent/'navigation-board-rev15u3-larger-english-text-2026-11-14/source/scene-fingerprint.py'))['fingerprint']
bpy.ops.wm.open_mainfile(filepath=b['source']);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();before=fp(s)
bpy.ops.wm.open_mainfile(filepath=b['editedMaster']);s=bpy.data.scenes['REV15U3 / Slightly larger English navigation'];bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();after=fp(s)
diff=[{'before':x,'after':y} for x,y in zip(before['data']['objects'],after['data']['objects']) if x!=y];print(json.dumps({'before':before['sha256'],'after':after['sha256'],'diff':diff},indent=2))
