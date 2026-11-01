import json,hashlib,subprocess,time,statistics
from pathlib import Path
O=Path(__file__).resolve().parents[1]
while not(O/'checkpoint/CAPTURES-DONE.json').exists():time.sleep(1)
walk=json.loads((O/'evidence/render-walk.json').read_text());assert len(walk)==120 and sorted(r['index']for r in walk)==list(range(120))
a=json.loads((O/'evidence/authoring.json').read_text())
for r in walk:
 assert r['masterSHA256']==a['masterSHA256'];assert hashlib.sha256((O/r['file']).read_bytes()).hexdigest()==r['sha256'];assert r['sourceFrame']==round(1+959*r['index']/119)
video=O/'review/Selected-C-Wider-Realism-Walk-40s.mp4'
subprocess.run(['ffmpeg','-y','-framerate','3','-i',str(O/'renders/walk/%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],stdout=subprocess.DEVNULL,stderr=(O/'evidence/video-encode.log').open('w'),check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,nb_read_frames,r_frame_rate:format=duration','-of','json',str(video)]))
assert int(probe['streams'][0]['nb_read_frames'])==120 and abs(float(probe['format']['duration'])-40)<.01
subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],stderr=(O/'evidence/video-full-decode.log').open('w'),check=True)
(O/'evidence/video-validation.json').write_text(json.dumps({'status':'PASS','actualFrames':120,'sourceRange':[1,960],'encodedDurationSeconds':40,'frameRate':3,'offlineNotInteractiveFPS':True,'metadata':probe,'sha256':hashlib.sha256(video.read_bytes()).hexdigest()},indent=2)+'\n')
for script in['build_review.py','build_report.py']:
 subprocess.run(['python',str(O/'source'/script)],check=True)
# A native text PDF of the full technical report accompanies the Markdown.
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import html
style=getSampleStyleSheet();style.add(ParagraphStyle('Technical',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=6,wordWrap='CJK'))
story=[]
for block in(O/'REPORT.md').read_text().split('\n\n'):
 if not block.strip():continue
 if block.startswith('# '):story.append(Paragraph(html.escape(block[2:]),style['Title']))
 elif block.startswith('## '):story.append(Paragraph(html.escape(block[3:]),style['Heading2']))
 else:story.append(Paragraph(html.escape(block).replace('\n','<br/>'),style['Technical']))
SimpleDocTemplate(str(O/'review/Selected-C-Wider-Realism-Technical-Report.pdf'),pagesize=(595,842),rightMargin=32,leftMargin=32,topMargin=32,bottomMargin=32).build(story)
(O/'checkpoint/REVIEWS-DONE.json').write_text('{"status":"PASS"}\n');print('REVIEWS_READY_FOR_VISUAL_QA',flush=True)
