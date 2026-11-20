import bpy,math
from mathutils import Vector
class Batch:
 def __init__(self):self.vertices=[];self.faces=[];self.indices=[]
 def poly(self,vs,fs,material=0):
  start=len(self.vertices);self.vertices.extend(vs);self.faces.extend(tuple(start+i for i in f)for f in fs);self.indices.extend([material]*len(fs))
 def box(self,centre,size,material=0,basis=None):
  c=Vector(centre);a,b,z=basis or(Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)));w,d,h=[s/2 for s in size];vs=[tuple(c+a*x*w+b*y*d+z*k*h)for x,y,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];fs=fs if a.cross(b).dot(z)>0 else[f[::-1]for f in fs];self.poly(vs,fs,material)
 def object(self,name,collection,materials,part):
  me=bpy.data.meshes.new('REV15Z / '+name);me.from_pydata(self.vertices,[],self.faces);me.update()
  for m in materials:me.materials.append(m)
  for f,i in zip(me.polygons,self.indices):f.material_index=i
  ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob);ob['contactPart']=part;return ob
def material(name,color,rough=.8,metal=0,grain=0):
 m=bpy.data.materials.new('REV15Z / '+name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Specular IOR Level'].default_value=.22
 if grain:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=grain;n.inputs['Detail'].default_value=3;b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=.001;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m
def image_material(name,image):
 m=material(name,(.85,.83,.74),.92);m.surface_render_method='DITHERED';m.use_backface_culling=True;p=m.node_tree.nodes['Principled BSDF'];t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;t.extension='CLIP';m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(t.outputs['Alpha'],p.inputs['Alpha']);return m
def quads(name,collection,records,material,part):
 verts=[];faces=[];uvs=[]
 for points,uv in records:
  start=len(verts);verts.extend(points);faces.append(tuple(start+i for i in range(4)));uvs.extend(uv)
 me=bpy.data.meshes.new('REV15Z / '+name);me.from_pydata(verts,[],faces);me.materials.append(material);uv=me.uv_layers.new(name='UVMap')
 for f in me.polygons:
  for li in f.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 me.update();ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob);ob['contactPart']=part;return ob
