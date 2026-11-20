from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];repo=R.parents[1];rows=json.loads((R/'evidence/upload-receipts.json').read_text());pdf=next(r['url']for r in rows if r['name']=='Breeze-Contact-Window-and-Clean-Accommodation-Rev15Y.pdf');folder='https://drive.google.com/drive/folders/1sLcU81eQ_OWoXHvwUS7mP-tgH8ick4sQ';b=json.loads((R/'evidence/build-verification.json').read_text());fp=b['sceneFingerprintSHA256']
summary=f'''**Latest: Rev15Y / 14 November 2026.** The approved Contact enquiry window is built in the existing right-side R1 house bay: person peeking from inside the left opening, a wide message panel on the right (71.93% of usable frontage), and a horizontally centred cream-white brush CONTACT US heading with a charcoal edge. Accommodation uses matching white COMING above SOON; its complete foreground low barrier, coping and trim (16 objects) are removed, leaving the cypher house wall. [Review PDF]({pdf}) · [Versioned recovery folder]({folder}). Native and private browser checks passed; visual approval, art freeze and full-world website integration remain open. Earlier entries below are historical.

'''
for filename in ['gullyverse-consolidated-handoff-current.md','gullyverse-shared-document-current.md','gullyverse-destination-design-current.md','gullyverse-accommodation-current.md']:
 p=repo/'docs'/filename;s=p.read_text();title,rest=s.split('\n',1);assert 'Latest: Rev15Y' not in s;p.write_text(title+'\n\n'+summary+rest.lstrip())
p=repo/'docs/gullyverse-contact-theme-current.md';old=p.read_text();p.write_text(f'''# Current Contact Us place

{summary}The native frontage includes faded-green timber, a shallow worn counter, small corrugated shade and local house lamps. Only the selected window's pane/sash/grille faces are removed; the surrounding house remains. The attendant reuses the approved Aftermovie person geometry. All 189 original crowd members remain, plus one new crew person. No public contact details are invented.

Current complete native: `/dev/shm/Gullyverse-Rev15Y-Enquiry-Window-and-Monochrome-Lettering.blend`, active scene `REV15Y / Enquiry window and monochrome graffiti`; 62 scenes / 145 packed images. Native scene fingerprint: `{fp}`. All 61 historical memberships, 3,208 protected original objects, untouched window faces/UVs/colours/materials, eight Team mural states, eight Events posters, old world/lights/exposure and all eight checked movement/application files are preserved. Independent source reconstruction and fresh opening passed. Source recovery reuses the verified full X1 dependency chain plus Y; see `reports/contact-rev15y-enquiry-window-2026-11-14/RESTORE.md`.

The Contact-only GLB, editable native component, deletion/replacement manifest and reusable accessible HTML form are included. The isolated browser viewer uses explicitly temporary house context/diagnostic lighting and is not the whole website. Laptop 1440×900 and phone 390×844 checks passed: person left, large right panel, no overflow or GL/page/request errors, failure preserves text, confirmed local test success resets it, and no duplicate submissions. No real messages were sent.

Next: mount into the existing world, preserve quarry movement and pause/release pointer lock while typing, restore input/focus/position on close, connect the existing `/api/contact` submission and `/admin/breeze-admin/contact` inbox, and complete full-world material baking and browser validation. No production application source, database/admin access, commit, push, PR or deployment changed in this phase. Events/admin/expiry policy remains proposed. Deadline: 28 November 2026, Asia/Kolkata, hour unspecified.

## Historical X1 proposal

'''+old)
print('Updated five current handoff files; historical text retained.')
