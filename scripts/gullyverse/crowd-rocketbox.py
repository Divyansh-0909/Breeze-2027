"""Bakes Microsoft Rocketbox avatars (MIT) into static posed crowd meshes for the web.

    blender -b --python scripts/gullyverse/crowd-rocketbox.py -- <rocketbox Assets dir> <out dir> <avatar> [<avatar> ...]

For each avatar: imports the rigged FBX, applies Rocketbox animations (in place, root motion removed) at a
representative frame (idle: first frame; cheer: hands highest; clap: hands closest; dance: mid-clip),
bakes each pose to a static mesh standing on z = 0 and centred on the pelvis, adds a ~30% decimated far
version and a ~10% distant version, keeps the body and head colour and normal maps (colour 1024 px, normal 512 px), and exports one
GLB per avatar with meshes named "<pose>|lod0", "<pose>|lod1" and "<pose>|lod2". Rocketbox faces -Y in Blender (three.js +Z).
"""
import bpy, sys, os, math, addon_utils
from mathutils import Vector

addon_utils.enable("io_scene_fbx")
addon_utils.enable("io_scene_gltf2")
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
assets, out, avatars = args[0], args[1], args[2:]
os.makedirs(out, exist_ok=True)
POSES = {"idle": "idle_neutral_01", "cheer": "cheer_01", "clap": "claphands_01", "dance": "dancing_neutral"}

def hand_metric(arm, pose):
    l = arm.pose.bones.get("Bip01 L Hand"); r = arm.pose.bones.get("Bip01 R Hand")
    if not l or not r: return 0
    lw, rw = arm.matrix_world @ l.head, arm.matrix_world @ r.head
    if pose == "cheer": return max(lw.z, rw.z)            # arms raised
    if pose == "clap": return -(lw - rw).length            # hands together
    return 0

for avatar in avatars:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sex = "f" if avatar.lower().startswith("female") else "m"
    bpy.ops.import_scene.fbx(filepath=f"{assets}/Avatars/Adults/{avatar}/Export/{avatar}.fbx")
    arm = next(o for o in bpy.context.scene.objects if o.type == "ARMATURE")
    mesh = next(o for o in bpy.context.scene.objects if o.type == "MESH")
    keep = []
    for pose, clip in POSES.items():
        before = set(bpy.context.scene.objects)
        acts_before = set(bpy.data.actions)
        bpy.ops.import_scene.fbx(filepath=f"{assets}/Animations/all_animations_max_motextr_static/{sex}_{clip}.max.fbx")
        added = set(bpy.context.scene.objects) - before
        source = next(o for o in added if o.type == "ARMATURE")
        action = source.animation_data.action
        # Retarget in world space: the clip's rest pose differs from the avatar's bind pose, so local
        # rotations do not transfer. Each avatar bone copies its namesake's world rotation (the pelvis
        # root also its location).
        for bone in arm.pose.bones:
            for c in list(bone.constraints): bone.constraints.remove(c)
            if bone.name not in source.pose.bones: continue
            c = bone.constraints.new("COPY_ROTATION"); c.target = source; c.subtarget = bone.name
            c.owner_space = c.target_space = "WORLD"
            if bone.name in ("Bip01", "Bip01 Pelvis"):
                c = bone.constraints.new("COPY_LOCATION"); c.target = source; c.subtarget = bone.name
                c.owner_space = c.target_space = "WORLD"
        src_arm = arm
        arm = source  # frame selection reads the clip's own hands
        start, end = int(action.frame_range[0]), int(action.frame_range[1])
        if pose == "idle": frame = start
        elif pose == "dance": frame = (start + end) // 2
        else:
            best, frame = -1e9, start
            for f in range(start, end + 1, 5):
                bpy.context.scene.frame_set(f)
                m = hand_metric(arm, pose)
                if m > best: best, frame = m, f
        arm = src_arm
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        data = bpy.data.meshes.new_from_object(mesh.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        data.transform(mesh.matrix_world)
        pelvis = arm.matrix_world @ arm.pose.bones["Bip01 Pelvis"].head
        zmin = min(v.co.z for v in data.vertices)
        data.transform(__import__("mathutils").Matrix.Translation(Vector((-pelvis.x, -pelvis.y, -zmin))))
        for lod, ratio in (("lod0", 1.0), ("lod1", 0.3), ("lod2", 0.1)):
            obj = bpy.data.objects.new(f"{pose}|{lod}", data if lod == "lod0" else data.copy())
            bpy.context.scene.collection.objects.link(obj)
            if ratio < 1:
                mod = obj.modifiers.new("decimate", "DECIMATE"); mod.ratio = ratio
                bpy.context.view_layer.objects.active = obj
                with bpy.context.temp_override(object=obj, active_object=obj):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
            obj["pose"] = pose; obj["frame"] = frame; obj["lod"] = lod
            keep.append(obj)
        for o in added: bpy.data.objects.remove(o, do_unlink=True)
        print("POSE", avatar, pose, "frame", frame, "tris", sum(len(p.vertices) - 2 for p in data.polygons))
    for o in list(bpy.context.scene.objects):
        if o not in keep: bpy.data.objects.remove(o, do_unlink=True)
    # Materials: rebuilt from the avatar's own colour and normal maps (the FBX texture links do not resolve),
    # matte, with default dielectric specular; textures resized for the web.
    textures = f"{assets}/Avatars/Adults/{avatar}/Textures"
    for mat in {s.material for o in keep for s in o.material_slots if s.material}:
        base = mat.name.split(".")[0]
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        out_node = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
        bsdf.inputs["Roughness"].default_value = 0.78
        bsdf.inputs["Metallic"].default_value = 0
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
        for kind, size in (("color", 1024), ("normal", 512)):
            file = f"{textures}/{base}_{kind}.tga"
            if not os.path.exists(file):
                if kind == "color": print("NO TEXTURE", file)
                continue
            image = bpy.data.images.load(file)
            if image.size[0] > size: image.scale(size, size)
            tex = nodes.new("ShaderNodeTexImage"); tex.image = image
            if kind == "color":
                links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
                if "opacity" in base:  # hair cards and lashes: alpha cut-out
                    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
                    mat.blend_method = "CLIP" if hasattr(mat, "blend_method") else mat.blend_method
                    mat.alpha_threshold = 0.5
            else:
                image.colorspace_settings.name = "Non-Color"
                nmap = nodes.new("ShaderNodeNormalMap")
                links.new(tex.outputs["Color"], nmap.inputs["Color"])
                links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    path = f"{out}/{avatar}.glb"
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_apply=True, export_animations=False,
                              export_skins=False, export_morph=False, export_extras=True, export_yup=True)
    print("WROTE", path, os.path.getsize(path))
