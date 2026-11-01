from pathlib import Path
from PIL import Image
import numpy as np,subprocess,json,hashlib,tempfile,os
O=Path(__file__).resolve().parents[1];tool=Path(os.environ.get('GULLYVERSE_OIDN','/workspace/gullyverse-world-concept/toolchain/oidn-2.5.1.x86_64.linux/bin/oidnDenoise'))
def denoise(src,dst):
 im=Image.open(src).convert('RGB');a=np.asarray(im,dtype=np.float32)/255
 with tempfile.TemporaryDirectory(prefix='oidn-',dir=O/'evidence')as tmp:
  p=Path(tmp)/'input.pfm';q=Path(tmp)/'output.pfm'
  with p.open('wb')as f:f.write(f'PF\n{im.width} {im.height}\n-1.0\n'.encode());np.flipud(a).tofile(f)
  result=subprocess.run([str(tool),'-d','cpu','--ldr',str(p),'--srgb','-o',str(q),'--threads','2','--maxmem','700','--quality','high','-v','1'],capture_output=True,text=True,check=True)
  with q.open('rb')as f:
   assert f.readline().strip()==b'PF';w,h=map(int,f.readline().split());scale=float(f.readline());data=np.frombuffer(f.read(),dtype='<f4'if scale<0 else'>f4').reshape((h,w,3));data=np.flipud(data)
  Image.fromarray(np.uint8(np.clip(data,0,1)*255+.5)).save(dst)
 return {'source':str(src.relative_to(O)),'output':str(dst.relative_to(O)),'rawSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'outputSHA256':hashlib.sha256(dst.read_bytes()).hexdigest(),'method':'Actual Blender Cycles LDR sRGB samples / OIDN 2.5.1 CPU high quality. Standard pixel denoising only, raw original retained.','toolLog':result.stdout[-600:]}
if __name__=='__main__':
 import sys
 src=Path(sys.argv[1]);dst=Path(sys.argv[2]);print(json.dumps(denoise(src,dst)))
