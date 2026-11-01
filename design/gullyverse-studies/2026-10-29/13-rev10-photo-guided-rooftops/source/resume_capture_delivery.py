"""Recover unuploaded evidence only; stream each finished bundle for backup."""
from pathlib import Path
import os,sys,subprocess,json,time,zipfile,hashlib,shutil
O=Path(__file__).resolve().parents[1];D=Path('/dev/shm/rev10/delivery');m=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';env=dict(os.environ,LP_NUM_THREADS='2');assert hashlib.sha256(m.read_bytes()).hexdigest()=='d530f164318ac4f736d43159b7eac705ca4233ac78d69fb545c2b71b950da850'
Q=O/'checkpoint/R1-upload-queue';P=O/'checkpoint/R1-progress-evidence';P.mkdir(exist_ok=True)
poses=['01-plan','02-entry-square','03-aerial','04-front','05-back','06-left-diagonal','07-right-diagonal','08-left-house','09-right-house','10-team','11-events','12-elevation','13-return-left','14-return-right','15-mobile','16-mobile-lateral','20-roof-utility','21-roof-gallery','22-street-entry','23-screen-side']
def blender(script,args,label):
 with (O/'evidence'/('R1-'+label+'.log')).open('w')as f:subprocess.run(['blender','-b',str(m),'-t','2','--python-exit-code','9','--python',str(O/'source'/script)]+args,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
def queue_zip(number,label,files):
 name=f'Rev10-R1-{number:02d}-{label}.zip';dest=D/name
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=3)as z:
  for target,p in sorted(files.items()):z.write(p,target)
 item={'name':name,'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'folder':'completion','save':str(D/('downloaded-'+name)),'payloadFiles':len(files),'archiveNumber':number}
 (Q/f'{number:02d}.json').write_text(json.dumps(item,indent=2));print('READY_FOR_VERIFIED_UPLOAD',name,flush=True)
def progress(file):shutil.copyfile(O/'evidence'/file,P/file)
for ed,number in [('A',7),('B',8)]:
 blender('render_studies.py',['--',ed]+poses,'stills-'+ed);progress('render-'+ed+'.json');files={str(p.relative_to(O)):p for p in (O/'renders'/ed).glob('*.png')};assert len(files)==20;queue_zip(number,'Proposal-'+ed+'-PNGs',files)
for ed,number in [('A',9),('B',10)]:
 blender('render_walk.py',['--',ed],'walk-'+ed);progress('render-walk-'+ed+'.json');movie=O/('review/Rev10-'+ed+'-40s-Offline-Walk.mp4')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','2','-i',str(O/('renders/walk-'+ed+'/%04d.png')),'-c:v','libx264','-pix_fmt','yuv420p','-crf','19',str(movie)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(movie)]));assert float(probe['format']['duration'])==40 and int(probe['streams'][0]['nb_frames'])==80
 files={str(p.relative_to(O)):p for p in (O/('renders/walk-'+ed)).glob('*.png')};assert len(files)==80;files[str(movie.relative_to(O))]=movie;queue_zip(number,'Proposal-'+ed+'-Actual-Walk',files)
for script in ['validate_captures.py','verify_website.py','build_report.py','build_reviews.py']:
 with (O/'evidence'/('R1-'+script+'.log')).open('w')as f:subprocess.run(['python',str(O/'source'/script)],stdout=f,stderr=subprocess.STDOUT,check=True)
# Keep the original already-uploaded 25-page PDF byte-for-byte. Companions are current.
shutil.copyfile(D/'downloaded-Rev10-Two-Rooftop-Alternatives-Phone-Review.pdf',O/'review/Rev10-Two-Rooftop-Alternatives-Phone-Review.pdf')
queue_zip(11,'Review-PDFs',{str(p.relative_to(O)):p for p in (O/'review').glob('*.pdf')})
with (O/'checkpoint/R1-packaging.log').open('w')as f:subprocess.run(['python',str(O/'source/package_checkpoint.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
items=json.loads((O/'checkpoint/final-archive-items.json').read_text())
for r in items:
 if r['folder']=='completion':(Q/f"{r['archiveNumber']:02d}.json").write_text(json.dumps(r,indent=2))
(O/'checkpoint/R1-PIPELINE-DONE.json').write_text(json.dumps({'status':'PASS','sameSealedMaster':True,'originalPhonePDFPreserved':True,'regeneratedOnlyUnuploadedEvidence':True,'finalArchiveItems':len(items)}));print('R1_PIPELINE_COMPLETE',flush=True)
