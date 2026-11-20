import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath="/workspace/Breeze-2027/reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend");s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
rows=[]
for o in s.objects:
 if o.type=="LIGHT" or any(k in o.name.lower() for k in ["events","team","fixture","lamp"]) or (o.type=="MESH" and o.data.name.startswith("REV13A shared")):
  row={"name":o.name,"type":o.type,"location":list(o.matrix_world.translation),"rotation":list(o.rotation_euler),"data":o.data.name if o.data else None,"props":dict(o.items())}
  if o.type=="LIGHT":row.update(energy=o.data.energy,color=list(o.data.color),kind=o.data.type,size=getattr(o.data,"size",None))
  if o.type=="MESH":row.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials])
  rows.append(row)
(R/"evidence/native-inspection.json").write_text(json.dumps(rows,indent=2,default=str));print("INSPECTED",len(rows),flush=True)
