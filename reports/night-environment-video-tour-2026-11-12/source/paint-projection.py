"""Convert original world-projected graffiti coordinates and alpha compositing."""
import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath='/workspace/Breeze-2027/reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend')
conversions=json.loads((R/'evidence/export.json').read_text())['materialConversions'];records=[]
def evaluate(socket,position,normal):
 if not socket.is_linked:return socket.default_value
 link=socket.links[0];n=link.from_node;out=link.from_socket.name
 if n.type=='NEW_GEOMETRY':return position if out=='Position' else normal
 if n.type=='SEPXYZ':return evaluate(n.inputs[0],position,normal)['XYZ'.index(out)]
 if n.type=='COMBXYZ':return tuple(evaluate(i,position,normal) for i in n.inputs)
 if n.type=='TEX_IMAGE':return 1.
 if n.type=='TEX_NOISE':return .5
 if n.type=='MATH':
  a,b=[evaluate(i,position,normal) for i in list(n.inputs)[:2]]
  return {'ADD':lambda:a+b,'SUBTRACT':lambda:a-b,'MULTIPLY':lambda:a*b,'DIVIDE':lambda:a/b,'GREATER_THAN':lambda:float(a>b),'LESS_THAN':lambda:float(a<b),'ABSOLUTE':lambda:abs(a),'MAXIMUM':lambda:max(a,b),'MINIMUM':lambda:min(a,b)}[n.operation]()
 raise ValueError((n.type,n.name,out))
for row in conversions:
 if 'ART /' not in row['source']:continue
 m=bpy.data.materials.get(row['source'])
 if not m:continue
 n=m.node_tree.nodes;image_node=next((x for x in n if x.type=='TEX_IMAGE' and ('Exact source paint' in x.name or 'original' in x.image.name.lower())),None)
 if not image_node:continue
 points=[(0,0,0),(1,0,0),(0,1,0),(0,0,1)];sample=[evaluate(image_node.inputs['Vector'],p,(1,0,0)) for p in points];offset=list(sample[0])[:2];matrix=[[sample[c+1][i]-sample[0][i] for c in range(3)]+[offset[i]] for i in range(2)]
 bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');fac=bs.inputs['Base Color'].links[0].from_node.inputs[0]
 normals=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)];mask=[evaluate(fac,(0,0,0),v) for v in normals]
 base=next((x for x in n if x.type=='MIX_RGB' and x.name=='World aligned paint mixture'),None);bg=np.array(base.inputs[1].default_value[:3]) if base else np.array([.2,.22,.19]);im=image_node.image;w,h=im.size;arr=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(arr);arr=arr.reshape((-1,4));arr[:,:3]=arr[:,:3]*arr[:,3:4]+bg*(1-arr[:,3:4]);arr[:,3]=1
 # A quiet border gives CLIP-like behaviour with glTF clamp-to-edge sampling.
 a=arr.reshape((h,w,4));a[0,:,:3]=a[-1,:,:3]=bg;a[:,0,:3]=a[:,-1,:3]=bg
 out=bpy.data.images.new('WEB exact paint '+str(len(records)),width=w,height=h,alpha=False);out.pixels.foreach_set(arr.ravel());out.update();file=R/'viewer/textures'/('paint-'+str(len(records))+'.png');out.filepath_raw=str(file);out.file_format='PNG';out.save()
 records.append({'sourceMaterial':m.name,'webMaterial':row['export'],'sourceImage':im.name,'UVMatrixWorldBlender':matrix,'normalMasks':dict(zip(['+X','-X','+Y','-Y','+Z','-Z'],mask)),'compositeFile':str(file.relative_to(R)),'background':bg.tolist(),'conversion':'original world-coordinate graph evaluated as affine UV projection; original alpha composited over original metal/paint background; normal-side mask retained'})
(R/'evidence/paint-projections.json').write_text(json.dumps(records,indent=2));print('EXACT PAINT PROJECTIONS',len(records),flush=True)
