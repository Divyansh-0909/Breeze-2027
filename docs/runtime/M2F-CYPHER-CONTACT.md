# M2F Cypher Contact enquiry

In the gated cypher preview, walk to the enquiry window and choose **Leave a message**. The option appears when the visitor can reach the viewing position across the existing deck. The original controller saves the walking pose, brings the camera to the window, and restores the exact pose after dismissal. The form and the walking route share one canvas. The short link `/runtime-preview/cypher?start=contact` starts by the window.

On a laptop, the HTML form projects onto the authored message surface. Phones and smaller views use a readable sheet. Keyboard focus goes to the first field when the form opens and back to the enquiry button after it closes. Drafts stay in the same form across close, reopen, and failed submission. The 3D fallback links to the existing Contact page.

The gated form posts through `/api/preview-contact`. The server checks both preview flags and a disposable loopback PostgreSQL database before calling the existing Contact handler. The preview shows sending as unavailable when those settings are absent.

## Verify locally

```sh
node node_modules/typescript/bin/tsc --noEmit --incremental false
npm run test:immersive
node node_modules/tsx/dist/cli.mjs scripts/gullyverse/test-cypher-contact.ts /absolute/path/to/review
```

The last command creates a temporary database, applies the checked-in Contact migration, and launches the actual Next preview on loopback. Chromium walks from the plaza to the window, submits the desktop and emulated-phone fixtures, and checks failed submission, draft retention, focus return and the Contact fallback. The harness checks the two stored fixture rows before discarding the database.

Live deployment and the other destination interactions remain open.
