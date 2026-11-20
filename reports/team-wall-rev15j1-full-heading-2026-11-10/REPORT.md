# Rev15J1 — Organising Committee heading in full

10 November 2026. The user's requested change is limited to expanding the mural's abbreviated `OC` heading to **ORGANISING COMMITTEE**.

The new transparent artwork retains the existing gold, orange and hot-pink graffiti family with cream highlights, black outline and navy extrusion. The heading stays centred at the same position and 0.72 m height. Its width follows the artwork's natural aspect ratio (approximately 5.15 m); no horizontal image stretching is used. The lower edge remains above the portraits.

The source is the verified Rev15J master, SHA-256 `0a67481232bd52e9aedc2637564a71d3cbce6d8fb55c2464b860172bbc02d9f0`. Only the Organising Committee heading's copied mesh, UVs and material change in the new scene. Portraits, names, roles, wall, lights, navigation and the other seven team slides are retained. Coordinators remains excluded; Organising Committee remains first in the eight-slide carousel. The 39 previous scenes remain intact; the new master has 40 scenes.

Open `delivery/Gullyverse-Rev15J1-Full-Heading.blend`, select scene **REV15J1 / Organising Committee Full Heading**, run the packed `team_wall_rev15j1_controls.py`, and use Sidebar / Team Wall. All image assets are packed. The standalone viewer is `viewer/index.html`, served over local HTTP.

The heading PNG was made with `image_gen.imagegen`, using the existing team heading atlas as a style reference. The tool did not report its underlying model. The complete generated PNG is preserved byte-for-byte. Its visible alpha bounds define the plane's UV crop; no image stretching, painted-over names or portrait regeneration is involved. Source reference and generation metadata are included in `inputs/` and `evidence/heading-art.json`.

Validation is recorded in `evidence/blender-validation.json`, `evidence/fresh-open.json` and `evidence/browser.json`. The updated Organising Committee laptop view is a new render of the actual Blender scene using the original reference wall and world lighting. The other seven rendered views are reused byte-for-byte from Rev15J, supported by the unchanged art/world owners. The eight-page PDF updates its first page and keeps the other seven views.

Current Drive subphase: https://drive.google.com/drive/folders/1OMVLChKOO7v0NWhFzASxhiiXfIv6TKLE. Upload receipts and independent restore verification are saved under `checkpoint/` after completion. Earlier checkpoints remain protected. No website integration, commit, push or deployment is included in this heading-only update.
