"""Self-contained review/export evidence; no credentials or broad backup."""
from pathlib import Path
import zipfile, json, hashlib, re, html

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "docs/gullyverse-stage-2c4-rock-look-restore.md"
OUT = ROOT / "reports/stage-2c4-rock-look-restore-2026-10-13"
ZIP = ROOT / "gullyverse-stage-2c4-rock-look-restore-review.zip"
paths = {REPORT}
for directory in ("before", "after", "reference", "raw", "scripts"):
    paths.update(p for p in (OUT/directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts
                 and p.name not in {"package-validation.json", "package-manifest.json", "package.log"})
paths.add(OUT/"gallery.html")
paths.update((ROOT/"public/models/gullyverse/rock-look-restore").glob("*"))
paths.update(ROOT/p for p in [
    "public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb",
    "assets-source/gullyverse/rock-pilot-2a/quarry-rock-pilot.blend",
    "public/models/gullyverse/limestone-excavation/grey-limestone-material.glb",
    "public/models/gullyverse/limestone-excavation/excavation-detailed.glb",
    "public/models/gullyverse/limestone-excavation/manifest.json",
    "components/immersive/LimestoneExcavationSession.ts",
    "components/immersive/ImmersiveShell.tsx",
    "scripts/blender/extract_original_rock_material.py",
    "scripts/blender/rock_pilot_materials.py",
    "scripts/blender/rock_pilot_surface.py",
    "scripts/blender/author_rock_pilot_2a.py",
    "tests/immersive/rock-look-restore.test.ts",
])
readme = OUT/"REVIEW-README.txt"
readme.write_text("Gullyverse Stage 2C.4 material correction review\n\n"
                  "On iPhone: download/unzip in Files; open individual PNGs inside reports/stage-2c4-rock-look-restore-2026-10-13/after.\n"
                  "The same folder has gallery.html with matched before/after pictures. The Markdown report is under docs/.\n"
                  "This is a review/material-export bundle, not the entire independently runnable website.\n"
                  "Original Stage2A Blender/GLB and reused connected geometry are included for inspection.\n"
                  "The broad recoverable working-tree backup stays in the workspace; it is not duplicated here.\n"
                  "No credentials, environment files, unrelated application data or new photorealistic production assets are included.\n")
paths.add(readme)
missing_links=[]
for target in re.findall(r'\]\(([^)]+)\)', REPORT.read_text()):
    if target.startswith(("http:", "https:", "#")):
        continue
    path=(REPORT.parent/target.split("#")[0]).resolve()
    if not path.is_file():
        missing_links.append(target)
    else:
        paths.add(path)
assert not missing_links, missing_links
for path in paths:
    assert path.is_file(), path
    assert path.is_relative_to(ROOT), path
    assert not any(part.startswith(".env") or part in {"backup", "credentials", "secrets", ".git", ".next", "node_modules", ".vercel"} for part in path.relative_to(ROOT).parts), path
manifest=[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(paths)]
(OUT/"raw/package-manifest.json").write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6)as archive:
    for path in sorted(paths):
        archive.write(path, path.relative_to(ROOT))
    archive.write(OUT/"raw/package-manifest.json",(OUT/"raw/package-manifest.json").relative_to(ROOT))
with zipfile.ZipFile(ZIP)as archive:
    assert archive.testzip() is None
    for row in manifest:
        assert hashlib.sha256(archive.read(row["path"])).hexdigest()==row["sha256"],row["path"]
    packaged=set(archive.namelist())
    gallery=OUT/"gallery.html"
    for target in re.findall(r'(?:src|href)="([^"#]+)"',gallery.read_text()):
        path=(gallery.parent/html.unescape(target)).resolve()
        assert str(path.relative_to(ROOT))in packaged,target
result={"status":"PASS","zip":str(ZIP.relative_to(ROOT)),"bytes":ZIP.stat().st_size,
        "sha256":hashlib.sha256(ZIP.read_bytes()).hexdigest(),"entries":len(packaged),
        "reportLinksResolve":True,"galleryLinksPackaged":True,"CRCAndAllFileHashesVerified":True,
        "excluded":"Credentials, build caches, unrelated application data and broad baseline backup."}
(OUT/"raw/package-validation.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
