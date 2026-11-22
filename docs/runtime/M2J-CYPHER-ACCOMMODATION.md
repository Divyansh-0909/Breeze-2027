# Cypher Accommodation preview

The Accommodation destination uses the transparent **COMING / SOON** graffiti on the locked Rev15Z Cypher house wall. The camera faces the wall straight on and fits both lines above the return button. The preview adds a walk-up button and lets visitors select the graffiti directly.

In the private preview, walk through the gate and head left into the forecourt, or use `/runtime-preview/cypher?start=accommodation` with `GULLYVERSE_RUNTIME_PREVIEW=1`. Select **View accommodation**, then choose **Back to walking** or press Escape to resume at the same position. The focused view provides a screen-reader status. The direct preview shows the same status as readable text if WebGL or the scene fails to load.

The preview uses the original plaza asset, including its local wall lamp. The lobby controller keeps ownership of the walking pose throughout the visit. There is no booking form.

## Verification

- `npm run test:immersive` checks the clear approach through the forecourt and the graffiti framing at four desktop and mobile sizes.
- `BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43997 node scripts/gullyverse/cypher-accommodation.browser.cjs <screenshot-directory>` exercises keyboard and touch, clicking the graffiti, returning on the same canvas, and the WebGL fallback. Start the private preview locally before running it.
