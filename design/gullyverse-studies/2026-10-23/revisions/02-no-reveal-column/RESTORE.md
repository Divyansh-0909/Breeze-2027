# Restore revision 02 — no reveal column

1. Verify the archive SHA-256 against CHECKPOINT-INDEX.json / its Drive verification receipt.
2. Extract Gullyverse-No-Reveal-Column-Source-Review.zip into a fresh folder.
3. Check FILE-SHA256SUMS.txt against the extracted files.
4. Open source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend in Blender 4.3.2 or compatible Blender. All 25 images are packed. No website, external Blend library or texture folder is needed to open the master.
5. Choose scene A / Grounded Indian Neighborhood, B / Festival Heavy Block or C / Balanced Neighborhood Cypher. Select any named camera; all original 13 cameras remain. Camera guide is source/camera-guide.json.
6. Open review/index.html for the 18 new full-resolution renders, or the review PDF. The previous 36-render/20s-animatic package remains historical and is not overwritten.

To repeat renders from the revised master: blender -b source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend -t 2 --python source/render_study.py -- revision
The renderer skips existing PNGs; use a fresh copy/output directory to regenerate.

The source remove_reveal_column.py and compare_masters.py document the exact transformation and tests against the prior master. Replaying those baseline comparisons requires the original master at its original relative location; this is not needed to open/render the already revised master. Original independently verified master: https://drive.google.com/file/d/1DShWnXw_k-GCKoOz1UDB3Sa-pVIlFiVY/view

This archive contains no Git repository, credentials, environment files or installed dependencies. It is a self-contained Blender concept, not a backup replacing the protected website or earlier phase checkpoints. No code should be copied into production automatically.
