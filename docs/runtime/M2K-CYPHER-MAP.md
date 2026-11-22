# M2K Cypher map navigation

Choose **Map** or press M anywhere on the walkable route. The camera rises above the same canvas until the whole route is in view, from the market lane to the Aftermovie screen. Laptop and phone landscape views run the route left to right. Portrait phones run it bottom to top. The camera frames the route between the map header and the walking toolbar.

The map labels eight stops in walking order. The five destinations are Accommodation, Contact, Events, Team and Aftermovie. The three places are Market lane, Navigation board and Cypher plaza. A green dot marks **You are here**. Labels are placed around every marker dot and each other, and stay between the header and toolbar. Keyboard focus starts on the stop nearest the visitor.

Choosing a stop lowers the camera to that stop's walking pose with the same descent used to close the map, so there is no cut. Arrival focuses the destination's existing action: **View team murals**, **Play Aftermovie**, **View accommodation**, **Leave a message** or **Browse event posters**. Events needs the catalog, so its action appears only when the catalog is available. The preview URL changes to the stop's `?start=` value, so refresh and shared links open there. Market lane removes the parameter. M, Escape and **Close map** without a choice return the visitor to where they were, and focus returns to **Map**. Reduced motion shortens the rise and descent.

`ImmersiveRuntime.travelFromMap(pose)` is the only runtime addition. It acts only while the map is open and rejects non-finite poses. It reuses the existing descent, so the original controller still owns movement, collision and the return pose. The start poses that `?start=` already used now live in `components/gullyverse-runtime/cypher-map.ts`. The preview page, the map and the tests share them.

## Verify locally

Start Next on loopback with `GULLYVERSE_RUNTIME_PREVIEW=1`. The map needs no database connection.

```sh
npm run test:immersive
BREEZE_PREVIEW_ORIGIN=http://127.0.0.1:43997 node scripts/gullyverse/cypher-map.browser.cjs /absolute/path/to/review
```

The unit tests check:

- travel from every stop's open map, including rejected early and invalid requests
- walking collision after landing
- reduced motion
- the destination actions within reach on arrival
- map framing at seven laptop and phone sizes
- URL handling

The browser harness checks a 1120 × 700 laptop and an emulated iPhone 13 in portrait and landscape:

- all eight labels inside the viewport and clear of the header and toolbar
- no label overlapping another label or covering a marker
- M, button, Enter and touch travel
- focus on the arrival action and the return to **Map**
- one shared canvas
- refresh keeping the stop

Software-rendered Chromium and phone emulation do not measure device performance.
