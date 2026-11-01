# Restore centered-board revision 03

Verify Gullyverse-Centered-Board-Source-Review.zip against CHECKPOINT-INDEX.json and the verified Drive receipt. Extract into a fresh folder and verify FILE-SHA256SUMS.txt. Open source/Gullyverse-Lane-Rooftop-ABC-Centered-Board.blend in Blender 4.3.2 or compatible Blender. It contains A/B/C scenes and all 25 packed images; no website or external Blend library is required.

The board is centered at [0,21,7.2]m. Original 13 cameras remain. Camera 14-board-arrival is an additional frontal inspection. Use review/index.html for all 19 full-resolution renders or the review PDF for comparison. Current source provenance is in source/provenance.

Render matched views: blender -b source/Gullyverse-Lane-Rooftop-ABC-Centered-Board.blend -t 2 --python source/render_study.py -- revision
Render the extra view with -- board-arrival. Existing PNGs are skipped; use a fresh output copy to repeat renders.

The center_navigation_board.py and compare_masters.py scripts document the exact delta against the prior no-column master. Replaying these baseline comparisons requires that master in its historical relative location; opening/rendering the supplied current master does not. Prior no-column master: https://drive.google.com/file/d/1PN7Xs_1kymQK88NC2GiLKb2DshjgJwvP/view

This is a standalone concept checkpoint, not website code and not permission to deploy. It excludes credentials, live environment contents, dependencies and build output. Older checkpoints must be preserved.
