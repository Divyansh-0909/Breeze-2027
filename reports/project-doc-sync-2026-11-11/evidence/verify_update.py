from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[1]
before = json.loads((ROOT/'evidence/before-document.json').read_text())
after = json.loads((ROOT/'evidence/after-document.json').read_text())
new = json.loads((ROOT/'evidence/new-content.json').read_text())
def units(s): return len(s.encode('utf-16-le'))//2
def txt(p): return ''.join(e.get('textRun',{}).get('content','') for e in p['paragraph']['elements'])
def paras(d): return [c for c in d['tabs'][0]['body']['content'] if 'paragraph' in c]
rows = paras(after)
actual = ''.join(map(txt, rows))
expected = (ROOT/'evidence/expected-after-text.txt').read_text()
assert actual == expected, 'Full text differs from the planned scoped edit'
(ROOT/'evidence/after-text.txt').write_text(actual)

def clean(x):
    if isinstance(x, dict):
        return {k:clean(v) for k,v in x.items() if k not in ('startIndex','endIndex','contentUri','thumbnailUri')}
    if isinstance(x, list): return [clean(v) for v in x]
    return x

by_index = {c['startIndex']:c for c in rows}
shift_state = units(new['state']) - (28905-26568)
def shift(i):
    return i + units(new['prefix']) + (units(new['pointer']) if i>=13388 else 0) + (shift_state if i>=28905 else 0) + (units(new['log']) if i>=575136 else 0)

checked = 0
mismatches=[]
for old in paras(before):
    i = old['startIndex']
    if 26568 <= i < 28905: continue
    current=by_index.get(shift(i))
    # The blank immediately after the replaced state inherits the adjacent
    # historic red author colour; its text and paragraph style are unchanged.
    boundary_blank = i == 28905 and txt(old) == '\n' and current is not None and txt(current) == '\n' and old['paragraph']['paragraphStyle'] == current['paragraph']['paragraphStyle']
    if not boundary_blank and (current is None or clean(old)!=clean(current)):
        mismatches.append({'beforeStart':i,'afterStart':shift(i),'text':txt(old)[:120], 'currentText':txt(current)[:120] if current else None, 'beforeParagraphStyle':old['paragraph'].get('paragraphStyle'),'afterParagraphStyle':current['paragraph'].get('paragraphStyle') if current else None})
    checked += 1

assert not mismatches, json.dumps(mismatches[:8], ensure_ascii=False)
assert len(before['tabs'])==len(after['tabs'])==1
btab,atab=before['tabs'][0],after['tabs'][0]
assert clean(btab['inlineObjects'])==clean(atab['inlineObjects']), 'Embedded image properties changed'
assert clean(btab['positionedObjects'])==clean(atab['positionedObjects'])
for key in ['headers','footers','footnotes','documentStyle','namedStyles','lists','dropdownDefinitions']:
    assert clean(btab.get(key))==clean(atab.get(key)), f'Native {key} changed'

first=txt(rows[0])
assert first.startswith('CURRENT CODEX STATUS / 2026-11-11 / Rev15O')
assert 'LAST_CHATGPT_REVIEWED_HANDOFF_ID: WORLD-REV13A-ANATOMY-20261102-995ca9fb-R1' in new['state']
assert 'eight teams' in new['state'] and 'Festival Guide was suggested only' in new['state']

# Ground the newly inserted status and log headings and every new native URL link.
heading_titles=['CURRENT CODEX STATUS / 2026-11-11 / Rev15O CONSOLIDATED HANDOFF','CURRENT LATEST CODEX HANDOFF / 2026-11-11','Gullyverse — consolidated Rev15O handoff']
for title in heading_titles:
    row=next(c for c in rows if txt(c).strip()==title)
    assert row['paragraph']['paragraphStyle']['namedStyleType']=='HEADING_1'
urls=set(re.findall(r'https://[^\s]+',''.join(new.values())))
links={e.get('textRun',{}).get('textStyle',{}).get('link',{}).get('url') for c in rows for e in c['paragraph']['elements']}
assert urls<=links, 'A new review/checkpoint URL is missing its native link'

proof={'status':'PASS','documentId':after['documentId'],'revisionId':after['revisionId'],'fullTextMatchesPlannedEdit':True,'preservedHistoricalParagraphs':checked,'historicalNonemptyContentAndStylesUnchanged':True,'boundaryBlankInheritsHistoricRedAuthorColour':True,'inlineObjectsPreserved':len(atab['inlineObjects']),'nativeTabHeadersFootersAndStylesPreserved':True,'newHeadingChecks':'PASS','newLinkedUrls':len(urls),'priorIndependentReviewIdPreserved':True,'afterTextSHA256':hashlib.sha256(actual.encode()).hexdigest(),'afterTextUTF16Units':units(actual),'beforeRevisionId':before['revisionId']}
(ROOT/'evidence/document-readback-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof,indent=2))
