"""Neutral display ground only; does not alter the world floor or proposal counters."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/options.json').read_text())
for s in bpy.data.scenes:
 if not s['variant'].startswith('OPTION counter'):continue
 bpy.context.window.scene=s;s.frame_set(1)
 # Original lane slab ends before the outside legs. A clearly labelled display
 # ground patch provides a neutral shadow receiver in these isolated studies.
 me=bpy.data.meshes.new('PROPOSAL DISPLAY / ground');me.from_pydata([(-6,-30,5.995),(-3.601,-30,5.995),(-3.601,-20,5.995),(-6,-20,5.995)],[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new('PROPOSAL DISPLAY / neutral floor extension, not world geometry',me);s.collection.objects.link(o);me.materials.append(bpy.data.materials['Dry lane dust'])
 r=next(r for r in d['renders']if r['scene']==s.name);s.camera=bpy.data.objects[r['camera']];s.render.filepath=str(O/r['file']);bpy.ops.render.render(write_still=True);r['sha256']=hashlib.sha256((O/r['file']).read_bytes()).hexdigest();r['displayGroundOnly']='neutral shadow receiver outside original lane in isolated proposal; not applied to world'
master=O/'source/Crowd-and-Counter-Proposals-Only.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True);d['masterSHA256']=hashlib.sha256(master.read_bytes()).hexdigest();d['neutralProposalGroundNotAppliedToWorld']=True;(O/'evidence/options.json').write_text(json.dumps(d,indent=2)+'\n')
