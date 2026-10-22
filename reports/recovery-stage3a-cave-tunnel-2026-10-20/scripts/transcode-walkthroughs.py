"""Phone-readable H.264 copies; retain original browser WebM and timing."""
from pathlib import Path
import subprocess,json,hashlib
R=Path('reports/recovery-stage3a-cave-tunnel-2026-10-20');rows=[]
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(p)]))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
for name in ['visitor-journey','automatic-lod-inspection']:
 src=R/'videos'/(name+'.webm');dst=R/'videos'/(name+'.mp4');assert src.is_file()and not dst.exists()
 log=R/'raw'/(name+'-transcode.log')
 with log.open('w')as f:subprocess.run(['ffmpeg','-nostdin','-i',str(src),'-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart','-threads','2','-an',str(dst)],stdout=f,stderr=subprocess.STDOUT,check=True)
 a=probe(src);b=probe(dst);delta=abs(float(a['format']['duration'])-float(b['format']['duration']));assert delta<.1
 assert(a['streams'][0]['width'],a['streams'][0]['height'])==(b['streams'][0]['width'],b['streams'][0]['height'])
 rows.append({'name':name,'originalSHA256':sha(src),'mp4SHA256':sha(dst),'mp4Bytes':dst.stat().st_size,'durationDifferenceSeconds':delta,'originalDurationSeconds':a['format']['duration'],'mp4DurationSeconds':b['format']['duration'],'dimensions':[b['streams'][0]['width'],b['streams'][0]['height']],'codec':b['streams'][0]['codec_name'],'speedOrFPSOverride':False,'audio':'Browser recorder does not capture audio; original playback is verified separately by browser state/time assertions.'})
(R/'raw/walkthrough-encoding.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
