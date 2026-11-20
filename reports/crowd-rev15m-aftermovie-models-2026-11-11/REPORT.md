# Consistent crowd around the environment / Rev15M

The user requested that people throughout the environment look like the Aftermovie crowd. This revision replaces the nine remaining simple mannequins: three along the approach ramp and six beside the cypher. They share actual existing Aftermovie LOD0 mesh and material datablocks, including modeled faces, hair, clothing, hands and shoes. Nine distinct wardrobe archetypes and relaxed/social poses provide variation.

All 180 existing audience members, their placement and mesh data are retained. No extra people are scattered. The same nine horizontal positions and standing heights are preserved; uniform scale maintains proportions. The old proxy feet floated 9 cm above the modeled surfaces. The replacements meet the surveyed ramp or rooftop surface instead, recorded per person in `evidence/replacements.json`.

The current full environment is `delivery/Gullyverse-Rev15M-Consistent-Crowd.blend`. It has 43 scenes, including all 42 previous scene object memberships. The original Rev15L1 master is byte-identical and retained separately. All unrelated current-scene objects and light data are shared unchanged. The current eight-panel mural carousel has an independent Rev15M controller. The navigation board, 72-cell logo spacing and 10,676-cell LED loop are preserved.

`source/build.py` reuses the verified Rev15L1 base and the recorded source mesh bank and ground plan. `source/fresh-open.py` verifies the delivered master in a new Blender process, all nine placements/visibility, packed image state, retained audience, independent mural states and exact LED wrap. `source/render.py` produces native whole-scene comparison views. Source inspection scripts and exact plans are included for traceability. Native source images are not creatively edited.

Review the approach before/after, cypher, original Aftermovie audience and navigation views in `renders/`, the PDF in `review/`, or `GALLERY.html`. Visual approval remains pending. This is an authored scene revision; public app source, original runtime crowd GLBs, website integration, commits and deployment are outside this change.

The checkpoint contains the complete edited packed master, source, source inventories, review evidence, original-base references and repository pointers. Unchanged historic authoring sources are reused from the verified Rev15L1 checkpoint listed in `evidence/base-reference.json`.

Drive subphase: https://drive.google.com/drive/folders/1_tDZFHffgNjri-vwKIeld0eGWDTrUCRt

Complete checkpoint: https://drive.google.com/drive/folders/1mSU3X5vAWYf5bWPE5ISj8Gk-DWJ3_io1
