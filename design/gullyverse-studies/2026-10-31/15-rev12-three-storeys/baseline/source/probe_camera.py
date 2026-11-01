import bpy,json
p=json.load(open('/dev/shm/rev11/evidence/source-signatures.json'))['objects']['13-CONTINUOUS-STRAIGHT-WALK'];o=bpy.data.objects['13-CONTINUOUS-STRAIGHT-WALK'];print('SOURCE BASIS',p['basis']);print('NEW BASIS',[list(r)for r in o.matrix_basis]);print('ACTION',o.animation_data.action.name);print('FRAME',bpy.context.scene.frame_current)
