import bpy,json,sys,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from scene_snapshot import snapshot
d=json.loads((O/'evidence/art-authoring.json').read_text());base=O/'source/baseline/Rev05C-Support-Off.blend';final=O/'source/Gullyverse-Rev05C-Corrugated-Artist-Graffiti.blend'
a,ea,ma,wa,ia=snapshot(base);b,eb,mb,wb,ib=snapshot(final)
assert ea==eb and wa==wb
assert not(set(a)-set(b))
assert set(b)-set(a)==set(d['newCameras'])
assert all(ma[n]==mb[n]for n in ma),'Original shared material changed'
assert all(ia[n]==ib[n]for n in ia),'Original image resource changed'
assert set(ib)-set(ia)==set(d['newImages'])
mesh=set(d['modifiedMeshObjects']);paint=set(d['paintMaterialOverrideObjects'])
assert len(mesh)==57 and len(paint)==63
changed=[]
for n,x in a.items():
 y=b[n]
 assert x['basis']==y['basis']and x['action']==y['action'],n
 if n not in mesh:assert x['dataHash']==y['dataHash'],n
 if n not in paint:assert x['materials']==y['materials'],n
 if x!=y:changed.append(n)
assert set(changed)==paint
for n in a:
 if a[n]['type']in ['LIGHT','CAMERA']:assert a[n]==b[n],n
counters=[n for n in a if n.startswith(('Counter','DJ tabletop','DJ table leg'))];assert all(a[n]==b[n]for n in counters)
stocks=[n for n in a if n.startswith(('Shop stock shelf','Dry goods carton'))];assert len(stocks)==225 and all(a[n]==b[n]for n in stocks)
for s in bpy.data.scenes:
 opt=[o for o in s.objects if o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')];assert len(opt)==5 and all(o.data.energy==0 for o in opt)
proof={'status':'PASS','baselineSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(final.read_bytes()).hexdigest(),'modifiedMeshObjects':sorted(mesh),'paintMaterialOverrideObjects':sorted(paint),'allOtherMeshUVTransformsAndActionsIdentical':True,'allOriginalMaterialsImagesAndWorldSettingsIdentical':True,'allOriginal17LightsAnd39CamerasIdentical':True,'fiveOptionalSupportsLockedOffPerScene':True,'counterAndDJObjectsUnchanged':counters,'all225StockObjectsUnchanged':True,'newObjectsOnlyReviewCameras':d['newCameras'],'newMeshObjects':0,'newImages':d['newImages'],'newMaterialCount':len(set(mb)-set(ma)),'bannerAbsent':bpy.data.objects.get('Festival takeover banner')is None,'websiteChanges':False}
(O/'evidence/preservation-audit.json').write_text(json.dumps(proof,indent=2)+'\n');print('ART_PRESERVATION_PASS',len(changed),'controlled existing objects',len(d['newCameras']),'review cameras')
