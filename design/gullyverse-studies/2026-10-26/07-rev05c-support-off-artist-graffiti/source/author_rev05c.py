"""Rev05C authorized local-light correction. Original art is never fabricated."""
import bpy, sys, json, hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(O/'source'))
from scene_snapshot import snapshot
BASE=O/'source/baseline/Rev05B.blend'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='8fbfbfb1c69bd0daefb5690c935c8317ed3516ab0e1af07e8a9bd371747ec5ff'
assert Path(bpy.data.filepath)==BASE
expected={f'Rev05B shop interior practical {side} {y}' for side,y in [(-1,-25),(-1,-7),(-1,2),(1,-16),(1,-7)]}
lights=[o for o in bpy.data.objects if o.type=='LIGHT' and o.name in expected]
assert len(lights)==5
for o in lights:
    assert o.data.type=='AREA' and o.data.shape=='RECTANGLE' and o.data.use_shadow and o.data.energy==45
    o.data.energy=0
    o['Rev05C_optional_support']='OFF — user decision; retained reversible editor option'
target=O/'source/Gullyverse-Rev05C-Interior-Support-Off.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
a,ea,ma,wa,ia=snapshot(BASE)
b,eb,mb,wb,ib=snapshot(target)
assert a.keys()==b.keys() and ea==eb and ma==mb and wa==wb and ia==ib
changed=[]
for n in a:
    if n in expected:
        aa=a[n].copy();bb=b[n].copy();aa.pop('dataHash');bb.pop('dataHash');assert aa==bb
        changed.append(n)
    else:assert a[n]==b[n],n
# Compare all supported light data fields, not only the generic object hash.
def light_state(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    return {o.name:{p.identifier:getattr(o.data,p.identifier)[:] if getattr(p,'is_array',False) else getattr(o.data,p.identifier) for p in o.data.bl_rna.properties if not p.is_readonly and p.type in {'BOOLEAN','INT','FLOAT','ENUM','STRING'} and p.identifier not in {'rna_type'}} for o in bpy.data.objects if o.type=='LIGHT'}
la=light_state(BASE);lb=light_state(target)
for n in la:
    if n in expected:
        assert la[n]['energy']==45 and lb[n]['energy']==0
        aa=la[n].copy();bb=lb[n].copy();aa.pop('energy');bb.pop('energy');assert aa==bb,n
    else:assert la[n]==lb[n],n
inventory=[]
for o in bpy.data.objects:
    if o.type=='MESH' and any(s in o.name.lower() for s in ['shutter','wall','plaster','building /']):
        points=[o.matrix_world@v.co for v in o.data.vertices]
        inventory.append({'name':o.name,'type':o.type,'location':list(o.location),'bounds':[[min(p[i]for p in points),max(p[i]for p in points)]for i in range(3)],'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials]})
(O/'evidence/surface-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
proof={'status':'PASS','scope':'Lighting correction only; original artist art unresolved. Not complete combined Rev05C.','beforeSHA256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'afterSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'changedOptionalLightEnergies':sorted(changed),'optionalEnergyBeforeW':45,'optionalEnergyAfterW':0,'original12LightsIdentical':True,'allOriginalMeshUVTransformsMaterialsImagesAndActionsIdentical':True,'allABCCamerasAndWorldSettingsIdentical':True,'allObjectNamesAndCountsIdentical':True,'newImages':0,'addedGeometry':0,'images':len(ib),'largeRedBannerAbsent':bpy.data.objects.get('Festival takeover banner') is None}
(O/'evidence/preservation-audit.json').write_text(json.dumps(proof,indent=2)+'\n')
print('REV05C_LIGHTS_OFF_PRESERVATION_PASS',len(changed),flush=True)
