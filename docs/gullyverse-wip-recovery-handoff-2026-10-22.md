# Completed recovery work prepared for WIP

Starting commit: `14f36da1a9b79a3b4926f7445bf0cde6c6c8f767`.
Target branch: `work-in-progress-2027`.

The user requested pushing the completed recovery work and leaving the current unfinished cave material/emboss study out. This checkpoint uses the exact saved pre-study state from 22 October 2026, verified against its SHA-256 inventory. The original dirty workspace is preserved. No reset, clean, art regeneration or public-default promotion is part of this handoff.

Included: the completed C8 3× scanned-material recovery, native-scale C9 recovery and fidelity corrections, Stage 3A integration, historical private cave comparison, editable Blender/source assets, runtime assets, reports, screenshots, recordings, authoring scripts and tests. Failed historical art remains labelled as diagnostic evidence; inclusion is not visual approval.

Excluded: the unfinished `cave-material-study` source/runtime/report directories, its scripts and test, `caveMaterialStudy.ts`, and its changes to four existing cave/shell files. Those four files use the saved pre-study versions. The unfinished study remains on disk, paused; its partial Drive upload is not a complete checkpoint.

C5.1 remains the ordinary default. Private comparisons retain their existing preview gate, including C8 `scanned-material-multi`, C9 `scanned-composition` / `geology-fidelity`, and Stage 3A `entranceReview=natural-cave`. The historical `deep-rock` diagnostic remains available without adoption. Global lighting, the stage, navigation, collision registry and quarry layout are unchanged.

Validation of this isolated pre-study state: production build PASS, 100 immersive unit tests PASS, final standalone TypeScript check PASS, lint PASS with existing warnings. The first TypeScript invocation before Next generated its ignored `next-env.d.ts` failed on image declarations; the build generated that standard file and the subsequent standalone check passed. No application change was needed. This push preparation does not claim fresh browser or physical-device acceptance. Prior reports retain the inherited geometry and browser readiness failures.

Complete source/art/runtime/evidence bytes already exist in the verified parent Drive checkpoint: https://drive.google.com/drive/folders/1XbZkyktnr2cLV-uXRmp_7ozRnyifnPMl . This handoff supplements that checkpoint with commit and validation metadata; previous backups are unchanged.
