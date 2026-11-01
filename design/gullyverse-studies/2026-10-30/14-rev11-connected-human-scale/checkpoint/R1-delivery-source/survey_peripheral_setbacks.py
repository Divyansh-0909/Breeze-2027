import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];s=next(s for s in bpy.data.scenes if s.get('variant')=='REV11');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();out=[]
for label,points in [('left',[(x,y)for y in[20,30,42]for x in[-15.8,-16.4,-17,-17.8]]),('right',[(x,y)for y in[20,32,42]for x in[15.8,16.4,17,17.8]]),('back',[(x,y)for x in[-10,0,10]for y in[47.8,48.4,49,49.7]]),('front-attachment',[(-12,14),(12,14)])]:
 for x,y in points:
  h=s.ray_cast(dep,Vector((x,y,7.3)),Vector((0,0,-1)),distance=8);out.append({'zone':label,'xy':[x,y],'hitZ':h[1].z if h[0]else None,'owner':h[4].name if h[0]else None,'publicWalkingSample':False})
(O/'evidence/peripheral-setback-survey.json').write_text(json.dumps({'scope':'Nonpublic roof-edge/lightwell inspection; no change to protected floor or registry','rows':out},indent=2));print('SETBACK_SURVEY',[(r['zone'],r['xy'],r['hitZ'])for r in out])
