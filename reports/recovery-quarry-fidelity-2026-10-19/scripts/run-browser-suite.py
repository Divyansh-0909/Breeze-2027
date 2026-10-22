from pathlib import Path
import argparse
import json
import os
import subprocess
import time

ROOT = Path.cwd()
OUT = ROOT / "reports/recovery-quarry-fidelity-2026-10-19"
parser = argparse.ArgumentParser()
parser.add_argument("jobs", nargs="*")
args = parser.parse_args()
jobs = {"public-stabilization": ROOT / "tests/immersive/stabilization.browser.mjs",
        "private-regressions": OUT / "scripts/candidate-regressions-c9.mjs",
        "directional-travel": OUT / "scripts/directional-travel-c9.mjs",
        "composition-ownership-recovery": OUT / "scripts/composition-browser-checks.mjs",
        "preview-persistence": OUT / "scripts/preview-persistence.mjs"}
rows = []
for name in args.jobs or jobs:
    output = OUT / "raw" / name
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(CHROME_PATH="/usr/bin/chromium", GULLYVERSE_ARTIFACT_ROOT=str(OUT),
               GULLYVERSE_ARTIFACT_DIR=str(output))
    started = time.monotonic()
    with (OUT / "raw" / ("browser-" + name + ".log")).open("w") as log:
        result = subprocess.run(["node", str(jobs[name])], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    rows.append({"name": name, "script": str(jobs[name].relative_to(ROOT)), "exitCode": result.returncode,
                 "build": (ROOT / ".next/BUILD_ID").read_text().strip(),
                 "seconds": round(time.monotonic() - started, 3)})
    (OUT / "raw/browser-suite-summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(rows[-1]), flush=True)
raise SystemExit(1 if any(row["exitCode"] for row in rows) else 0)
