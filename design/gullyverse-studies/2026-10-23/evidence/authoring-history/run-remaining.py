import subprocess,time
from pathlib import Path
O=Path(__file__).resolve().parent
while 'RENDER_JOBS_COMPLETE 36'not in (O/'evidence/render-final.log').read_text():time.sleep(5)
subprocess.run(['python',str(O/'source/finish_renders.py')],check=True)
