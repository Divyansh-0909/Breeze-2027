# HISTORICAL INITIAL GENERATOR ONLY. Later validated edits live in author_taller.py; do not regenerate it from this helper.
from pathlib import Path
O=Path(__file__).resolve().parents[1];src=(O/'baseline/source/author_connected.py').read_text();s=src[:src.index('# Height-only duplicates')].replace('REV11','REV12')
s=s.replace("d530f164318ac4f736d43159b7eac705ca4233ac78d69fb545c2b71b950da850","b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd")
s=s.replace("source=next(s for s in bpy.data.scenes if s.get('variant')=='PHOTO A')","source=next(s for s in bpy.data.scenes if s.get('variant')=='REV11')")
s=s.replace("arch=json.loads((O/'baseline/evidence/authoring.json').read_text());old=arch['studies'][0]","old=json.loads((O/'baseline/evidence/authoring.json').read_text())")
s=s.replace("s.name='REV12 / Connected Neighborhood +7 percent'","s.name='REV12 / Three-to-Five Real Upper Storeys'")
a=s.index('specs=[');b=s.index('\nfor idx,',a)
specs="""targetLevels={'L1':3,'L2':5,'L3':4,'R1':4,'R2':3,'R3':5,'B1':4,'B2':5,'B3':4,'F1':4,'F2':4}
pitches={key:3.0 for key in targetLevels}  # Shared floor datums; 3/4/5 counts and setbacks vary the roofline.
steps={'L1':[0,.35,.9],'L2':[0,.3,.7,1.1,1.5],'L3':[0,.4,1.,1.6],'R1':[0,.35,.8,1.2],'R2':[0,.45,1.],'R3':[0,.2,.5,1.,1.5],'B1':[0,.25,.65,1.1],'B2':[0,.3,.75,1.2,1.7],'B3':[0,.4,.9,1.35],'F1':[0,.3,.75,1.25],'F2':[0,.2,.6,1.05]}
materials={'L1':lime,'L2':sage,'L3':lime,'R1':ochre,'R2':lime,'R3':sage,'B1':cement,'B2':lime,'B3':ochre,'F1':lime,'F2':sage}
specs=[(h['id'],h['edge'],*h['alongM'],h['frontM'],h['depthM'],targetLevels[h['id']],steps[h['id']],materials[h['id']],h['id']in['L2','R1','R3','B2'])for h in old['houses']]
levelRecords=[];stairRecords=[]"""
s=s[:a]+specs+s[b:]
s=s.replace("width=hi-lo;center=(lo+hi)/2;half=width/2;zone=label","width=hi-lo;center=(lo+hi)/2;half=width/2;zone=label;pitch=pitches[label];cu=width*.26;su0,su1=cu-1.1,cu+1.1;sd0,sd1=depth-4.2,depth-.7")
s=s.replace("'stepped exposed terrace roof'}","'stepped exposed terrace roof','stair core side wall','stair core rear wall','stair core front partition','stair headroom side','stair headroom rear','stair headroom front','stair headroom lintel','stair headroom roof'}")
s=s.replace("(7.20+lev*3,3.0,offsets[lev])","(7.20+lev*pitch,pitch,offsets[lev])")
old="B('connected floor structural slab',0,(off+depth)/2,fl-.10,width,depth-off,.20,roof)"
new="""# A real stair opening is left in every elevated plate; no flights end below a solid slab.
  def plate(name,z,dd0,dd1,thick):
   if lev==0:
    B(name,0,(dd0+dd1)/2,z,width,dd1-dd0,thick,roof);return
   for u0,u1,d0,d1 in[(-half,su0,dd0,dd1),(su1,half,dd0,dd1),(su0,su1,dd0,sd0),(su0,su1,sd1,dd1)]:
    if u1-u0>.001 and d1-d0>.001:B(name,(u0+u1)/2,(d0+d1)/2,z,u1-u0,d1-d0,thick,roof)
  plate('connected floor structural slab',fl-.10,off,depth,.20)
  # Supported double-return stair: 16 risers, real intermediate/upper landings, side bearing walls.
  for uu in[su0-.075,su1+.075]:B('stair core side wall',uu,(sd0+sd1)/2,fl+fh/2,.15,sd1-sd0,fh,plaster)
  B('stair core rear wall',cu,sd1+.075,fl+fh/2,2.5,.15,fh,plaster)
  for uu in[cu-.85,cu+.85]:B('stair core front partition',uu,sd0-.075,fl+fh/2,.70,.15,fh,plaster)
  B('stair core front partition',cu,sd0-.075,fl+(2.10+fh)/2,1.10,.15,fh-2.10,plaster)
  B('stair access door',cu,sd0+.02,fl+1.06,.88,.06,2.04,timber,False)
  rise=fh/16
  for k in range(1,9):
   zz=fl+k*rise;B('lower return stair tread',cu-.55,sd0+.75+(k-.5)*.25,(fl+zz)/2,1.1,.25,zz-fl,cement,False)
   zz=fl+fh/2+k*rise;basez=fl+fh/2-.12;B('upper return stair tread',cu+.55,sd0+2.75-(k-.5)*.25,(basez+zz)/2,1.1,.25,zz-basez,cement,False)
  B('intermediate stair landing',cu,sd1-.375,fl+fh/2-.10,2.2,.75,.20,cement,False)
  B('upper stair landing',cu,sd0+.375,fl+fh-.10,2.2,.75,.20,cement,False)
  stairRecords.append({'parcel':label,'fromZ':fl,'toZ':fl+fh,'risers':16,'riseM':rise,'treadM':.25,'flightWidthM':1.1,'landingDepthM':.75,'wellLocalBounds':[su0,su1,sd0,sd1],'clearPlateOpening':lev>0,'notPublicNavigation':True})"""
assert old in s;s=s.replace(old,new)
s=s.replace("door=j==0 or (gallery and j==count-1)","door=(j==0 and (not upper or lev==2 or lev==levels+1 or gallery))or(gallery and j==len(centers)-1)")
needle="zs=sorted({fl,fl+fh,*[z for r in openings for z in r[2:4]]})"
s=s.replace(needle,"levelRecords.append({'parcel':label,'floorZ':fl,'pitchM':fh,'upperResidential':upper,'levelAboveCourt':lev-1 if upper else None,'frontOffsetM':off,'openings':[{'localU':(aa+bb)/2,'widthM':bb-aa,'bottomZ':zz0,'topZ':zz1,'isDoor':door}for aa,bb,zz0,zz1,door in openings]})\n  "+needle)
needle="R('door pull',(u+.28,off+inset-.08,mid-.10),(u+.28,off+inset-.08,mid+.10),.012,zinc)"
s=s.replace(needle,needle+"""
    if upper and not gallery and lev==levels+1:
     bw=ww+.85;B('individual domestic balcony slab',u,off-.45,fl-.03,bw,1.20,.20,cement,False)
     rail(u-bw/2,u+bw/2,off-.99,fl+.07)
     for du in[-bw/2,bw/2]:
      R('balcony side guard',(u+du,off-.99,fl+1.11),(u+du,off+.02,fl+1.11),.025,steel)
      R('balcony bearing post',(u+du,off-.99,fl+.07),(u+du,off-.99,fl+1.11),.025,steel)
      B('balcony knee support',u+du*.8,off-.35,fl-.27,.12,.90,.32,cement,False)""")
s=s.replace("top=7.2+levels*3\n B('joined final roof slab',0,(offsets[-1]+depth)/2,top+.11,width,depth-offsets[-1],.22,roof)","top=7.2+levels*pitch\n plate('joined final roof slab',top+.11,offsets[-1],depth,.22)\n # Extend the last landing to the roof finish, not an unconnected suspended stair.\n B('roof arrival landing',cu,sd0+.375,top+.11,2.2,.75,.22,cement,False)")
a=s.index(' if idx in[1,3,7,10]:');b=s.index(' # Vertical pipe begins',a)
head=""" # Roof stair headhouse is explicitly SECONDARY and NEVER a counted residential storey.
 hu=cu;hd=(sd0+sd1)/2;roofbase=top+.22
 for uu in[su0-.075,su1+.075]:B('stair headroom side',uu,hd,roofbase+1.20,.15,sd1-sd0+.3,2.40,plaster)
 B('stair headroom rear',cu,sd1+.075,roofbase+1.20,2.5,.15,2.40,plaster)
 for uu in[cu-.85,cu+.85]:B('stair headroom front',uu,sd0-.075,roofbase+1.20,.70,.15,2.40,plaster)
 B('stair headroom lintel',cu,sd0-.075,roofbase+2.25,1.10,.15,.30,plaster)
 B('stair headroom roof',cu,hd,roofbase+2.48,2.65,sd1-sd0+.5,.16,roof)
 B('roof stair door',cu,sd0+.02,roofbase+1.06,.88,.06,2.04,timber,False)
"""
s=s[:a]+head+s[b:]
s=s.replace("'floorToFloorUpperM':3.0","'floorToFloorUpperM':pitch")
s+= """
# No actor is rescaled here: the exact Rev11 H07 objects are shared, not copied or multiplied again.
actors=next(r for r in old['crowdVariants']if r['variant']=='REV11')['actors']
assert len(actors)==180 and all(s.objects.get(n)==source.objects[n]for a in actors for n in a['objects'])
s['proposalOnly']=True;s['selectedByUser']=False;s['crowdHeightFactorFromOriginal']=1.07;s['newScalingApplied']=False;s['sourceIdentity']='REV11 connected shell, hard three-plus occupied courtyard storeys'
bpy.context.window.scene=s;s.camera=source.camera;s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();dest=O/'source/Gullyverse-Rev12-Three-Plus-Storeys.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
result={'status':'AUTHORED_PENDING_INDEPENDENT_STOREY_QA_AND_USER_REVIEW','baselineSHA256':'b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd','masterSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'masterBytes':dest.stat().st_size,'newMeshes':new,'removedOnlyFromNewScene':old['newMeshes'],'houses':houses,'structuralParts':solid,'detailParts':parts,'levels':levelRecords,'stairs':stairRecords,'targetLevels':targetLevels,'sourceCrowdActorsShared':actors,'crowdHeightFactorFromOriginal':1.07,'additionalCrowdScaling':False,'original19ScenesPreserved':True,'newMaterialImageLightOwners':0,'floorScreenArtRegistryUnchanged':True,'secondaryRoofHeadhousesExcludedFromCount':True}
(O/'evidence/authoring.json').write_text(json.dumps(result,indent=2,default=lambda v:list(v)));print('REV12_AUTHORED',result['masterSHA256'],result['masterBytes'],flush=True)
"""
(O/'source/author_taller.py').write_text(s)
import ast;ast.parse(s);print('AUTHOR_SOURCE_READY',len(s))
