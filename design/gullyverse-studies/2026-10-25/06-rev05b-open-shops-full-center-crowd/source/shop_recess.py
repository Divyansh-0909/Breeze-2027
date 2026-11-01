"""Authorized Rev05B cavity builder. Imported by author_rev05b.py; no standalone scene mutation."""
import bpy,bmesh,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1]
SHOPS=[(-1,-25,0),(-1,-7,2),(-1,2,3),(1,-16,1),(1,-7,2)]
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
def make_recess(obj,side,center_y,ground,through=False):
    old=obj.data;points=[obj.matrix_basis@v.co for v in old.vertices]
    us=[side*p.x for p in points];vs=[p.y-center_y for p in points];zs=[p.z-ground for p in points]
    a,b=min(us),max(us);lo,hi=min(vs),max(vs);bottom,top=min(zs),max(zs)
    inner=3.125 if through else 3.1;innerbottom=.005 if through else .015;innertop=2.875 if through else 2.85;depth=b if through else 8.4
    outer=[(lo,bottom),(lo,top),(hi,top),(hi,bottom)];hole=[(-inner,innerbottom),(-inner,innertop),(inner,innertop),(inner,innerbottom)]
    raw=[(u,v,z)for u,loop in [(a,outer),(b,outer),(a,hole),(depth,hole)]for v,z in loop]
    inv=obj.matrix_basis.inverted();verts=[inv@Vector((side*u,center_y+v,ground+z))for u,v,z in raw]
    faces=[]
    for i in range(4):
        j=(i+1)%4;faces.append((i,4+i,4+j,j));faces.append((i,j,8+j,8+i));faces.append((8+i,8+j,12+j,12+i))
    if through:
        for i in range(4):j=(i+1)%4;faces.append((4+i,12+i,12+j,4+j))
    else:faces.extend([(7,6,5,4),(12,13,14,15)])
    data=bpy.data.meshes.new(old.name+'__approved_interior');data.from_pydata(verts,[],faces);data.update()
    for material in old.materials:data.materials.append(material)
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges)
    volume=bm.calc_volume(signed=True);assert volume>0
    bm.to_mesh(data);bm.free();assert not data.validate(clean_customdata=False)
    uv=data.uv_layers.new(name='UVMap')
    for polygon in data.polygons:
        normal=polygon.normal;axis=max(range(3),key=lambda i:abs(normal[i]))
        for index in polygon.loop_indices:
            p=obj.matrix_basis@data.vertices[data.loops[index].vertex_index].co
            uv.data[index].uv=((p.y*.28,p.z*.28)if axis==0 else(p.x*.28,p.z*.28)if axis==1 else(p.x*.28,p.y*.28))
    obj.data=data
    return {'object':obj.name,'oldVertices':len(old.vertices),'newVertices':len(data.vertices),'faces':len(data.polygons),'closedManifold':True,'signedVolume':volume,'throughTrim':through}
