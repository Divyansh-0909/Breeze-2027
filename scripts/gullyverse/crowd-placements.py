"""Writes public/models/gullyverse/crowd-rocketbox/crowd.json: which Rocketbox avatar and pose stands at each of
the 189 Rev15Z crowd positions (scripts/gullyverse/crowd-source-placements.json, read from the locked master).

Lane and plaza characters keep their master facing and stand idle. The audience faces the stage with a
little variation; raised-arm source poses cheer, hands-together ones clap, the rest mix idle, cheer, clap
and dance. Avatars alternate women and men and are spread so neighbours differ. Seeded, so reruns match.
Coordinates are Three.js (Blender x, z, -y); yaw is about +Y with the avatar facing +Z at 0.
"""
import json, math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts/gullyverse/crowd-source-placements.json"
OUT = ROOT / "public/models/gullyverse/crowd-rocketbox/crowd.json"
WOMEN = ["Female_Adult_04", "Female_Adult_05", "Female_Adult_07", "Female_Adult_09", "Female_Adult_12", "Female_Adult_14"]
MEN = ["Male_Adult_03", "Male_Adult_04", "Male_Adult_05", "Male_Adult_07", "Male_Adult_10", "Male_Adult_12",
       "Male_Adult_17", "Male_Adult_18", "Male_Adult_20"]
STAGE = (0.0, -44.8)  # three.js x, z of the screen

rng = random.Random(20271128)
rows = json.loads(SOURCE.read_text())
# Order by position so the round-robin spreads avatars across neighbours.
rows.sort(key=lambda r: (round(r["location"][1] / 1.5), r["location"][0]))
placements, w, m = [], 0, 0
for i, r in enumerate(rows):
    x, y, z = r["location"][0], r["footZ"], -r["location"][1]
    woman = i % 2 == 0
    if woman: avatar = WOMEN[(w * 5) % len(WOMEN)]; w += 1
    else: avatar = MEN[(m * 4) % len(MEN)]; m += 1
    audience = r["chunk"] == "cypher-audience"
    source = r["pose"] or ""
    if not audience: pose = "idle"
    elif source in ("single-cheer", "phone-record"): pose = "cheer"
    elif source == "hands-together": pose = "clap"
    else: pose = rng.choices(["idle", "cheer", "clap", "dance"], [0.45, 0.2, 0.2, 0.15])[0]
    if audience:
        yaw = math.atan2(STAGE[0] - x, STAGE[1] - z) + rng.uniform(-0.3, 0.3)
    else:
        yaw = r["yaw"]
    height = r["height"] if source not in ("single-cheer", "phone-record") else 1.75
    height = min(1.9, max(1.58, height)) * rng.uniform(0.97, 1.03)
    placements.append({"avatar": avatar, "pose": pose, "position": [round(x, 3), round(y, 3), round(z, 3)],
                       "yaw": round(yaw, 4), "height": round(height, 3), "source": r["name"]})
data = {
    "schemaVersion": 1,
    "license": "Microsoft Rocketbox avatar library, MIT licence (github.com/microsoft/Microsoft-Rocketbox)",
    "avatars": {a: {"file": f"{a}.glb", "mobileFile": f"{a}.mobile.glb"} for a in WOMEN + MEN},
    "lods": [{"name": "lod0", "until": 12}, {"name": "lod1", "until": 25}, {"name": "lod2", "until": 1e9}],
    "placements": placements,
}
OUT.write_text(json.dumps(data, indent=1) + "\n")
from collections import Counter
print(len(placements), Counter(p["pose"] for p in placements), Counter(p["avatar"] for p in placements).most_common(3))
