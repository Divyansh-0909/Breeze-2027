# Gullyverse — Navigation board in rooftop approach

Handoff: `WORLD-LANE-ROOFTOP-CENTERED-BOARD-20261023-03`.

The user requested the navigation board to be in the way of the rooftop cypher. The existing full board assembly is translated from [5.6, 25, 7.2]m to [0, 21, 7.2]m, placing it across the arrival centerline immediately before the original hub [0, 22, 7.2]m and the cypher. It is no longer tucked off to the right.

The same 18-object landmark retains its artwork, scale, meshes, UVs, materials and sign hierarchy. Its existing local practical follows the board in each of the three variants (3 light objects translated; none added). All global lighting, other objects, crowd, destination walls and screen remain unchanged. The reveal column stays removed. Team remains right, Events left and Aftermovie straight ahead. No variant is automatically selected.

## Validation

Both the previous no-column master and the revised master were reopened and compared. All original object sets remain. Every existing mesh/UV/material data hash matches; only the 18 board-object and 3 associated light transforms change. All original cameras are unchanged. A separate `14-board-arrival` camera was added for a clear frontal inspection; it is explicitly not presented as a matched historical pose.

The original 0.35m capsule, floor (<0.002m height tolerance) and sampled camera-path checks pass without relaxed tolerances. The minimum sampled one-sided clearance is 0.902m along entry, 0.981m toward Team and 0.625m toward Events; the screen route exceeds the 1.6m ray limit. These checks do not certify a continuous 3m route or regulatory accessibility. The old zero-visible-screen landing requirement remains retired after the preceding user-requested reveal-block removal; the unmodified historical survey still reports REVIEW_FAILURES on that art requirement. Current sampled screen-ray visibility is 10/15 landing, 11/15 opening, 15/15 final.

## Review package

19 new actual Blender EEVEE Next renders: six original matched cameras across A/B/C (18) plus the new frontal arrival view in C. The original pose, lens, quality and exposure settings are retained for matched views. The board is nearer the original hub camera, so that close framing can crop the board; the separate arrival camera shows the full structure without silently changing comparison poses.

A 9-page phone-friendly PDF includes before/after C opening, the new frontal arrival view, updated master plan and matched A/B/C images. Full-resolution PNGs, an offline gallery, three contact sheets, editable packed Blender source and authoring/validation scripts are included. Existing crowd/vehicles/stock remain concept proxies and event art remains placeholder. No new realism or hardware-performance claim is made.

## Preservation and backup

The preceding no-column master and all older evidence/backups remain unchanged. All 1,213 protected website files and Git status match the preservation baseline. The website remains `work-in-progress-2027` at `e638140b37045a805b23b4d406d387a8870f8486`. No website code, defaults, navigation behavior or deployment was changed; no commit, push or merge.

A new Drive subphase `03-Centered-Navigation-Board` contains the review and independently restorable checkpoint. Actual complete download-back SHA-256 verification and independent extracted-master opening are recorded in the separate checkpoint receipt. Stop for user review; no automatic next phase.
