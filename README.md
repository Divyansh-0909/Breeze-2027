# Breeze 2027

Next.js application on `work-in-progress-2027`. Cart checkout supports direct UPI payments into configurable receiving accounts, order-specific QR codes, and bank statement reconciliation.

## Local development

Use Node.js LTS and Git. React 19 and the Fiber 9 stack now have matching peers:

```powershell
npm ci
Copy-Item .env.example .env
```

Keep real credentials in the ignored `.env` file. The checkout backend needs a PostgreSQL development database; the admin screens need Supabase Auth and a `Roles` entry with `club_name = BREEZE`. Optional receipt uploads use the private Supabase `transaction-proofs` bucket.

Configure `DATABASE_URL`, `DIRECT_URL`, Supabase values, and SMTP values from `.env.example`. Set `NEXT_PUBLIC_APP_URL` to this application's actual origin.

For a fresh development database:

```powershell
npx prisma migrate deploy
npx prisma generate
npm run dev
```

For an existing database, check `npx prisma migrate status` and its schema before applying migrations. The additive payment migration is `prisma/migrations/20261007160000_order_payment_reconciliation/migration.sql`. An existing manually managed Supabase database may require baselining the older migration first; do not reset that database to install this feature.

## Preview without credentials

With the development server running:

- Customer checkout: http://localhost:3000/payments/preview
- Admin workflow: http://localhost:3000/payments/admin-preview
- Actual authenticated admin screen: http://localhost:3000/admin/breeze-admin/payments

The public preview pages use fictional records and make no payment, database, or email requests. Their QR encodes a non-payment preview URL. Enter sample customer details, then load the sample statement in the admin preview.

## Payment lifecycle

1. Checkout validates cart IDs, ticket variants, quantities, and registration availability. Prices are calculated on the server and snapshotted.
2. A random private checkout token and separate public `BZ27...` order reference are created. Each checkout retains its receiving account, UPI ID, recipient name, and prices.
3. Customer details are saved before the payment QR is shown. The order can be confirmed from a statement even if the customer closes the tab before clicking “I've paid.”
4. A QR and UPI link prefill recipient, amount, and the note `BREEZE <order reference>`. A payment request is not proof of success.
5. “I've paid” records a customer report. A full bank reference and receipt are optional fallback evidence. Receipt OCR runs locally, suggests a reference, and requires the customer to check its digits.
6. The customer checkout polls its own private token for confirmation. A pending customer report never confirms payment by itself.
7. Statement imports and the payment worker automatically approve exact eligible matches, create confirmed event/merch records, and queue confirmation emails and the existing `/reciept/<token>` receipt.

## Receiving accounts and real QR tests

Use **Payment accounts & statements** in the Breeze admin navigation.

Add the receiving account's label, bank name, last four account digits, UPI ID, and recipient name. Activate it for new checkouts. Existing checkouts retain their original payment destination when accounts change. Add a new account record instead of editing old destination details.

Before enabling **Confirm note test**, perform controlled payments using the supported UPI apps and this receiving account. Check that:

- The generated QR and mobile UPI link are accepted for the personal account.
- The exact amount and complete `BZ27...` order code reach the payment screen.
- The complete order code is present in the recipient's PDF/CSV bank statement.

Note preservation and personal-account UPI-link behaviour vary by app and bank. The checkbox records the verifying admin and time. Until verified, order-note-only matching is disabled; a complete customer-supplied bank reference can still be matched to an eligible credit. If a note is absent or changed, receipt/reference fallback or team review is required.

An order QR prefills payment information; it does not generate the bank UTR, lock the amount inside another app, expire an already-saved QR, or send a bank callback to the website.

## Statement imports

Choose the receiving account, then upload its bank PDF or CSV export (maximum 10 MB).

- CSV supports 1–15,000 rows, quoted descriptions, credit/debit columns, or an amount plus explicit CR/DR direction.
- Text PDFs support up to 100 pages. Scanned PDFs support up to 10 pages per upload with local English OCR.
- PDF/OCR extraction must be compared with the original. Where a reliable table is unavailable, extracted text is shown and corrected CSV can be supplied.
- Map columns, choose DMY or MDY, and validate. Calendar errors, invalid money, unknown direction, and shortened bank references block import.
- Browse all normalized transactions in pages of 100. Check the receiving account and extraction before importing.
- Original extracted text and corrected-row provenance remain private in the database. Statement files and credentials are not placed in public assets.
- Re-uploading a file or overlapping exports does not allocate a credit twice. Contradictory entries sharing a bank reference are held for review.

Example corrected CSV (fictional data):

```csv
Date,Description,Credit,Debit,Bank Reference
07/10/2026,UPI BREEZE BZ27ABCDEFGHJK,800.00,,627912345678
07/10/2026,UPI reversal,,800.00,627912345678
```

Automatic approval requires one reviewed incoming credit with the correct receiving account, exact server-stored amount, a full bank reference, and either the complete verified order note or the complete customer bank reference. Multiple claims, another order's code, conflicting entries, missing evidence, reversals, and payments outside the 30-day order window require review. An absent bank entry remains pending.

A later reversal flags an already confirmed order for team review; it does not silently delete registrations or initiate a refund.

## Jev and OCR

Set `TYPESAFE_API_KEY` and optionally `TYPESAFE_MODEL` (default `jev-latest`) in the server environment to enable Jev review of extracted statement text.

The [official TypeSafe API](https://docs.typesafe.ai/api) is called server-side using typed choices. Jev can suggest incoming/outgoing/reversal/uncertain classifications. It cannot invent a missing reference or override exact approval checks. No key is needed for deterministic matching; Jev is called only when an admin requests a review.

OCR uses Tesseract locally. Its English language model is downloaded on first use and cached in ignored `.payment-ocr-cache`; set `PAYMENT_OCR_CACHE` to a writable directory on the host if needed. OCR does not send bank documents to an external OCR service.

## Matching and email worker

Statement import in the admin screen runs matching in batches. Keep the worker running to process late reports, resume work after a closed admin tab, and deliver queued emails:

```powershell
npm run payments:worker
```

For a scheduled job:

```powershell
npm run payments:worker -- --once
```

The worker connects to the configured database and only processes reviewed statements. Deploy it as a server-side background process or scheduled job; it requires the dependencies installed by `npm ci`.

Approvals, bank-credit allocation, confirmed registrations, audit records, and email queue creation are transactional. Emails are claimed before sending so concurrent workers cannot send the same queued email together. Failed delivery can be retried from the admin queue. If a process crashes after SMTP accepts an email but before its status is saved, delivery is uncertain and the `SENDING` record needs operator inspection; automatic resending is intentionally avoided.

## Validation

```powershell
npm run test:payments
npm run test:payments:ocr
npm run test:payments:integration
npm run test:payments:browser
npm run build
```

Integration tests start an isolated PostgreSQL cluster bound to localhost with generated test credentials, apply both migrations, and stop it afterwards. They do not use the configured/live database or a real Jev key. Browser checks use installed Microsoft Edge and the public preview pages; set `PAYMENT_TEST_URL` to test another local origin.

Test clusters, screenshots, and OCR caches are ignored. Payment account/statement/credit/audit/email tables have row-level security with no browser-role access policies. Admin payment APIs check authentication, the BREEZE role, and request origin.

## Gullyverse vertical slice

`/` and `/aftermovie` share one persistent immersive renderer in the public
layout. Enter the tunnel, walk with WASD/arrows (or the basic touch pad), and
cross the Aftermovie threshold. Walk backward through the viewing area's
return threshold to reach the hub. Open **Map** (or press M) for the same travel
system. Direct `/aftermovie` entry skips the introduction. **Use without 3D**
provides native video and existing festival information links.

The major tunnel/quarry meshes are temporary movement blockouts. The original
Aftermovie stage, crowd, and three-panel LED wall remain. See
[implementation and acceptance report](docs/immersive-vertical-slice.md) and
[Blender environment pipeline](docs/gullyverse-environment-pipeline.md).

```powershell
npm run test:immersive
npm run build
npm start
```

In another terminal, measure the production build on installed Chrome:

```powershell
$env:GULLYVERSE_MODE = 'production'
npm run perf:immersive
```

The runner checks the complete loop, history, direct entry, playback, touch,
reduced motion, loading failures, ten return trips, and context loss. It writes
rendered-frame metrics and screenshots to ignored `.gullyverse-artifacts`.
Use `GULLYVERSE_BASE_URL`, `CHROME_PATH`, and `GULLYVERSE_PROFILES` to choose the
origin, browser executable, and profiles. Mobile emulation is not physical
device validation. Append `?diagnostics` to expose read-only performance data
and the runtime to the browser runner; ordinary visits do not collect samples.
