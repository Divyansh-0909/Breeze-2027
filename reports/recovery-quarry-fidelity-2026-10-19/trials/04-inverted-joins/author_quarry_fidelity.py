"""Native-proportion continuation across the ORIGINAL 35.557m study.

The 0.9x C9 hero and original external host curves are read-only inputs. Two
different native Coastal04 formations continue the middle/upper body. Their
proportions are never normalized to a chart. No Boolean, loft or noise cliff.
Run with Blender4.3.2, from the project root.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,hashlib,sys,math
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/blender'))
import author_recovered_c9 as toolkit
import refined_foundation_geometry as foundation
SOURCE=ROOT/'assets-source/gullyverse/quarry-fidelity-correction'
OUT=ROOT/'public/models/gullyverse/quarry-fidelity-correction'
RAW=ROOT/'reports/recovery-quarry-fidelity-2026-10-19/raw'
CACHE=SOURCE/'.authoring-cache'
for p in [SOURCE,OUT,RAW,CACHE]:p.mkdir(parents=True,exist_ok=True)
START,END=311.02719558677654,346.5843803697403
MID=(START+END)/2
B,G=toolkit.B,toolkit.G
loops=toolkit.boundary_loops
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def obj(name,xyz,faces):return toolkit.mesh_object(name,[B(p)for p in xyz],faces)

def components(bm):
    remaining=set(bm.verts);groups=[]
    while remaining:
        stack=[remaining.pop()];group=set(stack)
        while stack:
            v=stack.pop()
            for e in v.link_edges:
                q=e.other_vert(v)
                if q in remaining:remaining.remove(q);group.add(q);stack.append(q)
        groups.append(group)
    return sorted(groups,key=len,reverse=True)

def crop(original,name,x0,x1,z0,z1,y0,y1):
    m=original.data.copy();bm=bmesh.new();bm.from_mesh(m)
    planes=[((x0,0,(z0+z1)/2),(1,0,-.035)),((x1,0,(z0+z1)/2),(-1,0,-.025)),
            (((x0+x1)/2,0,z0),(.017,0,1)),(((x0+x1)/2,0,z1),(-.014,0,-1)),
            (((x0+x1)/2,y0,(z0+z1)/2),(0,1,0)),(((x0+x1)/2,y1,(z0+z1)/2),(0,-1,0))]
    for point,normal in planes:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,
                              plane_co=Vector(point),plane_no=Vector(normal),clear_inner=True)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=.0005)
    groups=components(bm);discarded=[{'vertices':len(c),'spanM':float(np.linalg.norm(np.ptp(np.array([v.co[:]for v in c]),axis=0)))}for c in groups[1:]]
    if len(groups)>1:bmesh.ops.delete(bm,geom=list(set.union(*groups[1:])),context='VERTS')
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
    boundaries=loops(m);boundaries.sort(key=len,reverse=True)
    if len(boundaries)>1:
        bm=bmesh.new();bm.from_mesh(m);bm.verts.ensure_lookup_table()
        for hole in boundaries[1:]:
            pts=np.array([m.vertices[i].co[:]for i in hole]);span=float(np.linalg.norm(np.ptp(pts,axis=0)))
            print('NATIVE_CAPTURE_HOLE',name,span,len(hole),'center',pts.mean(0).tolist(),'bounds',pts.min(0).tolist(),pts.max(0).tolist(),flush=True)
            assert span<.15 and len(hole)<30,('Unsuitable large native capture hole',name,span,len(hole))
            edges=[e for e in bm.edges if e.is_boundary and all(v.index in hole for v in e.verts)]
            bmesh.ops.holes_fill(bm,edges=edges,sides=0);discarded.append({'smallCaptureHoleFilledM':span})
        bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
    assert len(loops(m))==1,('Native crop not one disk',name)
    xyz=np.array([v.co[:]for v in m.vertices]);faces=np.array([p.vertices[:]for p in m.polygons])
    high=obj(name+'_High_Native',xyz,faces);high.data.materials.clear()
    return high,{'cropNativeBounds':[xyz.min(0).tolist(),xyz.max(0).tolist()],
                 'cropDimensionsM':np.ptp(xyz,axis=0).tolist(),'highTriangles':len(faces),
                 'planes':[{'point':p,'inwardNormal':n}for p,n in planes],'discardedDisconnectedCapture':discarded}

def author_retopology(high,name,target):
    # Cut-boundary simplification is allowed for the new formation's authoring
    # retopology, before its boundary is locked for all runtime LODs. Existing
    # quarry/hero boundaries never enter this modifier.
    o=bpy.data.objects.new(name+'_Retopology',high.data.copy());bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    mod=o.modifiers.new('Native_Form_Quadric_Retopology','DECIMATE');mod.ratio=min(1,target/len(o.data.polygons));mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=.0005)
    bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
    assert len(loops(o.data))==1,'Retopology broke native cut outline'
    return o

def vertex_normals(mesh):
    ns=np.zeros((len(mesh.vertices),3))
    for loop in mesh.loops:ns[loop.vertex_index]=G(mesh.corner_normals[loop.index].vector)
    return ns

def site_arc(xyz):
    # Only a coordinate lookup for UV/crop correspondence. This never changes
    # any source position, depth, proportion or uniform transformation.
    ss=np.linspace(START-5,END+5,1501);foot=foundation.old.frame(ss)[0]
    tree=KDTree(len(ss))
    for i,p in enumerate(foot):tree.insert((p[0],p[1],0),i)
    tree.balance();s=np.array([ss[tree.find((p[0],p[2],0))[1]]for p in xyz])
    xy=xyz[:,[0,2]]
    for _ in range(4):
        f=foundation.old.frame(s)[0];t=(foundation.old.frame(s+.001)[0]-foundation.old.frame(s-.001)[0])/.002
        s+=np.clip(((xy-f)*t).sum(1)/np.maximum((t*t).sum(1),1e-12),-.15,.15)
        s=np.clip(s,START-5,END+5)
    return s

def joined_host(level):
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'))
    imported=[o for o in bpy.data.objects if o not in before]
    host_objects=[bpy.data.objects[f'Foundation_Wall_{i}_LOD{level}']for i in [14,16]]
    # Preserve the existing native0.9 hero, its current surgery and all normals.
    old=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb'))
    originals=[o for o in bpy.data.objects if o not in old];hero=next(o for o in originals if o.name.startswith(f'C9_Wall_15_LOD{level}'))
    host_objects.insert(1,hero)
    xyz=[];uvs=[];normals=[];faces=[];tags=[];lookup={}
    repeat=json.loads((ROOT/'public/models/gullyverse/recovered-c8-material/manifest.json').read_text())['approvedUVRepeat']
    hero_spec=json.loads((ROOT/'public/models/gullyverse/recovered-c9-composition/manifest.json').read_text())['LODs'][level]
    for ob in host_objects:
        m=ob.data;m.calc_loop_triangles();ns=vertex_normals(m);huv=np.zeros((len(m.vertices),2))
        for loop in m.loops:huv[loop.vertex_index]=m.uv_layers[0].data[loop.index].uv[:]
        if ob==hero:huv[:,0]+=10/repeat
        mapping={}
        for i,v in enumerate(m.vertices):
            p=G(v.co);key=tuple(p)
            if key not in lookup:lookup[key]=len(xyz);xyz.append(p);uvs.append(huv[i]);normals.append(ns[i])
            mapping[i]=lookup[key]
        a=hero_spec['retainedHostTriangles'];b=a+hero_spec['sourceTriangles']
        for p in m.polygons:
            faces.append([mapping[int(i)]for i in p.vertices]);tags.append('hero'if ob==hero and a<=p.index<b else'host')
    for q in imported+originals:bpy.data.objects.remove(q,do_unlink=True)
    xyz,faces,uvs,normals=np.array(xyz),np.array(faces),np.array(uvs),np.array(normals)
    mesh=obj('Original_Combined_Interface_'+str(level),xyz,faces)
    border=loops(mesh.data);assert len(border)==1,('Host union has internal cracks',level,list(map(len,border)))
    bpy.data.objects.remove(mesh,do_unlink=True)
    return xyz,faces,uvs,normals,np.array(tags,dtype=object),set(border[0])

def locate_and_cut(hp,hf,uvs,hn,tags,protected,source,linear,translation,name):
    sp=np.array([G(v.co)for v in source.data.vertices])@linear.T+translation
    # Stored source coordinates use Blender(B), converted back to original XYZ
    # before the one rigid+uniform native transformation below by caller.
    sf=np.array([p.vertices[:]for p in source.data.polygons]);inner=loops(source.data)[0]
    native_chart=np.column_stack([site_arc(sp),sp[:,1]])
    envelope=toolkit.hull(native_chart[inner]);chart=np.column_stack([uvs[:,0]*2,hp[:,1]])
    remove=toolkit.inside_convex(chart[hf].mean(1),envelope,.34)
    remove&=~np.isin(hf,list(protected)).any(1)
    remove&=tags!='hero'
    remove=toolkit.regular_crop(hf,remove,protected)
    retained=hf[~remove];probe=obj('Host_Cut_Probe',hp,retained)
    boundaries=loops(probe.data);holes=[q for q in boundaries if not set(q)&protected]
    bpy.data.objects.remove(probe,do_unlink=True)
    assert len(holes)==1,(name,'expected one source interface',list(map(len,boundaries)))
    xyz=np.concatenate([hp,sp]);offset=len(hp)
    joins=toolkit.bridge(holes[0],[i+offset for i in inner],xyz)
    faces=np.concatenate([retained,sf+offset,np.array(joins)])
    uv=np.concatenate([uvs,np.column_stack([native_chart[:,0]/2,sp[:,1]/2])])
    ns=np.concatenate([hn,np.zeros_like(sp)])
    newtags=np.concatenate([tags[~remove],np.full(len(sf),name,dtype=object),np.full(len(joins),'join_'+name,dtype=object)])
    assert np.all(newtags[:len(retained)]!='')
    row={'removedHostTriangles':int(remove.sum()),'sourceTriangles':len(sf),'joinTriangles':len(joins),
         'nativeWorldBounds':[sp.min(0).tolist(),sp.max(0).tolist()],
         'nativeChartBounds':[native_chart.min(0).tolist(),native_chart.max(0).tolist()]}
    return xyz,faces,uv,ns,newtags,row

def finish_geometry(name,hp,hf,uv,hn,tags,protected_positions):
    ob=obj(name,hp,hf);m=ob.data
    # Keep exact original positions/outer normals; discard only unused vertices.
    used=np.unique(hf);lookup=np.full(len(hp),-1);lookup[used]=np.arange(len(used))
    bpy.data.objects.remove(ob,do_unlink=True);hp,uv,hn=hp[used],uv[used],hn[used];hf=lookup[hf]
    ob=obj(name,hp,hf);m=ob.data
    base=m.uv_layers.new(name='Metre_Scale_UV0');repeat=json.loads((ROOT/'public/models/gullyverse/recovered-c8-material/manifest.json').read_text())['approvedUVRepeat']
    uv[:,0]-=10/repeat
    for p in m.polygons:
        puv=uv[list(p.vertices)].copy()
        if abs(np.cross(puv[1]-puv[0],puv[2]-puv[0]))<1e-8:
            xyz=hp[list(p.vertices)];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);axes=[i for i in range(3)if i!=int(np.argmax(abs(n)))];puv=xyz[:,axes]/2
        for li,coord in zip(p.loop_indices,puv):base.data[li].uv=coord
    normals=[]
    for loop in m.loops:
        v=loop.vertex_index;n=hn[v]
        normals.append(B(n)if np.linalg.norm(n)>.9 else m.vertices[v].normal[:])
    m.normals_split_custom_set(normals)
    # Smart charts for the two lower representations only. UV0 is stable.
    m.uv_layers.new(name='Geometry_Bake_UV1')
    if name.endswith('LOD0'):
        for a,b in zip(m.uv_layers[1].data,m.uv_layers[0].data):a.uv=b.uv
    else:
        bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=ob;ob.select_set(True);m.uv_layers.active_index=1
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.01,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
    # Repair actual degenerate derivative corners with physical face normals/
    # side projections, never synthetic unit tangents or double-sided rendering.
    for layer in [0,1]:
        for attempt in range(4):
            m.free_tangents();m.calc_tangents(uvmap=m.uv_layers[layer].name);bad={l.index for l in m.loops if np.linalg.norm(l.tangent[:])<.99}
            if not bad:break
            normals=[n.vector[:]for n in m.corner_normals]
            affected=[p for p in m.polygons if set(p.loop_indices)&bad]
            assert len(affected)<25,('Too many invalid frames',name,layer,len(affected))
            for p in affected:
                assert not any(tuple(hp[v])in protected_positions for v in p.vertices),'Do not repair a protected border by changing its normals'
                xyz=hp[list(p.vertices)];n=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);axes=[i for i in range(3)if i!=int(np.argmax(abs(n)))];coords=xyz[:,axes]/2
                for li,coord in zip(p.loop_indices,coords):m.uv_layers[layer].data[li].uv=coord;normals[li]=p.normal[:]
                p.use_smooth=False
            m.normals_split_custom_set(normals)
        assert not bad,('Invalid tangent frames',name,layer,len(bad))
    m.uv_layers.active_index=0;m.uv_layers[0].active_render=True
    actual={tuple(hp[i])for i in loops(m)[0]};assert actual==protected_positions,'Protected outer boundary changed'
    return ob,hp,hf,tags

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source_path=SOURCE/'licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend'
    with bpy.data.libraries.load(str(source_path),link=False)as(src,dst):dst.objects=['coastal_cliff_04_LOD0']
    original=dst.objects[0];bpy.context.scene.collection.objects.link(original)
    # Distinct, non-overlapping portions of one real capture. Each follows its
    # local excavation plane through a rigid transform instead of bending one
    # planar capture across the full curved35.6m site.
    definitions=[('Middle_South',20,33.5,1.05,8.75,-4.5,4.2,1.03,15.3,13000,320.0),
                 ('Middle_North',3,16.5,1.05,8.75,-4.8,2.7,1.03,15.3,13000,336.0),
                 ('Upper_South',-28.7,-15.4,1.4,8.85,.6,6.0,1.06,26.0,12000,320.0),
                 ('Upper_North',-43.8,-30.5,1.4,8.85,.8,7.1,1.06,26.0,12000,336.0)]
    patches=[];source_rows=[]
    for name,x0,x1,z0,z1,y0,y1,scale,height,target,center_arc in definitions:
        foot,out,_=foundation.old.frame(np.array([center_arc]));outward=np.array([out[0,0],0,out[0,1]]);tangent=np.array([-out[0,1],0,out[0,0]])
        rotation=np.column_stack([tangent,outward,[0,1,0]]);assert np.linalg.det(rotation)>.99999
        high,row=crop(original,name,x0,x1,z0,z1,y0,y1)
        xyz=np.array([G(v.co)for v in high.data.vertices]);native_origin=np.array([(x0+x1)/2,float(np.median(xyz[:,1])),(z0+z1)/2])
        vv=np.linspace(0,1,1001);wall=foundation.point(np.full_like(vv,center_arc),vv);anchor=wall[np.argmin(abs(wall[:,1]-height))]
        linear=rotation*scale;translation=anchor-linear@native_origin
        retopo=author_retopology(high,name,target)
        source_rows.append(dict(row,name=name,source='coastal_cliff_04',uniformScale=scale,
                                transformWorldYUp=np.column_stack([linear,translation]).tolist(),singularValues=np.linalg.svd(linear)[1].tolist(),
                                nativeOrigin=native_origin.tolist(),siteArcCenterM=center_arc,retopologyTriangles=len(retopo.data.polygons)))
        patches.append((name,high,retopo,linear,translation))
        for v in high.data.vertices:v.co=B(G(v.co)@linear.T+translation)
        high.name=name+'_High_World';high.hide_set(True);high.hide_render=True
    bpy.data.objects.remove(original,do_unlink=True)
    oldmaster=ROOT/'assets-source/gullyverse/quarry-scanned-composition/quarry-scanned-composition.blend'
    with bpy.data.libraries.load(str(oldmaster),link=False)as(src,dst):dst.objects=['C9_Native_High_Unique_Uniform_0_9']
    hero_high=dst.objects[0];bpy.context.scene.collection.objects.link(hero_high);hero_high.hide_render=True;hero_high.hide_set(True)
    exports=[];rows=[];interfaces=[];near_tags=None
    for level in range(3):
        hp,hf,uv,hn,tags,protected=joined_host(level);original_positions={tuple(hp[i])for i in protected}
        interfaces.append({'LOD':level,'vertices':hp[sorted(protected)].tolist(),'normals':hn[sorted(protected)].tolist()})
        patch_rows=[]
        for name,high,retopo,linear,translation in patches:
            target=[len(retopo.data.polygons),2600 if 'Middle' in name else 2400,1000][level]
            selected=toolkit.simplify_source(retopo.data,level,target)
            hp,hf,uv,hn,tags,row=locate_and_cut(hp,hf,uv,hn,tags,protected,selected,linear,translation,name)
            patch_rows.append(dict(row,name=name));bpy.data.objects.remove(selected,do_unlink=True)
        ob,hp,hf,tags=finish_geometry(f'Fidelity_Wall_15_LOD{level}',hp,hf,uv,hn,tags,original_positions)
        if level==0:near_tags=tags.tolist()
        ob.data.materials.append(bpy.data.materials.get('Borrow_C8')or bpy.data.materials.new('Borrow_C8'))
        ob.hide_set(level!=0);ob.hide_render=level!=0;exports.append(ob)
        row={'LOD':level,'triangles':len(hf),'protectedBoundaryVertices':len(original_positions),'bounds':[hp.min(0).tolist(),hp.max(0).tolist()],
             'heroTriangles':int(np.count_nonzero(tags=='hero')),'patches':patch_rows}
        rows.append(row);print('FIDELITY_LOD',json.dumps(row),flush=True)
    for _,_,retopo,_,_ in patches:bpy.data.objects.remove(retopo,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in exports:ob.hide_set(False);ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/'fidelity-region.glb'),export_format='GLB',use_selection=True,
                             export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_yup=True,export_animations=False)
    bounds=np.array(rows[0]['bounds']);spec={'version':'quarry-fidelity-correction','regionArcM':[START,END],'regionLengthM':END-START,
        'sourceModels':source_rows,'heroSourceUniformScale':.9,'heroContractDependency':'quarry-scanned-composition/composition-contract.json',
        'heroRuntimeDependencySHA256':sha(ROOT/'public/models/gullyverse/recovered-c9-composition/composition-region.glb'),
        'hostGeometrySHA256':sha(ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'),
        'replacedHostParts':['Wall_14','Wall_15','Wall_16'],'parts':[{'id':'Wall_15','nodes':[o.name for o in exports],
        'center':bounds.mean(0).tolist(),'radius':float(np.linalg.norm(bounds[1]-bounds[0])/2)}],
        'LODs':rows,'approvedTextureScale':3,'newPBRImages':0,'newGeometryBakeImages':0,
        'runtime':'fidelity-region.glb','runtimeBytes':(OUT/'fidelity-region.glb').stat().st_size,'runtimeSHA256':sha(OUT/'fidelity-region.glb'),
        'privateOnly':True,'publicDefaultChanged':False,'collisionChanged':False,'lightingChanged':False,
        'method':'Different measured native scanned formations, uniform rigid transforms, actual host topology surgery and explicit oriented 3D stitches. No chart stretching, Boolean, displacement/noise cliff or full-world copy.'}
    text=bpy.data.texts.new('QUARRY_FIDELITY_CONTRACT');text.write(json.dumps(spec,indent=2));tagtext=bpy.data.texts.new('NEAR_FACE_SOURCE_TAGS');tagtext.write(json.dumps(near_tags))
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.ops.wm.save_as_mainfile(filepath=str(CACHE/'fidelity-unbaked.blend'))
    for p in [OUT/'manifest.json',SOURCE/'composition-contract.json']:p.write_text(json.dumps(spec,indent=2)+'\n')
    (SOURCE/'protected-interfaces.json').write_text(json.dumps(interfaces,indent=2)+'\n')
    (RAW/'authoring-native-composition.json').write_text(json.dumps(spec,indent=2)+'\n')
    print('FIDELITY_NATIVE_AUTHOR_COMPLETE',spec['runtimeBytes'],flush=True)

if __name__=='__main__':main()
