# Rev15T restoration

The complete packed native master is Gullyverse-Rev15T-Continuous-Asphalt-Gully-and-Cypher.blend. SHA256:

    8c0745fcb068ba8039a8196742e0b500e905026e842e09788e565d3c34a459fc

Its twelve verified parts, every byte count, SHA256 and authenticated Drive ID/link are indexed in delivery/Native-Master-Parts.json. Download all twelve into one empty directory, then run source/restore-master.py using its --index option. The helper checks every part and the assembled master and refuses to overwrite an existing output. The full master is independently restorable and includes all 49 native scenes and 95 packed images.

The source checkpoint ZIP contains the scripts, authored texture maps, configuration, selected source references, browser viewer and vendor license, native captures, PDF, evidence and current handoff documents. Its PAYLOAD-SHA256.json checks every payload. Check the ZIP itself against SHA256SUMS.txt.

The separately uploaded Rev15T-Asphalt-Ground-Additions.blend contains the thirteen new ground/detail objects and packed material data. It complements the complete master; it does not substitute for the surrounding environment.

Rev15T-Continuous-Asphalt-Ground.glb is the separate runtime ground asset. Put it in delivery/ beside viewer/, then serve the extracted checkpoint with an ordinary local HTTP server and open viewer/. The standalone viewer provides three fixed inspection views. It is not the public website or a replacement movement controller.

To reauthor from source, restore the unchanged Rev15S master and set source/road-layout.json's masterInput to its location. Its required SHA256 is afb20a12d58a782d570128a22b30581651a30233f1ef03ac5e5f11fbe3891cfd. This base remains verified in:

https://drive.google.com/drive/folders/1CDLGM466e7iUmb6BI5wQRKkQJClRtL4-

Run make-road-art.py in regular Python with NumPy/Pillow, build.py in Blender 4.3.2, then fresh-open-and-export.py and render.py in Blender. The PDF generator uses ReportLab, Pillow and pypdf with bundled DejaVu fonts. The browser check uses Playwright and /usr/bin/chromium and starts/stops its own local HTTP server.

The source scripts are relative to this report directory. Use an empty work directory and update output paths if /dev/shm is unavailable. Do not overwrite historical masters. The original smooth floor objects are retained, hidden, with navigationBaselineOnly metadata in Rev15T. They preserve the original footprint/grade for later movement integration. Do not use shallow render defects to change the original collision flow automatically.

All backups target losersamurai09@gmail.com. Source account cleanup is a separate pending migration step; CSD361 remains excluded. No Firecrawl calls were made for this implementation.
