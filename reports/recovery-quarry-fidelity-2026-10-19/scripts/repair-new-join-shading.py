from pathlib import Path
import bpy,json,sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts/blender'))
import author_quarry_fidelity as common
master=ROOT/'assets-source/gullyverse/quarry-fidelity-correction/.authoring-cache/fidelity-unbaked.blend'
bpy.ops.wm.open_mainfile(filepath=str(master));tags=json.loads(bpy.data.texts['ALL_LOD_FACE_SOURCE_TAGS'].as_string());rows=[]
for level in range(3):
 ob=bpy.data.objects[f'Fidelity_Wall_15_LOD{level}'];before=[v.co[:]for v in ob.data.vertices];protected={tuple(common.G(ob.data.vertices[i].co))for i in common.loops(ob.data)[0]}
 repairs=common.repair_join_shading(ob,tags[level],protected);assert before==[v.co[:]for v in ob.data.vertices];rows.append(dict(LOD=level,hardRockBreakFaces=repairs,positionsAndUVUnchanged=True))
bpy.ops.wm.save_as_mainfile(filepath=str(master));(ROOT/'reports/recovery-quarry-fidelity-2026-10-19/raw/join-normal-production.json').write_text(json.dumps(rows,indent=2))
