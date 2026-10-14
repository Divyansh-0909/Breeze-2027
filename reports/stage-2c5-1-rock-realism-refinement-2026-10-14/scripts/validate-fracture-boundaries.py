"""Inspect actual glTF fracture-region topology, without modifying exports."""
import bpy,bmesh,json
from pathlib import Path
ROOT=Path.cwd();rows=[]
for family in['quarry-foundation','quarry-foundation-refined']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'public/models/gullyverse'/family/'foundation-lod0.glb'))
    for index in[13,14,15]:
        ob=bpy.data.objects[f'Foundation_Wall_{index:02d}_LOD0'];bm=bmesh.new();bm.from_mesh(ob.data)
        # Weld attribute-only duplicates, so UV/tangent splitting does not
        # masquerade as a physical crack. This affects only the validation copy.
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5)
        boundary=[e for e in bm.edges if e.is_boundary]
        seen=set();loops=[]
        for edge in boundary:
            if edge in seen:continue
            stack=[edge];component=set()
            while stack:
                e=stack.pop()
                if e in component:continue
                component.add(e)
                for v in e.verts:stack.extend(q for q in v.link_edges if q.is_boundary and q not in component)
            seen|=component;loops.append(component)
        degreeBad=sum(sum(e.is_boundary for e in v.link_edges)!=2 for v in bm.verts if any(e.is_boundary for e in v.link_edges))
        interior=sum(not e.is_manifold and not e.is_boundary for e in bm.edges)
        row={'asset':family,'sector':index,'boundaryComponents':len(loops),'nonManifoldInteriorEdges':interior,'boundaryDegreeErrors':degreeBad,'boundaryEdgeCount':len(boundary)}
        assert len(loops)==1 and interior==0 and degreeBad==0,row
        # A single boundary loop is the perimeter of this connected surface;
        # internal fracture holes would introduce another boundary component.
        rows.append(row);bm.free()
out={'status':'PASS','method':'Actual LOD0 runtime exports, weld only validation copies at10micrometres. Every detailed sector has one outer surface boundary and zero additional internal fracture boundary loops. No fault caps/open slits or hidden duplicated faces are introduced by the authoring field. This is not an exhaustive self-intersection proof.','rows':rows}
(ROOT/'reports/stage-2c5-1-rock-realism-refinement-2026-10-14/raw/fracture-boundary-validation.json').write_text(json.dumps(out,indent=2))
print('PASS',rows,flush=True)
