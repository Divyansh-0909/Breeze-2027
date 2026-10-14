"""Credential-free snapshot of mutable source/assets, including untracked work."""
from pathlib import Path
import hashlib, json, subprocess, tarfile, time

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "reports/stage-2c5-1-rock-realism-refinement-2026-10-14"
for name in ("raw", "backup", "before", "after", "reference", "scripts"):
    (OUT / name).mkdir(parents=True, exist_ok=True)

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode()

def safe(path):
    return not any(part.startswith(".env") or part in {".git", "node_modules", ".next", "__pycache__", ".vercel"}
                   or part.lower() in {"credentials", "secrets", "cookies.json", "storage-state.json"}
                   for part in path.parts)

paths = sorted(set(git("ls-files", "-z").split("\0") + git("ls-files", "--others", "--exclude-standard", "-z").split("\0")))
paths = [p for p in paths if p and safe(Path(p)) and (ROOT / p).is_file()
         and not p.startswith(str(OUT.relative_to(ROOT)) + "/")]
rows = [{"path": p, "bytes": (ROOT/p).stat().st_size,
         "sha256": hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in paths]
(OUT/"raw/baseline-hashes.json").write_text(json.dumps(rows, indent=2))
status = git("status", "--porcelain=v1", "--untracked-files=all")
(OUT/"raw/baseline-git-status.txt").write_text(status)
(OUT/"raw/baseline-unstaged.patch").write_text(git("diff", "--", "app", "components", "lib", "scripts", "tests", "public", "docs"))
(OUT/"raw/baseline-staged.patch").write_text(git("diff", "--cached", "--", "app", "components", "lib", "scripts", "tests", "public", "docs"))
mutable = {"app", "components", "lib", "scripts", "tests", "public", "docs", "assets-source", "design", "styles", "types", "hooks", "prisma"}
snapshot = [p for p in paths if Path(p).parts[0] in mutable or len(Path(p).parts) == 1 and not p.endswith(".zip")]
archive = OUT/"backup/current-source-assets.tar.gz"
with tarfile.open(archive, "w:gz", compresslevel=1) as tar:
    for p in snapshot:
        tar.add(ROOT/p, arcname=p, recursive=False)
state = {"branch": git("branch", "--show-current").strip(), "head": git("rev-parse", "HEAD").strip(),
         "capturedAtUnix": time.time(), "stagedPaths": git("diff", "--cached", "--name-only").splitlines(),
         "unstagedPaths": git("diff", "--name-only").splitlines(), "untrackedFileCount": len(git("ls-files", "--others", "--exclude-standard").splitlines()),
         "inventoriedFiles": len(rows), "snapshotFiles": len(snapshot), "snapshotBytes": archive.stat().st_size,
         "scope": "Tracked and untracked mutable source/configuration/assets; all other existing files inventoried and left untouched. Credentials/build caches/review ZIP duplicates excluded."}
(OUT/"raw/baseline-state.json").write_text(json.dumps(state, indent=2))
print(json.dumps(state, indent=2))
