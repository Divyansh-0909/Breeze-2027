"""Run actual-browser checks serially; keep competing renderers out of profiling."""
from pathlib import Path
import subprocess, os, json, time

root = Path("reports/stage-2c4-rock-look-restore-2026-10-13")
scripts = root / "scripts"
commands = [
    ("default-regressions", ["npm", "run", "test:immersive:browser"]),
    ("connected-regressions", ["node", str(scripts/"candidate-regressions.mjs")]),
    ("directional-travel", ["node", str(scripts/"directional-travel.mjs")]),
    ("ten-toggle-cycles", ["node", str(scripts/"lifecycle.mjs")]),
    ("context-and-fallback", ["node", str(scripts/"recovery.mjs")]),
    ("ten-video-cycles", ["node", str(scripts/"video-cycles.mjs")]),
    ("before-performance", ["node", str(scripts/"measure.mjs"), "before"]),
    ("after-performance", ["node", str(scripts/"measure.mjs"), "after"]),
    ("material-and-network", ["node", str(scripts/"material-verification.mjs")]),
]
rows = []
for name, command in commands:
    print("START", name, flush=True)
    start = time.monotonic()
    environment = {**os.environ, "GULLYVERSE_ARTIFACT_DIR": str(root/"raw"/name)}
    with (root/"raw"/(name+".log")).open("w") as output:
        try:
            code = subprocess.run(command, env=environment, stdout=output, stderr=subprocess.STDOUT, timeout=1200).returncode
        except subprocess.TimeoutExpired:
            code = 124
    rows.append({"name": name, "command": command, "exitCode": code, "seconds": time.monotonic()-start})
    (root/"raw/browser-commands.json").write_text(json.dumps(rows, indent=2))
    print("END", name, code, flush=True)
raise SystemExit(1 if any(row["exitCode"] for row in rows) else 0)
