# M2F Cypher Contact enquiry

In the gated cypher preview, walk to the enquiry window and choose **Leave a message**. The option appears when the visitor can reach the viewing position across the existing deck. The original controller saves the walking pose, brings the camera to the window, and restores the exact pose after dismissal. The form and the walking route share one canvas. The short link `/runtime-preview/cypher?start=contact` starts by the window.

On a laptop, the camera frames the authored Contact Us graffiti and the HTML form projects onto the window's message surface. The runtime reads the heading mesh from the loaded plaza and adds a text heading only when that artwork is missing. On phones and short viewports, the lower view projects the inside edge of the window's upper border onto the scrollable form. The form follows that edge when the viewport changes, and the landscape panel stays narrower and shorter. Walking views aim 14° lower in portrait and 10° lower in landscape. The original walking pose, map framing and dedicated film shot are preserved. Keyboard focus goes to the first field when the form opens and back to the enquiry button after it closes. Drafts stay in the same form across close, reopen, and failed submission. The 3D fallback links to the existing Contact page.

The gated form posts through `/api/preview-contact`. The server checks both preview flags and a disposable loopback PostgreSQL database before calling the existing Contact handler. The preview shows sending as unavailable when those settings are absent.

## Verify locally

```sh
node node_modules/typescript/bin/tsc --noEmit --incremental false
npm run test:immersive
node node_modules/tsx/dist/cli.mjs scripts/gullyverse/test-cypher-contact.ts /absolute/path/to/review
```

The last command creates a temporary database, applies the checked-in Contact migration, and launches the actual Next preview on loopback. Chromium approaches the window, submits the desktop and emulated-phone fixtures, and checks failed submission, draft retention, focus return and the Contact fallback. The review captures a laptop at 1120 × 700 and emulated phones at 390 × 664, 320 × 568 and 844 × 390 CSS pixels. The harness checks the two stored fixture rows before discarding the database.

Live deployment and the other destination interactions remain open.
