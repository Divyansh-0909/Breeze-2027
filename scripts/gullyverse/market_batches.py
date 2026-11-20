"""Group rigid opaque market props that share the same authored surface data."""
import math


def batch_key(obj, source):
    if (
        source["sourceFaces"] != "ALL" or obj.get("streetLampId")
        or obj.get("groundSurface") or obj.modifiers
        or obj.data.color_attributes or len(obj.data.polygons) > 600
    ):
        return None
    materials = tuple(obj.data.materials)
    for material in materials:
        if not material or not material.use_nodes:
            return None
        nodes = material.node_tree.nodes
        shader = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
        if shader is None or material.surface_render_method == "BLENDED":
            return None
        for name, neutral in (("Alpha", 1), ("Transmission Weight", 0)):
            socket = shader.inputs[name]
            if socket.is_linked or socket.default_value != neutral:
                return None
        for node in nodes:
            if node.type not in {
                "BSDF_PRINCIPLED", "OUTPUT_MATERIAL", "TEX_IMAGE", "NORMAL_MAP",
                "TEX_COORD", "UVMAP", "RGB", "VALUE", "SEPARATE_COLOR",
            }:
                return None
            if node.type == "TEX_COORD" and any(output.is_linked for output in node.outputs if output.name != "UV"):
                return None
    if not materials:
        return None
    # Keep material groups local so frustum culling still rejects distant bays.
    return (
        math.floor(obj.matrix_world.translation.y / 9),
        obj.matrix_world.translation.x < 0,
        tuple(material.name for material in materials),
        tuple((uv.name, uv.active_render) for uv in obj.data.uv_layers),
    )
