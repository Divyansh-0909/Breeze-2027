# Rev05B execution notes — not a completion claim

User approved the latest shared Doc prompt on 25 October 2026. This explicitly resolves the shop cavity exception and authorizes crowd center fill, loose wings, sparse people beyond the board. No further permission is needed. Blender-only, no website changes/commit/push/deploy. No A/B/C selection or next art phase.

Root: `/workspace/gullyverse-world-concept/2026-10-25/06-rev05b-open-shops-full-center-crowd`.
Protected Rev05A input: `source/baseline/Rev05A.blend`, SHA b143dc873b9566217301119f97cf349a73db58d7fdc1591c451e2daf7000ee8c.
Final master: `source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend`, 4,035,714 bytes, SHA 8fbfbfb1c69bd0daefb5690c935c8317ed3516ab0e1af07e8a9bd371747ec5ff.

Implemented: 5 actual cavity hosts + 5 front trims, exact outer bounds; depths increased from failed 3.8m draft to 4.4m, width6.2m and height2.85m. Five wood backplanes move inward; 45 boards /180 cartons move as15 rigid rack assemblies onto two side walls. Five interior-only shadowed45W area sources added because stock was dark. All existing street/world/material/image/camera/action state fixed; all counters and DJ furniture exact; closed stores unchanged.

Crowd seed2026102506, A176/B184/C180 excluding9 unchanged lane/cypher people. 32 new shared actors /256 linked parts. 188 union actors /1504 parts, zero actual body/prop overlaps. Filled old center:16/18/16 people. Static narrow body buffer |X|>=.45 until Y36.95; original straight40sec action stops atY36.5. No parting, no collision disabling. All960 frames per A/B/C and original entry/screen/Team/Events checks pass .35m / .002m unchanged.

Important disclosed inherited limits: negative-Y shop approaches at leftY+2 and rightY-7 hit `Scooter steering.002` and `.001`; positive-Y alternatives pass. Keep failures; do not move locked scooters. No claim all approach options pass.

Full renders RUNNING:
- exec session61473: BEFORE, `evidence/render-before-all.log`, 75 targets (25poses xA/B/C). Six early valid C before captures are seeded; three bad section crops were archived and rerendered correctly.
- exec session91850: AFTER, `evidence/render-after-all.log`, 75 targets.
- Each render job now writes its own `render-manifest-<edition>-all.json`, avoiding concurrent JSON writes. Legacy `render-manifest.json` contains the early6 valid before rows and rejected drafts; `build_review.py` selects actual matching hashes by file and merges them safely. 1200x750 / portrait540x960, EEVEE16samples. Both render jobs use LP_NUM_THREADS=1 /OMP_NUM_THREADS=1 and Blender-t1. Software-only; no hardware FPS claims.
- Final corrected section cameras41..45 use ortho9.6 and rotate +/-90deg; near-plane cuts at local+2.7m. Actual after section inspected and shows both side walls + fixed counter. Old tight crops are diagnostics only.
- Rejected3.8m/no-fill previews, corrected previews and rejected tight section crops remain separate under `renders`; they are excluded from final pairs.

Tests already PASS: `preservation-audit.json`, `body-overlap-validation.json`, `shop-geometry-stock-validation.json`, `layout-validation.json`; all1213 protected WIP file hashes/Git status unchanged (`website-preservation.json`). WIP branchwork-in-progress-2027, HEAD e638140b37045a805b23b4d406d387a8870f8486. Do not edit either website worktree.
Budget final: A83564/B86698/C84768 evaluated triangles;17 authoring lights,24 packed images,95.86MiB estimated RGBA8+mips. No new images or external mesh kit. Original crowd remains static low-detail proxies.

Remaining sequence:
1. Finish both75-shot jobs. Validate logs/counts and inspect representative A/B/C sections/crowd/mobile.
2. Run `source/lighting_isolation.py` on final master AFTER full jobs stop (4 same-geometry C captures: storefront and inside, each0W/45W; no save). Use LP_NUM_THREADS=2 /OMP_NUM_THREADS=2 /Blender-t2 for isolated software still costs. No realtime FPS inference.
3. `python source/build_review.py` ->75 matched pairs/150 final PNGs,80-page fullPDF +14-page concisePDF, GALLERY.html. PDF uses JPEG85/subsampling1, originals remain losslessPNG. All3 preview JPGs are deterministic and should retain already-uploaded hashes.
4. `python source/build_report.py` ->REPORT.md + light/readability/offline-cost evidence.
5. `python source/package_checkpoint.py` ->9 required complementaryZIPs (Source-and-Tests, Reviews, A/B/C before+after, Image-Diagnostics), FILE-MANIFEST/SHA256SUMS and archive index. Every archive<49MiB. Includes checkpoint/drive-folders.json for reproducibility. Per-member hashes exclude manifest itself/receipts.
6. Independently extract ALL9 into fresh checkpoint/independent-restore, verify member hashes+PNG count, then run restored `source/verify_restored_master.py` in Blender with output receipt outside restored tree. Preserve source proofs and logs.
7. Upload all inventory items via Drive, parent/size/full download-backSHA256 check. Existing master/JPGs may be reused only if identicalSHA. Build/upload/verify external receipt with actual member count+restore proof.
8. Update shared Doc coreCODEX fields (protocol REQUIRES READY_FOR_REVIEW +newID/report/PDF/gallery/backup URLs) as well as appending red completion. Corefields are red/neutral, not green. Leave LAST_CHATGPT_REVIEWED/CHATGPT_STATUS/USER_VISUAL_APPROVAL/NEXT_PROMPT fields untouched. Add a short RED latest-delivery notice below top LATEST CODEX HANDOFF header so the user can find the delivery; retain old reviewed summary as history. Append full RED unique handoff `WORLD-OPEN-SHOPS-FULL-CENTER-CROWD-20261025-05B`. Fresh native Doc read + requiredRevisionId. Verify old green content/styles and all non-target text unchanged; index changes must account for edits.
9. Back up handoff/readback/receipts sidecar; final links + stop for visual review. No next task.

Drive folders (observed/created, no old checkpoint modified):
- Phase06: https://drive.google.com/drive/folders/1g807WYu5ZSlfaoLUXnQK4OFvzpHlXW7F
- Review: https://drive.google.com/drive/folders/1sRMTPGiTS8FYTVTg8wr3dj1Ya_4__PkM
- Checkpoint: https://drive.google.com/drive/folders/1RBUH2fDcXWhGUn32txMNqo6ejWKwFz7p
`checkpoint/drive-folders.json` stores returned IDs/URLs.

Already uploaded AND full download-back SHA verified (journals in checkpoint/uploaded-<ID>.json and verified-<ID>.json):
- Final master: https://drive.google.com/file/d/1zeEGl2vT_L0WiG0M7hEvUqddgxZfk-3q/view
- Optional in-progress source safety snapshot: https://drive.google.com/file/d/1DI-R6n-_mp6bP6ONHSL8UCdWlQhmQxjk/view ; SHA da59b9196b1224ee9210ff0c15224c5ca3c3d17693f65c2ad3fd131df9742df5. It is NOT the final complete phase checkpoint.
- Crowd-Center-Comparison.jpg: https://drive.google.com/file/d/1gRtAfn9kVuA9mYP9mry8AaKXtD79zfPf/view ; SHA ada34cb013d3e195fbf080dbc0151880dcc6528b1dc550f4108924a7813c877d
- Crowd-Eye-Comparison.jpg: https://drive.google.com/file/d/1Je08nwkpAxdB1SQYs5_eWSU9zB4KzbeT/view ; SHA9e1f3bfee9bda2724c9682f537f933684d706342e03ef6bb212e3a85410b5cb6
- Open-Shop-Comparison.jpg: https://drive.google.com/file/d/1m1ttBSto1503tE3EjqBseK8uansFf26h/view ; SHA20d7f662d08454094f0305e392b0d6da343fcfb7228220b6edde73b0f1d166a8

Current functions store keys: latestDoc/latestDocText (initial read), rev05BFolder/Review/Checkpoint, rev05BVerifyWorker=73528, rev05BUploadedRecords (5files), rev05BUploadHelper (JS function string). Helper refuses same-name/differingSHA, verifies metadata+raw full SHA and journals. If store lost, rebuild records from local uploaded JSONs and helper from tools metadata. NEVER reuse old Rev05A uploader targets.
Verifier session73528 is `stty -echo; python /workspace/wip-push-checkpoint/2026-10-22/verify-drive.py`. Send JSONurl/id/name/bytes/sha256/receipt via stdin, no echo; signedURL NEVER printed or persisted. Receipt records only id/name/size/hash/verified. Start a fresh no-echo worker if needed.

Disk: initially~516MiB free after removing ONLY the prior Rev05A independently verified temporary extraction (all127 hashes checked before removal; original sources/archive/checkpoints preserved). Current generated captures use space; monitor before packaging/full extraction. If necessary reduce PDF embedding quality85->80/subsample2 BEFORE uploading PDFs/archives, keeping all150 original PNGs untouched; this saves3 copies of PDF bytes. Do not delete prior backups/source/user work. Checkpoint sidecars/temporary independent restoration are excluded from final source archives except drive-folder metadata. Final master already safe on Drive.
