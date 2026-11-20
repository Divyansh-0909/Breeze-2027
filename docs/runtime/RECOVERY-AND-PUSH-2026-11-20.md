# Recovery and WIP publication — 20 November 2026

The user explicitly authorized committing and pushing all current work, including incomplete implementation, to work-in-progress-2027. This authorization supersedes the earlier private-phase no-push restriction for this checkpoint. Full website integration and production deployment are not marked complete.

The environment restart cleared the temporary implementation worktree while an eight-part M2A Drive upload was in progress. Three parts and an early safety source copy survived in Drive. The complete clean-texture checkpoint also survived. Recovery restored all 67 implementation source files byte-for-byte against the original M2A file manifest, plus 171 of 172 archived files exactly after rebuilding the missing runtime bundles. The remaining file is ground/manifest.json: its metadata was reconstructed and now records recovery provenance. Original ground geometry, old UVs, encoded mipmaps, denoised HDR, GLBs, shaders and artwork remain exact. The full 242,608,181-byte frozen Rev15Z master is included through Git LFS, SHA-256 89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041.

This checkpoint includes all physically available uncommitted project files, the clean texture/transparent-graffiti pipeline, the native Contact approach/form/return implementation, runtime assets, editable ground, lighting sources, reviews, evidence and the latest frozen art master. Historical reports contained 91 links to temporary folders that no longer exist. Those dangling machine-specific links are not committed as working assets; their exact inventory is in reports/github-checkpoint-2026-11-20/unavailable-ephemeral-links.json. The original Drive backups and recovery document remain the references for those older review payloads. Existing internal links are made relative for portability. Credentials, dependencies, build caches and temporary signed download references are excluded.

The original repository filesystem is full, so publication uses an isolated Git index/object store and a recovered source workspace in shared memory. Original local Git metadata and uncommitted files were not reset. GitHub is the durable current WIP snapshot after this push.

Current implementation: M0 audit and M1 clean lighting/alpha export are implemented; M2A Contact walking, focus/return, hash navigation, keyboard/touch form, isolated Contact POST persistence and failure/fallback behavior are implemented. Native Contact preview is behind GULLYVERSE_RUNTIME_PREVIEW=1 at /runtime-preview; it is 404 by default. Home, quarry entrance and Aftermovie retain their original behavior. The saved default-controller comparison matched 16,800 frames bit-for-bit. Recovered source validation reran all 111 immersive tests and TypeScript. Older browser/build evidence is dated 15 November; it is preserved as evidence, not described as a new physical-device test.

Remaining work includes full-world lane/cypher/gate chunk and collision integration, shared destination journeys, live Events/Team content adapters, final full-world night/specular matching, physical-device profiling and submission hardening. Live authentication/admin and deployment schema reconciliation remain separate. The submission deadline is 28 November 2026, Asia/Kolkata, hour unspecified.

Use Git LFS to hydrate large authoring and review payloads. Public runtime GLBs/textures remain regular Git files. See docs/runtime/M2A-CONTACT-JOURNEY.md and TEXTURE-ALPHA-FIX.md for local preview and export commands. For the source argument, use assets-source/gullyverse/locked-rev15z/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend after hydrating it.

Latest review PDF: https://drive.google.com/file/d/1WCfeAw0_1Ss_jucrKZw_0aF7DP2C993c/view
Recovery document: https://docs.google.com/document/d/1mUE4J2QCNMHk0ryoiSSOADbkjdwi3FN5IG5GZhoIBTU
Verified clean-texture checkpoint: https://drive.google.com/file/d/1IRa7nuHQpmVEW0mZ82rys2Ll2f1mJuRT/view
Frozen native source seal: https://drive.google.com/drive/folders/1pNvqnkT_Ic2XwMIe5v-_A37Vw7shLwcS

## Public-repository exclusions

Raw account-wide Drive migration inventories, maps, journals and the migration archive are excluded from the public commit. A project backup summary remains. Credentials, dependencies, build caches and expired machine-specific links are also excluded. Original private migration records remain unchanged in Drive/local storage.
