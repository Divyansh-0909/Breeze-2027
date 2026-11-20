/** Disposable loopback PostgreSQL. No hosted keys, mail, or production data. */
import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import { createServer } from "node:net";
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
// @ts-expect-error The existing package uses node16 type exports; tsx resolves it.
import EmbeddedPostgres from "embedded-postgres";
import { NextRequest } from "next/server";
const report =
  process.env.GULLYVERSE_REPORT ??
  "/dev/shm/art-lock-implementation-2026-11-14";
async function main() {
  const socket = createServer();
  await new Promise<void>((r) => socket.listen(0, "127.0.0.1", r));
  const port = (socket.address() as { port: number }).port;
  await new Promise<void>((r) => socket.close(() => r()));
  const directory = await fs.mkdtemp(
    path.join(os.tmpdir(), "breeze-isolated-db-"),
  );
  const password = randomBytes(20).toString("hex");
  const db = new EmbeddedPostgres({
    databaseDir: directory,
    user: "postgres",
    password,
    port,
    persistent: true,
    createPostgresUser: false,
    postgresFlags: ["-h", "127.0.0.1"],
    onLog: () => {},
    onError: () => {},
  });
  let prisma: typeof import("../../lib/prisma").prisma | undefined;
  const checks: Record<string, unknown> = {
    scope:
      "Disposable local PostgreSQL; auth placeholder only, no hosted Supabase or live account tests",
  };
  try {
    await db.initialise();
    await db.start();
    await db.createDatabase("breeze_runtime_tests");
    process.env.DATABASE_URL =
      process.env.DIRECT_URL = `postgresql://postgres:${password}@127.0.0.1:${port}/breeze_runtime_tests`;
    process.env.NEXT_PUBLIC_SUPABASE_URL = "http://127.0.0.1:9";
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY =
      "isolated-anonymous-placeholder-no-live-access";
    for (const key of [
      "EMAIL_HOST",
      "EMAIL_USERNAME",
      "EMAIL_PASSWORD",
      "SENDGRID_API_KEY",
      "SUPABASE_SERVICE_ROLE_KEY",
    ])
      delete process.env[key];
    const push = spawnSync(
      process.execPath,
      ["node_modules/prisma/build/index.js", "db", "push", "--skip-generate"],
      { env: process.env, encoding: "utf8" },
    );
    assert.equal(push.status, 0, "Disposable schema push failed");
    ({ prisma } = await import("../../lib/prisma"));
    const { POST } = await import("../../app/api/contact/route");
    const request = (body: unknown) =>
      new NextRequest("http://127.0.0.1/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
    const invalid = await POST(
      request({ name: "A", email: "invalid", phone: "1", message: "short" }),
    );
    assert.equal(invalid.status, 400);
    assert.equal(await prisma.contactSubmission.count(), 0);
    checks.contactValidationRejectsWithoutInsert = true;
    const valid = await POST(
      request({
        name: "Private Test",
        email: "test@example.invalid",
        phone: "9999999999",
        message: "Isolated local integration test only.",
      }),
    );
    assert.equal(valid.status, 200);
    assert.equal((await valid.json()).success, true);
    const rows = await prisma.contactSubmission.findMany();
    assert.equal(rows.length, 1);
    assert.equal(rows[0].message, "Isolated local integration test only.");
    checks.existingContactHandlerPersistsInIsolatedPostgres = true;
    await prisma.eventItem.createMany({
      data: Array.from({ length: 7 }, (_, i) => ({
        id: randomUUID(),
        event_name: `Private fixture ${i + 1}`,
        event_price: 0,
        event_type: i % 2 ? "Cultural" : "Technical",
        image_url: i % 3 ? null : "/fixtures/missing-poster.png",
      })),
    });
    const { readEventCatalog } = await import("../../lib/events/catalog");
    const catalog = await readEventCatalog(() => prisma!.eventItem.findMany());
    assert.equal(catalog.available, true);
    assert.equal(catalog.data!.length, 7);
    checks.variableCatalogAndMissingPosterFixturesRead = true;
    if (process.argv.includes("--build")) {
      const build = spawnSync(
        process.execPath,
        ["node_modules/next/dist/bin/next", "build"],
        {
          env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" },
          encoding: "utf8",
          maxBuffer: 12e6,
        },
      );
      await fs.writeFile(
        path.join(report, "scratch/isolated-production-build.log"),
        build.stdout + "\n" + build.stderr,
      );
      checks.nextBuildExitCode = build.status;
      assert.equal(
        build.status,
        0,
        "Isolated Next build failed; inspect build log",
      );
    }
    checks.status = "PASS";
  } catch (error) {
    checks.status = "FAIL";
    checks.error = String(error);
    process.exitCode = 1;
  } finally {
    if (prisma) await prisma.$disconnect();
    await db.stop();
    await fs.rm(directory, { recursive: true, force: true });
    await fs.writeFile(
      path.join(report, "evidence/isolated-backend.json"),
      JSON.stringify(checks, null, 2) + "\n",
    );
    console.log(JSON.stringify(checks));
  }
}
main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
