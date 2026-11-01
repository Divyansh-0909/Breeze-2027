# Rev09 independent restoration

Handoff WORLD-REV09-SQUARE-C180-20261028-3f637b22. This is a private Blender source/render study, not a website deployment or runtime GLB. No repository checkout is required to open the model.

Download ALL FIVE numbered final ZIPs from the Rev09 checkpoint folder. The final Drive archive index gives their exact names, byte sizes, SHA-256 values and links. Check every ZIP hash before extraction. Extract into one NEW empty folder, retaining paths; none of these archives replaces an older checkpoint. They are complementary ZIPs, not byte-split parts.

1. Rev09-01-Source-and-Evidence.zip — sealed packed editable master, recipe, validators, material provenance, report, gallery, file manifest and technical evidence.
2. Rev09-02-Protected-Baseline-Masters.zip — actual unchanged Rev08 master, actual original corrugated-art master and website-preservation fixture/source audit. No LFS-pointer substitutes.
3. Rev09-03-Before-PNGs.zip — nineteen matched old-crowd Rev08 control images.
4. Rev09-04-Square-and-Historical-PNGs.zip — nineteen new square images, two explicitly historical website-crowd controls, labelled furniture source inventory.
5. Rev09-05-Reviews-and-Walk.zip — phone/full/technical PDFs, original 40-second offline MP4 and all eighty genuine raw route frames.

Run `python source/verify_payload.py` from the extracted folder to check every payload byte/hash and relative gallery link. FILE-MANIFEST.json intentionally excludes its own hash. Archive hashes are in the separately verified Drive index. No credentials, node_modules, build output or cache is required or included.

Open `source/Gullyverse-Rev09-MultiStorey-Square-C180.blend` in Blender 4.3.2 or compatible newer Blender. Expected SHA-256: 3f637b223aff0fd4eb397ae6e51d821ed5de5675cf9707643a1cdf955821ab78 (15,261,739 bytes). All 33 image owners and required fonts are packed. Default scene: `REV09 / Multi-Storey Square + Previous Crowd`, variant `SQUARE C180`. Thirteen scenes retain all eleven Rev08 archives plus a comparison copy and the new candidate. The selected crowd is the exact earlier Blender C180; the website Man/Woman crowd remains archived only.

For independent reopen/preservation proof, using a terminal in the extraction root:

```sh
blender -b source/Gullyverse-Rev09-MultiStorey-Square-C180.blend -t 2 --python-exit-code 9 --python source/verify_reopen.py
GULLYVERSE_BASELINE_OVERRIDE="$PWD/source/baseline/Rev08-Protected-Original.blend" blender -b source/Gullyverse-Rev09-MultiStorey-Square-C180.blend -t 2 --python-exit-code 9 --python source/audit_preservation.py
```

Validation writes only JSON evidence; the master is not resaved. These evidence files may change on a later run, so verify the original payload BEFORE running local diagnostics. `source/verify_website.py` is optional and only applies if the exact preserved website checkout exists at the original path. It is not required to open or restore this packed Blender work.

To reproduce renders, invoke `render_square.py -- before`, `-- after`, or `-- web-history 04-front 03-aerial` with the packed master; `render_walk.py` samples the original 1–960 frame route. Render scripts set explicit cameras in memory and do NOT save the source. The top-plan renderer uses 91 m horizontal orthographic framing to include the entire housing envelope; this explicit camera override is recorded in capture metadata. The sealed master retains its original editorial camera setup.

Authoring recipe, only in a separate working copy: open `source/baseline/Rev08-Protected-Original.blend` and run `author_square.py` with GULLYVERSE_BASELINE_OVERRIDE set to that baseline's absolute path. This writes a newly authored master and authoring evidence into the copy; never run it over this sealed delivered checkpoint. A regenerated Blender file is not expected to reproduce a binary-identical master hash. The recipe preserves original object data and creates only the isolated new comparison/candidate scenes.

`GALLERY.html` works offline after all five ZIPs are extracted together. PDFs use compressed embeddings for phone downloads; the linked PNGs preserve full resolution. The walking movie is 80 real offline Blender frame samples encoded at 2fps for 40 seconds, NOT gameplay or hardware FPS. All five optional supports remain OFF; 12 original active lights remain exact. No glTF readiness, website integration or physical-device performance claim is made.

Ignore the superseded initial safety master in the checkpoint folder and any explicitly interim safety archive. The final direct master has `-Final.blend` in its Drive filename; the ZIP contains the normal sealed filename given above. Neither the initial safety snapshot nor Rev08's website-crowd variant is selected.

User visual approval of the square and original crowd remains pending. Steel rack/table source identity is still unresolved; no guessed furniture substitution is included. Do not automatically begin the next phase.
