# Stage2B review package

This self-contained evidence/source package contains the report, actual browser PNGs/recordings, capture metadata, raw measured data, tests, source patch and original Blender authoring/exports. It is not a complete runnable application checkout or a deployment.

Open `gallery.html` beside this README, or serve the extracted package root with `python -m http.server 8000` and open `/reports/stage-2b-first-wall-2026-10-12/gallery.html`. Main report: `docs/gullyverse-stage-2b-first-wall-integration.md` at package root. Editable asset: `assets-source/gullyverse/first-wall-section/first-wall-section.blend`; runtime combined asset: `public/models/gullyverse/first-wall-section/first-wall-section.glb`. Other GLBs are alternatives and should not all be mounted visible or downloaded redundantly.

For interactive quarry preview use the existing application checkout at the recorded baseline plus these bounded source changes and assets, following the main report's opt-in local build instructions. Default production appearance is preserved. This package contains relevant source for review, not dependencies/private environment configuration or unrelated site data.

The large recoverable pre-edit source/assets snapshot remains in the workspace backup directory and is deliberately not packaged. Its hash inventories/preservation results are included. Source master/maps are original; provided reference photographs are comparison material only. No credentials, `.env`, `.vercel`, `.git`, application databases, payments/admin data or dependencies are included.

Acceptance images are under `acceptance/`; unchanged initial captures under `baseline/`; rejected trial screenshots under `exploratory/` are clearly labeled in the report. Individual PNG resolution is retained. SwiftShader performance is not physical GPU/mobile acceptance.
