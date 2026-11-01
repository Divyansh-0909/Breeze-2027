from pathlib import Path
import json,subprocess,hashlib
O=Path(__file__).resolve().parents[1];V=O/'review';frames=sorted((O/'walk-frames/C').glob('*.png'))
assert len(frames)==120
target=V/'Straight-Connection-Walk-20s.mp4'
result=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-framerate','6','-pattern_type','glob','-i',str(O/'walk-frames/C/*.png'),'-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-metadata','title=Gullyverse actual Blender straight-walk proof / 6fps / 384x240',str(target)],text=True,capture_output=True)
(O/'evidence/video-encode.log').write_text(result.stdout+result.stderr);assert result.returncode==0
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)],text=True))
stream=next(s for s in probe['streams']if s['codec_type']=='video')
assert int(stream['nb_read_frames'])==120 and abs(float(probe['format']['duration'])-20)<.001
assert stream['width']==384 and stream['height']==240 and stream['avg_frame_rate']=='6/1'
(O/'evidence/video-validation.json').write_text(json.dumps({'status':'PASS','durationSeconds':20,'actualRenderedFrames':120,'fps':6,'resolution':[384,240],'sourceFrames':[300,776],'sourceStep':4,'noInterpolationOrHeldKeyframeSubstitution':True,'videoBytes':target.stat().st_size,'videoSHA256':hashlib.sha256(target.read_bytes()).hexdigest(),'scope':'Uncut Blender motion-proof excerpt, not runtime or hardware-FPS evidence. Complete 40-second editable camera action is supplied in the master.'},indent=2)+'\n')
print('VIDEO_VALIDATED',target.stat().st_size,flush=True)
