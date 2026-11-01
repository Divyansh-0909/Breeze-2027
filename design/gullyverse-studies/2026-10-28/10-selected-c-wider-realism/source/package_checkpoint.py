import json,hashlib,zipfile,os,datetime
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());out=Path('/dev/shm/rev07-delivery/archives');out.mkdir(exist_ok=True)
assert json.loads((O/'evidence/FINAL-VISUAL-QA.json').read_text())['masterSHA256']==a['masterSHA256']
restore=f"""# Wider C+A private Blender checkpoint

This restores the private artwork, not the website. Original A/B/C and approved pilot scenes remain intact. Do not promote, export into the app or alter the crowd/counters without separate approval.

Download all SEVEN complementary FINAL archives listed in ARCHIVE-INDEX.json. Compare byte counts and SHA-256, then extract them into the SAME NEW EMPTY directory. Never extract over an application repository or older checkpoint.

Verify FILE-SHA256SUMS.txt. Open source/Gullyverse-Selected-C-Wider-Realism.blend with Blender 4.3.2 or compatible later version. Choose SELECTED C+A / Wider Neighborhood Realism. There are five scenes: original A, B, C, approved pilot and new world. Keep five optional support lights at 0 W. All 33 image resources are packed. No live website dependency is needed.

World master SHA-256: {a['masterSHA256']}
Approved input SHA-256: 3ba2b0056a9cd12bc0fefaa9a503df0fe12539467d46a01c7fd0a91fa2124202

Crowd-and-Counter-Proposals-Only.blend is a SEPARATE proposal file, seven isolated scenes. No replacement has been applied to the world. Its neutral display-ground patch belongs only to isolated counter studies.

Open GALLERY.html after extracting ALL archives. PDFs, MP4, 44 full-resolution scene PNGs, 11 proposal PNGs and all 120 original walk frames are included. The walk is 40 seconds at 3 fps from original source frames 1-960, not interactive browser FPS.

## Reproduce in a separate working COPY

Run Blender with source/APPROVED-PILOT.blend and source/author_world.py. Then run source/repair_solidify_uv.py and source/finish_geometry.py against the resulting world master. These preserve exact evaluated floor geometry while correcting UVs and triangulating new fitting caps. Rerun run_validation.py, measure_visibility.py and validate_sightlines.py. No tolerance change is permitted.

Render matched before/after with render_world.py -- before / after. Run render_walk.py for source frames, then finalize_reviews.py. Run author_options.py against APPROVED-PILOT.blend and finish_option_ground.py against its separate output for proposal studies. Run validate_options.py on that proposal file.

Python review tooling requires Pillow, ReportLab and PyMuPDF; video tooling requires ffmpeg/ffprobe. No website dependencies or credentials are included or needed to open the delivered packed masters.

The source/prior-pilot directory includes the earlier source materials, artwork/provenance, authoring scripts and original corrugated-art master. Its duplicate prior pilot .blend is omitted because source/APPROVED-PILOT.blend is the identical original payload. Earlier independently verified full pilot checkpoint remains unchanged in Drive.

## Archive roles

1. Source-and-Tests: all new scripts, exact approved input, new world/proposal masters, technical evidence/report, restoration and per-file hashes.
2. Shared-Authoring-Inputs: prior editable corrugated master, raw/prepared art/material inputs and provenance.
3. Before-PNGs: 22 exact approved pilot views.
4. After-PNGs: 22 candidate views.
5. Proposal-PNGs-Final: 11 final proposal views.
6. Review-and-Gallery: review PDFs, technical PDF, walking clip and HTML gallery.
7. Original-Walk-Frames: all 120 genuine source frames.

Earlier Working-v1 and Validated-Source-v2 ZIPs are interim safety snapshots, not substitutes for the final seven archives. The earlier Proposal-PNGs ZIP predates neutral display-ground refinement; use Proposal-PNGs-Final for the final review. Earlier immutable backups are retained.

Final download-back receipts, independent fresh restore/reopen proof and shared Doc handoff are sidecars. They are not circularly included in their own precomputed archive hashes. A verified Drive backup does not assert that the user downloaded it to personal storage.
"""
(O/'RESTORE.md').write_text(restore)
files=[]
for folder in['source','evidence','renders','review']:
 for root,dirs,names in os.walk(O/folder,followlinks=True):
  dirs[:]=[d for d in dirs if d!='__pycache__']
  for name in names:
   p=Path(root)/name;rel=str(p.relative_to(O))
   if rel=='evidence/package.log':continue
   if p.suffix in['.pyc','.blend1']or rel=='source/prior-pilot/Gullyverse-Selected-C-Architectural-Pilot.blend':continue
   files.append(p)
files +=[O/'REPORT.md',O/'RESTORE.md',O/'GALLERY.html'];files=sorted(set(files))
rows=[{'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]
(O/'FILE-MANIFEST.json').write_text(json.dumps({'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSHA256':a['masterSHA256'],'members':rows},indent=2)+'\n');(O/'FILE-SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+r['path']+'\n'for r in rows))
groups={
 'Selected-C-Wider-Realism-Source-and-Tests.zip':[p for p in files if(str(p.relative_to(O)).startswith(('source/','evidence/'))and not str(p.relative_to(O)).startswith('source/prior-pilot/'))]+[O/'REPORT.md',O/'RESTORE.md',O/'FILE-MANIFEST.json',O/'FILE-SHA256SUMS.txt'],
 'Selected-C-Wider-Realism-Shared-Authoring-Inputs.zip':[p for p in files if str(p.relative_to(O)).startswith('source/prior-pilot/')],
 'Selected-C-Wider-Realism-Before-PNGs.zip':[p for p in files if str(p.relative_to(O)).startswith('renders/before/')],
 'Selected-C-Wider-Realism-After-PNGs.zip':[p for p in files if str(p.relative_to(O)).startswith('renders/after/')],
 'Selected-C-Wider-Realism-Proposal-PNGs-Final.zip':[p for p in files if str(p.relative_to(O)).startswith('renders/options/')],
 'Selected-C-Wider-Realism-Review-and-Gallery.zip':[p for p in files if str(p.relative_to(O)).startswith('review/')]+[O/'GALLERY.html'],
 'Selected-C-Wider-Realism-Original-Walk-Frames.zip':[p for p in files if str(p.relative_to(O)).startswith('renders/walk/')]
}
archives=[]
for name,members in groups.items():
 p=out/name
 if not p.exists():
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,6)as z:
   for f in members:z.write(f,str(f.relative_to(O)))
 with zipfile.ZipFile(p)as z:
  assert z.testzip()is None
  assert set(z.namelist())=={str(f.relative_to(O))for f in members}
  for f in members:assert hashlib.sha256(z.read(str(f.relative_to(O)))).hexdigest()==hashlib.sha256(f.read_bytes()).hexdigest()
 assert p.stat().st_size<80*1024**2
 archives.append({'name':name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'members':len(members),'folder':'checkpoint'})
index={'allSevenRequired':True,'extractIntoSameFreshDirectory':True,'masterSHA256':a['masterSHA256'],'archiveCount':7,'archives':archives,'payloadMemberCount':len(rows),'supersededProposalPNGs':'Earlier pre-display-ground archive remains historical, not a final restore input.'}
(O/'checkpoint/ARCHIVE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
queue=list(archives)
for rel,folder,name in[
 ('review/Selected-C-Wider-Realism-Phone-Review.pdf','review',None),('review/Selected-C-Wider-Realism-Full-Comparisons.pdf','review',None),('review/Selected-C-Wider-Realism-Technical-Report.pdf','review',None),('review/Selected-C-Wider-Realism-Walk-40s.mp4','review',None),('REPORT.md','review','Selected-C-Wider-Realism-Report.md'),
 ('source/Gullyverse-Selected-C-Wider-Realism.blend','checkpoint',None),('source/Crowd-and-Counter-Proposals-Only.blend','proposals',None),
 ('renders/after/01-lane-entry.png','review','Selected-C-Wider-Street.png'),('renders/after/11-rooftop-wide.png','review','Selected-C-Wider-Rooftop.png'),
 ('RESTORE.md','checkpoint',None),('FILE-MANIFEST.json','checkpoint',None),('FILE-SHA256SUMS.txt','checkpoint',None),('checkpoint/ARCHIVE-INDEX.json','checkpoint',None)]:
 p=O/rel;queue.append({'name':name or p.name,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'folder':folder})
(O/'checkpoint/UPLOAD-QUEUE.json').write_text(json.dumps(queue,indent=2)+'\n');print('FINAL_PACKAGES',len(rows),'payload files',len(queue),'upload entries',[(r['name'],r['bytes'])for r in archives],flush=True)
