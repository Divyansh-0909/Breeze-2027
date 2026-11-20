import bpy
import json

class TEAMWALLJ_OT_step(bpy.types.Operator):
    bl_idname = 'teamwallj.step'
    bl_label = 'Change team'
    direction: bpy.props.IntProperty(default=1)

    def execute(self, context):
        controller = context.scene.objects.get('REV15J1 / Team Carousel Controller')
        if not controller:
            return {'CANCELLED'}
        order = json.loads(context.scene['carouselOrder'])
        controller['team_index'] = (int(controller['team_index']) + self.direction) % len(order)
        controller.update_tag()
        context.view_layer.update()
        return {'FINISHED'}

class TEAMWALLJ_PT_panel(bpy.types.Panel):
    bl_label = 'Team Mural / Organising Committee'
    bl_idname = 'TEAMWALLJ_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Team Wall'

    def draw(self, context):
        controller = context.scene.objects.get('REV15J1 / Team Carousel Controller')
        if not controller:
            self.layout.label(text='Select the REV15J1 scene')
            return
        order = json.loads(context.scene['carouselOrder'])
        self.layout.label(text=order[int(controller['team_index'])])
        row = self.layout.row()
        row.operator('teamwallj.step', text='Previous').direction = -1
        row.operator('teamwallj.step', text='Next').direction = 1
        self.layout.prop(controller, '["team_index"]', text='Team')

for cls in [TEAMWALLJ_OT_step, TEAMWALLJ_PT_panel]:
    try:
        bpy.utils.register_class(cls)
    except ValueError:
        pass
