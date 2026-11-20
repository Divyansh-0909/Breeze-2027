import json,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=O.parent/'navigation-board-rev15l-led-sponsors-2026-11-11'
m=json.loads((B/'evidence/sponsors.json').read_text());position=0
for r in m['logos']:
 r['tileCells']=2*math.ceil(max(96,r['logoCells'][0]+72)/2);r['startCell']=position;position+=r['tileCells']
m.update(version='REV15L1',periodCells=position,minimumLogoGapCells=72,previousMinimumLogoGapCells=24)
for file in ['evidence/sponsors.json','viewer/sponsors.json']:(O/file).write_text(json.dumps(m,indent=2))
board=json.loads((B/'viewer/board.json').read_text());board.update(version='REV15L1',periodCells=position,periodSeconds=position/30,minimumLogoGapCells=72)
for file in ['evidence/board-manifest.json','viewer/board.json']:(O/file).write_text(json.dumps(board,indent=2))
