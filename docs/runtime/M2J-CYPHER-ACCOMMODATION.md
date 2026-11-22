# Cypher Accommodation preview

The Accommodation destination uses the transparent **COMING / SOON** graffiti and original lamp from the locked Rev15Z scene. The focused camera stays level and keeps the nearby house frontage in view. The preview adds a walk-up button and lets visitors select the graffiti directly.

In the private preview, walk through the gate and head left into the forecourt, or use `/runtime-preview/cypher?start=accommodation` with `GULLYVERSE_RUNTIME_PREVIEW=1`. Select **View accommodation**, then choose **Back to walking** or press Escape to resume at the same position. The focused view provides a screen-reader status. The direct preview shows the same status as readable text if WebGL or the scene fails to load.

The source scene contains a thin plaster plane over the house façade. In the browser bake its edges looked like a separate board. The preview hides that plane and transfers its baked lamp illumination onto the underlying plaster, blending the light into the original façade. The transfer is limited to the wall behind the graffiti and works with both the compressed lightmap and its HDR fallback. The original walking controller keeps ownership of the return pose.

## Verification

- `npm run test:immersive` checks the clear approach through the forecourt and the graffiti framing at four desktop and mobile sizes.
- `BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43997 node scripts/gullyverse/cypher-accommodation.browser.cjs <screenshot-directory>` exercises keyboard and touch, clicking the graffiti, returning on the same canvas, and the WebGL fallback. Start the private preview locally before running it.
