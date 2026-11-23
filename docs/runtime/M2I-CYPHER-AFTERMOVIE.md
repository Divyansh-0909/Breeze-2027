# M2I Cypher Aftermovie screen

The screen at the rear of the cypher loops `/after-movie.mp4` for the whole visit, starting muted (browsers allow muted autoplay) and pausing while the tab is hidden (`cypher-screen-film.ts`). Its sound is the gully's music: after the visitor's first click, tap or key press it plays from the screen's PA and, band-passed, from the shop radio in the lane, in sync with the picture (see [M2O](M2O-SOUND-DESIGN.md)). Approach the screen and choose **Watch Aftermovie** (E) or tap a screen panel to watch it: the film restarts from the beginning and plays directly while the rest of the gully ducks. The private preview has a shortcut at `/runtime-preview/cypher?start=aftermovie`. The three authored screen panels share one video texture and keep their original crop across the full screen.

The **Sound on / off** button (or V) is the gully's sound setting. **Exit Aftermovie** and Escape restore the exact walking pose; the film keeps looping on the screen. Media failures show a retry message and a direct video link. The direct preview offers the same video link when WebGL is unavailable.

## Verify locally

Start Next on loopback with `GULLYVERSE_RUNTIME_PREVIEW=1`. The Aftermovie screen uses the existing media file from the repository and needs no database connection. Run the browser harness with the local origin and an existing output directory.

```sh
npm run test:immersive
BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43995 node scripts/gullyverse/cypher-aftermovie.browser.cjs /absolute/path/to/review
```

The browser harness plays the actual 1920 × 1080 film, checks audio toggling, end and exit, media failure and retry, the no-WebGL link, and the same canvas on laptop and emulated phone viewports.
