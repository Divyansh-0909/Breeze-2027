# M2A — Native Contact journey, 15 November 2026 IST

The next implementation subphase connects the approved Contact frontage to the original movement/input services. This is a bounded integration, rather than a completed full-world visitor journey. Other destination chunks, the lane/gate connection, full shared-route navigation and Events/Team content adapters remain M2 work.

The private Next route is `/runtime-preview`, gated by server environment `GULLYVERSE_RUNTIME_PREVIEW=1`; the default route returns 404. The existing home, Aftermovie and other destination pages are not replaced. The same component also builds into an independently runnable standalone preview, with one Canvas through walking, map and form visits.

`ImmersiveRuntime` gains an optional native-space adapter and a generic focus/return interaction. The original acceleration, speed, look, delta clamp and transition clocks remain in that controller. Default quarry/Aftermovie state, pose, camera, opacity and map values match the saved pre-change controller bit-for-bit across 16,800 simulated frames. `useImmersiveInput` retains its keyboard/touch axes and editable-field behavior, while blocking walking/look during the form interaction. The original repository's files remain untouched; these edits exist only in the isolated worktree.

`native-space.ts` maps the frozen Contact wall's original tangent/normal into Three coordinates without scaling geometry. Native floor is 7.2m, eye height 1.7m and radius comes from the original controller. The narrow approach corridor stays on actual source pavement, outside the house overhang and deep potholes. Separate source geometry/UV comparisons and a 169-point BVH floor coverage check validate the corridor. The rendered adjoining ground includes lower pothole faces: the floor export must use explicit height bounds 6.5–7.5, rather than the original representative frontage's 7.15 lower limit.

The existing clean Contact GLBs, artwork, lighting and transparent heading remain byte-exact. A new adjoining ground chunk copies original source faces and old UVs, retains the original Generated frame for procedural colour conversion, and uses the same irradiance/OIDN pipeline. Ground lighting uses 1024px, 128 samples and linear-HDR mip generation; PBR colour conversion is 2048px. The old pilot's overlapping thin floor strip is hidden while the complete approach ground is displayed. This changes runtime partitioning, not the frozen art or native master.

The visitor walks within reach, opens the form, types without moving, and closes it to restore the exact prior walking position/heading/pitch. Desktop form projection remains inside the wide window; phone and no-WebGL fallbacks use readable HTML. Hash routes preserve approach/enquiry deep links, refresh and Back/Forward; the same form DOM retains drafts across visits and errors. Focus returns only after both the camera and enabled message button are ready. A reference-counted asset pool disposes late/cancelled loads and supports compatible PNG retry.

The loopback preview server starts disposable PostgreSQL and calls the actual existing Contact POST handler, rather than simulating success. It sends no email or messages externally. The Next preview enables sending only when `/api/preview-health` confirms both explicit isolated flags and a loopback test database. Live authentication/admin, schema/migration reconciliation and deployment remain separate; the existing migration gap for ContactSubmission is not hidden by fixture `db push`.

## Run

Restore the source/master seal and the prior clean-texture checkpoint, or use the self-contained standalone archive for review. Install repository/toolchain locked dependencies and pinned KTX/OIDN as described in TEXTURE-ALPHA-FIX.md. Set TMPDIR to a writable filesystem with space.

```sh
bash scripts/gullyverse/build-contact-ground.sh /absolute/frozen-Rev15Z.blend
node scripts/gullyverse/build-journey.mjs
node node_modules/tsx/dist/cli.mjs scripts/gullyverse/serve-journey.ts
```

The loopback server defaults to port 8897 and discards its database on SIGINT/SIGTERM. Its local test-only count endpoint is excluded from the Next application. For the optional Next preview, set `GULLYVERSE_RUNTIME_PREVIEW=1` and supply the isolated backend configuration; leave the flag unset for the normal website. No credentials or database contents belong in the checkpoint.

Behavior checks run with `npm run test:immersive` and `node scripts/gullyverse/contact-journey.browser.cjs`; the latter assumes the loopback server. Headless tests explicitly emulate foreground focus. SwiftShader and phone emulation do not establish physical-device FPS, GPU residency or soft-keyboard acceptance. Final check results, screenshots, PDF and preservation proofs are stored in this phase's checkpoint. No commits, pushes, merges, sharing changes or deployment.
