# M2L Walkable gully and cypher on the home page

`/` is the walkable gully and cypher for every visitor, starting in the market lane. Since 23 November 2026, at the user's request, the live site has no quarry: the quarry intro, the classic quarry hub (`?hub=classic`) and the quarry Aftermovie are gone, and `/aftermovie` redirects to the cypher's Aftermovie screen (`/?start=aftermovie`). The quarry code stays in the repository because the gully's walking controller shares it. The private `/runtime-preview/cypher` route is unchanged and still needs `GULLYVERSE_RUNTIME_PREVIEW=1`.

- `?start=<stop>` opens a map stop directly, as in the preview. Market lane removes the parameter, so a refresh there reopens the market lane.
- The Contact window posts to the existing `/api/contact` endpoint (the `ContactSubmission` table must exist in the deployment's database). The preview-only note is hidden.
- The Events wall reads the live event catalog. If the database is unreachable, the posters stay and the Events action is hidden.

Verified with `npm run build`, `tsc`, `npm run test:immersive` (131 pass) and a software-rendered Chromium run of `/` (market lane), `/?start=contact` (enquiry sent to `/api/contact`), and `/?start=quarry`, `/?hub=classic` and `/aftermovie`, which all open the gully.
