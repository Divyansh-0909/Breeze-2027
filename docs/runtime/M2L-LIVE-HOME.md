# M2L Walkable gully and cypher on the home page

`/` now opens the walkable journey for every visitor, starting in the market lane (since 23 November 2026, at the user's request). `/?start=quarry` keeps the original quarry and cave intro, where **Enter Gullyverse** hands off to the market lane, navigation approach, gate and full cypher on the same canvas. The private `/runtime-preview/cypher` route is unchanged and still needs `GULLYVERSE_RUNTIME_PREVIEW=1`.

- `?start=<stop>` opens a map stop directly, as in the preview. Market lane removes the parameter, so a refresh there reopens the market lane.
- The Contact window posts to the existing `/api/contact` endpoint (the `ContactSubmission` table must exist in the deployment's database). The preview-only note is hidden.
- The Events wall reads the live event catalog. If the database is unreachable, the posters stay and the Events action is hidden.
- The original hub remains as a fallback at `/?hub=classic`. While in it, the hub keeps `hub=classic` on the URLs it writes, so travel and refresh stay in the classic hub. Old `/?arrival=…` links from earlier visits open the new journey. `/aftermovie` keeps the original persistent shell.

Verified with `npm run build`, `tsc`, `npm run test:immersive` (131 pass) and a software-rendered Chromium run of `/` → quarry → market (one canvas), `/?start=contact` → enquiry sent to `/api/contact`, and `/?hub=classic`.
