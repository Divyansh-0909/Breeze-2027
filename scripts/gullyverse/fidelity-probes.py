"""Render street-level Cycles reflection probes (equirectangular HDR) from the locked Rev15Z master.

Usage: python fidelity-probes.py -- MASTER.blend OUTDIR WIDTH SAMPLES id:x:y:eye ...
Coordinates are Blender metres; eye height is above the floor found by a downward ray.
The camera faces +X with +Z up, matching three.js equirectangular mapping.
"""
import bpy, sys, math, time
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
blend, outdir, W, samples, *specs = argv
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene; vl = bpy.context.view_layer; vl.update()
VOL = {"PRINCIPLED_VOLUME","VOLUME_ABSORPTION","VOLUME_SCATTER"}
for o in sc.objects:
    if o.type == 'VOLUME' or (o.type == 'MESH' and any(m and m.use_nodes and any(n.type in VOL for n in m.node_tree.nodes) for m in o.data.materials)):
        o.hide_render = True
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(samples)
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = int(W), int(W)//2, 100
sc.render.image_settings.file_format = 'HDR'; sc.render.film_transparent = False
cd = bpy.data.cameras.new("Runtime probe"); cd.type = 'PANO'
try: cd.panorama_type = 'EQUIRECTANGULAR'
except Exception: cd.cycles.panorama_type = 'EQUIRECTANGULAR'
cam = bpy.data.objects.new("Runtime probe", cd); sc.collection.objects.link(cam)
cam.rotation_euler = (math.pi/2, 0, -math.pi/2)  # faces +X, up +Z -> three.js equirect convention
sc.camera = cam
dg = bpy.context.evaluated_depsgraph_get()
written = []
for spec in specs:
    name, x, y, h = spec.split(":"); x, y, h = float(x), float(y), float(h)
    hit, loc, *_ = sc.ray_cast(dg, Vector((x, y, 40)), Vector((0, 0, -1)))
    floor = loc.z if hit else 6.0
    cam.location = (x, y, floor + float(h)); vl.update()
    sc.render.filepath = f"{outdir}/probe-{name}.hdr"; t = time.time()
    bpy.ops.render.render(write_still=True)
    written.append({"id": name, "blender": [round(v, 3) for v in cam.location]})
    print("PROBE", name, [round(v,2) for v in cam.location], "floor", round(floor,2), "secs", round(time.time()-t,1), flush=True)
import json
json.dump(written, open(f"{outdir}/probes.json", "w"), indent=1)
import os; os._exit(0)
