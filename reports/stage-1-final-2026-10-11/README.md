# Stage 1 stabilization and acceptance evidence

- [Final acceptance report](../../docs/gullyverse-stage-1-final-acceptance.md)
- [Current user-approved baseline](../../docs/gullyverse-current-user-approved-baseline.md)
- [Matched before/after gallery](gallery.html)
- [Actual uninterrupted journey recording](acceptance/journey/recordings/full-journey.webm)
- [Journey browser trace](acceptance/journey/traces/full-journey.zip)
- [Physical-device verification procedure](PHYSICAL-DEVICE-PROCEDURE.md)
- [Evidence checksums and inventory](manifest.json)
- [Artifact/link validation](raw/artifact-validation.json)

Runtime regression checks and ten measured playback/return cycles pass; texture counts plateau. Current stage assets and user-approved spatial/lighting configuration are preserved. Physical GPU/mobile performance remains unverified, and native-resolution SwiftShader preparation timed out. The acceptance report retains failed runs and limitations. No commit, push, deployment or Stage 2 production work was performed.

## Git handoff

The user subsequently authorized committing and pushing this delivery. Reports describe the verification state before that authorization. Source, handoff documents and review evidence are included in Git. The recoverable `raw/current-approved-baseline.tar.gz` archive remains in the local workspace because its 616,058,995-byte size exceeds GitHub's 100 MB per-file limit. Its checksum remains in the evidence manifest. Generated Python caches, live server logs/PID and the duplicate Playwright recording filename are also excluded from Git. The named `full-journey.webm` recording and browser traces are included.
