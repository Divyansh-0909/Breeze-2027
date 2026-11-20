from pathlib import Path
import json,subprocess,time,hashlib,tempfile,os,fcntl,shutil
R=Path(__file__).resolve().parents[1];record=json.loads((R/'evidence/recording.json').read_text());assert record['status']=='PASS' and record['frames']==1140
src=R/'video/Night-Environment-Tour-Source10fps.mp4';final=R/'video/Breeze-Night-Environment-Full-Tour-2026-11-12.mp4'
lock=(R/'evidence/encode.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
fd,name=tempfile.mkstemp(prefix='delivery-candidate-',suffix='.mp4',dir=R/'video');os.close(fd);out=Path(name)
job=str(os.getpid());progress=R/f'evidence/delivery-encode-progress-{job}.txt';encode_log=R/f'evidence/delivery-encode-{job}.log'
cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(src),'-vf','tpad=stop_mode=clone:stop_duration=0.3,framerate=fps=24:interp_start=0:interp_end=255:scene=8:flags=scene_change_detect','-t','114','-an','-c:v','libx264','-preset','veryfast','-crf','21','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart','-metadata','title=Breeze 2027 - Full Night Environment Camera Tour','-metadata','comment=Private scene preview. Offline 10 FPS camera renders with 24 FPS temporally interpolated delivery. Not a live website FPS measurement.','-progress',str(progress),str(out)]
(R/'evidence/delivery-encode-command.json').write_text(json.dumps({'command':cmd,'scope':'Offline camera-video temporal frame interpolation and encoding only'},indent=2)+'\n');t=time.monotonic()
with encode_log.open('w') as f:subprocess.run(cmd,check=True,stdout=f,stderr=subprocess.STDOUT)
pr=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)],capture_output=True,text=True,check=True);assert not pr.stderr.strip(),pr.stderr;probe=json.loads(pr.stdout);video=[s for s in probe['streams'] if s['codec_type']=='video'];assert len(video)==1 and len(probe['streams'])==1
s=video[0];assert s.get('level',-1)>=0;assert s['width']==1280 and s['height']==720 and s['avg_frame_rate']=='24/1' and int(s['nb_frames'])==2736 and abs(float(s['duration'])-114)<.05
with (R/'evidence/video-full-decode.log').open('w') as f:subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-err_detect','explode','-i',str(out),'-f','null','-'],check=True,stdout=f,stderr=subprocess.STDOUT)
assert not (R/'evidence/video-full-decode.log').read_text().strip();head=out.read_bytes()[:100000];assert 0<=head.find(b'moov')<head.find(b'mdat')
os.replace(out,final);out=final;shutil.copyfile(progress,R/'evidence/delivery-encode-progress.txt');shutil.copyfile(encode_log,R/'evidence/delivery-encode.log')
proof={'status':'PASS','seconds':time.monotonic()-t,'sourceFrames':record['frames'],'sourceRenderFPS':10,'deliveryFPS':24,'interpolated':True,'duration':114,'frames':2736,'width':1280,'height':720,'codec':s['codec_name'],'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'fullDecode':'PASS','fastStart':True,'probe':probe}
(R/'evidence/video-validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='probe'}),flush=True)
