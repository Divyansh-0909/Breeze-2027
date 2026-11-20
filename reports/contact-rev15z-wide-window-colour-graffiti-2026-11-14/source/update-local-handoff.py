from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];repo=R.parents[1];rows=json.loads((R/'evidence/upload-receipts.json').read_text());pdf=next(r['url']for r in rows if r['name']=='Breeze-Wide-Contact-Window-and-Restored-Graffiti-Rev15Z.pdf');folder='https://drive.google.com/drive/folders/1I1r0UwtFVHjMLvbZKlULDJr9U6SX0hMQ';b=json.loads((R/'evidence/build-verification.json').read_text())
summary=f'''**Latest: Rev15Z / 14 November 2026.** Restored the exact earlier orange/gold/pink Accommodation COMING / SOON artwork, mesh, UVs, transform and material. The foreground board/coping/trim and extra label/supporting graphic remain removed. CONTACT US now matches that colourful graffiti style above one wide window. The attendant, separate left bay and centre divider are gone; the form spans the full 4.52 m usable opening. [Four-page PDF]({pdf}) · [Versioned recovery folder]({folder}). The user rejected Y's white brush/person layout; Z supersedes it. Native/private browser checks and independent source rebuild passed. User visual approval, art freeze and full-world website integration remain pending. Earlier records below are historical.

'''
for filename in ['gullyverse-consolidated-handoff-current.md','gullyverse-shared-document-current.md','gullyverse-destination-design-current.md','gullyverse-accommodation-current.md']:
 p=repo/'docs'/filename;s=p.read_text();title,rest=s.split('\n',1);assert 'Latest: Rev15Z'not in s
 if filename=='gullyverse-destination-design-current.md':title='# Events and Contact destination design'
 p.write_text(title+'\n\n'+summary+rest.lstrip())
p=repo/'docs/gullyverse-contact-theme-current.md';old=p.read_text();assert 'Latest: Rev15Z'not in old;p.write_text(f'''# Current Contact Us place

{summary}The new native assembly has a single 4.76 m outer frame, recessed full-width form, worn sill, green timber surround and two local house lamps. CONTACT US is horizontally centred above it, using bold orange/gold-to-pink graffiti, black depth and white highlights matched to the original Accommodation image. No Contact person, left shutter bay or centre divider remains. All 189 existing crowd members remain.

Current complete native: `/dev/shm/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend`, scene `REV15Z / Wide Contact window and restored graffiti`; 63 scenes / 146 packed images. Scene fingerprint: `{b['sceneFingerprintSHA256']}`. All 62 historical memberships and 3,211 non-target Y objects/materials/UVs/transforms are exact. Eight Team carousel states, eight Events posters, old non-Contact lighting/world and all eight checked original application/movement files are preserved. Independent reconstruction from restored Y source and fresh opening passed.

The private browser form spans 1,141.89 px at 1440×900; the 390×844 phone layout uses the readable sheet. There is no overflow or GL/page/request error. Failed local test sends preserve text, confirmed local success resets it and duplicates are avoided. No external messages were sent. The component viewer's plain house context and diagnostic lights are temporary; it is not the whole website. The combined editable native component and separate Contact/Accommodation GLBs are included with source/assets and the replacement manifest. Recovery reuses the verified complete Y base chain plus Z; see `reports/contact-rev15z-wide-window-colour-graffiti-2026-11-14/RESTORE.md`.

Next: mount into the existing world, preserve quarry movement and pause/release pointer lock while typing, restore input/focus/position on close, use the existing `/api/contact` and `/admin/breeze-admin/contact` inbox, then complete full-world material baking/browser validation. No production application code, database/admin permissions, commit, push, PR or deployment changed. Events/admin/expiry policy remains proposed. Deadline: 28 November 2026, Asia/Kolkata, hour unspecified.

## Historical Y layout — rejected and superseded

'''+old)
print('Updated five current handoff files; prior history preserved.')
