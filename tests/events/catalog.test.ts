import { test } from "node:test";
import assert from "node:assert/strict";
import { Prisma } from "@prisma/client";
import { readEventCatalog } from "../../lib/events/catalog";

test("available event records pass through unchanged", async () => {
  const events = [{ id: "original-event", event_name: "Original event", registration_open: true }];
  const result = await readEventCatalog(async () => events);
  assert.equal(result.available, true);
  assert.equal(result.data, events);
});

test("successful empty catalogs and absent event details remain available results", async () => {
  assert.deepEqual(await readEventCatalog(async () => []), { available: true, data: [] });
  assert.deepEqual(await readEventCatalog(async () => null), { available: true, data: null });
});

test("database initialization and connection exhaustion report unavailability without fabricated records", async () => {
  for (const error of [
    new Prisma.PrismaClientInitializationError("Connection unavailable", "5.22.0", "P1001"),
    new Prisma.PrismaClientKnownRequestError("Connection pool unavailable", { clientVersion: "5.22.0", code: "P2024" }),
  ]) {
    assert.deepEqual(await readEventCatalog(async () => { throw error; }), { available: false, data: null });
  }
});

test("unrelated request and programming errors are not swallowed", async () => {
  for (const error of [
    new Prisma.PrismaClientInitializationError("Schema validation error", "5.22.0", "P1012"),
    new Prisma.PrismaClientKnownRequestError("Unexpected constraint error", { clientVersion: "5.22.0", code: "P2002" }),
    new Error("Application error"),
  ]) {
    await assert.rejects(readEventCatalog(async () => { throw error; }), received => received === error);
  }
});
