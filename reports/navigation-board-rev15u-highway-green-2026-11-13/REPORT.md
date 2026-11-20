# Rev15U1 / Bilingual highway navigation

14 November 2026. The user requested the supplied Indian highway signs' green backgrounds, white borders and matching lettering, then added Hindi above English, taller destination panels, 45-degree direction arrows and Accommodation in place of Schedule. The digital sponsor board was explicitly excluded from changes.

All six physical destination plaques are now 0.68 m tall, increased from 0.55 m. Their orientations and the five upper plaque centres are preserved. The Past Sponsors plaque grows upward by 0.13 m, shifting its centre upward by 0.065 m while preserving its lower edge and the original short LED hang. The Gullyverse header retains its size and orientation. Green #087655 and white #F5F6F0 follow the references. English uses Overpass Medium and SemiBold, a Highway Gothic interpretation; Hindi uses correctly shaped Noto Sans Devanagari. Font sources, licenses, translations and shaping source are included. The four side arrows are diagonal: Events and Accommodation point up-left; Team and Contact Us point up-right. Aftermovie still points up. Labels are fitted within the taller panels.

| English | Hindi |
|---|---|
| Gullyverse | गलीवर्स |
| Aftermovie | आफ्टरमूवी |
| Events | कार्यक्रम |
| Team | टीम |
| Accommodation | आवास |
| Contact Us | संपर्क करें |
| Past Sponsors | पूर्व प्रायोजक |

The digital sponsor screen, casing, hangers, cable, screws, spill light, shader and native animation remain unchanged. All 62 sponsor marks retain the 72-cell gaps and 10,676-cell loop. Browser LED shader code, atlas and sponsor manifest are byte-identical to the prior version. Native frame/wrap tests and browser pixel-identical wrap, scrolling and mobile overflow checks passed.

The active master is `/dev/shm/Gullyverse-Rev15U1-Bilingual-Highway-Navigation.blend` (216,945,301 bytes; SHA256 `50fa05b16833cef444aef4bb1573eb4da042cc74a9f99b3fd5341a6da67f5975`). It contains 53 scenes, preserving the complete 52-scene T3 history, 109 packed images and both packed English fonts. Seven new packed images preserve correct Hindi conjunct and vowel-mark shaping. The corrected T3 potholes and all four road meshes, UVs and colours remain unchanged, as do the original movement source, crowd, shops, murals, world, lights and exposure. The earlier English-only styling draft is preserved separately in the parent Drive phase and history/english-only within the source checkpoint.

Fresh native opening and actual restoration from the verified T3 base plus packed U1 styling delta passed. The restored file was reopened in a separate Blender process to verify panel orientations, height, Hindi artwork, road preservation and the unchanged digital display. Native recovery reuses the complete T2 backup and T3 ground delta; see RESTORE.md and delivery/Dependency-Index.json. Whole-file serialization hashes can differ while verified scene content matches.

The [review PDF](https://drive.google.com/file/d/1VsZUfuLocVD97oZjX0h97_QXBUDAAx10/view?usp=drivesdk) is also saved as `review/Breeze-Bilingual-Highway-Navigation-Review.pdf`, with before/after and close-up views under the actual saved night lights. No inspection lighting or post-capture brightening is used. White paint takes on the existing warm light's cast. An occluded oblique draft capture is excluded from the PDF.

The separate runtime board asset and complete private viewer include the bilingual signs and original sponsor display logic. Full-world production website integration, including an Accommodation destination route, remains pending. This phase changes the editable 3D scene and its private board preview. No commit, push, merge, deployment or Firecrawl use occurred.

[Versioned bilingual Drive subphase](https://drive.google.com/drive/folders/1TR4sTlBjKOAoHEfoNKwHh3C8MahQ483D). Source checkpoint, dependency IDs, original/edited native components, runtime asset, visual evidence, restoration instructions, checksums and authenticated upload receipts are included.
