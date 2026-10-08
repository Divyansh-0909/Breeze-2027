import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { createServer } from "node:net";
// @ts-expect-error The package exports types via node16 resolution; tsx resolves it at runtime.
import EmbeddedPostgres from "embedded-postgres";
import { NextRequest } from "next/server";

async function main() {
  const listener = createServer();
  await new Promise<void>(resolve => listener.listen(0, "127.0.0.1", resolve));
  const port = (listener.address() as { port: number }).port;
  await new Promise<void>(resolve => listener.close(() => resolve()));
  const directory = path.resolve(".payment-test-data", randomUUID());
  if (!directory.startsWith(path.resolve(".payment-test-data") + path.sep)) throw new Error("Invalid isolated test directory.");
  const password = randomBytes(20).toString("hex");
  const database = new EmbeddedPostgres({ databaseDir: directory, user: "postgres", password, port, persistent: true, createPostgresUser: false, postgresFlags: ["-h", "127.0.0.1"], onLog: () => {}, onError: () => {} });
  let prisma: typeof import("../../lib/prisma").prisma;
  try {
    await database.initialise(); await database.start(); await database.createDatabase("breeze_payment_tests");
    process.env.DATABASE_URL = process.env.DIRECT_URL = `postgresql://postgres:${password}@127.0.0.1:${port}/breeze_payment_tests`;
    delete process.env.EMAIL_HOST; delete process.env.EMAIL_USERNAME; delete process.env.TYPESAFE_API_KEY;
    const migration = spawnSync(process.execPath, [path.resolve("node_modules/prisma/build/index.js"), "migrate", "deploy"], { env: process.env, encoding: "utf8" });
    assert.equal(migration.status, 0, migration.stderr);
    ({ prisma } = await import("../../lib/prisma"));
    const { createCheckout, submitPayment } = await import("../../lib/payments/customer");
    const { approvePayment, reconcileAccount } = await import("../../lib/payments/service");
    const { csvGrid, suggestColumns } = await import("../../lib/payments/statements");
    const { commitStatement } = await import("../../lib/payments/import");
    const { sha256 } = await import("../../lib/payments/core");
    const accountA = await prisma.paymentAccount.create({ data: { label: "Test account A", bankName: "Test bank", accountLast4: "1234", upiId: "test-a@bank", payeeName: "Test A", createdBy: "TEST", active: true, noteMatchingVerified: true } });
    const accountB = await prisma.paymentAccount.create({ data: { label: "Test account B", bankName: "Test bank", accountLast4: "5678", upiId: "test-b@bank", payeeName: "Test B", createdBy: "TEST" } });
    await assert.rejects(prisma.paymentAccount.update({ where: { id: accountB.id }, data: { active: true } }), /Unique constraint/);
    const eventId = randomUUID();
    await prisma.eventItem.create({ data: { id: eventId, event_name: "Integration event", event_price: 800, event_pair_price: 1500 } });
    const request = (body: unknown) => new NextRequest("http://localhost:3000/api/checkout", { method: "POST", headers: { "Content-Type": "application/json", origin: "http://localhost:3000" }, body: JSON.stringify(body) });
    const checkout = async (cart: Record<string, Record<string, number>> = { [eventId]: { SINGLE: 1 } }) => {
      const response = await createCheckout(request({ cart, amount: 1 }));
      assert.equal(response.status, 200, await response.clone().text());
      return (await response.json()).id as string;
    };
    const prepare = async (token: string, email: string) => {
      const form = new FormData();
      for (const [key, value] of Object.entries({ token, stage: "prepare", name: "Example Student", email, phone: "9876543210", rollNumber: "TEST123", college_status: "Example College, 2027", amount: "1" })) form.set(key, value);
      return submitPayment(new NextRequest("http://localhost:3000/api/pay", { method: "POST", headers: { origin: "http://localhost:3000" }, body: form }));
    };
    const token = await checkout();
    const prepared = await prepare(token, "first@example.invalid");
    assert.equal(prepared.status, 200, await prepared.clone().text());
    const preparedBody = await prepared.json();
    assert.equal(new URL(preparedBody.paymentUrl).searchParams.get("am"), "800.00");
    let order = await prisma.submittedTransaction.findUniqueOrThrow({ where: { token } });
    assert.equal(order.amount, BigInt(800)); assert.equal(order.paymentAccountId, accountA.id);
    assert.equal((order.pricingSnapshot as Record<string, Record<string, number>>)[eventId].SINGLE, 800);
    assert.equal((await prepare(token, "first@example.invalid")).status, 200);
    assert.equal(await prisma.submittedTransaction.count({ where: { token } }), 1);
    assert.equal((await createCheckout(request({ cart: { [eventId]: { SINGLE: -1 } } }))).status, 400);
    assert.equal((await createCheckout(request({ cart: { [randomUUID()]: { SINGLE: 1 } } }))).status, 400);
    assert.equal((await createCheckout(new NextRequest("http://localhost:3000/api/checkout", { method: "POST", headers: { origin: "https://untrusted.invalid", "Content-Type": "application/json" }, body: JSON.stringify({ cart: { [eventId]: { SINGLE: 1 } } }) }))).status, 403);
    console.log("PASS: checkout validation, server-authoritative amount, pre-payment persistence, and retries");

    await prisma.$transaction([prisma.paymentAccount.update({ where: { id: accountA.id }, data: { active: false } }), prisma.paymentAccount.update({ where: { id: accountB.id }, data: { active: true } })]);
    const nextToken = await checkout();
    assert.equal((await prisma.pendingTransaction.findUniqueOrThrow({ where: { id: nextToken } })).paymentAccountId, accountB.id);
    order = await prisma.submittedTransaction.findUniqueOrThrow({ where: { token } });
    assert.equal(order.paymentUpiId, "test-a@bank");
    console.log("PASS: account rotation preserves existing order destinations");

    const day = new Date(Date.now() + 330 * 60000).toISOString().slice(0, 10);
    const importCsv = async (accountId: string, description: string, amount: string, bankReference: string, direction = "CREDIT", nonce = randomUUID()) => {
      const csv = `Date,Description,Credit,Debit,Bank Reference\n${day},${description},${direction === "CREDIT" ? amount : ""},${direction === "DEBIT" ? amount : ""},${bankReference}\n`;
      const grid = csvGrid(csv);
      const statement = await prisma.bankStatement.create({ data: { accountId, fileHash: sha256(csv + nonce), filename: "test.csv", format: "CSV", extractedRows: { headers: grid.headers, rows: grid.rows, warnings: [] }, sourceText: csv, importedBy: "TEST" } });
      const input = { statementId: statement.id, columns: suggestColumns(grid.headers), dateOrder: "DMY" as const, accountConfirmed: true, extractionConfirmed: true };
      return { result: await commitStatement(input, "TEST"), input };
    };
    const firstImport = await importCsv(accountA.id, `UPI BREEZE ${order.paymentReference}`, "800.00", "612345678901");
    assert.equal(firstImport.result.imported, 1);
    assert.equal((await commitStatement(firstImport.input, "TEST")).alreadyImported, true);
    const overlapping = await importCsv(accountA.id, `UPI BREEZE ${order.paymentReference}`, "800.00", "612345678901");
    assert.equal(overlapping.result.imported, 0);
    assert.equal(await prisma.bankCredit.count({ where: { accountId: accountA.id } }), 1);
    const reconciled = await reconcileAccount(accountA.id, "TEST");
    assert.equal(reconciled.approved, 1);
    order = await prisma.submittedTransaction.findUniqueOrThrow({ where: { token } });
    assert.equal(order.approved, true); assert.equal(order.bankReference, "612345678901");
    assert.equal(order.paymentReportedAt, null); // No customer "I've paid" click was needed.
    assert.ok(order.matchedCreditId);
    assert.equal(await prisma.confirmedEvent.count({ where: { token } }), 1);
    const retry = await approvePayment(token, "TEST", undefined, false);
    assert.equal(retry.changed, false);
    assert.equal(await prisma.paymentAudit.count({ where: { token, action: "AUTO_APPROVED" } }), 1);
    assert.equal(await prisma.paymentEmail.count({ where: { token, kind: "APPROVED" } }), 1);
    console.log("PASS: reviewed statements auto-confirm saved orders, deduplicate overlapping exports, and preserve one approval/receipt queue");

    await importCsv(accountA.id, "UPI reversal", "800.00", "612345678901", "DEBIT");
    await reconcileAccount(accountA.id, "TEST");
    order = await prisma.submittedTransaction.findUniqueOrThrow({ where: { token } });
    assert.equal(order.paymentStatus, "APPROVED_REVIEW_REQUIRED"); assert.equal(order.approved, true);
    assert.equal(await prisma.confirmedEvent.count({ where: { token } }), 1);
    console.log("PASS: later reversals flag review without silently deleting fulfilled registrations");

    assert.equal((await prepare(nextToken, "second@example.invalid")).status, 200);
    const thirdToken = await checkout(); assert.equal((await prepare(thirdToken, "third@example.invalid")).status, 200);
    await prisma.submittedTransaction.updateMany({ where: { token: { in: [nextToken, thirdToken] } }, data: { claimedBankReference: "612345678902" } });
    await importCsv(accountB.id, "UPI customer credit", "800.00", "612345678902");
    const contested = await reconcileAccount(accountB.id, "TEST");
    assert.equal(contested.approved, 0);
    assert.equal(await prisma.submittedTransaction.count({ where: { token: { in: [nextToken, thirdToken] }, paymentStatus: "NEEDS_REVIEW" } }), 2);
    console.log("PASS: two claims for one credit cannot race into automatic approval");
    const manualCompetition = await Promise.allSettled([approvePayment(nextToken, "TEST", undefined, false), approvePayment(thirdToken, "TEST", undefined, false)]);
    assert.equal(manualCompetition.filter(result => result.status === "fulfilled").length, 1);
    assert.equal(await prisma.submittedTransaction.count({ where: { token: { in: [nextToken, thirdToken] }, approved: true } }), 1);
    console.log("PASS: different orders with the same bank reference cannot race into manual approval");

    const fourth = await checkout({ [eventId]: { SINGLE: 1, PAIR: 1 } });
    assert.equal((await prepare(fourth, "fourth@example.invalid")).status, 200);
    const concurrent = await Promise.all([approvePayment(fourth, "TEST", undefined, false), approvePayment(fourth, "TEST", undefined, false)]);
    assert.equal(concurrent.filter(result => result.changed).length, 1);
    assert.equal((await prisma.confirmedEvent.findUniqueOrThrow({ where: { token_id: { token: fourth, id: eventId } } })).quantity, BigInt(2));
    assert.equal(await prisma.paymentEmail.count({ where: { token: fourth, kind: "APPROVED" } }), 1);
    console.log("PASS: concurrent manual approvals are idempotent, including mixed single/pair variants");

    const { GET } = await import("../../app/api/breeze-admin/payments/accounts/route");
    const unauthorized = await GET(new NextRequest("http://localhost:3000/api/breeze-admin/payments/accounts"));
    assert.ok([401, 403, 500].includes(unauthorized.status));
    await prisma.$executeRawUnsafe('CREATE ROLE payment_test_anon');
    await prisma.$executeRawUnsafe('GRANT SELECT ON "BankStatement", "BankCredit", "PaymentAccount" TO payment_test_anon');
    await prisma.$transaction(async tx => {
      await tx.$executeRawUnsafe('SET LOCAL ROLE payment_test_anon');
      const rows = await tx.$queryRawUnsafe<{ count: bigint }[]>('SELECT count(*) FROM "BankStatement"');
      assert.equal(rows[0].count, BigInt(0));
    });
    console.log("PASS: admin APIs require authentication and row-level security prevents direct browser-role statement reads");
    console.log("All isolated PostgreSQL payment integration checks passed. No live database or API keys were used.");
  } finally { if (prisma) await prisma.$disconnect(); await database.stop(); }
}

main().catch(error => { console.error(error); process.exit(1); });
