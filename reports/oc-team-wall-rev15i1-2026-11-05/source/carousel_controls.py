import bpy
class OCWIDE_OT_step(bpy.types.Operator):
 bl_idname='ocwide.step';bl_label='Change team'
 direction:bpy.props.IntProperty(default=1)
 def execute(self,context):
  c=context.scene.objects.get('REV15I1 / Team Carousel Controller')
  if not c:return {'CANCELLED'}
  c['team_index']=(int(c['team_index'])+self.direction)%9;c.update_tag();context.view_layer.update();return {'FINISHED'}
class OCWIDE_PT_panel(bpy.types.Panel):
 bl_label='Team Carousel / OC Names and Positions';bl_idname='OCWIDE_PT_panel';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Team Wall'
 def draw(self,context):
  c=context.scene.objects.get('REV15I1 / Team Carousel Controller')
  if not c:self.layout.label(text='Select REV15I scene');return
  import json
  order=json.loads(context.scene['carouselOrder']);self.layout.label(text=order[int(c['team_index'])]);r=self.layout.row();r.operator('ocwide.step',text='Previous').direction=-1;r.operator('ocwide.step',text='Next').direction=1;self.layout.prop(c,'["team_index"]',text='Team')
for cls in [OCWIDE_OT_step,OCWIDE_PT_panel]:
 try:bpy.utils.register_class(cls)
 except ValueError:pass
