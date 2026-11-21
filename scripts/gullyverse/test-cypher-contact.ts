/** Exercise the real Next preview against disposable loopback PostgreSQL. */
import assert from "node:assert/strict";
import { spawn, spawnSync, type ChildProcess } from "node:child_process";
import { randomBytes } from "node:crypto";
import { mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import { createServer } from "node:net";
import { tmpdir } from "node:os";
import path from "node:path";
import { setTimeout as delay } from "node:timers/promises";
// @ts-expect-error Node16 exports are resolved by the existing tsx runner.
import EmbeddedPostgres from "embedded-postgres";

async function freePort() {
  const probe = createServer();
  await new Promise<void>(resolve => probe.listen(0, "127.0.0.1", resolve));
  const port = (probe.address() as { port: number }).port;
  await new Promise<void>(resolve => probe.close(() => resolve()));
  return port;
}

async function exited(process: ChildProcess) {
  return new Promise<number | null>((resolve, reject) => {
    process.once("error", reject);
    process.once("exit", resolve);
  });
}

async function main() {
  const output = process.argv[2];
  if (!output) throw new Error("Pass a directory for the Contact browser captures.");
  const events = process.argv[3] === "events";
  await mkdir(output, { recursive: true });
  const [dbPort, port] = await Promise.all([freePort(), freePort()]);
  const directory = await mkdtemp(path.join(tmpdir(), "breeze-cypher-contact-"));
  const password = randomBytes(20).toString("hex");
  const database = "breeze_runtime_tests_cypher";
  const db = new EmbeddedPostgres({
    databaseDir: directory, user: "postgres", password, port: dbPort, persistent: true,
    createPostgresUser: false, postgresFlags: ["-h", "127.0.0.1"], onLog: () => {}, onError: () => {},
  });
  const url = `postgresql://postgres:${password}@127.0.0.1:${dbPort}/${database}`;
  const origin = `http://127.0.0.1:${port}`;
  const settings = {
    DATABASE_URL: url, DIRECT_URL: url, GULLYVERSE_RUNTIME_PREVIEW: "1", GULLYVERSE_ISOLATED_TEST_BACKEND: "1",
    NEXT_PUBLIC_SUPABASE_URL: "http://127.0.0.1:9", NEXT_PUBLIC_SUPABASE_ANON_KEY: "isolated-contact-test",
    BREEZE_PREVIEW_ORIGIN: origin, NEXT_TELEMETRY_DISABLED: "1",
  };
  let next: ChildProcess | undefined;
  let prisma: typeof import("../../lib/prisma").prisma | undefined;
  try {
    await db.initialise();
    await db.start();
    await db.createDatabase(database);
    Object.assign(process.env, settings);
    const setup = spawnSync(process.execPath, [
      "node_modules/prisma/build/index.js", "db", "push", "--skip-generate",
    ], { encoding: "utf8" });
    assert.equal(setup.status, 0, "The disposable preview schema setup failed");
    ({ prisma } = await import("../../lib/prisma"));
    if (events) {
      const { readCypherEvents } = await import("../../lib/events/cypher-catalog");
      assert.deepEqual(await readCypherEvents(), { available: true, data: [] });
      await prisma.eventItem.createMany({ data: [
        ...Array.from({ length: 17 }, (_, index) => ({
          event_name: `Fixture event ${String(index + 1).padStart(2, "0")}`,
          event_description: "Disposable catalog fixture",
          event_date: `2099-01-${String(index + 1).padStart(2, "0")}`,
          event_venue: "Cypher", event_org: "Fixture club", event_type: "Cultural" as const,
          image_url: index === 0 ? "/events-header.png" : null,
          registration_open: index !== 16, event_price: 0,
        })),
        { event_name: "Expired fixture", event_date: "Jan 1st 2000", event_price: 0 },
      ] });
      const catalog = await readCypherEvents();
      assert.ok(catalog.available);
      assert.equal(catalog.data.length, 17);
      assert.equal(await prisma.eventItem.count(), 18);
    } else {
      await prisma.$executeRaw`DROP TABLE "ContactSubmission"`;
      const migration = await readFile("prisma/migrations/20261120152500_contact_submissions/migration.sql", "utf8");
      const migrated = spawnSync(process.execPath, [
        "node_modules/prisma/build/index.js", "db", "execute", "--schema", "prisma/schema.prisma", "--stdin",
      ], { input: migration, encoding: "utf8" });
      assert.equal(migrated.status, 0, "The Contact migration failed on disposable PostgreSQL");
    }
    next = spawn(process.execPath, [
      "node_modules/next/dist/bin/next", "dev", "--hostname", "127.0.0.1", "--port", String(port),
    ], { stdio: "inherit" });
    let ready = false;
    for (let attempt = 0; attempt < 100 && next.exitCode === null; attempt++) {
      const response = await fetch(origin + "/api/preview-health", { signal: AbortSignal.timeout(1_500) }).catch(() => null);
      if (response?.ok && (await response.json()).isolated === true) {
        ready = true;
        break;
      }
      await delay(500);
    }
    assert.ok(ready, "The isolated Next preview could not start");
    const browserScript = events ? "cypher-events.browser.cjs" : "cypher-contact.browser.cjs";
    const browser = spawn(process.execPath, ["scripts/gullyverse/" + browserScript, output], { stdio: "inherit" });
    assert.equal(await exited(browser), 0, "The cypher browser checks failed");
    if (events) {
      assert.equal(await prisma!.eventItem.count(), 18);
      console.log(JSON.stringify({ status: "PASS", isolatedEvents: 18, activePosters: 17, expiredRowsPreserved: 1 }));
      return;
    }
    ({ prisma } = await import("../../lib/prisma"));
    const submissions = await prisma.contactSubmission.findMany({
      select: { name: true, email: true, message: true }, orderBy: { name: "asc" },
    });
    assert.deepEqual(submissions, ["Cypher Desktop Fixture", "Cypher Phone Fixture"].map(name => ({
      name, email: "preview@example.invalid", message: "This is a disposable cypher integration test.",
    })));
    console.log(JSON.stringify({ status: "PASS", isolatedPostgresSubmissions: 2, invalidOrFailedSubmissions: 0 }));
  } finally {
    if (next && next.exitCode === null && next.signalCode === null) {
      const stopped = exited(next);
      next.kill("SIGTERM");
      await stopped;
    }
    await prisma?.$disconnect();
    await db.stop();
    await rm(directory, { recursive: true, force: true });
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
