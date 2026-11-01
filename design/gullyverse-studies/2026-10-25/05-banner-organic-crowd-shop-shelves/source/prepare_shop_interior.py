"""Prepared narrow shelf/interior correction; execution requires the pending user exception."""
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
    inner=3.125 if through else 3.1;innerbottom=.005 if through else .015;innertop=2.875 if through else 2.85;depth=b if through else 7.8
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
def main():
    if '--allow-interior-recesses'not in sys.argv:raise RuntimeError('Do not execute until the user answers the explicit shop-interior exception question.')
    records=[];counter_before={o.name:[list(r)for r in o.matrix_basis]for o in bpy.data.objects if o.name.startswith(('Counter','DJ tabletop','DJ table leg'))}
    objects=list(bpy.data.objects);shelves=[o for o in objects if o.name.startswith('Shop stock shelf')];items=[o for o in objects if o.name.startswith('Dry goods carton')]
    assert len(shelves)==45 and len(items)==180
    moved=[]
    for side,center_y,index in SHOPS:
        ground=floor(center_y);building=bpy.data.objects[f'Building / {side} / {index}']
        recess=min([o for o in objects if o.name.startswith('Shop recess')and o.location.x*side>0],key=lambda o:abs(o.location.y-center_y))
        back=min([o for o in objects if o.name.startswith('Shop warm interior')and o.location.x*side>0],key=lambda o:abs(o.location.y-center_y))
        records.append(make_recess(building,side,center_y,ground));records.append(make_recess(recess,side,center_y,ground,True))
        back_old=[list(r)for r in back.matrix_basis];back.location.x=side*7.72
        records.append({'object':back.name,'oldBasis':back_old,'newBasis':[list(r)for r in back.matrix_basis],'existingBackLiningSetInside':True})
        for bank,(delta_y,depth,wall)in enumerate([(-2.3,4.95,-1),(0,6.75,-1),(2.3,5.85,1)]):
            old_y=center_y+delta_y;stock=[o for o in shelves if o.location.x*side>0 and abs(o.location.y-old_y)<.01]
            assert len(stock)==3
            cargo=[o for o in items if o.location.x*side>0 and abs(o.location.y-old_y)<.71]
            assert len(cargo)==12
            pivot=Vector((side*3.83,old_y,ground));new=Vector((side*depth,center_y+wall*2.78,ground))
            transform=Matrix.Translation(new)@Matrix.Rotation(side*wall*math.pi/2,4,'Z')@Matrix.Translation(-pivot)
            for obj in stock+cargo:
                before=obj.matrix_basis.copy();obj.matrix_basis=transform@before
                moved.append({'object':obj.name,'shop':[side,center_y],'bank':bank,'before':[list(r)for r in before],'after':[list(r)for r in obj.matrix_basis]})
    assert len(moved)==225
    for name,matrix in counter_before.items():assert [list(r)for r in bpy.data.objects[name].matrix_basis]==matrix
    bpy.context.preferences.filepaths.save_version=0
    final=O/'source/Gullyverse-Banner-Organic-Crowd-Interior-Shelves.blend';bpy.ops.wm.save_as_mainfile(filepath=str(final),compress=True)
    (O/'evidence/shelf-interior-authoring.json').write_text(json.dumps({'status':'APPLIED_AFTER_USER_EXCEPTION','architecture':records,'shelfAndItemTransforms':moved,'allCountersAndDJTablesIdentical':True,'counterMatrices':counter_before,'modifiedExteriorDimensions':False,'addedLights':False,'shaderDefinitionsChanged':False,'finalMasterSHA256':hashlib.sha256(final.read_bytes()).hexdigest()},indent=2)+'\n')
if __name__=='__main__':main()
