"""Serial artifact finish after the current capture worker. Does not author/resave."""
from pathlib import Path
import subprocess,os,time,json
O=Path(__file__).resolve().parents[1]
while not (O/'checkpoint/CAPTURES-DONE.json').exists():time.sleep(5)
master=O/'source/Gullyverse-Rev09-MultiStorey-Square-C180.blend';env=dict(os.environ,LP_NUM_THREADS='2')
for edition in ['before','after']:
 with (O/'evidence'/('capture-plan-'+edition+'-full-envelope.log')).open('w')as f:
  subprocess.run(['blender','-b',str(master),'-t','2','--python-exit-code','9','--python',str(O/'source/render_square.py'),'--',edition,'01-plan'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
for script in ['validate_captures.py','build_report.py']:
 subprocess.run(['python',str(O/'source'/script)],check=True)
movie=O/'review/Rev09-Original-40s-Walk-Offline.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','2','-i',str(O/'renders/walk/%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','19',str(movie)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(movie)]));assert float(probe['format']['duration'])==40.0;assert int(probe['streams'][0]['nb_frames'])==80
(O/'evidence/walk-encoding.json').write_text(json.dumps({'status':'PASS','durationSeconds':40,'actualSourceFrames':80,'encodedFPS':2,'resolution':[480,270],'notGameplayFPS':True},indent=2))
subprocess.run(['python',str(O/'source/build_reviews.py')],check=True)
import fitz
pdfs=[]
for p in (O/'review').glob('*.pdf'):
 d=fitz.open(p);assert len(d)>0;assert all(len(x.get_text().strip())>25 for x in d);pdfs.append({'name':p.name,'pages':len(d),'bytes':p.stat().st_size})
(O/'evidence/pdf-qa.json').write_text(json.dumps({'status':'PASS','pdfs':pdfs},indent=2))
subprocess.run(['python',str(O/'source/package_checkpoint.py')],check=True)
(O/'checkpoint/REVIEWS-AND-PACKAGES-DONE.json').write_text(json.dumps({'status':'PASS','pdfs':pdfs}));print('REVIEWS_AND_PACKAGES_COMPLETE',flush=True)
