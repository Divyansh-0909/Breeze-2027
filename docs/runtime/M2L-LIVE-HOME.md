# M2L Walkable gully and cypher on the home page

`/` now opens the walkable journey for every visitor. The original quarry and cave entrance plays first. **Enter Gullyverse** then hands off to the market lane, navigation approach, gate and full cypher on the same canvas. The private `/runtime-preview/cypher` route is unchanged and still needs `GULLYVERSE_RUNTIME_PREVIEW=1`.

- `?start=<stop>` opens a map stop directly, as in the preview. Market lane removes the parameter, so a refresh there replays the quarry entrance.
- The Contact window posts to the existing `/api/contact` endpoint (the `ContactSubmission` table must exist in the deployment's database). The preview-only note is hidden.
- The Events wall reads the live event catalog. If the database is unreachable, the posters stay and the Events action is hidden.
- The original hub remains as a fallback at `/?hub=classic`. Its own `/?arrival=…` URLs and `/aftermovie` keep the original persistent shell.

Verified with `npm run build`, `tsc`, `npm run test:immersive` (131 pass) and a software-rendered Chromium run of `/` → quarry → market (one canvas), `/?start=contact` → enquiry sent to `/api/contact`, and `/?hub=classic`.
