# Actual night lighting / road review

13 November 2026. Four 1440 × 900 native captures show the gully lane and cypher roads, with a wide and close view of each. They use the current Rev15T1 saved night lighting. The painted circle is absent.

The world, lights, exposure, look, gamma and render engine were checked before and after every capture and remained identical. No inspection lights were added and no image brightening was applied. Only review cameras, output resolution and JPEG settings changed in memory. The native master was not saved or modified.

The current lighting leaves much of the cypher centre in shadow. The closer views show the road near the existing shop and Events lights. These are native scene captures; production website integration remains pending.

[Review PDF](https://drive.google.com/file/d/10bnZ4aTMnLJ2IRUhpa4OUGrZCEa5WWvb/view).

[Review backup folder](https://drive.google.com/drive/folders/1ULlzqn-bv-L-oqxh8olDkSMZ8Meu57hF).

The source scene is unchanged Rev15T1, working-file SHA256 5f32cb917b1f2d8037e1445b8bfad69462be28dde7e1194a230c8a65fd720a09. Its verified full Rev15T base and native material delta are indexed in delivery/Source-Scene-Dependencies.json. This read-only review does not duplicate that native checkpoint.

The archive includes all four original JPEGs, the PDF, source scripts, fonts/license and verification evidence. PAYLOAD-SHA256.json checks every payload. Extract into an empty directory; repository-relative report paths are preserved.

To recreate the views, restore the native scene through the Rev15T1 checkpoint and run source/render.py with Blender 4.3.2. If using a freshly reconstructed native save, supply --source PATH and --expected-sha256 SHA256 for that verified file after Blender's -- separator; reconstructed Blender saves can differ in binary layout. The script checks the active scene and preserves its lighting. Create the renders/ directory before running. Generate the PDF with source/create-review.py in Python using ReportLab, Pillow and pypdf.
