"""Filter irradiance only with pinned OIDN RTLightmap. Preserve artwork/PBR maps.
Numeric alpha is independent data; mips average linear HDR before RGBM packing.
"""
import bpy,hashlib,json,os,struct,subprocess,zlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];plan=json.loads(Path(os.environ.get('GULLYVERSE_PLAN',str(Path(__file__).with_name('export-plan.json')))).read_text());out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/plan['output'])));raw=out/'irradiance.raw.pfm';binary=Path(os.environ.get('GULLYVERSE_OIDN','/dev/shm/gullyverse-runtime-tools/oidn/oidn-2.5.1.x86_64.linux/bin/oidnDenoise'));assert binary.is_file(),'Install pinned OIDN or set GULLYVERSE_OIDN; never silently skip denoising'
def pfm(path):
 with Path(path).open('rb')as f:
  assert f.readline().strip()==b'PF';w,h=map(int,f.readline().split());scale=float(f.readline());return np.frombuffer(f.read(),dtype='<f4'if scale<0 else'>f4').reshape(h,w,3).copy()
before=pfm(raw);clean=out/'irradiance.denoised.pfm';result=subprocess.run([str(binary),'-d','cpu','-f','RTLightmap','--hdr',str(raw),'-o',str(clean),'--threads','4','--maxmem','1024','-q','high'],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
rgb=np.maximum(pfm(clean),0);assert rgb.shape==before.shape and np.isfinite(rgb).all();delta=float(np.abs(rgb-before).mean());assert delta>1e-8,'Denoiser returned input unchanged'
height,width,_=rgb.shape;image=bpy.data.images.new('Filtered irradiance only',width=width,height=height,alpha=False,float_buffer=True,is_data=True);image.colorspace_settings.name='Non-Color';rgba=np.ones((height,width,4),np.float32);rgba[...,:3]=rgb;image.pixels.foreach_set(rgba.ravel());image.filepath_raw=str(out/'lightmap.hdr');image.file_format='HDR';image.save();extent=float(2**np.ceil(np.log2(max(1,float(rgb.max())))))
def png(path,array):
 def chunk(kind,payload):return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
 h,w,_=array.shape;scanlines=b''.join(b'\x00'+row.tobytes()for row in array[::-1]);path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(scanlines,9))+chunk(b'IEND',b''))
mips=[];level=0;maximumError=0;litError=0
while True:
 alpha=np.ceil(np.clip(rgb.max(2)/extent,1/255,1)*255)/255;encoded=np.concatenate([rgb/(alpha[...,None]*extent),alpha[...,None]],2);data=np.uint8(np.clip(np.rint(encoded*255),0,255));decoded=data[...,:3]/255*(data[...,3:]/255)*extent;error=np.abs(decoded-rgb)
 if level==0:
  mask=rgb.max(2)>.01;litError=float(error[mask].mean());maximumError=float(error.max());assert litError<.001
 name='lightmap.png'if level==0 else f'lightmap.mip{level:02d}.png';png(out/name,data);mips.append(name)
 if rgb.shape[0]==1 and rgb.shape[1]==1:break
 assert rgb.shape[0]%2==0 and rgb.shape[1]%2==0;rgb=rgb.reshape(rgb.shape[0]//2,2,rgb.shape[1]//2,2,3).mean((1,3));level+=1
d=json.loads((out/'manifest.json').read_text());d['bake'].update(denoising='Intel Open Image Denoise 2.5.1 RTLightmap high CPU; irradiance only',denoiseMAE=delta,range=extent,encoding='RGBM-linear; independent numeric alpha',baselineURI='lightmap.hdr',mipmaps=mips,mipFiltering='Average denoised linear HDR before RGBM packing',RGBMRoundtripLitPixelMAE=litError,RGBMRoundtripMaxError=maximumError);(out/'manifest.json').write_text(json.dumps(d,indent=2)+'\n');proof={'status':'PASS','denoiser':'OIDN 2.5.1 RTLightmap','nonNoOpMAE':delta,'alphaIsDataNotCoverage':True,'sourceArtFiltered':False,'litPixelMAE':litError,'maximumError':maximumError,'mipCount':len(mips),'mipsComputedInLinearIrradiance':True,'rawPFMSHA256':hashlib.sha256(raw.read_bytes()).hexdigest(),'filteredPFMSHA256':hashlib.sha256(clean.read_bytes()).hexdigest()};(out/'rgbm-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print('DENOISE_AND_RGBM_PASS',json.dumps(proof))
