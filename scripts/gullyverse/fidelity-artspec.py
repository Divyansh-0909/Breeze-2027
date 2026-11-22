"""Extract object-linked, world-projected artwork from the locked Rev15Z master for the runtime.

Usage: python fidelity-artspec.py -- MASTER.blend OUT.json
Each projection chain (MATH nodes from a world axis to the image vector) is recorded exactly.
"""
import bpy, sys, json
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=argv[0]); out = argv[1]
vl = bpy.context.view_layer; vl.update(); sc = bpy.context.scene
FILES = {"ART / original RITVIZ / RGBA": "ritviz", "ART / original CHAAR DIWARI / RGBA": "chaar-diwari",
         "ART / original NEHA KAKKAR / RGBA": "neha-kakkar", "ART / generated supporting pieces / shared atlas": "supporting-atlas"}
def unlinked(n):
    return [i.default_value for i in n.inputs if not i.is_linked and i.enabled][0]
def chain(sock):
    """Walk MATH nodes back to a SEPXYZ axis; returns axis and ops in evaluation order."""
    ops = []
    while sock.is_linked:
        n = sock.links[0].from_node; s = sock.links[0].from_socket
        if n.type == 'SEPXYZ': return s.name, list(reversed(ops))
        assert n.type == 'MATH', n.type
        linked = [i for i in n.inputs if i.is_linked and i.enabled]
        assert len(linked) == 1, (n.name, n.operation)
        first = n.inputs[0].is_linked
        ops.append([n.operation, round(unlinked(n), 6), first])  # first=True: x op c, else c op x
        sock = linked[0]
    raise AssertionError("unterminated chain")
arts = {}
for o in sc.objects:
    if o.type != 'MESH' or o.hide_render or not o.visible_get(view_layer=vl): continue
    for s in o.material_slots:
        m = s.material
        if not m or not m.use_nodes or "Exact source paint / shared image" not in m.node_tree.nodes: continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        a = arts.setdefault(m.name, {"lo": [1e9]*3, "hi": [-1e9]*3, "objects": 0}); a["objects"] += 1
        for i in range(3): a["lo"][i] = min(a["lo"][i], min(c[i] for c in cs)); a["hi"][i] = max(a["hi"][i], max(c[i] for c in cs))
specs = []
for name, a in sorted(arts.items()):
    nt = bpy.data.materials[name].node_tree; nodes = nt.nodes
    img = nodes["Exact source paint / shared image"]
    comb = img.inputs["Vector"].links[0].from_node
    u_axis, u_ops = chain(comb.inputs["X"]); v_axis, v_ops = chain(comb.inputs["Y"])
    gt = next(n for n in nodes if n.type == 'MATH' and n.operation == 'GREATER_THAN' and n.inputs[0].is_linked and
              n.inputs[0].links[0].from_node.type == 'MATH' and n.inputs[0].links[0].from_node.inputs[0].is_linked and
              n.inputs[0].links[0].from_node.inputs[0].links[0].from_node.type == 'SEPXYZ')
    n_axis, n_ops = chain(gt.inputs[0])
    rect = None
    for n in nodes:
        if n.type == 'COMBXYZ' and n != comb and any(l.to_node.type == 'SEPXYZ' for out in n.outputs for l in out.links):
            ru_axis, ru_ops = chain(n.inputs["X"]); rv_axis, rv_ops = chain(n.inputs["Y"])
            rect = {"u": {"axis": ru_axis, "ops": ru_ops}, "v": {"axis": rv_axis, "ops": rv_ops}}
    shutter = "painted rolled steel" in name
    paint = None
    if shutter:
        mix = nodes["World aligned paint mixture"]
        paint = [round((mix.inputs[1].default_value[i] + mix.inputs[2].default_value[i]) / 2, 4) for i in range(3)]
    specs.append({"material": name, "texture": FILES[img.image.name], "kind": "shutter" if shutter else "wall",
        "lo": [round(v - 0.05, 3) for v in a["lo"]], "hi": [round(v + 0.05, 3) for v in a["hi"]], "objects": a["objects"],
        "u": {"axis": u_axis, "ops": u_ops}, "v": {"axis": v_axis, "ops": v_ops},
        "normal": {"axis": n_axis, "ops": n_ops, "threshold": round(gt.inputs[1].default_value, 6)}, "rect": rect, "paint": paint})
json.dump(specs, open(out, "w"), indent=1); print("SPECS", len(specs))
for s in specs: print("SPEC", s["material"], s["texture"], s["u"], s["v"], s["normal"], "rect" if s["rect"] else "")
import os; os._exit(0)
