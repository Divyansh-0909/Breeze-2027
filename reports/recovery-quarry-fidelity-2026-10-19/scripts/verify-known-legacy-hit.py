"""Do not call the old seventh coincident terrain defect fixed by a BVH tie."""
from pathlib import Path
import json,struct,hashlib,math,numpy as np
ROOT=Path.cwd();R=ROOT/'reports/recovery-quarry-fidelity-2026-10-19';path=ROOT/'public/models/gullyverse/quarry-foundation-refined/foundation-lod1.glb'
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
data=path.read_bytes();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
ob=bpy.data.objects['Foundation_Terrain_2_1_LOD1'];tree=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices)for p in ob.data.polygons],all_triangles=True,epsilon=1e-6)
eye=np.array([0,1.72,-96]);a,b=math.radians(30),math.radians(48);d=np.array([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)])
def B(p):return Vector((p[0],-p[2],p[1]))
point,normal,face,distance=tree.ray_cast(B(eye),B(d),650);assert point is not None;dot=normal.dot(B(d));assert dot>.03
node={'name':ob.name};t=np.array([distance]);idx=0

old=json.loads((ROOT/'reports/recovery-phase3-c9-2026-10-19/raw/composition-validation.json').read_text());historical=next(x for x in old['inheritedInvertedHits']if x['eye']==[0,1.72,-96]and x['pitch']==30 and x['yaw']==48 and x['LOD']==1)
current=json.loads((R/'raw/fidelity-geometry-validation.json').read_text());hit=next(x for x in current['rays']if x['eye']==[0,1.72,-96]and x['pitch']==30 and x['yaw']==48)
start=next(x for x in json.loads((R/'raw/starting-hashes.json').read_text())if x['path']==str(path.relative_to(ROOT)));assert hashlib.sha256(data).hexdigest()==start['sha256']
result={'status':'UNCHANGED_LEGACY_DEFECT_CONFIRMED','mesh':node['name'],'eye':eye.tolist(),'pitch':30,'yaw':48,'LOD':1,'componentDistanceM':float(t[idx]),'componentNormalDotRay':dot,'originalComponentHit':historical['candidate'][1],'currentWholeSceneFirstHit':hit['candidate'][1],'assetUnchangedSHA256':start['sha256'],'explanation':'The current whole-scene BVH returns coincident front-facing Wall06 at the same distance. The original unchanged Terrain2_1 back face still exists; it is not claimed repaired. Six other inherited first-hit LOD samples remain. All seven known legacy component defects are preserved, with no new candidate hits.'}
(R/'raw/known-seventh-legacy-hit.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'raw/survey-accounting.json').write_text(json.dumps({'standardDirectionsPerScene':len(current['rays']),'standardRaycastsPerSceneAcross3LODs':len(current['rays'])*3,'targetedAdditionalLODSpecificRaysPerScene':json.loads((R/'raw/targeted-ray-cones.json').read_text())['additionalRaysPerVersion'],'currentFirstHitInheritedSamples':len(current['inheritedInvertedHits']),'knownLegacyComponentSamplesIncludingCoincidentSeventh':7,'newCandidateHits':len(current['newInvertedHits']),'fullSceneVisibility':'FAIL_INHERITED'},indent=2)+'\n');print(result)
