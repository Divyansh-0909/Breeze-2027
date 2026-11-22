# M2H Cypher Team murals

Walk to the black-painted brick Team wall and choose **View team murals**. The gated preview also accepts `/runtime-preview/cypher?start=team` as a short route to the wall. The gallery focuses the original wall and returns to the exact walking pose on close. The same canvas stays mounted.

The carousel opens on Organising Committee and wraps through eight murals. Use the buttons, arrow keys or a horizontal touch swipe on the wall. A successful selection is kept in the preview URL for reload. The previous mural remains visible during loading or a failed request. Retry loads the requested artwork again.

The mural camera sits half a metre above the walking eye. It faces the wall straight on and shifts the lens vertically to fit the complete mural above the controls, including on narrow and landscape phones.

The Organising Committee texture already shipped with the lit plaza. Seven alternatives come from the sealed Rev15Z scene and match its decoded RGBA pixels. Each replaces the paint on the authored mural mesh at that team's original width. The wall mesh, normals, brick and baked illumination carry through each image. The original names and roles are available to screen readers. Regenerate the seven textures and the manifest with the following command.

```sh
python scripts/gullyverse/export-team-murals.py SEALED_MASTER.blend public/models/gullyverse/locked-rev15z-team
```

The exporter checks the frozen master SHA-256, eight ordered states, original UVs and exact decoded WebP pixels. It requires Blender 4.3.2 and Python with Pillow WebP support.

## Verify locally

Start the private Next preview with `GULLYVERSE_RUNTIME_PREVIEW=1` on loopback. The Team wall needs no database connection. Run the browser harness with the same origin and an existing output directory.

```sh
npm run test:immersive
BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43992 node scripts/gullyverse/cypher-team.browser.cjs /absolute/path/to/review
```

The harness exercises all eight murals, keyboard and touch controls, wraparound, image retry, selection links and return to walking. Chromium uses a software renderer and an emulated phone viewport.
