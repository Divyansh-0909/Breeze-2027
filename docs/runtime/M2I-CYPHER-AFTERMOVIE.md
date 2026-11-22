# M2I Cypher Aftermovie screen

Approach the screen at the rear of the cypher and choose **Play Aftermovie** or tap a screen panel. The private preview has a shortcut at `/runtime-preview/cypher?start=aftermovie`. The existing stage player streams `/after-movie.mp4` only after playback starts. The three authored screen panels share one video texture and keep their original crop across the full screen.

Playback starts muted. **Enable sound** and **Mute sound** switch the audio during playback. **Exit Aftermovie**, Escape, and the end of the film restore the exact walking pose and the original still. Leaving the page or losing the 3D context releases the video. Media failures return the visitor to the Play button and offer a direct video link. The direct preview offers the same video link when WebGL is unavailable.

## Verify locally

Start Next on loopback with `GULLYVERSE_RUNTIME_PREVIEW=1`. The Aftermovie screen uses the existing media file from the repository and needs no database connection. Run the browser harness with the local origin and an existing output directory.

```sh
npm run test:immersive
BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43995 node scripts/gullyverse/cypher-aftermovie.browser.cjs /absolute/path/to/review
```

The browser harness plays the actual 1920 × 1080 film, checks audio toggling, end and exit, media failure and retry, the no-WebGL link, and the same canvas on laptop and emulated phone viewports.
