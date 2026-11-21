# M2G Cypher Events wall

The gated preview reads the existing `EventItem` catalog from disposable loopback PostgreSQL. Start near the wall at `/runtime-preview/cypher?start=events`, or walk across the cypher and choose **Browse event posters**. The camera uses the shared focus and return path. The eight poster meshes are found by their authored source names, so their placement and baked lightmaps carry through each page.

Pages contain up to eight events, using the middle positions first for partial pages. Unoccupied positions are hidden. Image aspect ratio is preserved and a text poster covers missing or failed images. Choose an event from the wall or the keyboard-accessible list to see its details and open its existing Events page. A catalog snapshot stays consistent while the scene is open and refreshes on reload. Empty and unavailable catalogs have separate messages.

The preview accepts the formats already written by the date controls: `yyyy-MM-dd` and `MMM do yyyy`. Events remain through the end of their final Asia/Kolkata calendar day. A closed registration stays visible through that day. Missing, unrecognized and inverted date ranges remain visible for review. The catalog read keeps expired rows and registrations in the database. Admin permissions and the underlying schema are unchanged. Time-of-day expiry and publishing controls require a reliable admin data contract.

## Verify locally

```sh
npm run test:immersive
node node_modules/tsx/dist/cli.mjs scripts/gullyverse/test-cypher-contact.ts /absolute/path/to/review events
```

The browser harness uses the actual Next preview and disposable Prisma schema. It checks a catalog of 18 rows with 17 active posters across three pages, linked details, a closed registration and same-canvas return. The local fixture database is discarded after the run.
