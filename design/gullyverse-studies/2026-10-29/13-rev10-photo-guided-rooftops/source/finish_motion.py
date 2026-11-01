from pathlib import Path
import time,subprocess,os,json
O=Path(__file__).resolve().parents[1];m=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';env=dict(os.environ,LP_NUM_THREADS='2')
while not (O/'checkpoint/CAPTURES-DONE.json').exists():time.sleep(5)
for script in ['audit_budget.py','verify_reopen.py']:
 with (O/'evidence'/(script+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source'/script)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
for ed in ['A','B']:
 with (O/'evidence'/('walk-'+ed+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source/render_walk.py'),'--',ed],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 movie=O/('review/Rev10-'+ed+'-40s-Offline-Walk.mp4');subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','2','-i',str(O/('renders/walk-'+ed+'/%04d.png')),'-c:v','libx264','-pix_fmt','yuv420p','-crf','19',str(movie)],check=True)
 p=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(movie)]));assert float(p['format']['duration'])==40 and int(p['streams'][0]['nb_frames'])==80
(O/'checkpoint/MOTION-DONE.json').write_text(json.dumps({'status':'PASS','bothAlternativesActual40SecondRoute':True,'eightyActualFramesEachAt2fpsNotRuntimeFPS':True}));print('BOTH_MOTION_COMPLETE',flush=True)
