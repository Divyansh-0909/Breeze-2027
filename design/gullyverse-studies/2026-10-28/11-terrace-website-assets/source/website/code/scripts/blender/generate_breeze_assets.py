"""Generate authored Breeze festival environment assets for the web.

Run with Blender 5.x:
  blender --background --python scripts/blender/generate_breeze_assets.py -- <repo-root>

The script produces:
  public/models/breeze/aftermovie-stage.glb
  public/models/breeze/team-backstage.glb
  public/models/breeze/help-desk.glb

The scenes intentionally use real-world metres, applied transforms, bevelled
manufactured edges, named interaction surfaces and glTF-friendly Principled
materials so the React Three Fiber runtime can stay lightweight.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def repo_root() -> Path:
    args = sys.argv
    if "--" in args:
        tail = args[args.index("--") + 1 :]
        if tail:
            return Path(tail[0]).resolve()
    return Path(__file__).resolve().parents[2]


ROOT = repo_root()
OUT = ROOT / "public" / "models" / "breeze"
OUT.mkdir(parents=True, exist_ok=True)


def clean() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    # The standalone bpy 5.2 wheel still exposes Eevee under the historical
    # BLENDER_EEVEE identifier even though the desktop UI calls it Eevee Next.
    bpy.context.scene.render.engine = "BLENDER_EEVEE"


def material(
    name: str,
    color: tuple[float, float, float, float],
    *,
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def apply_bevel(obj: bpy.types.Object, width: float, segments: int = 2) -> None:
    if width <= 0:
        return
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(name="manufactured_edge", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=mod.name)


def box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    rot: tuple[float, float, float] = (0, 0, 0),
    bevel: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_bevel(obj, min(bevel, min(size) * 0.22), 2)
    obj.data.materials.append(mat)
    return obj


def cylinder(
    name: str,
    radius: float,
    depth: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    *,
    vertices: int = 20,
    rot: tuple[float, float, float] = (0, 0, 0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    apply_bevel(obj, min(radius * 0.12, 0.018), 2)
    return obj


def sphere(name: str, radius: float, loc: tuple[float, float, float], mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def cable(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, point in zip(spline.bezier_points, points):
        bp.co = point
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def text_mesh(
    name: str,
    body: str,
    loc: tuple[float, float, float],
    size: float,
    mat: bpy.types.Material,
    *,
    extrude: float = 0.014,
    align: str = "CENTER",
) -> bpy.types.Object:
    bpy.ops.object.text_add(location=loc, rotation=(math.radians(90), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = extrude
    obj.data.bevel_depth = 0.004
    obj.data.bevel_resolution = 2
    obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def export(name: str) -> None:
    path = OUT / name
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=False,
    )
    print(f"EXPORT {path}")


def stage_asset() -> None:
    clean()
    deck = material("MAT_stage_deck", (0.028, 0.034, 0.043, 1), metallic=0.28, roughness=0.48)
    deck_alt = material("MAT_stage_deck_worn", (0.045, 0.049, 0.055, 1), metallic=0.18, roughness=0.62)
    black = material("MAT_black_fabric", (0.008, 0.009, 0.012, 1), roughness=0.88)
    steel = material("MAT_stage_steel", (0.34, 0.37, 0.41, 1), metallic=0.88, roughness=0.27)
    rubber = material("MAT_rubber", (0.014, 0.015, 0.016, 1), roughness=0.84)
    yellow = material("MAT_safety_yellow", (0.63, 0.38, 0.035, 1), roughness=0.56)

    # Main deck and thrust use modular panels instead of one perfect cuboid.
    box("GEO_stage_subframe", (24.0, 9.0, 1.18), (0, 0.5, 0.59), black, bevel=0.035)
    for ix, x in enumerate((-10, -6, -2, 2, 6, 10)):
        for iy, y in enumerate((-2.9, 0.1, 3.1)):
            mat = deck_alt if (ix + iy) % 4 == 0 else deck
            box(f"GEO_deck_panel_{ix}_{iy}", (3.96, 2.96, 0.12), (x, y, 1.24), mat, bevel=0.02)
    box("GEO_runway_subframe", (6.0, 10.0, 1.18), (0, -9.0, 0.59), black, bevel=0.04)
    for iy, y in enumerate((-5.0, -7.0, -9.0, -11.0, -13.0)):
        box(f"GEO_runway_panel_{iy}", (5.9, 1.93, 0.12), (0, y, 1.24), deck if iy % 2 else deck_alt, bevel=0.018)

    # Skirting, aluminium edging and service stairs make the deck read as fabricated.
    box("GEO_front_skirt", (23.8, 0.08, 1.06), (0, -4.48, 0.62), black, bevel=0.01)
    for x in (-12.02, 12.02):
        box(f"GEO_stage_edge_{x}", (0.07, 9.0, 1.12), (x, 0.5, 0.65), steel, bevel=0.008)
    for x in (-11.2, 11.2):
        for i in range(4):
            box(
                f"GEO_service_step_{x}_{i}",
                (1.8, 0.66, 0.18),
                (x, -4.55 - i * 0.55, 1.02 - i * 0.25),
                deck,
                bevel=0.025,
            )

    # Monitor wedges, flight cases, cable ramps and small believable clutter.
    for i, x in enumerate((-8.7, -4.4, 4.4, 8.7)):
        box(f"PROP_monitor_{i}", (1.25, 0.72, 0.48), (x, -3.25, 1.58), black, rot=(math.radians(-8), 0, 0), bevel=0.07)
    for i, (x, y) in enumerate(((-10.1, 2.5), (9.4, 2.2), (-8.6, -0.8))):
        box(f"PROP_roadcase_{i}", (1.25, 0.85, 0.82), (x, y, 1.72), black, bevel=0.055)
        box(f"PROP_roadcase_trim_{i}", (1.28, 0.89, 0.05), (x, y, 2.13), steel, bevel=0.015)
    for i, x in enumerate((-3.7, 0, 3.7)):
        box(f"PROP_cable_ramp_{i}", (2.25, 0.72, 0.13), (x, -14.15, 0.07), rubber, bevel=0.06)
        box(f"PROP_cable_ramp_stripe_{i}", (0.32, 0.74, 0.145), (x, -14.15, 0.145), yellow, bevel=0.018)
    cable("PROP_stage_cable_01", [(-9, -3.7, 1.34), (-5, -3.9, 1.35), (-1, -4.0, 1.35), (2, -5.2, 1.34)], 0.035, rubber)

    export("aftermovie-stage.glb")


def team_asset() -> None:
    clean()
    board = material("MAT_team_board", (0.20, 0.27, 0.23, 1), roughness=0.91)
    wood = material("MAT_team_frame_wood", (0.22, 0.12, 0.065, 1), roughness=0.72)
    steel = material("MAT_team_support_steel", (0.29, 0.31, 0.31, 1), metallic=0.78, roughness=0.36)
    rubber = material("MAT_team_feet", (0.018, 0.019, 0.018, 1), roughness=0.9)
    warm = material(
        "MAT_team_bulb",
        (1.0, 0.62, 0.24, 1),
        roughness=0.18,
        emission=(1.0, 0.42, 0.10, 1),
        emission_strength=3.4,
    )

    # Freestanding festival notice board inspired by the user's real night-fest
    # reference. The face stays intentionally blank: accessible DOM content is
    # aligned over it in React so names/photos remain sharp and selectable.
    box("BOARD_team_backing", (8.2, 0.22, 4.75), (0, 0.08, 2.55), wood, bevel=0.055)
    box("BOARD_team_surface", (7.82, 0.055, 4.37), (0, -0.065, 2.55), board, bevel=0.02)

    for x in (-3.55, 3.55):
        cylinder(f"BOARD_post_{x}", 0.08, 5.55, (x, 0.16, 2.05), steel, vertices=16)
        box(f"BOARD_foot_{x}", (1.20, 1.0, 0.10), (x, 0.16, 0.05), rubber, bevel=0.035)
        box(f"BOARD_brace_{x}", (0.08, 1.40, 1.65), (x, 0.60, 0.72), steel, rot=(math.radians(-23), 0, 0), bevel=0.018)

    # A real cable and individual practical bulbs run around the board instead
    # of a uniformly emissive frame. This gives the renderer believable falloff.
    cable(
        "BOARD_string_cable",
        [(-3.82, -0.22, 4.94), (-1.9, -0.29, 5.05), (0, -0.34, 4.94), (1.9, -0.29, 5.05), (3.82, -0.22, 4.94)],
        0.018,
        rubber,
    )
    for i, x in enumerate((-3.65, -2.45, -1.22, 0, 1.22, 2.45, 3.65)):
        sphere(f"LGT_team_board_bulb_{i}", 0.065, (x, -0.31, 4.86 + (0.07 if i % 2 else 0)), warm)

    export("team-backstage.glb")


def help_desk_asset() -> None:
    clean()
    canvas = material("MAT_stall_black_canvas", (0.018, 0.021, 0.020, 1), roughness=0.96)
    canvas_alt = material("MAT_stall_black_canvas_alt", (0.032, 0.035, 0.033, 1), roughness=0.93)
    steel = material("MAT_stall_aluminium", (0.40, 0.42, 0.41, 1), metallic=0.84, roughness=0.31)
    table = material("MAT_stall_table", (0.11, 0.085, 0.060, 1), roughness=0.72)
    board = material("MAT_stall_back_board", (0.055, 0.064, 0.060, 1), roughness=0.91)
    cardboard = material("MAT_stall_cardboard", (0.43, 0.29, 0.16, 1), roughness=0.92)
    rubber = material("MAT_stall_rubber", (0.010, 0.011, 0.011, 1), roughness=0.91)
    warm = material(
        "MAT_stall_bulb",
        (1.0, 0.63, 0.25, 1),
        roughness=0.2,
        emission=(1.0, 0.43, 0.10, 1),
        emission_strength=3.5,
    )

    # Reusable real-world event stall: exposed aluminium frame, fabric roof,
    # cloth-covered empty table, top fascia, rear content board and a separate
    # cardboard lower banner. No kiosk shell, queue barriers or tabletop props.
    front_y = -1.65
    back_y = 1.05
    pole_x = 3.20
    pole_h = 4.15

    for x in (-pole_x, pole_x):
        for y in (front_y, back_y):
            cylinder(f"FRAME_pole_{x}_{y}", 0.055, pole_h, (x, y, pole_h / 2), steel, vertices=16)
            cylinder(f"FRAME_foot_{x}_{y}", 0.16, 0.055, (x, y, 0.035), rubber, vertices=20)

    cylinder("FRAME_front_rail", 0.045, 6.45, (0, front_y, 4.05), steel, vertices=14, rot=(0, math.radians(90), 0))
    cylinder("FRAME_back_rail", 0.045, 6.45, (0, back_y, 4.05), steel, vertices=14, rot=(0, math.radians(90), 0))
    cylinder("FRAME_left_rail", 0.045, 2.70, (-pole_x, -0.30, 4.05), steel, vertices=14, rot=(math.radians(90), 0, 0))
    cylinder("FRAME_right_rail", 0.045, 2.70, (pole_x, -0.30, 4.05), steel, vertices=14, rot=(math.radians(90), 0, 0))

    # Slightly pitched fabric canopy reads as a real pop-up/fair stall, with a
    # second inner layer providing subtle thickness at grazing angles.
    roof_angle = math.radians(8.5)
    box("CANOPY_left", (3.34, 2.95, 0.065), (-1.58, -0.30, 4.38), canvas, rot=(0, roof_angle, 0), bevel=0.018)
    box("CANOPY_right", (3.34, 2.95, 0.065), (1.58, -0.30, 4.38), canvas_alt, rot=(0, -roof_angle, 0), bevel=0.018)
    cylinder("CANOPY_ridge", 0.04, 2.95, (0, -0.30, 4.61), steel, vertices=14, rot=(math.radians(90), 0, 0))

    # Rear board for the contact form. The DOM form is aligned to this surface.
    box("DISPLAY_back_frame", (5.92, 0.16, 3.0), (0, back_y - 0.04, 2.38), steel, bevel=0.045)
    box("DISPLAY_back_panel", (5.62, 0.055, 2.70), (0, back_y - 0.15, 2.38), board, bevel=0.018)

    # Empty service table with textile drape falling over the front. The lower
    # branding panel is actual cardboard sitting slightly proud of the fabric.
    box("TABLE_top", (5.72, 1.12, 0.095), (0, front_y - 0.44, 1.12), table, bevel=0.035)
    box("TABLE_cloth_front", (5.76, 0.045, 1.54), (0, front_y - 1.02, 0.73), canvas_alt, bevel=0.012)
    box("TABLE_cloth_left", (0.045, 1.10, 1.50), (-2.86, front_y - 0.45, 0.75), canvas, bevel=0.012)
    box("TABLE_cloth_right", (0.045, 1.10, 1.50), (2.86, front_y - 0.45, 0.75), canvas, bevel=0.012)
    box("SIGN_bottom_cardboard", (4.72, 0.045, 0.92), (0, front_y - 1.065, 0.76), cardboard, bevel=0.022)

    # Top banner is a separate physical sign suspended from the front rail.
    box("SIGN_top_banner", (5.70, 0.055, 0.73), (0, front_y - 0.055, 3.64), canvas_alt, bevel=0.02)
    for x in (-2.55, 2.55):
        cylinder(f"SIGN_top_hanger_{x}", 0.012, 0.38, (x, front_y - 0.04, 3.99), steel, vertices=8)

    cable(
        "LGT_front_string_cable",
        [(-3.0, front_y - 0.11, 4.02), (-1.5, front_y - 0.13, 3.94), (0, front_y - 0.14, 4.01), (1.5, front_y - 0.13, 3.94), (3.0, front_y - 0.11, 4.02)],
        0.014,
        rubber,
    )
    for i, x in enumerate((-2.8, -1.4, 0, 1.4, 2.8)):
        sphere(f"LGT_stall_bulb_{i}", 0.065, (x, front_y - 0.17, 3.88 - (0.07 if i % 2 else 0)), warm)

    export("festival-stall.glb")
    export("help-desk.glb")


if __name__ == "__main__":
    stage_asset()
    team_asset()
    help_desk_asset()
    print("BREEZE_ASSETS_DONE")
