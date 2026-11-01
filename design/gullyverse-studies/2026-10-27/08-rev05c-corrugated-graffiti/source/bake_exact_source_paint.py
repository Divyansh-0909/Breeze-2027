"""Blender author-time matte refinement/bake after actual imagegen extraction trials.
Original JPEG colour, lettering and canvas remain authoritative; model RGB is never used.
"""
import bpy,numpy as np,json,hashlib
from collections import deque
from pathlib import Path
O=Path(__file__).resolve().parents[1];report=[]
for key in ['chaar-diwari','ritviz','neha-kakkar']:
 src=bpy.data.images.load(str(O/'source/originals'/f'{key}.jpeg'));w,h=src.size
 original=np.asarray(src.pixels[:],dtype=np.float32).reshape(h,w,4)
 trial=bpy.data.images.load(str(O/'source/derived'/f'{key}-extraction-trial.png'));trial.scale(w,h)
 guide=np.asarray(trial.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,3]
 rgb=original[:,:,:3]
 # Connected paper selection is deliberately NOT a global white colour key.
 # Enclosed white/silver letter highlights stay protected.
 paper=(rgb.min(2)>.90)&((rgb.max(2)-rgb.min(2))<.11)
 outside=np.zeros((h,w),dtype=bool);q=deque()
 for x in range(w):
  for y in [0,h-1]:
   if paper[y,x]and not outside[y,x]:outside[y,x]=True;q.append((x,y))
 for y in range(h):
  for x in [0,w-1]:
   if paper[y,x]and not outside[y,x]:outside[y,x]=True;q.append((x,y))
 def flood(queue,seen,allowed):
  pixels=[]
  while queue:
   x,y=queue.popleft();pixels.append((x,y))
   for xx,yy in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if 0<=xx<w and 0<=yy<h and allowed[yy,xx]and not seen[yy,xx]:seen[yy,xx]=True;queue.append((xx,yy))
  return pixels
 flood(q,outside,paper)
 seen=outside.copy();negative_holes=[];protected=[]
 for y,x in zip(*np.where(paper&~seen)):
  if seen[y,x]:continue
  seen[y,x]=True;component=flood(deque([(int(x),int(y))]),seen,paper)
  ys=np.array([p[1]for p in component]);xs=np.array([p[0]for p in component]);mean=float(guide[ys,xs].mean())
  # Guide may identify genuine enclosed paper counters; never erase bright highlights merely by value.
  if len(component)>25 and mean<.05:
   outside[ys,xs]=True;negative_holes.append({'pixels':len(component),'guideAlphaMean':mean})
  else:protected.append({'pixels':len(component),'guideAlphaMean':mean})
 alpha=(~outside).astype(np.float32)
 # Author-time edge decontamination: JPEG anti-alias pixels were matted over white.
 # Limit correction to a2pixel exterior boundary; enclosed white highlights remain untouched.
 near=outside.copy()
 for _ in range(2):
  expanded=near.copy();expanded[1:]|=near[:-1];expanded[:-1]|=near[1:];expanded[:,1:]|=near[:,:-1];expanded[:,:-1]|=near[:,1:];near=expanded
 boundary=near&~outside
 recovered=np.clip((1-rgb.min(2))/.95,0,1);recovered[recovered>=.995]=1
 alpha[boundary]=recovered[boundary]
 rgba=original.copy();adjust=boundary&(alpha<1)
 rgba[adjust,:3]=np.clip((rgb[adjust]-(1-alpha[adjust,None]))/np.maximum(alpha[adjust,None],.0001),0,1)
 rgba[:,:,3]=alpha;rgba[outside,:3]=0
 out=bpy.data.images.new(key+' / exact JPEG colour + refined matte',width=w,height=h,alpha=True)
 out.colorspace_settings.name='sRGB';out.alpha_mode='STRAIGHT';out.pixels.foreach_set(rgba.ravel());out.file_format='PNG';out.filepath_raw=str(O/'source/derived'/f'{key}-paint-rgba.png');out.save()
 mask=bpy.data.images.new(key+' / paper exclusion matte',width=w,height=h,alpha=True);mask.colorspace_settings.name='Non-Color'
 ma=np.repeat(alpha[:,:,None],4,axis=2);ma[:,:,3]=1;mask.pixels.foreach_set(ma.ravel());mask.file_format='PNG';mask.filepath_raw=str(O/'source/derived'/f'{key}-paint-mask.png');mask.save()
 stats={'key':key,'width':w,'height':h,'toolForExtractionTrial':'image_gen.imagegen','finalBake':'Blender4.3.2 authoring; connected exterior-paper matte plus model-guide negative holes; original JPEG RGB copied with2pixel-boundary white-matte decontamination. Generated RGB discarded.','sourceRGBResampled':False,'sourceRGBPixelChangesInsideFullyOpaquePaint':int(np.count_nonzero((rgba[:,:,:3]!=original[:,:,:3])&(alpha[:,:,None]==1))),'decontaminatedBoundaryPixels':int(adjust.sum()),'exteriorPaperPixels':int(outside.sum()),'protectedEnclosedWhiteHighlightPixels':sum(p['pixels']for p in protected),'negativePaperHoles':negative_holes,'protectedComponents':len(protected),'paintCoveragePixels':int((alpha>0).sum()),'rgbaSHA256':hashlib.sha256(Path(out.filepath_raw).read_bytes()).hexdigest(),'maskSHA256':hashlib.sha256(Path(mask.filepath_raw).read_bytes()).hexdigest()}
 report.append(stats)
 for image in [src,trial,out,mask]:bpy.data.images.remove(image)
(O/'evidence/exact-source-matte-bake.json').write_text(json.dumps({'status':'BAKED_REQUIRES_DARK_SURFACE_REVIEW','images':report},indent=2)+'\n');print('EXACT_SOURCE_RGBA_BAKED',[(r['key'],r['paintCoveragePixels'],r['protectedEnclosedWhiteHighlightPixels'])for r in report])
