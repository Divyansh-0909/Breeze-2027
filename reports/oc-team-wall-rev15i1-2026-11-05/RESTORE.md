# Restore the wider OC names

Download INDEX.json, restore.py and every required component. Check all sizes/SHA-256 hashes. Binary .blend.partNNN files join in numeric order; ZIPs extract into one empty directory. All required source/art/viewer assets and the authentic Rev15I baseline are included.

    python restore.py INDEX.json /path/to/downloads /empty/restore /empty/proof

Requires Python 3 and Blender 4.3.2. The script verifies component and payload hashes, runs the five scoped Blender groups, opens the packed 38-scene master with no linked libraries, verifies the unchanged local glTF and rechecks hashes. No earlier workspace is required.

Open delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend. Select scene REV15I1, run packed oc_wider_name_controls.py, then use Sidebar / Team Wall. Coordinators remain initial; OC is index 1. All historical scenes are preserved.

For the offline private local viewer:

    python -m http.server 8771 --directory /path/to/restored/viewer

Open http://localhost:8771/?team=1. No CDN is needed; Three.js and license are included. Browser lighting is a diagnostic approximation, while master screenshots use the approved unchanged world lighting.

Keep every listed component and final proof together outside Codex. Earlier checkpoints remain protected. No public promotion or deployment is authorized.
