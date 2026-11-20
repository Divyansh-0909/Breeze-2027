import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=O.parent/'navigation-board-rev15l-led-sponsors-2026-11-11';P=B/'delivery/Gullyverse-Rev15L-Navigation-LED.blend'
def sha(p):
 d=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):d.update(b)
 return d.hexdigest()
assert sha(P)=='0f52196c59562c337078c196c904239a055108b5dcc824bc7dc57e95799b8eca'
old=json.loads((B/'evidence/sponsors.json').read_text());m=json.loads((O/'evidence/sponsors.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene;assert s['variant']=='REV15L';s.name='REV15L1 / Navigation and Wider Sponsor Gaps';s['variant']='REV15L1';s.frame_end=m['periodCells']
face=s.objects['REV15L / animated sponsor LED face'];mat=face.data.materials[0];nodes=mat.node_tree.nodes
images=[n for n in nodes if n.type=='TEX_IMAGE'];assert len(images)==1
im=bpy.data.images.load(str(O/'viewer/logo-strip.png'));im.name='REV15L1 / sponsor strip with wider logo gaps';im.colorspace_settings.name='Non-Color';im.pack();images[0].image=im
denominators=[n for n in nodes if n.type=='MATH' and n.operation=='DIVIDE' and not n.inputs[1].is_linked and n.inputs[1].default_value==old['periodCells']];assert len(denominators)==1;denominators[0].inputs[1].default_value=m['periodCells']
drivers=mat.node_tree.animation_data.drivers;assert len(drivers)==1;drivers[0].driver.expression=f'(frame - 1) % {m["periodCells"]}'
face['periodCells']=m['periodCells'];face['minimumLogoGapCells']=72
checks={'all62Logos':len(m['logos'])==62,'logoSizeUnchanged':all(a['logoCells']==b['logoCells'] for a,b in zip(old['logos'],m['logos'])),'scrollSpeedUnchanged':s.render.fps==30 and m['cellsPerSecond']==old['cellsPerSecond'],'42ScenesRetained':len(bpy.data.scenes)==42}
for frame,value in [(1,0),(2,1),(m['periodCells']+1,0)]:
 s.frame_set(frame);bpy.context.view_layer.update();checks[f'loopFrame{frame}']=abs(nodes['LED scroll cells'].outputs[0].default_value-value)<.001
assert all(checks.values()),checks
s.frame_set(1);bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
out=O/'delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
checks['baseFileUnchanged']=sha(P)=='0f52196c59562c337078c196c904239a055108b5dcc824bc7dc57e95799b8eca'
(O/'evidence/blender-validation.json').write_text(json.dumps({'status':'PASS','checks':checks,'masterSHA256':sha(out),'masterBytes':out.stat().st_size,'sceneCount':42},indent=2));print('WIDER LOGO GAPS SAVED',flush=True)
