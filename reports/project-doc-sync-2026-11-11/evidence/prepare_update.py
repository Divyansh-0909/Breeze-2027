from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parents[1]
OLD = json.loads((ROOT / 'evidence/before-document.json').read_text())
TAB = 't.0'
HANDOFF = 'WORLD-REV15O-CONSOLIDATED-20261111-2c78b57e-R1'
REPORT = 'https://drive.google.com/file/d/1Gmb2grZHEg8fktyHioxyeZS3c6xmU-MZ/view?usp=drivesdk'
PDF = 'https://drive.google.com/file/d/1bBdRd61w1ryrXt-7-8h8C0mYhks4o95w/view?usp=drivesdk'
GALLERY = 'https://drive.google.com/drive/folders/1pz921xCMm3vpc3sQCDg7LGNTLsZdYQA2'
BACKUP = 'https://drive.google.com/drive/folders/1imTZqxSENLLjQczVOLzOHQc4dJgIAH17'
DOC_BACKUP = 'https://drive.google.com/drive/folders/1O53SmUTm-zgZWD_pMu5emcUgR-Dt_mML'

prefix = f'''CURRENT CODEX STATUS / 2026-11-11 / Rev15O CONSOLIDATED HANDOFF
{HANDOFF} — READY_FOR_REVIEW
Current native master: Rev15O / Clear Ground-Level House Fronts, 45 packed scenes. Eight Team murals, Organising Committee first; black painted brick and reference-based title/portrait placement. Aftermovie points up; Past Sponsors has the closely hung scrolling LED with wider logo gaps. Auxiliary crowd now matches Aftermovie. Events uses the existing cypher house's warm brick façade. Low ground-level house railings removed; upper balconies retained.
Resume from Rev15O, not the older Coordinator-first entries below. The dated consolidated log at the end records recovery, changes, reviews and restoration links. Earlier status/hold labels remain historical; current scoped user instructions and the CURRENT HANDOFF STATE govern resuming.
Pending: replacement for the rejected Schedule navigation label. Festival Guide is a suggestion only. Website integration and further art await the user's next request.
Consolidated handoff: {REPORT}
Latest review PDF: {PDF}
Current art checkpoint: {BACKUP}
Documentation snapshots/checkpoint: {DOC_BACKUP}

'''

pointer = f'''CURRENT LATEST CODEX HANDOFF / 2026-11-11
{HANDOFF} — READY_FOR_REVIEW
Use the Rev15O packed master and its REV15O / Team Carousel Controller (team_index 0–7; 0 = Organising Committee). The dated consolidated entry at the end covers I1 recovery and J, J1, K, L, L1, M, N and O. The active carousel has eight teams, without Coordinators. Current whole-environment scene count: 45.
Report: {REPORT}
Review PDF: {PDF}
Source/checkpoint: {BACKUP}
Earlier summaries below are historical; they do not replace this current resume point or authorize another phase.

'''

state = f'''CURRENT_PHASE: REV15O_NATIVE_ENVIRONMENT_COMPLETE_DOCUMENTATION_RECONCILED_2026_11_11
CODEX_STATUS: READY_FOR_REVIEW; USER_REQUESTED_DOCUMENT_SYNC; CURRENT_PACKED_MASTER_45_SCENES; NO_WEBSITE_INTEGRATION_OR_DEPLOYMENT
CODEX_HANDOFF_ID: {HANDOFF}
CODEX_REPORT_URL: {REPORT}
CODEX_REVIEW_PDF_URL: {PDF}
CODEX_GALLERY_URL: {GALLERY}
CODEX_BACKUP_FOLDER_URL: {BACKUP}
CODEX_BACKUP_VERIFICATION: PASS — 15 O uploads matched authenticated download-back SHA256, remote parent and size; all 36 payloads in eight ZIP parts passed streamed CRC/size/SHA checks; fresh Blender master open reported 45 scenes. O was not independently fully extracted again.
CURRENT_MASTER: reports/house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend
CURRENT_MASTER_SHA256: 2c78b57e97a5a97683f946d60ad265b22a1eb88ae12abed6220ec268ce473657
CURRENT_MASTER_BYTES: 171581117
CURRENT_SCENE: REV15O / Clear Ground-Level House Fronts
CURRENT_TEAM_CONTROLLER: REV15O / Team Carousel Controller; team_index 0–7; eight teams; Organising Committee first; Coordinators removed from active carousel
CURRENT_DOCUMENTATION_BACKUP_URL: {DOC_BACKUP}
LAST_CHATGPT_REVIEWED_HANDOFF_ID: WORLD-REV13A-ANATOMY-20261102-995ca9fb-R1
CHATGPT_STATUS: PRIOR_RECORDED_REVIEW_RETAINED; NO_NEW_INDEPENDENT_CHATGPT_REVIEW_OR_SIGNOFF_CLAIMED_BY_THIS_CODEX_DOCUMENT_SYNC
USER_VISUAL_APPROVAL: Earlier Rev12 architecture and Rev13A crowd approvals retained. User said “good” after Rev15O and requested this update; this accepts the direction for continuation, not blanket likeness/runtime/device/release approval.
PENDING_NAVIGATION: Schedule remains visible in the asset but was rejected as redundant with Events; Graffiti Yard was rejected; Festival Guide was suggested only, not selected or implemented.
NEXT_PROMPT_STATUS: AWAIT_NEXT_EXPLICIT_USER_REQUEST; DOCUMENT_UPDATE_IS_NOT_AN_EXECUTION_TRIGGER
NEXT_PROMPT_TEXT: Resume any future whole-world work from Rev15O and read the dated consolidated handoff first. Preserve prior approved baselines except later user-authorized scoped changes. Do not resume old Coordinator-first, nine-slide, Team-not-started or outdated stop/current labels as the current state. Further art, the navigation replacement and website integration require the user's next direction.
'''

md = (ROOT / 'delivery/CONSOLIDATED-HANDOFF.md').read_text()
log = '\n' + md.replace('`', '')
log = re.sub(r'(?m)^#+ ', '', log)
headings = ['Gullyverse — consolidated Rev15O handoff'] + re.findall(r'(?m)^## (.+)$', md)

def units(s): return len(s.encode('utf-16-le')) // 2
def rng(a, b): return {'startIndex': a, 'endIndex': b, 'tabId': TAB}
RED = {'red': 0.7764706, 'green': 0.15686275, 'blue': 0.15686275}
requests = []
operations = []

def insert(index, text, color=RED, title=None, heading_lines=()):
    end = index + units(text)
    requests.append({'insertText': {'location': {'index': index, 'tabId': TAB}, 'text': text}})
    requests.append({'updateParagraphStyle': {'range': rng(index, end), 'paragraphStyle': {'namedStyleType': 'NORMAL_TEXT', 'spaceBelow': {'magnitude': 6, 'unit': 'PT'}}, 'fields': 'namedStyleType,spaceBelow'}})
    requests.append({'updateTextStyle': {'range': rng(index, end), 'textStyle': {'foregroundColor': {'color': {'rgbColor': color}}, 'fontSize': {'magnitude': 11, 'unit': 'PT'}, 'bold': False, 'italic': False, 'underline': False}, 'fields': 'foregroundColor,fontSize,bold,italic,underline,link'}})
    for line in ([title] if title else []) + list(heading_lines):
        offset = text.index(line)
        h = rng(index + units(text[:offset]), index + units(text[:offset + len(line)]))
        requests.append({'updateParagraphStyle': {'range': h, 'paragraphStyle': {'namedStyleType': 'HEADING_1' if line == title else 'HEADING_2'}, 'fields': 'namedStyleType'}})
        requests.append({'updateTextStyle': {'range': h, 'textStyle': {'bold': True, 'fontSize': {'magnitude': 18 if line == title else 16, 'unit': 'PT'}}, 'fields': 'bold,fontSize'}})
    for match in re.finditer(r'https://[^\s]+', text):
        requests.append({'updateTextStyle': {'range': rng(index + units(text[:match.start()]), index + units(text[:match.end()])), 'textStyle': {'link': {'url': match[0]}, 'underline': True}, 'fields': 'link,underline'}})
    operations.append({'kind': 'insert', 'index': index, 'text': text})

# Work backward so original native indices remain valid.
insert(575136, log, title=headings[0], heading_lines=headings[1:])
requests.append({'deleteContentRange': {'range': rng(26568, 28905)}})
operations.append({'kind': 'delete', 'start': 26568, 'end': 28905})
insert(26568, state, color={'red': 0, 'green': 0, 'blue': 0})
insert(13388, pointer, title=pointer.splitlines()[0])
insert(1, prefix, title=prefix.splitlines()[0])

rows = [c for c in OLD['tabs'][0]['body']['content'] if 'paragraph' in c]
flat = ''.join(''.join(e.get('textRun', {}).get('content', '') for e in c['paragraph']['elements']) for c in rows)
offsets = {}
n = 0
for c in rows:
    offsets[c['startIndex']] = n
    n += units(''.join(e.get('textRun', {}).get('content', '') for e in c['paragraph']['elements']))
expected = flat.encode('utf-16-le')
# These operations are in original-index descending order, except the state replacement.
for op in operations:
    if op['kind'] == 'delete':
        a,b=offsets[op['start']]*2,offsets[op['end']]*2
        expected=expected[:a]+expected[b:]
    else:
        a=offsets[op['index']]*2
        expected=expected[:a]+op['text'].encode('utf-16-le')+expected[a:]

(ROOT/'evidence/expected-after-text.txt').write_text(expected.decode('utf-16-le'))
(ROOT/'evidence/update-plan.json').write_text(json.dumps({'document_id': OLD['documentId'], 'write_control': {'requiredRevisionId': OLD['revisionId']}, 'requests': requests}, ensure_ascii=False, indent=2)+'\n')
(ROOT/'evidence/edit-operations.json').write_text(json.dumps(operations, ensure_ascii=False, indent=2)+'\n')
(ROOT/'evidence/new-content.json').write_text(json.dumps({'prefix':prefix,'pointer':pointer,'state':state,'log':log},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'requestCount':len(requests),'oldParagraphs':len(rows),'newTextUnits':units(prefix)+units(pointer)+units(state)+units(log),'expectedTextUnits':len(expected)//2}))
