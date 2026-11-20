# Night pilot recovery — 12 November 2026

The user approved the Rev15P2 night look and explicitly requested the shared document update and upload of missing output files. The shared control document now records the completed native/browser work, measured limits, preservation checks, backup links and the next private walkable integration step.

Shared document: https://docs.google.com/document/d/1ynihhc-k0aSRGVY6oJttLY8MD1AhKPahCcqheL-g56k

## Verified source outputs

- Complete Rev15P base, including the packed editable Blender scene: https://drive.google.com/drive/folders/19lLbeomN6cqhASBobc3T2SvmUHoz8wKG
- Incremental Rev15P2 optimized browser viewer and sources: https://drive.google.com/drive/folders/1Ou_LWPXLKovvTrDRnSdpsBpWvupbhyzq
- Combined recovery index, script and native document snapshots: https://drive.google.com/drive/folders/1vIEijMklnKneib70t0xEnHo9mKaZQ7dh

Both archives are immutable copies of the earlier verified local checkpoints. The complete base is split into 11 parts; the incremental browser archive is split into two. All 13 parts were downloaded back through authenticated Drive access and checked for exact byte size and SHA-256, with remote parent folders verified. Together they preserve 293,608,528 original archive bytes and 156 verified payloads. The complete base includes all 46 packed native scenes and source artwork; it does not depend on a Git LFS pointer being available.

Download all `.partNNN` files from both source folders, plus `SOURCE-CHECKPOINT-INDEX.json` and `restore-checkpoints.py` from this folder. Keep their filenames. Run:

```sh
python restore-checkpoints.py /path/to/downloads /path/to/new-empty-restore
```

The script requires Python 3.9 or later and the standard library. It verifies each part, reassembles and checks both complete ZIPs, extracts the base before the incremental archive, and checks every payload against its recorded hash. It refuses to use a nonempty destination. Keep the original downloaded parts and archives until restoration has been checked.

Open `reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend` using Blender 4.3.2 or compatible. The native source retains all 45 earlier scenes plus the isolated night pilot and 69 packed images. Rev15O remains the unchanged historical native baseline.

From the restored root, run `python reports/night-atmosphere-rev15p2-browser-2026-11-12/source/serve.py` and open `http://127.0.0.1:8767/`. Python and a WebGL2 browser are sufficient for the supplied standalone viewer. Both base and incremental archives are required for baseline comparisons and complete source recovery. Read the restored `RESTORE.md` and `REPORT.md` files for rebuild dependencies and the GLB material contract, including `nativeLightfieldScale=32` and UV1 ground lightmaps.

Historical `LOCAL ONLY` and no-Drive-writes text inside the frozen archives records their original delivery state. This dated handoff and its receipts record the later explicit authorization and completed verified upload. Earlier checkpoints and Drive sharing settings were retained.

## Reviews already on Drive

- Latest browser/night comparison PDF: https://drive.google.com/file/d/1Sa9tBen_AD-pgb1fgLBMvD1CX4hR7N7-/view?usp=drivesdk
- Native night-pilot PDF: https://drive.google.com/file/d/1ZLlaD9XLDTBdhiiXC3AjWg4GvDzZi3cK/view?usp=drivesdk

These existing verified PDFs were reused. All visual previews should continue to be delivered in PDF.

## Current implementation status

The approved look and browser optimization are complete in a private pilot. The original quarry controller, input, rendering and transition files remain unchanged, with all eight recorded hashes rechecked. A walkable integration of the night assets with those controls is the next authorized implementation step and remains pending. No walkthrough bundle or completed integration test is claimed here. The browser asset is a representative subset with the current Organising Committee artwork, not the complete native crowd/stage or an eight-slide browser carousel.

Software-rendering measurements show lower comparative render cost. They do not certify the requested 60 FPS desktop or 30 FPS mobile targets or physical-device performance. Full-scene optimization, hardware testing and a useful replacement for the rejected Schedule label remain open. No production route changes, commits, pushes, merges or deployment were made.
