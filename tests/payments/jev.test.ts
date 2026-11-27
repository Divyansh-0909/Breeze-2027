import { test } from "node:test";
import assert from "node:assert/strict";
import { jevConfigured, jevReview } from "../../lib/payments/jev";

const KEYS = ["AI_GATEWAY_API_KEY", "AI_GATEWAY_JEV_MODEL", "TYPESAFE_API_KEY", "TYPESAFE_MODEL"] as const;

async function withEnv(run: () => Promise<void>) {
  const prior = Object.fromEntries(KEYS.map(key => [key, process.env[key]]));
  const priorFetch = global.fetch;
  try { for (const key of KEYS) delete process.env[key]; await run(); }
  finally {
    global.fetch = priorFetch;
    for (const key of KEYS) { if (prior[key] === undefined) delete process.env[key]; else process.env[key] = prior[key]; }
  }
}

function fakeJev(expectedUrl: string, expectedModel: string, expectedKey: string) {
  return async (url: string | URL | Request, options?: RequestInit) => {
    assert.equal(url, expectedUrl);
    assert.equal((options?.headers as Record<string, string>).Authorization, `Bearer ${expectedKey}`);
    const body = JSON.parse(String(options?.body));
    assert.equal(body.model, expectedModel);
    assert.equal(body.questions.entryKind.type, "choice");
    assert.ok(body.state.untrustedStatementText);
    return new Response(JSON.stringify({ answers: { entryKind: { choice: "incoming", confidence: 0.9 } }, usage: { input_tokens: 100 } }));
  };
}

test("Jev is optional", async () => withEnv(async () => {
  assert.equal(jevConfigured(), false);
  assert.equal((await jevReview("UPI credit")).enabled, false);
}));

test("Jev goes through Vercel AI Gateway when a Gateway key is set", async () => withEnv(async () => {
  process.env.AI_GATEWAY_API_KEY = "gateway-test-only";
  process.env.TYPESAFE_API_KEY = "direct-test-only";
  global.fetch = fakeJev("https://ai-gateway.vercel.sh/typesafe/v1/systemone", "typesafe-ai/jev", "gateway-test-only") as typeof fetch;
  assert.equal(jevConfigured(), true);
  const result = await jevReview("UPI credit");
  assert.equal(result.classification, "incoming"); assert.equal(result.inputTokens, 100);
  assert.equal("approved" in result, false);
}));

test("A direct TypeSafe key still works when no Gateway key is set", async () => withEnv(async () => {
  process.env.TYPESAFE_API_KEY = "direct-test-only";
  global.fetch = fakeJev("https://api.typesafe.ai/v1/systemone", "jev-latest", "direct-test-only") as typeof fetch;
  assert.equal((await jevReview("UPI credit")).classification, "incoming");
}));

test("Gateway errors report their type without leaking the key", async () => withEnv(async () => {
  process.env.AI_GATEWAY_API_KEY = "gateway-test-only";
  global.fetch = (async () => new Response(JSON.stringify({ error: { message: "Insufficient credits", type: "insufficient_funds" } }), { status: 402 })) as typeof fetch;
  await assert.rejects(jevReview("UPI credit"), (error: Error) => error.message === "Jev request failed (402, insufficient_funds)." && !error.message.includes("gateway-test-only"));
}));
