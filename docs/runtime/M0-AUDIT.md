# Art-locked website implementation — M0

User locked Rev15Z on 14 November 2026. Deadline: 28 November 2026, Asia/Kolkata; submission hour unspecified. This supersedes the old prompt's unconfirmed freeze and Rev15V2 input. The full website is the goal; the first implementation milestone is a representative export and runnable private preview.

## Verified starting point

- Original `work-in-progress-2027`, HEAD `0e1e23dd2f5181df202d862d147067249bc55a41`.
- Private worktree `/dev/shm/Breeze-2027-runtime`, branch `codex/locked-world-runtime-20261114`, same HEAD. No commits, pushes, merges, PRs or deployment.
- Frozen native SHA-256 `89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041`: 242,608,181 bytes, 63 scenes, 146 packed images. Full native scene: 3,230 objects, 1,970,362 triangles, 194 materials, 42 lights. Latest scene is `REV15Z / Wide Contact window and restored graffiti`.
- React 19, R3F 9, Three 0.169 and Next 15. Existing persistent immersive shell owns `/` and `/aftermovie`. Other destinations currently leave that shell. Thirty page routes inventoried in `M0-audit.json`.
- Original quarry controller/input/camera/navigation files retain their pre-task hashes. 106 existing immersive tests pass. TypeScript passes. Initial prerender failed without Supabase settings. After the user selected an isolated backend, the full Next production build passed using disposable local PostgreSQL and an anonymous auth placeholder. The actual Contact POST rejected invalid input without inserting, persisted a valid test submission, and the catalog read seven fixture events. No hosted backend or live credentials were used.
- Original quarry floor/bounds differ from the native lane/cypher. A coordinate and collision adapter is required before mounting the new level; changing camera/controller behavior is not required.

## Visitor journey backlog

| Priority | Destination | Current behavior | Next implementation and dependency | Owner |
|---|---|---|---|---|
| P0 | Entrance → hub → return | Existing quarry/cave and controller work | Keep controller and camera ownership; add native frame/floor mapping and collision; depends on exported chunks | Implementation |
| P0 | Main Stage / Aftermovie | `/aftermovie` already shares shell with home | Preserve existing video/stage and departure/return lifecycle; do not invent a second finished stage | Implementation |
| P0 | Events | Prisma catalog, category/detail routes; landing limits results | Stable event-ID poster slots/pages, missing-poster/loading/empty states; define typed end-time and publication policy before automatic expiry | Implementation + festival admin |
| P0 | Contact | `/api/contact`, ContactSubmission and admin inbox exist | Mount locked wide window, use existing endpoint, suspend movement/pointer lock while typing, restore focus/return | Implementation |
| P1 | Team | Separate scene; eight native mural states ready | Shared-canvas carousel, preserve approved images, names and roles | Implementation |
| P1 | Accommodation | Native COMING/SOON; no completed booking route | Coming-soon destination and readable HTML fallback; no invented booking | Implementation |
| P1 | Past Sponsors | Native LED display; `/sponsors` redirects home | Preserve hanging loop and logo spacing; keep current route policy | Implementation |
| P0 | All destinations | Existing navigation registry only hub/aftermovie | Expand explicit registry/state machine, neighbor prefetch, cancellation, cleanup; verify back, refresh and deep links | Implementation |

The current club dashboard is read-only for events; BreezeAdmin owns writes. Existing date strings are presentation data. Do not silently grant clubs new permissions or infer reliable expiry timestamps from those strings.

## Concrete file plan

| Files | Change | Milestone |
|---|---|---|
| `scripts/gullyverse/export-plan.json`, `export_locked.py`, `relight.py`, `finish_lightmap.py`, `reexport.py`, `collision.py`, `postprocess.mjs`, `build-pilot.mjs` | Versioned immutable-source export, PBR conversion, explicit lightmap UVs, separate collision/triggers, measured compression, repeatable private build | M1 implemented; quality gates reported separately |
| `components/gullyverse-runtime/PrivatePilot.tsx`, form/CSS/HTML, `public/models/gullyverse/locked-rev15z-v1/` | Isolated actual-GLB inspector, one Canvas, KTX2/Meshopt/HDR baseline, resource leases and retry | M1 implemented; no production route import |
| `components/immersive/world.ts`, `navigation.ts`, `runtime.ts`, `ImmersiveShell.tsx`, `HubScene.tsx` | Private feature-flagged registry/chunk adapter and transition lifecycle; retain original input/controller/camera contracts | M2 pending |
| `app/(user)/ClientLayout.tsx`; destination pages and `WorldOverlays.tsx` | Keep one canvas across approved destination routes; lazy HTML overlays and safe fallbacks | M2 pending |
| `lib/events/catalog.ts`, Events wall adapter; `app/api/contact/route.ts` only if an actual contract gap requires it | Existing content adapters; stable variable poster arrangement, form integration | M2 pending |
| `components/immersive/rendering.tsx`, chunk materials/manifest | Approved night match, low-cost fog and supported quality tiers | M3 pending |
| `scripts/perf-gullyverse.mjs`, `tests/immersive/`, private browser checks | Actual route/cleanup/performance/hardening evidence | M4–M5 pending |

## Critical path and acceptance

M1 representative pipeline: 1–2 days. M2 journeys/content/collision: 3–5 days. M3 night match/quality tiers: 2–3 days. M4 physical-device profiling: 1–2 days. M5 hardening: 2–3 days. These are estimates, not completion claims; the upper bounds exceed the remaining two weeks, so prioritize P0 navigation, loading, content and stability, overlap validation, and reserve final days for fixes.

Targets are about 60 FPS desktop and at least 30 FPS mid-range phone, measured on real hardware. SwiftShader/emulated phone captures do not prove those targets. Acceptance requires fixed-view Blender/browser comparisons, no console/network/GL errors, controlled resource growth, reachable routes and accessible fallbacks. Full M1 visual acceptance remains open if the report records a lighting mismatch. No aesthetic redesign and no production deployment without authorization.

Original repository pre-existing edits remain intact. Routine backups use separate phase/subphase folders in the authorized losersamurai09-owned Breeze Drive. Source seals and checkpoints include restoration instructions and download-back SHA-256 verification; credentials, dependencies and caches are excluded.

The ContactSubmission model/handler exists, but the checked-in migrations do not create that table. The isolated test used `prisma db push` against a disposable database. Deployment schema/migration reconciliation remains M2; successful fixture tests do not prove a live admin inbox or hosted authentication.
