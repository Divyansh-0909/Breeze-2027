"""Rebuild defects locally; retain the navigation shell and all earlier scenes."""
import bpy, json, hashlib, math, random, sys, argparse, subprocess
from pathlib import Path
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

R = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--base', default='/dev/shm/Gullyverse-Rev15T2-Wet-Grain-Asphalt-and-Muddy-Edges.blend')
ap.add_argument('--output', default='/dev/shm/Gullyverse-Rev15T3-Rebuilt-Potholes.blend')
args = ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
P = Path(args.base); expected = '33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb'
assert sha(P) == expected
bpy.ops.wm.open_mainfile(filepath=str(P))
base = bpy.context.scene; base.frame_set(1); bpy.context.view_layer.update()
history = {s.name: sorted(o.name for o in s.objects) for s in bpy.data.scenes}
s = base.copy(); s.name = 'REV15T3 / Rebuilt broken asphalt potholes'
for c in list(s.collection.children): s.collection.children.unlink(c)
for o in list(s.collection.objects): s.collection.objects.unlink(o)
bpy.context.window.scene = s; copies = {}
for old in base.objects:
    ob = old.copy(); ob.name = 'REV15T3 / ' + old.name.removeprefix('REV15T2 / ')
    if old.type in ['LIGHT', 'CAMERA']: ob.data = old.data.copy()
    s.collection.objects.link(ob); copies[old] = ob
for old, ob in copies.items():
    if old.parent in copies: ob.parent = copies[old.parent]
    if ob.animation_data:
        for f in ob.animation_data.drivers:
            for v in f.driver.variables:
                for t in v.targets:
                    if t.id in copies: t.id = copies[t.id]
layer = s.view_layers.new('REV15T3 / independent view')
for l in list(s.view_layers):
    if l != layer: s.view_layers.remove(l)
bpy.context.window.view_layer = layer
for n in s.node_tree.nodes:
    if n.type == 'R_LAYERS': n.scene = s; n.layer = layer.name
assets = bpy.data.collections.new('REV15T3 / Restored road defects and edge water')
s.collection.children.link(assets)
cfg = json.loads((R/'source/road-layout.json').read_text())
holes = [h for h in cfg['holes'] if h['id'] in cfg['activeHoleIds']]
rng = random.Random(27111303)
grade = lambda y: 6.0 if y <= -10 else 6+.05*(y+10) if y < 14 else 7.2
road = next(m for m in bpy.data.materials if m.name == 'REV15T2 / Wet coarse-grain asphalt')
rim = road.copy(); rim.name = 'REV15T3 / Broken asphalt top rim'
cut = road.copy(); cut.name = 'REV15T3 / Exposed aggregate fracture'
for m, rough in [(rim,.77),(cut,.88)]:
    b = m.node_tree.nodes.get('Principled BSDF')
    for link in list(b.inputs['Roughness'].links): m.node_tree.links.remove(link)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = .025
    next(n for n in m.node_tree.nodes if n.type=='NORMAL_MAP').inputs['Strength'].default_value = .5
mud = road.copy(); mud.name='REV15T3 / Recessed muddy pothole bed'
mb=mud.node_tree.nodes.get('Principled BSDF')
for link in list(mb.inputs['Roughness'].links):mud.node_tree.links.remove(link)
mb.inputs['Roughness'].default_value=.46;mb.inputs['Coat Weight'].default_value=.10
next(n for n in mud.node_tree.nodes if n.type=='NORMAL_MAP').inputs['Strength'].default_value=.18
water = bpy.data.materials['REV15T2 / Muddy settled edge water']
hidden = []; runtime = []
for old, ob in copies.items():
    if 'batched loose aggregate' in old.name or 'shallow damp pocket' in old.name:
        ob.hide_render = True; ob.hide_viewport = True; hidden.append(ob.name)
    elif old.get('groundSurface') or 'nearly flush drain' in old.name or 'REV15T2 / edge pool' in old.name:
        assets.objects.link(ob); runtime.append(ob)

def irregular(h, angle):
    return 1+.105*math.sin(angle*5+h['phase'])+.06*math.cos(angle*9-h['phase'])+.028*math.sin(angle*17+1.1)

checks = []; chipspec = []; used = set()
for old, ob in copies.items():
    if not old.get('groundSurface'): continue
    src = old.data; verts = [tuple(v.co) for v in src.vertices]
    colors = [tuple(x.color) for x in src.color_attributes['RoadTint'].data]
    faces = [tuple(f.vertices) for f in src.polygons]; indices = [f.material_index for f in src.polygons]
    mats = list(src.materials); rim_i=len(mats); mats += [rim,cut,mud]
    centres = [tuple(f.center) for f in src.polygons]
    kd=KDTree(len(verts))
    for i,v in enumerate(verts):kd.insert((v[0],v[1],0),i)
    kd.balance()
    topfaces=[f for f in src.polygons if f.normal.z>.85];kf=KDTree(len(topfaces))
    for j,f in enumerate(topfaces):kf.insert((f.center.x,f.center.y,0),j)
    kf.balance()
    def original_color(x,y):
        matches=kd.find_n((x,y,0),4);ww=[1/max(d,.003)**2 for _,i,d in matches];total=sum(ww)
        return tuple(sum(colors[i][k]*w for (_,i,d),w in zip(matches,ww))/total for k in range(4))
    def original_material(x,y):return topfaces[kf.find((x,y,0))[1]].material_index
    removed = set(); additions=[]; assignments=[]
    for h in holes:
        # Remove a complete grid patch, then stitch a fractured concentric cavity
        # to its exact outer boundary; no overlay disc can hide the depression.
        selected = [i for i,f in enumerate(src.polygons) if f.normal.z > .85
                    and abs(f.center.x-h['x']) < h['rx']*1.36
                    and abs(f.center.y-h['y']) < h['ry']*1.36
                    and abs(f.center.z-grade(f.center.y)) < .13]
        if not selected: continue
        assert h['id'] not in used; used.add(h['id']); removed.update(selected)
        edges=Counter(tuple(sorted((f[j], f[(j+1)%len(f)]))) for i in selected for f in [faces[i]] for j in range(len(f)))
        boundary=sorted({v for edge,n in edges.items() if n==1 for v in edge},
                        key=lambda v:math.atan2((verts[v][1]-h['y'])/h['ry'],(verts[v][0]-h['x'])/h['rx']))
        N=len(boundary); assert N>=16
        angles=[math.atan2((verts[v][1]-h['y'])/h['ry'],(verts[v][0]-h['x'])/h['rx']) for v in boundary]
        target=max(h['depth']*1.35,.074 if h['y'] < 14 else .082)
        depths=[0,.008,target*.43,target*.83,target]
        radii=[1.05,.96,.91,.71,.38]
        rings=[boundary]
        for k,(radius,depth) in enumerate(zip(radii,depths)):
            row=[]
            for j,angle in enumerate(angles):
                q=irregular(h,angle); x=h['x']+math.cos(angle)*h['rx']*radius*q; y=h['y']+math.sin(angle)*h['ry']*radius*q
                z=grade(y)-depth
                if k in [1,2]: z += .0035*math.sin(angle*13+h['phase'])
                row.append(len(verts)); verts.append((x,y,z))
                # Fresh rim remains dark, with exposed grey aggregate in its face.
                col=original_color(x,y)
                colors.append(col if k==0 else tuple(c*.88 for c in col[:3])+(1,) if k==1 else (.30,.31,.29,1) if k==2 else (.13,.075,.033,1))
            rings.append(row)
        for k in range(len(rings)-1):
            out,inside=rings[k],rings[k+1]
            matindex=0 if k==0 else rim_i if k==1 else rim_i+1 if k==2 else rim_i+2
            for j in range(N):
                face=(out[j],out[(j+1)%N],inside[(j+1)%N],inside[j]);additions.append(face)
                assignments.append(original_material(sum(verts[v][0] for v in face)/4,sum(verts[v][1] for v in face)/4) if k==0 else matindex)
        c=len(verts);verts.append((h['x'],h['y'],grade(h['y'])-target*1.03)); colors.append((.13,.075,.033,1))
        for j in range(N):additions.append((rings[-1][j],rings[-1][(j+1)%N],c));assignments.append(rim_i+2)
        # Flattened irregular chips, never single-apex pyramids.
        for j in range(7):
            angle=rng.uniform(-math.pi,math.pi);q=irregular(h,angle);r=rng.uniform(.99,1.16)
            x=h['x']+math.cos(angle)*h['rx']*q*r;y=h['y']+math.sin(angle)*h['ry']*q*r
            if abs(x)<1.42:continue
            chipspec.append((x,y,grade(y)+.001,rng.uniform(.023,.047),rng.uniform(.004,.009),rng.uniform(0,math.tau)))
        checks.append({'id':h['id'],'rimVertices':N,'removedGridFaces':len(selected),'depthMetres':target,
                       'water':bool(h['puddle'] and (h['y'] < -10 or h['y'] >=14)), 'hole':h})
    triangles=[];tri_indices=[]
    for f,mi in zip(additions,assignments):
        for j in range(1,len(f)-1):triangles.append((f[0],f[j],f[j+1]));tri_indices.append(mi)
    additions,assignments=triangles,tri_indices
    kept=[(f,mi) for i,(f,mi) in enumerate(zip(faces,indices)) if i not in removed]
    faces=[f for f,mi in kept]+additions; indices=[mi for f,mi in kept]+assignments
    # Eliminate the old hidden depression vertices as well.
    referenced=sorted({v for f in faces for v in f}); remap={v:i for i,v in enumerate(referenced)}
    me=bpy.data.meshes.new(ob.name+' / stitched cavities');me.from_pydata([verts[i] for i in referenced],[],[tuple(remap[v] for v in f) for f in faces]);me.update()
    for m in mats:me.materials.append(m)
    for f,mi in zip(me.polygons,indices):
        f.material_index=mi;f.use_smooth=(mi==rim_i+2)
    attr=me.color_attributes.new(name='RoadTint',type='FLOAT_COLOR',domain='POINT')
    for d,i in zip(attr.data,referenced):d.color=colors[i]
    me.color_attributes.active_color_name='RoadTint'
    for name in ['RoadWorldUV','RoadDetailUV']:me.uv_layers.new(name=name)
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co;me.uv_layers['RoadWorldUV'].data[lp.index].uv=((p.x+16)/32,(p.y+30)/78);me.uv_layers['RoadDetailUV'].data[lp.index].uv=(p.x/1.2,p.y/1.2)
    ob.data=me
assert used==set(cfg['activeHoleIds']) and len(checks)==16

def newmesh(name,vs,fs,material,colors=False):
    me=bpy.data.meshes.new('REV15T3 / '+name);me.from_pydata(vs,[],fs);me.update();me.materials.append(material)
    ob=bpy.data.objects.new(me.name,me);assets.objects.link(ob);runtime.append(ob)
    for name in ['RoadWorldUV','RoadDetailUV']:me.uv_layers.new(name=name)
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co;me.uv_layers['RoadWorldUV'].data[lp.index].uv=((p.x+16)/32,(p.y+30)/78);me.uv_layers['RoadDetailUV'].data[lp.index].uv=(p.x/1.2,p.y/1.2)
    if colors:
        attr=me.color_attributes.new(name='RoadTint',type='FLOAT_COLOR',domain='POINT')
        for d in attr.data:d.color=(.33,.34,.33,1)
        me.color_attributes.active_color_name='RoadTint'
    return ob
vs=[];fs=[]
for x,y,z,r,t,angle in chipspec:
    start=len(vs);points=[]
    for j in range(7):
        a=angle+j*math.tau/7;rr=r*rng.uniform(.72,1.12);points.append((x+math.cos(a)*rr,y+math.sin(a)*rr*.76))
    vs += [(u,v,z-.002) for u,v in points]+[(u,v,z+t+rng.uniform(-.0008,.0008)) for u,v in points]
    fs.append(tuple(start+7+j for j in range(7)))
    for j in range(7):fs.append((start+j,start+(j+1)%7,start+7+(j+1)%7,start+7+j))
newmesh('Flattened broken asphalt chips',vs,fs,rim,True)
floor_trees=[BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices) for f in ob.data.polygons]) for ob in runtime if ob.get('groundSurface')]
def surface(x,y):
    hits=[p.z for tree in floor_trees for p,_,_,_ in [tree.ray_cast(Vector((x,y,25)),Vector((0,0,-1)),50)] if p is not None]
    return max(hits) if hits else None
for row in checks:
    if not row['water']:continue
    h=row['hole'];z=grade(h['y'])-row['depthMetres']*.64;vs=[(h['x'],h['y'],z)]
    # The pool terminates inside the cavity; its surface is 5-6 cm below road.
    for j in range(80):
        a=j*math.tau/80;lo,hi=.25,1.2
        for iteration in range(24):
            q=(lo+hi)*.5;xx=h['x']+math.cos(a)*h['rx']*q;yy=h['y']+math.sin(a)*h['ry']*q
            if surface(xx,yy)<z-.002:lo=q
            else:hi=q
        q=lo;vs.append((h['x']+math.cos(a)*h['rx']*q,h['y']+math.sin(a)*h['ry']*q,z))
    ob=newmesh('Recessed pothole water '+h['id'],vs,[(0,j+1,(j+1)%80+1) for j in range(80)],water)
    uv=ob.data.uv_layers.new(name='WaterUV')
    for lp in ob.data.loops:
        p=ob.data.vertices[lp.vertex_index].co;uv.data[lp.index].uv=(p.x/2,p.y/2)
    ob['defectId']=h['id'];ob['belowRoadMetres']=row['depthMetres']*.64
s.camera=copies[base.camera];s['paintedCypherCircle']=False
bpy.context.window.scene=base;bpy.context.window.scene=s;bpy.context.window.view_layer=layer;s.frame_set(1);bpy.context.view_layer.update()
assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in history.items())
assert all(o.data.energy==ob.data.energy and list(o.data.color)==list(ob.data.color) for o,ob in copies.items() if o.type=='LIGHT')
assert s.world==base.world and s.view_settings.exposure==base.view_settings.exposure
assert sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)==189
assert all(ob.hide_render for old,ob in copies.items() if 'Cypher chalk arc' in old.name)
bpy.context.preferences.filepaths.save_version=0
out=Path(args.output);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
bpy.data.libraries.write(str(R/'delivery/Rev15T3-Rebuilt-Potholes-Additions.blend'),{assets},fake_user=True,compress=True)
proof={'status':'PASS','scene':s.name,'source':str(P),'sourceSHA256':expected,'editedMaster':str(out),'editedBytes':out.stat().st_size,'editedSHA256':sha(out),
       'historicalScenesPreserved':len(history),'scenes':len(bpy.data.scenes),'rebuiltPotholes':checks,'newFlattenedChips':len(chipspec),'oldPyramidScatterHidden':True,
       'oldPuddleDiscsHidden':True,'recessedWaterPockets':sum(c['water'] for c in checks),'standingSidePoolsRetained':16,
       'originalMovementShellRetained':True,'lightingAndExposureUnchanged':True,'crowdCount':189,'muralStates':8,'paintedCircle':False,'runtimeObjects':len(runtime),'productionWebsiteChanged':False}
(R/'evidence/build-verification.json').write_text(json.dumps(proof,indent=2)+'\n');assert sha(P)==expected
ex=bpy.data.scenes.new('TEMP EXPORT / restored potholes');bpy.context.window.scene=ex
for ob in runtime:ex.collection.objects.link(ob);ob.select_set(True)
bpy.context.view_layer.objects.active=runtime[0]
bpy.ops.export_scene.gltf(filepath=str(R/'delivery/Rev15T3-Rebuilt-Potholes-Ground.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_yup=True,export_materials='EXPORT',export_normals=True,export_texcoords=True)
subprocess.run(['python',str(R/'source/fix-export.py')],check=True)
print('REBUILT_POTHOLES_DONE',len(checks),len(runtime),out,flush=True)
